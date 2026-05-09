"""Pydantic schemas for OTP configuration."""

from datetime import datetime

from pydantic import BaseModel, Field


class OTPConfigRead(BaseModel):
    id: int
    footer: str
    ttl_s: int
    num_digits: int
    max_attempts: int
    active: bool
    updated_at: datetime


class OTPConfigUpdate(BaseModel):
    footer: str | None = Field(default=None, max_length=255)
    ttl_s: int | None = Field(default=None, ge=30, le=3600)
    num_digits: int | None = Field(default=None, ge=4, le=10)
    max_attempts: int | None = Field(default=None, ge=1, le=10)
    active: bool | None = None
