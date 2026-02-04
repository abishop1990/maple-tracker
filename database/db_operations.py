import sqlite3
from enum import Enum
from pathlib import Path

from database.import_data import Defaults, init_db, normalize_date, get_sql_query
from database.path_manager import PathManager


class SortOrder(str, Enum):
    ASC = "ASC"
    DESC = "DESC"


def init_database(database_path: str | Path = PathManager.MAPLE_DATABASE_PATH) -> None:
    """Initialize database with schema."""
    conn = init_db(database_path)
    conn.close()


def read_bowl_weight(conn: sqlite3.Connection) -> int:
    """Get bowl weight from settings."""
    cursor = conn.execute("SELECT value FROM settings WHERE key = 'bowl_weight'")
    row = cursor.fetchone()
    return int(row['value'] if isinstance(row, sqlite3.Row) else row[0]) if row else Defaults.BOWL_WEIGHT


def update_bowl_weight_(conn: sqlite3.Connection, weight: int) -> None:
    """Update the bowl weight in settings."""
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('bowl_weight', ?)", (str(weight),))
    conn.commit()


def read_previous_entry(conn: sqlite3.Connection) -> sqlite3.Row | None:
    """Get the most recent entry."""
    cursor = conn.execute("SELECT * FROM entries ORDER BY date DESC, time DESC LIMIT 1")
    return cursor.fetchone()


def read_all_entries(conn: sqlite3.Connection, order: SortOrder = SortOrder.ASC) -> list[dict]:
    """Get all entries, ordered by date and time."""
    order_sql = order.value
    cursor = conn.execute(f'SELECT * FROM entries ORDER BY date {order_sql}, time {order_sql}')
    return [dict(row) for row in cursor.fetchall()]


def create_entry(
        conn: sqlite3.Connection,
        date: str,
        time: str,
        total_weight: int,
        water_weight: int,
        drink: int = 0,
        refill_to: int | None = None,
        notes: str = ""
) -> int:
    """Add a new entry and return the new entry ID."""
    insert_sql = get_sql_query("insert_entry.sql")
    db_date = normalize_date(date)

    cursor = conn.execute(insert_sql, (db_date, time, total_weight, water_weight, drink, refill_to, notes))
    conn.commit()
    return cursor.lastrowid


def delete_entry_by_id(conn: sqlite3.Connection, entry_id: int) -> None:
    """Delete an entry by ID."""
    conn.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
    conn.commit()
