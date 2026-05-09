"""
Status endpoint — GET /status returns real service state as JSON.
"""

import time
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter
from tortoise import connections

from app.config import get_settings
from app.models.otp import OTPLog

router = APIRouter()
settings = get_settings()
_STARTED_AT = time.time()


def _uptime_s() -> int:
    return int(time.time() - _STARTED_AT)


async def _db_status() -> dict:
    try:
        conn = connections.get("default")
        await conn.execute_query("SELECT 1")
        return {"ok": True, "detail": "conectado"}
    except Exception as exc:
        return {"ok": False, "detail": str(exc)}


async def _notify_status(http: httpx.AsyncClient) -> dict:
    try:
        resp = await http.get(f"{settings.notify_base_url}/health", timeout=5)
        return {"ok": resp.status_code == 200, "detail": resp.json().get("service", str(resp.status_code))}
    except Exception as exc:
        return {"ok": False, "detail": str(exc)}


async def _otp_stats() -> dict:
    rows = await OTPLog.all()
    by_status = {"generated": 0, "sent": 0, "verified": 0, "failed": 0, "expired": 0}
    for r in rows:
        if r.status in by_status:
            by_status[r.status] += 1
    return {"total": len(rows), "by_status": by_status}


@router.get("/status")
async def status() -> dict:
    db = await _db_status()

    async with httpx.AsyncClient(timeout=5) as http:
        notify = await _notify_status(http)

    stats = await _otp_stats()
    recent = (
        await OTPLog.all().order_by("-created_at").limit(10)
    )

    return {
        "service": settings.service_name,
        "env": settings.env,
        "uptime_s": _uptime_s(),
        "config": {
            "footer": settings.otp_footer,
            "ttl_s": settings.otp_ttl_s,
            "num_digits": settings.otp_num_digits,
            "max_attempts": settings.otp_max_attempts,
            "active": settings.otp_active,
        },
        "connections": {
            "database": db,
            "notify": notify,
        },
        "otp_stats": stats,
        "recent_logs": [
            {
                "id": r.id,
                "external_id": r.external_id,
                "status": r.status,
                "message_id": r.message_id,
                "error_detail": r.error_detail,
                "verified_at": r.verified_at.isoformat() if r.verified_at else None,
                "created_at": r.created_at.isoformat(),
            }
            for r in recent
        ],
        "queried_at": datetime.now(timezone.utc).isoformat(),
    }
