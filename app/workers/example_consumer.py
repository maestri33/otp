"""
Exemplo de worker: consome eventos `*.user.created` da exchange `events`.

Rode com:  uv run python -m app.workers.example_consumer

Para subir varios workers num servico, crie um por arquivo aqui e suba
cada um como processo separado (systemd, docker, etc).
"""

import asyncio
from typing import Any

from app.db import close_db, init_db
from app.integrations.messaging import consume
from app.utils.logging import configure_logging, get_logger

log = get_logger(__name__)


async def handle_user_created(payload: dict[str, Any]) -> None:
    log.info("event.user.created", user_id=payload.get("id"))
    # TODO: regra de negocio aqui — chamar um service.


async def main() -> None:
    configure_logging()
    await init_db()
    try:
        await consume(
            queue_name="microservice-template.user.created",
            routing_key="*.user.created",
            handler=handle_user_created,
        )
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
