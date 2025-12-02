import pandas as pd
import os

INPUT_CSV = "cleaned_energy_data.csv"
BUILDING_SUMMARY_CSV = "building_summary.csv"
SUMMARY_TXT = "summary.txt"

def load_data(csv_path=INPUT_CSV):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"{csv_path} not found. Run data ingestion first.")

    df = pd.read_csv(csv_path)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])

    df["kwh"] = pd.to_numeric(df["kwh"], errors="coerce").fillna(0.0)

    if "building" not in df.columns:
        df["building"] = "Unknown"

    df = df.sort_values("timestamp").reset_index(drop=True)

    return df

def save_building_summary(df, out_csv=BUILDING_SUMMARY_CSV):
    summary = df.groupby("building")["kwh"].agg(
        count="count",
        total_kwh="sum",
        mean_kwh="mean",
        min_kwh="min",
        max_kwh="max"
    ).sort_values("total_kwh", ascending=False)

    summary.to_csv(out_csv)
    return summary

def campus_level_stats(df):
    stats = {}

    # Total campus consumption (sum of all kWh)
    total_campus = df["kwh"].sum()
    stats["total_campus_kwh"] = float(total_campus)

    # Highest-consuming building
    building_totals = df.groupby("building")["kwh"].sum()
    if not building_totals.empty:
        highest_building = building_totals.idxmax()
        highest_building_value = float(building_totals.max())
    else:
        highest_building = None
        highest_building_value = 0.0

    stats["highest_building"] = str(highest_building)
    stats["highest_building_kwh"] = highest_building_value

    # Peak load time
    df_ts = df.groupby("timestamp")["kwh"].sum()
    if not df_ts.empty:
        peak_timestamp = df_ts.idxmax()
        peak_value = float(df_ts.max())
        peak_timestamp_str = pd.to_datetime(peak_timestamp).strftime("%Y-%m-%d %H:%M:%S")
    else:
        peak_timestamp_str = None
        peak_value = 0.0

    stats["peak_timestamp"] = peak_timestamp_str
    stats["peak_kwh_at_timestamp"] = peak_value

    # Daily and weekly totals
    df_indexed = df.set_index("timestamp").sort_index()

    # Daily totals (D)
    daily_totals = df_indexed["kwh"].resample("D").sum()
    stats["daily_totals_series"] = [(d.strftime("%Y-%m-%d"), float(v)) for d, v in daily_totals.items()]

    # Weekly totals (W)
    weekly_totals = df_indexed["kwh"].resample("W").sum()
    stats["weekly_totals_series"] = [(d.strftime("%Y-%m-%d"), float(v)) for d, v in weekly_totals.items()]

    if len(weekly_totals) >= 2:
        last = weekly_totals.iloc[-1]
        prev = weekly_totals.iloc[-2]
        if prev == 0:
            pct_change = None
        else:
            pct_change = float((last - prev) / prev * 100.0)
        stats["last_week_total_kwh"] = float(last)
        stats["prev_week_total_kwh"] = float(prev)
        stats["week_over_week_pct_change"] = pct_change
    else:
        stats["last_week_total_kwh"] = None
        stats["prev_week_total_kwh"] = None
        stats["week_over_week_pct_change"] = None

    return stats

def write_summary_text(stats, building_summary_df, out_txt=SUMMARY_TXT):
    lines = []
    lines.append("Campus Energy Usage — Executive Summary")
    lines.append("=" * 40)
    lines.append(f"Total campus energy consumption: {stats['total_campus_kwh']:.3f} kWh")
    lines.append("")
    if stats["highest_building"]:
        lines.append(f"Highest-consuming building: {stats['highest_building']} ({stats['highest_building_kwh']:.3f} kWh)")
    else:
        lines.append("Highest-consuming building: N/A")
    lines.append("")
    if stats["peak_timestamp"]:
        lines.append(f"Peak campus load occurred at: {stats['peak_timestamp']} with {stats['peak_kwh_at_timestamp']:.3f} kWh")
    else:
        lines.append("Peak campus load: N/A")
    lines.append("")
    # Short weekly trend
    if stats["last_week_total_kwh"] is not None:
        pct = stats["week_over_week_pct_change"]
        if pct is None:
            pct_text = "N/A (previous week total was 0)"
        else:
            pct_text = f"{pct:.2f}%"
        lines.append("Weekly trend:")
        lines.append(f"  Last week total: {stats['last_week_total_kwh']:.3f} kWh")
        lines.append(f"  Previous week total: {stats['prev_week_total_kwh']:.3f} kWh")
        lines.append(f"  Week-over-week change: {pct_text}")
    else:
        lines.append("Weekly trend: Insufficient weekly data.")

    lines.append("")
    lines.append("Daily totals (date : kWh) — last 7 days shown (or fewer if not available):")
    last_days = stats["daily_totals_series"][-7:]
    for d, v in last_days:
        lines.append(f"  {d} : {v:.3f}")

    lines.append("")
    lines.append("Top 5 buildings by total consumption:")
    top_buildings = building_summary_df.head(5)
    for name, row in top_buildings.iterrows():
        lines.append(f"  {name} — total: {row['total_kwh']:.3f} kWh | mean: {row['mean_kwh']:.3f} | readings: {int(row['count'])}")

    lines.append("")
    lines.append("Notes:")
    lines.append(" - Data processed using pandas resampling (daily/weekly).")
    lines.append(" - Timestamps were parsed by pandas; any invalid timestamps were dropped.")
    lines.append(" - kWh values coerced to numeric; invalid values replaced with 0.0.")
    lines.append("")
    lines.append("Generated by report_generator.py")

    with open(out_txt, "w") as f:
        f.write("\n".join(lines))

    return "\n".join(lines)

def run_all():

    df = load_data(INPUT_CSV)
    building_summary = save_building_summary(df, BUILDING_SUMMARY_CSV)
    stats = campus_level_stats(df)
    summary_text = write_summary_text(stats, building_summary, SUMMARY_TXT)


    print("\n=== Report Generated ===")
    print(f"Building summary saved to: {BUILDING_SUMMARY_CSV}")
    print(f"Executive summary saved to: {SUMMARY_TXT}")
    print("\n--- Executive Summary ---\n")
    print(summary_text)
    print("\n=========================\n")

if __name__ == "__main__":
    run_all()
