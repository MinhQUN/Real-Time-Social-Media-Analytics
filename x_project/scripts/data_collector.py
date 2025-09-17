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

from tweepy.errors import TooManyRequests
from typing import List
from tweepy import Paginator

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
        """ Authenticate using OAuth 2.0 bearer token only for X API v2 read-only endpoints."""
        try:
        # OAuth 1.0a for v1.1 endpoints
            auth = tweepy.OAuth1UserHandler(
                TWITTER_API_CONFIG['consumer_key'],
                TWITTER_API_CONFIG['consumer_secret'],
                TWITTER_API_CONFIG['access_token'],
                TWITTER_API_CONFIG['access_token_secret']
            )
            self.api = tweepy.API(auth, wait_on_rate_limit=True)

            # OAuth 2.0 for v2 endpoints
            self.client = tweepy.Client(
                bearer_token=TWITTER_API_CONFIG['bearer_token'],
                consumer_key=TWITTER_API_CONFIG['consumer_key'],
                consumer_secret=TWITTER_API_CONFIG['consumer_secret'],
                access_token=TWITTER_API_CONFIG['access_token'],
                access_token_secret=TWITTER_API_CONFIG['access_token_secret'],
                wait_on_rate_limit=False
            )

            self.logger.info("Authentication successful (OAuth1.0a and OAuth2.0 initialized)")

        except Exception as e:
            self.logger.error(f"Twitter API authentication failed: {e}")
            raise
    
    def build_search_query(self, topic: str) -> List[str]:
        """
        Build simple search queries for the given topic. This returns the list of queries from TOPICS_CONFIG.
        """
        from config import TOPICS_CONFIG

        if topic not in TOPICS_CONFIG:
            raise ValueError(f"Unknown topic: {topic}")
        return TOPICS_CONFIG[topic].get('search_queries', [])


    def collect_tweets_for_topic(self, topic: str, count: int = 100) -> pd.DataFrame:
        self.logger.info(f"Starting data collection for topic: {topic}")
        all_tweets = []
        queries = self.build_search_query(topic)
        per_query = max(1, count // len(queries))

        for query in queries:
            try:
                # Use Paginator for manual rate‐limit control
                paginator = Paginator(
                    self.client.search_recent_tweets,
                    query=query,
                    tweet_fields=[
                        'id','text','created_at','author_id','public_metrics',
                        'lang','entities','context_annotations','conversation_id'
                    ],
                    expansions=['author_id'],
                    user_fields=['username','public_metrics','verified','location'],
                    max_results=per_query,
                    limit=1,                    # only one batch per query
                    wait_on_rate_limit=False    # disable auto‐sleep
                )

                # flatten yields Tweet objects up to per_query
                tweets = []
                for tweet in paginator.flatten(limit=per_query):
                    tweets.append(tweet)

                all_tweets.extend(tweets)

            except TooManyRequests:
                self.logger.warning(
                    f"Rate limit hit for '{topic}' on query '{query}'. "
                    "Skipping remaining queries."
                )
                break

            except Exception as e:
                self.logger.error(f"Error collecting tweets for query '{query}': {e}")
                continue

        # Map to DataFrame
        df = pd.DataFrame([self._map_v2_tweet(t) for t in all_tweets])
        if not df.empty:
            df['topic'] = topic
            df['collection_timestamp'] = datetime.now()
            self.logger.info(f"Collected {len(df)} tweets for topic: {topic}")
        else:
            self.logger.info(f"No tweets collected for topic: {topic}")

        return df
    

    def collect_tweets_by_query(self, query: str, count: int) -> List[Dict[str, Any]]:
        tweets_data = []
        try:
            # Use v2 search_recent_tweets
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(count, RATE_LIMITS['tweets_per_request']),
                tweet_fields=[
                    'id',
                    'text',
                    'created_at',
                    'author_id',
                    'public_metrics',
                    'lang',
                    'entities',
                    'context_annotations',
                    'conversation_id',
                    'in_reply_to_user_id',
                    'referenced_tweets',
                    'source'
                ],
                expansions=['author_id'],
                user_fields=['username','public_metrics','verified','location']
            )
            tweets = response.data or []

            # Process each v2 Tweet object
            for tweet in tweets:
                tweet_data = {
                    'tweet_id': str(tweet.id),
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat(),
                    'retweet_count': tweet.public_metrics['retweet_count'],
                    'like_count': tweet.public_metrics['like_count'],
                    'reply_count': tweet.public_metrics['reply_count'],
                    'quote_count': tweet.public_metrics['quote_count'],
                    'language': tweet.lang,
                    'hashtags': [h['tag'] for h in (tweet.entities or {}).get('hashtags', [])],
                    'mentions': [m['username'] for m in (tweet.entities or {}).get('mentions', [])],
                    'search_query': query
                }
                tweets_data.append(tweet_data)

        except Exception as e:
            self.logger.error(f"Error in collect_tweets_by_query: {e}")
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
