# scripts/data_collector.py
"""
Advanced Twitter data collection module with multi-topic support
"""

import tweepy
import pandas as pd
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import time
import os

from config import (
    TWITTER_API_CONFIG, RATE_LIMITS, TOPICS_CONFIG, 
    COLLECTION_SETTINGS, DATA_DIR, LOGS_DIR, FILE_NAMING
)

class TwitterDataCollector:
    """
    Advanced Twitter data collector with multi-topic support
    """
    
    def __init__(self):
        self.setup_logging()
        self.authenticate_twitter()
        self.topics = list(TOPICS_CONFIG.keys())
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = os.path.join(LOGS_DIR, 'collection_logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'collection_{datetime.now().strftime("%Y%m%d")}.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def authenticate_twitter(self):
        """Authenticate with Twitter API"""
        try:
            # OAuth 1.0a authentication
            auth = tweepy.OAuthHandler(
                TWITTER_API_CONFIG['consumer_key'],
                TWITTER_API_CONFIG['consumer_secret']
            )
            auth.set_access_token(
                TWITTER_API_CONFIG['access_token'],
                TWITTER_API_CONFIG['access_token_secret']
            )
            
            self.api = tweepy.API(auth, wait_on_rate_limit=True)
            
            # Verify credentials
            self.api.verify_credentials()
            self.logger.info("Twitter API authentication successful")
            
        except Exception as e:
            self.logger.error(f"Twitter API authentication failed: {e}")
            raise
    
    def collect_tweets_for_topic(self, topic: str, count: int = 100) -> pd.DataFrame:
        """
        Collect tweets for a specific topic
        
        Args:
            topic: Topic name ('technology', 'stock_market', 'sports')
            count: Number of tweets to collect
            
        Returns:
            DataFrame containing tweet data
        """
        if topic not in TOPICS_CONFIG:
            raise ValueError(f"Unknown topic: {topic}")
        
        self.logger.info(f"Starting data collection for topic: {topic}")
        
        topic_config = TOPICS_CONFIG[topic]
        all_tweets = []
        
        # Collect tweets using different search strategies
        for query in topic_config['search_queries']:
            try:
                tweets = self.collect_tweets_by_query(query, count // len(topic_config['search_queries']))
                all_tweets.extend(tweets)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error collecting tweets for query '{query}': {e}")
                continue
        
        # Convert to DataFrame
        df = pd.DataFrame(all_tweets)
        
        if not df.empty:
            df['topic'] = topic
            df['collection_timestamp'] = datetime.now()
            
        self.logger.info(f"Collected {len(df)} tweets for topic: {topic}")
        return df
    
    def collect_tweets_by_query(self, query: str, count: int) -> List[Dict[str, Any]]:
        """
        Collect tweets using a specific search query
        
        Args:
            query: Search query string
            count: Number of tweets to collect
            
        Returns:
            List of tweet dictionaries
        """
        tweets_data = []
        
        try:
            tweets = tweepy.Cursor(
                self.api.search_tweets,
                q=query,
                tweet_mode='extended',
                lang='en',
                result_type='mixed'
            ).items(count)
            
            for tweet in tweets:
                tweet_data = {
                    'tweet_id': tweet.id,
                    'text': tweet.full_text,
                    'user_id': tweet.user.id,
                    'username': tweet.user.screen_name,
                    'user_followers': tweet.user.followers_count,
                    'user_following': tweet.user.friends_count,
                    'user_verified': tweet.user.verified,
                    'created_at': tweet.created_at,
                    'retweet_count': tweet.retweet_count,
                    'favorite_count': tweet.favorite_count,
                    'quote_count': getattr(tweet, 'quote_count', 0),
                    'reply_count': getattr(tweet, 'reply_count', 0),
                    'hashtags': [tag['text'] for tag in tweet.entities.get('hashtags', [])],
                    'mentions': [mention['screen_name'] for mention in tweet.entities.get('user_mentions', [])],
                    'urls': [url['expanded_url'] for url in tweet.entities.get('urls', [])],
                    'is_retweet': hasattr(tweet, 'retweeted_status'),
                    'is_quote': hasattr(tweet, 'quoted_status'),
                    'language': tweet.lang,
                    'source': tweet.source,
                    'location': tweet.user.location,
                    'search_query': query
                }
                
                tweets_data.append(tweet_data)
                
        except Exception as e:
            self.logger.error(f"Error in collect_tweets_by_query: {e}")
            raise
        
        return tweets_data
    
    def collect_all_topics(self) -> Dict[str, pd.DataFrame]:
        """
        Collect data for all configured topics
        
        Returns:
            Dictionary mapping topic names to DataFrames
        """
        all_data = {}
        
        for topic in self.topics:
            try:
                settings = COLLECTION_SETTINGS[topic]
                df = self.collect_tweets_for_topic(topic, settings['tweets_per_collection'])
                all_data[topic] = df
                
                # Brief pause between topics
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Failed to collect data for topic {topic}: {e}")
                all_data[topic] = pd.DataFrame()
        
        return all_data
    
    def save_raw_data(self, data: Dict[str, pd.DataFrame]) -> Dict[str, str]:
        """
        Save raw collected data to CSV files
        
        Args:
            data: Dictionary mapping topic names to DataFrames
            
        Returns:
            Dictionary mapping topic names to file paths
        """
        file_paths = {}
        timestamp = datetime.now().strftime(FILE_NAMING['timestamp_format'])
        
        for topic, df in data.items():
            if df.empty:
                continue
                
            # Create topic directory
            topic_dir = os.path.join(DATA_DIR, 'raw', topic)
            os.makedirs(topic_dir, exist_ok=True)
            
            # Generate filename
            filename = f"{FILE_NAMING['raw_data_prefix']}{topic}_{timestamp}.csv"
            file_path = os.path.join(topic_dir, filename)
            
            # Save to CSV
            df.to_csv(file_path, index=False)
            file_paths[topic] = file_path
            
            self.logger.info(f"Saved {len(df)} tweets for {topic} to {file_path}")
        
        return file_paths
