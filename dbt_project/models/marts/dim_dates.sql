{{ config(materialized='table', schema = 'mart') }}

WITH date_spine AS (
    SELECT DISTINCT DATE(message_date) as date_day
    FROM {{ ref('stg_telegram_messages') }}
    WHERE message_date IS NOT NULL
)

SELECT 
    date_day,
    EXTRACT(YEAR FROM date_day) as year,
    EXTRACT(MONTH FROM date_day) as month,
    EXTRACT(DAY FROM date_day) as day,
    EXTRACT(DOW FROM date_day) as day_of_week,
    TO_CHAR(date_day, 'Day') as day_name,
    TO_CHAR(date_day, 'Month') as month_name,
    EXTRACT(QUARTER FROM date_day) as quarter,
    CASE WHEN EXTRACT(DOW FROM date_day) IN (0, 6) THEN true ELSE false END as is_weekend
FROM date_spine