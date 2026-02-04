import unittest
from pathlib import Path

import pandas as pd

from database.import_data import init_db, import_to_db


class TestDatabaseIntegration(unittest.TestCase):
    def setUp(self):
        """Use a real file path for integration, but keep it temporary."""
        self.test_db_path = Path("test_maple_temp.db")
        if self.test_db_path.exists():
            self.test_db_path.unlink()

    def tearDown(self):
        if self.test_db_path.exists():
            self.test_db_path.unlink()

    def test_init_and_import_with_real_sql_files(self):
        """
        Runs the database with real SQL files.
            1. Test init_db (verifies schema.sql exists and is valid) and verify settings table was populated by init_db
            2. Test import_to_db (verifies insert_entry.sql exists and is valid)
            3. Final verification of data persistence
        """
        conn = init_db(self.test_db_path)

        cursor = conn.execute("SELECT value FROM settings WHERE key = 'bowl_weight'")
        self.assertEqual(cursor.fetchone()[0], "423")

        df = pd.DataFrame([{
            "Date": "2026/02/25",
            "Time": "08:00",
            "Total_Weight_g": 500,
            "Water_Weight_g": 100,
            "Drink_g": 50,
            "Refill_To_g": None
        }])

        count = import_to_db(conn, df)
        self.assertEqual(count, 1)

        row = conn.execute("SELECT drink, refill_to FROM entries").fetchone()
        self.assertEqual(row[0], 50)
        self.assertIsNone(row[1])

        conn.close()
