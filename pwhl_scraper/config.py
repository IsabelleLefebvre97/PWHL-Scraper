"""
Configuration settings for the PWHL Scraper application.
"""
import os
import logging

# Base directory of the application
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data directory
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Database path
DB_PATH = os.path.join(DATA_DIR, "pwhl_data.db")

# API configuration
API_CONFIG = {
    "HOCKEYTECH_BASE_URL": "https://lscluster.hockeytech.com/feed/",
    "HOCKEYTECH_KEY": "446521baf8c38984",
    "CLIENT_CODE": "pwhl"
}


# Logging configuration
def configure_logging(log_level: str = "INFO") -> None:
    """Configure logging for the application."""
    log_dir = os.path.join(DATA_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "pwhl_scraper.log")

    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }

    level = log_levels.get(log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
