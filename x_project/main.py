# main.py
"""
Main orchestration script for Twitter data collection and processing
"""

import argparse
import logging
from datetime import datetime
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.data_collector import TwitterDataCollector
from scripts.data_cleaner import TwitterDataCleaner
from scripts.data_processor import TwitterDataProcessor
from scripts.sentiment_analyzer import TwitterSentimentAnalyzer
from scripts.automation_scheduler import TwitterAutomationScheduler

from config import LOGS_DIR, TOPICS_CONFIG

def setup_main_logging():
    """Setup main application logging"""
    log_dir = os.path.join(LOGS_DIR, 'main_logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'main_{datetime.now().strftime("%Y%m%d")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def collect_and_process_data():
    """Main data collection and processing workflow"""
    logger = setup_main_logging()
    logger.info("Starting Twitter data collection and processing workflow")
    
    try:
        # Initialize components
        collector = TwitterDataCollector()
        cleaner = TwitterDataCleaner()
        processor = TwitterDataProcessor()
        sentiment_analyzer = TwitterSentimentAnalyzer()
        
        # Step 1: Collect raw data
        logger.info("Step 1: Collecting raw data")
        raw_data = collector.collect_all_topics()
        raw_files = collector.save_raw_data(raw_data)
        
        # Step 2: Clean data
        logger.info("Step 2: Cleaning data")
        cleaned_data = cleaner.clean_all_topics(raw_data)
        cleaned_files = cleaner.save_cleaned_data(cleaned_data)
        
        # Step 3: Process data for Tableau
        logger.info("Step 3: Processing data for Tableau")
        processed_data = processor.process_all_topics(cleaned_data)
        tableau_files = processor.save_tableau_data(processed_data)
        
        # Step 4: Perform sentiment analysis
        logger.info("Step 4: Performing sentiment analysis")
        sentiment_data = sentiment_analyzer.analyze_all_topics(cleaned_data)
        sentiment_files = sentiment_analyzer.save_sentiment_data(sentiment_data)
        
        # Step 5: Generate summary report
        logger.info("Step 5: Generating summary report")
        summary = processor.generate_summary_report(processed_data)
        
        logger.info("Data collection and processing workflow completed successfully")
        
        return {
            'raw_files': raw_files,
            'cleaned_files': cleaned_files,
            'tableau_files': tableau_files,
            'sentiment_files': sentiment_files,
            'summary': summary
        }
        
    except Exception as e:
        logger.error(f"Error in main workflow: {e}")
        raise

def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(description='Twitter Data Collection and Processing')
    parser.add_argument(
        '--mode', 
        choices=['collect', 'schedule', 'analyze'],
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
        default=200,
        help='Number of tweets to collect per topic'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'collect':
        results = collect_and_process_data()
        print("Data collection completed successfully!")
        print(f"Files created: {len(results['tableau_files'])} Tableau files")
        
    elif args.mode == 'schedule':
        scheduler = TwitterAutomationScheduler()
        scheduler.start_scheduled_collection()
        
    elif args.mode == 'analyze':
        # Future: Add analysis-only mode
        print("Analysis mode not implemented yet")

if __name__ == "__main__":
    main()
