{{ config(materialized='table') }}

SELECT 
    ROW_NUMBER() OVER (ORDER BY channel_name) as channel_id,
    channel_name,
    COUNT(*) as total_messages,
    MIN(message_date) as first_message_date,
    MAX(message_date) as last_message_date,
    COUNT(CASE WHEN has_media THEN 1 END) as messages_with_media,
    ROUND(AVG(message_length), 2) as avg_message_length
FROM {{ ref('stg_telegram_messages') }}
GROUP BY channel_name