import argparse
import logging
import os
import sys
from datetime import datetime
import time
import random

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.data_collector import TwitterDataCollector
from scripts.data_cleaner import TwitterDataCleaner
from scripts.data_processor import TwitterDataProcessor
from scripts.sentiment_analyzer import TwitterSentimentAnalyzer
from scripts.automation_scheduler import TwitterAutomationScheduler
from scripts.realtime_collector import RealTimeCollector
from config import LOGS_DIR, TOPICS_CONFIG, COLLECTION_SETTINGS

def setup_main_logging():
    """Setup main application logging"""
    log_dir = os.path.join(LOGS_DIR, 'main_logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'main_{datetime.now():%Y%m%d}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def collect_and_process_data(topic_arg, count_arg):
    logger = setup_main_logging()
    logger.info("Starting Twitter data collection and processing workflow")
    
    results = {'raw_files': {}, 'cleaned_files': {}, 'tableau_files': {}, 'sentiment_files': {}}
    collector = TwitterDataCollector()
    cleaner = TwitterDataCleaner()
    processor = TwitterDataProcessor()
    sentiment_analyzer = TwitterSentimentAnalyzer()

    if topic_arg != 'all':
        topics = [topic_arg]
    else:
        topics = list(TOPICS_CONFIG.keys())
        random.shuffle(topics)       # Shuffle for random order each run

    for topic in topics:
        try:
            tweets_per_topic = count_arg if topic_arg != 'all' else COLLECTION_SETTINGS[topic]['tweets_per_collection']
            logger.info(f"Collecting raw data for {topic} (count={tweets_per_topic})")
            
            # 1. Collect into DataFrame
            df_raw = collector.collect_tweets_for_topic(topic, tweets_per_topic)
            if df_raw.empty:
                logger.warning(f"No tweets collected for {topic}")
                continue

            # 2. Save raw CSV but DON'T overwrite df_raw
            raw_path = collector.save_raw_data({topic: df_raw})[topic]
            results['raw_files'][topic] = raw_path

            # 3. Clean using the DataFrame
            logger.info(f"Cleaning data for {topic}")
            df_clean = cleaner.clean_topic_data(topic, df_raw) 
            clean_path = cleaner.save_cleaned_data({topic: df_clean})[topic]
            results['cleaned_files'][topic] = clean_path

            # 4. Process
            logger.info(f"Processing data for {topic}")
            df_proc = processor.process_topic_data(df_clean, topic)
            tableau_path = processor.save_tableau_data({topic: df_proc})[topic]
            results['tableau_files'][topic] = tableau_path

            # 5. Sentiment
            logger.info(f"Analyzing sentiment for {topic}")
            df_sent = sentiment_analyzer.analyze_topic_sentiment(topic, df_clean)
            sent_path = sentiment_analyzer.save_sentiment_data({topic: df_sent})[topic]
            results['sentiment_files'][topic] = sent_path

        except Exception as e:
            logger.error(f"Error processing topic {topic}: {e}", exc_info=True)

    logger.info("Pipeline complete")
    return results


def start_realtime_mode():
    """Start continuous real-time collection and processing"""
    logger = setup_main_logging()
    logger.info("Starting real-time data collection mode")
    
    try:
        rtc = RealTimeCollector()
        threads = rtc.start_realtime_collection()
        
        print(" Real-time collection started. Press Ctrl+C to stop...")
        print(" Check data/raw/, data/cleaned/, and tableau_data/ for files")
        
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n Stopping real-time collection...")
        rtc.stop_collection()
        for thread in threads:
            thread.join(timeout=5)
        logger.info("Real-time collection stopped by user")
        print("Real-time collection stopped successfully")

    except Exception as e:
        logger.error(f"Error in real-time mode: {e}", exc_info=True)
        print(f"Real-time collection failed: {e}")

def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(description='Twitter Data Collection and Processing')
    parser.add_argument(
        '--mode',
        choices=['collect', 'schedule', 'analyze', 'realtime'],
        default='collect',
        help='Operation mode'
    )
    parser.add_argument(
        '--topic',
        choices=list(TOPICS_CONFIG.keys()) + ['all'],
        default='all',
        help='Topic to process'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=10,
        help='Number of tweets to collect per topic (only for collect mode)'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'collect':
        results = collect_and_process_data(args.topic, args.count)
        print("Data collection completed successfully!")
        print(f"Files created: {len(results['tableau_files'])} Tableau files")
        
    elif args.mode == 'schedule':
        scheduler = TwitterAutomationScheduler()
        scheduler.start_scheduled_collection()
        
    elif args.mode == 'realtime':
        start_realtime_mode()
        
    elif args.mode == 'analyze':
        # Future: Add analysis-only mode
        print("Analysis mode not implemented yet")

if __name__ == "__main__":
    main()
