import praw
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import time
from datetime import datetime, timezone

# Load environment variables from .env file
load_dotenv()

# DEBUG: Print the value of the client ID to see if it was loaded
print("CLIENT_ID from .env:", os.getenv('REDDIT_CLIENT_ID'))

# --- Configuration ---
SUBREDDIT_NAME = "dogs+cats+AskVet"
SEARCH_QUERY = "euthanasia put down vet sleep loss grief died"  # Leave empty for all posts. Use "dog", "cat", etc. to filter.
POST_LIMIT = 10000  # Number of posts to scrape. Set to None for all (use cautiously).
OUTPUT_FILENAME = f"reddit_combined_petloss_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"


# --- Authenticate with Reddit ---
# TEMPORARY: Hardcode your values directly here for testing
client_id = "t1zQj9ocpJxLVR_gWubhzQ"  # <- Your actual client_id
client_secret = "cjol1Q6wTGK2pTLfjXx-0_-46u2lDQ"  # <- Your actual client_secret
user_agent = "script:PetLossScraper:v1.0 (by u/Exotic_Ad_8689)" # <- Your actual user agent

print(f"Using Client ID: {client_id}")

try:
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        # username and password omitted for read-only mode
    )
    # Test authentication
    print("Authentication successful in read-only mode.")
    # Try a simple API call to confirm
    sub = reddit.subreddit("test")
    print(f"Successfully accessed subreddit: {sub.display_name}")
except Exception as e:
    print(f"Error during authentication: {e}")
    exit()

# --- Function to scrape posts ---
def scrape_subreddit(subreddit_name, query="", limit=None):
    """
    Scrapes posts AND comments from a specified subreddit.
    Focuses on harvesting supportive comments for training an empathetic AI.
    """
    subreddit = reddit.subreddit(subreddit_name)
    posts_list = []
    
    # Choose the search method
    if query:
        print(f"Searching r/{subreddit_name} for posts containing: '{query}'")
        submissions = subreddit.search(query, limit=limit)
    else:
        print(f"Scraping top posts from r/{subreddit_name}")
        submissions = subreddit.top(limit=limit, time_filter='all') # 'all' to get the most upvoted ever

    # Iterate through submissions
    for i, submission in enumerate(submissions):
        try:
            # Skip stickied posts (often rules or announcements)
            if submission.stickied:
                continue
                
            # --- 1. FIRST, SAVE THE MAIN POST ITSELF ---
            post_data = {
                "type": "post",
                "post_id": submission.id,
                "title": submission.title,
                "author": str(submission.author),
                "score": submission.score,
                "num_comments": submission.num_comments,
                "created_utc": datetime.fromtimestamp(submission.created_utc, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                "url": submission.url,
                "text": submission.selftext,
                "subreddit": str(submission.subreddit)
            }
            posts_list.append(post_data)
            
            # --- 2. THEN, SCRAPE ALL COMMENTS FOR THAT POST ---
            print(f"Scraping comments for post: {submission.title}")
            # This line is crucial: it handles 'load more' comments
            submission.comments.replace_more(limit=0) 
            
            # Now iterate through all comments in the flattened list
            for comment in submission.comments.list():
                # Skip automated moderator comments and deleted comments
                if comment.author == 'AutoModerator' or comment.body == '[deleted]' or comment.body == '[removed]':
                    continue
                    
                comment_data = {
                    "type": "comment",
                    "post_id": submission.id,
                    "comment_id": comment.id,
                    "author": str(comment.author),
                    "score": comment.score,
                    "created_utc": datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                    "text": comment.body,
                    "parent_post_title": submission.title # Useful for context
                }
                posts_list.append(comment_data)
            
            # Print progress
            if (i + 1) % 5 == 0: # Print every 5 posts since it's slower
                print(f"Scraped {i + 1} posts and all their comments...")
                
            # Be respectful and avoid hitting rate limits
            time.sleep(1) # Increased sleep time because comment scraping is more intensive
            
        except Exception as e:
            print(f"Error processing post {submission.id}: {e}")
            continue
    
    return posts_list

# --- Main execution ---

if __name__ == "__main__":
    print("Starting Reddit scraper...")
    
    # Scrape the posts
    posts_data = scrape_subreddit(SUBREDDIT_NAME, SEARCH_QUERY, POST_LIMIT)
    
    if posts_data:
        # Convert to DataFrame
        df = pd.DataFrame(posts_data)
        
        # Basic data cleaning: remove posts with empty text
        df = df[df['text'].str.strip().astype(bool)]
        df.reset_index(drop=True, inplace=True)
        
        # Save to CSV
        df.to_csv(OUTPUT_FILENAME, index=False, encoding='utf-8')
        print(f"Successfully scraped {len(df)} posts. Data saved to '{OUTPUT_FILENAME}'.")
        
        # Preview the data
        print("\nPreview of the scraped data:")
        print(df[['title', 'author', 'score', 'created_utc']].head())
        
    else:
        print("No posts were scraped. Check your subreddit name and search query.")