
import pandas as pd
import numpy as np

df = pd.read_csv("heatmap_spatial_analysis.csv")
df = df.sort_values("tile_id").reset_index(drop=True)

ROWS = 9
COLS = 9

LAT_METERS = 111320
MEAN_LAT = df["center_lat"].mean()
LON_METERS = LAT_METERS * np.cos(np.radians(MEAN_LAT))

horizontal = []
vertical = []

# Horizontal neighboring bounding boxes
for row in range(ROWS):
    for col in range(COLS - 1):
        i = row * COLS + col
        a = df.iloc[i]
        b = df.iloc[i + 1]

        overlap_lon = a["max_lon"] - b["min_lon"]
        overlap_lat = min(a["max_lat"], b["max_lat"]) - max(
            a["min_lat"], b["min_lat"]
        )

        horizontal.append({
            "tile_a": int(a["tile_id"]),
            "tile_b": int(b["tile_id"]),
            "overlap_width_m": overlap_lon * LON_METERS,
            "overlap_height_m": overlap_lat * LAT_METERS
        })

# Vertical neighboring bounding boxes
for row in range(ROWS - 1):
    for col in range(COLS):
        i = row * COLS + col
        a = df.iloc[i]
        b = df.iloc[i + COLS]

        overlap_lat = a["max_lat"] - b["min_lat"]
        overlap_lon = min(a["max_lon"], b["max_lon"]) - max(
            a["min_lon"], b["min_lon"]
        )

        vertical.append({
            "tile_a": int(a["tile_id"]),
            "tile_b": int(b["tile_id"]),
            "overlap_height_m": overlap_lat * LAT_METERS,
            "overlap_width_m": overlap_lon * LON_METERS
        })

h = pd.DataFrame(horizontal)
v = pd.DataFrame(vertical)

print("=" * 65)
print("BOUNDING BOX OVERLAP DIAGNOSTIC")
print("=" * 65)

print("\nHORIZONTAL NEIGHBORS")
print(h.describe().round(4).to_string())

print("\nVERTICAL NEIGHBORS")
print(v.describe().round(4).to_string())

print("\nSAMPLE HORIZONTAL PAIRS")
print(h.head(10).round(4).to_string(index=False))

print("\nSAMPLE VERTICAL PAIRS")
print(v.head(10).round(4).to_string(index=False))

print("\n========== SUMMARY ==========")
print("Horizontal pairs:", len(h))
print("Vertical pairs:", len(v))

print("Horizontal positive bbox overlaps:",
      (h["overlap_width_m"] > 0).sum())

print("Vertical positive bbox overlaps:",
      (v["overlap_height_m"] > 0).sum())

print("\nNOTE: These are bounding-box measurements,")
print("not proof of overlap between original tile polygons.")
