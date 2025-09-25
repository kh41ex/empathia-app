# followup_llm.py
import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # Add this at the top

class FollowUpModel:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def generate_follow_up_question(self, user_input: str, peer_response: str, expert_response: str, conversation_history: str = "") -> str:
        prompt = f"""
        Create ONE gentle, open-ended follow-up question based on this conversation.

        USER: {user_input}
        PEER SUPPORT: {peer_response}
        {f"EXPERT ADVICE: {expert_response}" if expert_response else ""}
        {f"CONVERSATION HISTORY: {conversation_history}" if conversation_history else ""}

        Guidelines:
        - Directly relate to user's specific situation
        - Show deep listening and understanding
        - Help explore feelings more deeply
        - Open-ended (no yes/no answers)
        - Gentle, curious, supportive tone
        - Max 12 words
        - Natural conversation flow

        Critical rules:
        - Do NOT repeat the user's words
        - Do NOT ask about the pet's death or details
        - Do NOT ask questions about how user will apply expert advice

        Question:
        """

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=30,
            temperature=0.8,
            timeout=10
        )

        return response.choices[0].message.content.strip().replace('"', '').replace('?', '') + '?'
    

# Global instance
# follow_up_model = FollowUpModel()


def get_follow_up_model():
    """Get the follow-up model instance"""
    try:
        if 'follow_up_model' not in st.session_state:
            st.session_state.follow_up_model = FollowUpModel()
        return st.session_state.follow_up_model
    except (AttributeError, RuntimeError):
        # Fallback for threads: use module-level cache
        if not hasattr(get_follow_up_model, "_instance"):
            get_follow_up_model._instance = FollowUpModel()
        return get_follow_up_model._instance