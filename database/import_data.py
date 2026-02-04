import sqlite3
from pathlib import Path

import pandas as pd

from database.path_manager import PathManager


class Defaults:
    BOWL_WEIGHT = 423


def get_sql_query(filename: str | Path) -> str:
    """Helper to read SQL files from the queries directory."""
    query_path = PathManager.SQL_SCRIPS_DIR / filename
    return query_path.read_text()


def init_db(database_path: str | Path = PathManager.MAPLE_DATABASE_PATH) -> sqlite3.Connection:
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
