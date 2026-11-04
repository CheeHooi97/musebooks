package handler

import (
	"errors"
	"net/http"

	"github.com/labstack/echo/v4"

	"musebooks/model"
	"musebooks/service"
)

// Notifications for new publications. As with MuseCards alerts, turning them
// on needs a signed-in account; the subscription is stored for that account.

type pushSubscriptionRequest struct {
	Endpoint string `json:"endpoint"`
	Keys     struct {
		P256dh string `json:"p256dh"`
		Auth   string `json:"auth"`
	} `json:"keys"`
	Language string `json:"language"`
}

func (h *Handler) pushUser(c echo.Context) (*model.User, error) {
	user, err := h.Auth.CurrentUser(c.Request().Context(), authToken(c))
	if err != nil || user == nil {
		return nil, authFailure(c, http.StatusUnauthorized, "Sign in to turn on notifications.", "session_expired")
	}
	return user, nil
}

// PushConfig tells the browser whether notifications are available and which
// key the server signs with. It is public.
func (h *Handler) PushConfig(c echo.Context) error {
	return responseJSON(c, map[string]any{"enabled": h.Push.Enabled(), "publicKey": h.Push.PublicKey()})
}

// PushStatus reports whether this browser is on for the signed-in account.
func (h *Handler) PushStatus(c echo.Context) error {
	user, err := h.pushUser(c)
	if user == nil {
		return err
	}
	on, err := h.Push.Subscribed(c.Request().Context(), user.Id, c.QueryParam("endpoint"))
	if err != nil {
		return authFailure(c, http.StatusServiceUnavailable, "Notifications are unavailable right now.", "push_unavailable")
	}
	return responseJSON(c, map[string]any{"subscribed": on})
}

func (h *Handler) PushSubscribe(c echo.Context) error {
	user, err := h.pushUser(c)
	if user == nil {
		return err
	}
	var input pushSubscriptionRequest
	if err := c.Bind(&input); err != nil {
		return authFailure(c, http.StatusBadRequest, "This browser's notification details were not accepted.", "invalid_subscription")
	}
	switch err := h.Push.Subscribe(c.Request().Context(), user.Id, input.Endpoint, input.Keys.P256dh, input.Keys.Auth, input.Language); {
	case err == nil:
		return responseJSON(c, map[string]any{"subscribed": true})
	case errors.Is(err, service.ErrInvalidPushSubscription):
		return authFailure(c, http.StatusBadRequest, "This browser's notification details were not accepted.", "invalid_subscription")
	case errors.Is(err, service.ErrPushDeviceLimit):
		return authFailure(c, http.StatusConflict, "Notifications are on for too many devices. Turn them off on one first.", "device_limit")
	default:
		return authFailure(c, http.StatusServiceUnavailable, "Notifications are unavailable right now.", "push_unavailable")
	}
}

func (h *Handler) PushUnsubscribe(c echo.Context) error {
	user, err := h.pushUser(c)
	if user == nil {
		return err
	}
	var input pushSubscriptionRequest
	if err := c.Bind(&input); err != nil || input.Endpoint == "" {
		return authFailure(c, http.StatusBadRequest, "Missing notification details.", "invalid_subscription")
	}
	if err := h.Push.Unsubscribe(c.Request().Context(), user.Id, input.Endpoint); err != nil {
		return authFailure(c, http.StatusServiceUnavailable, "Notifications are unavailable right now.", "push_unavailable")
	}
	return responseJSON(c, map[string]any{"subscribed": false})
}
