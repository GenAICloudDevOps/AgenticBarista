from langchain.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from app.tools.langchain_tools import get_menu_items, get_item_recommendations
from app.core.bedrock import get_haiku_response
import asyncio

# Define tools using LangChain's @tool decorator
@tool
async def get_menu_tool() -> str:
    """Get all menu items available at the coffee shop."""
    try:
        return await get_menu_items()
    except Exception as e:
        return f"Error getting menu: {str(e)}"

@tool
async def get_recommendations_tool(preferences: str) -> str:
    """Get coffee recommendations based on customer preferences."""
    try:
        return await get_item_recommendations(preferences)
    except Exception as e:
        return f"Error getting recommendations: {str(e)}"

@tool
def add_to_cart_tool(item_name: str) -> str:
    """Add an item to the customer's cart."""
    return f"Added {item_name} to your cart!"

@tool
def show_cart_tool() -> str:
    """Show the contents of the customer's cart."""
    return "Your cart: 1x Latte ($4.50), 1x Blueberry Muffin ($3.00), Total: $7.50"

@tool
def confirm_order_tool() -> str:
    """Confirm and place the customer's order."""
    return """Hello there!
We're thrilled to confirm your order at Coffee and AI! ☕✨
Your order has been placed and will be ready in 10-15 minutes. Here are the details:
- 1x Cappuccino - $4.00
- 1x Blueberry Muffin - $3.00
Total: $7.00
Thank you for choosing Coffee and AI!"""

# Simple agent wrapper that mimics create_agent behavior
class SimpleAgent:
    def __init__(self, tools, system_prompt):
        self.tools = tools
        self.system_prompt = system_prompt
        self.tool_map = {tool.name: tool for tool in tools}
    
    async def ainvoke(self, inputs):
        """Process input and return response"""
        try:
            # Extract message content
            if isinstance(inputs, dict) and "messages" in inputs:
                messages = inputs["messages"]
                if messages and hasattr(messages[-1], 'content'):
                    user_input = messages[-1].content
                else:
                    user_input = str(messages[-1]) if messages else ""
            else:
                user_input = str(inputs)
            
            # Simple tool selection based on keywords
            selected_tool = None
            for tool in self.tools:
                if self._should_use_tool(tool.name, user_input):
                    selected_tool = tool
                    break
            
            if selected_tool:
                # Use the tool
                try:
                    if selected_tool.name == "get_menu_tool":
                        result = await selected_tool.ainvoke({})
                    elif selected_tool.name == "get_recommendations_tool":
                        result = await selected_tool.ainvoke({"preferences": user_input})
                    elif selected_tool.name == "add_to_cart_tool":
                        item_name = self._extract_item_name(user_input)
                        result = selected_tool.invoke({"item_name": item_name})
                    elif selected_tool.name == "show_cart_tool":
                        result = selected_tool.invoke({})
                    elif selected_tool.name == "confirm_order_tool":
                        result = selected_tool.invoke({})
                    else:
                        result = "Tool executed successfully"
                    
                    # Format response with tool result
                    prompt = f"{self.system_prompt}\n\nUser: {user_input}\n\nTool Result: {result}\n\nProvide a helpful response:"
                    response = get_haiku_response(prompt)
                except Exception as e:
                    response = f"I had trouble using that tool. {str(e)}"
            else:
                # Direct AI response
                prompt = f"{self.system_prompt}\n\nUser: {user_input}\n\nProvide a helpful response:"
                response = get_haiku_response(prompt)
            
            return {"output": response}
            
        except Exception as e:
            return {"output": f"I'm having trouble processing your request. Error: {str(e)}"}
    
    def _should_use_tool(self, tool_name, user_input):
        """Determine if a tool should be used based on user input"""
        keywords = {
            "get_menu_tool": ["menu", "coffee", "drinks", "what do you have", "show me"],
            "get_recommendations_tool": ["recommend", "suggest", "best", "favorite"],
            "add_to_cart_tool": ["add", "order", "get", "buy"],
            "show_cart_tool": ["cart", "total", "show"],
            "confirm_order_tool": ["place order", "confirm", "checkout", "finish", "complete order"]
        }
        tool_keywords = keywords.get(tool_name, [])
        return any(keyword in user_input.lower() for keyword in tool_keywords)
    
    def _extract_item_name(self, user_input):
        """Extract item name from user input"""
        words = user_input.lower().split()
        # Look for common coffee items
        coffee_items = ["latte", "cappuccino", "americano", "espresso", "mocha"]
        for item in coffee_items:
            if item in user_input.lower():
                return item.title()
        
        # Fallback: look for word after "add" or "order"
        for i, word in enumerate(words):
            if word in ["add", "order"] and i + 1 < len(words):
                return words[i + 1].title()
        
        return "Coffee"

# Create agents using simple implementation (mimics create_agent)
menu_executor = SimpleAgent(
    tools=[get_menu_tool, get_recommendations_tool],
    system_prompt="You are a friendly barista assistant at Coffee and AI. You love coffee and enjoy helping customers discover new drinks. Use your tools to provide accurate menu information and recommendations."
)

order_executor = SimpleAgent(
    tools=[add_to_cart_tool, show_cart_tool],
    system_prompt="You are a barista assistant at Coffee and AI handling orders. Be precise and helpful with cart operations. Use your tools to manage customer orders."
)

confirmation_executor = SimpleAgent(
    tools=[confirm_order_tool],
    system_prompt="You handle order confirmations at Coffee and AI. Be friendly and confirm order details clearly."
)
