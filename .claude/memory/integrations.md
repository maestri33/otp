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

_Nenhuma ainda. Adicione aqui assim que criar o primeiro
`app/integrations/<servico>_client.py`._
