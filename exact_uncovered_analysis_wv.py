
import json
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import box, shape
from shapely.ops import transform, unary_union

# ==========================================
# 1. Original API AOI
# ==========================================

WEST = -81.623467
EAST = -81.613467
SOUTH = 38.359224
NORTH = 38.369224

GEOJSON_FILE = Path("recovered_wv/heatmap_polygons_wv.geojson")

# ==========================================
# 2. Load original polygons
# ==========================================

with open(GEOJSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

tiles = [
    shape(feature["geometry"])
    for feature in data["features"]
    if feature.get("geometry")
]

print("Loaded tiles:", len(tiles))

# ==========================================
# 3. Build and project AOI
# ==========================================

aoi = box(WEST, SOUTH, EAST, NORTH)

to_utm = Transformer.from_crs(
    "EPSG:4326", "EPSG:32617", always_xy=True
)

to_wgs84 = Transformer.from_crs(
    "EPSG:32617", "EPSG:4326", always_xy=True
)

aoi_m = transform(to_utm.transform, aoi)

tiles_m = [
    transform(to_utm.transform, tile)
    for tile in tiles
]

# ==========================================
# 4. Calculate uncovered geometry
# ==========================================

tiles_union = unary_union(tiles_m)
uncovered = aoi_m.difference(tiles_union)

if uncovered.is_empty:
    regions = []
elif uncovered.geom_type == "Polygon":
    regions = [uncovered]
elif uncovered.geom_type == "MultiPolygon":
    regions = list(uncovered.geoms)
else:
    regions = [
        geom for geom in getattr(uncovered, "geoms", [])
        if geom.geom_type == "Polygon"
    ]

regions.sort(key=lambda geom: geom.area, reverse=True)

# ==========================================
# 5. Print results
# ==========================================

print("\n" + "=" * 60)
print("WEST VIRGINIA - UNCOVERED AREA ANALYSIS")
print("=" * 60)

print("Number of uncovered regions:", len(regions))
print("Total uncovered area:", round(uncovered.area, 3), "m2")
print(
    "Uncovered percentage:",
    round(uncovered.area / aoi_m.area * 100, 3),
    "%"
)

print("\nINDIVIDUAL REGIONS")

for i, region in enumerate(regions, 1):
    centroid = region.centroid

    lon, lat = to_wgs84.transform(
        centroid.x, centroid.y
    )

    print("\nRegion:", i)
    print("Area:", round(region.area, 3), "m2")
    print("Latitude:", round(lat, 8))
    print("Longitude:", round(lon, 8))

# ==========================================
# 6. Save uncovered geometry
# ==========================================

output_dir = Path("exact_wv_original_aoi_analysis")
output_dir.mkdir(exist_ok=True)

uncovered_wgs84 = transform(
    to_wgs84.transform,
    uncovered
)

output_geojson = {
    "type": "FeatureCollection",
    "features": []
}

if not uncovered.is_empty:
    output_geojson["features"].append({
        "type": "Feature",
        "properties": {
            "uncovered_area_m2": uncovered.area,
            "region_count": len(regions)
        },
        "geometry": uncovered_wgs84.__geo_interface__
    })

output_file = output_dir / "wv_uncovered_regions.geojson"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output_geojson, f, indent=2)

print("\nSaved:", output_file)
print("\nVALIDATION COMPLETED")
