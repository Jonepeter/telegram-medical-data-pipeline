#!/usr/bin/env python3
"""
Main pipeline runner script
"""
import asyncio
import subprocess
import sys
from pathlib import Path
from src.scraping.telegram_scraper import TelegramScraper
from src.scraping.data_loader import DataLoader
from src.enrichment.yolo_detector import YOLODetector
from src.config import TELEGRAM_CHANNELS

async def run_scraping():
    """Run the scraping phase"""
    print("Starting Telegram data scraping...")
    scraper = TelegramScraper()
    
    for channel in TELEGRAM_CHANNELS:
        print(f"Scraping channel: {channel}")
        messages = await scraper.scrape_channel(channel, limit=100)
        scraper.save_to_json(messages, channel)
    
    await scraper.client.disconnect()
    print("Scraping completed!")

def run_loading():
    """Run the data loading phase"""
    print("Loading data to PostgreSQL...")
    loader = DataLoader()
    loader.load_all_json_files()
    print("Data loading completed!")

def run_dbt():
    """Run dbt transformations for the project."""
    import os
    from dotenv import load_dotenv

    # Load environment variables from .env
    load_dotenv()

    # Use a relative path for portability
    dbt_dir = Path(os.path.join(os.getcwd(), "dbt_project"))
    print(f"dbt directory: {dbt_dir}")

    # Check if directory exists
    if not Path(dbt_dir).exists():
        print(f"dbt directory does not exist: {dbt_dir}")
        return

    try:
        # Run dbt debug to check connection before running transformations
        debug_result = subprocess.run(
            "dbt debug",
            cwd=dbt_dir,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        print(debug_result.stdout)
        if debug_result.returncode != 0:
            print("dbt debug failed:")
            print(debug_result.stdout)
            print(debug_result.stderr)
            return
        # Run dbt run
        result = subprocess.run(
            "dbt run",
            shell=True,
            cwd=dbt_dir,
            capture_output=True,
            text=True,
            timeout=300
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"dbt run failed:\n{result.stderr}")
            return

        # Run dbt test
        result = subprocess.run(
            "dbt test",
            shell=True, 
            cwd=dbt_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"dbt test failed:\n{result.stderr}")

        print("dbt transformations completed!")
    except subprocess.TimeoutExpired:
        print("dbt execution timed out")
    except Exception as e:
        print(f"dbt failed: {e}")

def run_enrichment():
    """Run YOLO enrichment"""
    print("Running YOLO enrichment...")
    detector = YOLODetector()
    detector.create_detections_table()
    detector.process_all_images()
    print("YOLO enrichment completed!")

async def main():
    """Run the complete pipeline"""
    print("Starting Telegram Data Pipeline...")
    
    # Phase 1: Scraping
    # await run_scraping()
    
    # Phase 2: Loading
    # run_loading()
    
    # Phase 3: Transformation
    run_dbt()
    
    # Phase 4: Enrichment
    # run_enrichment()
    
    print("Pipeline completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())