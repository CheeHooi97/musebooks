package handler

import (
	"musebooks/utils"

	"github.com/labstack/echo/v4"
)

func (h *Handler) SearchUser(c echo.Context) error {
	var i struct {
		Username  string `json:"username" validate:"required"`
		SupportId string `json:"supportId" validate:"required"`
	}

	if msg, err := utils.ValidateRequest(c, &i); err != nil {
		return responseValidationError(c, msg)
	}

	return responseJSON(c, nil)
}
