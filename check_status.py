
import os
import json
import requests
from dotenv import load_dotenv

# ==========================================
# 1. Load API Key
# ==========================================

load_dotenv()

API_KEY = os.getenv("FORTYGUARD_API_KEY")

if not API_KEY:
    print("Error: API key not found in .env file.")
    exit()

# ==========================================
# 2. Existing Activity ID
# ==========================================

activity_id = "ce3399cc-51cc-4549-9a60-7b604c1bdc6f"

# ==========================================
# 3. API Request
# ==========================================
ACTIVITY_ID = "ba10be6e-0172-493a-9343-61034cf06c47"

url = f"https://api.fortyguard.com/v1/status/{ACTIVITY_ID}"

headers = {
    "api-key": API_KEY,
    "Content-Type": "application/json"
}

print("=" * 50)
print("FORTYGUARD HEATMAP STATUS CHECK")
print("=" * 50)

try:
    response = requests.get(url, headers=headers, timeout=60)

    print("\nHTTP Status Code:", response.status_code)

    response.raise_for_status()

    result = response.json()

    # ==========================================
    # 4. Display Important Information
    # ==========================================

    print("\n========== TASK INFORMATION ==========")

    print("Activity ID:", ACTIVITY_ID)
    print("Status:", result.get("status", "Not found"))
    print("Message:", result.get("message", "Not found"))

    print("\n========== RESPONSE KEYS ==========")
    print(list(result.keys()))

    # ==========================================
    # 5. Save Full Response
    # ==========================================

    output_file = "heatmap_result.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print("\nFull response saved to:", output_file)

    # ==========================================
    # 6. Display First 3000 Characters
    # ==========================================

    print("\n========== RESPONSE PREVIEW ==========")

    preview = json.dumps(result, indent=2, ensure_ascii=False)

    print(preview[:3000])

    if len(preview) > 3000:
        print("\n... Remaining response is saved in heatmap_result.json")

    print("\n" + "=" * 50)
    print("STATUS CHECK FINISHED")
    print("=" * 50)

except requests.exceptions.HTTPError as error:
    print("\nHTTP Error:", error)
    print("Response:", response.text[:2000])

except requests.exceptions.RequestException as error:
    print("\nConnection Error:", error)

except json.JSONDecodeError:
    print("\nError: API did not return valid JSON.")
    print(response.text[:2000])

except Exception as error:
    print("\nUnexpected Error:", error)
