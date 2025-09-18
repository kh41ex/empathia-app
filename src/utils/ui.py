# ui.py
import streamlit as st
import time
from .state import clear_state

def show_conversation():
    """Display chat history."""
    for speaker, message in st.session_state.conversation_history:
        if speaker == "user":
            st.chat_message("user").write(message)
        else:
            st.chat_message("assistant").write(message)

def add_message(speaker: str, message: str):
    """Append a message and render it."""
    st.session_state.conversation_history.append((speaker, message))
    st.chat_message(speaker).write(message)

def show_debug_panel():
    """Debug sidebar for developers."""
    with st.sidebar:
        st.header("🔧 Debug Panel")
        if st.button("Clear Conversation"):
            clear_state()
            st.rerun()
        # Avoid dumping full conversation
        st.write("Session state:", {k: v for k, v in st.session_state.items() if k != "conversation_history"})
        if st.session_state.expert_loading:
            st.write(f"Expert loading for: {int(time.time() - st.session_state.expert_start_time)} seconds")


# --- Stream message function ---
def stream_message(message: str, speed: float = 0.01):
    """Stream message with paragraph awareness"""
    message_placeholder = st.empty()
    full_response = ""
    
    # Split into paragraphs
    paragraphs = message.split('\n\n')
    
    for i, paragraph in enumerate(paragraphs):
        if paragraph.strip():  # Skip empty paragraphs
            # Stream the current paragraph
            current_para = ""
            for char in paragraph:
                current_para += char
                full_response += char
                # Display with all paragraphs so far
                display_text = "\n\n".join(paragraphs[:i]) + "\n\n" + current_para if i > 0 else current_para
                message_placeholder.markdown(display_text + "▌")
                time.sleep(speed)
            
            # Add paragraph break
            if i < len(paragraphs) - 1:
                full_response += "\n\n"
                message_placeholder.markdown(full_response + "▌")
    
    # Final display without cursor
    message_placeholder.markdown(full_response)

    return full_response



