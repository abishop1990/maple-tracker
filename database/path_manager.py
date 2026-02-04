from pathlib import Path


class PathManager:
    BASE_DIR = Path(__file__).parent.parent

    DATA_DIR = BASE_DIR / "database" / "data"
    DATABASE_PATH = DATA_DIR / "maple.db"
    RAW_DATA_PATH = DATA_DIR / "data-raw.txt"
    
    OUTPUT_DIR = BASE_DIR / "output"

if __name__ == "__main__":
    print(PathManager.BASE_DIR)
    print(PathManager.DATABASE_PATH)