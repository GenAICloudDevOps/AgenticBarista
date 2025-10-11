from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from app.agents.coordinator import CoordinatorAgent
import json
import uuid

router = APIRouter()
coordinator = CoordinatorAgent()

class ChatMessage(BaseModel):
    message: str
    session_id: str = None

@router.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    session_id = chat_message.session_id or str(uuid.uuid4())
    response = await coordinator.process_message(chat_message.message, session_id)
    
    return {
        "response": response,
        "session_id": session_id
    }

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message = message_data.get("message", "")
            
            response = await coordinator.process_message(message, session_id)
            
            await websocket.send_text(json.dumps({
                "response": response,
                "session_id": session_id
            }))
            
    except WebSocketDisconnect:
        pass
