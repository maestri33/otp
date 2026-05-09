# Memória — Arquitetura

## Forma deste serviço

- Um único processo Uvicorn na porta **80**.
- Banco próprio: SQLite em `data/app.db` (Postgres opcional via `DATABASE_URL`).
- Comunicação externa: HTTP via `app/integrations/http_client.py`.
- Única integração ativa: **notify** (envio de mensagens).

## Princípios

1. **Service-per-database.** Acoplamento via API, nunca via SQL.
2. **Camadas finas.** `api/` → `services/` → `models/`.
3. **Configuração via env.** Sem banco pra config — tudo no `.env`.
4. **Erros explícitos.** Exceptions de domínio em `app/exceptions.py`, convertidas pra JSON no handler global.

## Histórico de decisões

### 2026-05-09 — Simplificação: config no env, remoção de boilerplate
- **Decisão:** Remover OTPConfig do banco e mover tudo pra `.env`. Remover Redis, RabbitMQ, webhooks e workers (não usados).
- **Por quê:** Menos peças móveis, serviço mais enxuto e previsível.
- **Consequência:** Para alterar config é preciso restart do serviço.

### 2026-05-02 — Bootstrap inicial
- **Decisão:** SQLite como default, Postgres opcional via `DATABASE_URL`.
