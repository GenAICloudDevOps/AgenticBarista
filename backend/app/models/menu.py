from tortoise.models import Model
from tortoise import fields
from pydantic import BaseModel
from typing import Optional

class MenuItem(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    description = fields.TextField()
    price = fields.DecimalField(max_digits=6, decimal_places=2)
    category = fields.CharField(max_length=50)
    available = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "menu_items"

class MenuItemSchema(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    price: float
    category: str
    available: bool = True

    class Config:
        from_attributes = True
