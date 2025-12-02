
import pandas as pd
import matplotlib.pyplot as plt
import os

INPUT_CSV = "cleaned_energy_data.csv"
OUTPUT_PNG = "dashboard.png"

def load_and_prepare(csv_path):
    df = pd.read_csv(csv_path)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    df["kwh"] = pd.to_numeric(df["kwh"], errors="coerce").fillna(0.0)
    df = df.set_index("timestamp").sort_index()

    return df

def trend_line_daily(df, ax):

    daily_per_building = df.groupby("building").resample("D")["kwh"].sum().unstack(level=0)

    for col in daily_per_building.columns:
        ax.plot(daily_per_building.index, daily_per_building[col], label=col)

    ax.set_title("Daily Energy Consumption — All Buildings")
    ax.set_xlabel("Date")
    ax.set_ylabel("kWh per day")
    ax.legend(fontsize="small", loc="upper left")
    ax.grid(True)

def bar_chart_weekly_avg(df, ax):

    weekly_per_building = df.groupby("building").resample("W")["kwh"].sum().unstack(level=0)
    avg_weekly = weekly_per_building.mean(axis=0).sort_values(ascending=False)

    ax.bar(avg_weekly.index, avg_weekly.values)
    ax.set_title("Average Weekly Energy Usage by Building")
    ax.set_xlabel("Building")
    ax.set_ylabel("Average kWh per week")
    ax.set_xticklabels(avg_weekly.index, rotation=45, ha="right")
    ax.grid(axis="y", linestyle="--", linewidth=0.5)

def scatter_peak_hours(df, ax, top_n_per_building=10):
    
    hourly = df.groupby("building").resample("H")["kwh"].sum().unstack(level=0)

    for col in hourly.columns:
        series = hourly[col].dropna()
        if series.empty:
            continue
        top = series.sort_values(ascending=False).head(top_n_per_building)
        ax.scatter(top.index, top.values, label=col, s=20)

    ax.set_title(f"Peak-Hour Consumption (top {top_n_per_building} per building)")
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("kWh in that hour")
    ax.legend(fontsize="small", loc="upper left")
    ax.grid(True)

def create_dashboard(input_csv=INPUT_CSV, output_png=OUTPUT_PNG):
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"{input_csv} not found. Run ingestion first.")

    df = load_and_prepare(input_csv)

    fig, axes = plt.subplots(3, 1, figsize=(12, 14), constrained_layout=True)

    # Chart 1: Trend line (daily)
    trend_line_daily(df, axes[0])

    # Chart 2: Bar chart (average weekly)
    bar_chart_weekly_avg(df, axes[1])

    # Chart 3: Scatter (peak hours)
    scatter_peak_hours(df, axes[2], top_n_per_building=10)

    # Save the combined dashboard
    fig.suptitle("Campus Energy Dashboard", fontsize=16, y=0.98)
    fig.savefig(output_png, dpi=300)
    print(f"Saved dashboard to {output_png}")

if __name__ == "__main__":
    create_dashboard()

