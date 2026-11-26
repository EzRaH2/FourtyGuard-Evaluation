
import pandas as pd
import numpy as np
from pyproj import Transformer

# =========================================================
# 1. LOAD DATA
# =========================================================

CSV_FILE = "heatmap_spatial_analysis.csv"

df = pd.read_csv(CSV_FILE)
df = df.sort_values("tile_id").reset_index(drop=True)

print("=" * 70)
print("SPATIAL GRID VALIDATION")
print("=" * 70)

print(f"\nTotal tiles: {len(df)}")

# =========================================================
# 2. VALIDATE TILE COUNT
# =========================================================

GRID_ROWS = 9
GRID_COLS = 9

expected_tiles = GRID_ROWS * GRID_COLS

print("\n========== GRID STRUCTURE ==========")
print(f"Expected tiles: {expected_tiles}")
print(f"Actual tiles:   {len(df)}")

if len(df) == expected_tiles:
    print("Tile count: PASS")
else:
    print("Tile count: FAIL")

# =========================================================
# 3. CONVERT COORDINATES TO METERS
# =========================================================

transformer = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32617",
    always_xy=True
)

df["x"], df["y"] = transformer.transform(
    df["center_lon"].values,
    df["center_lat"].values
)

# =========================================================
# 4. CHECK HORIZONTAL NEIGHBOR DISTANCES
# =========================================================

print("\n========== HORIZONTAL DISTANCES ==========")

horizontal_distances = []

for row in range(GRID_ROWS):

    start = row * GRID_COLS
    end = start + GRID_COLS

    row_tiles = df.iloc[start:end]

    for col in range(GRID_COLS - 1):

        tile_a = row_tiles.iloc[col]
        tile_b = row_tiles.iloc[col + 1]

        distance = np.sqrt(
            (tile_b["x"] - tile_a["x"]) ** 2 +
            (tile_b["y"] - tile_a["y"]) ** 2
        )

        horizontal_distances.append(distance)

horizontal_distances = np.array(horizontal_distances)

print(f"Number of horizontal comparisons: {len(horizontal_distances)}")
print(f"Mean distance: {horizontal_distances.mean():.3f} m")
print(f"Min distance:  {horizontal_distances.min():.3f} m")
print(f"Max distance:  {horizontal_distances.max():.3f} m")
print(f"Std deviation: {horizontal_distances.std():.3f} m")

# =========================================================
# 5. CHECK VERTICAL NEIGHBOR DISTANCES
# =========================================================

print("\n========== VERTICAL DISTANCES ==========")

vertical_distances = []

for row in range(GRID_ROWS - 1):

    for col in range(GRID_COLS):

        index_a = row * GRID_COLS + col
        index_b = (row + 1) * GRID_COLS + col

        tile_a = df.iloc[index_a]
        tile_b = df.iloc[index_b]

        distance = np.sqrt(
            (tile_b["x"] - tile_a["x"]) ** 2 +
            (tile_b["y"] - tile_a["y"]) ** 2
        )

        vertical_distances.append(distance)

vertical_distances = np.array(vertical_distances)

print(f"Number of vertical comparisons: {len(vertical_distances)}")
print(f"Mean distance: {vertical_distances.mean():.3f} m")
print(f"Min distance:  {vertical_distances.min():.3f} m")
print(f"Max distance:  {vertical_distances.max():.3f} m")
print(f"Std deviation: {vertical_distances.std():.3f} m")

# =========================================================
# 6. CHECK DISTANCE CONSISTENCY
# =========================================================

print("\n========== DISTANCE CONSISTENCY ==========")

def check_consistency(distances, name):

    mean_distance = distances.mean()

    deviations = (
        np.abs(distances - mean_distance) / mean_distance
    ) * 100

    print(f"\n{name}")

    print(f"Mean: {mean_distance:.3f} m")
    print(f"Maximum deviation: {deviations.max():.2f}%")
    print(f"Pairs deviating more than 5%: {(deviations > 5).sum()}")
    print(f"Pairs deviating more than 10%: {(deviations > 10).sum()}")

    if deviations.max() <= 5:
        print("Consistency: PASS")
    else:
        print("Consistency: REVIEW REQUIRED")

    return deviations


horizontal_deviations = check_consistency(
    horizontal_distances,
    "Horizontal spacing"
)

vertical_deviations = check_consistency(
    vertical_distances,
    "Vertical spacing"
)

# =========================================================
# 7. CHECK TILE ID ORDER
# =========================================================

print("\n========== TILE ID ORDER ==========")

tile_ids = df["tile_id"].values

expected_ids = np.arange(len(df))

if np.array_equal(tile_ids, expected_ids):
    print("Tile IDs: PASS - sequential ordering")
else:
    print("Tile IDs: FAIL - missing or unexpected IDs")

print(f"First tile ID: {tile_ids[0]}")
print(f"Last tile ID:  {tile_ids[-1]}")

# =========================================================
# 8. CHECK ROW POSITION CONSISTENCY
# =========================================================

print("\n========== ROW POSITION ANALYSIS ==========")

row_data = []

for row in range(GRID_ROWS):

    start = row * GRID_COLS
    end = start + GRID_COLS

    current_row = df.iloc[start:end]

    row_data.append({
        "row": row,
        "mean_lat": current_row["center_lat"].mean(),
        "min_lon": current_row["center_lon"].min(),
        "max_lon": current_row["center_lon"].max(),
        "tile_count": len(current_row)
    })

row_df = pd.DataFrame(row_data)

print(row_df.round(6).to_string(index=False))

# =========================================================
# 9. FINAL SUMMARY
# =========================================================

print("\n========== FINAL SUMMARY ==========")

print(f"Total tiles: {len(df)}")
print(f"Grid shape: {GRID_ROWS} x {GRID_COLS}")

print(
    f"Horizontal mean spacing: "
    f"{horizontal_distances.mean():.3f} m"
)

print(
    f"Vertical mean spacing: "
    f"{vertical_distances.mean():.3f} m"
)

print(
    f"Horizontal max deviation: "
    f"{horizontal_deviations.max():.2f}%"
)

print(
    f"Vertical max deviation: "
    f"{vertical_deviations.max():.2f}%"
)

print("\nValidation completed.")
