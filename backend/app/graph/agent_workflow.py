from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.agents.langchain_agents import menu_executor, order_executor, confirmation_executor

class AgentCafeState(TypedDict):
    session_id: str
    messages: List[BaseMessage]
    cart: Dict[str, Any]
    current_intent: str
    menu_context: List[str]
    total_amount: float

# Node functions that use standard LangChain agents
async def coordinator_node(state: AgentCafeState) -> AgentCafeState:
    """Determine which agent should handle the request"""
    user_message = state["messages"][-1].content.lower()
    
    # Intent classification - improved for order confirmation
    if any(keyword in user_message for keyword in ["place order", "confirm", "checkout", "finish", "complete order"]):
        intent = "confirmation"
    elif any(keyword in user_message for keyword in ["menu", "coffee", "drinks", "what do you have", "show me"]):
        intent = "menu"
    elif any(keyword in user_message for keyword in ["add", "order", "cart", "buy", "get"]):
        intent = "order"
    else:
        intent = "menu"  # Default to menu
    
    return {**state, "current_intent": intent}

async def menu_agent_node(state: AgentCafeState) -> AgentCafeState:
    """Handle menu-related queries using standard LangChain agent"""
    user_input = state["messages"][-1].content
    
    # Use standard LangChain agent
    response = await menu_executor.ainvoke({"messages": [HumanMessage(content=user_input)]})
    ai_message = AIMessage(content=response["output"])
    
    return {
        **state,
        "messages": state["messages"] + [ai_message]
    }

async def order_agent_node(state: AgentCafeState) -> AgentCafeState:
    """Handle order-related queries using standard LangChain agent"""
    user_input = state["messages"][-1].content
    
    # Use standard LangChain agent
    response = await order_executor.ainvoke({"messages": [HumanMessage(content=user_input)]})
    ai_message = AIMessage(content=response["output"])
    
    # Simple cart update logic
    cart = state["cart"].copy()
    if "add" in user_input.lower():
        words = user_input.lower().split()
        for i, word in enumerate(words):
            if word == "add" and i + 1 < len(words):
                item_name = words[i + 1]
                cart[item_name] = cart.get(item_name, 0) + 1
                break
    
    return {
        **state,
        "messages": state["messages"] + [ai_message],
        "cart": cart
    }

async def confirmation_agent_node(state: AgentCafeState) -> AgentCafeState:
    """Handle order confirmation using standard LangChain agent"""
    user_input = state["messages"][-1].content
    
    # Use standard LangChain agent
    response = await confirmation_executor.ainvoke({"messages": [HumanMessage(content=user_input)]})
    ai_message = AIMessage(content=response["output"])
    
    return {
        **state,
        "messages": state["messages"] + [ai_message]
    }

# Routing function
def route_to_agent(state: AgentCafeState) -> str:
    """Route to appropriate agent based on intent"""
    intent = state["current_intent"]
    
    if intent == "menu":
        return "menu_agent"
    elif intent == "order":
        return "order_agent"
    elif intent == "confirmation":
        return "confirmation_agent"
    else:
        return "menu_agent"  # Default

# Create the LangGraph workflow
def create_agent_workflow():
    """Create and return the agent workflow"""
    
    # Create the state graph
    workflow = StateGraph(AgentCafeState)
    
    # Add nodes
    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("menu_agent", menu_agent_node)
    workflow.add_node("order_agent", order_agent_node)
    workflow.add_node("confirmation_agent", confirmation_agent_node)
    
    # Add edges
    workflow.add_edge(START, "coordinator")
    workflow.add_conditional_edges(
        "coordinator",
        route_to_agent,
        {
            "menu_agent": "menu_agent",
            "order_agent": "order_agent", 
            "confirmation_agent": "confirmation_agent"
        }
    )
    workflow.add_edge("menu_agent", END)
    workflow.add_edge("order_agent", END)
    workflow.add_edge("confirmation_agent", END)
    
    # Add memory for persistence
    memory = MemorySaver()
    
    # Compile the workflow
    return workflow.compile(checkpointer=memory)

# Create the workflow instance
agent_workflow = create_agent_workflow()
