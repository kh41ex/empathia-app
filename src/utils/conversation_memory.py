# src/utils/conversation_memory.py
from typing import List, Dict
import json
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

class ConversationMemory:
    def __init__(self, max_history_length=6):
        self.max_history_length = max_history_length
        self.memory_file = os.path.join(PROJECT_ROOT, "data", "outputs", "conversation_memory.json")
        self.conversations = self._load_memory()
    
    def _load_memory(self):
        """Load conversation memory from file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_memory(self):
        """Save conversation memory to file"""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        with open(self.memory_file, 'w') as f:
            json.dump(self.conversations, f, indent=2)
    
    def add_message(self, session_id: str, role: str, message: str):
        """Add a message to conversation history"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append({
            "role": role,
            "message": message
        })
        
        # Keep only the most recent messages
        if len(self.conversations[session_id]) > self.max_history_length:
            self.conversations[session_id] = self.conversations[session_id][-self.max_history_length:]
        
        self._save_memory()
    
    def get_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for a session"""
        return self.conversations.get(session_id, [])
    
    def get_formatted_history(self, session_id: str) -> str:
        """Get conversation history as formatted text"""
        history = self.get_history(session_id)
        if not history:
            return "No previous conversation."
        
        formatted = []
        for i, msg in enumerate(history):
            speaker = "User" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{speaker}: {msg['message']}")
        
        return "\n".join(formatted[-4:])  # Last 4 messages
    
    def clear_history(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]
            self._save_memory()

# Global memory instance
conversation_memory = ConversationMemory()