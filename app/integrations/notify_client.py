"""
HTTP client for the notify service (10.10.10.157).

Only `send_message` is used by the OTP service.
"""

from typing import Any

import httpx

from app.config import get_settings
from app.exceptions import IntegrationError
from app.integrations.http_client import request_with_retry


def _safe_json(resp: httpx.Response) -> dict | list:
    """Parse JSON safely — returns dict on non-JSON body."""
    try:
        return resp.json()
    except ValueError:
        return {"error": resp.text.strip() or f"HTTP {resp.status_code}"}


def _url(path: str) -> str:
    return f"{get_settings().notify_base_url}{path}"


async def send_message(
    client: httpx.AsyncClient,
    *,
    external_id: str,
    content: str,
    media_url: str | None = None,
    flags: dict | None = None,
    instruction: str | None = None,
) -> dict:
    """Send a message to a contact via notify."""
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
