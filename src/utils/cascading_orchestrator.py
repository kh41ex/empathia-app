# src/utils/cascading_orchestrator.py
import threading
import queue
import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from src.core.psychology_rag import PsychologyBookExpert, get_psychology_expert
from src.core.peer_support_llm import peer_support_model
from src.core.followup_llm import follow_up_model
from src.utils.triggers import calculate_advice_priority
from src.utils.conversation_memory import conversation_memory

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Thread-safe queues
peer_queue = queue.Queue()
expert_queue = queue.Queue()
followup_queue = queue.Queue()

def generate_peer_response_async(user_input: str, session_id: str, debug: bool = False):
    """Generate peer support in background thread."""
    try:
        response = peer_support_model.generate_response(user_input, session_id)
        peer_queue.put(("success", response))
        if debug:
            print(f"DEBUG: Peer response ready")
    except Exception as e:
        peer_queue.put(("error", f"Peer support error: {e}"))

def generate_expert_response_async(user_input: str, session_id: str, debug: bool = False):
    """Generate expert advice in background thread."""
    try:
        psychology_expert = get_psychology_expert()
        response = psychology_expert.get_expert_response(user_input, session_id)
        expert_queue.put(("success", response))
        if debug:
            print(f"DEBUG: Expert response ready")
    except Exception as e:
        expert_queue.put(("error", f"Expert error: {e}"))

def generate_followup_question_async(user_input: str, peer_response: str, expert_response: str, session_id: str, debug: bool = False):
    """Generate follow-up question in background thread."""
    try:

        # Get conversation history for context-aware follow-up questions
        history = conversation_memory.get_formatted_history(session_id)

        response = follow_up_model.generate_follow_up_question(
            user_input=user_input, 
            peer_response=peer_response, 
            expert_response=expert_response,
            conversation_history=history  # Pass history to follow-up model
        )

        question = response.strip().replace('"', '').replace('?', '') + '?'
        followup_queue.put(("success", question))
        if debug:
            print(f"DEBUG: Follow-up question ready: {question}")
            
    except Exception as e:
        followup_queue.put(("error", "What's coming up for you as you share this?"))



# Main orchestrator function

def orchestrate_cascading_response(user_input: str, session_id: str = "default", debug: bool = False) -> dict:
    """
    Orchestrates the cascading async response generation.
    Returns: {'peer': response, 'expert': response, 'followup': question}
    """
    results = {'peer': None, 'expert': None, 'followup': None}
    
    # 1. Start peer support immediately
    peer_thread = threading.Thread(
        target=generate_peer_response_async, 
        args=(user_input, session_id, debug),
        daemon=True
    )
    peer_thread.start()
    
    # 2. Check if expert is needed and start it
    advice_priority = calculate_advice_priority(user_input, "")
    needs_expert = advice_priority > 0.2
    
    if needs_expert:
        expert_thread = threading.Thread(
            target=generate_expert_response_async,
            args=(user_input, session_id, debug),
            daemon=True
        )
        expert_thread.start()
    
    # 3. Wait for peer response (blocks until ready)
    peer_status, peer_response = peer_queue.get()
    results['peer'] = peer_response if peer_status == "success" else "I'm here to listen to you."
    

    # 4. Wait for expert response if needed BEFORE starting follow-up
    expert_response = ""
    if needs_expert:
        try:
            # Give expert more time to complete
            expert_status, expert_response = expert_queue.get(timeout=2.0)
            if expert_status == "success":
                results['expert'] = expert_response
                if debug:
                    print("DEBUG: Expert response received")
            else:
                results['expert'] = None
        except queue.Empty:
            # Expert timed out, proceed without it
            results['expert'] = None
            if debug:
                print("DEBUG: Expert response timed out")


    # 5. Start follow-up question generation with actual expert response (if available)
    followup_thread = threading.Thread(
        target=generate_followup_question_async,
        args=(user_input, results['peer'], results['expert'] or "", session_id, debug),  # Include expert response
        daemon=True
    )
    followup_thread.start()
    
    
    # 6. Wait for follow-up question (blocks until ready)
    followup_status, followup_question = followup_queue.get()
    results['followup'] = followup_question if followup_status == "success" else "How are you feeling now?"
    
    
    return results