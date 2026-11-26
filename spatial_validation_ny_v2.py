
import json
from pathlib import Path

import pandas as pd
from shapely.geometry import Polygon
from shapely.ops import transform, unary_union
from pyproj import Transformer

# ==================================================
# 1. Load Heatmap Result
# ==================================================

file_path = Path("heatmap_result_ny.json")

if not file_path.exists():
    raise FileNotFoundError("heatmap_result_ny.json not found!")

with open(file_path, "r", encoding="utf-8") as file:
    response = json.load(file)

data = response.get("data", {})
result = data.get("result", {})
features = result.get("map_data", {}).get("features", [])

print("=" * 65)
print("NEW YORK - ACCURATE SPATIAL VALIDATION")
print("=" * 65)

# ==================================================
# 2. Define Original AOI Polygon
# ==================================================

latitude = 40.601349
longitude = -73.475794
offset = 0.001

aoi_coordinates = [
    (longitude - offset, latitude - offset),
    (longitude + offset, latitude - offset),
    (longitude + offset, latitude + offset),
    (longitude - offset, latitude + offset),
    (longitude - offset, latitude - offset)
]

aoi_polygon = Polygon(aoi_coordinates)

print("\n========== AOI ==========")
print("AOI Valid:", aoi_polygon.is_valid)
print("AOI Bounds:", aoi_polygon.bounds)

# ==================================================
# 3. Coordinate Transformation
# ==================================================

# New York is within UTM Zone 18N
transformer = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32618",
    always_xy=True
)

def project_geometry(geometry):
    return transform(transformer.transform, geometry)

aoi_projected = project_geometry(aoi_polygon)

aoi_area_m2 = aoi_projected.area

print("AOI Area (m²):", round(aoi_area_m2, 2))

# ==================================================
# 4. Convert Tiles to Real Polygons
# ==================================================

tile_polygons = []
tile_rows = []

for feature in features:

    properties = feature.get("properties", {})
    geometry_data = feature.get("geometry", {})

    tile_id = properties.get("tile_id")
    temperature = properties.get("average_temperature")

    if geometry_data.get("type") != "Polygon":
        print("Skipping unsupported geometry:", tile_id)
        continue

    polygon_coordinates = geometry_data.get("coordinates", [])

    if not polygon_coordinates:
        continue

    tile_polygon = Polygon(polygon_coordinates[0])

    if not tile_polygon.is_valid:
        tile_polygon = tile_polygon.buffer(0)

    projected_tile = project_geometry(tile_polygon)

    tile_area_m2 = projected_tile.area

    # Actual geometric intersection
    intersection = aoi_projected.intersection(projected_tile)

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
# 5. Union Tiles (Avoid Double Counting)
# ==================================================

if tile_polygons:

    tiles_union = unary_union(tile_polygons)

    actual_intersection = aoi_projected.intersection(tiles_union)

    covered_area_m2 = actual_intersection.area

    actual_coverage_percent = (
        covered_area_m2 / aoi_area_m2 * 100
        if aoi_area_m2 > 0 else 0
    )

    uncovered_area = aoi_projected.difference(tiles_union)

    uncovered_area_m2 = uncovered_area.area

else:

    covered_area_m2 = 0
    actual_coverage_percent = 0
    uncovered_area_m2 = aoi_area_m2

# ==================================================
# 6. Check Tile Overlaps
# ==================================================

sum_intersections = tiles_df["intersection_area_m2"].sum()

overlap_inside_aoi_m2 = max(
    0,
    sum_intersections - covered_area_m2
)

# ==================================================
# 7. Display Results
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

    print(tiles_df[display_columns].round(3).to_string(index=False))

print("\n========== OVERALL COVERAGE ==========")

print("Number of tiles:", len(tile_polygons))
print("AOI Area (m²):", round(aoi_area_m2, 3))
print("Covered Area (m²):", round(covered_area_m2, 3))
print("Uncovered Area (m²):", round(uncovered_area_m2, 3))
print("Coverage Percentage:", round(actual_coverage_percent, 4), "%")
print("Uncovered Percentage:", round(100 - actual_coverage_percent, 4), "%")

print("\nOverlapping area inside AOI (m²):",
      round(overlap_inside_aoi_m2, 3))

# ==================================================
# 8. Coverage Classification
# ==================================================

if actual_coverage_percent >= 99.99:
    coverage_status = "FULL COVERAGE"

elif actual_coverage_percent > 0:
    coverage_status = "PARTIAL COVERAGE"

else:
    coverage_status = "NO COVERAGE"

print("\nCoverage Status:", coverage_status)

# ==================================================
# 9. Save CSV
# ==================================================

tiles_df.to_csv("spatial_validation_ny_v2.csv", index=False)

# ==================================================
# 10. Save JSON Report
# ==================================================

report = {
    "location": "New York",
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

with open("spatial_validation_ny_v2.json", "w", encoding="utf-8") as file:
    json.dump(report, file, indent=4)

print("\n========== EXPORT ==========")
print("CSV: spatial_validation_ny_v2.csv")
print("JSON: spatial_validation_ny_v2.json")

print("\n" + "=" * 65)
print("SPATIAL VALIDATION COMPLETED")
print("=" * 65)
