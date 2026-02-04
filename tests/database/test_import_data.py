import sqlite3
import unittest
from unittest.mock import patch

import pandas as pd

from database.import_data import import_to_db


class TestImportData(unittest.TestCase):
    def setUp(self):
        """Creates an in-memory db for testing"""
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("""
                          CREATE TABLE entries
                          (
                              date         TEXT,
                              time         TEXT,
                              total_weight INTEGER,
                              water_weight INTEGER,
                              drink        INTEGER,
                              refill_to    INTEGER,
                              notes        TEXT
                          )
                          """)

        self.test_df = pd.DataFrame([{
            "Date": "2026-01-01",
            "Time": "12:00",
            "Total_Weight_g": 500,
            "Water_Weight_g": 100,
            "Drink_g": 20,
            "Refill_To_g": 600
        }])

    def tearDown(self):
        self.conn.close()

    @patch("database.import_data.get_sql_query")
    def test_import_to_db_success(self, mock_get_sql):
        """Mock the SQL query to return a simple insert string"""
        mock_get_sql.return_value = "INSERT INTO entries VALUES (?, ?, ?, ?, ?, ?, ?)"

        imported_count = import_to_db(self.conn, self.test_df)

        self.assertEqual(imported_count, 1)
        cursor = self.conn.execute("SELECT drink FROM entries")
        self.assertEqual(cursor.fetchone()[0], 20)

    @patch("database.import_data.get_sql_query")
    def test_import_with_missing_refill(self, mock_get_sql):
        """Ensure Refill_To_g can be None/NaN without error."""
        mock_get_sql.return_value = "INSERT INTO entries VALUES (?, ?, ?, ?, ?, ?, ?)"

        data = [{
            "Date": "04/02/2026",
            "Time": "01:58",
            "Total_Weight_g": 560,
            "Drink_g": 28
            # Refill_To_g is missing here
        }]
        df = pd.DataFrame(data)

        imported = import_to_db(self.conn, df)
        self.assertEqual(imported, 1)

        row = self.conn.execute("SELECT refill_to FROM entries").fetchone()
        self.assertIsNone(row[0])

    @patch("database.import_data.get_sql_query")
    def test_import_multiple_entries(self, mock_get_sql):
        """Test bulk insertion count."""
        mock_get_sql.return_value = "INSERT INTO entries VALUES (?, ?, ?, ?, ?, ?, ?)"
        df = pd.DataFrame([
            {"Date": "2025/01/01", "Time": "10:00", "Drink_g": 5},
            {"Date": "2025/01/01", "Time": "11:00", "Drink_g": 10}
        ])
        imported = import_to_db(self.conn, df)
        self.assertEqual(imported, 2)


if __name__ == "__main__":
    unittest.main()
