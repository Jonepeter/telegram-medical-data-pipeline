{{ config(materialized='view') }}

SELECT 
    id as detection_id,
    message_id,
    image_path,
    detected_class,
    confidence_score,
    bbox_coordinates,
    created_at
FROM {{ source('raw', 'image_detections') }}
WHERE confidence_score >= 0.5