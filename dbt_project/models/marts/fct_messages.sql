{{ config(materialized='table') }}

SELECT 
    m.message_id,
    c.channel_id,
    DATE(m.message_date) as date_day,
    m.message_text,
    m.message_length,
    m.has_media,
    m.media_type,
    m.mentions_price,
    COALESCE(d.detection_count, 0) as detection_count,
    m.scraped_at
FROM {{ ref('stg_telegram_messages') }} m
LEFT JOIN {{ ref('dim_channels') }} c ON m.channel_name = c.channel_name
LEFT JOIN (
    SELECT 
        message_id,
        COUNT(*) as detection_count
    FROM {{ ref('stg_image_detections') }}
    GROUP BY message_id
) d ON m.message_id = d.message_id