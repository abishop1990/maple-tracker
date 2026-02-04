import unittest

from database.data_parse import parse_kitty_data, read_raw_data
from database.path_manager import PathManager


class TestReadRawData(unittest.TestCase):
    def setUp(self):
        self.data_path = PathManager.TEST_RESOURCES_DIR / "raw-data.txt"

    def test_read_raw_data(self):
        data = read_raw_data(self.data_path)
        self.assertEqual(type(data), str)

        data_split = data.strip().split("\n")
        self.assertEqual(len(data_split), 14)

    def test_read_raw_data_invalid(self):
        self.assertRaises(FileNotFoundError, read_raw_data, "inexistent/data/path/raw-data.txt")


class TestDataParse(unittest.TestCase):
    def setUp(self):
        self.raw_sample = (
            "25/01/2026 - 01:41 -> 574g total | 151g water |\n"
            "25/01/2026 - 22:16 -> 514g total |  91g water | 17g drink |\n"
            "26/01/2026 - 16:11 -> 540g total | 117g water | 56g drink | 630g refill"
        )
        self.data_path = PathManager.TEST_RESOURCES_DIR / "raw-data.txt"

    def test_parse_kitty_data_columns(self):
        df = parse_kitty_data(self.raw_sample)
        self.assertIn("Date", df.columns)
        self.assertIn("Time", df.columns)
        self.assertIn("Drink_g", df.columns)
        self.assertIn("Water_Weight_g", df.columns)
        self.assertIn("Total_Weight_g", df.columns)
        self.assertIn("Refill_To_g", df.columns)
        self.assertEqual(len(df), 3)

    def test_parse_kitty_data_with_file(self):
        raw_data = read_raw_data(self.data_path)
        df = parse_kitty_data(raw_data)
        self.assertEqual(len(df), 13)

    def test_parse_values(self):
        """Check specific row (3rd row has 56g drink)"""
        df = parse_kitty_data(self.raw_sample)
        self.assertEqual(df.iloc[2]["Date"], "26/01/2026")
        self.assertEqual(df.iloc[2]["Time"], "16:11")
        self.assertEqual(df.iloc[2]["Drink_g"], 56)
        self.assertEqual(df.iloc[2]["Water_Weight_g"], 117)
        self.assertEqual(df.iloc[2]["Total_Weight_g"], 540)
        self.assertEqual(df.iloc[2]["Refill_To_g"], 630)

    def test_invalid_lines_ignored(self):
        """Should only parse the one valid line with `->`"""
        bad_data = "Bowl has 423g\nSome random note\n25/01/2026 - 01:41 -> 574g total"
        df = parse_kitty_data(bad_data)
        self.assertEqual(len(df), 1)


if __name__ == "__main__":
    unittest.main()
