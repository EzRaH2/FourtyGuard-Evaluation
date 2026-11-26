
import json
import matplotlib.pyplot as plt

from shapely.geometry import Polygon, shape
from shapely.ops import transform
from pyproj import Transformer


# ==============================
# 1. Load API result
# ==============================

with open("heatmap_result_ny.json", "r") as file:
    data = json.load(file)


# Search for GeoJSON features inside the JSON
def find_features(obj):

    if isinstance(obj, dict):

        if "features" in obj and isinstance(obj["features"], list):
            return obj["features"]

        for value in obj.values():
            result = find_features(value)

            if result is not None:
                return result

    elif isinstance(obj, list):

        for item in obj:
            result = find_features(item)

            if result is not None:
                return result

    return None


features = find_features(data)

if features is None:
    raise ValueError("Could not find GeoJSON features in the JSON file.")


# ==============================
# 2. Define AOI
# ==============================

latitude = 40.601349
longitude = -73.475794
offset = 0.001

aoi = Polygon([
    (longitude - offset, latitude - offset),
    (longitude + offset, latitude - offset),
    (longitude + offset, latitude + offset),
    (longitude - offset, latitude + offset)
])


# ==============================
# 3. Convert to meters (UTM)
# ==============================

transformer = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32618",
    always_xy=True
)

project_geometry = lambda geom: transform(
    transformer.transform,
    geom
)

aoi_projected = project_geometry(aoi)


# ==============================
# 4. Extract API tiles
# ==============================

tiles = []

for i, feature in enumerate(features):

    geometry = shape(feature["geometry"])

    projected_geometry = project_geometry(geometry)

    properties = feature.get("properties", {})

    temperature = properties.get(
        "avg_temperature",
        properties.get("temperature", "N/A")
    )

    tiles.append({
        "id": i,
        "geometry": projected_geometry,
        "temperature": temperature
    })


# ==============================
# 5. Calculate spatial coverage
# ==============================

tile_union = tiles[0]["geometry"]

for tile in tiles[1:]:
    tile_union = tile_union.union(tile["geometry"])

covered_area = aoi_projected.intersection(tile_union)

uncovered_area = aoi_projected.difference(tile_union)

coverage_percent = (
    covered_area.area / aoi_projected.area
) * 100


print("=" * 45)
print("SPATIAL VISUALIZATION")
print("=" * 45)

print(f"Number of tiles: {len(tiles)}")
print(f"AOI area: {aoi_projected.area:.2f} m²")
print(f"Covered area: {covered_area.area:.2f} m²")
print(f"Uncovered area: {uncovered_area.area:.2f} m²")
print(f"Coverage: {coverage_percent:.3f}%")


# ==============================
# 6. Plot
# ==============================

fig, ax = plt.subplots(figsize=(12, 9))


# AOI
x, y = aoi_projected.exterior.xy

ax.plot(
    x,
    y,
    linewidth=2.5,
    label="AOI Boundary"
)

ax.fill(
    x,
    y,
    alpha=0.10
)


# Uncovered AOI
if not uncovered_area.is_empty:

    geometries = (
        list(uncovered_area.geoms)
        if hasattr(uncovered_area, "geoms")
        else [uncovered_area]
    )

    for geom in geometries:

        if geom.geom_type == "Polygon":

            ux, uy = geom.exterior.xy

            ax.fill(
                ux,
                uy,
                alpha=0.3,
                hatch="///",
                label="Uncovered AOI"
            )


# API Tiles
for tile in tiles:

    geom = tile["geometry"]

    polygons = (
        list(geom.geoms)
        if hasattr(geom, "geoms")
        else [geom]
    )

    for polygon in polygons:

        if polygon.geom_type != "Polygon":
            continue

        tx, ty = polygon.exterior.xy

        ax.fill(
            tx,
            ty,
            alpha=0.45,
            label=f"Tile {tile['id']}"
        )

        ax.plot(
            tx,
            ty,
            linewidth=1.5
        )

    centroid = geom.centroid

    ax.text(
        centroid.x,
        centroid.y,
        f"Tile {tile['id']}\n{tile['temperature']}°C",
        ha="center",
        va="center",
        fontsize=9
    )


# ==============================
# 7. Final settings
# ==============================

ax.set_title(
    f"FortyGuard Spatial Coverage - New York\n"
    f"Coverage: {coverage_percent:.3f}%"
)

ax.set_xlabel("Easting (meters)")
ax.set_ylabel("Northing (meters)")

ax.set_aspect("equal")

ax.grid(True, alpha=0.3)

# Remove duplicate legend entries
handles, labels = ax.get_legend_handles_labels()

plt.tight_layout()

# Save image
plt.savefig(
    "spatial_visualization_ny.png",
    dpi=300
)

plt.show()

print("\nVisualization saved successfully!")
print("File: spatial_visualization_ny.png")
