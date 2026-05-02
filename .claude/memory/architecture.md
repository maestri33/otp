# Memória — Arquitetura

> Decisões arquiteturais deste serviço, em ordem cronológica.
> **Toda decisão nova entra aqui** com data, contexto e consequência.

## Forma deste serviço

- Um único processo Uvicorn na porta **80**.
- Banco próprio (SQLite por padrão, Postgres quando crescer) —
  **nenhum outro serviço acessa esse banco diretamente**.
- Comunicação com o mundo externo:
  - **Síncrona:** HTTP via `app/integrations/http_client.py`.
  - **Assíncrona:** RabbitMQ via `app/integrations/messaging.py`
    (publisher) e `app/workers/` (consumers).
  - **Cache / pub-sub leve:** Redis via `app/integrations/redis_client.py`.
  - **Eventos pra terceiros:** webhooks outbound em
    `app/integrations/webhooks.py`.

## Princípios

1. **Service-per-database.** Acoplamento via API ou evento, nunca via SQL.
2. **Camadas finas.** `api/` → `services/` → `models/`. Sem mais.
3. **Erros explícitos.** Exceptions de domínio em `app/exceptions.py`,
   convertidas pra HTTPException no router.
4. **Idempotência onde dá.** Endpoints `POST` que criam algo via evento
   externo aceitam um header `Idempotency-Key`.

## Histórico de decisões

### 2026-05-02 — Bootstrap inicial
- **Decisão:** SQLite como default no template, Postgres opcional via
  `DATABASE_URL`.
- **Por quê:** simplifica o boot do serviço novo (zero infra), e como o
  banco é por-serviço a migração futura é trivial.
- **Consequência:** ao escalar para produção, trocar `DATABASE_URL` para
  uma instância Postgres dedicada **antes** de ter dados que doam.
