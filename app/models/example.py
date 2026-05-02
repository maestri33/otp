"""
Modelo de exemplo — Item.

Tortoise tem cara de Django: classe herda de Model, campos sao Field do
proprio Tortoise. Use este arquivo como referencia para criar entidades novas.
"""

from tortoise import fields
from tortoise.models import Model


class Item(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=120)
    description = fields.TextField(null=True)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "items"

    def __str__(self) -> str:
        return f"Item(id={self.id}, name={self.name!r})"
