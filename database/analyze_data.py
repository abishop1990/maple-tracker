from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def daily_summary_to_csv(df: pd.DataFrame, save_dir: str | Path | None = None, cat_name: str = "Maple") -> pd.DataFrame:
    daily_summary = df.groupby("Date")["Drink_g"].sum().reset_index()
    daily_summary["Date_dt"] = pd.to_datetime(daily_summary["Date"], format="%Y-%m-%d")
    daily_summary = daily_summary.sort_values("Date_dt")

    if save_dir is not None:
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(save_dir / f"{cat_name.lower()}-water-log.csv", index=False)
        daily_summary[["Date", "Drink_g"]].to_csv(save_dir / f"{cat_name.lower()}-daily-summary.csv", index=False)
    return daily_summary


def plot_kitty_data(daily_summary: pd.DataFrame, save_dir: str | Path | None = None, cat_name: str = "Maple") -> None:
    plt.figure(figsize=(10, 6))
    date_labels = daily_summary["Date_dt"].dt.strftime("%d/%m")
    bars = plt.bar(date_labels, daily_summary["Drink_g"], color="#E8D4A8", edgecolor="#2C3E50", linewidth=1.2)

    avg_intake = daily_summary["Drink_g"].mean()
    median_intake = daily_summary["Drink_g"].median()
    std_intake = daily_summary["Drink_g"].std()
    plt.axhline(y=avg_intake, color="#E74C3C", linestyle="--", label=f"Average: {avg_intake:.2f}g", linewidth=2)
    plt.axhline(y=median_intake, color="#27AE60", linestyle=":", label=f"Median: {median_intake:.2f}g", linewidth=2)
    plt.axhspan(
        avg_intake - std_intake,
        avg_intake + std_intake,
        alpha=0.15,
        color="black",
        label=f"±1 Std Dev ({std_intake:.1f}g)",
    )

    plt.title(f"{cat_name.capitalize()} Daily Water Intake", fontsize=16, fontweight="bold", pad=15)
    plt.xlabel("Date (Day/Month)", fontsize=11)
    plt.ylabel("Water Consumed (g)", fontsize=11)
    plt.xticks(rotation=0)
    plt.legend(loc="upper right", fontsize=9)
    plt.grid(axis="y", linestyle="--", alpha=0.4)

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{int(height)}g",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    if save_dir is not None:
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_dir / f"{cat_name.lower()}-water-intake.png", dpi=150, facecolor="white", bbox_inches="tight")
    plt.show()


def time_period(hour: int) -> str:
    morning_start_hour = 5
    morning_end_hour = 12
    afternoon_end_hour = 18
    evening_end_hour = 23
    if morning_start_hour <= hour < morning_end_hour:
        return "Morning\n(5-12)"
    elif morning_end_hour <= hour < afternoon_end_hour:
        return "Afternoon\n(12-18)"
    elif afternoon_end_hour <= hour < evening_end_hour:
        return "Evening\n(18-23)"
    else:
        return "Night\n(23-5)"


def plot_time_pie_chart(df: pd.DataFrame, save_dir: str | Path | None = None, cat_name: str = "Maple") -> None:
    df = df.copy()
    df["Hour"] = pd.to_datetime(df["Time"], format="%H:%M").dt.hour
    period_order = ["Morning\n(5-12)", "Afternoon\n(12-18)", "Evening\n(18-23)", "Night\n(23-5)"]
    colors = ["#F9E79F", "#F5B041", "#E59866", "#5D6D7E"]
    df["Period"] = df["Hour"].apply(time_period)
    period_summary = df.groupby("Period")["Drink_g"].sum().reset_index()
    period_summary = period_summary.set_index("Period").reindex(period_order).fillna(0).reset_index()

    mask = period_summary["Drink_g"] > 0
    labels = period_summary.loc[mask, "Period"].tolist()
    values = period_summary.loc[mask, "Drink_g"].tolist()
    chart_colors = [colors[period_order.index(p)] for p in labels]

    fig, ax = plt.subplots(figsize=(8, 6))

    _wedges, _texts, autotexts = ax.pie(
        values,
        labels=labels,
        colors=chart_colors,
        autopct=lambda pct: f"{pct:.1f}%\n({int(pct / 100 * sum(values))}g)",
        startangle=90,
        explode=[0.02] * len(values),
        shadow=True,
        textprops={"fontsize": 10},
    )

    for autotext in autotexts:
        autotext.set_fontweight("bold")
        autotext.set_fontsize(9)

    ax.set_title(f"{cat_name.capitalize()} Drinking Pattern by Time of Day", fontsize=14, fontweight="bold", pad=20)

    total = sum(values)
    fig.text(
        0.5,
        0.02,
        f"Total tracked: {int(total)}g over {len(df)} measurements",
        ha="center",
        fontsize=9,
        color="gray",
        style="italic",
    )

    plt.tight_layout()
    if save_dir is not None:
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(
            save_dir / f"{cat_name.lower()}-drinking-pattern-time-of-day.png",
            dpi=150,
            facecolor="white",
            bbox_inches="tight",
        )
    plt.show()


if __name__ == "__main__":
    from database.data_parse import parse_kitty_data, read_raw_data
    from database.path_manager import PathManager

    raw_data = read_raw_data(PathManager.MAPLE_RAW_DATA_PATH)
    maple_df = parse_kitty_data(raw_data)
    cat = "Maple"
    maple_summary = daily_summary_to_csv(maple_df, save_dir=PathManager.OUTPUT_DIR, cat_name=cat)
    plot_kitty_data(maple_summary, save_dir=PathManager.OUTPUT_DIR, cat_name=cat)
    plot_time_pie_chart(maple_df, save_dir=PathManager.OUTPUT_DIR, cat_name=cat)
