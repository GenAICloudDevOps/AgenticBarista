from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.models.user import User, UserResponse
from app.models.order import Order, OrderStatus
from app.core.security import get_current_admin_user
from app.core.email import (
    send_order_ready_email,
    send_admin_notification,
    send_email
)
from app.core.slack import send_order_ready_notification
from pydantic import BaseModel, EmailStr

router = APIRouter()

class EmailNotification(BaseModel):
    to_email: EmailStr
    subject: str
    message: str

class BulkEmailNotification(BaseModel):
    user_ids: List[int]
    subject: str
    message: str

class OrderStatusUpdate(BaseModel):
    order_id: int
    status: OrderStatus

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_admin: User = Depends(get_current_admin_user)
):
    """Get all users (admin only)"""
    users = await User.all().offset(skip).limit(limit)
    return [UserResponse.from_orm(user) for user in users]

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user)
):
    """Get user by ID (admin only)"""
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.from_orm(user)

@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user)
):
    """Activate a user (admin only)"""
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    await user.save()
    
    return {"message": f"User {user.username} activated successfully"}

@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user)
):
    """Deactivate a user (admin only)"""
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate admin users"
        )
    
    user.is_active = False
    await user.save()
    
    return {"message": f"User {user.username} deactivated successfully"}

@router.post("/email/send")
async def send_email_to_user(
    email_data: EmailNotification,
    current_admin: User = Depends(get_current_admin_user)
):
    """Send email to a specific user (admin only)"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #6B4423 0%, #8B6F47 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>☕ Coffee and AI</h1>
            </div>
            <div class="content">
                <p>{email_data.message}</p>
            </div>
            <div class="footer">
                <p>© 2024 Coffee and AI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    success = await send_email(
        email_data.to_email,
        email_data.subject,
        html_content,
        email_data.message
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )
    
    return {"message": "Email sent successfully"}

@router.post("/email/bulk")
async def send_bulk_email(
    email_data: BulkEmailNotification,
    current_admin: User = Depends(get_current_admin_user)
):
    """Send email to multiple users (admin only)"""
    users = await User.filter(id__in=email_data.user_ids, is_active=True)
    
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active users found with provided IDs"
        )
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #6B4423 0%, #8B6F47 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>☕ Coffee and AI</h1>
            </div>
            <div class="content">
                <p>{email_data.message}</p>
            </div>
            <div class="footer">
                <p>© 2024 Coffee and AI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    sent_count = 0
    failed_count = 0
    
    for user in users:
        try:
            success = await send_email(
                user.email,
                email_data.subject,
                html_content,
                email_data.message
            )
            if success:
                sent_count += 1
            else:
                failed_count += 1
        except Exception as e:
            print(f"Failed to send email to {user.email}: {str(e)}")
            failed_count += 1
    
    return {
        "message": f"Bulk email completed",
        "sent": sent_count,
        "failed": failed_count,
        "total": len(users)
    }

@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_admin: User = Depends(get_current_admin_user)
):
    """Update order status and notify user (admin only)"""
    order = await Order.get_or_none(id=order_id).prefetch_related('customer')
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    old_status = order.status
    order.status = status_update.status
    await order.save()
    
    # If order is ready, send notification email and Slack
    if status_update.status == OrderStatus.READY:
        customer = await order.customer
        user = await User.get_or_none(email=customer.session_id)
        
        # Send Slack notification
        try:
            customer_name = customer.session_id.split('@')[0] if '@' in customer.session_id else customer.session_id[:8]
            await send_order_ready_notification(order.id, customer_name)
        except Exception as e:
            print(f"Failed to send Slack notification: {str(e)}")
        
        # Send email if user is registered
        if user:
            try:
                await send_order_ready_email(
                    user.email,
                    user.username,
                    order.id
                )
            except Exception as e:
                print(f"Failed to send order ready email: {str(e)}")
    
    return {
        "message": f"Order status updated from {old_status} to {status_update.status}",
        "order_id": order.id,
        "new_status": status_update.status
    }

@router.get("/stats")
async def get_admin_stats(current_admin: User = Depends(get_current_admin_user)):
    """Get admin dashboard statistics"""
    total_users = await User.all().count()
    active_users = await User.filter(is_active=True).count()
    total_orders = await Order.all().count()
    pending_orders = await Order.filter(status=OrderStatus.PENDING).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "total_orders": total_orders,
        "pending_orders": pending_orders
    }
