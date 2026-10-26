package service

import (
	"context"
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"errors"
	"fmt"
	"log"
	"math/big"
	"musebooks/model"
	"musebooks/repository"
	"musebooks/utils"
	"net/mail"
	"strings"
	"time"

	"golang.org/x/crypto/bcrypt"
)

var (
	ErrInvalidCredentials           = errors.New("invalid email or password")
	ErrEmailAlreadyRegistered       = errors.New("email is already registered")
	ErrInvalidEmail                 = errors.New("a valid email address is required")
	ErrPasswordTooShort             = errors.New("password must be at least 8 characters")
	ErrPasswordTooLong              = errors.New("password must be 72 bytes or fewer")
	ErrSessionInvalid               = errors.New("session is invalid or expired")
	ErrEmailNotVerified             = errors.New("email address is not verified")
	ErrEmailVerificationUnavailable = errors.New("email verification is not configured")
	ErrInvalidVerificationCode      = errors.New("verification code is invalid")
	ErrVerificationCodeExpired      = errors.New("verification code has expired")
	ErrVerificationAttemptsExceeded = errors.New("verification code attempt limit reached")
	ErrVerificationResendTooSoon    = errors.New("verification code was sent recently")
)

const (
	emailVerificationCodeTTL     = 10 * time.Minute
	emailVerificationResendDelay = time.Minute
	emailVerificationMaxAttempts = 5
	passwordResetCodeTTL         = 15 * time.Minute
)

type AuthService struct {
	userRepo          repository.UserRepository
	sessionRepo       repository.AuthSessionRepository
	sessionTTL        time.Duration
	verificationEmail VerificationEmailSender
	verificationKey   []byte
}

func NewAuthService(userRepo repository.UserRepository, sessionRepo repository.AuthSessionRepository, sessionTTL time.Duration) *AuthService {
	if sessionTTL <= 0 {
		sessionTTL = 30 * 24 * time.Hour
	}
	return &AuthService{userRepo: userRepo, sessionRepo: sessionRepo, sessionTTL: sessionTTL}
}

// ConfigureEmailVerification enables email/password registration with OTP
// verification. The separate secret is used to HMAC the short OTP before it
// is stored, so a database read alone does not reveal the code.
func (s *AuthService) ConfigureEmailVerification(sender VerificationEmailSender, secret string) {
	if s == nil {
		return
	}
	s.verificationEmail = sender
	s.verificationKey = []byte(strings.TrimSpace(secret))
}

func NormalizeEmail(email string) string {
	return strings.ToLower(strings.TrimSpace(email))
}

func validateCredentials(email, password string) (string, error) {
	normalized := NormalizeEmail(email)
	parsed, err := mail.ParseAddress(normalized)
	if err != nil || parsed.Address != normalized || !strings.Contains(normalized, "@") {
		return "", ErrInvalidEmail
	}
	if len(password) < 8 {
		return "", ErrPasswordTooShort
	}
	if len(password) > 72 {
		return "", ErrPasswordTooLong
	}
	return normalized, nil
}

func (s *AuthService) register(ctx context.Context, email, password string) (*model.User, string, error) {
	normalized, err := validateCredentials(email, password)
	if err != nil {
		return nil, "", err
	}
	if !s.emailVerificationConfigured() {
		return nil, "", ErrEmailVerificationUnavailable
	}
	existing, err := s.userRepo.GetUserByEmail(normalized)
	if err != nil {
		return nil, "", err
	}
	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return nil, "", fmt.Errorf("hash password: %w", err)
	}
	if existing != nil {
		// Answer exactly like a new sign-up so the response never reveals
		// whether the address already has an account; the email says what
		// actually happened.
		s.registerExisting(ctx, existing, string(hash))
		return &model.User{Email: normalized}, "", nil
	}
	user := &model.User{
		Id:            utils.UniqueID(),
		Username:      normalized,
		Email:         normalized,
		PasswordHash:  string(hash),
		Status:        true,
		EmailVerified: boolPointer(false),
	}
	user.DateTime()
	code, err := generateEmailVerificationCode()
	if err != nil {
		return nil, "", err
	}
	now := time.Now().UTC()
	setEmailVerificationCode(user, code, s.verificationKey, now)
	if err := s.userRepo.CreateUser(user); err != nil {
		return nil, "", err
	}
	if err := s.verificationEmail.SendVerificationCode(ctx, user.Email, code); err != nil {
		clearEmailVerificationCode(user)
		user.UpdateDt()
		_ = s.userRepo.UpdateUser(user)
		return user, "", fmt.Errorf("%w: %v", ErrEmailDelivery, err)
	}
	return user, "", nil
}

// registerExisting handles a sign-up for an address that already has an
// account. A verified owner is told they already have one. An unverified
// account takes the new password with a fresh code, so only whoever can read
// the inbox can finish it. Failures are logged, never returned, because the
// caller must answer the same way either way.
func (s *AuthService) registerExisting(ctx context.Context, user *model.User, passwordHash string) {
	now := time.Now().UTC()
	if !user.Status || (user.EmailVerificationSentAt != nil && now.Sub(*user.EmailVerificationSentAt) < emailVerificationResendDelay) {
		return
	}
	if userEmailIsVerified(user) {
		user.EmailVerificationSentAt = &now
		user.UpdateDt()
		if err := s.userRepo.UpdateUser(user); err != nil {
			log.Printf("[auth] record existing-account notice: %v", err)
			return
		}
		if err := s.verificationEmail.SendAccountExistsNotice(ctx, user.Email); err != nil {
			log.Printf("[auth] send existing-account notice: %v", err)
		}
		return
	}
	code, err := generateEmailVerificationCode()
	if err != nil {
		log.Printf("[auth] re-registration code: %v", err)
		return
	}
	user.PasswordHash = passwordHash
	setEmailVerificationCode(user, code, s.verificationKey, now)
	user.UpdateDt()
	if err := s.userRepo.UpdateUser(user); err != nil {
		log.Printf("[auth] re-registration update: %v", err)
		return
	}
	if err := s.verificationEmail.SendVerificationCode(ctx, user.Email, code); err != nil {
		log.Printf("[auth] re-registration email: %v", err)
	}
}

// dummyPasswordHash is compared when no account matches, so a failed login
// takes about as long whether or not the email is registered.
var dummyPasswordHash, _ = bcrypt.GenerateFromPassword([]byte("musebooks-timing-equalizer"), bcrypt.DefaultCost)

func (s *AuthService) login(ctx context.Context, email, password string) (*model.User, string, error) {
	if len(password) > 72 {
		return nil, "", ErrInvalidCredentials
	}
	normalized := NormalizeEmail(email)
	user, err := s.userRepo.GetUserByEmail(normalized)
	if err != nil {
		return nil, "", err
	}
	if user == nil || !user.Status || user.PasswordHash == "" {
		_ = bcrypt.CompareHashAndPassword(dummyPasswordHash, []byte(password))
		return nil, "", ErrInvalidCredentials
	}
	if bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(password)) != nil {
		return nil, "", ErrInvalidCredentials
	}
	if !userEmailIsVerified(user) {
		return nil, "", ErrEmailNotVerified
	}
	token, err := s.createSession(ctx, user.Id)
	if err != nil {
		return nil, "", err
	}
	return user, token, nil
}

// OAuthLogin signs in a provider-verified email address. Provider identities
// are deliberately normalized to the same local account model as password
// sign-ins, so subscriptions and existing approved-email access continue to
// follow the MuseBooks account rather than the provider session.
func (s *AuthService) oauthLogin(ctx context.Context, provider, subject, email, photoURL string) (*model.User, string, error) {
	if provider != "google" || strings.TrimSpace(subject) == "" {
		return nil, "", ErrInvalidCredentials
	}
	normalized := NormalizeEmail(email)
	parsed, err := mail.ParseAddress(normalized)
	if err != nil || parsed.Address != normalized || !strings.Contains(normalized, "@") {
		return nil, "", ErrInvalidEmail
	}
	var user *model.User
	if strings.TrimSpace(subject) != "" {
		user, err = s.userRepo.GetUserByOAuthSubject(provider, subject)
		if err != nil {
			return nil, "", err
		}
	}
	if user == nil {
		user, err = s.userRepo.GetUserByEmail(normalized)
		if err != nil {
			return nil, "", err
		}
	}
	if user == nil {
		// Social-only accounts still receive an unusable password hash so the
		// existing password-based account deletion flow cannot be bypassed.
		hash, err := unusablePasswordHash()
		if err != nil {
			return nil, "", err
		}
		user = &model.User{
			Id:            utils.UniqueID(),
			Username:      normalized,
			Email:         normalized,
			PasswordHash:  hash,
			PhotoURL:      strings.TrimSpace(photoURL),
			Status:        true,
			EmailVerified: boolPointer(true),
		}
		setOAuthSubject(user, provider, subject)
		user.DateTime()
		if err := s.userRepo.CreateUser(user); err != nil {
			return nil, "", err
		}
	} else if !user.Status {
		return nil, "", ErrInvalidCredentials
	} else {
		changed := setOAuthSubject(user, provider, subject)
		if !userEmailIsVerified(user) {
			// Nobody proved ownership of this address before the provider did, so
			// the password (and any session) may belong to someone who registered
			// it first. Drop both so only the provider-verified owner gets in.
			hash, err := unusablePasswordHash()
			if err != nil {
				return nil, "", err
			}
			if err := s.DeleteAccountSessions(ctx, user.Id); err != nil {
				return nil, "", err
			}
			user.PasswordHash = hash
			user.EmailVerified = boolPointer(true)
			clearEmailVerificationCode(user)
			changed = true
		}
		if strings.TrimSpace(user.PhotoURL) == "" && strings.TrimSpace(photoURL) != "" {
			user.PhotoURL = strings.TrimSpace(photoURL)
			changed = true
		}
		if changed {
			user.UpdateDt()
			if err := s.userRepo.UpdateUser(user); err != nil {
				return nil, "", err
			}
		}
	}
	token, err := s.createSession(ctx, user.Id)
	if err != nil {
		return nil, "", err
	}
	return user, token, nil
}

func (s *AuthService) verifyEmail(ctx context.Context, email, code string) (*model.User, string, error) {
	if !s.emailVerificationConfigured() {
		return nil, "", ErrEmailVerificationUnavailable
	}
	if len(code) != 6 {
		return nil, "", ErrInvalidVerificationCode
	}
	for _, digit := range code {
		if digit < '0' || digit > '9' {
			return nil, "", ErrInvalidVerificationCode
		}
	}
	user, err := s.userRepo.GetUserByEmail(NormalizeEmail(email))
	if err != nil {
		return nil, "", err
	}
	if user == nil || !user.Status {
		return nil, "", ErrInvalidVerificationCode
	}
	if userEmailIsVerified(user) {
		return nil, "", ErrInvalidVerificationCode
	}
	now := time.Now().UTC()
	if user.EmailVerificationAttempts >= emailVerificationMaxAttempts {
		return nil, "", ErrVerificationAttemptsExceeded
	}
	if user.EmailVerificationCodeHash == "" || user.EmailVerificationExpiresAt == nil || !user.EmailVerificationExpiresAt.After(now) {
		return nil, "", ErrVerificationCodeExpired
	}
	user.EmailVerificationAttempts++
	if err := s.userRepo.UpdateUser(user); err != nil {
		return nil, "", err
	}
	expected := emailVerificationCodeHash(s.verificationKey, user.Id, code)
	if !hmac.Equal([]byte(user.EmailVerificationCodeHash), []byte(expected)) {
		if user.EmailVerificationAttempts >= emailVerificationMaxAttempts {
			return nil, "", ErrVerificationAttemptsExceeded
		}
		return nil, "", ErrInvalidVerificationCode
	}
	user.EmailVerified = boolPointer(true)
	clearEmailVerificationCode(user)
	user.UpdateDt()
	if err := s.userRepo.UpdateUser(user); err != nil {
		return nil, "", err
	}
	token, err := s.createSession(ctx, user.Id)
	if err != nil {
		return nil, "", err
	}
	return user, token, nil
}

// ResendEmailVerification deliberately succeeds for unknown and already
// verified addresses so callers cannot use it to enumerate accounts.
func (s *AuthService) resendEmailVerification(ctx context.Context, email string) error {
	if !s.emailVerificationConfigured() {
		return ErrEmailVerificationUnavailable
	}
	user, err := s.userRepo.GetUserByEmail(NormalizeEmail(email))
	if err != nil || user == nil || !user.Status || userEmailIsVerified(user) {
		return err
	}
	if user.EmailVerificationSentAt != nil && time.Since(*user.EmailVerificationSentAt) < emailVerificationResendDelay {
		return ErrVerificationResendTooSoon
	}
	code, err := generateEmailVerificationCode()
	if err != nil {
		return err
	}
	setEmailVerificationCode(user, code, s.verificationKey, time.Now().UTC())
	user.UpdateDt()
	if err := s.userRepo.UpdateUser(user); err != nil {
		return err
	}
	if err := s.verificationEmail.SendVerificationCode(ctx, user.Email, code); err != nil {
		clearEmailVerificationCode(user)
		user.UpdateDt()
		_ = s.userRepo.UpdateUser(user)
		return fmt.Errorf("%w: %v", ErrEmailDelivery, err)
	}
	return nil
}

// RequestPasswordReset emails a reset code. It succeeds silently for unknown,
// disabled and recently-sent addresses so callers cannot enumerate accounts.
func (s *AuthService) requestPasswordReset(ctx context.Context, email string) error {
	if !s.emailVerificationConfigured() {
		return ErrEmailVerificationUnavailable
	}
	user, err := s.userRepo.GetUserByEmail(NormalizeEmail(email))
	if err != nil || user == nil || !user.Status {
		return err
	}
	now := time.Now().UTC()
	if user.PasswordResetSentAt != nil && now.Sub(*user.PasswordResetSentAt) < emailVerificationResendDelay {
		return nil
	}
	code, err := generateEmailVerificationCode()
	if err != nil {
		return err
	}
	expiresAt := now.Add(passwordResetCodeTTL)
	user.PasswordResetCodeHash = passwordResetCodeHash(s.verificationKey, user.Id, code)
	user.PasswordResetExpiresAt = &expiresAt
	user.PasswordResetSentAt = &now
	user.PasswordResetAttempts = 0
	user.UpdateDt()
	if err := s.userRepo.UpdateUser(user); err != nil {
		return err
	}
	if err := s.verificationEmail.SendPasswordResetCode(ctx, user.Email, code); err != nil {
		return fmt.Errorf("%w: %v", ErrEmailDelivery, err)
	}
	return nil
}

// ResetPassword sets a new password after checking the emailed code, signs
// out every existing session, and starts a fresh one. Receiving the code also
// proves the address, so the email becomes verified.
func (s *AuthService) resetPassword(ctx context.Context, email, code, password string) (*model.User, string, error) {
	if !s.emailVerificationConfigured() {
		return nil, "", ErrEmailVerificationUnavailable
	}
	normalized, err := validateCredentials(email, password)
	if err != nil {
		return nil, "", err
	}
	if !isVerificationCode(code) {
		return nil, "", ErrInvalidVerificationCode
	}
	user, err := s.userRepo.GetUserByEmail(normalized)
	if err != nil {
		return nil, "", err
	}
	if user == nil || !user.Status {
		return nil, "", ErrInvalidVerificationCode
	}
	now := time.Now().UTC()
	if user.PasswordResetAttempts >= emailVerificationMaxAttempts {
		return nil, "", ErrVerificationAttemptsExceeded
	}
	if user.PasswordResetCodeHash == "" || user.PasswordResetExpiresAt == nil || !user.PasswordResetExpiresAt.After(now) {
		return nil, "", ErrVerificationCodeExpired
	}
	user.PasswordResetAttempts++
	if err := s.userRepo.UpdateUser(user); err != nil {
		return nil, "", err
	}
	expected := passwordResetCodeHash(s.verificationKey, user.Id, code)
	if !hmac.Equal([]byte(user.PasswordResetCodeHash), []byte(expected)) {
		if user.PasswordResetAttempts >= emailVerificationMaxAttempts {
			return nil, "", ErrVerificationAttemptsExceeded
		}
		return nil, "", ErrInvalidVerificationCode
	}
	hash, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return nil, "", fmt.Errorf("hash password: %w", err)
	}
	if err := s.DeleteAccountSessions(ctx, user.Id); err != nil {
		return nil, "", err
	}
	user.PasswordHash = string(hash)
	user.EmailVerified = boolPointer(true)
	clearEmailVerificationCode(user)
	user.PasswordResetCodeHash = ""
	user.PasswordResetExpiresAt = nil
	user.PasswordResetSentAt = nil
	user.PasswordResetAttempts = 0
	user.UpdateDt()
	if err := s.userRepo.UpdateUser(user); err != nil {
		return nil, "", err
	}
	token, err := s.createSession(ctx, user.Id)
	if err != nil {
		return nil, "", err
	}
	return user, token, nil
}

func isVerificationCode(code string) bool {
	if len(code) != 6 {
		return false
	}
	for _, digit := range code {
		if digit < '0' || digit > '9' {
			return false
		}
	}
	return true
}

// Reset codes are keyed separately from verification codes, so one can never
// be replayed as the other.
func passwordResetCodeHash(key []byte, userID, code string) string {
	return emailVerificationCodeHash(key, "password-reset:"+userID, code)
}

func (s *AuthService) emailVerificationConfigured() bool {
	if s == nil || s.verificationEmail == nil || len(s.verificationKey) < 32 {
		return false
	}
	if configured, ok := s.verificationEmail.(interface{ Configured() bool }); ok && !configured.Configured() {
		return false
	}
	return true
}

func (s *AuthService) EmailVerificationConfigured() bool { return s.emailVerificationConfigured() }

func generateEmailVerificationCode() (string, error) {
	value, err := rand.Int(rand.Reader, big.NewInt(1_000_000))
	if err != nil {
		return "", fmt.Errorf("generate email verification code: %w", err)
	}
	return fmt.Sprintf("%06d", value.Int64()), nil
}

func setEmailVerificationCode(user *model.User, code string, key []byte, now time.Time) {
	expiresAt := now.Add(emailVerificationCodeTTL)
	sentAt := now
	user.EmailVerificationCodeHash = emailVerificationCodeHash(key, user.Id, code)
	user.EmailVerificationExpiresAt = &expiresAt
	user.EmailVerificationSentAt = &sentAt
	user.EmailVerificationAttempts = 0
}

func clearEmailVerificationCode(user *model.User) {
	user.EmailVerificationCodeHash = ""
	user.EmailVerificationExpiresAt = nil
	user.EmailVerificationSentAt = nil
	user.EmailVerificationAttempts = 0
}

// unusablePasswordHash returns a bcrypt hash of random bytes nobody knows.
func unusablePasswordHash() (string, error) {
	secret := make([]byte, 32)
	if _, err := rand.Read(secret); err != nil {
		return "", fmt.Errorf("create oauth account secret: %w", err)
	}
	hash, err := bcrypt.GenerateFromPassword(secret, bcrypt.DefaultCost)
	if err != nil {
		return "", fmt.Errorf("hash oauth account secret: %w", err)
	}
	return string(hash), nil
}

func boolPointer(value bool) *bool {
	return &value
}

// Legacy records without proof of email ownership remain unverified.
func userEmailIsVerified(user *model.User) bool {
	return user != nil && user.EmailVerified != nil && *user.EmailVerified
}

func emailVerificationCodeHash(key []byte, userID, code string) string {
	mac := hmac.New(sha256.New, key)
	_, _ = mac.Write([]byte(userID + ":" + code))
	return fmt.Sprintf("%x", mac.Sum(nil))
}

func setOAuthSubject(user *model.User, provider, subject string) bool {
	if user == nil || strings.TrimSpace(subject) == "" {
		return false
	}
	subject = strings.TrimSpace(subject)
	switch strings.ToLower(strings.TrimSpace(provider)) {
	case "google":
		if user.GoogleSubject == subject {
			return false
		}
		user.GoogleSubject = subject
		return true
	default:
		return false
	}
}

func (s *AuthService) CurrentUser(ctx context.Context, token string) (*model.User, error) {
	hash := hashSessionToken(token)
	if hash == "" {
		return nil, ErrSessionInvalid
	}
	session, err := s.sessionRepo.GetSession(ctx, hash)
	if err != nil {
		return nil, err
	}
	if session == nil || !session.ExpiresAt.After(time.Now().UTC()) {
		return nil, ErrSessionInvalid
	}
	user, err := s.userRepo.GetUserById(session.UserID)
	if err != nil {
		return nil, err
	}
	if user == nil || !user.Status || !userEmailIsVerified(user) {
		return nil, ErrSessionInvalid
	}
	return user, nil
}

func (s *AuthService) Logout(ctx context.Context, token string) error {
	hash := hashSessionToken(token)
	if hash == "" {
		return nil
	}
	return s.sessionRepo.DeleteSession(ctx, hash)
}

func (s *AuthService) SessionExpiresAt(now time.Time) time.Time {
	if s == nil || s.sessionTTL <= 0 {
		return now.UTC().Add(30 * 24 * time.Hour)
	}
	return now.UTC().Add(s.sessionTTL)
}

func (s *AuthService) VerifyPassword(userID, password string) error {
	if s == nil || strings.TrimSpace(userID) == "" {
		return ErrInvalidCredentials
	}
	user, err := s.userRepo.GetUserById(userID)
	if err != nil {
		return err
	}
	if user == nil || !user.Status || bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(password)) != nil {
		return ErrInvalidCredentials
	}
	return nil
}

func (s *AuthService) DeleteAccountSessions(ctx context.Context, userID string) error {
	if s == nil || s.sessionRepo == nil {
		return nil
	}
	if repo, ok := s.sessionRepo.(interface {
		DeleteSessionsForUser(context.Context, string) error
	}); ok {
		return repo.DeleteSessionsForUser(ctx, userID)
	}
	return nil
}

func (s *AuthService) createSession(ctx context.Context, userID string) (string, error) {
	if err := s.sessionRepo.DeleteExpiredSessions(ctx, time.Now().UTC()); err != nil {
		return "", err
	}
	raw := make([]byte, 32)
	if _, err := rand.Read(raw); err != nil {
		return "", fmt.Errorf("create session token: %w", err)
	}
	token := base64.RawURLEncoding.EncodeToString(raw)
	if err := s.sessionRepo.CreateSession(ctx, &model.AuthSession{
		TokenHash: hashSessionToken(token), UserID: userID,
		ExpiresAt: time.Now().UTC().Add(s.sessionTTL), CreatedAt: time.Now().UTC(),
	}); err != nil {
		return "", err
	}
	return token, nil
}

func hashSessionToken(token string) string {
	trimmed := strings.TrimSpace(token)
	if trimmed == "" {
		return ""
	}
	digest := sha256.Sum256([]byte(trimmed))
	return fmt.Sprintf("%x", digest[:])
}

// Production repositories hold a database lock for each account mutation.
func (s *AuthService) locked(ctx context.Context, email string, run func(*AuthService) error) error {
	if locker, ok := s.userRepo.(interface {
		WithAuthLock(context.Context, string, func(repository.UserRepository, repository.AuthSessionRepository) error) error
	}); ok {
		var operationErr error
		err := locker.WithAuthLock(ctx, NormalizeEmail(email), func(users repository.UserRepository, sessions repository.AuthSessionRepository) error {
			scoped := *s
			scoped.userRepo, scoped.sessionRepo = users, sessions
			operationErr = run(&scoped)
			// Expected auth failures still commit attempt counters and delivery
			// cooldowns. Database statement failures abort PostgreSQL's transaction.
			return nil
		})
		if err != nil {
			return err
		}
		return operationErr
	}
	return run(s)
}

func (s *AuthService) Register(ctx context.Context, email, password string) (user *model.User, token string, err error) {
	err = s.locked(ctx, email, func(scoped *AuthService) error { user, token, err = scoped.register(ctx, email, password); return err })
	return
}

func (s *AuthService) Login(ctx context.Context, email, password string) (user *model.User, token string, err error) {
	err = s.locked(ctx, email, func(scoped *AuthService) error { user, token, err = scoped.login(ctx, email, password); return err })
	return
}

func (s *AuthService) VerifyEmail(ctx context.Context, email, code string) (user *model.User, token string, err error) {
	err = s.locked(ctx, email, func(scoped *AuthService) error { user, token, err = scoped.verifyEmail(ctx, email, code); return err })
	return
}

func (s *AuthService) ResendEmailVerification(ctx context.Context, email string) error {
	return s.locked(ctx, email, func(scoped *AuthService) error { return scoped.resendEmailVerification(ctx, email) })
}

func (s *AuthService) RequestPasswordReset(ctx context.Context, email string) error {
	return s.locked(ctx, email, func(scoped *AuthService) error { return scoped.requestPasswordReset(ctx, email) })
}

func (s *AuthService) ResetPassword(ctx context.Context, email, code, password string) (user *model.User, token string, err error) {
	err = s.locked(ctx, email, func(scoped *AuthService) error {
		user, token, err = scoped.resetPassword(ctx, email, code, password)
		return err
	})
	return
}

func (s *AuthService) OAuthLogin(ctx context.Context, provider, subject, email, photoURL string) (user *model.User, token string, err error) {
	err = s.locked(ctx, email, func(scoped *AuthService) error {
		user, token, err = scoped.oauthLogin(ctx, provider, subject, email, photoURL)
		return err
	})
	return
}
