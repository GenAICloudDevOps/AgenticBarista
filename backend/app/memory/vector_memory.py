from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta

class SimpleVectorMemory:
    """Simple vector-based memory for conversation history"""
    
    def __init__(self, max_tokens: int = 2000):
        self.conversations: Dict[str, List[Dict]] = {}
        self.max_tokens = max_tokens
        self.memory_key = "conversation_history"
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load conversation history for the session"""
        session_id = inputs.get("session_id", "default")
        history = self.get_relevant_history(session_id, inputs.get("user_message", ""))
        
        # Format history for prompt
        formatted_history = []
        for entry in history:
            formatted_history.append(f"User: {entry['user']}")
            formatted_history.append(f"Assistant: {entry['assistant']}")
        
        return {
            self.memory_key: "\n".join(formatted_history[-10:])  # Last 5 exchanges
        }
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save the conversation context"""
        session_id = inputs.get("session_id", "default")
        user_message = inputs.get("user_message", "")
        assistant_response = outputs.get("response", "")
        
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        # Add new conversation entry
        entry = {
            "user": user_message,
            "assistant": assistant_response,
            "timestamp": datetime.now().isoformat(),
            "tokens": len(user_message.split()) + len(assistant_response.split())
        }
        
        self.conversations[session_id].append(entry)
        
        # Trim old conversations if too long
        self._trim_memory(session_id)
    
    def clear(self) -> None:
        """Clear all memory"""
        self.conversations.clear()
    
    def get_relevant_history(self, session_id: str, current_message: str) -> List[Dict]:
        """Get relevant conversation history using simple similarity"""
        if session_id not in self.conversations:
            return []
        
        history = self.conversations[session_id]
        
        # Simple relevance: recent conversations + keyword matching
        relevant = []
        current_words = set(current_message.lower().split())
        
        for entry in history[-10:]:  # Last 10 entries
            # Always include recent entries
            if len(relevant) < 5:
                relevant.append(entry)
            else:
                # Check for keyword overlap
                entry_words = set((entry['user'] + ' ' + entry['assistant']).lower().split())
                overlap = len(current_words.intersection(entry_words))
                
                if overlap > 1:  # At least 2 word overlap
                    relevant.append(entry)
        
        return relevant[-8:]  # Return last 8 relevant entries
    
    def _trim_memory(self, session_id: str) -> None:
        """Trim memory to stay within token limits"""
        if session_id not in self.conversations:
            return
        
        conversations = self.conversations[session_id]
        total_tokens = sum(entry['tokens'] for entry in conversations)
        
        # Remove oldest entries if over limit
        while total_tokens > self.max_tokens and len(conversations) > 5:
            removed = conversations.pop(0)
            total_tokens -= removed['tokens']
    
    def clear_session(self, session_id: str) -> None:
        """Clear memory for a specific session"""
        if session_id in self.conversations:
            del self.conversations[session_id]
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary statistics for a session"""
        if session_id not in self.conversations:
            return {"total_messages": 0, "total_tokens": 0}
        
        conversations = self.conversations[session_id]
        return {
            "total_messages": len(conversations),
            "total_tokens": sum(entry['tokens'] for entry in conversations),
            "first_message": conversations[0]['timestamp'] if conversations else None,
            "last_message": conversations[-1]['timestamp'] if conversations else None
        }

# Global memory instance
vector_memory = SimpleVectorMemory()
