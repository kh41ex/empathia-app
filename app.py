# app.py - COMPLETE WITH SIMULTANEOUS PROCESSING
import streamlit as st
import uuid
import base64
from pathlib import Path
from dotenv import load_dotenv

# Core logic imports
from src.core.psychology_rag import psychology_expert
from src.core.peer_support_llm import peer_support_model

# Utils
from src.utils.state import init_session_state
from src.utils.expert import check_expert_timeout
from src.utils.ui import show_conversation, add_message, show_debug_panel, stream_message
from src.utils.cascading_orchestrator import orchestrate_cascading_response
from src.utils.conversation_memory import conversation_memory
from src.utils.voice_input import voice_interface



# --- Set background image ---
def set_local_background():
    # Get the path to your image
    image_path = Path("static/prints.png")
    
    # Check if file exists
    if not image_path.exists():
        st.error("Background image not found!")
        return
    
    # Read and encode the image
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* Make content readable */
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.92);
            border-radius: 15px;
            padding: 2rem;
            margin-top: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
            backdrop-filter: blur(5px);
        }}
        
        /* Style the title */
        .stTitle {{
            color: white;
            text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.8);
            font-weight: bold;
        }}
        
        /* Style chat messages */
        .stChatMessage {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-radius: 15px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #4CAF50;
        }}
        
        /* Style input area */
        .stChatInput {{
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 10px;
            padding: 1rem;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )







load_dotenv()
DEBUG_MODE = False

# --- Initialize app ---
init_session_state()

# Unique session ID for conversation memory
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'messages' not in st.session_state:
    st.session_state.messages = []

# --- Configure the page ---

set_local_background()

st.set_page_config(page_title="EMPATHIA - Pet Loss Support", page_icon="🐾")
st.title("🐾 EMPATHIA")
st.markdown("Welcome. This is a safe space to express your feelings about the loss of your beloved pet.")

# --- Debug sidebar ---
if DEBUG_MODE:
    show_debug_panel()

# --- Background task handling ---
if st.session_state.expert_loading:
    check_expert_timeout(25)


# --- Conversation history display ---
show_conversation()

# --- User input ---
user_input = st.chat_input("How are you feeling today?")

# --- Process user input ---
# Only process if new input
if user_input and user_input != st.session_state.last_input:
    add_message("user", user_input)
    st.session_state.last_input = user_input

    # Add to conversation memory
    conversation_memory.add_message(st.session_state.session_id, "user", user_input)
    
    try:
        if DEBUG_MODE:
            print(f"DEBUG: Starting cascading response for: {user_input}")
        
        # 🎯 SINGLE CALL THAT MANAGES EVERYTHING
        results = orchestrate_cascading_response(user_input, session_id=st.session_state.session_id, debug=DEBUG_MODE)
        
        # Build the complete response
        complete_response = results['peer']
        
        if results['expert']:
            complete_response += f"\n\n🧠 {results['expert']}"
        
        complete_response += f"\n\n{results['followup']}"
        
        # Display everything in one smooth stream
        with st.chat_message("assistant"):
            stream_message(complete_response, speed=0.01)
        
        st.session_state.conversation_history.append(("assistant", complete_response))
        conversation_memory.add_message(st.session_state.session_id, "assistant", complete_response)
        
    except Exception as e:
        error_msg = f"I'm having trouble connecting right now. Please try again."
        add_message("assistant", error_msg)
        if DEBUG_MODE:
            print(f"DEBUG: Cascading response failed: {e}")
    
    # Rerun to refresh UI
    st.rerun()


# --- TTS for last assistant response ---
if st.session_state.conversation_history and st.session_state.conversation_history[-1][0] == "assistant":
    last_response = st.session_state.conversation_history[-1][1]
    if st.button("🔊 Read last response aloud"):
        audio_bytes = voice_interface.text_to_speech(last_response)
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)