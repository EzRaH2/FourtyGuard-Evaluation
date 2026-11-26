
import os
import json
import requests
from dotenv import load_dotenv

# ==========================================
# 1. Load API Key
# ==========================================

load_dotenv()

api_key = os.getenv("FORTYGUARD_API_KEY")

if not api_key:
    raise ValueError(
        "API key not found. Please check your .env file."
    )

# ==========================================
# 2. API Configuration
# ==========================================

url = "https://api.fortyguard.com/v1/heatmap"

headers = {
    "api-key": api_key,
    "Content-Type": "application/json"
}

# ==========================================
# 3. Geographic Coordinates
# ==========================================

# New test location: New York
latitude = 39.9612
longitude = -82.9988

offset = 0.001

polygon_coordinates = [[
    [longitude - offset, latitude - offset],
    [longitude + offset, latitude - offset],
    [longitude + offset, latitude + offset],
    [longitude - offset, latitude + offset],
    [longitude - offset, latitude - offset]
]]

# ==========================================
# 4. Request Payload
# ==========================================

payload = {
    "polygon_aoi": {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": polygon_coordinates
                }
            }
        ]
    },

    "date_time": {
        "start_date": "2024-07-15",
        "start_time": "14:00",
        "filter_type": 1
    },

    "granularity": 100
}

# ==========================================
# 5. Send API Request
# ==========================================

print("=" * 50)
print("FORTYGUARD HEATMAP API TEST")
print("=" * 50)

print("\nLocation: New York")
print(f"Latitude:  {latitude}")
print(f"Longitude: {longitude}")

print("\nSending API request...")

try:

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60
    )

    print("\nHTTP Status Code:", response.status_code)

    # ======================================
    # 6. Parse API Response
    # ======================================

    try:
        result = response.json()

        print("\nAPI Response:")
        print(json.dumps(result, indent=4))

    except ValueError:
        result = None

        print("\nInvalid JSON response:")
        print(response.text[:2000])

    # ======================================
    # 7. Handle Successful Response
    # ======================================

    if response.ok:

        print("\nRequest accepted or completed.")

        if isinstance(result, dict):

            data = result.get("data", {})
            activity_id = data.get("activity_id")

            if activity_id:

                print("\nActivity ID:", activity_id)
                print("Next step: Check task status.")

            else:

                print("\nNo activity_id found in the response.")

    # ======================================
    # 8. Handle API Errors
    # ======================================

    else:

        print("\nAPI Request Failed.")

        if isinstance(result, dict):

            print("Error Code:", result.get("code"))
            print("Error Message:", result.get("message"))
            print("Error Field:", result.get("field"))

        else:

            print("Response:", response.text[:2000])

except requests.exceptions.Timeout:

    print("\nRequest timed out.")
    print("Do not retry until submission status is checked.")

except requests.exceptions.ConnectionError:

    print("\nConnection error.")
    print("Please check your internet connection.")

except requests.exceptions.RequestException as error:

    print("\nRequest error:", error)

print("\n" + "=" * 50)
print("TEST FINISHED")
print("=" * 50)
