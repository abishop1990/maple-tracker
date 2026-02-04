import sqlite3

import pandas as pd
from database.data_parse import parse_kitty_data
from database.db_operations import read_bowl_weight, create_entry


def import_raw_text(conn: sqlite3.Connection, raw_text: str) -> int:
    """
    Import data from raw text format using existing parser.

    :param conn: Database connection
    :param raw_text: Raw text data in the expected format
    :return: Number of successfully imported entries
    """
    bowl_weight = read_bowl_weight(conn)

    df = parse_kitty_data(raw_text)

    if df.empty:
        return 0

    imported = 0
    for _, row in df.iterrows():
        try:
            total_weight = row.get("Total_Weight_g", 0)
            water_weight = row.get("Water_Weight_g", 0)

            if total_weight == 0 and water_weight > 0:
                total_weight = water_weight + bowl_weight
            elif water_weight == 0 and total_weight > 0:
                water_weight = total_weight - bowl_weight

            create_entry(
                conn=conn,
                date=row["Date"],
                time=row["Time"],
                total_weight=int(total_weight),
                water_weight=int(water_weight),
                drink=int(row.get("Drink_g", 0)),
                refill_to=int(row["Refill_To_g"]) if "Refill_To_g" in row and not _is_nan(row["Refill_To_g"]) else None,
                notes="",
            )
            imported += 1
        except Exception as e:
            print(f"Error importing row: {row.to_dict()}, Error: {e}")
            continue

    return imported


def _is_nan(value) -> bool:
    """Check if value is NaN (works with pandas NaN and None)."""
    try:
        return pd.isna(value)
    except (ImportError, TypeError):
        return value is None
