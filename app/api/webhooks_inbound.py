"""
Webhooks de entrada.

Endpoint generico que aceita payload de outros sistemas, valida o minimo
e despacha pra um handler em `app/services/`. Ajuste por origem.
"""

from fastapi import APIRouter, Request, status

from app.utils.logging import get_logger

router = APIRouter()
log = get_logger(__name__)


@router.post("/{source}", status_code=status.HTTP_202_ACCEPTED)
async def receive_webhook(source: str, request: Request) -> dict:
    payload = await request.json()
    # NUNCA logar o payload completo — pode conter dado sensivel.
    log.info("webhook.received", source=source, keys=list(payload.keys()))
    # TODO: dispatch por source -> handler em app/services/
    return {"accepted": True, "source": source}
