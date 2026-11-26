
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# ==========================================
# 1. Configuration
# ==========================================

load_dotenv()

API_KEY = os.getenv("FORTYGUARD_API_KEY")

ACTIVITY_ID = "d217d8b4-bf08-41f6-83ca-67975221d616"

BASE_URL = "https://api.fortyguard.com/v1/status"

OUTPUT_DIR = Path("recovered_wv")
OUTPUT_DIR.mkdir(exist_ok=True)

RAW_FILE = OUTPUT_DIR / "heatmap_result_wv_recovered.json"
GEOJSON_FILE = OUTPUT_DIR / "heatmap_polygons_wv.geojson"

# ==========================================
# 2. Validate API Key
# ==========================================

if not API_KEY:
    raise SystemExit("ERROR: API key not found in .env file.")

# ==========================================
# 3. Request Existing Activity
# ==========================================

url = f"{BASE_URL}/{ACTIVITY_ID}"

headers = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

print("=" * 60)
print("WEST VIRGINIA HEATMAP RECOVERY")
print("=" * 60)

print("\nActivity ID:", ACTIVITY_ID)
print("Sending GET request to retrieve existing activity...")

try:
    response = requests.get(
        url,
        headers=headers,
        timeout=60
    )

    print("\nHTTP Status Code:", response.status_code)

    # Save the response body even if the server returns an HTTP error.
    try:
        result = response.json()
    except ValueError:
        print("\nThe API did not return valid JSON.")
        print(response.text[:3000])
        raise SystemExit(1)

    # ==========================================
    # 4. Save Raw Response Safely
    # ==========================================

    with open(RAW_FILE, "w", encoding="utf-8") as file:
        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nRaw response saved to:")
    print(RAW_FILE)

    if not response.ok:
        print("\nRequest returned an HTTP error.")
        print(json.dumps(result, indent=2, ensure_ascii=False)[:3000])
        raise SystemExit(1)

    # ==========================================
    # 5. Display Activity Information
    # ==========================================

    print("\n========== ACTIVITY INFORMATION ==========")

    print("Top-level keys:", list(result.keys()))

    print("Status:", result.get("status", "Not found"))
    print("Message:", result.get("message", "Not found"))

    data = result.get("data", {})

    if isinstance(data, dict):
        print("Data keys:", list(data.keys()))

        print(
            "Activity ID in response:",
            data.get("activity_id", "Not found")
        )

    # ==========================================
    # 6. Search for GeoJSON Features
    # ==========================================

    def find_feature_collections(obj, path="root"):
        found = []

        if isinstance(obj, dict):

            if (
                obj.get("type") == "FeatureCollection"
                and isinstance(obj.get("features"), list)
            ):
                found.append((path, obj))

            if (
                isinstance(obj.get("features"), list)
                and obj.get("features")
                and all(
                    isinstance(item, dict)
                    and item.get("type") == "Feature"
                    for item in obj["features"]
                )
            ):
                found.append((path, {
                    "type": "FeatureCollection",
                    "features": obj["features"]
                }))

            for key, value in obj.items():
                found.extend(
                    find_feature_collections(
                        value,
                        f"{path}.{key}"
                    )
                )

        elif isinstance(obj, list):

            for index, value in enumerate(obj):
                found.extend(
                    find_feature_collections(
                        value,
                        f"{path}[{index}]"
                    )
                )

        return found

    collections = find_feature_collections(result)

    # ==========================================
    # 7. Save Original GeoJSON
    # ==========================================

    if collections:

        # Prefer the collection containing the largest number of features.
        collections.sort(
            key=lambda item: len(item[1]["features"]),
            reverse=True
        )

        geojson_path, geojson = collections[0]

        features = geojson["features"]

        with open(GEOJSON_FILE, "w", encoding="utf-8") as file:
            json.dump(
                geojson,
                file,
                indent=4,
                ensure_ascii=False
            )

        print("\n========== GEOJSON RECOVERY ==========")
        print("GeoJSON found at:", geojson_path)
        print("Number of features:", len(features))
        print("GeoJSON saved to:", GEOJSON_FILE)

        if features:
            print(
                "First feature geometry type:",
                features[0].get("geometry", {}).get("type")
            )

            print(
                "First feature properties:",
                features[0].get("properties", {})
            )

    else:

        print("\n========== GEOJSON NOT FOUND ==========")
        print("No GeoJSON FeatureCollection was found in the response.")
        print("The complete raw response is preserved.")
        print("We need to inspect its structure before deciding the next step.")

    # ==========================================
    # 8. Final Summary
    # ==========================================

    print("\n" + "=" * 60)
    print("RECOVERY ATTEMPT FINISHED")
    print("=" * 60)

except requests.exceptions.Timeout:
    print("\nRequest timed out.")

except requests.exceptions.ConnectionError:
    print("\nConnection error. Check your internet connection.")

except requests.exceptions.RequestException as error:
    print("\nRequest error:", error)

except Exception as error:
    print("\nUnexpected error:", error)
