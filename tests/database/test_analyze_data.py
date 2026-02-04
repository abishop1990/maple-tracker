import unittest

import pandas as pd

from database.analyze_data import daily_summary_to_csv, time_period


class TestAnalyzeData(unittest.TestCase):
    def setUp(self):
        data = {
            "Date": ["01/01/2026", "01/01/2026", "02/01/2026"],
            "Drink_g": [10, 20, 50]
        }
        self.df = pd.DataFrame(data)

    def test_daily_summary_calculation(self):
        """01/01/2026 should have 10 + 20 = 30"""
        summary = daily_summary_to_csv(self.df)

        jan1_sum = summary[summary["Date"] == "01/01/2026"]["Drink_g"].values[0]
        self.assertEqual(jan1_sum, 30)
        self.assertEqual(len(summary), 2)

    def test_time_period_logic(self):
        self.assertEqual(time_period(8), "Morning\n(5-12)")
        self.assertEqual(time_period(14), "Afternoon\n(12-18)")
        self.assertEqual(time_period(20), "Evening\n(18-23)")
        self.assertEqual(time_period(2), "Night\n(23-5)")


if __name__ == "__main__":
    unittest.main()
