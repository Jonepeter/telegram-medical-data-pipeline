# Telegram Medical Data Pipeline

## Overview

This project implements a comprehensive end-to-end data pipeline for analyzing medical business data from Ethiopian Telegram channels. The pipeline extracts messages and media from Telegram channels, processes the data using dbt transformations, enriches it with YOLO object detection, and exposes insights through a FastAPI application.

## 🚀 Key Features

- **Automated Data Extraction**: Scrapes Telegram channels using Telethon with robust error handling
- **Data Storage**: PostgreSQL database with raw and processed data layers
- **Data Transformation**: Clean and model data using dbt with comprehensive testing
- **Image Analysis**: YOLO object detection for medical product identification
- **REST API**: FastAPI application for data access and analytics
- **Pipeline Orchestration**: Dagster for workflow management
- **Containerized Deployment**: Docker and Docker Compose for easy deployment
- **Data Quality**: Comprehensive testing and validation at every stage

## 📁 Project Structure

```
telegram-medical-data-pipeline/
├── data/                          # Data storage
│   ├── raw/                      # Raw scraped data
│   │   ├── telegram_messages/    # JSON message files
│   │   └── media/               # Downloaded images/videos
│   └── processed/               # Processed data outputs
├── src/                         # Source code
│   ├── scraping/               # Telegram data extraction
│   ├── enrichment/             # YOLO object detection
│   ├── api/                    # FastAPI application
│   ├── orchestration/          # Dagster pipeline
│   └── models/                 # Data models
├── dbt_project/                # dbt transformations
│   ├── models/                 # dbt models
│   │   ├── staging/           # Staging layer
│   │   └── marts/             # Data marts
│   └── tests/                 # Custom dbt tests
├── docker/                     # Docker configurations
├── notebooks/                  # Jupyter notebooks for analysis
└── logs/                      # Application logs
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Telegram API credentials
- PostgreSQL (via Docker)

### 1. Environment Configuration

```bash
# Clone the repository
git clone <repository-url>
cd telegram-medical-data-pipeline

# Copy environment template
cp .env.example .env
```

**Configure your `.env` file with:**
- **Telegram API credentials** (get from https://my.telegram.org/apps)
- **Database passwords** (use strong passwords)
- **Channel names** to scrape

```bash
# Example .env configuration
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH="your_api_hash_here"
TELEGRAM_PHONE="+your_phone_number_here"
TELEGRAM_CHANNELS="@channel1,@channel2,@channel3"

DB_HOST=localhost
DB_PORT=5432
DB_NAME=telegram_data
DB_USER=db_user
DB_PASSWORD=your_secure_password_here
```

### 2. Docker Setup (Recommended)

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Local Development Setup (Optional)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p data/raw/telegram_messages data/raw/media data/processed logs
```

### 4. Database Setup

```bash
# Database initialization happens automatically via Docker
# Tables are created through dbt migrations

# Manual database setup (if needed)
psql -h localhost -p 5432 -U db_user -d telegram_data -f docker/init.sql
```

### 5. dbt Configuration

```bash
cd dbt_project

# Copy profiles template
cp profiles.yml.example profiles.yml

# Test dbt connection
dbt debug

# Run initial setup
dbt deps
dbt run
dbt test
```

## 🚀 Usage Guide

### Running the Complete Pipeline

```bash
# Option 1: Using the main pipeline script
python run_pipeline.py

# Option 2: Using Docker Compose
docker-compose up pipeline

# Option 3: Using Dagster (recommended for production)
dagster dev -f src/orchestration/dagster_pipeline.py
# Access Dagster UI at http://localhost:3000
```

### Individual Components

#### 1. Data Scraping
```bash
# Scrape specific channels
python -m src.scraping.telegram_scraper

# Scrape with custom parameters
python -c "
from src.scraping.telegram_scraper import TelegramScraper
import asyncio

async def main():
    scraper = TelegramScraper()
    messages = await scraper.scrape_channel('@channel_name', limit=500)
    scraper.save_to_json(messages, 'channel_name')

asyncio.run(main())
"
```

#### 2. Data Transformation (dbt)
```bash
cd dbt_project

# Run all models
dbt run

# Run specific models
dbt run --select staging
dbt run --select marts

# Run tests
dbt test

# Generate and serve documentation
dbt docs generate
dbt docs serve --port 8080
```

#### 3. Object Detection
```bash
# Process images with YOLO
python -m src.enrichment.yolo_detector

# Process specific directory
python -c "
from src.enrichment.yolo_detector import YOLODetector
detector = YOLODetector()
detector.process_images('data/raw/media/channel_name/')
"
```

#### 4. API Server
```bash
# Start FastAPI server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Access API documentation
# http://localhost:8000/docs
# http://localhost:8000/redoc
```

## 📊 API Endpoints

### Analytics Endpoints
- `GET /api/reports/top-products` - Most mentioned products across channels
- `GET /api/channels/{channel_name}/activity` - Channel activity statistics
- `GET /api/channels/{channel_name}/messages` - Recent messages from channel
- `GET /api/search/messages?query=keyword` - Search messages by keyword
- `GET /api/stats/overview` - Overall pipeline statistics

### Data Access Endpoints
- `GET /api/messages/{message_id}` - Get specific message details
- `GET /api/detections/{message_id}` - Get object detection results
- `GET /api/channels` - List all monitored channels

### Health and Monitoring
- `GET /health` - Application health check
- `GET /api/pipeline/status` - Pipeline execution status

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run dbt tests
cd dbt_project
dbt test

# Run with coverage
pytest --cov=src tests/
```

## 📈 Data Model

### Raw Layer
- **telegram_messages**: Unprocessed message data from Telegram
- **image_detections**: Raw YOLO detection results

### Staging Layer
- **stg_telegram_messages**: Cleaned and standardized messages
- **stg_image_detections**: Processed detection results

### Marts Layer (Star Schema)
- **dim_channels**: Channel dimension with metadata
- **dim_dates**: Date dimension for time-based analysis
- **fct_messages**: Message facts with metrics
- **fct_image_detections**: Object detection facts

## 🔧 Configuration

### Key Configuration Files
- `.env`: Environment variables and secrets
- `src/config.py`: Application configuration
- `dbt_project/dbt_project.yml`: dbt project settings
- `docker-compose.yml`: Service orchestration
- `dbt_project/profiles.yml`: Database connections

### Environment Variables
```bash
# Telegram Configuration
TELEGRAM_API_ID=          # Your Telegram API ID
TELEGRAM_API_HASH=        # Your Telegram API Hash
TELEGRAM_PHONE=           # Your phone number
TELEGRAM_CHANNELS=        # Comma-separated channel list

# Database Configuration
DB_HOST=                  # Database host
DB_PORT=                  # Database port
DB_NAME=                  # Database name
DB_USER=                  # Database user
DB_PASSWORD=              # Database password

# API Configuration
API_HOST=                 # API server host
API_PORT=                 # API server port
```

## 🚨 Troubleshooting

### Common Issues

1. **Telegram Authentication Errors**
   ```bash
   # Clear session and re-authenticate
   rm *.session
   python -m src.scraping.telegram_scraper
   ```

2. **Database Connection Issues**
   ```bash
   # Check database status
   docker-compose ps postgres
   
   # Reset database
   docker-compose down -v
   docker-compose up -d postgres
   ```

3. **dbt Connection Problems**
   ```bash
   # Test dbt connection
   cd dbt_project
   dbt debug
   
   # Check profiles configuration
   cat profiles.yml
   ```

4. **Docker Issues**
   ```bash
   # Rebuild containers
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

### Logs and Monitoring

```bash
# View application logs
tail -f logs/telegram_scraper.log
tail -f logs/api.log

# Docker logs
docker-compose logs -f app
docker-compose logs -f postgres

# dbt logs
cd dbt_project
cat logs/dbt.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Telegram API for data access
- dbt for data transformation framework
- YOLO for object detection capabilities
- FastAPI for API framework
- Dagster for pipeline orchestration