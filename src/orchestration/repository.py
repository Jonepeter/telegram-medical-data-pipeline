from dagster import Definitions
from src.orchestration.jobs import telegram_pipeline_job
from src.orchestration.schedules import daily_schedule

defs = Definitions(
    jobs=[telegram_pipeline_job],
    schedules=[daily_schedule],
)
