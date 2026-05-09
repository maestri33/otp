# Memória — Integrações com outros serviços

## Integrações ativas

### notify (10.10.10.157 via notify.local)
- **Tipo:** HTTP
- **Base URL:** http://notify.local/api/v1 (resolve pra 10.10.10.157)
- **Endpoints usados:**
  - POST /messages/send — envia mensagem formatada
- **Auth:** nenhuma (DMZ)
- **Retry:** 3x backoff exponencial (via http_client)
- **Última verificação:** 2026-05-09
- **Notas:** Client em `app/integrations/notify_client.py`, camada de serviço em `app/services/notify.py`. O contacto deve existir previamente no notify.
