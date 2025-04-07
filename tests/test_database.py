import unittest
import os
import sqlite3
from unittest.mock import patch, MagicMock
import tempfile

from pwhl_scraper.database.db_manager import (
    create_connection, execute_query, fetch_all, fetch_one,
    setup_database, create_table
)


class TestDatabase(unittest.TestCase):

    def setUp(self):
        # Create a temporary database file for testing
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp()
        self.conn = create_connection(self.temp_db_path)

    def tearDown(self):
        # Close and remove the temporary database
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        os.close(self.temp_db_fd)
        os.unlink(self.temp_db_path)

    def test_create_connection(self):
        # Test that connection is created successfully
        conn = create_connection(self.temp_db_path)
        self.assertIsInstance(conn, sqlite3.Connection)
        conn.close()

    def test_execute_query(self):
        # Test executing a simple query
        create_table(self.conn, "test_table",
                     "CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)")

        # Insert data
        result = execute_query(
            self.conn,
            "INSERT INTO test_table (name) VALUES (?)",
            ("Test Name",)
        )

        # Verify data was inserted
        self.assertEqual(result, 1)  # One row affected

        # Query the data
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM test_table WHERE id = 1")
        name = cursor.fetchone()[0]
        self.assertEqual(name, "Test Name")

    def test_fetch_all(self):
        # Create a test table and insert data
        create_table(self.conn, "test_fetch",
                     "CREATE TABLE IF NOT EXISTS test_fetch (id INTEGER PRIMARY KEY, value TEXT)")

        execute_query(self.conn, "INSERT INTO test_fetch (value) VALUES (?)", ("Value 1",))
        execute_query(self.conn, "INSERT INTO test_fetch (value) VALUES (?)", ("Value 2",))

        # Test fetch_all
        results = fetch_all(self.conn, "SELECT * FROM test_fetch ORDER BY id")

        # Verify results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].value, "Value 1")
        self.assertEqual(results[1].value, "Value 2")

    def test_fetch_one(self):
        # Create a test table and insert data
        create_table(self.conn, "test_fetch_one",
                     "CREATE TABLE IF NOT EXISTS test_fetch_one (id INTEGER PRIMARY KEY, value TEXT)")

        execute_query(self.conn, "INSERT INTO test_fetch_one (value) VALUES (?)", ("Single Value",))

        # Test fetch_one
        result = fetch_one(self.conn, "SELECT value FROM test_fetch_one WHERE id = 1")

        # Verify result
        self.assertEqual(result[0], "Single Value")

    @patch('pwhl_scraper.database.db_manager.create_connection')
    def test_setup_database(self, mock_create_connection):
        # Mock the connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_create_connection.return_value = mock_conn

        # Call setup_database
        setup_database(self.temp_db_path)

        # Verify connection was created
        mock_create_connection.assert_called_once_with(self.temp_db_path)
        # Verify some tables were created (just check a few)
        self.assertGreater(mock_cursor.execute.call_count, 0)


if __name__ == '__main__':
    unittest.main()
