from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from app.graph.agent_workflow import agent_workflow, AgentCafeState
from app.memory.vector_memory import vector_memory
from app.tools.langchain_tools import AVAILABLE_TOOLS

class CoordinatorAgent:
    def __init__(self):
        self.workflow = agent_workflow
        self.memory = vector_memory
        self.tools = AVAILABLE_TOOLS
        # Shared cart storage
        self.cart_storage = {}
    
    async def process_message(self, message: str, session_id: str = "default") -> str:
        """Process message using LangChain agents with LangGraph workflow"""
        try:
            # Initialize state
            state = AgentCafeState({
                "session_id": session_id,
                "messages": [HumanMessage(content=message)],
                "cart": self.cart_storage.get(session_id, {}),
                "current_intent": "",
                "menu_context": [],
                "total_amount": 0.0
            })
            
            # Configuration for checkpointer with thread_id
            config = {"configurable": {"thread_id": session_id}}
            
            # Run the agent workflow with proper config
            result = await self.workflow.ainvoke(state, config=config)
            
            # Update cart storage
            if session_id not in self.cart_storage:
                self.cart_storage[session_id] = {}
            self.cart_storage[session_id].update(result.get("cart", {}))
            
            # Get AI response
            if result["messages"] and len(result["messages"]) > 1:
                ai_response = result["messages"][-1].content
            else:
                ai_response = "I'm here to help! Ask me about our menu or place an order."
            
            # Save to vector memory
            self.memory.save_context(
                inputs={"session_id": session_id, "user_message": message},
                outputs={"response": ai_response}
            )
            
            return ai_response
                
        except Exception as e:
            error_response = f"I'm having some technical difficulties with the LangChain agents. Please try again. Error: {str(e)}"
            
            # Still save to memory
            self.memory.save_context(
                inputs={"session_id": session_id, "user_message": message},
                outputs={"response": error_response}
            )
            
            return error_response
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get session statistics from vector memory"""
        return self.memory.get_session_summary(session_id)
    
    def clear_session(self, session_id: str) -> None:
        """Clear session data"""
        self.memory.clear_session(session_id)
        if session_id in self.cart_storage:
            del self.cart_storage[session_id]
