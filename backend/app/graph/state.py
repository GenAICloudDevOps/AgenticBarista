from typing import Dict, List, Any, Optional
from typing_extensions import TypedDict
from langgraph.graph import MessagesState

class CafeState(MessagesState):
    """State for the cafe chatbot"""
    session_id: str
    cart: Dict[int, int]  # item_id -> quantity
    current_agent: str
    user_intent: str
    menu_context: List[Dict[str, Any]]
    conversation_history: List[Dict[str, str]]
    total_amount: float
