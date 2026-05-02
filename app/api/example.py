"""
CRUD de exemplo: /items

Use este arquivo como modelo pra criar uma feature nova.
A regra de negocio fica em `services/`, NAO aqui.
"""

from fastapi import APIRouter, status

from app.schemas.example import ItemCreate, ItemRead, ItemUpdate
from app.services import example_service

router = APIRouter()


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(payload: ItemCreate) -> ItemRead:
    item = await example_service.create_item(payload)
    return ItemRead.model_validate(item, from_attributes=True)


@router.get("/{item_id}", response_model=ItemRead)
async def get_item(item_id: int) -> ItemRead:
    item = await example_service.get_item(item_id)
    return ItemRead.model_validate(item, from_attributes=True)


@router.get("", response_model=list[ItemRead])
async def list_items(limit: int = 50, offset: int = 0) -> list[ItemRead]:
    items = await example_service.list_items(limit=limit, offset=offset)
    return [ItemRead.model_validate(i, from_attributes=True) for i in items]


@router.patch("/{item_id}", response_model=ItemRead)
async def update_item(item_id: int, payload: ItemUpdate) -> ItemRead:
    item = await example_service.update_item(item_id, payload)
    return ItemRead.model_validate(item, from_attributes=True)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int) -> None:
    await example_service.delete_item(item_id)
