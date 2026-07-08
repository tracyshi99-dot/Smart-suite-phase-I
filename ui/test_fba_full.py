import sys, os, json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\ui')
os.chdir(r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1')

# Load env
env_path = r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\.env'
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

from zhice_engine import _call_qianwen

query = "亚马逊FBA是什么？中国卖家如何使用FBA？"

print(f"Query: {query}")
print("Platform: 通义千问 (Qianwen)")
print("=" * 60)

r = _call_qianwen(query)
answer = r.get("full_answer", "")

# Check for our content
has_gs = "gs.amazon" in answer.lower() or "globalselling" in answer.lower()
has_brand = "全球开店" in answer or "Global Selling" in answer
has_fba_link = "amazon.cn/fba" in answer.lower() or "fba" in answer.lower()

print(f"\nFull Answer ({len(answer)} chars):")
print("-" * 40)
print(answer)
print("-" * 40)
print(f"\n=== Analysis ===")
print(f"Official link (gs.amazon.cn): {'✅ YES' if has_gs else '❌ NO'}")
print(f"Brand mention (全球开店): {'✅ YES' if has_brand else '❌ NO'}")
print(f"FBA mentioned: {'✅ YES' if has_fba_link else '❌ NO'}")

# Save result
output_dir = Path(r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\output\zhice')
output_dir.mkdir(parents=True, exist_ok=True)

result = {
    "query": query,
    "platform": "qianwen",
    "timestamp": datetime.now().isoformat(),
    "answer": answer,
    "analysis": {
        "has_official_link": has_gs,
        "has_brand_mention": has_brand,
        "answer_length": len(answer),
    }
}

out_file = output_dir / f"fba_test_qianwen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
out_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"\nSaved to: {out_file}")
