package service

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"strings"
	"time"
)

var ErrEmailDelivery = errors.New("verification email could not be delivered")

type VerificationEmailSender interface {
	SendVerificationCode(ctx context.Context, to, code string) error
	SendPasswordResetCode(ctx context.Context, to, code string) error
	SendAccountExistsNotice(ctx context.Context, to string) error
}

// ResendEmailSender sends verification messages through Resend's HTTP API.
// The API key stays in backend configuration and is never returned to clients.
type ResendEmailSender struct {
	apiKey string
	from   string
	client *http.Client
}

func NewResendEmailSender(apiKey, from string) *ResendEmailSender {
	return &ResendEmailSender{
		apiKey: strings.TrimSpace(apiKey),
		from:   strings.TrimSpace(from),
		client: &http.Client{Timeout: 10 * time.Second},
	}
}

func (s *ResendEmailSender) Configured() bool {
	return s != nil && s.apiKey != "" && s.from != ""
}

func (s *ResendEmailSender) SendVerificationCode(ctx context.Context, to, code string) error {
	return s.send(ctx, to, "Verify your MuseBooks email",
		fmt.Sprintf("Your MuseBooks verification code is %s. It expires in 10 minutes.", code),
		fmt.Sprintf("<p>Your MuseBooks verification code is:</p><p style=\"font-size:28px;font-weight:700;letter-spacing:6px\">%s</p><p>This code expires in 10 minutes. If you did not create an account, you can ignore this email.</p>", code))
}

func (s *ResendEmailSender) SendPasswordResetCode(ctx context.Context, to, code string) error {
	return s.send(ctx, to, "Reset your MuseBooks password",
		fmt.Sprintf("Your MuseBooks password reset code is %s. It expires in 15 minutes. If you did not ask to reset your password, you can ignore this email; your password has not changed.", code),
		fmt.Sprintf("<p>Your MuseBooks password reset code is:</p><p style=\"font-size:28px;font-weight:700;letter-spacing:6px\">%s</p><p>This code expires in 15 minutes. If you did not ask to reset your password, you can ignore this email; your password has not changed.</p>", code))
}

// SendAccountExistsNotice answers a sign-up for an address that already has
// an account, so the sign-up response itself never reveals that fact.
func (s *ResendEmailSender) SendAccountExistsNotice(ctx context.Context, to string) error {
	return s.send(ctx, to, "You already have a MuseBooks account",
		"Someone tried to create a MuseBooks account with this email, but you already have one. Sign in instead, or use \"Forgot password?\" on the sign-in page to choose a new password. If this wasn't you, you can ignore this email.",
		"<p>Someone tried to create a MuseBooks account with this email, but you already have one.</p><p>Sign in instead, or use <strong>Forgot password?</strong> on the sign-in page to choose a new password.</p><p>If this wasn't you, you can ignore this email.</p>")
}

func (s *ResendEmailSender) send(ctx context.Context, to, subject, text, html string) error {
	if !s.Configured() {
		return errors.New("Resend email is not configured")
	}
	payload := struct {
		From    string   `json:"from"`
		To      []string `json:"to"`
		Subject string   `json:"subject"`
		Text    string   `json:"text"`
		HTML    string   `json:"html"`
	}{
		From:    s.from,
		To:      []string{to},
		Subject: subject,
		Text:    text,
		HTML:    html,
	}
	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("encode email: %w", err)
	}
	request, err := http.NewRequestWithContext(ctx, http.MethodPost, "https://api.resend.com/emails", bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("create Resend request: %w", err)
	}
	request.Header.Set("Authorization", "Bearer "+s.apiKey)
	request.Header.Set("Content-Type", "application/json")
	response, err := s.client.Do(request)
	if err != nil {
		return fmt.Errorf("send email: %w", err)
	}
	defer response.Body.Close()
	if response.StatusCode < http.StatusOK || response.StatusCode >= http.StatusMultipleChoices {
		return fmt.Errorf("Resend returned status %d", response.StatusCode)
	}
	return nil
}
