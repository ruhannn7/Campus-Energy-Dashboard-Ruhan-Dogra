# Campus-Energy-Dashboard-Ruhan-Dogra
Assignment: Capstone – End-to-End Energy Consumption Analysis and Visualization

🏫 Project Objective
The goal of this project is to design a Campus Energy Use Dashboard that processes energy consumption data collected across multiple campus buildings.
The dashboard helps understand patterns such as:
1.Daily and weekly energy usage
2.Highest and lowest consumption periods
3.Building-wise performance
4.Overall campus energy trends
This project combines data ingestion, aggregation, object-oriented modeling, visualization, and report generation into a complete end-to-end pipeline.

📊 Dataset Source

A sample dataset was created to simulate hourly electricity usage across 3 campus buildings:

1.Building A
2.Building B
3.Building C
Each CSV file includes:
-Timestamp
-Energy consumption value (kWh)
-File names follow the format: BuildingName_YYYY-MM.csv

🛠️ Methodology (Tasks 1–5)
✔ Task 1 — Data Ingestion (data_ingestion.py)
  Does:
    Reads all CSV files from the /data/ folder
    Normalizes column names
    Converts timestamps
    Cleans invalid or missing values
    Combines everything into a single file: cleaned_energy_data.csv

✔ Task 2 — Aggregation (aggregation.py)
  Computes:
    Daily energy totals (via resampling)
    Weekly energy totals
    Building-wise statistics - (mean, min, max, total consumption)

✔ Task 3 — Object-Oriented Model (oop_model.py)
  Implements a Building class:
    Stores building name and energy readings
    Computes average, min/max, totals
    Saves individual text reports to /reports/

✔ Task 4 — Visualization (visualize.py)
  Generates a multi-chart dashboard PNG (dashboard.png) containing:
    Daily consumption trends for each building
    Weekly average usage bar chart
    Peak-hour scatter plot

✔ Task 5 — Executive Summary (summary.py)
  Produces:
    building_summary.csv – building-level stats
    summary.txt – executive insights including:
    total campus energy usage
    highest-consuming building
    daily & weekly trends
    data cleaning notes

📈 Key Insights

From the sample dataset:
  1.Building A had the highest total consumption.
  2.All buildings showed a clear daily usage pattern with evening peaks.
  3.Weekly totals highlight consistent energy usage across the 3 buildings.
  4.No major anomalies in timestamp or numeric values were found after cleaning.
