"""
OTP endpoints — /api/v1/otp

- POST /              — generate OTP, persist, send via notify
- GET  /              — list all OTP logs
- POST /check         — validate OTP (external_id + code)
- GET  /logs          — logs with filters (external_id, status)
- GET  /config        — read current configuration
- PATCH /config       — update configuration
"""

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import http_client_dep
from app.schemas.otp import (
    OTPCheck,
    OTPCheckResponse,
    OTPCreate,
    OTPLogFilter,
    OTPRead,
)
from app.schemas.otp_config import OTPConfigRead, OTPConfigUpdate
from app.services import otp as otp_service

router = APIRouter(prefix="/api/v1/otp", tags=["otp"])


@router.post(
    "",
    response_model=OTPRead,
    status_code=status.HTTP_201_CREATED,
    summary="Gerar e enviar OTP",
    description="""
Gera um código OTP para o `external_id` informado, salva no banco e envia a
mensagem formatada via serviço externo **notify**.

- O código gerado é numérico (tamanho configurável, default 6 dígitos).
- O hash SHA256 do código é armazenado — o código em texto plano **nunca** é
  salvo.
- A mensagem é renderizada a partir do template `app/services/otp.md`.

Respostas possíveis:
- `201` — OTP gerado e enviado com sucesso (`status: "sent"`).
- `201` com `status: "failed"` — OTP gerado mas envio falhou
  (ex.: contacto não existe no notify, serviço notify fora do ar).
- `201` com `status: "failed"` e detail "Serviço OTP desativado" — quando
  a configuração `active=false`.
""",
)
async def create_otp(
    payload: OTPCreate,
    http=Depends(http_client_dep),
) -> OTPRead:
    """Generate an OTP, persist it, and send the formatted message via notify."""
    otp_log = await otp_service.generate_and_send(
        http, external_id=payload.external_id
    )
    return OTPRead.model_validate(otp_log, from_attributes=True)


@router.get(
    "",
    response_model=list[OTPRead],
    summary="Listar OTPs",
    description="""
Lista logs de OTP com filtros opcionais por `external_id` e `status`.

Parâmetros de query:
- `external_id` — filtra por ID externo.
- `status` — filtra por status (`generated`, `sent`, `verified`, `expired`, `failed`).
- `limit` — máximo de registros (1–200, default 50).
- `offset` — deslocamento para paginação (default 0).
""",
)
async def list_otps(
    external_id: str | None = Query(default=None, description="Filtrar por external_id"),
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Filtrar por status (generated, sent, verified, expired, failed)",
    ),
    limit: int = Query(default=50, ge=1, le=200, description="Registros por página"),
    offset: int = Query(default=0, ge=0, description="Deslocamento para paginação"),
) -> list[OTPRead]:
    """List OTP logs with optional filters by external_id and status."""
    logs = await otp_service.list_logs(
        external_id=external_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    return [OTPRead.model_validate(log, from_attributes=True) for log in logs]


@router.post(
    "/check",
    response_model=OTPCheckResponse,
    summary="Validar OTP",
    description="""
Valida um código OTP para o `external_id` informado.

- Busca o OTP mais recente com status `sent` para este `external_id`.
- Verifica expiração por tempo (TTL configurável, default 300s).
- Compara o código informado com o hash armazenado (SHA256, comparação
  em tempo constante).

Respostas possíveis:
- `{"valid": true, "detail": "ok"}` — código válido, OTP marcado como `verified`.
- `{"valid": false, "detail": "Código inválido"}` — código não confere.
- `{"valid": false, "detail": "OTP expirado"}` — TTL excedido.
- `{"valid": false, "detail": "Nenhum OTP pendente encontrado"}` —
  nenhum OTP no status `sent` para este external_id.
- `{"valid": false, "detail": "Serviço OTP desativado"}` — configuração
  `active=false`.
""",
)
async def verify_otp(
    payload: OTPCheck,
    http=Depends(http_client_dep),
) -> OTPCheckResponse:
    """Validate an OTP code — returns true/false."""
    result = await otp_service.verify_code(
        http,
        external_id=payload.external_id,
        code=payload.code,
    )
    return OTPCheckResponse(**result)


@router.get(
    "/logs",
    response_model=list[OTPRead],
    summary="Listar logs de OTP",
    description="""
Lista logs de OTP com filtros por `external_id` e/ou `status`.
Funcionalmente idêntico ao `GET /api/v1/otp`.
""",
)
async def list_otp_logs(
    external_id: str | None = Query(default=None, description="Filtrar por external_id"),
    status_filter: str | None = Query(
        default=None,
        alias="status",
        description="Filtrar por status",
    ),
    limit: int = Query(default=50, ge=1, le=200, description="Registros por página"),
    offset: int = Query(default=0, ge=0, description="Deslocamento para paginação"),
) -> list[OTPRead]:
    """List OTP logs with filters by external_id and/or status."""
    logs = await otp_service.list_logs(
        external_id=external_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    return [OTPRead.model_validate(log, from_attributes=True) for log in logs]


# ---------------------------------------------------------------------------
# Config endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/config",
    response_model=OTPConfigRead,
    summary="Consultar configuração OTP",
    description="""
Retorna a configuração atual do serviço OTP.

Campos retornados:
- `footer` — texto de rodapé da mensagem.
- `ttl_s` — tempo de vida do código em segundos.
- `num_digits` — quantidade de dígitos do código.
- `max_attempts` — tentativas máximas antes de invalidar (não implementado ainda).
- `active` — se o serviço está habilitado.
""",
)
async def get_config() -> OTPConfigRead:
    """Return the current OTP configuration (footer, TTL, digits, etc.)."""
    cfg = await otp_service.get_config()
    return OTPConfigRead.model_validate(cfg, from_attributes=True)


@router.patch(
    "/config",
    response_model=OTPConfigRead,
    summary="Atualizar configuração OTP",
    description="""
Atualiza a configuração do serviço OTP — apenas os campos informados são alterados.

Campos aceitos (todos opcionais):
- `footer` (string, max 255) — texto de rodapé.
- `ttl_s` (int, 30–3600) — TTL do código em segundos.
- `num_digits` (int, 4–10) — número de dígitos do código.
- `max_attempts` (int, 1–10) — tentativas máximas.
- `active` (bool) — ativar/desativar serviço.
""",
)
async def update_config(payload: OTPConfigUpdate) -> OTPConfigRead:
    """Update OTP configuration — only the provided fields."""
    cfg = await otp_service.update_config(**payload.model_dump(exclude_unset=True))
    return OTPConfigRead.model_validate(cfg, from_attributes=True)
