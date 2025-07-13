{{ config(materialized='view') }}

SELECT 
    message_id,
    channel_name,
    TRIM(message_text) as message_text,
    message_date::timestamp as message_date,
    has_media,
    media_type,
    scraped_at::timestamp as scraped_at,
    LENGTH(TRIM(message_text)) as message_length,
    CASE 
        WHEN message_text ILIKE '%price%' OR message_text ILIKE '%cost%' OR message_text ILIKE '%birr%' THEN true
        ELSE false
    END as mentions_price,
    raw_data
FROM {{ source('raw', 'telegram_messages') }}
WHERE message_text IS NOT NULL 
    AND message_text != ''