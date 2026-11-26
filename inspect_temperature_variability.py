import json
from pathlib import Path
from shapely.geometry import shape

file_path = Path("recovered_wv/heatmap_result_wv_recovered.json")

with open(file_path, encoding="utf-8") as f:
    data = json.load(f)

features = data["data"]["result"]["map_data"]["features"]

print("=" * 60)
print("TEMPERATURE & GEOMETRY VALIDATION")
print("=" * 60)

print("Total tiles:", len(features))

avg_temps = [f["properties"]["average_temperature"] for f in features]
min_temps = [f["properties"]["min_temperature"] for f in features]
max_temps = [f["properties"]["max_temperature"] for f in features]

print("\nTEMPERATURE ANALYSIS")
print("-" * 40)
print("Unique average temperatures:", sorted(set(avg_temps)))
print("Unique minimum temperatures:", sorted(set(min_temps)))
print("Unique maximum temperatures:", sorted(set(max_temps)))

geometries = [shape(f["geometry"]) for f in features]
geometry_keys = [g.wkb for g in geometries]

print("\nGEOMETRY ANALYSIS")
print("-" * 40)
print("Total geometries:", len(geometries))
print("Unique geometries:", len(set(geometry_keys)))
print("Invalid geometries:", sum(not g.is_valid for g in geometries))
print("Empty geometries:", sum(g.is_empty for g in geometries))

print("\nDUPLICATE GEOMETRIES")
print("-" * 40)
print("Duplicate count:", len(geometry_keys) - len(set(geometry_keys)))

print("\nTEMPERATURE VARIABILITY")
print("-" * 40)
print("Mean:", sum(avg_temps) / len(avg_temps))
print("Min:", min(avg_temps))
print("Max:", max(avg_temps))
print("Range:", max(avg_temps) - min(avg_temps))

print("\n" + "=" * 60)
print("VALIDATION COMPLETED")
print("=" * 60)
