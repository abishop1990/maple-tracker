import argparse
from pathlib import Path

from database.analyze_data import daily_summary_to_csv, plot_kitty_data, plot_time_pie_chart
from database.data_parse import parse_kitty_data, read_raw_data
from database.path_manager import PathManager


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze data and generate plots and CSV summaries")
    parser.add_argument("--data-file", "-d", type=Path, required=True, help="Path to raw data file.")
    parser.add_argument("--save-dir", "-s", type=Path, default=PathManager.OUTPUT_DIR, help="Path to save outputs.")
    parser.add_argument(
        "--cat-name", "-n", type=str, default="Maple", help="Cat name to display on plots and output directory name."
    )
    args = parser.parse_args()

    raw_data_path = Path(args.data_file)
    cat_name: str = args.cat_name.lower()
    save_dir = Path(args.save_dir) / cat_name
    save_dir.mkdir(parents=True, exist_ok=True)

    raw_data = read_raw_data(raw_data_path)
    cat_df = parse_kitty_data(raw_data)

    cat_summary = daily_summary_to_csv(cat_df, save_dir=save_dir, cat_name=cat_name)
    plot_kitty_data(cat_summary, save_dir=save_dir, cat_name=cat_name)
    plot_time_pie_chart(cat_df, save_dir=save_dir, cat_name=cat_name)


if __name__ == "__main__":
    main()
