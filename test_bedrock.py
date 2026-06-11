"""Quick test: can we call Claude and get valid JSON back?"""
import boto3
import json

client = boto3.Session(region_name="us-east-1").client("bedrock-runtime")

resp = client.converse(
    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
    messages=[{"role": "user", "content": [{"text": """Simulate search results for the query "如何在亚马逊美国站开店" on 2 platforms.
Output ONLY valid JSON (no markdown, no explanation):
{"results":{"chatgpt":{"key_points":["point1"],"sources":[{"title":"t","domain":"d","url":"u","is_our_content":false}]},"deepseek":{"key_points":["point1"],"sources":[]}},"key_findings":"finding","our_content_found":false,"coverage_note":"note"}"""}]}],
    system=[{"text": "You are a JSON-only output bot. Output raw JSON without any markdown code fences or explanation text."}],
    inferenceConfig={"maxTokens": 1024, "temperature": 0.3},
)

raw = resp["output"]["message"]["content"][0]["text"]
print("=== RAW RESPONSE ===")
print(raw[:500])
print("\n=== PARSE TEST ===")
try:
    data = json.loads(raw)
    print("SUCCESS! Parsed JSON.")
    print(json.dumps(data, ensure_ascii=False, indent=2)[:300])
except json.JSONDecodeError as e:
    print(f"FAILED: {e}")
    # Try extracting JSON
    import re
    m = re.search(r'\{[\s\S]*\}', raw)
    if m:
        try:
            data = json.loads(m.group())
            print("SUCCESS with regex extraction!")
        except:
            print("Regex extraction also failed")
