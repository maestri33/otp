"""
Dependencias reutilizaveis (FastAPI Depends).

Exemplos uteis: cliente HTTP compartilhado, redis, autenticacao.
Por enquanto a DMZ permite que a maioria fique sem auth.
"""

from typing import AsyncIterator

from app.integrations.http_client import get_http_client
from app.integrations.redis_client import get_redis_client


async def http_client_dep() -> AsyncIterator:
    """Disponibiliza um httpx.AsyncClient compartilhado."""
    async for client in get_http_client():
        yield client


async def redis_dep() -> AsyncIterator:
    """Disponibiliza a conexao redis.asyncio."""
    async for r in get_redis_client():
        yield r
