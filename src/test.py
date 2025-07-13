import os
import sys
import importlib

system_path = os.path.abspath('..')
if system_path not in sys.path:
    sys.path.append(system_path)

from src.run_pipeline import run_scraping