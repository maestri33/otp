"""Health/readiness endpoints — used by load balancer and Proxmox."""

from fastapi import APIRouter
from tortoise import connections

from app.config import get_settings

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    """Liveness — the process is alive."""
    return {"status": "ok", "service": get_settings().service_name}


@router.get("/ready")
async def ready() -> dict:
    """Readiness — ready to receive traffic.

    Verifica conectividade com o banco. Retorna 200 se ok, 503 se não.
    """
    try:
        conn = connections.get("default")
        await conn.execute_query("SELECT 1")
        return {"status": "ready"}
    except Exception as exc:
        return {"status": "not_ready", "detail": str(exc)}
