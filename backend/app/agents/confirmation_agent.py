from typing import Dict
from app.models.order import Order, OrderStatus
from app.models.customer import Customer
from app.models.menu import MenuItem
from app.models.user import User
from app.core.email import send_order_confirmation_email

class ConfirmationAgent:
    def __init__(self):
        pass
    
    async def process(self, message: str, context: Dict) -> str:
        session_id = context.get("session_id", "default")
        cart_storage = context.get("cart_storage", {})
        
        try:
            if any(word in message.lower() for word in ["confirm", "place", "yes", "proceed"]):
                return await self._confirm_order(session_id, cart_storage)
            
            elif any(word in message.lower() for word in ["cancel", "no", "abort"]):
                return "Order cancelled. You can start a new order anytime!"
            
            else:
                return "Would you like to confirm your order? Say 'confirm order' or 'cancel order'."
                
        except Exception as e:
            return "I'm having trouble confirming your order. Please try again."
    
    async def _confirm_order(self, session_id: str, cart_storage: Dict) -> str:
        if session_id not in cart_storage or not cart_storage[session_id]:
            return "Your cart is empty. Add some items first!"
        
        print(f"[CONFIRM DEBUG] Confirming order for session_id: {session_id}")
        
        # Get or create customer
        customer, created = await Customer.get_or_create(session_id=session_id)
        print(f"[CONFIRM DEBUG] Customer ID: {customer.id}, Created: {created}")
        
        # Calculate total and create order items
        cart = cart_storage[session_id]
        subtotal = 0
        order_items = []
        
        for item_id, quantity in cart.items():
            item = await MenuItem.get(id=item_id)
            item_total = float(item.price) * quantity
            subtotal += item_total
            order_items.append({
                "item_id": item_id,
                "name": item.name,
                "quantity": quantity,
                "price": float(item.price)
            })
        
        # Calculate tax (8%) and total
        tax = subtotal * 0.08
        total = subtotal + tax
        
        print(f"[CONFIRM DEBUG] Subtotal: ${subtotal:.2f}, Tax: ${tax:.2f}, Total: ${total:.2f}")
        
        # Create order
        order = await Order.create(
            customer=customer,
            items=order_items,
            total=total,
            status=OrderStatus.CONFIRMED
        )
        
        print(f"[CONFIRM DEBUG] Order created with ID: {order.id}")
        
        # Clear cart
        cart_storage[session_id] = {}
        
        # Try to send email notification if user is registered
        email_sent = False
        try:
            print(f"[EMAIL DEBUG] Looking for user with email: {session_id}")
            user = await User.get_or_none(email=session_id)
            
            if user:
                print(f"[EMAIL DEBUG] User found: {user.username} ({user.email})")
                print(f"[EMAIL DEBUG] Sending order confirmation email...")
                email_sent = await send_order_confirmation_email(
                    user_email=user.email,
                    username=user.username,
                    order_id=order.id,
                    items=order_items,
                    total=total
                )
                print(f"[EMAIL DEBUG] Email sent status: {email_sent}")
            else:
                print(f"[EMAIL DEBUG] No user found with email: {session_id}")
        except Exception as e:
            print(f"[EMAIL DEBUG] Failed to send order confirmation email: {str(e)}")
            import traceback
            traceback.print_exc()
        
        response = f"""Order confirmed! 🎉

Order #: {order.id}
Subtotal: ${subtotal:.2f}
Tax (8%): ${tax:.2f}
Total: ${total:.2f}
Status: Confirmed

Your order is being prepared. Thank you for choosing our cafe!"""

        if email_sent:
            response += "\n\n📧 A confirmation email has been sent to your registered email address."
        
        response += "\n\nYou can start a new order anytime by saying 'show menu'."
        
        return response
