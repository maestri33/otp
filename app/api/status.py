"""
Status page — HTML dashboard at / showing real service state.
"""

import os
import time
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from tortoise import connections

from app.config import get_settings
from app.models.otp import OTPLog

router = APIRouter()
settings = get_settings()
_STARTED_AT = time.time()

_STATUS_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       background: #0f172a; color: #e2e8f0; padding: 2rem; max-width: 900px; margin: auto; }
h1 { font-size: 1.5rem; margin-bottom: 0.25rem; }
h2 { font-size: 1.1rem; margin: 1.5rem 0 0.75rem; color: #94a3b8; }
.env-tag { font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
.env-prod { background: #dc2626; color: #fff; }
.env-dev { background: #2563eb; color: #fff; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
.card { background: #1e293b; border-radius: 8px; padding: 1rem; border: 1px solid #334155; }
.card h3 { font-size: 0.75rem; color: #64748b; text-transform: uppercase; margin-bottom: 0.5rem; }
.card .value { font-size: 1.25rem; font-weight: 600; }
.status-ok { color: #22c55e; }
.status-fail { color: #ef4444; }
.status-warn { color: #f59e0b; }
table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; }
th { text-align: left; color: #64748b; font-size: 0.75rem; padding: 6px 8px; border-bottom: 1px solid #334155; }
td { padding: 6px 8px; font-size: 0.85rem; border-bottom: 1px solid #1e293b; }
tr:hover { background: #1e293b; }
.badge { font-size: 0.7rem; padding: 2px 6px; border-radius: 3px; font-weight: 600; text-transform: uppercase; }
.badge-sent { background: #166534; color: #4ade80; }
.badge-verified { background: #1e3a5f; color: #60a5fa; }
.badge-failed { background: #7f1d1d; color: #fca5a5; }
.badge-generated { background: #713f12; color: #fcd34d; }
.badge-expired { background: #3f3f46; color: #a1a1aa; }
.time { color: #64748b; font-size: 0.75rem; margin-top: 2rem; }
"""


def _uptime() -> str:
    s = int(time.time() - _STARTED_AT)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


async def _db_status() -> tuple[bool, str]:
    try:
        conn = connections.get("default")
        await conn.execute_query("SELECT 1")
        return True, "conectado"
    except Exception as exc:
        return False, str(exc)


async def _notify_status(http: httpx.AsyncClient) -> tuple[bool, str]:
    try:
        resp = await http.get(f"{settings.notify_base_url}/health", timeout=5)
        data = resp.json()
        return resp.status_code == 200, data.get("service", "notify")
    except Exception as exc:
        return False, str(exc)


async def _otp_stats() -> dict:
    rows = await OTPLog.all()
    total = len(rows)
    by_status = {"sent": 0, "verified": 0, "failed": 0, "generated": 0, "expired": 0}
    for r in rows:
        if r.status in by_status:
            by_status[r.status] += 1
    return {"total": total, "by_status": by_status}


@router.get("/", response_class=HTMLResponse)
async def status() -> str:
    db_ok, db_info = await _db_status()

    async with httpx.AsyncClient(timeout=5) as http:
        notify_ok, notify_info = await _notify_status(http)

    stats = await _otp_stats()
    recent = (
        await OTPLog.all().order_by("-created_at").limit(10)
    )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    return f"""<!DOCTYPE html>
<html lang="pt">
<head>
<meta charset="utf-8">
<title>OTP — Status</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{_STATUS_CSS}</style>
</head>
<body>
<h1>{settings.service_name}
<span class="env-tag env-{settings.env}">{settings.env.upper()}</span>
</h1>
<p style="color:#64748b;font-size:0.85rem">Uptime: {_uptime()} &mdash; Porta {settings.port}</p>

<h2>Configuração</h2>
<div class="grid">
<div class="card"><h3>Rodapé</h3><div class="value" style="font-size:0.9rem">{settings.otp_footer}</div></div>
<div class="card"><h3>TTL</h3><div class="value">{settings.otp_ttl_s}s</div></div>
<div class="card"><h3>Dígitos</h3><div class="value">{settings.otp_num_digits}</div></div>
<div class="card"><h3>Tentativas máx</h3><div class="value">{settings.otp_max_attempts}</div></div>
<div class="card"><h3>Ativo</h3><div class="value {'status-ok' if settings.otp_active else 'status-fail'}">{'sim' if settings.otp_active else 'não'}</div></div>
</div>

<h2>Conexões</h2>
<div class="grid">
<div class="card">
  <h3>Banco (SQLite)</h3>
  <div class="value {'status-ok' if db_ok else 'status-fail'}">{db_info}</div>
</div>
<div class="card">
  <h3>Notify</h3>
  <div class="value {'status-ok' if notify_ok else 'status-fail'}">{notify_info if notify_ok else 'offline'}</div>
  <div style="font-size:0.7rem;color:#64748b;margin-top:4px">{settings.notify_base_url}</div>
</div>
</div>

<h2>OTPs (total: {stats['total']})</h2>
<div class="grid">
<div class="card"><h3>Enviados</h3><div class="value status-ok">{stats['by_status']['sent']}</div></div>
<div class="card"><h3>Verificados</h3><div class="value" style="color:#60a5fa">{stats['by_status']['verified']}</div></div>
<div class="card"><h3>Falhos</h3><div class="value status-fail">{stats['by_status']['failed']}</div></div>
<div class="card"><h3>Expirados</h3><div class="value status-warn">{stats['by_status']['expired']}</div></div>
<div class="card"><h3>Gerados</h3><div class="value" style="color:#fcd34d">{stats['by_status']['generated']}</div></div>
</div>

<h2>Recentes</h2>
<table>
<tr><th>ID</th><th>External ID</th><th>Status</th><th>Data</th><th>Detalhe</th></tr>
{"".join(
    f'<tr>'
    f'<td>{r.id}</td>'
    f'<td>{r.external_id}</td>'
    f'<td><span class="badge badge-{r.status}">{r.status}</span></td>'
    f'<td style="font-size:0.8rem;color:#94a3b8">{r.created_at.strftime("%H:%M:%S")}</td>'
    f'<td style="font-size:0.75rem;color:#64748b;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{r.error_detail or (f"msg #{r.message_id}" if r.message_id else "-")}</td>'
    f'</tr>'
    for r in recent
)}
</table>

<p class="time">Atualizado: {now}</p>
</body>
</html>"""
