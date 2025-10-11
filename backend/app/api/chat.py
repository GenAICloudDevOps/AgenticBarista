from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from app.agents.modern_agent import ModernBaristaAgent
from app.agents.advanced_agent import AdvancedBaristaAgent
from app.agents.custom_workflow import CustomWorkflowAgent
import json
import uuid

router = APIRouter()
modern_agent = ModernBaristaAgent()
advanced_agent = AdvancedBaristaAgent()
workflow_agent = CustomWorkflowAgent()

class ChatMessage(BaseModel):
    message: str
    session_id: str = None
    agent_type: str = "modern"  # modern, advanced, workflow
    user_context: dict = None

@router.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    session_id = chat_message.session_id or str(uuid.uuid4())
    
    # Route to different agents based on type
    if chat_message.agent_type == "advanced":
        result = await advanced_agent.process_message(
            chat_message.message, 
            session_id, 
            chat_message.user_context
        )
    elif chat_message.agent_type == "workflow":
        result = await workflow_agent.process_message(chat_message.message, session_id)
    else:
        result = await modern_agent.process_message(chat_message.message, session_id)
    
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

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message = message_data.get("message", "")
            agent_type = message_data.get("agent_type", "modern")
            user_context = message_data.get("user_context")
            
            # Route to appropriate agent
            if agent_type == "advanced":
                result = await advanced_agent.process_message(message, session_id, user_context)
            elif agent_type == "workflow":
                result = await workflow_agent.process_message(message, session_id)
            else:
                result = await modern_agent.process_message(message, session_id)
            
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
