
import pandas as pd
import numpy as np

# =========================================================
# 1. LOAD DATA
# =========================================================

df = pd.read_csv("heatmap_spatial_analysis.csv")
df = df.sort_values("tile_id").reset_index(drop=True)

ROWS = 9
COLS = 9

print("=" * 65)
print("TILE BOUNDARY VALIDATION")
print("=" * 65)

# =========================================================
# 2. TILE DIMENSIONS
# =========================================================

latitudes = df["center_lat"].values

mean_lat = np.mean(latitudes)

lat_height = (
    df["max_lat"] - df["min_lat"]
) * 111320

lon_width = (
    df["max_lon"] - df["min_lon"]
) * 111320 * np.cos(np.radians(mean_lat))

print("\n========== TILE DIMENSIONS ==========")

print(f"Mean tile height: {lat_height.mean():.3f} m")
print(f"Min tile height:  {lat_height.min():.3f} m")
print(f"Max tile height:  {lat_height.max():.3f} m")

print(f"\nMean tile width: {lon_width.mean():.3f} m")
print(f"Min tile width:  {lon_width.min():.3f} m")
print(f"Max tile width:  {lon_width.max():.3f} m")

# =========================================================
# 3. HORIZONTAL BOUNDARY CHECK
# =========================================================

horizontal_gaps = []

for row in range(ROWS):

    for col in range(COLS - 1):

        i = row * COLS + col
        j = i + 1

        tile_a = df.iloc[i]
        tile_b = df.iloc[j]

        # Positive = gap
        # Negative = overlap
        gap_deg = tile_b["min_lon"] - tile_a["max_lon"]

        gap_m = (
            gap_deg
            * 111320
            * np.cos(np.radians(mean_lat))
        )

        horizontal_gaps.append(gap_m)

horizontal_gaps = np.array(horizontal_gaps)

# =========================================================
# 4. VERTICAL BOUNDARY CHECK
# =========================================================

vertical_gaps = []

for row in range(ROWS - 1):

    for col in range(COLS):

        i = row * COLS + col
        j = i + COLS

        tile_a = df.iloc[i]
        tile_b = df.iloc[j]

        # Positive = gap
        # Negative = overlap
        gap_deg = tile_b["min_lat"] - tile_a["max_lat"]

        gap_m = gap_deg * 111320

        vertical_gaps.append(gap_m)

vertical_gaps = np.array(vertical_gaps)

# =========================================================
# 5. REPORT
# =========================================================

def report_gaps(gaps, direction):

    print(f"\n========== {direction} BOUNDARIES ==========")

    print(f"Total comparisons: {len(gaps)}")
    print(f"Mean gap/overlap: {gaps.mean():.6f} m")
    print(f"Minimum: {gaps.min():.6f} m")
    print(f"Maximum: {gaps.max():.6f} m")

    gap_count = np.sum(gaps > 0.01)
    overlap_count = np.sum(gaps < -0.01)
    touching_count = np.sum(np.abs(gaps) <= 0.01)

    print(f"Gaps (> 1 cm): {gap_count}")
    print(f"Overlaps (> 1 cm): {overlap_count}")
    print(f"Approximately touching: {touching_count}")

    if gap_count == 0 and overlap_count == 0:
        print("Boundary result: PASS")
    else:
        print("Boundary result: REVIEW REQUIRED")


report_gaps(horizontal_gaps, "HORIZONTAL")
report_gaps(vertical_gaps, "VERTICAL")

# =========================================================
# 6. FINAL RESULT
# =========================================================

print("\n========== FINAL SUMMARY ==========")

print("Horizontal boundary checks:", len(horizontal_gaps))
print("Vertical boundary checks:", len(vertical_gaps))

print("Total boundary comparisons:",
      len(horizontal_gaps) + len(vertical_gaps))

print("\nBoundary validation completed.")
