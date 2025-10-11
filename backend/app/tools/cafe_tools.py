from langchain_core.tools import tool
from typing import List, Dict, Any
from app.models.menu import MenuItem
import json

@tool
def get_menu_items(category: str = None) -> str:
    """Get menu items, optionally filtered by category (coffee, pastry, food)"""
    try:
        query = MenuItem.all()
        if category:
            query = query.filter(category__icontains=category)
        items = await query.filter(available=True)
        
        menu_list = []
        for item in items:
            menu_list.append({
                "id": item.id,
                "name": item.name,
                "price": float(item.price),
                "description": item.description,
                "category": item.category
            })
        
        return json.dumps(menu_list)
    except Exception as e:
        return f"Error getting menu: {str(e)}"

@tool
def add_to_cart(session_id: str, item_name: str, quantity: int = 1) -> str:
    """Add an item to the user's cart"""
    try:
        # This will be handled by the state management
        return f"Added {quantity}x {item_name} to cart for session {session_id}"
    except Exception as e:
        return f"Error adding to cart: {str(e)}"

@tool
def get_cart_contents(session_id: str) -> str:
    """Get the current contents of the user's cart"""
    try:
        # This will be handled by the state management
        return f"Cart contents for session {session_id}"
    except Exception as e:
        return f"Error getting cart: {str(e)}"

@tool
def remove_from_cart(session_id: str, item_name: str) -> str:
    """Remove an item from the user's cart"""
    try:
        # This will be handled by the state management
        return f"Removed {item_name} from cart for session {session_id}"
    except Exception as e:
        return f"Error removing from cart: {str(e)}"

@tool
def confirm_order(session_id: str) -> str:
    """Confirm and place the user's order"""
    try:
        # This will be handled by the confirmation agent
        return f"Order confirmed for session {session_id}"
    except Exception as e:
        return f"Error confirming order: {str(e)}"
