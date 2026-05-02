"""
Webhooks de saida.

Para webhooks de ENTRADA, ver `app/api/webhooks_inbound.py`.

Aqui ficam emissores: este servico avisa um sistema externo de que algo
aconteceu. Idealmente fazemos com retry + dead-letter (uma fila propria);
por simplicidade o template faz fire-and-forget com retry curto.
"""

from typing import Any

import httpx

from app.config import get_settings
from app.exceptions import IntegrationError
from app.integrations.http_client import request_with_retry
from app.utils.logging import get_logger

log = get_logger(__name__)


async def send_webhook(target_url: str, payload: dict[str, Any]) -> None:
    """Dispara um webhook para um destino externo."""
    settings = get_settings()
    timeout = httpx.Timeout(settings.webhook_outbound_timeout_s, connect=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await request_with_retry(
            client,
            "POST",
            target_url,
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code >= 400:
            log.warning("webhook.failed", url=target_url, status=resp.status_code)
            raise IntegrationError(
                f"Webhook para {target_url} falhou ({resp.status_code})"
            )
        log.info("webhook.sent", url=target_url, status=resp.status_code)
