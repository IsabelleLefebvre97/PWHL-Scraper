"""
Database management utilities for PWHL Scraper.

This module provides functions for database setup, connection management,
and query execution.
"""

import os
import sqlite3
import logging
from typing import List, Dict, Any, Optional, Tuple

from pwhl_scraper.database.models import DB_SCHEMA
from pwhl_scraper.config import DB_PATH, DATA_DIR

logger = logging.getLogger(__name__)


def create_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Create a connection to the SQLite database.

    Args:
        db_path: Path to database file. If None, uses the default path from config.

    Returns:
        Database connection object

    Raises:
        sqlite3.Error: If connection fails
    """
    if db_path is None:
        db_path = DB_PATH

    try:
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Enable foreign key constraints
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise


def get_db_connection(db_path: Optional[str] = None):
    """Get database connection as a context manager."""
    conn = create_connection(db_path)
    try:
        yield conn
    finally:
        conn.close()


def execute_query(conn: sqlite3.Connection, query: str, params: Optional[Tuple] = None) -> int:
    """
    Execute a SQL query and return the number of affected rows.

    Args:
        conn: Database connection
        query: SQL query to execute
        params: Query parameters

    Returns:
        Number of affected rows

    Raises:
        sqlite3.Error: If query execution fails
    """
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.rowcount
    except sqlite3.Error as e:
        logger.error(f"Query execution error: {e}")
        logger.debug(f"Query: {query}")
        if params:
            logger.debug(f"Parameters: {params}")
        conn.rollback()
        raise


def execute_many(conn: sqlite3.Connection, query: str, params_list: List[Tuple]) -> int:
    """
    Execute a SQL query with multiple parameter sets.

    Args:
        conn: Database connection
        query: SQL query to execute
        params_list: List of parameter tuples

    Returns:
        Number of affected rows

    Raises:
        sqlite3.Error: If query execution fails
    """
    try:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
        return cursor.rowcount
    except sqlite3.Error as e:
        logger.error(f"Executemany error: {e}")
        logger.debug(f"Query: {query}")
        logger.debug(f"Parameter count: {len(params_list)}")
        conn.rollback()
        raise


def with_transaction(func):
    """Decorator to execute a function within a transaction."""

    def wrapper(conn, *args, **kwargs):
        cursor = conn.cursor()
        try:
            cursor.execute("BEGIN TRANSACTION")
            result = func(conn, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise

    return wrapper


def fetch_all(conn: sqlite3.Connection, query: str, params: Optional[Tuple] = None) -> List[Tuple]:
    """
    Execute a SQL query and fetch all results.

    Args:
        conn: Database connection
        query: SQL query to execute
        params: Query parameters

    Returns:
        List of result rows

    Raises:
        sqlite3.Error: If query execution fails
    """
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Query error: {e}")
        logger.debug(f"Query: {query}")
        if params:
            logger.debug(f"Parameters: {params}")
        raise


def fetch_one(conn: sqlite3.Connection, query: str, params: Optional[Tuple] = None) -> Optional[Tuple]:
    """
    Execute a SQL query and fetch the first result.

    Args:
        conn: Database connection
        query: SQL query to execute
        params: Query parameters

    Returns:
        First result row or None if no results

    Raises:
        sqlite3.Error: If query execution fails
    """
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchone()
    except sqlite3.Error as e:
        logger.error(f"Query error: {e}")
        logger.debug(f"Query: {query}")
        if params:
            logger.debug(f"Parameters: {params}")
        raise


def create_table(conn: sqlite3.Connection, table_name: str, schema: str) -> None:
    """
    Create a table if it doesn't exist.

    Args:
        conn: Database connection
        table_name: Name of the table to create
        schema: SQL schema definition for the table

    Raises:
        sqlite3.Error: If table creation fails
    """
    try:
        cursor = conn.cursor()
        cursor.execute(schema)
        conn.commit()
        logger.info(f"Table {table_name} created or already exists")
    except sqlite3.Error as e:
        logger.error(f"Table creation error for {table_name}: {e}")
        conn.rollback()
        raise


def create_indexes(conn: sqlite3.Connection, indexes: List[str]) -> None:
    """
    Create indexes if they don't exist.

    Args:
        conn: Database connection
        indexes: List of SQL index creation statements

    Raises:
        sqlite3.Error: If index creation fails
    """
    cursor = conn.cursor()
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
            logger.debug(f"Index created or already exists: {index_sql}")
        except sqlite3.Error as e:
            logger.error(f"Index creation error: {e}")
            logger.debug(f"Index SQL: {index_sql}")
            # Continue with other indexes even if one fails
    conn.commit()


def setup_database(db_path: Optional[str] = None) -> None:
    """
    Set up the database schema.

    Creates all tables and indexes defined in the schema.

    Args:
        db_path: Path to database file. If None, uses the default path from config.

    Raises:
        sqlite3.Error: If database setup fails
    """
    if db_path is None:
        db_path = DB_PATH

    logger.info(f"Setting up database at {db_path}")

    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Connect to database
    conn = create_connection(db_path)
    try:
        # Create tables
        for table_name, table_info in DB_SCHEMA["tables"].items():
            create_table(conn, table_name, table_info["schema"])
            logger.info(f"Created table: {table_name}")

        # Create indexes
        for index_group, index_list in DB_SCHEMA["indexes"].items():
            logger.info(f"Creating indexes for {index_group}")
            create_indexes(conn, index_list)

        logger.info("Database setup complete")
    except sqlite3.Error as e:
        logger.error(f"Database setup failed: {e}")
        raise
    finally:
        conn.close()


def reset_database(db_path: Optional[str] = None, confirm: bool = False) -> None:
    """
    Reset the database by dropping all tables and recreating them.

    CAUTION: This will delete all data in the database!

    Args:
        db_path: Path to database file. If None, uses the default path from config.
        confirm: Must be True to confirm the reset action

    Raises:
        ValueError: If confirm is not True
        sqlite3.Error: If database reset fails
    """
    if not confirm:
        raise ValueError("Database reset must be explicitly confirmed by setting confirm=True")

    if db_path is None:
        db_path = DB_PATH

    logger.warning(f"Resetting database at {db_path}")

    # If the database file exists, delete it
    if os.path.exists(db_path):
        os.remove(db_path)
        logger.info(f"Deleted existing database file: {db_path}")

    # Set up a new database
    setup_database(db_path)
    logger.info("Database reset complete")


def get_tables(conn: sqlite3.Connection) -> List[str]:
    """
    Get a list of all tables in the database.

    Args:
        conn: Database connection

    Returns:
        List of table names
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    return tables


def get_table_info(conn: sqlite3.Connection, table_name: str) -> List[Dict[str, Any]]:
    """
    Get information about a table's columns.

    Args:
        conn: Database connection
        table_name: Name of the table

    Returns:
        List of dictionaries with column information
    """
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = []
    for row in cursor.fetchall():
        columns.append({
            "cid": row[0],
            "name": row[1],
            "type": row[2],
            "notnull": row[3],
            "default": row[4],
            "pk": row[5]
        })
    return columns


def get_row_count(conn: sqlite3.Connection, table_name: str) -> int:
    """
    Get the number of rows in a table.

    Args:
        conn: Database connection
        table_name: Name of the table

    Returns:
        Number of rows in the table
    """
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]


def vacuum_database(conn: sqlite3.Connection) -> None:
    """
    Vacuum the database to optimize storage.

    Args:
        conn: Database connection
    """
    conn.execute("VACUUM")
    logger.info("Database vacuumed")
