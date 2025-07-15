# At the top of your file, import pandas for CSV inspection
import pandas as pd

# ================================================
# 1. Run a simple collection test and inspect the DataFrame
# ================================================
from scripts.data_collector import TwitterDataCollector
from config import TWITTER_API_CONFIG

# Initialize collector
collector = TwitterDataCollector()

# Perform a manual test collection (e.g., 5 tweets for '#AI')
test_topic = 'technology'
test_count = 5
df_test = collector.collect_tweets_for_topic(test_topic, test_count)

# ================================================
# 2. Print basic info to the console
# ================================================
print(f"=== DataFrame Info for {test_topic} ===")
print(df_test.info())               
print(f"Total tweets collected: {len(df_test)}")

# ================================================
# 3. Show the first few rows
# ================================================
print("=== First 5 rows ===")
print(df_test.head(5))                # Displays sample records

# ================================================
# 4. Conditionally save CSV only if non-empty
# ================================================
import os
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

if df_test.empty:
    print(f"⚠️  No data collected for topic '{test_topic}' at {timestamp}")
else:
    # Ensure directory exists
    out_dir = os.path.join('data', 'raw', test_topic)
    os.makedirs(out_dir, exist_ok=True)
    
    # Build filename
    filename = f"raw_{test_topic}_{timestamp}.csv"
    file_path = os.path.join(out_dir, filename)
    
    # Save DataFrame to CSV
    df_test.to_csv(file_path, index=False)
    print(f"✅  Saved {len(df_test)} records to {file_path}")
