import unittest

from database.analyze_data import daily_summary_to_csv
from database.data_parse import read_raw_data, parse_kitty_data
from database.path_manager import PathManager


class TestDataParseIntegration(unittest.TestCase):
    def test_full_pipeline_from_raw_file(self):
        """
        Tests reading the actual raw file and calculating summaries.
            1. Reads the actual data from the file
            2. Parse the text into a DataFrame
            3. Generate a daily summary
            4. Verification against known data in maple-data-raw.txt. On 25/01/2026,
                Maple had three entries: 0g (implied), 43g measured at 14:13 and 17g measured at 22:16.
            5. Verify sorting (latest date should be at the end)
        """
        raw_path = PathManager.MAPLE_RAW_DATA_PATH
        self.assertTrue(raw_path.exists(), f"Raw data file not found at {raw_path}")
        raw_text = read_raw_data(raw_path)

        df = parse_kitty_data(raw_text)
        self.assertGreater(len(df), 0)

        summary = daily_summary_to_csv(df)

        jan_25_data = summary[summary["Date"] == "25/01/2026"]
        self.assertFalse(jan_25_data.empty)

        total_drink_jan_25 = jan_25_data["Drink_g"].values[0]
        self.assertEqual(total_drink_jan_25, 60)

        last_date = summary.iloc[-1]["Date"]
        self.assertEqual(last_date, "04/02/2026")


if __name__ == "__main__":
    unittest.main()
