package service

import (
	"context"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"strings"
	"sync"
	"time"

	webpush "github.com/SherClockHolmes/webpush-go"
	"gorm.io/gorm"
	"gorm.io/gorm/clause"

	"musebooks/model"
)

// Daily new-publications notification over standard Web Push (VAPID): no
// Firebase or other account. The server signs each message with its own key.
const (
	pushDigestHourUTC   = 2 // 10:00 Malaysia time, as MuseCards' daily digest
	pushDigestMinGap    = 20 * time.Hour
	pushMaxFailures     = 5
	pushBatchSize       = 500
	pushWorkers         = 8
	pushTopic           = "new-publications"
	pushSubscriptionCap = 20 // devices per account
)

var (
	ErrPushUnavailable         = errors.New("push notifications are not configured")
	ErrInvalidPushSubscription = errors.New("invalid push subscription")
	ErrPushDeviceLimit         = errors.New("too many devices with notifications")
)

type PushConfig struct {
	PublicKey  string
	PrivateKey string
	Subject    string
}

type PushService struct {
	db     *gorm.DB
	cfg    PushConfig
	client webpush.HTTPClient
	now    func() time.Time
}

func NewPushService(db *gorm.DB, cfg PushConfig) *PushService {
	return &PushService{db: db, cfg: cfg, client: pushHTTPClient(), now: time.Now}
}

// pushHTTPClient talks only to the allowlisted push services and never
// follows a redirect elsewhere.
func pushHTTPClient() *http.Client {
	return &http.Client{Timeout: 15 * time.Second, CheckRedirect: func(*http.Request, []*http.Request) error { return http.ErrUseLastResponse }}
}

func (s *PushService) Enabled() bool {
	return s != nil && s.db != nil && s.cfg.PublicKey != "" && s.cfg.PrivateKey != ""
}

func (s *PushService) PublicKey() string {
	if !s.Enabled() {
		return ""
	}
	return s.cfg.PublicKey
}

// The browser push services (Chrome/Android, Firefox, Safari, Edge). The
// server POSTs to whatever endpoint is stored, so anything else is refused.
var pushHosts = map[string]bool{"fcm.googleapis.com": true, "updates.push.services.mozilla.com": true, "web.push.apple.com": true}
var pushHostSuffixes = []string{".push.services.mozilla.com", ".push.apple.com", ".notify.windows.com"}

func ValidPushEndpoint(raw string) bool {
	if len(raw) > 1000 {
		return false
	}
	parsed, err := url.Parse(raw)
	if err != nil || parsed.Scheme != "https" || parsed.User != nil || (parsed.Port() != "" && parsed.Port() != "443") {
		return false
	}
	host := strings.ToLower(parsed.Hostname())
	if pushHosts[host] {
		return true
	}
	for _, suffix := range pushHostSuffixes {
		if strings.HasSuffix(host, suffix) {
			return true
		}
	}
	return false
}

func decodePushKey(value string) []byte {
	decoded, err := base64.RawURLEncoding.DecodeString(strings.TrimRight(strings.TrimSpace(value), "="))
	if err != nil {
		return nil
	}
	return decoded
}

// validPushKeys checks the browser's P-256 public key (65 bytes, uncompressed)
// and 16-byte auth secret before they are stored.
func validPushKeys(p256dh, auth string) bool {
	key, secret := decodePushKey(p256dh), decodePushKey(auth)
	return len(key) == 65 && key[0] == 4 && len(secret) == 16
}

func pushLanguage(value string) string {
	switch value {
	case "ja", "zh-Hans", "zh-Hant":
		return value
	}
	return "en"
}

func pushSubscriptionID(endpoint string) string {
	sum := sha256.Sum256([]byte(endpoint))
	return hex.EncodeToString(sum[:])
}

// Subscribe stores this browser for the signed-in account. Subscribing again
// refreshes its keys, language and owner.
func (s *PushService) Subscribe(ctx context.Context, userID, endpoint, p256dh, auth, language string) error {
	if !s.Enabled() {
		return ErrPushUnavailable
	}
	if strings.TrimSpace(userID) == "" || !ValidPushEndpoint(endpoint) || !validPushKeys(p256dh, auth) {
		return ErrInvalidPushSubscription
	}
	id := pushSubscriptionID(endpoint)
	return s.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		var count int64
		if err := tx.Model(&model.PushSubscription{}).Where("user_id = ? AND id <> ?", userID, id).Count(&count).Error; err != nil {
			return err
		}
		if count >= pushSubscriptionCap {
			return ErrPushDeviceLimit
		}
		row := model.PushSubscription{ID: id, UserID: userID, Endpoint: endpoint, P256dh: strings.TrimSpace(p256dh), Auth: strings.TrimSpace(auth), Language: pushLanguage(language)}
		return tx.Clauses(clause.OnConflict{Columns: []clause.Column{{Name: "id"}}, DoUpdates: clause.Assignments(map[string]any{
			"user_id": row.UserID, "p256dh": row.P256dh, "auth": row.Auth, "language": row.Language, "failures": 0, "updated_at": s.now().UTC(),
		})}).Create(&row).Error
	})
}

// Unsubscribe removes this browser if it belongs to the signed-in account.
func (s *PushService) Unsubscribe(ctx context.Context, userID, endpoint string) error {
	if s == nil || s.db == nil {
		return ErrPushUnavailable
	}
	return s.db.WithContext(ctx).Where("id = ? AND user_id = ?", pushSubscriptionID(endpoint), userID).Delete(&model.PushSubscription{}).Error
}

// Subscribed reports whether this browser is on for the signed-in account.
func (s *PushService) Subscribed(ctx context.Context, userID, endpoint string) (bool, error) {
	if s == nil || s.db == nil {
		return false, nil
	}
	var count int64
	err := s.db.WithContext(ctx).Model(&model.PushSubscription{}).Where("id = ? AND user_id = ?", pushSubscriptionID(endpoint), userID).Count(&count).Error
	return count > 0, err
}

type pushTitle struct {
	OriginalTitle string
	EnglishTitle  string
}

type pushMessage struct {
	Title string `json:"title"`
	Body  string `json:"body"`
	URL   string `json:"url"`
	Tag   string `json:"tag"`
}

// digestMessage words the notification in the subscriber's language. titles
// are the newest few of count publications.
func digestMessage(language string, count int, titles []pushTitle) pushMessage {
	names := make([]string, 0, len(titles))
	for _, title := range titles {
		name := strings.TrimSpace(title.OriginalTitle)
		if language == "en" && strings.TrimSpace(title.EnglishTitle) != "" {
			name = strings.TrimSpace(title.EnglishTitle)
		}
		if runes := []rune(name); len(runes) > 60 {
			name = string(runes[:59]) + "…"
		}
		if name != "" {
			names = append(names, name)
		}
	}
	more := count - len(names)
	var title, body string
	switch language {
	case "ja":
		title, body = "MuseBooksの新着", fmt.Sprintf("新着%d件：%s", count, strings.Join(names, "、"))
		if more > 0 {
			body += fmt.Sprintf(" ほか%d件", more)
		}
	case "zh-Hans":
		title, body = "MuseBooks 新收录", fmt.Sprintf("新增 %d 本：%s", count, strings.Join(names, "、"))
		if more > 0 {
			body += " 等"
		}
	case "zh-Hant":
		title, body = "MuseBooks 新收錄", fmt.Sprintf("新增 %d 本：%s", count, strings.Join(names, "、"))
		if more > 0 {
			body += " 等"
		}
	default:
		noun := "publications"
		if count == 1 {
			noun = "publication"
		}
		title, body = "New on MuseBooks", fmt.Sprintf("%d new %s: %s", count, noun, strings.Join(names, ", "))
		if more > 0 {
			body += fmt.Sprintf(" and %d more", more)
		}
	}
	// The home page lists the newest publications; new book pages are only
	// published with the next site build.
	return pushMessage{Title: title, Body: body, URL: "/", Tag: pushTopic}
}

// SendNewPublicationDigest notifies every subscriber about works published
// since the previous run. The first run only records the starting point, and
// a run within 20 hours of the last one does nothing, so restarts and several
// API processes never send twice.
func (s *PushService) SendNewPublicationDigest(ctx context.Context) (count, delivered int, err error) {
	if !s.Enabled() {
		return 0, 0, ErrPushUnavailable
	}
	now := s.now().UTC()
	var titles []pushTitle
	var digest model.PushDigest
	err = s.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		if err := tx.Exec("SELECT pg_advisory_xact_lock(hashtext('musebooks:push-digest'))").Error; err != nil {
			return err
		}
		var last model.PushDigest
		found := tx.Order("through DESC").Limit(1).Find(&last)
		if found.Error != nil {
			return found.Error
		}
		if found.RowsAffected == 0 {
			return tx.Create(&model.PushDigest{Through: now}).Error
		}
		if now.Sub(last.Through) < pushDigestMinGap {
			return nil
		}
		works := tx.Model(&model.Work{}).Where("status = ? AND created_at > ? AND created_at <= ?", "published", last.Through, now)
		var total int64
		if err := works.Count(&total).Error; err != nil {
			return err
		}
		if err := works.Order("created_at DESC").Limit(2).Select("original_title, english_title").Scan(&titles).Error; err != nil {
			return err
		}
		count = int(total)
		digest = model.PushDigest{Through: now, Count: count}
		return tx.Create(&digest).Error
	})
	if err != nil || count == 0 {
		return count, 0, err
	}
	delivered, err = s.deliver(ctx, func(language string) pushMessage { return digestMessage(language, count, titles) })
	if digest.ID != 0 {
		s.db.WithContext(ctx).Model(&model.PushDigest{}).Where("id = ?", digest.ID).Update("delivered", delivered)
	}
	return count, delivered, err
}

// deliver sends one message per subscription, a batch at a time.
func (s *PushService) deliver(ctx context.Context, message func(language string) pushMessage) (int, error) {
	payloads := map[string][]byte{}
	for _, language := range []string{"en", "ja", "zh-Hans", "zh-Hant"} {
		payload, err := json.Marshal(message(language))
		if err != nil {
			return 0, err
		}
		payloads[language] = payload
	}
	var delivered int
	var mu sync.Mutex
	after := ""
	for {
		var batch []model.PushSubscription
		if err := s.db.WithContext(ctx).Where("id > ?", after).Order("id").Limit(pushBatchSize).Find(&batch).Error; err != nil {
			return delivered, err
		}
		if len(batch) == 0 {
			return delivered, nil
		}
		after = batch[len(batch)-1].ID
		jobs := make(chan model.PushSubscription)
		var wg sync.WaitGroup
		for range pushWorkers {
			wg.Add(1)
			go func() {
				defer wg.Done()
				for sub := range jobs {
					if s.send(ctx, sub, payloads[pushLanguage(sub.Language)]) {
						mu.Lock()
						delivered++
						mu.Unlock()
					}
				}
			}()
		}
		for _, sub := range batch {
			jobs <- sub
		}
		close(jobs)
		wg.Wait()
		if ctx.Err() != nil {
			return delivered, ctx.Err()
		}
	}
}

// send delivers one message. A subscription the push service reports gone
// (404/410) is deleted; one that keeps failing is dropped after 5 tries.
func (s *PushService) send(ctx context.Context, sub model.PushSubscription, payload []byte) bool {
	if !ValidPushEndpoint(sub.Endpoint) {
		s.db.WithContext(ctx).Delete(&model.PushSubscription{}, "id = ?", sub.ID)
		return false
	}
	resp, err := webpush.SendNotificationWithContext(ctx, payload, &webpush.Subscription{Endpoint: sub.Endpoint, Keys: webpush.Keys{P256dh: sub.P256dh, Auth: sub.Auth}}, &webpush.Options{
		HTTPClient: s.client, Subscriber: s.cfg.Subject, VAPIDPublicKey: s.cfg.PublicKey, VAPIDPrivateKey: s.cfg.PrivateKey,
		TTL: 24 * 60 * 60, Urgency: webpush.UrgencyNormal, Topic: pushTopic,
	})
	status := 0
	if resp != nil {
		status = resp.StatusCode
		io.Copy(io.Discard, io.LimitReader(resp.Body, 4096))
		resp.Body.Close()
	}
	switch {
	case err == nil && status >= 200 && status < 300:
		if sub.Failures > 0 {
			s.db.WithContext(ctx).Model(&model.PushSubscription{}).Where("id = ?", sub.ID).Update("failures", 0)
		}
		return true
	case status == http.StatusNotFound || status == http.StatusGone:
		s.db.WithContext(ctx).Delete(&model.PushSubscription{}, "id = ?", sub.ID)
	case sub.Failures+1 >= pushMaxFailures:
		s.db.WithContext(ctx).Delete(&model.PushSubscription{}, "id = ?", sub.ID)
	default:
		s.db.WithContext(ctx).Model(&model.PushSubscription{}).Where("id = ?", sub.ID).Update("failures", gorm.Expr("failures + 1"))
	}
	return false
}

// NextPushDigest is the next 10:00 Malaysia time after now.
func NextPushDigest(now time.Time) time.Time {
	now = now.UTC()
	next := time.Date(now.Year(), now.Month(), now.Day(), pushDigestHourUTC, 0, 0, 0, time.UTC)
	if !next.After(now) {
		next = next.AddDate(0, 0, 1)
	}
	return next
}

// Run sends the digest every day at 10:00 Malaysia time until ctx ends. On
// a new database it first records where the first digest starts, so the
// existing catalog is not announced.
func (s *PushService) Run(ctx context.Context) {
	if !s.Enabled() {
		return
	}
	var digests int64
	if err := s.db.WithContext(ctx).Model(&model.PushDigest{}).Count(&digests).Error; err != nil {
		log.Printf("[push] notifications off: %v", err)
		return
	}
	if digests == 0 {
		if _, _, err := s.SendNewPublicationDigest(ctx); err != nil {
			log.Printf("[push] record digest starting point: %v", err)
		}
	}
	for {
		select {
		case <-ctx.Done():
			return
		case <-time.After(time.Until(NextPushDigest(s.now()))):
		}
		count, delivered, err := s.SendNewPublicationDigest(ctx)
		if err != nil {
			log.Printf("[push] new-publications digest failed after %d delivered: %v", delivered, err)
		} else if count > 0 {
			log.Printf("[push] new-publications digest: %d publications, %d devices", count, delivered)
		}
	}
}
