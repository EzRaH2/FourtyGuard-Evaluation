import json
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import box
from shapely.ops import transform, unary_union
from pyproj import Transformer

# ==================================================
# 1. Load Existing West Virginia Spatial Data
# ==================================================

file_path = Path("heatmap_spatial_analysis.csv")

if not file_path.exists():
    raise FileNotFoundError("heatmap_spatial_analysis.csv not found!")

df = pd.read_csv(file_path)

print("=" * 65)
print("WEST VIRGINIA - SPATIAL VALIDATION")
print("=" * 65)

# ==================================================
# 2. Define Original AOI
# ==================================================

latitude = 38.359224
longitude = -81.623467
offset = 0.01

aoi_polygon = box(
    longitude - offset,
    latitude - offset,
    longitude + offset,
    latitude + offset
)

print("\n========== AOI ==========")
print("AOI Valid:", aoi_polygon.is_valid)
print("AOI Bounds:", aoi_polygon.bounds)

# ==================================================
# 3. Coordinate Transformation
# ==================================================

# West Virginia: UTM Zone 17N

transformer = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32617",
    always_xy=True
)

def project_geometry(geometry):
    return transform(transformer.transform, geometry)

aoi_projected = project_geometry(aoi_polygon)

aoi_area_m2 = aoi_projected.area

print("AOI Area (m²):", round(aoi_area_m2, 2))

# ==================================================
# 4. Reconstruct Tile Polygons from CSV Boundaries
# ==================================================

tile_polygons = []
tile_rows = []

for _, row in df.iterrows():

    tile_id = row["tile_id"]
    temperature = row["temperature"]

    min_lat = row["min_lat"]
    max_lat = row["max_lat"]

    min_lon = row["min_lon"]
    max_lon = row["max_lon"]

    # Reconstruct rectangular tile from saved boundaries

    tile_polygon = box(
        min_lon,
        min_lat,
        max_lon,
        max_lat
    )

    if not tile_polygon.is_valid:
        tile_polygon = tile_polygon.buffer(0)

    projected_tile = project_geometry(tile_polygon)

    tile_area_m2 = projected_tile.area

    # Intersection with AOI

    intersection = aoi_projected.intersection(
        projected_tile
    )

    intersection_area_m2 = intersection.area

    tile_coverage_percent = (
        intersection_area_m2 / tile_area_m2 * 100
        if tile_area_m2 > 0 else 0
    )

    aoi_coverage_percent = (
        intersection_area_m2 / aoi_area_m2 * 100
        if aoi_area_m2 > 0 else 0
    )

    tile_polygons.append(projected_tile)

    tile_rows.append({
        "tile_id": tile_id,
        "temperature": temperature,
        "tile_area_m2": tile_area_m2,
        "intersection_area_m2": intersection_area_m2,
        "tile_coverage_percent": tile_coverage_percent,
        "aoi_coverage_percent": aoi_coverage_percent,
        "intersects_aoi": not intersection.is_empty
    })

tiles_df = pd.DataFrame(tile_rows)

# ==================================================
# 5. Union Tiles - Avoid Double Counting
# ==================================================

if tile_polygons:

    tiles_union = unary_union(tile_polygons)

    actual_intersection = aoi_projected.intersection(
        tiles_union
    )

    covered_area_m2 = actual_intersection.area

    actual_coverage_percent = (
        covered_area_m2 / aoi_area_m2 * 100
        if aoi_area_m2 > 0 else 0
    )

    uncovered_area = aoi_projected.difference(
        tiles_union
    )

    uncovered_area_m2 = uncovered_area.area

else:

    covered_area_m2 = 0
    actual_coverage_percent = 0
    uncovered_area_m2 = aoi_area_m2

# ==================================================
# 6. Check Tile Overlaps Inside AOI
# ==================================================

sum_intersections = tiles_df[
    "intersection_area_m2"
].sum()

overlap_inside_aoi_m2 = max(
    0,
    sum_intersections - covered_area_m2
)

# ==================================================
# 7. Display Tile Details
# ==================================================

print("\n========== TILE DETAILS ==========")

if not tiles_df.empty:

    display_columns = [
        "tile_id",
        "temperature",
        "tile_area_m2",
        "intersection_area_m2",
        "tile_coverage_percent",
        "aoi_coverage_percent",
        "intersects_aoi"
    ]

    print(
        tiles_df[display_columns]
        .round(3)
        .to_string(index=False)
    )

# ==================================================
# 8. Overall Coverage
# ==================================================

print("\n========== OVERALL COVERAGE ==========")

print("Number of tiles:", len(tile_polygons))
print("AOI Area (m²):", round(aoi_area_m2, 3))
print("Covered Area (m²):", round(covered_area_m2, 3))
print("Uncovered Area (m²):", round(uncovered_area_m2, 3))
print("Coverage Percentage:", round(actual_coverage_percent, 4), "%")
print("Uncovered Percentage:", round(100 - actual_coverage_percent, 4), "%")

print(
    "Overlapping area inside AOI (m²):",
    round(overlap_inside_aoi_m2, 3)
)

# ==================================================
# 9. Coverage Classification
# ==================================================

if actual_coverage_percent >= 99.99:

    coverage_status = "FULL COVERAGE"

elif actual_coverage_percent > 0:

    coverage_status = "PARTIAL COVERAGE"

else:

    coverage_status = "NO COVERAGE"

print("\nCoverage Status:", coverage_status)

# ==================================================
# 10. Temperature Analysis
# ==================================================

if not tiles_df.empty:

    temperatures = tiles_df["temperature"]

    print("\n========== TEMPERATURE ANALYSIS ==========")

    print("Mean:", round(temperatures.mean(), 4))
    print("Min:", round(temperatures.min(), 4))
    print("Max:", round(temperatures.max(), 4))
    print("Std:", round(temperatures.std(), 4))

# ==================================================
# 11. Export CSV
# ==================================================

tiles_df.to_csv(
    "spatial_validation_wv.csv",
    index=False
)

# ==================================================
# 12. Export JSON Report
# ==================================================

report = {
    "location": "West Virginia",
    "aoi_area_m2": aoi_area_m2,
    "covered_area_m2": covered_area_m2,
    "uncovered_area_m2": uncovered_area_m2,
    "coverage_percentage": actual_coverage_percent,
    "uncovered_percentage": 100 - actual_coverage_percent,
    "overlap_inside_aoi_m2": overlap_inside_aoi_m2,
    "number_of_tiles": len(tile_polygons),
    "coverage_status": coverage_status,
    "tiles": tile_rows
}

with open(
    "spatial_validation_wv.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(report, file, indent=4)

# ==================================================
# 13. Visualization
# ==================================================

fig, ax = plt.subplots(figsize=(10, 10))

# AOI

aoi_x, aoi_y = aoi_projected.exterior.xy

ax.plot(
    aoi_x,
    aoi_y,
    linewidth=2,
    label="AOI Boundary"
)

# Tiles

for i, tile in enumerate(tile_polygons):

    tile_x, tile_y = tile.exterior.xy

    ax.plot(
        tile_x,
        tile_y,
        linewidth=0.8,
        alpha=0.7
    )

# Covered area

if not actual_intersection.is_empty:

    geometries = (
        [actual_intersection]
        if actual_intersection.geom_type == "Polygon"
        else list(actual_intersection.geoms)
    )

    for geometry in geometries:

        x, y = geometry.exterior.xy

        ax.fill(
            x,
            y,
            alpha=0.35,
            label="Covered Area" if i == 0 else None
        )

ax.set_title("West Virginia - Spatial Coverage Validation")
ax.set_xlabel("UTM Easting (meters)")
ax.set_ylabel("UTM Northing (meters)")
ax.legend()
ax.grid(True)

plt.tight_layout()

plt.savefig(
    "spatial_validation_wv.png",
    dpi=300
)

plt.show()

# ==================================================
# 14. Final
# ==================================================

print("\n========== EXPORT ==========")
print("CSV: spatial_validation_wv.csv")
print("JSON: spatial_validation_wv.json")
print("Image: spatial_validation_wv.png")

print("\n" + "=" * 65)
print("WEST VIRGINIA SPATIAL VALIDATION COMPLETED")
print("=" * 65)