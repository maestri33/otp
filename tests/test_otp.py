"""Testes dos endpoints OTP — sem mocks, com banco real (SQLite in-memory)."""

import hashlib
import time

import pytest
from httpx import AsyncClient

from app.models.otp import OTPLog
from app.models.otp_config import OTPConfig


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


async def test_get_config_default(client: AsyncClient) -> None:
    """GET /api/v1/otp/config retorna a config default quando nada existe."""
    resp = await client.get("/api/v1/otp/config")
    assert resp.status_code == 200
    body = resp.json()
    assert body["footer"] == "Equipe OTP"
    assert body["ttl_s"] == 300
    assert body["num_digits"] == 6
    assert body["max_attempts"] == 3
    assert body["active"] is True


async def test_update_config(client: AsyncClient) -> None:
    """PATCH /api/v1/otp/config atualiza só os campos informados."""
    resp = await client.patch(
        "/api/v1/otp/config",
        json={"footer": "Test Footer", "ttl_s": 120},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["footer"] == "Test Footer"
    assert body["ttl_s"] == 120
    # Campos não informados mantêm valores anteriores
    assert body["num_digits"] == 6
    assert body["active"] is True


async def test_update_config_validation(client: AsyncClient) -> None:
    """PATCH /api/v1/otp/config rejeita valores fora dos limites."""
    resp = await client.patch(
        "/api/v1/otp/config",
        json={"ttl_s": 10},  # mínimo é 30
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Listagem
# ---------------------------------------------------------------------------


async def test_list_otps_empty(client: AsyncClient) -> None:
    """GET /api/v1/otp retorna lista vazia quando não há logs."""
    resp = await client.get("/api/v1/otp")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_otps_with_data(client: AsyncClient) -> None:
    """GET /api/v1/otp retorna logs ordenados por created_at decrescente."""
    await OTPLog.create(
        external_id="user-a", code_hash="abc123", status="sent"
    )
    await OTPLog.create(
        external_id="user-b", code_hash="def456", status="verified"
    )

    resp = await client.get("/api/v1/otp")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 2
    assert body[0]["external_id"] == "user-b"  # mais recente primeiro
    assert body[1]["external_id"] == "user-a"


async def test_list_otps_filter_by_external_id(client: AsyncClient) -> None:
    """GET /api/v1/otp?external_id=X filtra corretamente."""
    await OTPLog.create(
        external_id="filter-me", code_hash="abc", status="sent"
    )
    await OTPLog.create(
        external_id="filter-other", code_hash="def", status="sent"
    )

    resp = await client.get("/api/v1/otp", params={"external_id": "filter-me"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["external_id"] == "filter-me"


async def test_list_otps_filter_by_status(client: AsyncClient) -> None:
    """GET /api/v1/otp?status=X filtra corretamente."""
    await OTPLog.create(
        external_id="user-1", code_hash="a", status="sent"
    )
    await OTPLog.create(
        external_id="user-2", code_hash="b", status="failed"
    )

    resp = await client.get("/api/v1/otp", params={"status": "failed"})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["status"] == "failed"


async def test_list_otps_pagination(client: AsyncClient) -> None:
    """GET /api/v1/otp respeita limit e offset."""
    for i in range(5):
        await OTPLog.create(
            external_id=f"user-{i}", code_hash=f"hash{i}", status="sent"
        )

    resp = await client.get("/api/v1/otp", params={"limit": 2, "offset": 1})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 2


# ---------------------------------------------------------------------------
# Verificação (não depende de notify — testa só a lógica local)
# ---------------------------------------------------------------------------


def _hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


async def test_verify_code_success(client: AsyncClient) -> None:
    """POST /api/v1/otp/check retorna valid=true para código correto."""
    code = "123456"
    await OTPLog.create(
        external_id="verify-me",
        code_hash=_hash(code),
        status="sent",
    )

    resp = await client.post(
        "/api/v1/otp/check",
        json={"external_id": "verify-me", "code": code},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is True
    assert body["detail"] == "ok"

    # Verifica que o log foi atualizado
    log = await OTPLog.filter(external_id="verify-me", status="verified").first()
    assert log is not None
    assert log.verified_at is not None


async def test_verify_code_invalid(client: AsyncClient) -> None:
    """POST /api/v1/otp/check retorna valid=false para código errado."""
    await OTPLog.create(
        external_id="wrong-code",
        code_hash=_hash("999999"),
        status="sent",
    )

    resp = await client.post(
        "/api/v1/otp/check",
        json={"external_id": "wrong-code", "code": "111111"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is False
    assert body["detail"] == "Código inválido"


async def test_verify_code_no_pending_otp(client: AsyncClient) -> None:
    """POST /api/v1/otp/check com external_id sem OTP pendente."""
    resp = await client.post(
        "/api/v1/otp/check",
        json={"external_id": "no-otp-here", "code": "123456"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is False
    assert body["detail"] == "Nenhum OTP pendente encontrado"


async def test_verify_code_expired(client: AsyncClient) -> None:
    """POST /api/v1/otp/check retorna expired quando TTL excedido."""
    # Cria OTP com created_at no passado (TTL default = 300s)
    from datetime import datetime, timedelta, timezone

    old = datetime.now(timezone.utc) - timedelta(seconds=600)
    log = await OTPLog.create(
        external_id="expired-otp",
        code_hash=_hash("123456"),
        status="sent",
    )
    # Força created_at para o passado (bypass auto_now_add)
    log.created_at = old
    await log.save()

    resp = await client.post(
        "/api/v1/otp/check",
        json={"external_id": "expired-otp", "code": "123456"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is False
    assert body["detail"] == "OTP expirado"


async def test_verify_code_service_disabled(client: AsyncClient) -> None:
    """POST /api/v1/otp/check bloqueia quando active=false."""
    # Garante que a config existe
    cfg = await OTPConfig.first() or await OTPConfig.create()
    cfg.active = False
    await cfg.save()

    resp = await client.post(
        "/api/v1/otp/check",
        json={"external_id": "anyone", "code": "123456"},
    )
    assert resp.status_code == 200
    assert resp.json()["valid"] is False
    assert resp.json()["detail"] == "Serviço OTP desativado"

    # Restaura
    cfg.active = True
    await cfg.save()


# ---------------------------------------------------------------------------
# Geração (depende do notify estar rodando — teste de integração real)
# ---------------------------------------------------------------------------


@pytest.mark.integration
async def test_generate_otp_service_disabled(client: AsyncClient) -> None:
    """POST /api/v1/otp bloqueia geração quando active=false (não depende de notify)."""
    cfg = await OTPConfig.first() or await OTPConfig.create()
    cfg.active = False
    await cfg.save()

    resp = await client.post(
        "/api/v1/otp",
        json={"external_id": "disabled-test"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "failed"
    assert "desativado" in body["error_detail"]

    cfg.active = True
    await cfg.save()


@pytest.mark.integration
async def test_generate_otp_contact_not_found(client: AsyncClient) -> None:
    """POST /api/v1/otp com contact que não existe no notify retorna failed."""
    resp = await client.post(
        "/api/v1/otp",
        json={"external_id": "nonexistent-contact-xyz"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "failed"
    assert "nao encontrado" in body["error_detail"].lower()


@pytest.mark.integration
async def test_generate_and_verify_full_flow(client: AsyncClient) -> None:
    """Fluxo completo: gera OTP + verifica com código real.

    Nota: o contact precisa existir no notify. Usamos um external_id
    que foi previamente cadastrado no notify.
    """
    external_id = "5511999999999"

    # 1. Gera OTP
    resp = await client.post(
        "/api/v1/otp",
        json={"external_id": external_id},
    )
    assert resp.status_code == 201
    gen = resp.json()
    assert gen["status"] == "sent"
    assert gen["message_id"] is not None
