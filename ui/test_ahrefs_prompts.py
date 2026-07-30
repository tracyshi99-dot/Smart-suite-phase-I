"""Test Ahrefs Brand Radar prompts and ai-responses endpoints."""
import requests
import json

API_KEY = "qII2G3fkeGsZFBUam2ar0UryqQWtaNXK6RIkFIWU"
REPORT_ID = "019e4f11-83ad-7648-a3d4-5a0d3760861e"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# Test 1: Get prompts list (what queries are being monitored)
print("=" * 60)
print("TEST 1: GET brand-radar-prompts (query list)")
print("=" * 60)
r1 = requests.get(
    f"https://api.ahrefs.com/v3/management/brand-radar-prompts",
    headers=headers,
    params={"report_id": REPORT_ID},
    timeout=30,
)
print(f"Status: {r1.status_code}")
print(f"Response: {r1.text[:3000]}")

# Test 2: Get AI responses for prompts
print("\n" + "=" * 60)
print("TEST 2: GET brand-radar/ai-responses")
print("=" * 60)
r2 = requests.get(
    f"https://api.ahrefs.com/v3/brand-radar/ai-responses",
    headers=headers,
    params={"report_id": REPORT_ID, "limit": 5},
    timeout=30,
)
print(f"Status: {r2.status_code}")
print(f"Response: {r2.text[:3000]}")

# Test 3: POST version if GET doesn't work
print("\n" + "=" * 60)
print("TEST 3: POST brand-radar/ai-responses")
print("=" * 60)
payload = {
    "report_id": REPORT_ID,
    "data_source": ["chatgpt", "perplexity"],
    "country": ["tw"],
    "select": ["prompt", "data_source", "brand_mentioned", "url_mentioned"],
}
r3 = requests.post(
    f"https://api.ahrefs.com/v3/brand-radar/ai-responses",
    headers=headers,
    json=payload,
    timeout=30,
)
print(f"Status: {r3.status_code}")
print(f"Response: {r3.text[:3000]}")
