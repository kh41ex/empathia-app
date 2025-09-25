# test_peer.py
from src.core.peer_support_llm import get_peer_support_model

# Test the peer support model directly
test_input = "I'm feeling really sad about losing my dog"
print(f"Testing with: {test_input}")

try:
    model = get_peer_support_model()  # Get the instance using the function
    response = model.generate_response(test_input)
    print("SUCCESS! Peer response:")
    print(response)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()