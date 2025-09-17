"""
General application settings and configurations
"""

import os
from datetime import datetime

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
TABLEAU_DIR = os.path.join(BASE_DIR, 'tableau_data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Data processing settings
DATA_PROCESSING = {
    'remove_duplicates': True,
    'clean_text': True,
    'extract_hashtags': True,
    'calculate_engagement': True,
    'sentiment_analysis': True
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}

# File naming conventions
FILE_NAMING = {
    'timestamp_format': '%Y%m%d_%H%M%S',
    'raw_data_prefix': 'raw_tweets_',
    'cleaned_data_prefix': 'cleaned_tweets_',
    'processed_data_prefix': 'processed_tweets_'
}

# Tableau export settings
TABLEAU_EXPORT = {
    'include_sentiment': True,
    'include_engagement_metrics': True,
    'include_time_analysis': True,
    'max_records_per_file': 10000
}
