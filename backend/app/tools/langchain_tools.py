from typing import List, Dict, Any, Optional
from app.models.menu import MenuItem
import json

async def get_menu_items(category: Optional[str] = None) -> str:
    """Get menu items, optionally filtered by category (coffee, pastry, food).
    
    Args:
        category: Optional category to filter by
        
    Returns:
        JSON string of menu items
    """
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
        
        return json.dumps(menu_list, indent=2)
    except Exception as e:
        return f"Error getting menu: {str(e)}"

def add_item_to_cart(session_id: str, item_id: int, quantity: int = 1) -> str:
    """Add an item to the user's cart.
    
    Args:
        session_id: User session identifier
        item_id: ID of the menu item to add
        quantity: Number of items to add (default 1)
        
    Returns:
        Success message
    """
    return f"Tool called: add_item_to_cart(session_id={session_id}, item_id={item_id}, quantity={quantity})"

def remove_item_from_cart(session_id: str, item_id: int) -> str:
    """Remove an item from the user's cart.
    
    Args:
        session_id: User session identifier
        item_id: ID of the menu item to remove
        
    Returns:
        Success message
    """
    return f"Tool called: remove_item_from_cart(session_id={session_id}, item_id={item_id})"

def get_cart_total(session_id: str) -> str:
    """Calculate the total amount for items in the user's cart.
    
    Args:
        session_id: User session identifier
        
    Returns:
        Cart total information
    """
    return f"Tool called: get_cart_total(session_id={session_id})"

def search_menu_items(query: str) -> str:
    """Search menu items by name or description.
    
    Args:
        query: Search term to look for in item names and descriptions
        
    Returns:
        JSON string of matching items
    """
    return f"Tool called: search_menu_items(query={query})"

async def get_item_recommendations(preferences: str) -> str:
    """Get item recommendations based on user preferences.
    
    Args:
        preferences: User preferences (e.g., "sweet", "strong", "cold")
        
    Returns:
        JSON string of recommended items
    """
    try:
        # Simple recommendation logic
        items = await MenuItem.filter(available=True)
        recommendations = []
        
        preferences_lower = preferences.lower()
        
        for item in items:
            score = 0
            item_text = f"{item.name} {item.description}".lower()
            
            # Simple scoring based on keywords
            if "sweet" in preferences_lower and any(word in item_text for word in ["chocolate", "mocha", "sweet", "vanilla"]):
                score += 2
            if "strong" in preferences_lower and any(word in item_text for word in ["espresso", "bold", "strong"]):
                score += 2
            if "cold" in preferences_lower and any(word in item_text for word in ["iced", "cold", "frappuccino"]):
                score += 2
            if "hot" in preferences_lower and any(word in item_text for word in ["hot", "steamed", "warm"]):
                score += 1
                
            if score > 0:
                recommendations.append({
                    "id": item.id,
                    "name": item.name,
                    "price": float(item.price),
                    "description": item.description,
                    "score": score
                })
        
        # Sort by score
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return json.dumps(recommendations[:3], indent=2)  # Top 3 recommendations
    except Exception as e:
        return f"Error getting recommendations: {str(e)}"

# List of all available tools (as simple functions)
AVAILABLE_TOOLS = [
    get_menu_items,
    add_item_to_cart,
    remove_item_from_cart,
    get_cart_total,
    search_menu_items,
    get_item_recommendations
]
