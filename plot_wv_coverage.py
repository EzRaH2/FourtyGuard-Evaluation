
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from shapely.geometry import shape, box

# ==========================================
# 1. Input files
# ==========================================

tiles_file = Path("recovered_wv/heatmap_polygons_wv.geojson")

uncovered_file = Path(
    "exact_wv_original_aoi_analysis/wv_uncovered_regions.geojson"
)

output_file = Path(
    "exact_wv_original_aoi_analysis/wv_coverage_map.png"
)

# Original API AOI
WEST = -81.623467
EAST = -81.613467
SOUTH = 38.359224
NORTH = 38.369224

# ==========================================
# 2. Load GeoJSON files
# ==========================================

with open(tiles_file, "r", encoding="utf-8") as f:
    tiles_data = json.load(f)

with open(uncovered_file, "r", encoding="utf-8") as f:
    uncovered_data = json.load(f)

tiles = [
    shape(feature["geometry"])
    for feature in tiles_data["features"]
    if feature.get("geometry")
]

uncovered = [
    shape(feature["geometry"])
    for feature in uncovered_data["features"]
    if feature.get("geometry")
]

aoi = box(WEST, SOUTH, EAST, NORTH)

print("Loaded tiles:", len(tiles))
print("Loaded uncovered geometries:", len(uncovered))

# ==========================================
# 3. Plot helpers
# ==========================================

def draw_polygon(ax, polygon, facecolor, edgecolor, linewidth, alpha, zorder):
    if polygon.is_empty:
        return

    if polygon.geom_type == "Polygon":
        polygons = [polygon]
    elif polygon.geom_type == "MultiPolygon":
        polygons = list(polygon.geoms)
    else:
        return

    for poly in polygons:
        x, y = poly.exterior.xy

        ax.fill(
            x,
            y,
            facecolor=facecolor,
            edgecolor=edgecolor,
            linewidth=linewidth,
            alpha=alpha,
            zorder=zorder
        )

        # Draw interior rings, if any
        for interior in poly.interiors:
            ix, iy = interior.xy
            ax.fill(ix, iy, facecolor="white", zorder=zorder + 1)


# ==========================================
# 4. Create map
# ==========================================

fig, ax = plt.subplots(figsize=(12, 10))

# Draw tiles
for tile in tiles:
    draw_polygon(
        ax,
        tile,
        facecolor="skyblue",
        edgecolor="navy",
        linewidth=0.45,
        alpha=0.55,
        zorder=2
    )

# Draw uncovered area
for region in uncovered:
    draw_polygon(
        ax,
        region,
        facecolor="red",
        edgecolor="darkred",
        linewidth=1.0,
        alpha=0.85,
        zorder=4
    )

# Draw original AOI boundary
x, y = aoi.exterior.xy

ax.plot(
    x,
    y,
    color="black",
    linestyle="--",
    linewidth=2.2,
    zorder=5
)

# ==========================================
# 5. Labels and formatting
# ==========================================

legend_items = [
    Patch(
        facecolor="skyblue",
        edgecolor="navy",
        alpha=0.65,
        label=f"Heatmap tiles ({len(tiles)})"
    ),
    Patch(
        facecolor="red",
        edgecolor="darkred",
        alpha=0.85,
        label="Uncovered area"
    ),
    Patch(
        facecolor="none",
        edgecolor="black",
        linestyle="--",
        label="Original AOI boundary"
    )
]

ax.legend(handles=legend_items, loc="upper right")

ax.set_title(
    "West Virginia - Original AOI Coverage Analysis",
    fontsize=15,
    fontweight="bold"
)

ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

ax.set_xlim(WEST - 0.0005, EAST + 0.0005)
ax.set_ylim(SOUTH - 0.0005, NORTH + 0.0005)

ax.set_aspect("equal", adjustable="box")
ax.grid(True, linestyle=":", alpha=0.4)

plt.tight_layout()

# ==========================================
# 6. Save map
# ==========================================

output_file.parent.mkdir(parents=True, exist_ok=True)

plt.savefig(
    output_file,
    dpi=250,
    bbox_inches="tight"
)

print("\nMap saved successfully:")
print(output_file)

plt.show()
