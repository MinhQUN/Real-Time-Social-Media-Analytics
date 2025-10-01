# scripts/testing.py
import pandas as pd
import os
import sys
from datetime import datetime

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now imports will work
from scripts.data_collector import TwitterDataCollector
from config import TWITTER_API_CONFIG

# Initialize collector
collector = TwitterDataCollector()

# Perform a manual test collection
test_topic = 'technology'
test_count = 10  # Changed to 10 since API requires min 10
df_test = collector.collect_tweets_for_topic(test_topic, test_count)

# Print basic info to the console
print(f"=== DataFrame Info for {test_topic} ===")
print(f"DataFrame shape: {df_test.shape}")
print(f"Total tweets collected: {len(df_test)}")

if not df_test.empty:
    print(f"Columns: {list(df_test.columns)}")
    print("\n=== First 3 rows ===")
    print(df_test.head(3))
    
    # Save CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join('..', 'data', 'raw', test_topic)  # Go up one level
    os.makedirs(out_dir, exist_ok=True)
    
    filename = f"test_raw_{test_topic}_{timestamp}.csv"
    file_path = os.path.join(out_dir, filename)
    
    df_test.to_csv(file_path, index=False)
    print(f"Saved {len(df_test)} records to {file_path}")
else:
    print(f"No data collected for topic '{test_topic}'")
    print("This might be due to:")
    print("- Rate limits")
    print("- No matching tweets for the queries")
    print("- API quota exceeded")
