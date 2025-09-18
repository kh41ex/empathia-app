# expert.py - Enhanced version
import time
import threading
import traceback
import queue
import streamlit as st
from src.core.psychology_rag import psychology_expert

# Thread-safe queue for async responses
expert_response_queue = queue.Queue()

def fetch_expert_async(user_input: str, debug: bool = False):
    """Background worker for fetching expert advice."""
    try:
        if debug:
            print(f"DEBUG [expert.py]: Starting expert fetch for: {user_input}")
        
        expert_response = psychology_expert.get_expert_response(user_input)
        
        if debug:
            print(f"DEBUG [expert.py]: Expert fetch successful: {expert_response[:100]}...")
        
        expert_response_queue.put(("success", expert_response))
        if debug:
            print("DEBUG [expert.py]: Result placed in queue")
        
    except Exception as e:
        error_msg = f"Expert system error: {str(e)}"
        if debug:
            print(f"DEBUG [expert.py]: Expert fetch failed: {error_msg}")
            traceback.print_exc()
        expert_response_queue.put(("error", error_msg))

def start_expert_thread(user_input: str):
    """Kick off expert fetch in a background thread."""
    st.session_state.expert_loading = True
    st.session_state.expert_start_time = time.time()
    st.session_state.last_expert_trigger = user_input  # ✅ Store what triggered this
    
    if st.session_state.get('DEBUG_MODE', False):
        print(f"DEBUG [expert.py]: Starting expert thread for: {user_input}, loading={st.session_state.expert_loading}")
    
    threading.Thread(
        target=fetch_expert_async,
        args=(user_input, st.session_state.get('DEBUG_MODE', False)),
        daemon=True
    ).start()

def check_expert_timeout(timeout: int = 25):
    """Check if expert request exceeded timeout."""
    if time.time() - st.session_state.expert_start_time > timeout:
        if st.session_state.get('DEBUG_MODE', False):
            print("DEBUG [expert.py]: Expert request timed out")
        expert_response_queue.put(("error", "Expert guidance request timed out. Please try again."))
        st.session_state.expert_loading = False

def handle_expert_queue(debug: bool = False):
    """Process results from background thread (if any)."""
    if not expert_response_queue.empty():
        status, result = expert_response_queue.get()
        if status == "success":
            st.session_state.prefetched_expert_response = result
            if debug:
                print(f"DEBUG [expert.py]: Expert response stored: {result[:100]}...")
        else:
            st.session_state.prefetched_expert_response = result
            if debug:
                print(f"DEBUG [expert.py]: Expert fetch error: {result}")
        
        st.session_state.expert_loading = False
        if debug:
            print(f"DEBUG [expert.py]: Set expert_loading to {st.session_state.expert_loading}")
        return True  # Indicate that state changed
    
    return False

def fetch_expert_sync(user_input: str) -> str:
    """Synchronous expert fetch (fallback)."""
    return psychology_expert.get_expert_response(user_input)

def get_cached_expert_response() -> str:
    """Get pre-fetched expert response if available"""
    if (hasattr(st.session_state, 'prefetched_expert_response') and 
        st.session_state.prefetched_expert_response and
        not st.session_state.prefetched_expert_response.lower().startswith("error")):
        return st.session_state.prefetched_expert_response
    return None

def inject_expert_advice_if_available() -> bool:
    """Inject expert advice into conversation if ready and relevant"""
    # Define add_message if not already imported
    def add_message(speaker, message):
        if not hasattr(st.session_state, "conversation_history"):
            st.session_state.conversation_history = []
        st.session_state.conversation_history.append((speaker, message))

    expert_response = get_cached_expert_response()
    if expert_response and st.session_state.conversation_history:
        last_user_msg = None
        for speaker, msg in reversed(st.session_state.conversation_history):
            if speaker == "user":
                last_user_msg = msg
                break
        
        if last_user_msg and calculate_relevance(last_user_msg, expert_response) > 0.4:
            add_message("assistant", f"**🧠 Research-based insight:** {expert_response}")
            st.session_state.prefetched_expert_response = None
            return True
    return False

def calculate_relevance(user_input: str, expert_response: str) -> float:
    """Calculate how relevant expert advice is to current conversation"""
    # Simple implementation - could use embeddings for better relevance
    user_words = set(user_input.lower().split())
    expert_words = set(expert_response.lower().split())
    
    if not user_words:
        return 0.0
        
    intersection = user_words.intersection(expert_words)
    return len(intersection) / len(user_words)