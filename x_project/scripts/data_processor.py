# scripts/data_processor.py
"""
TwitterDataProcessor: Cleans, enriches, and processes tweet data for Tableau export
"""

import os
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

from config import (
    DATA_DIR, TABLEAU_DIR, LOGS_DIR, FILE_NAMING,
    DATA_PROCESSING, TABLEAU_EXPORT
)

try:
    from textblob import TextBlob
except ImportError:
    print("Warning: TextBlob not installed. Sentiment analysis will be disabled.")
    TextBlob = None


class TwitterDataProcessor:
    """
    Processes cleaned tweet data and prepares it for Tableau visualization
    """

    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)

    def setup_logging(self):
        """Setup logging for data processing"""
        log_dir = Path(LOGS_DIR) / 'processing_logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'processing_{datetime.now().strftime("%Y%m%d")}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def clean_text(self, text: str) -> str:
        """Clean and normalize tweet text"""
        if not isinstance(text, str):
            return ""
        
        import re
        # Remove URLs
        text = re.sub(r"http\S+|www\S+", "", text)
        # Remove mentions but keep the context
        text = re.sub(r"@\w+", "", text)
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r"[^\w\s.,!?-]", "", text)
        
        return text.strip()

    def calculate_engagement_score(self, row: pd.Series) -> float:
        """Calculate engagement score from metrics"""
        try:
            engagement = (
                row.get('retweet_count', 0) +
                row.get('like_count', 0) +
                row.get('reply_count', 0) +
                row.get('quote_count', 0)
            )
            return float(engagement)
        except:
            return 0.0

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Perform sentiment analysis on text"""
        if not TextBlob or not text:
            return {'polarity': 0.0, 'subjectivity': 0.0, 'sentiment_label': 'neutral'}
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Classify sentiment
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'polarity': polarity,
                'subjectivity': subjectivity,
                'sentiment_label': label
            }
        except:
            return {'polarity': 0.0, 'subjectivity': 0.0, 'sentiment_label': 'neutral'}

    def extract_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract time-based features for temporal analysis"""
        if 'created_at' not in df.columns:
            return df
        
        try:
            # Ensure created_at is datetime
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # Extract time features
            df['hour_of_day'] = df['created_at'].dt.hour
            df['day_of_week'] = df['created_at'].dt.day_name()
            df['month'] = df['created_at'].dt.month_name()
            df['date'] = df['created_at'].dt.date
            
        except Exception as e:
            self.logger.warning(f"Error extracting time features: {e}")
        
        return df

    def process_topic_data(self, df: pd.DataFrame, topic: str) -> pd.DataFrame:
        """Process data for a specific topic"""
        if df.empty:
            self.logger.warning(f"No data to process for topic: {topic}")
            return df

        self.logger.info(f"Processing {len(df)} tweets for topic: {topic}")
        processed_df = df.copy()

        # Clean text if enabled
        if DATA_PROCESSING.get('clean_text', True):
            processed_df['cleaned_text'] = processed_df['text'].apply(self.clean_text)

        # Calculate engagement scores
        if DATA_PROCESSING.get('calculate_engagement', True):
            processed_df['engagement_score'] = processed_df.apply(self.calculate_engagement_score, axis=1)

        # Perform sentiment analysis
        if DATA_PROCESSING.get('sentiment_analysis', True) and TABLEAU_EXPORT.get('include_sentiment', True):
            sentiment_results = processed_df['text'].apply(self.analyze_sentiment)
            
            # Extract sentiment components
            processed_df['sentiment_polarity'] = sentiment_results.apply(lambda x: x['polarity'])
            processed_df['sentiment_subjectivity'] = sentiment_results.apply(lambda x: x['subjectivity'])
            processed_df['sentiment_label'] = sentiment_results.apply(lambda x: x['sentiment_label'])

        # Extract time features
        if TABLEAU_EXPORT.get('include_time_analysis', True):
            processed_df = self.extract_time_features(processed_df)

        # Add processing metadata
        processed_df['processed_at'] = datetime.now()
        processed_df['topic'] = topic

        self.logger.info(f"Successfully processed {len(processed_df)} tweets for {topic}")
        return processed_df

    def process_all_topics(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Process data for all topics"""
        processed_data = {}
        
        for topic, df in data.items():
            try:
                processed_data[topic] = self.process_topic_data(df, topic)
            except Exception as e:
                self.logger.error(f"Error processing topic {topic}: {e}")
                processed_data[topic] = pd.DataFrame()
        
        return processed_data

    def prepare_tableau_export(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare DataFrame for Tableau export with selected columns"""
        if df.empty:
            return df

        # Define columns to include in Tableau export
        tableau_columns = [
            'tweet_id', 'text', 'cleaned_text', 'created_at', 'topic',
            'username', 'user_followers', 'user_verified',
            'retweet_count', 'like_count', 'reply_count', 'quote_count',
            'engagement_score', 'hashtags', 'mentions',
            'hour_of_day', 'day_of_week', 'month', 'date'
        ]

        # Add sentiment columns if enabled
        if TABLEAU_EXPORT.get('include_sentiment', True):
            tableau_columns.extend(['sentiment_polarity', 'sentiment_subjectivity', 'sentiment_label'])

        # Filter to existing columns
        available_columns = [col for col in tableau_columns if col in df.columns]
        tableau_df = df[available_columns].copy()

        # Handle max records per file
        max_records = TABLEAU_EXPORT.get('max_records_per_file', 10000)
        if len(tableau_df) > max_records:
            self.logger.warning(f"Dataset has {len(tableau_df)} records, truncating to {max_records}")
            tableau_df = tableau_df.head(max_records)

        return tableau_df

    def save_tableau_data(self, processed_data: Dict[str, pd.DataFrame]) -> Dict[str, str]:
        """Save processed data as Tableau-ready CSV files"""
        tableau_files = {}
        timestamp = datetime.now().strftime(FILE_NAMING['timestamp_format'])
        
        # Ensure tableau directory exists
        tableau_dir = Path(TABLEAU_DIR)
        tableau_dir.mkdir(parents=True, exist_ok=True)

        # Save individual topic files
        for topic, df in processed_data.items():
            if df.empty:
                continue

            try:
                # Prepare for Tableau
                tableau_df = self.prepare_tableau_export(df)
                
                # Save topic-specific file
                filename = f"{topic}_dashboard_{timestamp}.csv"
                filepath = tableau_dir / filename
                tableau_df.to_csv(filepath, index=False, encoding='utf-8')
                
                tableau_files[topic] = str(filepath)
                self.logger.info(f"Saved Tableau file for {topic}: {filepath}")

            except Exception as e:
                self.logger.error(f"Error saving Tableau file for {topic}: {e}")

        # Create combined dashboard file
        try:
            all_data = []
            for topic, df in processed_data.items():
                if not df.empty:
                    tableau_df = self.prepare_tableau_export(df)
                    all_data.append(tableau_df)

            if all_data:
                combined_df = pd.concat(all_data, ignore_index=True)
                combined_filename = f"combined_dashboard_{timestamp}.csv"
                combined_filepath = tableau_dir / combined_filename
                combined_df.to_csv(combined_filepath, index=False, encoding='utf-8')
                
                tableau_files['combined'] = str(combined_filepath)
                self.logger.info(f"Saved combined Tableau file: {combined_filepath}")

        except Exception as e:
            self.logger.error(f"Error creating combined Tableau file: {e}")

        return tableau_files

    def generate_summary_report(self, processed_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Generate summary statistics for processed data"""
        summary = {
            'processing_timestamp': datetime.now().isoformat(),
            'total_tweets': 0,
            'topics': {}
        }

        for topic, df in processed_data.items():
            if df.empty:
                topic_summary = {'tweet_count': 0, 'avg_engagement': 0}
            else:
                topic_summary = {
                    'tweet_count': len(df),
                    'unique_users': df['username'].nunique() if 'username' in df.columns else 0,
                    'avg_engagement': df['engagement_score'].mean() if 'engagement_score' in df.columns else 0,
                    'sentiment_distribution': df['sentiment_label'].value_counts().to_dict() if 'sentiment_label' in df.columns else {},
                    'top_hashtags': self._extract_top_hashtags(df),
                    'date_range': {
                        'start': str(df['created_at'].min()) if 'created_at' in df.columns else None,
                        'end': str(df['created_at'].max()) if 'created_at' in df.columns else None
                    }
                }
                summary['total_tweets'] += len(df)

            summary['topics'][topic] = topic_summary

        return summary

    def _extract_top_hashtags(self, df: pd.DataFrame, limit: int = 5) -> List[str]:
        """Extract top hashtags from processed data"""
        try:
            if 'hashtags' not in df.columns:
                return []
            
            all_hashtags = []
            for hashtags in df['hashtags'].dropna():
                if isinstance(hashtags, str):
                    # Handle string representation of lists
                    try:
                        hashtags = eval(hashtags)
                    except:
                        continue
                if isinstance(hashtags, list):
                    all_hashtags.extend(hashtags)
            
            from collections import Counter
            hashtag_counts = Counter(all_hashtags)
            return [tag for tag, count in hashtag_counts.most_common(limit)]
        except:
            return []
