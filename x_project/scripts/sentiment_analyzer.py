# scripts/sentiment_analyzer.py

import pandas as pd
from textblob import TextBlob
import os
import logging
from datetime import datetime
from config import DATA_DIR, LOGS_DIR, FILE_NAMING

class TwitterSentimentAnalyzer:
    def __init__(self):
        # optional logging setup
        log_dir = os.path.join(LOGS_DIR, 'sentiment_logs')
        os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_dir, f"sentiment_{datetime.now():%Y%m%d}.log"),
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def analyze_sentiment(self, text: str) -> (float, str):
        """Return polarity (-1 to 1) and label."""
        if not isinstance(text, str) or text.strip()=="":
            return 0.0, 'neutral'
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        if polarity >  0.1: label = 'positive'
        elif polarity < -0.1: label = 'negative'
        else:                label = 'neutral'
        return polarity, label

    def analyze_all_topics(self, cleaned_data: dict) -> dict:
        """
        Apply sentiment analysis to each topic’s cleaned DataFrame.
        Input: {'technology': df1, 'stock_market': df2, ...}
        Returns: same keys, with 'sentiment_score' and 'sentiment_label' columns.
        """
        results = {}
        for topic, df in cleaned_data.items():
            if df.empty:
                results[topic] = df
                continue
            self.logger.info(f"Analyzing sentiment for topic: {topic}")
            scores, labels = zip(*df['text_cleaned'].map(self.analyze_sentiment))
            df['sentiment_score'] = scores
            df['sentiment_label'] = labels
            results[topic] = df
        return results

    def save_sentiment_data(self, sentiment_data: dict) -> dict:
        """
        Save enriched DataFrames back to CSV.
        Returns dict of file paths.
        """
        file_paths = {}
        ts = datetime.now().strftime(FILE_NAMING['timestamp_format'])
        for topic, df in sentiment_data.items():
            if df.empty: continue
            out_dir = os.path.join(DATA_DIR, 'sentiment', topic)
            os.makedirs(out_dir, exist_ok=True)
            fname = f"{FILE_NAMING['processed_data_prefix']}{topic}_{ts}.csv"
            path = os.path.join(out_dir, fname)
            df.to_csv(path, index=False)
            file_paths[topic] = path
            self.logger.info(f"Saved sentiment data for {topic} at {path}")
        return file_paths
