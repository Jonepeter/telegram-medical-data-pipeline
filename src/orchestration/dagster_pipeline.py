from dagster import op, job, schedule, DefaultScheduleStatus, get_dagster_logger
import asyncio
import subprocess
import os
from src.scraping.telegram_scraper import TelegramScraper
from src.scraping.data_loader import DataLoader
from src.enrichment.yolo_detector import YOLODetector

@op
def scrape_telegram_data():
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
def load_raw_to_postgres():
    logger = get_dagster_logger()
    logger.info("Loading raw data to PostgreSQL")
    
    loader = DataLoader()
    loader.load_all_json_files()

@op
def run_dbt_transformations():
    logger = get_dagster_logger()
    logger.info("Running dbt transformations")
    
    os.chdir("dbt_project")
    try:
        subprocess.run(["dbt", "run"], check=True)
        subprocess.run(["dbt", "test"], check=True)
    finally:
        os.chdir("..")

@op
def run_yolo_enrichment():
    logger = get_dagster_logger()
    logger.info("Running YOLO enrichment")
    
    detector = YOLODetector()
    detector.create_detections_table()
    detector.process_all_images()

@job
def telegram_pipeline():
    raw_data = scrape_telegram_data()
    loaded_data = load_raw_to_postgres(raw_data)
    transformed_data = run_dbt_transformations(loaded_data)
    run_yolo_enrichment(transformed_data)

@schedule(
    job=telegram_pipeline,
    cron_schedule="0 2 * * *",
    default_status=DefaultScheduleStatus.STOPPED
)
def daily_telegram_schedule():
    return {}