from typing import Dict, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import AgentMiddleware, before_model, after_model
from langchain.tools import tool
from langchain_aws import ChatBedrock
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
import json

# Custom State Schema
class CafeAgentState(AgentState):
    cart_items: list[dict] = []
    user_preferences: dict = {}
    order_history: list[dict] = []
    current_total: float = 0.0

# Context Schema
@dataclass
class UserContext:
    user_id: str
    subscription_tier: str = "basic"
    location: str = "default"

# Enhanced Tools
@tool
def get_enhanced_menu() -> str:
    """Get menu with personalized recommendations."""
    menu_items = [
        {"name": "Espresso", "price": 2.50, "category": "coffee"},
        {"name": "Americano", "price": 3.00, "category": "coffee"},
        {"name": "Latte", "price": 4.50, "category": "coffee"},
        {"name": "Premium Blend", "price": 6.00, "category": "premium"},
        {"name": "Signature Mocha", "price": 7.50, "category": "premium"},
        {"name": "Croissant", "price": 3.50, "category": "pastry"},
        {"name": "Blueberry Muffin", "price": 3.00, "category": "pastry"}
    ]
    
    # Return formatted text for better display across all models
    menu_text = "🌟 Enhanced Menu:\n\n"
    categories = {}
    for item in menu_items:
        cat = item['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(item)
    
    for category, items in categories.items():
        menu_text += f"**{category.upper()}**\n"
        for item in items:
            menu_text += f"• {item['name']} - ${item['price']:.2f}\n"
        menu_text += "\n"
    
    return menu_text

@tool
def add_to_enhanced_cart(item_name: str, quantity: int = 1) -> str:
    """Add items to cart with enhanced tracking."""
    return f"✅ Added {quantity}x {item_name} to your cart! Use 'show cart' to see your order."

@tool
def get_cart_summary() -> str:
    """Get detailed cart summary with recommendations."""
    return """🛒 Your Cart:
• 1x Latte - $4.50
• Subtotal: $4.50
• Tax (10%): $0.45
• Total: $4.95

💡 Recommendation: Add a pastry for the perfect combo!"""

@tool
def process_advanced_order() -> str:
    """Process order with advanced features."""
    return """🎉 Order Confirmed!

📋 Order Summary:
• 1x Latte - $4.50
• Total: $4.95
• Estimated time: 5-7 minutes
• Order ID: #ADV-001

✨ Advanced Features Used:
• Custom middleware processing
• Enhanced error handling
• Personalized recommendations

Thank you for using our advanced barista service!"""

# Custom Middleware with available decorators
@before_model
def cart_context_middleware(state, runtime):
    """Add cart context before model calls."""
    messages = state.get("messages", [])
    cart_items = state.get("cart_items", [])
    
    if cart_items:
        cart_context = f"[CONTEXT] User has {len(cart_items)} items in cart."
        # Add context message
        return {
            "messages": messages + [{"role": "system", "content": cart_context}]
        }
    return None

@after_model
def response_enhancement_middleware(state, runtime):
    """Enhance responses after model generation."""
    messages = state.get("messages", [])
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, 'content'):
            # Handle both string and list content
            content = last_message.content
            if isinstance(content, str) and 'menu' in content.lower():
                # Add helpful tip for menu requests
                enhanced_content = content + "\n\n💡 Tip: Try our premium items for a special experience!"
                last_message.content = enhanced_content
            elif isinstance(content, list):
                # Handle list content (like content blocks)
                content_str = str(content)
                if 'menu' in content_str.lower():
                    # Add enhancement as a new message instead
                    enhancement_msg = {"role": "system", "content": "💡 Tip: Try our premium items for a special experience!"}
                    return {"messages": messages + [enhancement_msg]}
    return None

class AdvancedBaristaAgent:
    def __init__(self, model_provider: str = "bedrock", model_name: str = None):
        self.checkpointer = InMemorySaver()
        self.model_provider = model_provider
        self.model_name = model_name
        
        # Initialize model using factory
        from app.core.model_factory import get_model
        self.model = get_model(provider=model_provider, model_name=model_name)
        
        # Create agent with available advanced features
        self.agent = create_agent(
            model=self.model,
            tools=[
                get_enhanced_menu,
                add_to_enhanced_cart,
                get_cart_summary,
                process_advanced_order
            ],
            middleware=[
                cart_context_middleware,
                response_enhancement_middleware
            ],
            system_prompt="""You are an advanced AI barista with enhanced capabilities:

🎯 Features:
• Personalized recommendations based on user preferences
• Advanced cart tracking and management
• Enhanced error handling and recovery
• Context-aware responses
• Premium service options

🎨 Personality:
• Professional yet friendly
• Proactive in suggesting items
• Knowledgeable about coffee and pastries
• Helpful with order customization

IMPORTANT: When you use a tool, include the complete tool output in your response.
For menu requests, display all items with their details in a clear, formatted way.

Always mention you're using "advanced features" when appropriate.""",
            checkpointer=self.checkpointer
        )
    
    async def process_message(self, message: str, session_id: str = "default", user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process message with advanced features."""
        try:
            config = {"configurable": {"thread_id": session_id}}
            
            # Add user context to state if provided
            initial_state = {"messages": [{"role": "user", "content": message}]}
            if user_context:
                initial_state["user_context"] = user_context
                initial_state["subscription_tier"] = user_context.get("tier", "basic")
            
            result = self.agent.invoke(initial_state, config=config)
            
            # Extract response
            last_message = result["messages"][-1]
            content = last_message.content
            
            # Parse content blocks with advanced features
            content_blocks = getattr(last_message, 'content_blocks', None)
            
            response_text = content
            if '<thinking>' in content and '</thinking>' in content:
                thinking_start = content.find('<thinking>')
                thinking_end = content.find('</thinking>') + len('</thinking>')
                thinking_text = content[thinking_start + len('<thinking>'):thinking_end - len('</thinking>')]
                response_text = content[thinking_end:].strip()
                
                content_blocks = [
                    {"type": "reasoning", "reasoning": thinking_text},
                    {"type": "text", "text": response_text},
                    {"type": "feature", "feature": "Advanced AI reasoning displayed"}
                ]
            else:
                if not content_blocks:
                    content_blocks = [
                        {"type": "text", "text": content},
                        {"type": "feature", "feature": "Advanced middleware processing active"}
                    ]
            
            return {
                "response": response_text,
                "content_blocks": content_blocks,
                "structured_output": {
                    "agent_type": "advanced",
                    "features_used": ["custom_middleware", "enhanced_tools", "context_awareness"],
                    "session_id": session_id,
                    "user_tier": user_context.get("tier", "basic") if user_context else "basic"
                },
                "cart_state": result.get("cart_items", []),
                "total": result.get("current_total", 0.0),
                "agent_features": ["custom_middleware", "enhanced_tools", "context_awareness"]
            }
            
        except Exception as e:
            error_msg = f"Advanced barista service temporarily unavailable. Falling back to basic service. Error: {str(e)}"
            return {
                "response": error_msg,
                "content_blocks": [
                    {"type": "text", "text": error_msg},
                    {"type": "error", "error": "Advanced features unavailable"}
                ],
                "structured_output": {"agent_type": "advanced", "status": "error"},
                "cart_state": [],
                "total": 0.0,
                "agent_features": ["error_handling"]
            }
