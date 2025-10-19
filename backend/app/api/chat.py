from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from app.agents.modern_agent import ModernBaristaAgent
from app.agents.advanced_agent import AdvancedBaristaAgent
from app.agents.custom_workflow import CustomWorkflowAgent
from app.agents.deep_coordinator import DeepCoordinatorAgent
import json
import uuid

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    session_id: str = None
    agent_type: str = "modern"  # modern, advanced, workflow, deepagents
    model_provider: str = "bedrock"  # bedrock, gemini, mistral
    model_name: str = None  # Specific model ID (optional)
    user_context: dict = None

@router.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    session_id = chat_message.session_id or str(uuid.uuid4())
    
    # Create agents with selected model
    model_provider = chat_message.model_provider or "bedrock"
    model_name = chat_message.model_name
    
    # Route to different agents based on type
    if chat_message.agent_type == "deepagents":
        try:
            deep_agent = DeepCoordinatorAgent(
                model_provider=model_provider,
                model_name=model_name
            )
            response = await deep_agent.process_message(chat_message.message, session_id)
            cart = deep_agent.cart_storage.get(session_id, {})
            total = await _calculate_cart_total(cart)
            return {
                "response": str(response),
                "content_blocks": [{"type": "text", "text": str(response)}],
                "session_id": session_id,
                "agent_type": "deepagents",
                "model_info": {
                    "provider": model_provider,
                    "model": model_name or "default"
                },
                "structured_output": {
                    "agent_type": "deepagents",
                    "features_used": ["planning", "subagents", "tools"],
                    "cart_state": dict(cart),
                    "total": float(total)
                }
            }
        except Exception as e:
            return {
                "response": f"DeepAgent error: {str(e)}",
                "content_blocks": [{"type": "text", "text": f"DeepAgent error: {str(e)}"}],
                "session_id": session_id,
                "agent_type": "deepagents",
                "model_info": {
                    "provider": model_provider,
                    "model": model_name or "default"
                },
                "structured_output": {"error": str(e)}
            }
    elif chat_message.agent_type == "advanced":
        advanced_agent = AdvancedBaristaAgent(
            model_provider=model_provider,
            model_name=model_name
        )
        result = await advanced_agent.process_message(
            chat_message.message, 
            session_id, 
            chat_message.user_context
        )
        result["model_info"] = {
            "provider": model_provider,
            "model": model_name or "default"
        }
    elif chat_message.agent_type == "workflow":
        workflow_agent = CustomWorkflowAgent()
        result = await workflow_agent.process_message(chat_message.message, session_id)
        result["model_info"] = {
            "provider": "workflow",
            "model": "rule-based"
        }
    else:
        modern_agent = ModernBaristaAgent(
            model_provider=model_provider,
            model_name=model_name
        )
        result = await modern_agent.process_message(chat_message.message, session_id)
        result["model_info"] = {
            "provider": model_provider,
            "model": model_name or "default"
        }
    
    return {
        "response": result["response"],
        "content_blocks": result["content_blocks"],
        "session_id": session_id,
        "agent_type": chat_message.agent_type,
        "structured_output": result.get("structured_output"),
        "cart_state": result.get("cart_state", []),
        "total": result.get("total", 0.0),
        "intent": result.get("intent"),
        "confidence": result.get("confidence")
    }

async def _calculate_cart_total(cart: dict) -> float:
    """Helper to calculate cart total"""
    try:
        from app.models.menu import MenuItem
        total = 0
        for item_id, quantity in cart.items():
            item = await MenuItem.get(id=int(item_id))
            total += float(item.price) * quantity
        return total
    except:
        return 0.0

@router.get("/models")
async def get_available_models():
    """Get list of all available models"""
    from app.core.model_factory import get_available_models
    return {
        "models": get_available_models(),
        "default": {
            "provider": "bedrock",
            "model": "amazon.nova-lite-v1:0"
        }
    }

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message = message_data.get("message", "")
            agent_type = message_data.get("agent_type", "modern")
            model_provider = message_data.get("model_provider", "bedrock")
            model_name = message_data.get("model_name")
            user_context = message_data.get("user_context")
            
            # Route to appropriate agent with model selection
            if agent_type == "deepagents":
                deep_agent = DeepCoordinatorAgent(
                    model_provider=model_provider,
                    model_name=model_name
                )
                response = await deep_agent.process_message(message, session_id)
                cart = deep_agent.cart_storage.get(session_id, {})
                total = await _calculate_cart_total(cart)
                result = {
                    "response": response,
                    "content_blocks": [{"type": "text", "text": response}],
                    "model_info": {
                        "provider": model_provider,
                        "model": model_name or "default"
                    },
                    "structured_output": {
                        "agent_type": "deepagents",
                        "features_used": ["planning", "subagents", "tools"],
                        "cart_state": dict(cart),
                        "total": float(total)
                    }
                }
            elif agent_type == "advanced":
                advanced_agent = AdvancedBaristaAgent(
                    model_provider=model_provider,
                    model_name=model_name
                )
                result = await advanced_agent.process_message(message, session_id, user_context)
                result["model_info"] = {
                    "provider": model_provider,
                    "model": model_name or "default"
                }
            elif agent_type == "workflow":
                workflow_agent = CustomWorkflowAgent()
                result = await workflow_agent.process_message(message, session_id)
                result["model_info"] = {
                    "provider": "workflow",
                    "model": "rule-based"
                }
            else:
                modern_agent = ModernBaristaAgent(
                    model_provider=model_provider,
                    model_name=model_name
                )
                result = await modern_agent.process_message(message, session_id)
                result["model_info"] = {
                    "provider": model_provider,
                    "model": model_name or "default"
                }
            
            await websocket.send_text(json.dumps({
                "response": result["response"],
                "content_blocks": result["content_blocks"],
                "session_id": session_id,
                "agent_type": agent_type,
                "structured_output": result.get("structured_output"),
                "cart_state": result.get("cart_state", []),
                "total": result.get("total", 0.0),
                "intent": result.get("intent"),
                "confidence": result.get("confidence")
            }))
            
    except WebSocketDisconnect:
        pass
