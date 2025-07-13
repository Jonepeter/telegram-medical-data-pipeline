# Telegram Data Pipeline

End-to-end data pipeline for analyzing Ethiopian medical businesses from Telegram channels.

## Project Structure

```
telegram_data_pipeline/
├── data/                          # Data storage
│   ├── raw/                      # Raw scraped data
│   └── processed/                # Processed data
├── src/                          # Source code
│   ├── scraping/                 # Data extraction
│   ├── enrichment/               # YOLO object detection
│   ├── api/                      # FastAPI application
│   └── orchestration/            # Dagster pipeline
├── dbt_project/                  # dbt transformations
│   ├── models/                   # dbt models
│   └── tests/                    # dbt tests
└── docker/                       # Docker configurations
```

## Setup

1. **Environment Setup**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# - Telegram API credentials
# - Database passwords
```

2. **Docker Setup**
```bash
# Start services
docker-compose up -d

# Install dependencies locally (optional)
pip install -r requirements.txt
```

3. **Database Setup**
```bash
# Database will be initialized automatically via docker-compose
# Tables are created via init.sql
```

## Usage

### Manual Pipeline Run
```bash
python run_pipeline.py
```

### API Server
```bash
# Start FastAPI server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Access API documentation
http://localhost:8000/docs
```

### Dagster Orchestration
```bash
# Start Dagster UI
dagster dev -f src/orchestration/dagster_pipeline.py

# Access Dagster UI
http://localhost:3000
```

### dbt Operations
```bash
cd dbt_project

# Run transformations
dbt run

# Run tests
dbt test

# Generate documentation
dbt docs generate
dbt docs serve
```

## API Endpoints

- `GET /api/reports/top-products` - Most mentioned products
- `GET /api/channels/{channel_name}/activity` - Channel activity stats
- `GET /api/search/messages?query=keyword` - Search messages
- `GET /api/stats/overview` - Overview statistics

## Pipeline Phases

1. **Extract**: Scrape Telegram channels using Telethon
2. **Load**: Store raw data in PostgreSQL
3. **Transform**: Clean and model data using dbt
4. **Enrich**: Add object detection results using YOLO
5. **Serve**: Expose data via FastAPI

## Data Model

- **Raw Layer**: Unprocessed Telegram data
- **Staging Layer**: Cleaned and typed data
- **Marts Layer**: Star schema with fact and dimension tables
  - `dim_channels`: Channel information
  - `dim_dates`: Date dimension
  - `fct_messages`: Message facts
  - `fct_image_detections`: Object detection facts

## Configuration

Key configuration files:
- `.env`: Environment variables
- `src/config.py`: Application configuration
- `dbt_project/dbt_project.yml`: dbt configuration
- `docker-compose.yml`: Service orchestration