import argparse
from pathlib import Path

from database.data_parse import read_raw_data, parse_kitty_data
from database.import_data import init_db, import_to_db
from database.path_manager import PathManager


def main():
    parser = argparse.ArgumentParser(description="Import raw data to SQLite database.")
    parser.add_argument("--data-file", "-d", type=Path, required=True, help="Path to raw data file.")
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
