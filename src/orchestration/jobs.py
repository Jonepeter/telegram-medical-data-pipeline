from dagster import job, schedule, DefaultScheduleStatus

from src.orchestration.ops import (
    scrape_telegram_data_op,
    load_raw_to_postgres_op,
    run_dbt_transformations_op,
    run_yolo_enrichment_op,
)

@job
def telegram_pipeline_job():
    raw_data = scrape_telegram_data_op()
    loaded_data = load_raw_to_postgres_op(raw_data)
    transformed_data = run_dbt_transformations_op(loaded_data)
    run_yolo_enrichment_op(transformed_data)



