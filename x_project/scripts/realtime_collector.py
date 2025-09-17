# scripts/realtime_collector.py
"""
Real-time continuous data collection and processing
"""

import threading
import queue
import time
from datetime import datetime
import logging

from scripts.data_collector import TwitterDataCollector
from scripts.data_processor import TwitterDataProcessor
from config import COLLECTION_SETTINGS

class RealTimeCollector:
    def __init__(self):
        self.data_queue = queue.Queue()
        self.collector = TwitterDataCollector()
        self.processor = TwitterDataProcessor()
        self.running = False
        self.logger = logging.getLogger(__name__)
        
    def continuous_collect(self, topic):
        """Continuously collect data for a topic and immediately process it"""
        while self.running:
            try:
                # Collect small batch (10-20 tweets to manage quota)
                df = self.collector.collect_tweets_for_topic(topic, count=15)
                
                if not df.empty:
                    # Immediately save raw data
                    raw_files = self.collector.save_raw_data({topic: df})
                    
                    # Process and save to Tableau immediately
                    processed = self.processor.process_topic_data(df, topic)
                    tableau_files = self.processor.save_tableau_data({topic: processed})
                    
                    print(f"✅ {topic}: Collected {len(df)} tweets, saved to {tableau_files.get(topic, 'N/A')}")
                    self.logger.info(f"Real-time collection: {topic} - {len(df)} tweets processed")
                else:
                    print(f"⚠️ {topic}: No new tweets found")
                
                # Wait based on collection frequency from config
                settings = COLLECTION_SETTINGS.get(topic, {})
                frequency = settings.get('collection_frequency', 'every_hour')
                
                if frequency == 'every_30_minutes':
                    sleep_time = 1800  # 30 minutes
                elif frequency == 'every_2_hours':
                    sleep_time = 7200  # 2 hours
                else:  # every_hour default
                    sleep_time = 3600  # 1 hour
                
                print(f"💤 {topic}: Sleeping for {sleep_time//60} minutes...")
                time.sleep(sleep_time)
                    
            except Exception as e:
                print(f"Error in continuous collection for {topic}: {e}")
                self.logger.error(f"Real-time collection error for {topic}: {e}")
                time.sleep(300)  # 5 minute pause on error

    def start_realtime_collection(self):
        """Start real-time collection threads for all topics"""
        self.running = True
        threads = []
        
        topics = list(COLLECTION_SETTINGS.keys())
        
        for topic in topics:
            thread = threading.Thread(target=self.continuous_collect, args=(topic,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            print(f"🚀 Started real-time collection thread for {topic}")
            time.sleep(2)  # Stagger thread starts
        
        return threads

    def stop_collection(self):
        """Stop all collection threads"""
        self.running = False
        print("🛑 Stopping real-time collection...")
