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
                wait_on_rate_limit=True
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
    
    def _map_v2_tweet(self, tweet) -> Dict[str, Any]:
        """Map v2 Tweet object to dictionary format - THIS WAS MISSING!"""
        try:
            return {
                'tweet_id': str(tweet.id),
                'text': tweet.text,
                'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
                'author_id': str(tweet.author_id) if tweet.author_id else None,
                'retweet_count': tweet.public_metrics.get('retweet_count', 0) if hasattr(tweet, 'public_metrics') and tweet.public_metrics else 0,
                'like_count': tweet.public_metrics.get('like_count', 0) if hasattr(tweet, 'public_metrics') and tweet.public_metrics else 0,
                'reply_count': tweet.public_metrics.get('reply_count', 0) if hasattr(tweet, 'public_metrics') and tweet.public_metrics else 0,
                'quote_count': tweet.public_metrics.get('quote_count', 0) if hasattr(tweet, 'public_metrics') and tweet.public_metrics else 0,
                'language': getattr(tweet, 'lang', None),
                'hashtags': [h['tag'] for h in (tweet.entities or {}).get('hashtags', [])] if hasattr(tweet, 'entities') and tweet.entities else [],
                'mentions': [m['username'] for m in (tweet.entities or {}).get('mentions', [])] if hasattr(tweet, 'entities') and tweet.entities else [],
            }
        except Exception as e:
            self.logger.error(f"Error mapping tweet {getattr(tweet, 'id', 'unknown')}: {e}")
            return {
                'tweet_id': str(getattr(tweet, 'id', 'unknown')),
                'text': getattr(tweet, 'text', ''),
                'created_at': None,
                'author_id': None,
                'retweet_count': 0,
                'like_count': 0,
                'reply_count': 0,
                'quote_count': 0,
                'language': None,
                'hashtags': [],
                'mentions': []
            }

    def collect_tweets_for_topic(self, topic: str, count: int = 100) -> pd.DataFrame:
        """Collect tweets for a single topic with proper error handling"""
        self.logger.info(f"Starting data collection for topic: {topic}")
        all_tweets = []
        
        try:
            queries = self.build_search_query(topic)
            self.logger.info(f"Found {len(queries)} queries for {topic}")
            per_query = max(10, min(RATE_LIMITS['tweets_per_request'], count // len(queries)))

            for i, query in enumerate(queries):
                try:
                    self.logger.info(f"Executing query {i+1}/{len(queries)}: {query} (max_results={per_query})")
                    
                    # Direct API call instead of Paginator for simplicity
                    response = self.client.search_recent_tweets(
                        query=query,
                        max_results=per_query,
                        tweet_fields=['id','text','created_at','author_id','public_metrics','lang','entities'],
                        expansions=['author_id'],
                        user_fields=['username','verified']
                    )
                    
                    if response.data:
                        all_tweets.extend(response.data)
                        self.logger.info(f"Got {len(response.data)} tweets from query: {query}")
                    else:
                        self.logger.warning(f"No tweets returned for query: {query}")
                    
                    # Stop if we have enough tweets
                    if len(all_tweets) >= count:
                        break
                        
                except TooManyRequests:
                    self.logger.warning(f"Rate limit hit on query: {query}")
                    break  # Stop trying more queries
                except Exception as e:
                    self.logger.error(f"Error with query '{query}': {e}")
                    continue

            # Convert to DataFrame
            if all_tweets:
                self.logger.info(f"Converting {len(all_tweets)} tweets to DataFrame")
                tweet_dicts = [self._map_v2_tweet(tweet) for tweet in all_tweets]
                df = pd.DataFrame(tweet_dicts)
                df['topic'] = topic
                df['collection_timestamp'] = datetime.now()
                
                self.logger.info(f"Successfully collected {len(df)} tweets for {topic}")
                return df
            else:
                self.logger.warning(f"No tweets collected for {topic}")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Fatal error collecting {topic}: {e}")
            return pd.DataFrame()
    

    def collect_tweets_by_query(self, query: str, count: int) -> List[Dict[str, Any]]:
        tweets_data = []
        try:
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

            for tweet in tweets:
                tweet_data = self._map_v2_tweet(tweet)
                tweet_data['search_query'] = query
                tweets_data.append(tweet_data)

        except Exception as e:
            self.logger.error(f"Error in collect_tweets_by_query: {e}")
        return tweets_data


    def collect_all_topics(self) -> Dict[str, pd.DataFrame]:
        """
        Collect data for all configured topics
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
        file_paths = {}
        timestamp = datetime.now().strftime(FILE_NAMING['timestamp_format'])
        
        os.makedirs(DATA_DIR, exist_ok=True) # Ensure base data directory exists

        for topic, df in data.items():
            if df.empty:
                self.logger.warning(f"No data to save for topic: {topic}")
                continue
                
            try:
                # Create topic directory
                topic_dir = os.path.join(DATA_DIR, 'raw', topic)
                os.makedirs(topic_dir, exist_ok=True)
                
                # Generate filename
                filename = f"{FILE_NAMING['raw_data_prefix']}{topic}_{timestamp}.csv"
                file_path = os.path.join(topic_dir, filename)
                
                # Save to CSV
                df.to_csv(file_path, index=False, encoding='utf-8')
                file_paths[topic] = file_path
                
                self.logger.info(f"✅ Saved {len(df)} tweets for {topic} to {file_path}")
                print(f"✅ Data saved: {file_path}")  # Console feedback
                
            except Exception as e:
                self.logger.error(f"❌ Failed to save data for {topic}: {e}")
                print(f"❌ Save failed for {topic}: {e}")
        
        return file_paths
