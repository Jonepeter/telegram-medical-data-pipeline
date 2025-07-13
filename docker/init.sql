-- Initialize database schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS marts;

-- Raw data table for telegram messages
CREATE TABLE IF NOT EXISTS raw.telegram_messages (
    id SERIAL PRIMARY KEY,
    message_id BIGINT,
    channel_name VARCHAR(255),
    message_text TEXT,
    message_date TIMESTAMP,
    has_media BOOLEAN,
    media_type VARCHAR(50),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_data JSONB
);