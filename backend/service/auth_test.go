package service

import (
	"context"
	"errors"
	"musebooks/model"
	"musebooks/repository"
	"sync"
	"testing"
	"time"

	"golang.org/x/crypto/bcrypt"
)

type authUserRepoStub struct {
	user *model.User
}

type transactionalAuthRepoStub struct {
	authUserRepoStub
	mu       sync.Mutex
	sessions *authSessionRepoStub
	commits  int
}

func (r *transactionalAuthRepoStub) WithAuthLock(_ context.Context, _ string, run func(repository.UserRepository, repository.AuthSessionRepository) error) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	var snapshot *model.User
	if r.user != nil {
		copied := *r.user
		snapshot = &copied
	}
	scoped := &authUserRepoStub{user: snapshot}
	if err := run(scoped, r.sessions); err != nil {
		return err
	}
	r.user = scoped.user
	r.commits++
	return nil
}

func TestAuthMutationsUseTransactionRepositoriesAndConsumeCodeOnce(t *testing.T) {
	ctx := context.Background()
	sessions := &authSessionRepoStub{}
	users := &transactionalAuthRepoStub{sessions: sessions}
	sender := &authVerificationEmailSenderStub{}
	auth := NewAuthService(users, &authSessionRepoStub{}, time.Hour)
	auth.ConfigureEmailVerification(sender, "0123456789abcdef0123456789abcdef")
	if _, _, err := auth.Register(ctx, "reader@example.com", "password-123"); err != nil {
		t.Fatal(err)
	}
	if users.user == nil {
		t.Fatal("registration did not commit through the transaction repository")
	}
	code := sender.code
	wrong := "111111"
	if wrong == code {
		wrong = "222222"
	}
	if _, _, err := auth.VerifyEmail(ctx, "reader@example.com", wrong); !errors.Is(err, ErrInvalidVerificationCode) {
		t.Fatal(err)
	}
	if users.user.EmailVerificationAttempts != 1 {
		t.Fatal("failed attempt was rolled back")
	}
	var wg sync.WaitGroup
	results := make(chan error, 8)
	for i := 0; i < 8; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			_, _, err := auth.VerifyEmail(ctx, "reader@example.com", code)
			results <- err
		}()
	}
	wg.Wait()
	close(results)
	accepted := 0
	for err := range results {
		if err == nil {
			accepted++
		}
	}
	if accepted != 1 || len(sessions.sessions) != 1 {
		t.Fatalf("one code created %d sign-ins and %d sessions", accepted, len(sessions.sessions))
	}
}

func (r *authUserRepoStub) CreateUser(user *model.User) error { r.user = user; return nil }
func (r *authUserRepoStub) GetUserById(id string) (*model.User, error) {
	if r.user != nil && r.user.Id == id {
		return r.user, nil
	}
	return nil, nil
}
func (r *authUserRepoStub) GetUserByUserNameAndCompanyId(string, string) (*model.User, error) {
	return nil, nil
}
func (r *authUserRepoStub) GetUserByUserName(string) (*model.User, error) { return nil, nil }
func (r *authUserRepoStub) GetUserInfoByFriendIds([]string) ([]*model.User, error) {
	return nil, nil
}
func (r *authUserRepoStub) GetUserByEmail(email string) (*model.User, error) {
	if r.user != nil && NormalizeEmail(r.user.Email) == NormalizeEmail(email) {
		return r.user, nil
	}
	return nil, nil
}
func (r *authUserRepoStub) GetUserByOAuthSubject(provider, subject string) (*model.User, error) {
	if r.user == nil {
		return nil, nil
	}
	if provider == "google" && r.user.GoogleSubject == subject {
		return r.user, nil
	}

	return nil, nil
}
func (r *authUserRepoStub) UpdateUser(user *model.User) error { r.user = user; return nil }
func (r *authUserRepoStub) DeleteUser(string) error           { return nil }

type authSessionRepoStub struct {
	sessions map[string]*model.AuthSession
}

// Deliberately returns expired rows to verify the service itself rejects them.
type unfilteredAuthSessionRepo struct{ authSessionRepoStub }

func (r *unfilteredAuthSessionRepo) GetSession(_ context.Context, hash string) (*model.AuthSession, error) {
	return r.sessions[hash], nil
}

func TestCurrentUserRejectsExpiredSessionWithoutRepositoryFiltering(t *testing.T) {
	users := &authUserRepoStub{user: &model.User{Id: "user", Status: true, EmailVerified: boolPointer(true)}}
	sessions := &unfilteredAuthSessionRepo{authSessionRepoStub{sessions: map[string]*model.AuthSession{
		hashSessionToken("expired"): {UserID: "user", ExpiresAt: time.Now().Add(-time.Second)},
		hashSessionToken("valid"):   {UserID: "user", ExpiresAt: time.Now().Add(time.Hour)},
	}}}
	auth := NewAuthService(users, sessions, time.Hour)
	if _, err := auth.CurrentUser(context.Background(), "expired"); !errors.Is(err, ErrSessionInvalid) {
		t.Fatalf("expired session error = %v", err)
	}
	if _, err := auth.CurrentUser(context.Background(), "valid"); err != nil {
		t.Fatalf("valid session: %v", err)
	}
	if err := auth.Logout(context.Background(), "valid"); err != nil {
		t.Fatal(err)
	}
	if _, err := auth.CurrentUser(context.Background(), "valid"); !errors.Is(err, ErrSessionInvalid) {
		t.Fatalf("revoked session error = %v", err)
	}
}

type authVerificationEmailSenderStub struct {
	to        string
	code      string
	resetCode string
	notices   int
}

func (s *authVerificationEmailSenderStub) SendPasswordResetCode(_ context.Context, to, code string) error {
	s.to = to
	s.resetCode = code
	return nil
}

func (s *authVerificationEmailSenderStub) SendAccountExistsNotice(_ context.Context, to string) error {
	s.to = to
	s.notices++
	return nil
}

func (s *authVerificationEmailSenderStub) SendVerificationCode(_ context.Context, to, code string) error {
	s.to = to
	s.code = code
	return nil
}

func (r *authSessionRepoStub) CreateSession(_ context.Context, session *model.AuthSession) error {
	if r.sessions == nil {
		r.sessions = make(map[string]*model.AuthSession)
	}
	r.sessions[session.TokenHash] = session
	return nil
}
func (r *authSessionRepoStub) GetSession(_ context.Context, tokenHash string) (*model.AuthSession, error) {
	session := r.sessions[tokenHash]
	if session == nil || !session.ExpiresAt.After(time.Now().UTC()) {
		return nil, nil
	}
	return session, nil
}
func (r *authSessionRepoStub) DeleteSession(_ context.Context, tokenHash string) error {
	delete(r.sessions, tokenHash)
	return nil
}
func (r *authSessionRepoStub) DeleteExpiredSessions(_ context.Context, now time.Time) error {
	for token, session := range r.sessions {
		if !session.ExpiresAt.After(now) {
			delete(r.sessions, token)
		}
	}
	return nil
}

func TestAuthServiceRegistersAndRevokesSession(t *testing.T) {
	users := &authUserRepoStub{}
	sessions := &authSessionRepoStub{}
	emailSender := &authVerificationEmailSenderStub{}
	service := NewAuthService(users, sessions, time.Hour)
	service.ConfigureEmailVerification(emailSender, "0123456789abcdef0123456789abcdef")

	user, token, err := service.Register(context.Background(), " Owner@Example.com ", "password-123")
	if err != nil {
		t.Fatalf("register: %v", err)
	}
	if user.Email != "owner@example.com" || token != "" {
		t.Fatalf("unexpected registration result: user=%+v token=%q", user, token)
	}
	if emailSender.to != user.Email || len(emailSender.code) != 6 {
		t.Fatalf("verification email was not sent: to=%q code=%q", emailSender.to, emailSender.code)
	}
	user, token, err = service.VerifyEmail(context.Background(), user.Email, emailSender.code)
	if err != nil {
		t.Fatalf("verify email: %v", err)
	}
	if token == "" || user.EmailVerified == nil || !*user.EmailVerified {
		t.Fatalf("verification did not activate the account: user=%+v token=%q", user, token)
	}
	if bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte("password-123")) != nil {
		t.Fatal("password was not stored as a valid bcrypt hash")
	}
	current, err := service.CurrentUser(context.Background(), token)
	if err != nil || current.Id != user.Id {
		t.Fatalf("current user: user=%+v err=%v", current, err)
	}
	if err := service.Logout(context.Background(), token); err != nil {
		t.Fatalf("logout: %v", err)
	}
	if _, err := service.CurrentUser(context.Background(), token); !errors.Is(err, ErrSessionInvalid) {
		t.Fatalf("expected revoked session, got %v", err)
	}
}

func TestVerificationRejectsWrongExpiredAndReplayedCodes(t *testing.T) {
	ctx := context.Background()
	users, sessions, sender := &authUserRepoStub{}, &authSessionRepoStub{}, &authVerificationEmailSenderStub{}
	auth := NewAuthService(users, sessions, time.Hour)
	auth.ConfigureEmailVerification(sender, "0123456789abcdef0123456789abcdef")
	user, _, err := auth.Register(ctx, "verify@example.com", "password-123")
	if err != nil {
		t.Fatal(err)
	}
	code := sender.code
	if user.EmailVerificationCodeHash == code || len(sessions.sessions) != 0 {
		t.Fatal("registration leaked a code or created a session")
	}
	wrong := "111111"
	if code == wrong {
		wrong = "222222"
	}
	for i := 0; i < 5; i++ {
		if _, _, err := auth.VerifyEmail(ctx, user.Email, wrong); err == nil {
			t.Fatal("wrong code accepted")
		}
	}
	if _, _, err = auth.VerifyEmail(ctx, user.Email, code); !errors.Is(err, ErrVerificationAttemptsExceeded) {
		t.Fatalf("attempt cap bypassed: %v", err)
	}
	user.EmailVerificationSentAt = nil
	if err = auth.ResendEmailVerification(ctx, user.Email); err != nil {
		t.Fatal(err)
	}
	if err = auth.ResendEmailVerification(ctx, user.Email); !errors.Is(err, ErrVerificationResendTooSoon) {
		t.Fatal("resend cooldown bypassed")
	}
	expired := time.Now().Add(-time.Second)
	user.EmailVerificationExpiresAt = &expired
	if _, _, err = auth.VerifyEmail(ctx, user.Email, sender.code); !errors.Is(err, ErrVerificationCodeExpired) {
		t.Fatal("expired code accepted")
	}
	user.EmailVerificationSentAt = nil
	if err = auth.ResendEmailVerification(ctx, user.Email); err != nil {
		t.Fatal(err)
	}
	code = sender.code
	if _, _, err = auth.VerifyEmail(ctx, user.Email, code); err != nil {
		t.Fatal(err)
	}
	if _, _, err = auth.VerifyEmail(ctx, user.Email, code); !errors.Is(err, ErrInvalidVerificationCode) {
		t.Fatal("code replayed")
	}
}

func TestLegacyUnverifiedRecordsCannotUseSessions(t *testing.T) {
	users := &authUserRepoStub{user: &model.User{Id: "legacy", Status: true}}
	sessions := &authSessionRepoStub{sessions: map[string]*model.AuthSession{hashSessionToken("old-token"): {UserID: "legacy", ExpiresAt: time.Now().Add(time.Hour)}}}
	auth := NewAuthService(users, sessions, time.Hour)
	if _, err := auth.CurrentUser(context.Background(), "old-token"); !errors.Is(err, ErrSessionInvalid) {
		t.Fatal("legacy email implicitly verified")
	}
}

func TestAuthServiceRejectsDuplicateAndInvalidLogin(t *testing.T) {
	users := &authUserRepoStub{}
	sessions := &authSessionRepoStub{}
	emailSender := &authVerificationEmailSenderStub{}
	service := NewAuthService(users, sessions, time.Hour)
	service.ConfigureEmailVerification(emailSender, "0123456789abcdef0123456789abcdef")
	if _, _, err := service.Register(context.Background(), "owner@example.com", "password-123"); err != nil {
		t.Fatalf("register: %v", err)
	}
	if _, _, err := service.Login(context.Background(), "owner@example.com", "password-123"); !errors.Is(err, ErrEmailNotVerified) {
		t.Fatalf("expected unverified account login error, got %v", err)
	}
	if _, _, err := service.Login(context.Background(), "owner@example.com", "wrong-pass"); !errors.Is(err, ErrInvalidCredentials) {
		t.Fatalf("expected invalid credentials, got %v", err)
	}
}

func TestAuthServiceRejectsPasswordsLongerThanBcryptLimit(t *testing.T) {
	users := &authUserRepoStub{}
	sessions := &authSessionRepoStub{}
	service := NewAuthService(users, sessions, time.Hour)

	if _, _, err := service.Register(context.Background(), "long-password@example.com", string(make([]byte, 73))); !errors.Is(err, ErrPasswordTooLong) {
		t.Fatalf("expected long-password error, got %v", err)
	}
	if users.user != nil {
		t.Fatal("long password should be rejected before creating a user")
	}
}

// Someone who registers an address they don't own must not keep a working
// password once the real owner signs in through a provider.
func TestAuthServiceOAuthLoginRevokesPasswordOfUnverifiedAccount(t *testing.T) {
	users := &authUserRepoStub{}
	sessions := &authSessionRepoStub{}
	service := NewAuthService(users, sessions, time.Hour)
	service.ConfigureEmailVerification(&authVerificationEmailSenderStub{}, "0123456789abcdef0123456789abcdef")

	if _, _, err := service.Register(context.Background(), "victim@example.com", "attacker-pass"); err != nil {
		t.Fatalf("register: %v", err)
	}
	user, token, err := service.OAuthLogin(context.Background(), "google", "google-subject", "victim@example.com", "")
	if err != nil || token == "" {
		t.Fatalf("oauth login: token=%q err=%v", token, err)
	}
	if user.EmailVerified == nil || !*user.EmailVerified {
		t.Fatal("oauth login should verify the provider-confirmed email")
	}
	if _, _, err := service.Login(context.Background(), "victim@example.com", "attacker-pass"); !errors.Is(err, ErrInvalidCredentials) {
		t.Fatalf("pre-registered password still works after oauth verification: %v", err)
	}
}

func TestAuthServiceOAuthLoginKeepsPasswordOfVerifiedAccount(t *testing.T) {
	users := &authUserRepoStub{}
	sessions := &authSessionRepoStub{}
	emailSender := &authVerificationEmailSenderStub{}
	service := NewAuthService(users, sessions, time.Hour)
	service.ConfigureEmailVerification(emailSender, "0123456789abcdef0123456789abcdef")

	user, _, err := service.Register(context.Background(), "owner@example.com", "password-123")
	if err != nil {
		t.Fatalf("register: %v", err)
	}
	if _, _, err := service.VerifyEmail(context.Background(), user.Email, emailSender.code); err != nil {
		t.Fatalf("verify email: %v", err)
	}
	if _, _, err := service.OAuthLogin(context.Background(), "google", "google-subject", "owner@example.com", ""); err != nil {
		t.Fatalf("oauth login: %v", err)
	}
	if _, _, err := service.Login(context.Background(), "owner@example.com", "password-123"); err != nil {
		t.Fatalf("verified owner's password should keep working: %v", err)
	}
}

func TestAuthServiceOAuthLoginCreatesAndReusesAccount(t *testing.T) {
	users := &authUserRepoStub{}
	sessions := &authSessionRepoStub{}
	service := NewAuthService(users, sessions, time.Hour)

	created, firstToken, err := service.OAuthLogin(context.Background(), "google", "google-subject", " Owner@Example.com ", "https://example.com/avatar.png")
	if err != nil {
		t.Fatalf("oauth create: %v", err)
	}
	if created.Email != "owner@example.com" || created.PhotoURL == "" || firstToken == "" {
		t.Fatalf("unexpected oauth account: user=%+v token=%q", created, firstToken)
	}
	if _, _, err := service.OAuthLogin(context.Background(), "google", "google-subject", "owner@example.com", ""); err != nil {
		t.Fatalf("oauth reuse: %v", err)
	}
	if users.user.Id != created.Id {
		t.Fatalf("oauth login created a second account: first=%q second=%q", created.Id, users.user.Id)
	}
}

func newResetTestService(t *testing.T) (*AuthService, *authUserRepoStub, *authVerificationEmailSenderStub) {
	t.Helper()
	users := &authUserRepoStub{}
	emailSender := &authVerificationEmailSenderStub{}
	service := NewAuthService(users, &authSessionRepoStub{}, time.Hour)
	service.ConfigureEmailVerification(emailSender, "0123456789abcdef0123456789abcdef")
	return service, users, emailSender
}

func registerVerified(t *testing.T, service *AuthService, emailSender *authVerificationEmailSenderStub, email, password string) *model.User {
	t.Helper()
	if _, _, err := service.Register(context.Background(), email, password); err != nil {
		t.Fatalf("register: %v", err)
	}
	user, _, err := service.VerifyEmail(context.Background(), email, emailSender.code)
	if err != nil {
		t.Fatalf("verify: %v", err)
	}
	return user
}

// A sign-up for a registered address must look like any other sign-up.
func TestRegisterExistingVerifiedAccountAnswersLikeNewSignUp(t *testing.T) {
	service, users, emailSender := newResetTestService(t)
	registerVerified(t, service, emailSender, "owner@example.com", "password-123")

	user, token, err := service.Register(context.Background(), "OWNER@example.com", "other-pass-1")
	if err != nil || token != "" || user == nil || user.Email != "owner@example.com" {
		t.Fatalf("existing-account sign-up should look normal: user=%+v token=%q err=%v", user, token, err)
	}
	if emailSender.notices != 1 {
		t.Fatalf("owner should be told they already have an account, notices=%d", emailSender.notices)
	}
	if bcrypt.CompareHashAndPassword([]byte(users.user.PasswordHash), []byte("password-123")) != nil {
		t.Fatal("a sign-up attempt must not change a verified account's password")
	}
}

func TestRegisterExistingUnverifiedAccountTakesNewPasswordAndCode(t *testing.T) {
	service, users, emailSender := newResetTestService(t)
	if _, _, err := service.Register(context.Background(), "owner@example.com", "first-pass-1"); err != nil {
		t.Fatalf("register: %v", err)
	}
	firstCode := emailSender.code
	sentAt := time.Now().UTC().Add(-2 * emailVerificationResendDelay)
	users.user.EmailVerificationSentAt = &sentAt

	if _, _, err := service.Register(context.Background(), "owner@example.com", "second-pass-1"); err != nil {
		t.Fatalf("re-register: %v", err)
	}
	if emailSender.code == firstCode {
		t.Fatal("re-registering should send a fresh code")
	}
	if _, _, err := service.VerifyEmail(context.Background(), "owner@example.com", emailSender.code); err != nil {
		t.Fatalf("verify: %v", err)
	}
	if _, _, err := service.Login(context.Background(), "owner@example.com", "second-pass-1"); err != nil {
		t.Fatalf("latest password should work: %v", err)
	}
	if _, _, err := service.Login(context.Background(), "owner@example.com", "first-pass-1"); !errors.Is(err, ErrInvalidCredentials) {
		t.Fatalf("earlier password should no longer work: %v", err)
	}
}

func TestPasswordResetReplacesPasswordAndSignsOutOtherSessions(t *testing.T) {
	service, _, emailSender := newResetTestService(t)
	registerVerified(t, service, emailSender, "owner@example.com", "password-123")
	_, oldToken, err := service.Login(context.Background(), "owner@example.com", "password-123")
	if err != nil {
		t.Fatalf("login: %v", err)
	}

	if err := service.RequestPasswordReset(context.Background(), "owner@example.com"); err != nil {
		t.Fatalf("request reset: %v", err)
	}
	if len(emailSender.resetCode) != 6 {
		t.Fatalf("reset code was not sent: %q", emailSender.resetCode)
	}
	_, newToken, err := service.ResetPassword(context.Background(), "owner@example.com", emailSender.resetCode, "new-password-1")
	if err != nil || newToken == "" {
		t.Fatalf("reset: token=%q err=%v", newToken, err)
	}
	if _, err := service.CurrentUser(context.Background(), oldToken); !errors.Is(err, ErrSessionInvalid) {
		t.Fatalf("old session should be signed out, got %v", err)
	}
	if _, _, err := service.Login(context.Background(), "owner@example.com", "new-password-1"); err != nil {
		t.Fatalf("new password should work: %v", err)
	}
	if _, _, err := service.ResetPassword(context.Background(), "owner@example.com", emailSender.resetCode, "another-pass-1"); !errors.Is(err, ErrVerificationCodeExpired) {
		t.Fatalf("a used reset code must not work again, got %v", err)
	}
}

func TestPasswordResetRejectsWrongCodesAndLimitsAttempts(t *testing.T) {
	service, _, emailSender := newResetTestService(t)
	registerVerified(t, service, emailSender, "owner@example.com", "password-123")
	if err := service.RequestPasswordReset(context.Background(), "owner@example.com"); err != nil {
		t.Fatalf("request reset: %v", err)
	}
	wrong := "000000"
	if emailSender.resetCode == wrong {
		wrong = "111111"
	}
	for i := 0; i < emailVerificationMaxAttempts-1; i++ {
		if _, _, err := service.ResetPassword(context.Background(), "owner@example.com", wrong, "new-password-1"); !errors.Is(err, ErrInvalidVerificationCode) {
			t.Fatalf("attempt %d: expected invalid code, got %v", i, err)
		}
	}
	if _, _, err := service.ResetPassword(context.Background(), "owner@example.com", wrong, "new-password-1"); !errors.Is(err, ErrVerificationAttemptsExceeded) {
		t.Fatalf("expected attempt limit, got %v", err)
	}
	if _, _, err := service.ResetPassword(context.Background(), "owner@example.com", emailSender.resetCode, "new-password-1"); !errors.Is(err, ErrVerificationAttemptsExceeded) {
		t.Fatalf("the right code must not work after the limit, got %v", err)
	}
}

func TestPasswordResetRequestIsSilentForUnknownEmail(t *testing.T) {
	service, _, emailSender := newResetTestService(t)
	if err := service.RequestPasswordReset(context.Background(), "nobody@example.com"); err != nil {
		t.Fatalf("unknown email should look like success, got %v", err)
	}
	if emailSender.resetCode != "" {
		t.Fatal("no email should be sent for an unknown address")
	}
}

// A verification code must not work as a reset code.
func TestPasswordResetDoesNotAcceptVerificationCode(t *testing.T) {
	service, users, emailSender := newResetTestService(t)
	registerVerified(t, service, emailSender, "owner@example.com", "password-123")
	if err := service.RequestPasswordReset(context.Background(), "owner@example.com"); err != nil {
		t.Fatalf("request reset: %v", err)
	}
	verificationStyleHash := emailVerificationCodeHash(service.verificationKey, users.user.Id, emailSender.resetCode)
	if users.user.PasswordResetCodeHash == verificationStyleHash {
		t.Fatal("reset codes must be hashed under their own purpose")
	}
}

func (r *authSessionRepoStub) DeleteSessionsForUser(_ context.Context, userID string) error {
	for hash, session := range r.sessions {
		if session.UserID == userID {
			delete(r.sessions, hash)
		}
	}
	return nil
}
