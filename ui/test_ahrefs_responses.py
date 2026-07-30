"""Test Ahrefs ai-responses with correct fields."""
import requests
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "qII2G3fkeGsZFBUam2ar0UryqQWtaNXK6RIkFIWU"
REPORT_ID = "019e4f11-83ad-7648-a3d4-5a0d3760861e"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# Test with correct select fields
payload = {
    "report_id": REPORT_ID,
    "data_source": ["chatgpt"],
    "country": ["tw"],
    "select": ["question", "links", "data_source", "last_updated"],
    "limit": 5,
}
r = requests.post(
    "https://api.ahrefs.com/v3/brand-radar/ai-responses",
    headers=headers,
    json=payload,
    timeout=60,
)
print(f"Status: {r.status_code}")
data = r.json()
# Print structure info
if isinstance(data, dict):
    print(f"Keys: {list(data.keys())}")
    for key, val in data.items():
        if isinstance(val, list):
            print(f"  {key}: list of {len(val)} items")
            if val:
                print(f"    First item keys: {list(val[0].keys()) if isinstance(val[0], dict) else type(val[0])}")
                # Print first item without full response text
                item = val[0]
                for k, v in item.items():
                    if k == "response":
                        print(f"      {k}: (len={len(str(v))})")
                    elif isinstance(v, str) and len(v) > 200:
                        print(f"      {k}: {v[:200]}...")
                    else:
                        print(f"      {k}: {v}")
        else:
            print(f"  {key}: {val}")
