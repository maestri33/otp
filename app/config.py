"""
Configuracao do servico — leitura do .env via pydantic-settings.

Tudo que vier de fora (URL de banco, broker, redis, secrets) passa por aqui.
Nao leia env var direto fora deste modulo.
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

    # Identificacao do servico
    service_name: str = "microservice-template"
    env: Literal["dev", "staging", "prod"] = "dev"
    log_level: str = "INFO"
    port: int = 80

    # Banco — cada servico tem o seu proprio
    database_url: str = "sqlite://data/app.db"

    # Redis (cache + pub/sub leve)
    redis_url: str = "redis://localhost:6379/0"

    # RabbitMQ / AMQP (fila de mensagens)
    broker_url: str = "amqp://guest:guest@localhost:5672/"

    # Webhooks
    webhook_outbound_timeout_s: int = 10


@lru_cache
def get_settings() -> Settings:
    """Settings singleton — uma instancia por processo."""
    return Settings()
