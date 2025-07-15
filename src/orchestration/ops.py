from dagster import op, get_dagster_logger
from src.scraping.telegram_scraper import TelegramScraper
from src.scraping.data_loader import DataLoader
from src.enrichment.yolo_detector import YOLODetector
import asyncio
import os
import subprocess

@op
def scrape_telegram_data_op():
    logger = get_dagster_logger()
    logger.info("Starting Telegram data scraping")
    
    async def run_scraper():
        scraper = TelegramScraper()
        from src.config import TELEGRAM_CHANNELS
        
        for channel in TELEGRAM_CHANNELS:
            messages = await scraper.scrape_channel(channel, limit=100)
            scraper.save_to_json(messages, channel)
        
        await scraper.client.disconnect()
    
    asyncio.run(run_scraper())

@op
def load_raw_to_postgres_op():
    logger = get_dagster_logger()
    logger.info("Loading raw data to PostgreSQL")
    
    loader = DataLoader()
    loader.load_all_json_files()

@op
def run_dbt_transformations_op():
    logger = get_dagster_logger()
    logger.info("Running dbt transformations")
    
    os.chdir("dbt_project")
    try:
        subprocess.run(["dbt run"], check=True)
        subprocess.run(["dbt test"], check=True)
    finally:
        os.chdir("..")

@op
def run_yolo_enrichment_op():
    logger = get_dagster_logger()
    logger.info("Running YOLO enrichment")
    
    detector = YOLODetector()
    detector.create_detections_table()
    detector.process_all_images()

