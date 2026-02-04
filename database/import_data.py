import argparse
import sqlite3
from pathlib import Path

import pandas as pd

from database.data_parse import read_raw_data, parse_kitty_data
from database.path_manager import PathManager


class Defaults:
    BOWL_WEIGHT = 423


def get_sql_query(filename: str | Path) -> str:
    """Helper to read SQL files from the queries directory."""
    query_path = PathManager.SQL_SCRIPS_DIR / filename
    return query_path.read_text()


def init_db(database_path: str | Path = PathManager.DATABASE_PATH) -> sqlite3.Connection:
    """Initialize database with schema."""
    database_path = Path(database_path)
    conn = sqlite3.connect(database_path)

    schema_sql = get_sql_query("schema.sql")
    conn.executescript(schema_sql)

    cursor = conn.execute("SELECT value FROM settings WHERE key = 'bowl_weight'")
    if cursor.fetchone() is None:
        conn.execute("INSERT INTO settings (key, value) VALUES ('bowl_weight', ?)", (str(Defaults.BOWL_WEIGHT),))

    conn.commit()
    return conn


def import_to_db(conn, df: pd.DataFrame) -> int:
    """
    Takes a pandas DataFrame and inserts it into the SQLite database.
    Handles potential NaN/None for Refill_To_g
    """
    imported = 0
    insert_sql = get_sql_query("insert_entry.sql")

    for row in df.itertuples():
        try:
            refill = int(row.Refill_To_g) if hasattr(row, "Refill_To_g") and not pd.isna(row.Refill_To_g) else None

            conn.execute(insert_sql, (
                row.Date,
                row.Time,
                getattr(row, "Total_Weight_g", 0),
                getattr(row, "Water_Weight_g", 0),
                row.Drink_g,
                refill,
                ""
            ))
            imported += 1
            print(f"\t{row.Date} {row.Time} - {row.Drink_g}g drink")
        except Exception as e:
            print(f"\t! Error inserting row {row.Index}: {e}")

    conn.commit()
    return imported


def main():
    parser = argparse.ArgumentParser(description="Import raw data to SQLite database.")
    parser.add_argument("--data-file", "-d", type=Path, required=True, help="Path to raw data file")
    parser.add_argument("--cat-name", "-n", type=str, default="Maple", help="Cat name representing the database file.")

    args = parser.parse_args()

    data_file = Path(args.data_file)
    cat_name: str = args.cat_name.lower()
    if not data_file.exists():
        print(f"Error: File not found: {data_file}")
        return

    database_path = PathManager.DATA_DIR / f"{cat_name}.db"

    print(f"\n{cat_name.capitalize()} Water Tracker - Data Import")
    print("=" * 40)
    print(f"Database: {database_path}")
    print(f"Data file: {data_file}")
    conn = init_db(database_path=database_path)

    print("\nParsing raw data...")
    raw_text = read_raw_data(data_file)
    df = parse_kitty_data(raw_text)

    print(f"Importing {len(df)} entries...")
    imported_count = import_to_db(conn, df)

    print()
    print("=" * 40)
    print(f"Successfully imported {imported_count} entries!")
    conn.close()


if __name__ == "__main__":
    main()
