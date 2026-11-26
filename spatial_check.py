
import json
import pandas as pd

# ==========================================
# 1. Load JSON
# ==========================================

with open("heatmap_result.json", "r", encoding="utf-8") as file:
    response = json.load(file)

features = response["data"]["result"]["map_data"]["features"]

# ==========================================
# 2. Extract Spatial Information
# ==========================================

rows = []

for feature in features:

    properties = feature.get("properties", {})
    geometry = feature.get("geometry", {})

    coordinates = geometry.get("coordinates", [])

    if not coordinates or not coordinates[0]:
        continue

    polygon = coordinates[0]

    # Remove closing coordinate if repeated
    if polygon[0] == polygon[-1]:
        polygon = polygon[:-1]

    longitudes = [point[0] for point in polygon]
    latitudes = [point[1] for point in polygon]

    rows.append({
        "tile_id": properties.get("tile_id"),
        "temperature": properties.get("average_temperature"),
        "center_lat": sum(latitudes) / len(latitudes),
        "center_lon": sum(longitudes) / len(longitudes),
        "min_lat": min(latitudes),
        "max_lat": max(latitudes),
        "min_lon": min(longitudes),
        "max_lon": max(longitudes),
        "geometry": json.dumps(coordinates)
    })

df = pd.DataFrame(rows)

# ==========================================
# 3. Spatial Analysis
# ==========================================

print("=" * 55)
print("FORTYGUARD SPATIAL ANALYSIS")
print("=" * 55)

print("\nNumber of valid tiles:", len(df))

print("\nUnique geometries:", df["geometry"].nunique())

print("\nUnique center coordinates:")
print("Latitude:", df["center_lat"].nunique())
print("Longitude:", df["center_lon"].nunique())

print("\nGeographical boundaries:")

print("Latitude range:",
      df["min_lat"].min(),
      "to",
      df["max_lat"].max())

print("Longitude range:",
      df["min_lon"].min(),
      "to",
      df["max_lon"].max())

# ==========================================
# 4. Temperature vs Spatial Variation
# ==========================================

print("\n========== TEMPERATURE CHECK ==========")

print("Unique temperatures:",
      df["temperature"].nunique())

print("Temperature values:")
print(df["temperature"].value_counts())

# ==========================================
# 5. Inspect Sample Tiles
# ==========================================

print("\n========== FIRST 5 TILES ==========")

print(
    df[[
        "tile_id",
        "temperature",
        "center_lat",
        "center_lon"
    ]].head().to_string(index=False)
)

print("\n========== LAST 5 TILES ==========")

print(
    df[[
        "tile_id",
        "temperature",
        "center_lat",
        "center_lon"
    ]].tail().to_string(index=False)
)

# ==========================================
# 6. Export Spatial Data
# ==========================================

df.drop(columns=["geometry"]).to_csv(
    "heatmap_spatial_analysis.csv",
    index=False
)

print("\nSpatial analysis exported successfully.")

print("\n" + "=" * 55)
print("SPATIAL ANALYSIS COMPLETED")
print("=" * 55)
