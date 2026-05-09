"""
HTTP client for the notify service (10.10.10.157).

High-level wrapper over httpx — all calls to notify go through here.
Do NOT scatter httpx.get/post to notify throughout the code.
"""

from typing import Any

import httpx

from app.config import get_settings
from app.exceptions import IntegrationError
from app.integrations.http_client import request_with_retry
from app.utils.logging import get_logger

log = get_logger(__name__)


def _safe_json(resp: httpx.Response) -> dict | list:
    """Parse JSON safely — returns empty dict on non-JSON body."""
    try:
        return resp.json()
    except ValueError:
        return {"error": resp.text.strip() or f"HTTP {resp.status_code}"}


def _url(path: str) -> str:
    return f"{get_settings().notify_base_url}{path}"


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


async def health(client: httpx.AsyncClient) -> dict:
    resp = await request_with_retry(client, "GET", _url("/health"))
    return _safe_json(resp)


async def ready(client: httpx.AsyncClient) -> dict:
    resp = await request_with_retry(client, "GET", _url("/ready"))
    return _safe_json(resp)


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------


async def check_contact(
    client: httpx.AsyncClient,
    *,
    phone: str | None = None,
    email: str | None = None,
) -> dict:
    params = {}
    if phone:
        params["phone"] = phone
    if email:
        params["email"] = email
    resp = await request_with_retry(client, "GET", _url("/contacts/check"), params=params)
    return _safe_json(resp)


async def create_contact(
    client: httpx.AsyncClient,
    *,
    external_id: str,
    phone: str | None = None,
) -> dict:
    body: dict[str, Any] = {"external_id": external_id, "phone": phone or external_id}
    resp = await request_with_retry(client, "POST", _url("/contacts"), json=body)
    return _safe_json(resp)


async def list_contacts(
    client: httpx.AsyncClient,
    *,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    resp = await request_with_retry(
        client, "GET", _url("/contacts"), params={"limit": limit, "offset": offset}
    )
    return _safe_json(resp)


async def get_contact(client: httpx.AsyncClient, external_id: str) -> dict:
    resp = await request_with_retry(client, "GET", _url(f"/contacts/{external_id}"))
    return _safe_json(resp)


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------


async def send_message(
    client: httpx.AsyncClient,
    *,
    external_id: str,
    content: str,
    media_url: str | None = None,
    flags: dict | None = None,
    instruction: str | None = None,
) -> dict:
    body: dict[str, Any] = {"external_id": external_id, "content": content}
    if media_url:
        body["media_url"] = media_url
    if flags:
        body["flags"] = flags
    if instruction:
        body["instruction"] = instruction
    resp = await request_with_retry(client, "POST", _url("/messages/send"), json=body)
    if resp.status_code >= 400:
        detail = _safe_json(resp)
        raise IntegrationError(
            f"Notify send_message failed ({resp.status_code}): {detail}"
        )
    return _safe_json(resp)


async def list_messages(
    client: httpx.AsyncClient,
    *,
    contact_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    if contact_id is not None:
        params["contact_id"] = contact_id
    resp = await request_with_retry(client, "GET", _url("/messages"), params=params)
    return _safe_json(resp)


async def get_message(client: httpx.AsyncClient, message_id: int) -> dict:
    resp = await request_with_retry(client, "GET", _url(f"/messages/{message_id}"))
    return _safe_json(resp)


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------


async def get_email_template(client: httpx.AsyncClient) -> dict:
    resp = await request_with_retry(client, "GET", _url("/templates/email"))
    return _safe_json(resp)


async def update_email_template(
    client: httpx.AsyncClient,
    *,
    html: str | None = None,
    instruction: str | None = None,
) -> dict:
    body: dict[str, Any] = {}
    if html is not None:
        body["html"] = html
    if instruction is not None:
        body["instruction"] = instruction
    resp = await request_with_retry(client, "PUT", _url("/templates/email"), json=body)
    return _safe_json(resp)


# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------


async def list_logs(
    client: httpx.AsyncClient,
    *,
    message_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    if message_id is not None:
        params["message_id"] = message_id
    resp = await request_with_retry(client, "GET", _url("/logs"), params=params)
    return _safe_json(resp)
