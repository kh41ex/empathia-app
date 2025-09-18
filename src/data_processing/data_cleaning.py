import pandas as pd
import re
import numpy as np

# Load the combined data
input_filename = 'data/combined_dataset_with_comments.csv'
df = pd.read_csv(input_filename)
print(f"Original dataset shape: {df.shape}")

# --- 1. Handle Missing Values ---
# Drop rows where the main text is completely missing (NaN)
df = df.dropna(subset=['text'])
print(f"Shape after dropping rows with missing text: {df.shape}")

# Fill other missing values if necessary (e.g., author)
df['author'] = df['author'].fillna('Unknown')

# --- 2. Remove Duplicates Carefully ---
# It's less straightforward now. One strategy is to remove duplicate text *within the same post*
# This keeps the same comment if it appears on different posts (which is rare but possible).
# Alternatively, you might decide duplicates are unlikely and skip this step for now.
# Let's skip it for the initial cleaning to be safe.
# df = df.drop_duplicates(subset=['post_id', 'text']) # Example of how you might do it later

# --- 3. Basic Text Cleaning Function --- 
# This function remains the same and works for both posts and comments
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text) # Remove URLs
    text = re.sub(r'<.*?>', '', text) # Remove HTML
    text = re.sub(r'[^a-zA-Z\s\?!.,\']', '', text) # Keep basic punctuation
    text = re.sub(r'\s+', ' ', text) # Remove extra whitespace
    return text.strip()

# --- 4. Apply the Cleaning Function ---
print("Cleaning text...")
df['cleaned_text'] = df['text'].apply(clean_text)

# --- 5. Remove Rows That Are Empty After Cleaning ---
# This removes posts/comments that were only URLs or special characters
df = df[df['cleaned_text'].str.strip().astype(bool)]
print(f"Shape after removing empty text after cleaning: {df.shape}")

# --- 6. (Optional) Analyze and Filter by Type ---
# This is where you can analyze posts and comments separately
print("\n--- Dataset Breakdown ---")
print(df['type'].value_counts())

# You can now easily create separate DataFrames for posts and comments if needed:
posts_df = df[df['type'] == 'post']
comments_df = df[df['type'] == 'comment']

# --- 7. Save the Cleaned Combined Dataset ---
output_filename = input_filename.replace('.csv', '_cleaned.csv')
df.to_csv(output_filename, index=False, encoding='utf-8')

print(f"\n Combined data cleaning complete!")
print(f"Cleaned data saved to: {output_filename}")

# --- Preview the Results ---
print("\n--- Preview: 5 Posts ---")
print(df[df['type'] == 'post'][['cleaned_text', 'type']].head())
print("\n--- Preview: 5 Comments ---")
print(df[df['type'] == 'comment'][['cleaned_text', 'type', 'parent_post_title']].head())