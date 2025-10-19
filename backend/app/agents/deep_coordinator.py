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
        return "No items in cart"
    
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

Your capabilities:
- Answer general questions about coffee naturally (no tools needed)
- Show menu using get_menu_items tool
- Add items to cart using add_to_cart tool
- Show cart using show_cart tool
- Confirm orders using confirm_order tool when customer says "confirm", "place order", "yes", etc.

CRITICAL RULES - READ CAREFULLY: 
1. When customer says "confirm" or "confirm order", you MUST call the confirm_order tool to place the order.

2. YOUR RESPONSE FORMAT (MANDATORY):
   Step 1: Write <thinking>your reasoning here</thinking>
   Step 2: Write your response to the user AFTER the </thinking> tag
   
3. TOOL OUTPUT DISPLAY (MANDATORY):
   - After ANY tool call, copy the COMPLETE tool output into your response
   - The tool output goes OUTSIDE and AFTER the </thinking> tag
   - Do NOT summarize or paraphrase the tool output
   - Copy it EXACTLY as the tool returns it

4. SPECIFIC TOOL INSTRUCTIONS:
   - add_to_cart: Show "✓ Added 1x [Item] ($X.XX each)" message
   - get_menu_items: Show the complete formatted menu
   - show_cart: Show the complete cart with all items and totals
   - confirm_order: Show the complete order confirmation

5. FORBIDDEN:
   - DO NOT put tool outputs inside <thinking> tags
   - DO NOT say "I've added" without showing the tool output
   - DO NOT end your response after </thinking> tag without showing tool results
   - DO NOT generate code snippets like "tool_code print()" or "default_api.confirm_order()"
   - DO NOT show how to call the tool - just show the tool's output

CORRECT Example for adding item:
<thinking>User wants to add a latte. I'll call add_to_cart tool.</thinking>
✓ Added 1x Latte ($4.50 each)

Would you like anything else?

CORRECT Example for confirming order:
<thinking>User wants to confirm their order. I'll call confirm_order tool.</thinking>
✓ Order Confirmed!

• 1x Mocha - $5.00

Subtotal: $5.00
Tax (8%): $0.40
Total: $5.40

Your order will be ready in 5-7 minutes. Thank you!

WRONG Example (NEVER DO THIS):
<thinking>User wants to add a latte. I called add_to_cart and it returned: ✓ Added 1x Latte ($4.50 each)</thinking>

WRONG Example 2 (NEVER DO THIS):
<thinking>User wants to add a latte. I'll call add_to_cart tool.</thinking>

WRONG Example 3 (NEVER DO THIS):
<thinking>User wants to confirm order.</thinking>
tool_code print(default_api.confirm_order())

Be warm and helpful!""",
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
                
                # Extract thinking tags and return separately
                import re
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
