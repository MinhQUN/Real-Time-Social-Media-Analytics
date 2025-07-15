# scripts/data_cleaner.py
"""
Advanced data cleaning module for Twitter data
"""

import pandas as pd
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional
import os

from config import DATA_DIR, LOGS_DIR, FILE_NAMING, DATA_PROCESSING

class TwitterDataCleaner:
    """
    Advanced Twitter data cleaning with topic-specific processing
    """
    
    def __init__(self):
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = os.path.join(LOGS_DIR, 'processing_logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'cleaning_{datetime.now().strftime("%Y%m%d")}.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def clean_text(self, text: str) -> str:
        """
        Clean tweet text by removing unwanted characters and formatting
        
        Args:
            text: Raw tweet text
            
        Returns:
            Cleaned text
        """
        if pd.isna(text):
            return ""
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove special characters but keep hashtags and mentions
        text = re.sub(r'[^\w\s#@]', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
    
    def extract_hashtags(self, text: str) -> List[str]:
        """
        Extract hashtags from tweet text
        
        Args:
            text: Tweet text
            
        Returns:
            List of hashtags
        """
        if pd.isna(text):
            return []
        
        hashtags = re.findall(r'#\w+', text)
        return [tag.lower() for tag in hashtags]
    
    def calculate_engagement_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate engagement metrics for tweets
        
        Args:
            df: DataFrame containing tweet data
            
        Returns:
            DataFrame with additional engagement metrics
        """
        # Basic engagement rate
        df['total_engagement'] = (
            df['retweet_count'] + 
            df['favorite_count'] + 
            df['quote_count'] + 
            df['reply_count']
        )
        
        # Engagement rate relative to follower count
        df['engagement_rate'] = (
            df['total_engagement'] / 
            df['user_followers'].replace(0, 1)
        ) * 100
        
        # Virality score (weighted engagement)
        df['virality_score'] = (
            df['retweet_count'] * 3 +
            df['favorite_count'] * 1 +
            df['quote_count'] * 2 +
            df['reply_count'] * 1.5
        )
        
        # Normalize virality score
        if df['virality_score'].max() > 0:
            df['virality_score_normalized'] = (
                df['virality_score'] / df['virality_score'].max()
            ) * 100
        else:
            df['virality_score_normalized'] = 0
        
        return df
    
    def add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add time-based features for analysis
        
        Args:
            df: DataFrame containing tweet data
            
        Returns:
            DataFrame with time features
        """
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Extract time components
        df['hour'] = df['created_at'].dt.hour
        df['day_of_week'] = df['created_at'].dt.dayofweek
        df['day_name'] = df['created_at'].dt.day_name()
        df['month'] = df['created_at'].dt.month
        df['year'] = df['created_at'].dt.year
        df['date'] = df['created_at'].dt.date
        
        # Create time periods
        df['time_period'] = df['hour'].apply(self.categorize_time_period)
        
        return df
    
    def categorize_time_period(self, hour: int) -> str:
        """
        Categorize hour into time periods
        
        Args:
            hour: Hour of the day (0-23)
            
        Returns:
            Time period category
        """
        if 5 <= hour < 12:
            return 'Morning'
        elif 12 <= hour < 17:
            return 'Afternoon'
        elif 17 <= hour < 21:
            return 'Evening'
        else:
            return 'Night'
    
    def clean_topic_data(self, df: pd.DataFrame, topic: str) -> pd.DataFrame:
        """
        Clean data for a specific topic
        
        Args:
            df: Raw tweet DataFrame
            topic: Topic name
            
        Returns:
            Cleaned DataFrame
        """
        if df.empty:
            return df
        
        self.logger.info(f"Cleaning data for topic: {topic}")
        original_count = len(df)
        
        # Remove duplicates
        if DATA_PROCESSING['remove_duplicates']:
            df = df.drop_duplicates(subset=['tweet_id'])
        
        # Clean text
        if DATA_PROCESSING['clean_text']:
            df['text_cleaned'] = df['text'].apply(self.clean_text)
        
        # Extract hashtags
        if DATA_PROCESSING['extract_hashtags']:
            df['hashtags_extracted'] = df['text'].apply(self.extract_hashtags)
        
        # Calculate engagement metrics
        if DATA_PROCESSING['calculate_engagement']:
            df = self.calculate_engagement_metrics(df)
        
        # Add time features
        df = self.add_time_features(df)
        
        # Remove rows with empty text
        df = df[df['text_cleaned'].str.len() > 0]
        
        # Remove bots (basic heuristic)
        df = df[df['user_followers'] > 0]
        df = df[df['user_followers'] < 1000000]  # Remove accounts with >1M followers (likely bots or celebrities)
        
        cleaned_count = len(df)
        removed_count = original_count - cleaned_count
        
        self.logger.info(f"Cleaned {topic} data: {removed_count} tweets removed, {cleaned_count} tweets remaining")
        
        return df
    
    def clean_all_topics(self, raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        Clean data for all topics
        
        Args:
            raw_data: Dictionary mapping topic names to raw DataFrames
            
        Returns:
            Dictionary mapping topic names to cleaned DataFrames
        """
        cleaned_data = {}
        
        for topic, df in raw_data.items():
            try:
                cleaned_df = self.clean_topic_data(df, topic)
                cleaned_data[topic] = cleaned_df
                
            except Exception as e:
                self.logger.error(f"Error cleaning data for topic {topic}: {e}")
                cleaned_data[topic] = pd.DataFrame()
        
        return cleaned_data
    
    def save_cleaned_data(self, cleaned_data: Dict[str, pd.DataFrame]) -> Dict[str, str]:
        """
        Save cleaned data to CSV files
        
        Args:
            cleaned_data: Dictionary mapping topic names to cleaned DataFrames
            
        Returns:
            Dictionary mapping topic names to file paths
        """
        file_paths = {}
        timestamp = datetime.now().strftime(FILE_NAMING['timestamp_format'])
        
        for topic, df in cleaned_data.items():
            if df.empty:
                continue
                
            # Create topic directory
            topic_dir = os.path.join(DATA_DIR, 'cleaned', topic)
            os.makedirs(topic_dir, exist_ok=True)
            
            # Generate filename
            filename = f"{FILE_NAMING['cleaned_data_prefix']}{topic}_{timestamp}.csv"
            file_path = os.path.join(topic_dir, filename)
            
            # Save to CSV
            df.to_csv(file_path, index=False)
            file_paths[topic] = file_path
            
            self.logger.info(f"Saved cleaned data for {topic} to {file_path}")
        
        return file_paths
