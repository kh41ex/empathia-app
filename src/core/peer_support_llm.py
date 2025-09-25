# reddit_peer_llm.py
from turtle import st
from openai import OpenAI
from src.utils.conversation_memory import conversation_memory
import os
from dotenv import load_dotenv

load_dotenv()  # Add this at the top

class PeerSupportModel:
    def __init__(self, model_id="ft:gpt-3.5-turbo-0125:personal:empathia-peer:CBmcBHZ7"):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model_id = model_id

    def generate_response(self, user_input: str, session_id: str = "default") -> str:
        """Generates a peer response using the fine-tuned model."""
        
        # Get conversation history
        history = conversation_memory.get_formatted_history(session_id)

        # Update the prompt to include history
        prompt = f"""You are a compassionate grief counselor.

            CONVERSATION HISTORY:
            {history}

            CURRENT USER MESSAGE:
            {user_input}

            Respond with warmth, validation, and understanding. Keep your response under 50 words. Focus on emotional support rather than advice."""

        
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=60,
                timeout=10
            )

            response_text = response.choices[0].message.content.strip()
        
            # Add to conversation memory
            conversation_memory.add_message(session_id, "user", user_input)
            conversation_memory.add_message(session_id, "assistant", response_text)
        
            return response_text

        except Exception as e:
            print(f"Error generating peer response: {e}")
            return "I'm so sorry you're going through this. I'm here to listen..."

# Global instance
# peer_support_model = PeerSupportModel()


def get_peer_support_model():
    """Get the peer support model instance (Streamlit-safe)"""
    try:
        if 'peer_support_model' not in st.session_state:
            st.session_state.peer_support_model = PeerSupportModel()
        return st.session_state.peer_support_model
    except (AttributeError, RuntimeError):
        # Fallback for threads: use module-level cache
        if not hasattr(get_peer_support_model, "_instance"):
            get_peer_support_model._instance = PeerSupportModel()
        return get_peer_support_model._instance