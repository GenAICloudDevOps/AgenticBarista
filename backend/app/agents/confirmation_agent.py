from typing import Dict
from app.models.order import Order, OrderStatus
from app.models.customer import Customer
from app.models.menu import MenuItem

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
        
        # Get or create customer
        customer, created = await Customer.get_or_create(session_id=session_id)
        
        # Calculate total and create order items
        cart = cart_storage[session_id]
        total = 0
        order_items = []
        
        for item_id, quantity in cart.items():
            item = await MenuItem.get(id=item_id)
            item_total = float(item.price) * quantity
            total += item_total
            order_items.append({
                "item_id": item_id,
                "name": item.name,
                "quantity": quantity,
                "price": float(item.price)
            })
        
        # Create order
        order = await Order.create(
            customer=customer,
            items=order_items,
            total=total,
            status=OrderStatus.CONFIRMED
        )
        
        # Clear cart
        cart_storage[session_id] = {}
        
        return f"""Order confirmed! 🎉

Order #: {order.id}
Total: ${total:.2f}
Status: Confirmed

Your order is being prepared. Thank you for choosing our cafe!

You can start a new order anytime by saying 'show menu'."""
