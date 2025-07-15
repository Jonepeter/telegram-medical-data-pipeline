
from dagster import ScheduleDefinition
from src.orchestration.jobs import telegram_pipeline_job

daily_schedule = ScheduleDefinition(
    job=telegram_pipeline_job,
    cron_schedule="0 2 * * *",
    name="daily_telegram_pipeline",
)