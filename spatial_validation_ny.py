
import json
from pathlib import Path

# ==================================================
# 1. Load New York Heatmap Result
# ==================================================

file_path = Path("heatmap_result_ny.json")

if not file_path.exists():
    print("ERROR: heatmap_result_ny.json not found!")
    exit()

with open(file_path, "r", encoding="utf-8") as file:
    response = json.load(file)

data = response.get("data", {})
result = data.get("result", {})
features = result.get("map_data", {}).get("features", [])

# ==================================================
# 2. Define Original AOI
# ==================================================

latitude = 40.601349
longitude = -73.475794
offset = 0.001

# AOI bounds
aoi_min_lat = latitude - offset
aoi_max_lat = latitude + offset

aoi_min_lon = longitude - offset
aoi_max_lon = longitude + offset

aoi_width = aoi_max_lon - aoi_min_lon
aoi_height = aoi_max_lat - aoi_min_lat

aoi_area = aoi_width * aoi_height

print("=" * 60)
print("NEW YORK SPATIAL VALIDATION")
print("=" * 60)

print("\n========== AOI INFORMATION ==========")

print("Center Latitude:", latitude)
print("Center Longitude:", longitude)

print("\nAOI Bounds:")
print("Latitude:", aoi_min_lat, "to", aoi_max_lat)
print("Longitude:", aoi_min_lon, "to", aoi_max_lon)

print("\nAOI Area (degrees squared):", aoi_area)

# ==================================================
# 3. Validate Each Tile
# ==================================================

tile_results = []

for feature in features:

    properties = feature.get("properties", {})
    geometry = feature.get("geometry", {})

    coordinates = geometry.get("coordinates", [])

    if not coordinates or not coordinates[0]:
        print("Skipping tile with missing geometry.")
        continue

    ring = coordinates[0]

    tile_lons = [point[0] for point in ring]
    tile_lats = [point[1] for point in ring]

    tile_min_lon = min(tile_lons)
    tile_max_lon = max(tile_lons)

    tile_min_lat = min(tile_lats)
    tile_max_lat = max(tile_lats)

    tile_width = tile_max_lon - tile_min_lon
    tile_height = tile_max_lat - tile_min_lat

    tile_area = tile_width * tile_height

    # ----------------------------------------------
    # Calculate intersection
    # ----------------------------------------------

    intersection_min_lon = max(aoi_min_lon, tile_min_lon)
    intersection_max_lon = min(aoi_max_lon, tile_max_lon)

    intersection_min_lat = max(aoi_min_lat, tile_min_lat)
    intersection_max_lat = min(aoi_max_lat, tile_max_lat)

    intersection_width = max(
        0,
        intersection_max_lon - intersection_min_lon
    )

    intersection_height = max(
        0,
        intersection_max_lat - intersection_min_lat
    )

    intersection_area = intersection_width * intersection_height

    # ----------------------------------------------
    # Coverage percentages
    # ----------------------------------------------

    tile_coverage = (
        intersection_area / tile_area * 100
        if tile_area > 0 else 0
    )

    aoi_coverage = (
        intersection_area / aoi_area * 100
        if aoi_area > 0 else 0
    )

    intersects = intersection_area > 0

    tile_results.append({
        "tile_id": properties.get("tile_id"),
        "temperature": properties.get("average_temperature"),
        "tile_area": tile_area,
        "intersection_area": intersection_area,
        "tile_coverage_percent": tile_coverage,
        "aoi_coverage_percent": aoi_coverage,
        "intersects_aoi": intersects,
        "min_latitude": tile_min_lat,
        "max_latitude": tile_max_lat,
        "min_longitude": tile_min_lon,
        "max_longitude": tile_max_lon
    })

# ==================================================
# 4. Display Tile Validation
# ==================================================

print("\n========== TILE VALIDATION ==========")

for tile in tile_results:

    print("\nTile ID:", tile["tile_id"])
    print("Temperature:", tile["temperature"])

    print("Tile Bounds:")
    print("Latitude:",
          tile["min_latitude"],
          "to",
          tile["max_latitude"])

    print("Longitude:",
          tile["min_longitude"],
          "to",
          tile["max_longitude"])

    print("Intersects AOI:", tile["intersects_aoi"])

    print("Tile covered by AOI (%):",
          round(tile["tile_coverage_percent"], 4))

    print("AOI covered by this tile (%):",
          round(tile["aoi_coverage_percent"], 4))

# ==================================================
# 5. Overall Validation
# ==================================================

intersecting_tiles = [
    tile for tile in tile_results
    if tile["intersects_aoi"]
]

total_intersection_area = sum(
    tile["intersection_area"]
    for tile in intersecting_tiles
)

# Note: This sum may double-count areas if tiles overlap.
approximate_coverage = (
    total_intersection_area / aoi_area * 100
    if aoi_area > 0 else 0
)

print("\n========== OVERALL VALIDATION ==========")

print("Total Tiles:", len(tile_results))
print("Intersecting Tiles:", len(intersecting_tiles))
print("Non-intersecting Tiles:",
      len(tile_results) - len(intersecting_tiles))

print("\nApproximate AOI Coverage (%):",
      round(approximate_coverage, 4))

if approximate_coverage >= 99.99:
    print("Coverage Result: AOI appears fully covered.")
elif approximate_coverage > 0:
    print("Coverage Result: AOI is partially covered.")
else:
    print("Coverage Result: No overlap with AOI.")

# ==================================================
# 6. Save Validation Report
# ==================================================

with open("spatial_validation_ny.json", "w", encoding="utf-8") as file:
    json.dump({
        "aoi": {
            "latitude": latitude,
            "longitude": longitude,
            "offset": offset,
            "bounds": {
                "min_latitude": aoi_min_lat,
                "max_latitude": aoi_max_lat,
                "min_longitude": aoi_min_lon,
                "max_longitude": aoi_max_lon
            },
            "area_degrees_squared": aoi_area
        },
        "total_tiles": len(tile_results),
        "intersecting_tiles": len(intersecting_tiles),
        "approximate_coverage_percent": approximate_coverage,
        "tiles": tile_results
    }, file, indent=4)

print("\nValidation report saved:")
print("spatial_validation_ny.json")

print("\n" + "=" * 60)
print("SPATIAL VALIDATION COMPLETED")
print("=" * 60)
