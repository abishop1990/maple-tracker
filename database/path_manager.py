from pathlib import Path


class PathManager:
    BASE_DIR = Path(__file__).parent.parent

    DATA_DIR = BASE_DIR / "database" / "data"
    SQL_SCRIPS_DIR = BASE_DIR / "database" / "sql-scripts"
    MAPLE_DATABASE_PATH = DATA_DIR / "maple.db"
    MAPLE_RAW_DATA_PATH = DATA_DIR / "maple-data-raw.txt"

    OUTPUT_DIR = BASE_DIR / "output"
    TEST_RESOURCES_DIR = BASE_DIR / "tests" / "resources"


if __name__ == "__main__":
    print(PathManager.BASE_DIR)
    print(PathManager.MAPLE_DATABASE_PATH)
