import pandas as pd 

#---DAILY TOTALS---
def calculate_daily_totals(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"],errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df = df.set_index("timestamp")

    daily = df.resample("D")["kwh"].sum()
    return daily

# ---WEEKLY TOTALS---
def calculate_weekly_totals(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"],errors="coerce")
    df = df.dropna(subset=["timestamp"])
    df = df.set_index("timestamp")

    weekly = df.resample("W")["kwh"].sum()
    return weekly

# ---BUILDING SUMMARY---
def building_wise_summary(df):
    summary = df.groupby("building")["kwh"].agg(
        mean_kwh="mean",
        min_kwh="min",
        max_kwh="max",
        total_kwh="sum"
    )
    return summary

if __name__ == "__main__":
    df= pd.read_csv("cleaned_energy_data.csv")
    print("\n---Daily Totals---")
    print(calculate_daily_totals(df))
    
    print("\n---Weekly Totals---")
    print(calculate_weekly_totals(df))
    
    print("\n---Buidling Summary---")
    print(building_wise_summary(df))

    
