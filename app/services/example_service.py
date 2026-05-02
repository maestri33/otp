"""
Camada de servico do CRUD de Item.

Regra: services NAO conhecem FastAPI. Levantam excecoes de dominio
(`app.exceptions`) que sao convertidas no handler global em main.py.
"""

from app.exceptions import NotFound
from app.models.example import Item
from app.schemas.example import ItemCreate, ItemUpdate


async def create_item(payload: ItemCreate) -> Item:
    return await Item.create(**payload.model_dump())


async def get_item(item_id: int) -> Item:
    item = await Item.get_or_none(id=item_id)
    if item is None:
        raise NotFound(f"Item {item_id} nao encontrado")
    return item


async def list_items(limit: int = 50, offset: int = 0) -> list[Item]:
    return await Item.all().offset(offset).limit(limit)


async def update_item(item_id: int, payload: ItemUpdate) -> Item:
    item = await get_item(item_id)
    data = payload.model_dump(exclude_unset=True)
    if data:
        await item.update_from_dict(data).save()
    return item


async def delete_item(item_id: int) -> None:
    item = await get_item(item_id)
    await item.delete()
