import pandas as pd
import os

DATA_FOLDER = "data"
OUTPUT_FILE = "cleaned_energy_data.csv"
LOG_FILE = "ingestion_log.txt"

def log_message(msg):
    print(msg)
    with open(LOG_FILE,"a") as f:
        f.write(msg + "\n")

def read_single_csv(filepath):
    try:
        df = pd.read_csv(filepath, on_bad_lines='skip')
    except:
        log_message(f"ERROR: could not read the file {filepath}")
        return None
    
    df.columns = [c.strip().lower() for c in df.columns]
    timestamp_col = None
    for c in df.columns:
        if 'time' in c or "date" in c:
            timestamp_col = c
            break

    if timestamp_col is None:
        log_message(f"WARNING: No timestamp column in {filepath}. Using first column.")
        timestamp_col = df.columns[0]

    kwh_col = None
    for c in df.columns:
        if "kwh" in c or "energy" in c or "consumption" in c:
            kwh_col=c
            break
    if kwh_col is None:
        log_message("WARNING: No kwh column in {filepath}.Trying to pick numeric column.")
        numeric_cols = df.select_dtypes(include="number").columns
        if len(numeric_cols) > 0:
            kwh_col=numeric_cols[0]
        else:
            log_message(f"ERROR: No usable kwh column in {filepath}")
            return None

    df = df[[timestamp_col,kwh_col]].copy
    df = df.rename(columns={timestamp_col:"timestamp", kwh_col:"kwh"})    

    df["kwh"] = pd.to_numeric(df["kwh"],errors="coerce").fillna(0)

    filename = os.path.basename(filepath)
    building = filename.split("_",)[0]
    df["building"] = building
    return df

def ingest_data():
    if not os.path.exists(DATA_FOLDER):
        log_message(f"ERROR: Data folder '{DATA_FOLDER}'does not exist.")
        return
    
    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]
    if len(files) == 0:
        log_message("ERROR: No csv files found inside data folder.")
        return
    
    all_data = []

    for file in files:
        path = os.path.join(DATA_FOLDER, file)
        log_message(f"Reading {file}....")
        df = read_single_csv(path)

        if df is not None:
            all_data.append(df)
            log_message(f"SUCCESS: Loaded {len(df)} rows from {file}")
        else:
            log_message(f"SKIPPED: {file}")

    if len(all_data) == 0:
        log_message("ERROR: No valid data loaded.")
        return
    
    final_df = pd.concat(all_data, ignore_index=True)

    final_df.to_csv(OUTPUT_FILE, index= False)
    log_message(f"SAVED: Cleaned data ➡️ {OUTPUT_FILE}")
    log_message("Ingestion completed successfully.")
    return final_df

if __name__ == "__main__":
    open(LOG_FILE,"w").close()
    ingest_data