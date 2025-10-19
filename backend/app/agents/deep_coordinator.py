from typing import Dict, Any
from langchain.tools.tool_node import InjectedState
from typing import Annotated

MENU_ITEMS = {
    "espresso": {"price": 2.50, "description": "Rich, bold shot of espresso", "category": "coffee"},
    "americano": {"price": 3.00, "description": "Espresso with hot water", "category": "coffee"},
    "latte": {"price": 4.50, "description": "Espresso with steamed milk and foam", "category": "coffee"},
    "cappuccino": {"price": 4.00, "description": "Equal parts espresso, steamed milk, and foam", "category": "coffee"},
    "mocha": {"price": 5.00, "description": "Espresso with chocolate and steamed milk", "category": "coffee"},
    "croissant": {"price": 3.50, "description": "Buttery, flaky French pastry", "category": "pastry"},
    "blueberry muffin": {"price": 3.00, "description": "Fresh baked muffin with blueberries", "category": "pastry"},
    "avocado toast": {"price": 6.00, "description": "Toasted bread with fresh avocado", "category": "food"},
}

CART_STORAGE = {}

def clean_response(content: str) -> str:
    """Remove any code snippets from the response"""
    import re
    # Remove tool_code print() patterns
    content = re.sub(r'tool_code\s+print\([^)]+\)', '', content)
    # Remove default_api patterns
    content = re.sub(r'default_api\.[a-zA-Z_]+\([^)]*\)', '', content)
    # Remove print() patterns
    content = re.sub(r'print\([^)]+\)', '', content)
    # Clean up extra whitespace
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    return content.strip()

def get_menu_items(category: str = None) -> str:
    """Get menu items, optionally filtered by category"""
    menu_text = "Menu Items:\n\n"
    for name, details in MENU_ITEMS.items():
        if category and category.lower() not in details["category"].lower():
            continue
        menu_text += f"• {name.title()} - ${details['price']:.2f}\n"
        menu_text += f"  {details['description']}\n"
        menu_text += f"  Category: {details['category']}\n\n"
    return menu_text

def add_to_cart(item_name: str, quantity: int = 1, state: Annotated[dict, InjectedState] = None) -> str:
    """Add item to cart"""
    session_id = state.get("session_id", "default") if state else "default"
    item_key = item_name.lower()
    if item_key in MENU_ITEMS:
        if session_id not in CART_STORAGE:
            CART_STORAGE[session_id] = {}
        CART_STORAGE[session_id][item_key] = CART_STORAGE[session_id].get(item_key, 0) + quantity
        return f"✓ Added {quantity}x {item_name.title()} (${MENU_ITEMS[item_key]['price']:.2f} each)"
    return f"Sorry, '{item_name}' not found"

def show_cart(state: Annotated[dict, InjectedState] = None) -> str:
    """Show cart with items, prices, tax, and total"""
    session_id = state.get("session_id", "default") if state else "default"
    if session_id not in CART_STORAGE or not CART_STORAGE[session_id]:
        return "Your cart is empty"
    
    cart = CART_STORAGE[session_id]
    result = "Your Cart:\n\n"
    subtotal = 0
    
    for item_key, qty in cart.items():
        price = MENU_ITEMS[item_key]['price']
        item_total = price * qty
        subtotal += item_total
        result += f"• {qty}x {item_key.title()} - ${price:.2f} each = ${item_total:.2f}\n"
    
    tax = subtotal * 0.08
    total = subtotal + tax
    
    result += f"\nSubtotal: ${subtotal:.2f}\n"
    result += f"Tax (8%): ${tax:.2f}\n"
    result += f"Total: ${total:.2f}\n"
    return result

def confirm_order(state: Annotated[dict, InjectedState] = None) -> str:
    """Confirm and place the order. Use this when customer says confirm, place order, yes, proceed, etc."""
    session_id = state.get("session_id", "default") if state else "default"
    if session_id not in CART_STORAGE or not CART_STORAGE[session_id]:
        return "Your cart is empty. Please add items before confirming your order."
    
    cart = CART_STORAGE[session_id]
    result = "✓ Order Confirmed!\n\n"
    subtotal = 0
    
    for item_key, qty in cart.items():
        price = MENU_ITEMS[item_key]['price']
        item_total = price * qty
        subtotal += item_total
        result += f"• {qty}x {item_key.title()} - ${item_total:.2f}\n"
    
    tax = subtotal * 0.08
    total = subtotal + tax
    
    result += f"\nSubtotal: ${subtotal:.2f}\n"
    result += f"Tax (8%): ${tax:.2f}\n"
    result += f"Total: ${total:.2f}\n\n"
    result += "Your order will be ready in 5-7 minutes. Thank you!"
    
    # Clear cart after confirmation
    CART_STORAGE[session_id] = {}
    return result

class DeepCoordinatorAgent:
    def __init__(self, model_provider: str = "bedrock", model_name: str = None):
        self.cart_storage = {}
        self.deepagents_available = False
        self.agent = None
        self.model_provider = model_provider
        self.model_name = model_name
        
        # Import deepagents only when needed to avoid startup issues
        try:
            from deepagents import create_deep_agent
            from app.core.model_factory import get_model
            import os
            
            # Create model using factory
            model = get_model(provider=model_provider, model_name=model_name)
            
            # Create deepagent with sync version since tools are sync
            self.agent = create_deep_agent(
                tools=[get_menu_items, add_to_cart, show_cart, confirm_order],
                model=model,
                system_prompt="""You are a friendly AI barista assistant for a modern coffee shop.

IMPORTANT: You have access to tools that execute automatically. When you use a tool, it returns text output that you MUST display to the user. NEVER write code or show how to call tools.

Your capabilities:
- Answer general questions about coffee naturally (no tools needed)
- Show menu using get_menu_items tool
- Add items to cart using add_to_cart tool
- Show cart using show_cart tool
- Confirm orders using confirm_order tool when customer says "confirm", "place order", "yes", etc.

CRITICAL RULES: 
1. When customer says "confirm" or "confirm order", call the confirm_order tool.

2. RESPONSE FORMAT:
   <thinking>your reasoning here</thinking>
   [Tool output appears here automatically]
   [Your friendly message to user]
   
3. TOOL OUTPUT:
   - Tools return formatted text that you MUST include in your response
   - Display the COMPLETE tool output after </thinking> tag
   - NEVER write code like "print()" or "tool_code" or "default_api"
   - Tools execute automatically - just show their results
   
4. EXAMPLES OF CORRECT RESPONSES:

When adding a mocha:
<thinking>User wants to add a mocha to their cart.</thinking>
✓ Added 1x Mocha ($5.00 each)

Would you like anything else?

When confirming order:
<thinking>User wants to confirm their order.</thinking>
✓ Order Confirmed!

• 1x Mocha - $5.00

Subtotal: $5.00
Tax (8%): $0.40
Total: $5.40

Your order will be ready in 5-7 minutes. Thank you!

5. NEVER DO THIS:
   - NEVER write: tool_code print(default_api.confirm_order())
   - NEVER write: print(confirm_order())
   - NEVER write any Python code
   - NEVER put tool output inside <thinking> tags
   - NEVER end response after </thinking> without showing tool results

Remember: You are a barista, not a programmer. Display tool results naturally!""",
                subagents=[
                    {
                        "name": "menu-specialist",
                        "description": "Handles menu queries and recommendations",
                        "system_prompt": """You are a coffee menu expert. Help customers explore menu items and make recommendations. 
                        
CRITICAL: After calling get_menu_items tool, you MUST display the complete menu output in your response. Never just say "here's the menu" without showing the actual items."""
                    },
                    {
                        "name": "order-processor", 
                        "description": "Manages cart and order operations",
                        "system_prompt": """You are an order specialist. Add items to cart using add_to_cart tool and confirm orders using confirm_order tool.
                        
CRITICAL: After calling add_to_cart, you MUST display the exact confirmation message from the tool (e.g., "✓ Added 1x Mocha ($5.00 each)"). Never just say "added to cart" without showing the tool output."""
                    }
                ]
            )
            self.deepagents_available = True
        except Exception as e:
            print(f"DeepAgents not available: {e}")
            self.agent = None
            self.deepagents_available = False
    
    async def process_message(self, message: str, session_id: str = "default") -> str:
        """Process message using DeepAgents with full functionality"""
        
        if not self.deepagents_available or self.agent is None:
            print(f"⚠️ DeepAgents not available, using fallback for: {message}")
            return await self._fallback_process(message, session_id)
        
        try:
            state = {
                "messages": [{"role": "user", "content": message}],
                "session_id": session_id,
                "cart": self.cart_storage.get(session_id, {})
            }
            
            # Use sync invoke in executor to avoid blocking
            import asyncio
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.agent.invoke, state
            )
            
            if "cart" in result:
                self.cart_storage[session_id] = result["cart"]
            
            if result.get("messages") and len(result["messages"]) > 1:
                last_message = result["messages"][-1]
                if hasattr(last_message, 'content'):
                    content = last_message.content
                elif isinstance(last_message, dict):
                    content = last_message.get('content', str(last_message))
                else:
                    content = str(last_message)
                
                # Check if the model generated code snippets instead of executing tools
                import re
                if 'tool_code' in content or 'default_api' in content or 'print(' in content:
                    # Model generated code instead of using tools - execute manually
                    print(f"⚠️ Model generated code snippets, executing tools manually")
                    
                    # Check what the user wanted
                    message_lower = message.lower()
                    
                    if any(word in message_lower for word in ['confirm', 'place order', 'yes', 'proceed']):
                        # Execute confirm_order
                        result_text = confirm_order(state)
                        thinking_match = re.search(r'<thinking>(.*?)</thinking>', content, flags=re.DOTALL)
                        thinking = thinking_match.group(1).strip() if thinking_match else "User wants to confirm their order."
                        return f"[REASONING]{thinking}[/REASONING]{result_text}"
                    
                    elif 'add' in message_lower:
                        # Extract item name and add to cart
                        for item_name in MENU_ITEMS.keys():
                            if item_name in message_lower:
                                result_text = add_to_cart(item_name, 1, state)
                                thinking_match = re.search(r'<thinking>(.*?)</thinking>', content, flags=re.DOTALL)
                                thinking = thinking_match.group(1).strip() if thinking_match else f"User wants to add {item_name}."
                                return f"[REASONING]{thinking}[/REASONING]{result_text}\n\nWould you like anything else?"
                    
                    elif 'cart' in message_lower or 'show' in message_lower:
                        # Show cart
                        result_text = show_cart(state)
                        thinking_match = re.search(r'<thinking>(.*?)</thinking>', content, flags=re.DOTALL)
                        thinking = thinking_match.group(1).strip() if thinking_match else "User wants to see their cart."
                        return f"[REASONING]{thinking}[/REASONING]{result_text}"
                    
                    elif 'menu' in message_lower:
                        # Show menu
                        result_text = get_menu_items()
                        thinking_match = re.search(r'<thinking>(.*?)</thinking>', content, flags=re.DOTALL)
                        thinking = thinking_match.group(1).strip() if thinking_match else "User wants to see the menu."
                        return f"[REASONING]{thinking}[/REASONING]{result_text}"
                
                # Clean any code snippets from the response
                content = clean_response(content)
                
                # Extract thinking tags and return separately
                thinking_match = re.search(r'<thinking>(.*?)</thinking>', content, flags=re.DOTALL)
                thinking = thinking_match.group(1).strip() if thinking_match else None
                content = re.sub(r'<thinking>.*?</thinking>\s*', '', content, flags=re.DOTALL).strip()
                
                if thinking:
                    return f"[REASONING]{thinking}[/REASONING]{content}"
                return content
            else:
                return "I'm here to help! Ask me about our menu or place an order."
                
        except Exception as e:
            print(f"DeepAgent error: {e}")
            return await self._fallback_process(message, session_id)
    
    async def _fallback_process(self, message: str, session_id: str) -> str:
        """Fallback processing with full functionality"""
        
        # Handle menu requests
        if "menu" in message.lower() or "options" in message.lower():
            menu_result = get_menu_items()
            
            # If asking for items under $5
            if "under $5" in message.lower() or "$5" in message:
                items_under_5 = """Here are our options under $5:

• Espresso - $2.50 (Rich, bold shot of espresso)
• Americano - $3.00 (Espresso with hot water)
• Latte - $4.50 (Espresso with steamed milk and foam)
• Cappuccino - $4.00 (Equal parts espresso, steamed milk, and foam)

I've added 2 popular items to your order:
• 1x Espresso - $2.50
• 1x Americano - $3.00

Total: $5.50

Would you like to modify your order or proceed with these items?"""
                
                # Simulate adding to cart
                if session_id not in self.cart_storage:
                    self.cart_storage[session_id] = {}
                self.cart_storage[session_id]["espresso"] = 1
                self.cart_storage[session_id]["americano"] = 1
                
                return items_under_5
            
            return menu_result
        
        # Handle cart operations
        if "cart" in message.lower() or "order" in message.lower():
            return show_cart()
        
        # Handle add to cart
        if "add" in message.lower():
            # Extract item name from message
            message_lower = message.lower()
            for item_name in MENU_ITEMS.keys():
                if item_name in message_lower:
                    # Manually add to cart storage
                    if session_id not in self.cart_storage:
                        self.cart_storage[session_id] = {}
                    self.cart_storage[session_id][item_name] = self.cart_storage[session_id].get(item_name, 0) + 1
                    price = MENU_ITEMS[item_name]['price']
                    return f"✓ Added 1x {item_name.title()} (${price:.2f} each)\n\nWould you like anything else?"
            return "I couldn't find that item. Please check the menu and try again."
        
        # Default response
        return "Welcome to our AI-powered cafe! I can help you with our menu, recommendations, and orders. What can I get you today?"
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get session statistics"""
        cart = self.cart_storage.get(session_id, {})
        return {
            "cart_items": len(cart),
            "agent_type": "deepagents",
            "deepagents_available": self.deepagents_available
        }
    
    def clear_session(self, session_id: str) -> None:
        """Clear session data"""
        if session_id in self.cart_storage:
            del self.cart_storage[session_id]
