"""
Router agregador.

Toda feature nova adiciona seu router aqui via include_router.
"""

from fastapi import APIRouter

from app.api import example, health, webhooks_inbound

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(example.router, prefix="/items", tags=["items"])
api_router.include_router(webhooks_inbound.router, prefix="/webhooks", tags=["webhooks"])
