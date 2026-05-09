"""
OTP service — generates authentication codes, sends via notify, and validates.

Flow:
  1. POST /otp → generate_code() → save OTPLog(status=generated) →
     render otp.md template → notify.send_message() → update status=sent.
  2. POST /otp/check → find latest unexpired OTP → validate →
     update status=verified (or expired/failed).
  3. GET /otp, GET /otp/logs → query OTPLog with filters.

Configuration is read from env vars (Settings), not the database.
"""

import hashlib
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from app.config import get_settings
from app.models.otp import OTPLog
from app.services import notify
from app.utils.logging import get_logger

log = get_logger(__name__)
settings = get_settings()

_TEMPLATE_PATH = Path(__file__).parent / "otp.md"


# ---------------------------------------------------------------------------
# Code generation and hashing
# ---------------------------------------------------------------------------


def generate_code(length: int | None = None) -> str:
    """Generate a secure numeric code of `length` digits."""
    n = length or settings.otp_num_digits
    return "".join(str(secrets.randbelow(10)) for _ in range(n))


def _hash_code(code: str) -> str:
    """SHA256 of the code — plain-text code is never stored."""
    return hashlib.sha256(code.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Message template
# ---------------------------------------------------------------------------


def _render_template(code: str, footer: str) -> str:
    """Render the otp.md template replacing variables.

    Available template variables:
      {{codigo}} — the generated code
      {{rodape}} — optional footer text
    """
    raw = _TEMPLATE_PATH.read_text(encoding="utf-8")
    return raw.replace("{{codigo}}", code).replace("{{rodape}}", footer)


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------


async def generate_and_send(
    http: httpx.AsyncClient,
    *,
    external_id: str,
) -> OTPLog:
    """Generate an OTP, persist it, and send the formatted message via notify.

    Returns the created OTPLog.
    """
    if not settings.otp_active:
        log.warning("otp.generate.blocked", external_id=external_id)
        return await OTPLog.create(
            external_id=external_id,
            code_hash="",
            status="failed",
            error_detail="Serviço OTP desativado na configuração",
        )

    log.info("otp.generate.requested", external_id=external_id)
    code = generate_code()

    # 1. Persist as "generated"
    otp_log = await OTPLog.create(
        external_id=external_id,
        code_hash=_hash_code(code),
        status="generated",
    )
    log.info("otp.generated", id=otp_log.id, external_id=external_id)

    # 2. Render template and send via notify
    content = _render_template(code, footer=settings.otp_footer)

    try:
        result = await notify.send_message(
            http,
            external_id=external_id,
            content=content,
        )
        otp_log.status = "sent"
        otp_log.message_id = result.get("id")
        await otp_log.save()
        log.info("otp.sent", id=otp_log.id, message_id=otp_log.message_id)

    except Exception as exc:
        otp_log.status = "failed"
        otp_log.error_detail = str(exc)
        await otp_log.save()
        log.error("otp.send_failed", id=otp_log.id, error=str(exc))

    return otp_log


async def verify_code(
    http: httpx.AsyncClient,
    *,
    external_id: str,
    code: str,
) -> dict:
    """Validate an OTP code against the latest unexpired log.

    Returns {"valid": true/false, "detail": "..."}
    """
    if not settings.otp_active:
        log.warning("otp.verify.blocked", external_id=external_id)
        return {"valid": False, "detail": "Serviço OTP desativado"}

    log.info("otp.verify.requested", external_id=external_id)

    # Find the most recent OTP for this external_id that hasn't been used
    otp_log = (
        await OTPLog.filter(external_id=external_id, status="sent")
        .order_by("-created_at")
        .first()
    )

    if otp_log is None:
        log.info("otp.check.no_pending_otp", external_id=external_id)
        return {"valid": False, "detail": "Nenhum OTP pendente encontrado"}

    # Check time-based expiration
    age_s = time.time() - otp_log.created_at.timestamp()
    if age_s > settings.otp_ttl_s:
        otp_log.status = "expired"
        await otp_log.save()
        log.info("otp.check.expired", id=otp_log.id, age_s=age_s)
        return {"valid": False, "detail": "OTP expirado"}

    # Compare hash
    if not secrets.compare_digest(otp_log.code_hash, _hash_code(code)):
        log.info("otp.check.invalid_code", id=otp_log.id)
        return {"valid": False, "detail": "Código inválido"}

    # Success — mark as verified
    otp_log.status = "verified"
    otp_log.verified_at = datetime.now(timezone.utc)
    await otp_log.save()
    log.info("otp.check.verified", id=otp_log.id, external_id=external_id)
    return {"valid": True, "detail": "ok"}


async def list_logs(
    *,
    external_id: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[OTPLog]:
    """List OTP logs with optional filters."""
    qs = OTPLog.all()
    if external_id:
        qs = qs.filter(external_id=external_id)
    if status:
        qs = qs.filter(status=status)
    return await qs.order_by("-created_at").offset(offset).limit(limit)
