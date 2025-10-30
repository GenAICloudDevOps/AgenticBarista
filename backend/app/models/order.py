from tortoise.models import Model
from tortoise import fields
from pydantic import BaseModel, field_serializer
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"

class Order(Model):
    id = fields.IntField(pk=True)
    customer = fields.ForeignKeyField("models.Customer", related_name="orders")
    items = fields.JSONField()  # List of {item_id, quantity, price}
    total = fields.DecimalField(max_digits=8, decimal_places=2)
    status = fields.CharEnumField(OrderStatus, default=OrderStatus.PENDING)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "orders"

class OrderItemSchema(BaseModel):
    item_id: int
    name: str
    quantity: int
    price: float

class OrderSchema(BaseModel):
    id: Optional[int] = None
    customer_id: int
    items: List[Dict]  # Changed from List[OrderItemSchema] to List[Dict] for flexibility
    total: float
    status: OrderStatus = OrderStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: Optional[datetime], _info):
        if dt:
            return dt.isoformat()
        return None

    class Config:
        from_attributes = True
