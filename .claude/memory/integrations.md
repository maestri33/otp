# Memória — Integrações com outros serviços

> Para **cada serviço externo** com que este fala, registre aqui:
> base URL, endpoints usados, formato de erro, política de retry,
> última vez que foi testado.

## Template de entrada

```
### <nome-do-servico>
- **Tipo:** HTTP | Webhook | Fila (RabbitMQ) | Pub/Sub (Redis)
- **Base URL / queue:** http://...
- **Endpoints / tópicos usados:**
  - GET /api/v1/...
- **Auth:** nenhuma (DMZ) | bearer | hmac
- **Retry:** 3x backoff exponencial (já no http_client)
- **Última verificação:** YYYY-MM-DD
- **Notas:** ...
```

## Integrações ativas

### notify (10.10.10.157 via notify.local)
- **Tipo:** HTTP
- **Base URL:** http://notify.local/api/v1 (resolve pra 10.10.10.157)
- **Endpoints usados:**
  - GET /health, GET /ready
  - POST /contacts, GET /contacts, GET /contacts/check, GET /contacts/{external_id}
  - POST /messages/send, GET /messages, GET /messages/{message_id}
  - GET /templates/email, PUT /templates/email
  - GET /logs
- **Auth:** nenhuma (DMZ)
- **Retry:** 3x backoff exponencial (via http_client)
- **Última verificação:** 2026-05-09
- **Notas:** Servico externo de notificacoes (WhatsApp, email, TTS). Client em
  `app/integrations/notify_client.py`, camada de servico em `app/services/notify.py`.
  Endpoints usam prefixo `/api/v1` no router principal do notify.
