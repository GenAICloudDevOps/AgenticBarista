from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from app.graph.state import CafeState
from app.graph.nodes import menu_node, order_node, confirmation_node, router_node

def create_cafe_workflow():
    """Create the LangGraph workflow for the cafe chatbot"""
    
    # Create the state graph
    workflow = StateGraph(CafeState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("menu", menu_node)
    workflow.add_node("order", order_node)
    workflow.add_node("confirmation", confirmation_node)
    
    # Set entry point
    workflow.set_entry_point("router")
    
    # Add conditional edges from router
    workflow.add_conditional_edges(
        "router",
        lambda state: state.get("current_agent", "menu"),
        {
            "menu": "menu",
            "order": "order", 
            "confirmation": "confirmation"
        }
    )
    
    # All nodes end the conversation
    workflow.add_edge("menu", END)
    workflow.add_edge("order", END)
    workflow.add_edge("confirmation", END)
    
    return workflow.compile()

# Create the compiled workflow
cafe_workflow = create_cafe_workflow()
