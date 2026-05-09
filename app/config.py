"""
Application config — reads .env via pydantic-settings.

All external configuration flows through here.
Never read env vars directly outside this module.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service identity
    service_name: str = "otp"
    env: Literal["dev", "staging", "prod"] = "dev"
    log_level: str = "INFO"
    port: int = 80

    # Database
    database_url: str = "sqlite://data/app.db"

    # External notify service
    notify_base_url: str = "http://10.10.10.144"

    # OTP
    otp_footer: str = "Equipe OTP"
    otp_ttl_s: int = 300
    otp_num_digits: int = 6
    otp_max_attempts: int = 3
    otp_active: bool = True


@lru_cache
def get_settings() -> Settings:
    """Settings singleton — one instance per process."""
    return Settings()
