from typing import Dict, Any
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware, before_model
from langchain.tools import tool
from langchain_aws import ChatBedrock
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
import json

# Define tools as standalone functions
@tool
def get_menu_tool() -> str:
    """Get all available menu items."""
    try:
        menu_items = [
            {"name": "Espresso", "price": 2.50, "description": "Rich, bold shot"},
            {"name": "Americano", "price": 3.00, "description": "Espresso with hot water"},
            {"name": "Latte", "price": 4.50, "description": "Espresso with steamed milk"},
            {"name": "Cappuccino", "price": 4.00, "description": "Equal parts espresso, milk, foam"},
            {"name": "Mocha", "price": 5.00, "description": "Espresso with chocolate"},
            {"name": "Croissant", "price": 3.50, "description": "Buttery French pastry"},
            {"name": "Blueberry Muffin", "price": 3.00, "description": "Fresh baked muffin"}
        ]
        return json.dumps(menu_items, indent=2)
    except Exception as e:
        return f"Error getting menu: {str(e)}"

@tool
def add_to_cart_tool(item_name: str, quantity: int = 1) -> str:
    """Add items to the customer's cart."""
    return f"Added {quantity}x {item_name} to your cart!"

@tool
def show_cart_tool() -> str:
    """Show current cart contents."""
    return "Your cart: 1x Latte ($4.50), Total: $4.50"

@tool
def confirm_order_tool() -> str:
    """Confirm and process the order."""
    return """Order confirmed! ☕
    
Your order:
- 1x Latte - $4.50
Total: $4.50

Your order will be ready in 5-10 minutes. Thank you for choosing Coffee and AI!"""

# Custom middleware for message trimming
@before_model
def trim_messages_middleware(state, runtime):
    """Keep only last 10 messages to manage context."""
    messages = state["messages"]
    
    if len(messages) > 10:
        # Keep first message (system) and last 9 messages
        first_msg = messages[0]
        recent_messages = messages[-9:]
        
        return {
            "messages": [
                RemoveMessage(id=REMOVE_ALL_MESSAGES),
                first_msg,
                *recent_messages
            ]
        }
    return None

class ModernBaristaAgent:
    def __init__(self, model_provider: str = "bedrock", model_name: str = None):
        self.checkpointer = InMemorySaver()
        self.cart_storage = {}
        self.model_provider = model_provider
        self.model_name = model_name
        
        # Initialize model using factory
        from app.core.model_factory import get_model
        self.model = get_model(provider=model_provider, model_name=model_name)
        
        # Create agent with middleware - LangChain v1 features
        self.agent = create_agent(
            model=self.model,
            tools=[
                get_menu_tool,
                add_to_cart_tool,
                show_cart_tool,
                confirm_order_tool
            ],
            middleware=[
                # Built-in summarization middleware
                SummarizationMiddleware(
                    model=self.model,
                    max_tokens_before_summary=2000
                ),
                # Custom message trimming middleware
                trim_messages_middleware
            ],
            system_prompt="""You are a friendly AI barista at Coffee and AI cafe. 
            Help customers browse the menu, add items to their cart, and place orders.
            Be conversational and helpful. Always confirm orders before processing.""",
            checkpointer=self.checkpointer
        )
    
    async def process_message(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """Process message using modern LangChain v1 agent with content_blocks support."""
        try:
            config = {"configurable": {"thread_id": session_id}}
            
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": message}]},
                config=config
            )
            
            # Extract the last AI message
            last_message = result["messages"][-1]
            
            # Get the raw content
            content = last_message.content
            
            # Get content_blocks - LangChain v1 feature
            content_blocks = getattr(last_message, 'content_blocks', None)
            
            # Parse content to separate thinking from response
            response_text = content
            
            # Check if content has thinking tags
            if '<thinking>' in content and '</thinking>' in content:
                # Extract thinking and response parts
                thinking_start = content.find('<thinking>')
                thinking_end = content.find('</thinking>') + len('</thinking>')
                thinking_text = content[thinking_start + len('<thinking>'):thinking_end - len('</thinking>')]
                response_text = content[thinking_end:].strip()
                
                # Create structured content blocks
                content_blocks = [
                    {"type": "reasoning", "reasoning": thinking_text},
                    {"type": "text", "text": response_text}
                ]
            else:
                # If no content_blocks, create default text block
                if not content_blocks:
                    content_blocks = [{"type": "text", "text": content}]
            
            return {
                "response": response_text,
                "content_blocks": content_blocks
            }
            
        except Exception as e:
            error_msg = f"I'm having some technical difficulties. Please try again. Error: {str(e)}"
            return {
                "response": error_msg,
                "content_blocks": [{"type": "text", "text": error_msg}]
            }
