
import pandas as pd
import numpy as np

df = pd.read_csv("heatmap_spatial_analysis.csv")
df = df.sort_values("tile_id").reset_index(drop=True)

mean_lat = df["center_lat"].mean()

# Convert bounding-box dimensions to approximate meters
df["width_m"] = (
    (df["max_lon"] - df["min_lon"])
    * 111320
    * np.cos(np.radians(mean_lat))
)

df["height_m"] = (
    (df["max_lat"] - df["min_lat"])
    * 111320
)

# Convert centers to approximate local metric coordinates
df["x"] = (
    (df["center_lon"] - df["center_lon"].mean())
    * 111320
    * np.cos(np.radians(mean_lat))
)

df["y"] = (
    (df["center_lat"] - df["center_lat"].mean())
    * 111320
)

print("=" * 65)
print("TILE GEOMETRY CONSISTENCY")
print("=" * 65)

print("\n========== DIMENSION STATISTICS ==========")

for col in ["width_m", "height_m"]:
    print(f"\n{col}")
    print(f"Mean: {df[col].mean():.4f} m")
    print(f"Min:  {df[col].min():.4f} m")
    print(f"Max:  {df[col].max():.4f} m")
    print(f"Std:  {df[col].std():.6f} m")

print("\n========== HORIZONTAL BOUNDARY CHECK ==========")

horizontal_results = []

for row in range(9):
    for col in range(8):
        i = row * 9 + col
        j = i + 1

        a = df.iloc[i]
        b = df.iloc[j]

        center_distance = b["x"] - a["x"]

        expected_half_widths = (
            a["width_m"] + b["width_m"]
        ) / 2

        overlap = expected_half_widths - center_distance

        horizontal_results.append(overlap)

print("Mean calculated overlap:",
      np.mean(horizontal_results), "m")

print("Min calculated overlap:",
      np.min(horizontal_results), "m")

print("Max calculated overlap:",
      np.max(horizontal_results), "m")

print("\n========== VERTICAL BOUNDARY CHECK ==========")

vertical_results = []

for row in range(8):
    for col in range(9):
        i = row * 9 + col
        j = i + 9

        a = df.iloc[i]
        b = df.iloc[j]

        center_distance = b["y"] - a["y"]

        expected_half_heights = (
            a["height_m"] + b["height_m"]
        ) / 2

        overlap = expected_half_heights - center_distance

        vertical_results.append(overlap)

print("Mean calculated overlap:",
      np.mean(vertical_results), "m")

print("Min calculated overlap:",
      np.min(vertical_results), "m")

print("Max calculated overlap:",
      np.max(vertical_results), "m")

print("\n========== INTERPRETATION ==========")

print(
    "These calculations use CSV bounding-box dimensions "
    "and center coordinates."
)

print(
    "They do not establish overlap between original polygons."
)

print("\nValidation completed.")
