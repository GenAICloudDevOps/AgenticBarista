from fastapi import APIRouter, HTTPException, Depends
from app.models.order import Order, OrderSchema
from app.models.customer import Customer
from app.models.user import User
from app.core.security import get_current_active_user
from app.core.email import send_order_confirmation_email
from typing import List, Optional

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

@router.get("/my-orders", response_model=List[OrderSchema])
async def get_my_orders(current_user: User = Depends(get_current_active_user)):
    """Get orders for authenticated user"""
    try:
        print(f"[ORDER HISTORY DEBUG] Fetching orders for user: {current_user.email}")
        
        # Find customer by email (using email as session_id for authenticated users)
        customer = await Customer.get_or_none(session_id=current_user.email)
        if not customer:
            print(f"[ORDER HISTORY DEBUG] No customer found with session_id: {current_user.email}")
            return []
        
        print(f"[ORDER HISTORY DEBUG] Found customer ID: {customer.id}")
        
        orders = await Order.filter(customer=customer).order_by("-created_at")
        print(f"[ORDER HISTORY DEBUG] Found {len(orders)} orders")
        
        return [OrderSchema.from_orm(order) for order in orders]
    except Exception as e:
        print(f"[ORDER HISTORY DEBUG] Error fetching orders: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

@router.post("/order/{order_id}/notify")
async def notify_order_confirmation(
    order_id: int,
    current_user: Optional[User] = Depends(get_current_active_user)
):
    """Send order confirmation email to user"""
    try:
        order = await Order.get(id=order_id).prefetch_related('customer')
        customer = await order.customer
        
        # If user is authenticated, use their email
        if current_user:
            user_email = current_user.email
            username = current_user.username
        else:
            # Try to find user by customer session_id
            user = await User.get_or_none(email=customer.session_id)
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="User email not found. Please register or login to receive email notifications."
                )
            user_email = user.email
            username = user.username
        
        # Send confirmation email
        success = await send_order_confirmation_email(
            user_email=user_email,
            username=username,
            order_id=order.id,
            items=order.items,
            total=float(order.total)
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send confirmation email"
            )
        
        return {
            "message": "Order confirmation email sent successfully",
            "order_id": order.id,
            "email": user_email
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error sending notification: {str(e)}"
        )
