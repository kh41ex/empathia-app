# create_enriched_dataset.py
import pandas as pd
import json
from openai import OpenAI
import os
from dotenv import load_dotenv
import time

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def synthesize_responses_for_post(post_text, list_of_responses):
    """
    Uses an LLM to combine multiple peer responses into one ideal, comprehensive response.
    """
    responses_text = "\n\n".join([f"Response {i+1}: {r}" for i, r in enumerate(list_of_responses)])

    prompt = f"""
### TASK:
You are an expert at synthesizing community wisdom. Below is a grieving post from a pet loss forum, followed by multiple compassionate responses it received.

Synthesize these responses into a SINGLE, comprehensive, and ideal empathetic response. Capture the best insights, phrases, and tones from each. The goal is to create a longer, more perfect response that embodies the collective compassion and wisdom of the community.

### GRIEVING POST:
{post_text}

### COMMUNITY RESPONSES:
{responses_text}

### SYNTHESIZED IDEAL RESPONSE:
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a synthesizer of compassionate advice. Your goal is to merge the best elements of multiple responses into one ideal, empathetic, and comprehensive reply. Be heartfelt, wise, and kind."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error synthesizing responses for post: {e}")
        return list_of_responses[0] # Fallback to the first response



def create_enriched_dataset(input_path, output_path):
    """
    Processes the dataset: Groups responses by post and synthesizes them into one ideal response per post.
    """

    print(f"Loading data from: {input_path}")

    df = pd.read_parquet(input_path)

    print(f"Original dataset shape: {df.shape}")

    post_grouped = df.groupby('grieving_post').agg({'supportive_response': list}).reset_index()

    print(f"Number of unique posts: {len(post_grouped)}")
    print("First few posts:")
    print(post_grouped.head(2))  # Show first 2 rows to verify data

    enriched_data = []
    for i, (_, row) in enumerate(post_grouped.iterrows()):
        post_text = row['grieving_post']
        responses = row['supportive_response']
        
        # Add progress indicator
        if i % 10 == 0:  # Print every 10 posts
            print(f"Processing post {i+1}/{len(post_grouped)}...")

        if len(responses) == 1:
            ideal_response = responses[0]
        else:
            print(f"  Synthesizing {len(responses)} responses for post {i+1}...")
            ideal_response = synthesize_responses_for_post(post_text, responses)
            time.sleep(1)

        # ✅ CORRECT: Only user and assistant roles
        enriched_data.append({
            "messages": [
                {"role": "user", "content": post_text},
                {"role": "assistant", "content": ideal_response}
            ]
        })

    # Save in the correct format
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in enriched_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"Enriched dataset created with {len(enriched_data)} entries.")


create_enriched_dataset(
    input_path="data/final_relevant_training_dataset.parquet",  # Your input Parquet file
    output_path="data/enriched_fine_tuning_data.jsonl"  # Your output JSONL file
)