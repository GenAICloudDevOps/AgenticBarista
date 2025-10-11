from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from app.graph.state import CafeState
from app.core.bedrock import get_haiku_response
from app.models.menu import MenuItem
import json

async def menu_node(state: CafeState) -> Dict[str, Any]:
    """Handle menu-related queries"""
    try:
        # Get latest user message
        user_message = state["messages"][-1].content
        
        # Get menu items for context
        items = await MenuItem.filter(available=True)
        menu_context = "\n".join([f"- {item.name}: ${float(item.price):.2f} - {item.description}" for item in items])
        
        prompt = f"""You are a helpful barista assistant. Here's our menu:

{menu_context}

Customer message: "{user_message}"

Respond naturally and helpfully about our menu items. Be friendly and conversational."""

        ai_response = get_haiku_response(prompt)
        
        return {
            "messages": state["messages"] + [AIMessage(content=ai_response)],
            "current_agent": "menu",
            "menu_context": [{"name": item.name, "price": float(item.price), "description": item.description} for item in items]
        }
    except Exception as e:
        return {
            "messages": state["messages"] + [AIMessage(content="I'm having trouble with the menu right now. Please try again.")],
            "current_agent": "menu"
        }

async def order_node(state: CafeState) -> Dict[str, Any]:
    """Handle order-related operations"""
    try:
        user_message = state["messages"][-1].content
        session_id = state.get("session_id", "default")
        current_cart = state.get("cart", {})
        
        # Get menu for context
        menu_items = await MenuItem.filter(available=True)
        menu_context = "\n".join([f"- {item.name}: ${float(item.price):.2f}" for item in menu_items])
        
        prompt = f"""You are a barista assistant handling orders. Available items:

{menu_context}

Current cart: {json.dumps(current_cart) if current_cart else "Empty"}

Customer message: "{user_message}"

Analyze the message and respond with ONE of these actions:
1. If adding items: "ADD: [item1], [item2]" (exact item names from menu)
2. If showing cart: "SHOW_CART"
3. If removing items: "REMOVE: [item1]"
4. If unclear: "CLARIFY"

Only respond with the action, nothing else."""

        ai_response = get_haiku_response(prompt)
        
        # Process AI response
        if ai_response.startswith("ADD:"):
            items_to_add = ai_response.replace("ADD:", "").strip().split(",")
            updated_cart = current_cart.copy()
            added_items = []
            
            for item_text in items_to_add:
                item_text = item_text.strip()
                for item in menu_items:
                    if item.name.lower() in item_text.lower():
                        if item.id in updated_cart:
                            updated_cart[item.id] += 1
                        else:
                            updated_cart[item.id] = 1
                        added_items.append(f"1x {item.name} (${float(item.price):.2f})")
                        break
            
            if added_items:
                response = f"Added to your order:\n• " + "\n• ".join(added_items) + "\n\nSay 'show cart' to see your total!"
            else:
                response = "I couldn't find those items on our menu."
            
            return {
                "messages": state["messages"] + [AIMessage(content=response)],
                "current_agent": "order",
                "cart": updated_cart
            }
            
        elif ai_response.startswith("SHOW_CART"):
            if not current_cart:
                response = "Your cart is empty. Add some items by saying something like 'add a latte'!"
            else:
                total = 0
                cart_display = "Your order:\n\n"
                
                for item_id, quantity in current_cart.items():
                    item = await MenuItem.get(id=item_id)
                    item_total = float(item.price) * quantity
                    total += item_total
                    cart_display += f"• {quantity}x {item.name} - ${item_total:.2f}\n"
                
                cart_display += f"\nTotal: ${total:.2f}\n\nSay 'confirm order' to place your order!"
                response = cart_display
            
            return {
                "messages": state["messages"] + [AIMessage(content=response)],
                "current_agent": "order",
                "total_amount": total if current_cart else 0
            }
        
        else:
            response = "I can help you add items to your order! Try saying 'add a latte' or 'show my cart'."
            return {
                "messages": state["messages"] + [AIMessage(content=response)],
                "current_agent": "order"
            }
            
    except Exception as e:
        return {
            "messages": state["messages"] + [AIMessage(content="I'm having trouble with your order. Please try again.")],
            "current_agent": "order"
        }

async def confirmation_node(state: CafeState) -> Dict[str, Any]:
    """Handle order confirmation"""
    try:
        current_cart = state.get("cart", {})
        session_id = state.get("session_id", "default")
        
        if not current_cart:
            response = "Your cart is empty. Add some items first!"
        else:
            # Here you would save to database
            response = f"🎉 Order confirmed! Your order has been placed and will be ready shortly. Order ID: {session_id[:8]}"
            # Clear cart after confirmation
            current_cart = {}
        
        return {
            "messages": state["messages"] + [AIMessage(content=response)],
            "current_agent": "confirmation",
            "cart": current_cart
        }
        
    except Exception as e:
        return {
            "messages": state["messages"] + [AIMessage(content="I'm having trouble confirming your order. Please try again.")],
            "current_agent": "confirmation"
        }

async def router_node(state: CafeState) -> str:
    """Route to appropriate agent based on user intent"""
    try:
        user_message = state["messages"][-1].content.lower()
        
        # Menu-related keywords
        if any(word in user_message for word in ["menu", "coffee", "latte", "cappuccino", "espresso", "mocha", "americano", "what do you have", "options", "drinks"]):
            return "menu"
        
        # Order-related keywords
        elif any(word in user_message for word in ["add", "order", "cart", "remove", "total", "show", "get"]):
            return "order"
        
        # Confirmation keywords
        elif any(word in user_message for word in ["confirm", "place", "yes", "proceed", "checkout"]):
            return "confirmation"
        
        # Default to menu for general queries
        else:
            return "menu"
            
    except Exception:
        return "menu"
