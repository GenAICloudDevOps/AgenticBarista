from typing import Dict, List
from app.models.menu import MenuItem
from app.core.bedrock import get_haiku_response
import re

class OrderAgent:
    def __init__(self):
        pass
    
    async def process(self, message: str, context: Dict) -> str:
        session_id = context.get("session_id", "default")
        cart_storage = context.get("cart_storage", {})
        
        try:
            # Get menu for AI context
            menu_items = await MenuItem.filter(available=True)
            menu_context = "\n".join([f"- {item.name}: ${float(item.price):.2f}" for item in menu_items])
            
            # Use AI for intent detection and item extraction
            prompt = f"""You are a barista assistant handling orders. Available items:

{menu_context}

Customer message: "{message}"

Analyze the message and respond with ONE of these actions:
1. If adding items: "ADD: [item1], [item2]" (exact item names from menu)
2. If showing cart: "SHOW_CART"
3. If removing items: "REMOVE: [item1]"
4. If unclear: "CLARIFY"

Only respond with the action, nothing else."""

            try:
                ai_response = get_haiku_response(prompt)
                
                if ai_response.startswith("ADD:"):
                    items_to_add = ai_response.replace("ADD:", "").strip().split(",")
                    return await self._handle_add_to_cart_ai(items_to_add, session_id, cart_storage)
                elif ai_response.startswith("SHOW_CART"):
                    return await self._show_cart(session_id, cart_storage)
                elif ai_response.startswith("REMOVE:"):
                    items_to_remove = ai_response.replace("REMOVE:", "").strip().split(",")
                    return await self._handle_remove_from_cart_ai(items_to_remove, session_id, cart_storage)
            except:
                pass
            
            # Fallback to rule-based logic
            if any(word in message.lower() for word in ["add", "order", "get", "want"]):
                return await self._handle_add_to_cart(message, session_id, cart_storage)
            elif any(word in message.lower() for word in ["cart", "order", "total"]):
                return await self._show_cart(session_id, cart_storage)
            elif any(word in message.lower() for word in ["remove", "delete", "cancel"]):
                return await self._handle_remove_from_cart(message, session_id, cart_storage)
            else:
                return "I can help you add items to your order! Try saying 'add a latte' or 'show my cart'."
                
        except Exception as e:
            return "I'm having trouble with your order. Please try again."
    
    async def _handle_add_to_cart_ai(self, items_to_add: List[str], session_id: str, cart_storage: Dict) -> str:
        menu_items = await MenuItem.filter(available=True)
        added_items = []
        
        for item_text in items_to_add:
            item_text = item_text.strip()
            for item in menu_items:
                if item.name.lower() in item_text.lower():
                    if session_id not in cart_storage:
                        cart_storage[session_id] = {}
                    
                    if item.id in cart_storage[session_id]:
                        cart_storage[session_id][item.id] += 1
                    else:
                        cart_storage[session_id][item.id] = 1
                    
                    added_items.append(f"1x {item.name} (${float(item.price):.2f} each)")
                    break
        
        if added_items:
            return f"Added to your order:\n• " + "\n• ".join(added_items) + "\n\nSay 'show cart' to see your total!"
        else:
            return "I couldn't find those items on our menu. Try asking 'show menu' to see what's available."
    
    async def _handle_add_to_cart(self, message: str, session_id: str, cart_storage: Dict) -> str:
        menu_items = await MenuItem.filter(available=True)
        added_items = []
        
        for item in menu_items:
            if item.name.lower() in message.lower():
                quantity = 1
                quantity_match = re.search(r'(\d+)\s*' + re.escape(item.name.lower()), message.lower())
                if quantity_match:
                    quantity = int(quantity_match.group(1))
                
                if session_id not in cart_storage:
                    cart_storage[session_id] = {}
                
                if item.id in cart_storage[session_id]:
                    cart_storage[session_id][item.id] += quantity
                else:
                    cart_storage[session_id][item.id] = quantity
                
                added_items.append(f"{quantity}x {item.name} (${float(item.price):.2f} each)")
        
        if added_items:
            return f"Added to your order:\n• " + "\n• ".join(added_items) + "\n\nSay 'show cart' to see your total!"
        else:
            return "I couldn't find that item on our menu. Try asking 'show menu' to see what's available."
    
    async def _show_cart(self, session_id: str, cart_storage: Dict) -> str:
        if session_id not in cart_storage or not cart_storage[session_id]:
            return "Your cart is empty. Add some items by saying something like 'add a latte'!"
        
        cart = cart_storage[session_id]
        total = 0
        cart_display = "Your order:\n\n"
        
        for item_id, quantity in cart.items():
            item = await MenuItem.get(id=item_id)
            item_total = float(item.price) * quantity
            total += item_total
            cart_display += f"• {quantity}x {item.name} - ${item_total:.2f}\n"
        
        cart_display += f"\nTotal: ${total:.2f}\n\nSay 'confirm order' to place your order!"
        return cart_display
    
    async def _handle_remove_from_cart(self, message: str, session_id: str, cart_storage: Dict) -> str:
        if session_id not in cart_storage:
            return "Your cart is empty."
        
        menu_items = await MenuItem.filter(available=True)
        removed_items = []
        
        for item in menu_items:
            if item.name.lower() in message.lower() and item.id in cart_storage[session_id]:
                del cart_storage[session_id][item.id]
                removed_items.append(item.name)
        
        if removed_items:
            return f"Removed from your order: {', '.join(removed_items)}"
        else:
            return "I couldn't find that item in your cart."
    
    async def _handle_remove_from_cart_ai(self, items_to_remove: List[str], session_id: str, cart_storage: Dict) -> str:
        if session_id not in cart_storage:
            return "Your cart is empty."
        
        menu_items = await MenuItem.filter(available=True)
        removed_items = []
        
        for item_text in items_to_remove:
            item_text = item_text.strip()
            for item in menu_items:
                if item.name.lower() in item_text.lower() and item.id in cart_storage[session_id]:
                    del cart_storage[session_id][item.id]
                    removed_items.append(item.name)
                    break
        
        if removed_items:
            return f"Removed from your order: {', '.join(removed_items)}"
        else:
            return "I couldn't find those items in your cart."
