"""
Mensageria com RabbitMQ (aio-pika).

Use para eventos durables entre microservices (ex.: "user.created",
"payment.approved"). Topicos sao exchanges do tipo `topic`.

Convencao de nome: `<servico>.<entidade>.<acao>` (ex.: auth.user.created).
"""

import json
from typing import Any, Awaitable, Callable

import aio_pika

from app.config import get_settings
from app.utils.logging import get_logger

log = get_logger(__name__)


async def publish_event(
    routing_key: str,
    payload: dict[str, Any],
    *,
    exchange_name: str = "events",
) -> None:
    """Publica um evento na exchange `events` (tipo topic)."""
    settings = get_settings()
    conn = await aio_pika.connect_robust(settings.amqp_url)
    try:
        async with conn:
            channel = await conn.channel()
            exchange = await channel.declare_exchange(
                exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
            )
            message = aio_pika.Message(
                body=json.dumps(payload).encode("utf-8"),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )
            await exchange.publish(message, routing_key=routing_key)
            log.info("event.published", routing_key=routing_key)
    finally:
        if not conn.is_closed:
            await conn.close()


async def consume(
    queue_name: str,
    routing_key: str,
    handler: Callable[[dict[str, Any]], Awaitable[None]],
    *,
    exchange_name: str = "events",
) -> None:
    """
    Loop de consumo. Roda no startup de um worker, em
    `app/workers/<topico>_consumer.py`.
    """
    settings = get_settings()
    conn = await aio_pika.connect_robust(settings.amqp_url)
    channel = await conn.channel()
    await channel.set_qos(prefetch_count=8)
    exchange = await channel.declare_exchange(
        exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
    )
    queue = await channel.declare_queue(queue_name, durable=True)
    await queue.bind(exchange, routing_key=routing_key)

    log.info("consumer.started", queue=queue_name, routing_key=routing_key)
    async with queue.iterator() as it:
        async for message in it:
            async with message.process():
                payload = json.loads(message.body.decode("utf-8"))
                await handler(payload)
