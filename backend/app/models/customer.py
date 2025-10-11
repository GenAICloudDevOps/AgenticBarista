from tortoise.models import Model
from tortoise import fields
from pydantic import BaseModel
from typing import Optional

class Customer(Model):
    id = fields.IntField(pk=True)
    session_id = fields.CharField(max_length=100, unique=True)
    name = fields.CharField(max_length=100, null=True)
    preferences = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "customers"

class CustomerSchema(BaseModel):
    id: Optional[int] = None
    session_id: str
    name: Optional[str] = None
    preferences: dict = {}

    class Config:
        from_attributes = True
