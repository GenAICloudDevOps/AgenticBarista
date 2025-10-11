from typing import Dict, Any, Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_aws import ChatBedrock
from langchain.tools import tool
import json

# Custom State for Manual Graph
class WorkflowState(TypedDict):
    messages: list[dict]
    intent: str
    cart: list[dict]
    confidence: float
    needs_clarification: bool
    order_ready: bool
    session_id: str

# Tools for workflow
@tool
def analyze_intent(query: str) -> dict:
    """Analyze user intent from query."""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["menu", "what", "available", "options"]):
        return {"intent": "browse_menu", "confidence": 0.9}
    elif any(word in query_lower for word in ["add", "order", "want", "get", "latte", "espresso", "americano", "cappuccino", "mocha"]):
        return {"intent": "place_order", "confidence": 0.8}
    elif any(word in query_lower for word in ["cart", "total", "summary"]):
        return {"intent": "view_cart", "confidence": 0.9}
    elif any(word in query_lower for word in ["confirm", "yes", "proceed", "checkout"]):
        return {"intent": "confirm_order", "confidence": 0.9}
    else:
        return {"intent": "general", "confidence": 0.5}

# Workflow Nodes
def intent_analysis_node(state: WorkflowState) -> WorkflowState:
    """Analyze user intent."""
    user_message = state["messages"][-1]["content"]
    analysis = analyze_intent.invoke(user_message)
    
    return {
        **state,
        "intent": analysis["intent"],
        "confidence": analysis["confidence"],
        "needs_clarification": analysis["confidence"] < 0.7
    }

def menu_node(state: WorkflowState) -> WorkflowState:
    """Handle menu requests."""
    menu_items = [
        {"name": "Espresso", "price": 2.50},
        {"name": "Americano", "price": 3.00},
        {"name": "Latte", "price": 4.50},
        {"name": "Cappuccino", "price": 4.00},
        {"name": "Mocha", "price": 5.00}
    ]
    
    response = "🔥 **Custom StateGraph Menu** 🔥\n\n" + "\n".join([
        f"• {item['name']} - ${item['price']:.2f}" for item in menu_items
    ]) + "\n\n✨ *Powered by conditional routing & subgraphs*"
    
    return {
        **state,
        "messages": state["messages"] + [{"role": "assistant", "content": response}]
    }

def order_node(state: WorkflowState) -> WorkflowState:
    """Handle order placement."""
    user_message = state["messages"][-1]["content"]
    
    # Enhanced order parsing with better item detection
    items = []
    menu_items = {
        "latte": {"name": "Latte", "price": 4.50},
        "espresso": {"name": "Espresso", "price": 2.50},
        "americano": {"name": "Americano", "price": 3.00},
        "cappuccino": {"name": "Cappuccino", "price": 4.00},
        "mocha": {"name": "Mocha", "price": 5.00}
    }
    
    for item_key, item_data in menu_items.items():
        if item_key in user_message.lower():
            items.append({**item_data, "quantity": 1})
    
    # Add to cart
    current_cart = state.get("cart", [])
    current_cart.extend(items)
    
    if items:
        item_names = [item["name"] for item in items]
        total = sum(item["price"] * item["quantity"] for item in current_cart)
        response = f"🛒 **Advanced Order System** 🛒\n\nAdded {', '.join(item_names)} to your cart!\n\nCurrent cart: {len(current_cart)} items (${total:.2f})\n\n✨ *Using custom StateGraph routing*"
    else:
        response = "🛒 **Advanced Order System** 🛒\n\nI'd be happy to help you place an order! What would you like to add to your cart?\n\n✨ *Using custom StateGraph routing*"
    
    return {
        **state,
        "cart": current_cart,
        "messages": state["messages"] + [{"role": "assistant", "content": response}]
    }

def cart_node(state: WorkflowState) -> WorkflowState:
    """Handle cart viewing."""
    if not state["cart"]:
        response = "🛒 Your cart is currently empty.\n\n💡 Would you like to see our menu?\n\n✨ *StateGraph conditional logic active*"
    else:
        total = sum(item["price"] * item["quantity"] for item in state["cart"])
        response = f"🛒 **Your Cart** (StateGraph managed):\n" + "\n".join([
            f"• {item['name']} x{item['quantity']} - ${item['price'] * item['quantity']:.2f}"
            for item in state["cart"]
        ]) + f"\n\n💰 Total: ${total:.2f}"
    
    return {
        **state,
        "messages": state["messages"] + [{"role": "assistant", "content": response}]
    }

def clarification_node(state: WorkflowState) -> WorkflowState:
    """Handle unclear requests."""
    response = """🤔 **Smart Clarification System** 🤔

I'm not sure what you'd like to do. You can:
• 📋 View our menu
• 🛒 Place an order  
• 👀 Check your cart

✨ *Powered by conditional edge routing*

How can I help you?"""
    
    return {
        **state,
        "messages": state["messages"] + [{"role": "assistant", "content": response}],
        "needs_clarification": False
    }

def confirm_order_node(state: WorkflowState) -> WorkflowState:
    """Handle order confirmation."""
    if not state["cart"]:
        response = "🛒 Your cart is empty! Please add some items first.\n\n✨ *StateGraph order validation*"
    else:
        total = sum(item["price"] * item["quantity"] for item in state["cart"])
        response = f"""✅ **Order Confirmed!** ✅

Your order:
""" + "\n".join([
            f"• {item['name']} x{item['quantity']} - ${item['price'] * item['quantity']:.2f}"
            for item in state["cart"]
        ]) + f"""

💰 Total: ${total:.2f}

🎉 Thank you! Your order will be ready in 5-10 minutes.

✨ *Powered by StateGraph workflow*"""
        
        # Clear cart after confirmation
        state = {**state, "cart": [], "order_ready": True}
    
    return {
        **state,
        "messages": state["messages"] + [{"role": "assistant", "content": response}]
    }

# Conditional Edge Functions
def route_by_intent(state: WorkflowState) -> Literal["menu", "order", "cart", "confirm", "clarify"]:
    """Route based on detected intent."""
    if state["needs_clarification"]:
        return "clarify"
    
    intent_map = {
        "browse_menu": "menu",
        "place_order": "order", 
        "view_cart": "cart",
        "confirm_order": "confirm",
        "general": "clarify"
    }
    return intent_map.get(state["intent"], "clarify")

class CustomWorkflowAgent:
    def __init__(self):
        self.checkpointer = InMemorySaver()
        
        # Create main workflow
        self.workflow = self._create_main_workflow()
    
    def _create_main_workflow(self) -> StateGraph:
        """Create main workflow with conditional routing."""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("analyze_intent", intent_analysis_node)
        workflow.add_node("menu", menu_node)
        workflow.add_node("order", order_node)
        workflow.add_node("cart", cart_node)
        workflow.add_node("clarify", clarification_node)
        workflow.add_node("confirm", confirm_order_node)
        
        # Add edges
        workflow.add_edge(START, "analyze_intent")
        
        # Conditional routing from analysis
        workflow.add_conditional_edges("analyze_intent", route_by_intent)
        
        # All paths lead to END
        workflow.add_edge("menu", END)
        workflow.add_edge("order", END)
        workflow.add_edge("cart", END)
        workflow.add_edge("clarify", END)
        workflow.add_edge("confirm", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def process_message(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """Process message using custom workflow."""
        try:
            config = {"configurable": {"thread_id": session_id}}
            
            # Initialize state
            initial_state = {
                "messages": [{"role": "user", "content": message}],
                "intent": "",
                "cart": [],
                "confidence": 0.0,
                "needs_clarification": False,
                "order_ready": False,
                "session_id": session_id
            }
            
            # Run workflow
            result = self.workflow.invoke(initial_state, config=config)
            
            # Extract response
            response_message = result["messages"][-1]["content"]
            
            return {
                "response": response_message,
                "content_blocks": [
                    {"type": "text", "text": response_message},
                    {"type": "workflow", "workflow": "Custom StateGraph with conditional edges"}
                ],
                "intent": result["intent"],
                "confidence": result["confidence"],
                "workflow_type": "custom_stategraph",
                "features_used": ["conditional_edges", "custom_routing", "state_management"]
            }
            
        except Exception as e:
            error_msg = f"Custom workflow error: {str(e)}"
            return {
                "response": error_msg,
                "content_blocks": [{"type": "text", "text": error_msg}],
                "intent": "error",
                "confidence": 0.0,
                "workflow_type": "custom_stategraph",
                "features_used": ["error_handling"]
            }
