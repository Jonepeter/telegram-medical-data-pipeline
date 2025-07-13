-- Test for duplicate messages
SELECT 
    message_id,
    channel_name,
    COUNT(*) as duplicate_count
FROM {{ ref('stg_telegram_messages') }}
GROUP BY message_id, channel_name
HAVING COUNT(*) > 1