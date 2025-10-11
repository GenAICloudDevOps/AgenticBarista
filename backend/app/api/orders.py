from fastapi import APIRouter, HTTPException
from app.models.order import Order, OrderSchema
from app.models.customer import Customer
from typing import List

router = APIRouter()

@router.get("/orders/{session_id}", response_model=List[OrderSchema])
async def get_orders(session_id: str):
    try:
        customer = await Customer.get(session_id=session_id)
        orders = await Order.filter(customer=customer).order_by("-created_at")
        return [OrderSchema.from_orm(order) for order in orders]
    except:
        return []

@router.get("/order/{order_id}", response_model=OrderSchema)
async def get_order(order_id: int):
    try:
        order = await Order.get(id=order_id)
        return OrderSchema.from_orm(order)
    except:
        raise HTTPException(status_code=404, detail="Order not found")
