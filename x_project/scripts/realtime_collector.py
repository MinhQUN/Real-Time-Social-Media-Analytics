import threading
import queue
import time
from datetime import datetime
from scripts.data_collector import TwitterDataCollector
from scripts.data_processor import TwitterDataProcessor

class RealTimeCollector:
    def __init__(self):
        self.data_queue = queue.Queue()
        self.collector = TwitterDataCollector()
        self.processor = TwitterDataProcessor()
        self.running = False
        
    def continuous_collect(self, topic):
        """Continuously collect data for a topic and immediately process it"""
        while self.running:
            try:
                # Collect small batch (10-20 tweets)
                df = self.collector.collect_tweets_for_topic(topic, count=20)
                
                if not df.empty:
                    # Immediately save raw data
                    raw_files = self.collector.save_raw_data({topic: df})
                    
                    # Process and save to Tableau immediately
                    processed = self.processor.process_topic_data(df, topic)
                    tableau_files = self.processor.save_tableau_data({topic: processed})
                    
                    print(f"✅ {topic}: Collected {len(df)} tweets, saved to {tableau_files.get(topic, 'N/A')}")
                
                # Wait based on collection frequency
                settings = COLLECTION_SETTINGS.get(topic, {})
                if settings.get('collection_frequency') == 'every_30_minutes':
                    time.sleep(1800)  # 30 minutes
                else:
                    time.sleep(3600)  # 1 hour default
                    
            except Exception as e:
                print(f"Error in continuous collection for {topic}: {e}")
                time.sleep(300)  # 5 minute pause on error

    def start_realtime_collection(self):
        """Start real-time collection threads for all topics"""
        self.running = True
        threads = []
        
        for topic in ['technology', 'stock_market', 'sports']:
            thread = threading.Thread(target=self.continuous_collect, args=(topic,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
            print(f"🚀 Started real-time collection for {topic}")
        
        return threads

    def stop_collection(self):
        """Stop all collection threads"""
        self.running = False
        print("🛑 Stopping real-time collection...")
