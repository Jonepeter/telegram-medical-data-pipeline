{{ config(materialized='table') }}

SELECT 
    d.detection_id,
    d.message_id,
    c.channel_id,
    DATE(m.message_date) as date_day,
    d.detected_class,
    d.confidence_score,
    d.created_at
FROM {{ ref('stg_image_detections') }} d
LEFT JOIN {{ ref('stg_telegram_messages') }} m ON d.message_id = m.message_id
LEFT JOIN {{ ref('dim_channels') }} c ON m.channel_name = c.channel_name