"""
Database management for PWHL Scraper.
"""

from pwhl_scraper.database.db_manager import (
    setup_database,
    create_connection,
    execute_query,
    execute_many,
    fetch_all,
    fetch_one
)

from pwhl_scraper.database.models import get_table_schema

__all__ = [
    'setup_database',
    'create_connection',
    'execute_query',
    'execute_many',
    'fetch_all',
    'fetch_one',
    'get_table_schema'
]
