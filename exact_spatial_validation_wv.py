
import json
from pathlib import Path

import pandas as pd
from shapely.geometry import shape, box
from shapely.ops import transform, unary_union
from pyproj import Transformer

# ==================================================
# 1. CONFIGURATION
# ==================================================

GEOJSON_FILE = Path(
    "recovered_wv/heatmap_polygons_wv.geojson"
)

OUTPUT_DIR = Path("exact_wv_analysis")
OUTPUT_DIR.mkdir(exist_ok=True)

CENTER_LAT = 38.359224
CENTER_LON = -81.623467
OFFSET = 0.01

# West Virginia UTM Zone 17N
transformer = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32617",
    always_xy=True
)

# ==================================================
# 2. LOAD ORIGINAL GEOJSON
# ==================================================

print("=" * 65)
print("WEST VIRGINIA - ORIGINAL POLYGON SPATIAL VALIDATION")
print("=" * 65)

if not GEOJSON_FILE.exists():
    raise FileNotFoundError(
        f"GeoJSON file not found: {GEOJSON_FILE}"
    )

with open(GEOJSON_FILE, "r", encoding="utf-8") as file:
    geojson = json.load(file)

features = geojson.get("features", [])

if not features:
    raise ValueError("No features found in GeoJSON.")

print("\n========== INPUT DATA ==========")
print("Feature count:", len(features))
print("GeoJSON type:", geojson.get("type"))

# ==================================================
# 3. BUILD AOI
# ==================================================

aoi_wgs84 = box(
    CENTER_LON - OFFSET,
    CENTER_LAT - OFFSET,
    CENTER_LON + OFFSET,
    CENTER_LAT + OFFSET
)

aoi = transform(
    transformer.transform,
    aoi_wgs84
)

print("\n========== AOI ==========")
print("AOI valid:", aoi.is_valid)
print("AOI area:", round(aoi.area, 3), "m2")

if not aoi.is_valid:
    raise ValueError("AOI geometry is invalid.")

# ==================================================
# 4. LOAD ORIGINAL TILE GEOMETRIES
# ==================================================

tile_records = []
tile_geometries = []

invalid_count = 0
empty_count = 0

for index, feature in enumerate(features):

    properties = feature.get("properties", {})
    geometry_data = feature.get("geometry")

    if not geometry_data:
        print(f"WARNING: Missing geometry at feature {index}")
        empty_count += 1
        continue

    geometry_wgs84 = shape(geometry_data)

    if geometry_wgs84.is_empty:
        empty_count += 1
        continue

    geometry_utm = transform(
        transformer.transform,
        geometry_wgs84
    )

    if not geometry_utm.is_valid:
        invalid_count += 1

    tile_id = properties.get("tile_id", index)
    temperature = properties.get("average_temperature")

    tile_geometries.append(geometry_utm)

    tile_records.append({
        "tile_id": tile_id,
        "temperature": temperature,
        "geometry_type": geometry_utm.geom_type,
        "tile_area_m2": geometry_utm.area,
        "geometry_valid": geometry_utm.is_valid
    })

print("\n========== GEOMETRY VALIDATION ==========")
print("Loaded geometries:", len(tile_geometries))
print("Invalid geometries:", invalid_count)
print("Empty geometries:", empty_count)

if invalid_count > 0:
    raise ValueError(
        "Invalid original geometries found. "
        "Stop and inspect before calculating coverage."
    )

if not tile_geometries:
    raise ValueError("No usable tile geometries.")

# ==================================================
# 5. INDIVIDUAL TILE INTERSECTIONS
# ==================================================

for record, polygon in zip(tile_records, tile_geometries):

    intersection = polygon.intersection(aoi)

    intersection_area = intersection.area

    record["intersection_area_m2"] = intersection_area

    record["tile_coverage_percent"] = (
        intersection_area / polygon.area * 100
        if polygon.area > 0 else 0
    )

    record["aoi_coverage_percent"] = (
        intersection_area / aoi.area * 100
    )

    record["intersects_aoi"] = polygon.intersects(aoi)

# ==================================================
# 6. UNION-BASED COVERAGE
# ==================================================

tiles_union = unary_union(tile_geometries)

if not tiles_union.is_valid:
    raise ValueError("Union geometry is invalid.")

covered_geometry = tiles_union.intersection(aoi)

covered_area = covered_geometry.area

sum_individual_intersections = sum(
    record["intersection_area_m2"]
    for record in tile_records
)

overlap_excess = (
    sum_individual_intersections - covered_area
)

uncovered_area = aoi.area - covered_area

coverage_percent = (
    covered_area / aoi.area * 100
)

uncovered_percent = (
    uncovered_area / aoi.area * 100
)

area_identity_error = (
    aoi.area - covered_area - uncovered_area
)

# ==================================================
# 7. TEMPERATURE ANALYSIS
# ==================================================

temperatures = [
    record["temperature"]
    for record in tile_records
    if record["temperature"] is not None
]

temperature_summary = {}

if temperatures:

    temperature_series = pd.to_numeric(
        pd.Series(temperatures),
        errors="coerce"
    ).dropna()

    if not temperature_series.empty:

        temperature_summary = {
            "count": int(len(temperature_series)),
            "mean": float(temperature_series.mean()),
            "min": float(temperature_series.min()),
            "max": float(temperature_series.max()),
            "std": float(temperature_series.std(ddof=0))
        }

# ==================================================
# 8. TILE CLASSIFICATION
# ==================================================

fully_inside = 0
partially_intersecting = 0
outside = 0

for polygon in tile_geometries:

    if not polygon.intersects(aoi):
        outside += 1

    elif aoi.covers(polygon):
        fully_inside += 1

    else:
        partially_intersecting += 1

# ==================================================
# 9. PRINT RESULTS
# ==================================================

print("\n========== EXACT COVERAGE RESULTS ==========")

print(
    "AOI area:",
    round(aoi.area, 3),
    "m2"
)

print(
    "Sum of individual intersections:",
    round(sum_individual_intersections, 3),
    "m2"
)

print(
    "Union intersection area:",
    round(covered_area, 3),
    "m2"
)

print(
    "Overlap excess area:",
    round(overlap_excess, 3),
    "m2"
)

print(
    "Uncovered AOI area:",
    round(uncovered_area, 3),
    "m2"
)

print(
    "Coverage:",
    round(coverage_percent, 4),
    "%"
)

print(
    "Uncovered:",
    round(uncovered_percent, 4),
    "%"
)

print("\n========== TILE CLASSIFICATION ==========")

print("Fully inside:", fully_inside)
print("Partially intersecting:", partially_intersecting)
print("Outside:", outside)

print("\n========== TEMPERATURE SUMMARY ==========")

for key, value in temperature_summary.items():
    print(f"{key}: {value}")

print("\n========== AREA IDENTITY CHECK ==========")

print(
    "AOI - (Covered + Uncovered):",
    round(area_identity_error, 6),
    "m2"
)

print(
    "Result:",
    "PASS" if abs(area_identity_error) < 0.01 else "CHECK"
)

# ==================================================
# 10. SAVE TILE ANALYSIS
# ==================================================

df = pd.DataFrame(tile_records)

csv_path = OUTPUT_DIR / "wv_original_polygon_analysis.csv"

df.to_csv(csv_path, index=False)

# ==================================================
# 11. SAVE SUMMARY JSON
# ==================================================

summary = {
    "source": str(GEOJSON_FILE),
    "feature_count": len(features),
    "loaded_geometry_count": len(tile_geometries),
    "invalid_geometry_count": invalid_count,
    "empty_geometry_count": empty_count,

    "aoi_area_m2": aoi.area,
    "sum_individual_intersections_m2":
        sum_individual_intersections,
    "covered_area_m2": covered_area,
    "overlap_excess_area_m2": overlap_excess,
    "uncovered_area_m2": uncovered_area,

    "coverage_percent": coverage_percent,
    "uncovered_percent": uncovered_percent,

    "fully_inside": fully_inside,
    "partially_intersecting": partially_intersecting,
    "outside": outside,

    "temperature": temperature_summary,

    "area_identity_error_m2": area_identity_error,
    "area_identity_check":
        abs(area_identity_error) < 0.01
}

json_path = OUTPUT_DIR / "wv_original_polygon_summary.json"

with open(json_path, "w", encoding="utf-8") as file:
    json.dump(
        summary,
        file,
        indent=4,
        ensure_ascii=False
    )

# ==================================================
# 12. FINAL
# ==================================================

print("\n========== OUTPUT FILES ==========")
print("Tile analysis:", csv_path)
print("Summary:", json_path)

print("\n" + "=" * 65)
print("ORIGINAL POLYGON VALIDATION COMPLETED")
print("=" * 65)
