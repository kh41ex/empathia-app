# test_rag.py
from src.core.psychology_rag import get_psychology_expert

# Test the expert system directly
test_input = "I'm feeling really sad about losing my dog"
print(f"Testing with: {test_input}")

try:
    response = get_psychology_expert().get_expert_response(test_input)
    print("SUCCESS! Expert response:")
    print(response)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()