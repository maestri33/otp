"""
Notification service — business layer for the external notify (10.10.10.157).

Uses `app.integrations.notify_client` for all HTTP calls.
Does not know about FastAPI. Raises `DomainError` on failure.
"""

import httpx

from app.integrations import notify_client as client
from app.utils.logging import get_logger

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Contacts
# ---------------------------------------------------------------------------


async def check_contact(
    http: httpx.AsyncClient,
    *,
    phone: str | None = None,
    email: str | None = None,
) -> dict:
    """Check whether a contact exists in notify, validating phone/email."""
    log.info("notify.contact.check", phone=phone, email=email)
    return await client.check_contact(http, phone=phone, email=email)


async def create_contact(
    http: httpx.AsyncClient,
    *,
    external_id: str,
    phone: str | None = None,
) -> dict:
    """Create a contact in notify."""
    log.info("notify.contact.create", external_id=external_id)
    return await client.create_contact(
        http, external_id=external_id, phone=phone
    )


async def get_contact(http: httpx.AsyncClient, external_id: str) -> dict:
    """Fetch a contact by external_id."""
    log.info("notify.contact.get", external_id=external_id)
    return await client.get_contact(http, external_id)


async def list_contacts(
    http: httpx.AsyncClient, *, limit: int = 50, offset: int = 0
) -> list[dict]:
    """List contacts with pagination."""
    return await client.list_contacts(http, limit=limit, offset=offset)


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------


async def send_message(
    http: httpx.AsyncClient,
    *,
    external_id: str,
    content: str,
    media_url: str | None = None,
    with_ai: bool = False,
    with_tts: bool = False,
    with_image: bool = False,
    instruction: str | None = None,
) -> dict:
    """Send a message to a contact via notify.

    Flags:
        with_ai: AI-powered response
        with_tts: text-to-speech audio
        with_image: image generation
    """
    flags = {"ai": with_ai, "tts": with_tts, "img": with_image}
    log.info(
        "notify.message.send",
        external_id=external_id,
        flags=flags,
    )
    return await client.send_message(
        http,
        external_id=external_id,
        content=content,
        media_url=media_url,
        flags=flags,
        instruction=instruction,
    )


async def list_messages(
    http: httpx.AsyncClient,
    *,
    contact_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """List messages, optionally filtered by contact_id."""
    return await client.list_messages(
        http, contact_id=contact_id, limit=limit, offset=offset
    )


async def get_message(http: httpx.AsyncClient, message_id: int) -> dict:
    """Fetch a message by id."""
    log.info("notify.message.get", message_id=message_id)
    return await client.get_message(http, message_id)


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------


async def get_email_template(http: httpx.AsyncClient) -> dict:
    """Return the current email template."""
    return await client.get_email_template(http)


async def update_email_template(
    http: httpx.AsyncClient,
    *,
    html: str | None = None,
    instruction: str | None = None,
) -> dict:
    """Update the email template."""
    log.info("notify.template.update")
    return await client.update_email_template(
        http, html=html, instruction=instruction
    )


# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------


async def list_logs(
    http: httpx.AsyncClient,
    *,
    message_id: int | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """List logs, optionally filtered by message_id."""
    return await client.list_logs(
        http, message_id=message_id, limit=limit, offset=offset
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


async def health(http: httpx.AsyncClient) -> dict:
    """Check whether the notify service is alive."""
    return await client.health(http)


async def ready(http: httpx.AsyncClient) -> dict:
    """Check whether the notify service is ready for traffic."""
    return await client.ready(http)
