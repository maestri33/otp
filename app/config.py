"""
Application config — reads .env via pydantic-settings.

All external configuration (DB URL, broker, Redis, secrets) flows through here.
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

    # Database — each service owns its own
    database_url: str = "sqlite://data/app.db"

    # Redis (cache + lightweight pub/sub)
    redis_url: str = "redis://localhost:6379/0"

    # RabbitMQ / AMQP (message broker)
    broker_url: str = "amqp://guest:guest@localhost:5672/"

    # External notify service
    notify_base_url: str = "http://10.10.10.144"

    # Webhooks
    webhook_outbound_timeout_s: int = 10


@lru_cache
def get_settings() -> Settings:
    """Settings singleton — one instance per process."""
    return Settings()
