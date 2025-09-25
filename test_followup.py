#test_followup.py
from src.core.followup_llm import get_follow_up_model

# Test the follow-up model directly
test_input = "I'm feeling really sad about losing my dog"
peer_response = "I'm so sorry you're going through this. Losing a pet is incredibly painful."
expert_response = "Research shows that creating rituals can help with pet loss grief."

print(f"Testing with user input: {test_input}")
print(f"Peer response: {peer_response}")
print(f"Expert response: {expert_response}")

try:
    model = get_follow_up_model()  # Get the instance using the function
    response = model.generate_follow_up_question(test_input, peer_response, expert_response)
    print("SUCCESS! Follow-up question:")
    print(response)
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()