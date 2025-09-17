# scripts/automation_scheduler.py

import schedule
import time
import logging
import os
from datetime import datetime
from config import COLLECTION_SETTINGS, LOGS_DIR

class TwitterAutomationScheduler:
    """
    Automates scheduled triggering of the main data pipeline defined in main.py.
    """

    def __init__(self):
        # Setup scheduler logging
        log_dir = os.path.join(LOGS_DIR, 'scheduler_logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f'scheduler_{datetime.now():%Y%m%d}.log')
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        self.logger = logging.getLogger(__name__)

    def job(self):
        """
        Trigger the main pipeline defined in main.py without direct imports,
        to avoid circular dependencies.
        """
        self.logger.info("Scheduler triggering main pipeline")
        try:
            # Import inside method to prevent circular import
            from main import collect_and_process_data
            collect_and_process_data()
            self.logger.info("Main pipeline run successful")
        except Exception as e:
            self.logger.error(f"Main pipeline run failed: {e}", exc_info=True)

    def start_scheduled_collection(self):
        """
        Schedule the job according to COLLECTION_SETTINGS without re-implementing pipeline logic.
        """
        settings = COLLECTION_SETTINGS

        # Schedule by topic frequencies
        if 'technology' in settings:
            freq = settings['technology']['collection_frequency']
            if freq == 'every_hour':
                schedule.every().hour.do(self.job)
            # add more patterns as needed

        if 'stock_market' in settings:
            freq = settings['stock_market']['collection_frequency']
            if freq == 'every_30_minutes':
                schedule.every(30).minutes.do(self.job)

        if 'sports' in settings:
            freq = settings['sports']['collection_frequency']
            if freq == 'every_2_hours':
                schedule.every(2).hours.do(self.job)

        self.logger.info("Scheduler started with configured intervals")

        while True:
            schedule.run_pending()
            time.sleep(1)
