import pandas as pd

class MeterReading:
    def __init__(self,timestamp,kwh):
        self.timestamp = timestamp
        try:
            self.kwh = float(kwh)
        except:
            self.kwh = 0.0

    def __repr__(self):
        return f"MeterReading(timestamp={self.timestamp},kwh={self.kwh})"

class Building:
    def __init__(self,name):
        self.name = name
        self.meter_readings = []
        
    def add_reading(self,reading):
        if isinstance(reading,MeterReading):
            self.meter_readings.append(reading)
        else:
            try:
                timestamp , kwh = reading
                self.meter_readings.append(MeterReading(timestamp,kwh))
            except Exception:
                raise ValueError("Reading must be MeterReading or (timestamp,kwh) tuple")
            
    def calculate_total_consumption(self):
        return sum(r.kwh for r in self.meter_readings)

    def calculate_mean_consumption(self):
        n = len(self.meter_readings)
        return self.calculate_total_consumption() / n if n > 0 else 0.0

    def calculate_min_max(self):
        if not self.meter_readings:
            return 0.0, 0.0
        values = [r.kwh for r in self.meter_readings]
        return min(values), max(values)

    def generate_report(self):
        total = self.calculate_total_consumption()
        mean = self.calculate_mean_consumption()
        mn, mx = self.calculate_min_max()
        lines = [
            f"Building: {self.name}",
            f"  Readings count: {len(self.meter_readings)}",
            f"  Total kWh: {total:.3f}",
            f"  Mean kWh (per reading): {mean:.3f}",
            f"  Min kWh: {mn:.3f}",
            f"  Max kWh: {mx:.3f}"
        ]
        return "\n".join(lines)


class BuildingManager:
    def __init__(self):
        self.buildings = {}

    def get_or_create(self, building_name):
        if building_name not in self.buildings:
            self.buildings[building_name] = Building(building_name)
        return self.buildings[building_name]

    def add_reading_to_building(self, building_name, timestamp, kwh):
        b = self.get_or_create(building_name)
        b.add_reading((timestamp, kwh))

    def summary_table(self):
        rows = []
        for name, b in self.buildings.items():
            total = b.calculate_total_consumption()
            mean = b.calculate_mean_consumption()
            mn, mx = b.calculate_min_max()
            count = len(b.meter_readings)
            rows.append({
                "building": name,
                "count": count,
                "total_kwh": total,
                "mean_kwh": mean,
                "min_kwh": mn,
                "max_kwh": mx
            })
        return pd.DataFrame(rows).set_index("building").sort_index()

    def save_all_reports(self, out_folder="reports"):
        import os
        os.makedirs(out_folder, exist_ok=True)
        for name, b in self.buildings.items():
            fname = os.path.join(out_folder, f"{name}_report.txt")
            with open(fname, "w") as f:
                f.write(b.generate_report())


if __name__ == "__main__":

    df = pd.read_csv("cleaned_energy_data.csv")

    mgr = BuildingManager()
    for idx, row in df.iterrows():
        ts = row.get("timestamp", None)
        kwh = row.get("kwh", 0)
        building = row.get("building", "Unknown")
        mgr.add_reading_to_building(building, ts, kwh)


    print("\n=== Building Summary Table ===")
    print(mgr.summary_table())

    mgr.save_all_reports(out_folder="reports")
    print("\nSaved per-building reports to ./reports/")
