# state.py
import streamlit as st

def init_session_state():
    """Initialize session state variables if not already set."""
    defaults = {
        "conversation_history": [],
        "last_input": "",
        "prefetched_expert_response": None,
        "expert_loading": False,
        "expert_start_time": 0,
        "processing": False,
        "DEBUG_MODE": True,
        "last_expert_trigger": "",  # ✅ NEW: Track what triggered expert advice
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def clear_state():
    """Reset session state (used in debug panel)."""
    st.session_state.conversation_history = []
    st.session_state.show_expert_advice = False
    st.session_state.prefetched_expert_response = None
    st.session_state.expert_loading = False