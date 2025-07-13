-- Test for messages with future dates
SELECT 
    message_id,
    channel_name,
    message_date
FROM {{ ref('stg_telegram_messages') }}
WHERE message_date > CURRENT_DATE