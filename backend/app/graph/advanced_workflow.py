from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from app.core.bedrock import get_haiku_response
from app.prompts.templates import MENU_PROMPT, ORDER_PROMPT, CONFIRMATION_PROMPT, INTENT_PROMPT
from app.tools.langchain_tools import AVAILABLE_TOOLS, get_menu_items, get_item_recommendations
from app.memory.vector_memory import vector_memory
from app.models.menu import MenuItem
import json

class AdvancedCafeState(dict):
    """Advanced state for the cafe chatbot with tool calling"""
    session_id: str
    messages: List[Any]
    cart: Dict[int, int]
    current_intent: str
    tool_calls: List[Dict]
    menu_context: List[Dict]
    total_amount: float
    user_preferences: Dict[str, Any]

async def intent_classification_node(state: AdvancedCafeState) -> Dict[str, Any]:
    """Classify user intent using LangChain prompt template"""
    try:
        user_message = state["messages"][-1].content
        session_id = state.get("session_id", "default")
        
        # Load conversation history from vector memory
        memory_vars = vector_memory.load_memory_variables({
            "session_id": session_id,
            "user_message": user_message
        })
        
        # Simple intent classification based on keywords - ORDER FIRST
        message_lower = user_message.lower()
        
        # Menu queries (check first for menu-specific requests)
        if any(phrase in message_lower for phrase in [
            "show menu", "show me the menu", "what do you have", "menu please",
            "see the menu", "view menu", "tell me about coffee", "why people love coffee",
            "coffee culture", "recommend", "suggest", "best coffee"
        ]):
            intent = "MENU"
        
        # Order operations (specific add/buy actions)
        elif any(word in message_lower for word in [
            "add", "order", "get", "buy", "purchase", "want", "i'll have", "give me"
        ]) or any(phrase in message_lower for phrase in [
            "add a", "add an", "order a", "order an", "get a", "get an", 
            "i want a", "i want an", "i'll take", "give me a"
        ]):
            intent = "ORDER"
        
        # Cart operations
        elif any(phrase in message_lower for phrase in [
            "show cart", "my cart", "cart total", "what's in my cart"
        ]) or any(word in message_lower for word in [
            "total", "remove", "delete"
        ]):
            intent = "ORDER"
        
        # Confirmation keywords
        elif any(word in message_lower for word in [
            "confirm", "place", "yes", "proceed", "checkout", "pay"
        ]):
            intent = "CONFIRMATION"
        
        # Greetings
        elif any(word in message_lower for word in [
            "hello", "hi", "help", "start", "welcome"
        ]) and not any(word in message_lower for word in ["add", "order", "get"]):
            intent = "GREETING"
        
        # General menu/coffee queries
        elif any(word in message_lower for word in [
            "coffee", "latte", "cappuccino", "espresso", "mocha", "americano", 
            "drinks", "morning", "why", "love", "caffeine", "favorite"
        ]):
            intent = "MENU"
        
        # Default to menu for general queries
        else:
            intent = "MENU"
        
        return {
            **state,
            "current_intent": intent
        }
        
    except Exception as e:
        return {
            **state,
            "current_intent": "MENU"  # Default to menu if unsure
        }

async def menu_agent_node(state: AdvancedCafeState) -> Dict[str, Any]:
    """Enhanced menu agent with tool calling and prompt templates"""
    try:
        user_message = state["messages"][-1].content
        session_id = state.get("session_id", "default")
        
        # Get menu items directly from database
        from app.models.menu import MenuItem
        items = await MenuItem.filter(available=True)
        
        # Format menu for prompt
        menu_text = "\n".join([
            f"- {item.name}: ${float(item.price):.2f} - {item.description}"
            for item in items
        ])
        
        # Load conversation history
        memory_vars = vector_memory.load_memory_variables({
            "session_id": session_id,
            "user_message": user_message
        })
        
        # Enhanced prompt for general coffee questions
        prompt = f"""You are a knowledgeable and friendly barista assistant. You can discuss coffee culture, answer questions about coffee, and help with our menu.

Our menu:
{menu_text}

Previous conversation:
{memory_vars.get("conversation_history", "")}

Customer message: "{user_message}"

If they're asking about coffee in general (like why people love coffee in the morning), provide an informative and engaging answer about coffee culture, then naturally transition to mentioning our menu options. If they're asking about our specific menu, focus on our offerings. Be conversational and helpful."""

        ai_response = get_haiku_response(prompt)
        
        # Check if user wants recommendations
        if any(word in user_message.lower() for word in ["recommend", "suggest", "best", "favorite"]):
            # Simple recommendations based on keywords
            if "sweet" in user_message.lower():
                ai_response += "\n\nFor something sweet, I'd especially recommend our Mocha - it's espresso with chocolate and steamed milk!"
            if "strong" in user_message.lower():
                ai_response += "\n\nFor something strong, try our Espresso or Americano!"
        
        menu_items = [{"name": item.name, "price": float(item.price), "description": item.description} for item in items]
        
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=ai_response)],
            "menu_context": menu_items
        }
        
    except Exception as e:
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=f"I'm having trouble with the menu right now. Error: {str(e)}")]
        }

async def order_agent_node(state: AdvancedCafeState) -> Dict[str, Any]:
    """Enhanced order agent with tool calling"""
    try:
        user_message = state["messages"][-1].content
        session_id = state.get("session_id", "default")
        current_cart = state.get("cart", {})
        
        # Get menu items directly from database
        from app.models.menu import MenuItem
        menu_items = await MenuItem.filter(available=True)
        menu_text = "\n".join([f"- {item.name}: ${float(item.price):.2f}" for item in menu_items])
        
        # Format current cart
        cart_text = "Empty"
        if current_cart:
            cart_items = []
            for item_id, quantity in current_cart.items():
                # Find item name
                try:
                    item = await MenuItem.get(id=item_id)
                    cart_items.append(f"{quantity}x {item.name}")
                except:
                    cart_items.append(f"{quantity}x Item {item_id}")
            cart_text = ", ".join(cart_items)
        
        # Load conversation history
        memory_vars = vector_memory.load_memory_variables({
            "session_id": session_id,
            "user_message": user_message
        })
        
        # Simple prompt
        prompt = f"""You are a barista assistant handling orders. Available items:

{menu_text}

Current cart: {cart_text}

Previous conversation:
{memory_vars.get("conversation_history", "")}

Customer message: "{user_message}"

Analyze the message and respond with ONE of these actions:
1. If adding items: "ADD: [item1], [item2]" (exact item names from menu)
2. If showing cart: "SHOW_CART"
3. If removing items: "REMOVE: [item1]"
4. If unclear: "CLARIFY"

Only respond with the action, nothing else."""

        ai_response = get_haiku_response(prompt)
        
        # Process the AI response for actions
        updated_cart = current_cart.copy()
        
        if ai_response.startswith("ADD:"):
            items_to_add = ai_response.replace("ADD:", "").strip().split(",")
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
                
        elif ai_response.startswith("SHOW_CART"):
            if not updated_cart:
                response = "Your cart is empty. Add some items by saying something like 'add a latte'!"
            else:
                total = 0
                cart_display = "Your order:\n\n"
                
                for item_id, quantity in updated_cart.items():
                    try:
                        item = await MenuItem.get(id=item_id)
                        item_total = float(item.price) * quantity
                        total += item_total
                        cart_display += f"• {quantity}x {item.name} - ${item_total:.2f}\n"
                    except:
                        cart_display += f"• {quantity}x Item {item_id}\n"
                
                cart_display += f"\nTotal: ${total:.2f}\n\nSay 'confirm order' to place your order!"
                response = cart_display
        else:
            response = ai_response if not ai_response.startswith("CLARIFY") else "I can help you add items to your order! Try saying 'add a latte' or 'show my cart'."
        
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=response)],
            "cart": updated_cart
        }
        
    except Exception as e:
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=f"I'm having trouble with your order. Error: {str(e)}")]
        }

async def confirmation_agent_node(state: AdvancedCafeState) -> Dict[str, Any]:
    """Enhanced confirmation agent"""
    try:
        user_message = state["messages"][-1].content
        session_id = state.get("session_id", "default")
        current_cart = state.get("cart", {})
        
        if not current_cart:
            response = "Your cart is empty. Add some items first!"
        else:
            # Calculate total using database
            from app.models.menu import MenuItem
            total = 0
            cart_summary = []
            
            for item_id, quantity in current_cart.items():
                try:
                    item = await MenuItem.get(id=item_id)
                    item_total = float(item.price) * quantity
                    total += item_total
                    cart_summary.append(f"{quantity}x {item.name}")
                except:
                    cart_summary.append(f"{quantity}x Item {item_id}")
            
            # Load conversation history
            memory_vars = vector_memory.load_memory_variables({
                "session_id": session_id,
                "user_message": user_message
            })
            
            # Create confirmation response
            response = f"""🎉 Order Confirmed! 

Your order has been placed successfully:
{chr(10).join([f"• {item}" for item in cart_summary])}

Total: ${total:.2f}
Order ID: {session_id[:8]}

Thank you for choosing our cafe! Your order will be ready shortly. ☕"""
            
            # Clear cart after confirmation
            current_cart = {}
        
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=response)],
            "cart": current_cart
        }
        
    except Exception as e:
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=f"I'm having trouble confirming your order. Error: {str(e)}")]
        }

def route_to_agent(state: AdvancedCafeState) -> str:
    """Route to appropriate agent based on classified intent"""
    intent = state.get("current_intent", "MENU")
    
    if intent == "ORDER":
        return "order_agent"
    elif intent == "CONFIRMATION":
        return "confirmation_agent"
    elif intent == "GREETING":
        return "greeting_agent"
    else:
        return "menu_agent"

async def greeting_agent_node(state: AdvancedCafeState) -> Dict[str, Any]:
    """Handle greetings and general queries"""
    response = """Welcome to our cafe! ☕

I'm your AI barista assistant powered by LangChain and LangGraph. I can help you:
• Browse our menu with personalized recommendations
• Add items to your order with smart suggestions  
• Remember our conversation history
• Confirm your order with detailed summaries

What would you like to explore today?"""
    
    return {
        **state,
        "messages": state["messages"] + [AIMessage(content=response)]
    }

def create_advanced_workflow():
    """Create advanced LangGraph workflow with all features"""
    workflow = StateGraph(AdvancedCafeState)
    
    # Add nodes
    workflow.add_node("intent_classifier", intent_classification_node)
    workflow.add_node("menu_agent", menu_agent_node)
    workflow.add_node("order_agent", order_agent_node)
    workflow.add_node("confirmation_agent", confirmation_agent_node)
    workflow.add_node("greeting_agent", greeting_agent_node)
    
    # Set entry point
    workflow.set_entry_point("intent_classifier")
    
    # Add conditional routing from intent classifier
    workflow.add_conditional_edges(
        "intent_classifier",
        route_to_agent,
        {
            "menu_agent": "menu_agent",
            "order_agent": "order_agent",
            "confirmation_agent": "confirmation_agent",
            "greeting_agent": "greeting_agent"
        }
    )
    
    # All agents end the workflow
    workflow.add_edge("menu_agent", END)
    workflow.add_edge("order_agent", END)
    workflow.add_edge("confirmation_agent", END)
    workflow.add_edge("greeting_agent", END)
    
    return workflow.compile()

# Create the advanced workflow
advanced_workflow = create_advanced_workflow()
