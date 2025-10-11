from typing import List, Dict
from app.core.bedrock import get_haiku_response
from app.models.menu import MenuItem

class MenuAgent:
    def __init__(self):
        pass
        
    async def process(self, message: str, context: Dict) -> str:
        try:
            # Get menu items for context
            items = await self._get_menu_items()
            menu_context = "\n".join([f"- {item['name']}: ${item['price']:.2f} - {item['description']}" for item in items])
            
            # Use AI for natural language processing
            prompt = f"""You are a helpful barista assistant. Here's our menu:

{menu_context}

Customer message: "{message}"

Respond naturally and helpfully about our menu items. If they ask about the menu, show items with prices. If they ask about specific categories like coffee or pastries, filter accordingly. Be friendly and conversational."""

            # Try AI first, fallback to rules
            try:
                ai_response = get_haiku_response(prompt)
                if "error" not in ai_response.lower():
                    return ai_response
            except:
                pass
            
            # Fallback to rule-based logic
            if "menu" in message.lower():
                response = "Here's our menu:\n\n"
                for item in items:
                    response += f"• {item['name']} - ${item['price']:.2f}\n  {item['description']}\n\n"
                return response
            
            elif any(word in message.lower() for word in ["coffee", "latte", "espresso", "cappuccino"]):
                coffee_items = await self._get_menu_items("coffee")
                response = "Our coffee selection:\n\n"
                for item in coffee_items:
                    response += f"• {item['name']} - ${item['price']:.2f}\n  {item['description']}\n\n"
                return response
            
            return "I can help you explore our menu! Ask me about our coffee, pastries, or say 'show menu' to see everything."
                
        except Exception as e:
            return "I'm having trouble accessing the menu right now. Please try again."
    
    async def _get_menu_items(self, category: str = None) -> List[Dict]:
        query = MenuItem.all()
        if category:
            query = query.filter(category__icontains=category)
        items = await query.filter(available=True)
        return [{"id": item.id, "name": item.name, "description": item.description, 
                 "price": float(item.price), "category": item.category} for item in items]
