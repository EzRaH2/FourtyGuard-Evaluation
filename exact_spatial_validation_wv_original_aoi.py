
import json
from pathlib import Path

import pandas as pd
from shapely.geometry import shape, box
from shapely.ops import transform, unary_union
from pyproj import Transformer

# ==================================================
# 1. CONFIGURATION - ORIGINAL API AOI
# ==================================================

GEOJSON_FILE = Path(
    "recovered_wv/heatmap_polygons_wv.geojson"
)

OUTPUT_DIR = Path("exact_wv_original_aoi_analysis")
OUTPUT_DIR.mkdir(exist_ok=True)

# Exact coordinates recovered from original request
WEST = -81.623467
EAST = -81.613467
SOUTH = 38.359224
NORTH = 38.369224

transformer = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32617",
    always_xy=True
)

def project(geometry):
    return transform(
        transformer.transform,
        geometry
    )

# ==================================================
# 2. LOAD ORIGINAL GEOJSON
# ==================================================

with open(GEOJSON_FILE, "r", encoding="utf-8") as f:
    geojson = json.load(f)

features = geojson.get("features", [])

if not features:
    raise ValueError("No GeoJSON features found.")

# ==================================================
# 3. BUILD EXACT ORIGINAL AOI
# ==================================================

aoi_wgs84 = box(
    WEST,
    SOUTH,
    EAST,
    NORTH
)

aoi = project(aoi_wgs84)

if not aoi.is_valid:
    raise ValueError("Invalid AOI geometry.")

# ==================================================
# 4. LOAD ORIGINAL TILE POLYGONS
# ==================================================

tile_records = []
tile_geometries = []

for index, feature in enumerate(features):

    geometry_data = feature.get("geometry")

    if not geometry_data:
        continue

    tile = project(shape(geometry_data))

    if tile.is_empty:
        continue

    if not tile.is_valid:
        raise ValueError(
            f"Invalid tile geometry at index {index}"
        )

    properties = feature.get("properties", {})

    tile_id = properties.get("tile_id", index)

    temperature = properties.get(
        "average_temperature"
    )

    intersection = tile.intersection(aoi)

    tile_geometries.append(tile)

    tile_records.append({
        "tile_id": tile_id,
        "temperature": temperature,
        "tile_area_m2": tile.area,
        "intersection_area_m2": intersection.area,
        "intersects_aoi": tile.intersects(aoi),
        "tile_coverage_percent": (
            intersection.area / tile.area * 100
            if tile.area else 0
        ),
        "aoi_coverage_percent": (
            intersection.area / aoi.area * 100
        )
    })

if not tile_geometries:
    raise ValueError("No valid tile geometries.")

# ==================================================
# 5. UNION-BASED COVERAGE
# ==================================================

tiles_union = unary_union(tile_geometries)

covered_geometry = tiles_union.intersection(aoi)

covered_area = covered_geometry.area

uncovered_area = aoi.difference(
    tiles_union
).area

sum_intersections = sum(
    row["intersection_area_m2"]
    for row in tile_records
)

overlap_excess = (
    sum_intersections - covered_area
)

coverage_percent = (
    covered_area / aoi.area * 100
)

uncovered_percent = (
    uncovered_area / aoi.area * 100
)

# ==================================================
# 6. TILE CLASSIFICATION
# ==================================================

fully_inside = 0
partially_intersecting = 0
outside = 0

for tile in tile_geometries:

    if not tile.intersects(aoi):
        outside += 1

    elif aoi.covers(tile):
        fully_inside += 1

    else:
        partially_intersecting += 1

# ==================================================
# 7. TEMPERATURE SUMMARY
# ==================================================

temperatures = pd.to_numeric(
    pd.Series([
        row["temperature"]
        for row in tile_records
    ]),
    errors="coerce"
).dropna()

# ==================================================
# 8. PRINT RESULTS
# ==================================================

print("=" * 65)
print("WEST VIRGINIA - ORIGINAL API AOI VALIDATION")
print("=" * 65)

print("\nORIGINAL AOI BOUNDS")
print("West:", WEST)
print("East:", EAST)
print("South:", SOUTH)
print("North:", NORTH)

print("\nINPUT DATA")
print("Features:", len(features))
print("Loaded polygons:", len(tile_geometries))

print("\nAREA RESULTS")
print("AOI area:", round(aoi.area, 3), "m2")
print("Sum intersections:", round(sum_intersections, 3), "m2")
print("Union covered area:", round(covered_area, 3), "m2")
print("Uncovered area:", round(uncovered_area, 3), "m2")
print("Overlap excess:", round(overlap_excess, 6), "m2")

print("\nCOVERAGE")
print("Coverage:", round(coverage_percent, 4), "%")
print("Uncovered:", round(uncovered_percent, 4), "%")

print("\nTILE CLASSIFICATION")
print("Fully inside:", fully_inside)
print("Partially intersecting:", partially_intersecting)
print("Outside:", outside)

print("\nTEMPERATURE")
if not temperatures.empty:
    print("Count:", len(temperatures))
    print("Mean:", temperatures.mean())
    print("Min:", temperatures.min())
    print("Max:", temperatures.max())
    print("Std:", temperatures.std(ddof=0))

# ==================================================
# 9. AREA IDENTITY CHECK
# ==================================================

identity_error = (
    aoi.area - covered_area - uncovered_area
)

print("\nAREA IDENTITY CHECK")
print("Difference:", round(identity_error, 8), "m2")
print(
    "Result:",
    "PASS" if abs(identity_error) < 0.01 else "CHECK"
)

# ==================================================
# 10. EXPORT RESULTS
# ==================================================

df = pd.DataFrame(tile_records)

csv_path = OUTPUT_DIR / "wv_original_aoi_tile_analysis.csv"
json_path = OUTPUT_DIR / "wv_original_aoi_summary.json"

df.to_csv(csv_path, index=False)

summary = {
    "source": str(GEOJSON_FILE),
    "aoi_bounds": {
        "west": WEST,
        "east": EAST,
        "south": SOUTH,
        "north": NORTH
    },
    "feature_count": len(features),
    "loaded_polygon_count": len(tile_geometries),
    "aoi_area_m2": aoi.area,
    "covered_area_m2": covered_area,
    "uncovered_area_m2": uncovered_area,
    "sum_individual_intersections_m2": sum_intersections,
    "overlap_excess_area_m2": overlap_excess,
    "coverage_percent": coverage_percent,
    "uncovered_percent": uncovered_percent,
    "fully_inside": fully_inside,
    "partially_intersecting": partially_intersecting,
    "outside": outside,
    "temperature": {
        "count": int(len(temperatures)),
        "mean": float(temperatures.mean()),
        "min": float(temperatures.min()),
        "max": float(temperatures.max()),
        "std": float(temperatures.std(ddof=0))
    } if not temperatures.empty else {},
    "area_identity_error_m2": identity_error,
    "area_identity_passed": abs(identity_error) < 0.01
}

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=4)

print("\nOUTPUT FILES")
print(csv_path)
print(json_path)

print("\nVALIDATION COMPLETED")
