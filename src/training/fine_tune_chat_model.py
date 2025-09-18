# fine_tune_chat_model.py
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def create_fine_tune_job():
    # 1. Upload the file (in CHAT format)
    with open("data/enriched_fine_tuning_data.jsonl", "rb") as f:
        file_response = client.files.create(file=f, purpose="fine-tune")
    
    print(f"File uploaded with ID: {file_response.id}")
    
    # 2. Create fine-tuning job for CHAT model
    fine_tune_response = client.fine_tuning.jobs.create(
        training_file=file_response.id,
        model="gpt-3.5-turbo",  # This is the chat model
        suffix="empathia-peer",
        hyperparameters={
            "n_epochs": 3,
        }
    )
    
    print(f"Fine-tuning job created with ID: {fine_tune_response.id}")
    return fine_tune_response.id

if __name__ == "__main__":
    job_id = create_fine_tune_job()
    print(f"Monitor job with: openai api fine_tunes.follow -i {job_id}")