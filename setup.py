from setuptools import setup, find_packages

setup(
    name="telegram-data-pipeline",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "python-dotenv>=1.0.0",
        "psycopg2-binary>=2.9.7",
        "sqlalchemy>=2.0.21",
        "telethon>=1.29.3",
        "dbt-core>=1.6.6",
        "dbt-postgres>=1.6.6",
        "ultralytics>=8.0.196",
        "opencv-python>=4.8.1.78",
        "Pillow>=10.0.1",
        "fastapi>=0.103.2",
        "uvicorn>=0.23.2",
        "pydantic>=2.4.2",
        "dagster>=1.5.1",
        "dagster-webserver>=1.5.1",
        "dagster-postgres>=0.21.1",
        "requests>=2.31.0",
        "pandas>=2.1.1",
        "numpy>=1.25.2"
    ],
    python_requires=">=3.13",
    author="Kara Solutions",
    description="End-to-end data pipeline for Telegram medical business analysis",
)