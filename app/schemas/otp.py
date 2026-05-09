"""Pydantic schemas for OTP."""

from datetime import datetime

from pydantic import BaseModel, Field


class OTPCreate(BaseModel):
    external_id: str = Field(min_length=1, max_length=255)


class OTPCheck(BaseModel):
    external_id: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=10)


class OTPCheckResponse(BaseModel):
    valid: bool
    detail: str = "ok"


class OTPRead(BaseModel):
    id: int
    external_id: str
    status: str
    message_id: int | None = None
    error_detail: str | None = None
    verified_at: datetime | None = None
    created_at: datetime


class OTPLogFilter(BaseModel):
    external_id: str | None = None
    status: str | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
