# test_fine_tuned_model.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.core.peer_support_llm import generate_peer_response

test_inputs = [
    "I had to put my dog down yesterday and I can't stop crying",
    "I feel so guilty about what happened to my cat",
    "It's been a month but the pain is still fresh",
    "Nobody understands how much my bird meant to me"
]

for user_input in test_inputs:
    response = generate_peer_response(user_input)
    print(f"🧑: {user_input}")
    print(f"🤖: {response}")
    print("---")