# scripts/automation_scheduler.py
import schedule
import time
import logging
from config import COLLECTION_SETTINGS
from main import collect_and_process_data

class TwitterAutomationScheduler:
    def __init__(self):
        logging.basicConfig(
            filename="logs/scheduler.log",
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def job(self):
        """Invoke full pipeline."""
        self.logger.info("Scheduler triggered pipeline run")
        try:
            collect_and_process_data()
            self.logger.info("Pipeline run successful")
        except Exception as e:
            self.logger.error(f"Pipeline run failed: {e}")

    def start_scheduled_collection(self):
        """Schedule jobs per topic settings."""
        # Example: technology hourly, stock_market every 30m, sports every 1h
        settings = COLLECTION_SETTINGS
        schedule.every().hour.do(self.job)                              # technology
        schedule.every(15).minutes.do(self.job)                         # stock_market
        schedule.every(1).hours.do(self.job)                            # sports

        self.logger.info("Scheduler started")
        while True:
            schedule.run_pending()
            time.sleep(1)
