
import json
import pandas as pd
from pathlib import Path

# ==========================================
# 1. Load Heatmap JSON
# ==========================================

file_path = Path("heatmap_result_ny.json")

if not file_path.exists():
    print("Error: heatmap_result_ny.json not found!")
    exit()

with open(file_path, "r", encoding="utf-8") as file:
    response = json.load(file)

print("=" * 60)
print("FORTYGUARD NEW YORK HEATMAP ANALYSIS")
print("=" * 60)

# ==========================================
# 2. Extract Response Data
# ==========================================

data = response.get("data", {})
result = data.get("result", {})

map_data = result.get("map_data", {})
features = map_data.get("features", [])

stats_data = result.get("stats_data", {})

print("\nAPI STATUS:", data.get("status"))
print("NUMBER OF TILES:", len(features))

# ==========================================
# 3. Extract Tile Data + Coordinates
# ==========================================

rows = []

for feature in features:

    properties = feature.get("properties", {})
    geometry = feature.get("geometry", {})

    coordinates = geometry.get("coordinates", [])

    # Polygon outer boundary
    ring = coordinates[0] if coordinates else []

    # Extract longitude and latitude
    longitudes = [point[0] for point in ring]
    latitudes = [point[1] for point in ring]

    rows.append({
        "tile_id": properties.get("tile_id"),
        "average_temperature": properties.get("average_temperature"),
        "min_temperature": properties.get("min_temperature"),
        "max_temperature": properties.get("max_temperature"),
        "min_latitude": min(latitudes) if latitudes else None,
        "max_latitude": max(latitudes) if latitudes else None,
        "min_longitude": min(longitudes) if longitudes else None,
        "max_longitude": max(longitudes) if longitudes else None
    })

df = pd.DataFrame(rows)

if df.empty:
    print("\nNo heatmap features found.")
    print("Available result keys:", list(result.keys()))
    exit()

# ==========================================
# 4. Dataset Exploration
# ==========================================

print("\n========== DATASET INFORMATION ==========")

print("\nDataset:")
print(df)

print("\nShape:")
print(df.shape)

print("\nMissing Values:")
print(df.isnull().sum())

print("\nUnique Values:")
print(df.nunique())

# ==========================================
# 5. Temperature Statistics
# ==========================================

print("\n========== TEMPERATURE STATISTICS ==========")

temperature = df["average_temperature"]

print("Minimum:", temperature.min())
print("Maximum:", temperature.max())
print("Mean:", temperature.mean())
print("Median:", temperature.median())
print("Standard Deviation:", temperature.std())
print("Unique Temperatures:", temperature.nunique())

print("\nTemperature Frequency:")
print(temperature.value_counts().sort_index())

# ==========================================
# 6. Spatial Analysis
# ==========================================

print("\n========== SPATIAL ANALYSIS ==========")

print("Latitude Range:")
print(df["min_latitude"].min(), "to", df["max_latitude"].max())

print("\nLongitude Range:")
print(df["min_longitude"].min(), "to", df["max_longitude"].max())

print("\nTile Coordinates:")
print(df[[
    "tile_id",
    "min_latitude",
    "max_latitude",
    "min_longitude",
    "max_longitude"
]])

# ==========================================
# 7. API Statistical Data
# ==========================================

print("\n========== API STATISTICAL DATA ==========")

print(json.dumps(
    stats_data,
    indent=4,
    ensure_ascii=False
))

# ==========================================
# 8. Export CSV
# ==========================================

output_file = "heatmap_tiles_ny.csv"

df.to_csv(output_file, index=False)

print("\n========== EXPORT ==========")
print("CSV created:", output_file)

print("\n" + "=" * 60)
print("NEW YORK ANALYSIS COMPLETED")
print("=" * 60)
