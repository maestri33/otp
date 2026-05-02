# microservice-template

Template **bootstrap** de microserviço para o ecossistema interno (Proxmox / DMZ).
Stack: **FastAPI + Tortoise ORM + Uvicorn + uv**, com **Claude Code já configurado**
por dentro (memória, regras, Context7, DeepSeek v4 Pro).

> **Filosofia.** Cada microserviço deve ser **genérico, reutilizável, simples e
> completo**. Cada serviço tem o **seu próprio Claude Code** (com memória própria),
> o **seu próprio banco**, e fala com os outros serviços via HTTP, fila ou webhook —
> nunca via banco compartilhado.

---

## Como usar este template

### 1. Clonar pra um serviço novo

```bash
# copia o template e renomeia
./scripts/new_service.sh auth-svc

cd auth-svc
cp .env.example .env          # ajusta valores reais
uv sync
make dev                      # sobe na porta 80
```

O script `new_service.sh` troca `microservice-template` pelo nome novo
em todos os arquivos relevantes (`pyproject.toml`, README, etc.).

### 2. Subir o Claude Code pra esse serviço

Dentro da pasta do serviço:

```bash
export ANTHROPIC_BASE_URL="http://proxy.local:8787"   # seu proxy DeepSeek
export ANTHROPIC_AUTH_TOKEN="..."
export CONTEXT7_API_KEY="..."

claude                        # ou claude-code, dependendo da sua instalacao
```

O Claude Code vai automaticamente:
- Ler `.claude/CLAUDE.md` (memória + regras)
- Ler `.claude/memory/*.md` (contexto persistente)
- Carregar Context7 via `.mcp.json` (docs reais das libs)
- Usar DeepSeek v4 Pro como modelo (configurado em `.claude/settings.json`)

> **Importante:** o Claude Code daquela pasta é **exclusivo daquele
> serviço**. Cada serviço tem o próprio.

### 3. O que o Claude Code já sabe fazer aqui

Ele foi instruído a, sem você precisar repetir:
- **Não alucinar** (consulta Context7 quando não sabe).
- **Fazer apenas o que você pedir** (não cria features extras).
- **Salvar tudo na memória** (`.claude/memory/`).
- **Manter a estrutura de pastas** definida.
- **Trabalhar em PT-BR** nos comentários e docs.
- **Usar a porta 80**.
- **Ignorar segurança por enquanto** (DMZ — vamos travar depois).

---

## Estrutura

```
.
├── .claude/                  # Claude Code: memoria + regras + modelo
├── .mcp.json                 # Context7 MCP
├── app/
│   ├── main.py               # FastAPI entrypoint, porta 80
│   ├── config.py             # pydantic-settings
│   ├── db.py                 # Tortoise init/close
│   ├── api/                  # routers HTTP (1 arquivo por feature)
│   ├── models/               # modelos Tortoise
│   ├── schemas/              # Pydantic request/response
│   ├── services/             # regras de negocio
│   ├── integrations/         # httpx, redis, rabbitmq, webhooks
│   ├── workers/              # consumers de fila
│   └── utils/                # logging etc
├── tests/
├── scripts/
├── pyproject.toml
├── Makefile
└── .env.example
```

Detalhes de **onde colocar cada coisa nova** estão em
`.claude/memory/conventions.md`.

---

## Contexto operacional (Proxmox / DMZ)

- Roda em LXC ou VM no Proxmox.
- Está em **zona desmilitarizada** — sem firewall entre serviços internos.
- Ambiente é **dev**, mas **infra é real**: portas, hosts, banco.
- **Segurança não é prioridade agora** (auth, CORS, rate-limit). Quando for,
  vamos abrir um issue específico.

## Comandos

```bash
make install     # uv sync
make dev         # uvicorn --reload na porta 80
make run         # uvicorn 2 workers
make test        # pytest
make lint        # ruff + mypy
make fmt         # ruff format
make migrate     # aerich migrate && upgrade
```

## Banco

Default: **SQLite** em `./data/app.db` (zero infra, perfeito pra subir o
serviço sem dependência externa).

Pra trocar pra Postgres dedicado deste serviço, basta mudar `DATABASE_URL`
no `.env`:

```env
DATABASE_URL=postgres://user:pass@db.proxmox.local:5432/auth_svc
```

> **Lembrete arquitetural:** este banco é **só desse serviço**. Outro serviço
> que precise desses dados consulta pela API.

## Integrações prontas

| Módulo                          | Pra quê                                |
| ------------------------------- | -------------------------------------- |
| `app/integrations/http_client.py` | Falar com outros microservices via HTTP |
| `app/integrations/redis_client.py` | Cache + pub/sub leve                   |
| `app/integrations/messaging.py`  | RabbitMQ (eventos entre serviços)      |
| `app/integrations/webhooks.py`   | Receber e enviar webhooks              |
| `app/workers/`                   | Consumers de fila / jobs em background |

Cada uma tem um exemplo funcional. Quando você (ou o Claude Code) adicionar
uma chamada nova pra outro serviço, **registre em `.claude/memory/integrations.md`**.
