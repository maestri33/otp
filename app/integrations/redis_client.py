"""
Cliente Redis async — cache + pub/sub leve.

Use o Redis para:
- Cache (get/set com TTL).
- Pub/Sub leve entre instancias (notificacoes, invalidate cache).

NAO use Redis como fila de tarefas duraveis — pra isso, RabbitMQ.
"""

from typing import AsyncIterator

import redis.asyncio as redis

from app.config import get_settings


async def get_redis_client() -> AsyncIterator[redis.Redis]:
    """Yielda uma conexao Redis. Use como Depends() no FastAPI."""
    settings = get_settings()
    r = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        yield r
    finally:
        await r.aclose()


async def cache_get(key: str) -> str | None:
    settings = get_settings()
    r = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        return await r.get(key)
    finally:
        await r.aclose()


async def cache_set(key: str, value: str, ttl_s: int = 60) -> None:
    settings = get_settings()
    r = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await r.set(key, value, ex=ttl_s)
    finally:
        await r.aclose()


async def publish(channel: str, message: str) -> int:
    """Publica em um canal pub/sub. Retorna o numero de subscribers."""
    settings = get_settings()
    r = redis.from_url(settings.redis_url, decode_responses=True)
    try:
        return await r.publish(channel, message)
    finally:
        await r.aclose()
