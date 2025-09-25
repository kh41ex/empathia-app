# test_peer_simple.py
from src.core.peer_support_llm import PeerSupportModel

# Test the peer support model directly (bypassing the getter function)
test_input = "I'm feeling really sad about losing my dog"
print(f"Testing with: {test_input}")

try:
    model = PeerSupportModel()  # Create instance directly
    response = model.generate_response(test_input)
    print("SUCCESS! Peer response:")
    print(response)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()