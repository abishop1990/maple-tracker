import re
from pathlib import Path

import pandas as pd


def read_raw_data(raw_data_path: str | Path) -> str:
    with open(raw_data_path, "r") as f:
        raw_data = f.read()
    return raw_data


def parse_kitty_data(data: str) -> pd.DataFrame:
    """
    Assumes the data is in the raw data format.
    Splits the timestamp and data by `->` and then by `-`.
    Then parses the segments separated by `|` where it extracts the number from string via regex.

    :param data: The data as string from the raw data.
    :return: A pandas DataFrame containing the parsed data.
    """
    lines = data.strip().split("\n")
    parsed_data = []

    for line in lines:
        line = line.strip()
        if not line or "Bowl has" in line:
            continue

        parts = line.split("->")
        if len(parts) < 2:
            continue

        timestamp_str = parts[0].strip()
        data_part = parts[1].strip()
        date_str, time_str = timestamp_str.split(" - ")

        entry = {"Date": date_str, "Time": time_str, "Drink_g": 0}

        segments = [s.strip() for s in data_part.split("|") if s.strip()]
        for seg in segments:
            num = int(re.search(r"(\d+)", seg).group(1))
            if "total" in seg:
                entry["Total_Weight_g"] = num
            elif "water" in seg:
                entry["Water_Weight_g"] = num
            elif "drink" in seg:
                entry["Drink_g"] = num
            elif "refill" in seg:
                entry["Refill_To_g"] = num

        parsed_data.append(entry)

    return pd.DataFrame(parsed_data)
