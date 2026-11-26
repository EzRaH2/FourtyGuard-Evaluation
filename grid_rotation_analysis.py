
import pandas as pd
import numpy as np
from pyproj import Transformer

df = pd.read_csv("heatmap_spatial_analysis.csv")
df = df.sort_values("tile_id").reset_index(drop=True)

ROWS = 9
COLS = 9

transformer = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32617",
    always_xy=True
)

df["x"], df["y"] = transformer.transform(
    df["center_lon"].values,
    df["center_lat"].values
)

horizontal_dx = []
horizontal_dy = []

vertical_dx = []
vertical_dy = []

# Horizontal center-to-center vectors
for row in range(ROWS):
    for col in range(COLS - 1):
        i = row * COLS + col
        j = i + 1

        horizontal_dx.append(df.loc[j, "x"] - df.loc[i, "x"])
        horizontal_dy.append(df.loc[j, "y"] - df.loc[i, "y"])

# Vertical center-to-center vectors
for row in range(ROWS - 1):
    for col in range(COLS):
        i = row * COLS + col
        j = i + COLS

        vertical_dx.append(df.loc[j, "x"] - df.loc[i, "x"])
        vertical_dy.append(df.loc[j, "y"] - df.loc[i, "y"])

horizontal_dx = np.array(horizontal_dx)
horizontal_dy = np.array(horizontal_dy)

vertical_dx = np.array(vertical_dx)
vertical_dy = np.array(vertical_dy)

# Mean vector components
h_dx = horizontal_dx.mean()
h_dy = horizontal_dy.mean()

v_dx = vertical_dx.mean()
v_dy = vertical_dy.mean()

# Angles relative to east and north
horizontal_angle = np.degrees(np.arctan2(h_dy, h_dx))
vertical_angle = np.degrees(np.arctan2(v_dx, v_dy))

print("=" * 65)
print("GRID ROTATION ANALYSIS")
print("=" * 65)

print("\nHORIZONTAL MOVEMENT")
print(f"Mean dx: {h_dx:.4f} m")
print(f"Mean dy: {h_dy:.4f} m")
print(f"Mean distance: {np.hypot(h_dx, h_dy):.4f} m")
print(f"Angle from east: {horizontal_angle:.4f} degrees")

print("\nVERTICAL MOVEMENT")
print(f"Mean dx: {v_dx:.4f} m")
print(f"Mean dy: {v_dy:.4f} m")
print(f"Mean distance: {np.hypot(v_dx, v_dy):.4f} m")
print(f"Angle from north: {vertical_angle:.4f} degrees")

print("\nVECTOR CONSISTENCY")
print(f"Horizontal dx range: {horizontal_dx.min():.4f} to {horizontal_dx.max():.4f}")
print(f"Horizontal dy range: {horizontal_dy.min():.4f} to {horizontal_dy.max():.4f}")
print(f"Vertical dx range: {vertical_dx.min():.4f} to {vertical_dx.max():.4f}")
print(f"Vertical dy range: {vertical_dy.min():.4f} to {vertical_dy.max():.4f}")

print("\nAnalysis completed.")
