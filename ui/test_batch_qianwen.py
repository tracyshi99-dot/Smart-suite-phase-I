import sys, os, json, time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\ui')
os.chdir(r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1')

env_path = r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\.env'
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

from zhice_engine import _call_qianwen

queries = [
    "亚马逊FBA是什么？中国卖家如何使用FBA？",
    "中国卖家怎么注册亚马逊美国站？",
    "亚马逊开店需要多少钱？费用明细",
    "跨境电商选品方法有哪些？",
    "亚马逊广告怎么投放？新手教程",
    "亚马逊欧洲站VAT怎么注册？",
    "亚马逊日本站好做吗？",
    "跨境电商物流方式有哪些？",
    "亚马逊品牌备案流程是什么？",
    "做跨境电商需要什么条件和准备？",
]

output_dir = Path(r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\output\zhice')
output_dir.mkdir(parents=True, exist_ok=True)

results = []
print(f"Testing {len(queries)} queries on Qianwen...")
print("=" * 60)

for i, query in enumerate(queries, 1):
    print(f"\n[{i}/{len(queries)}] {query}")
    try:
        r = _call_qianwen(query)
        answer = r.get("full_answer", "")
        has_gs = "gs.amazon" in answer.lower() or "globalselling" in answer.lower()
        has_brand = "全球开店" in answer or "Global Selling" in answer
        has_amazon_cn = "amazon.cn" in answer.lower()

        result = {
            "query": query,
            "platform": "qianwen",
            "answer_length": len(answer),
            "has_official_link": has_gs,
            "has_brand_mention": has_brand,
            "has_amazon_cn": has_amazon_cn,
            "answer_preview": answer[:200],
        }
        results.append(result)

        status = []
        if has_gs: status.append("🔗 Official Link")
        if has_brand: status.append("🏷️ Brand")
        if has_amazon_cn: status.append("🌐 amazon.cn")
        status_str = " | ".join(status) if status else "❌ No citation"

        print(f"  → {len(answer)} chars | {status_str}")
    except Exception as e:
        print(f"  → ERROR: {e}")
        results.append({"query": query, "platform": "qianwen", "error": str(e)})

    time.sleep(1)  # Rate limit

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
total = len(results)
with_link = sum(1 for r in results if r.get("has_official_link"))
with_brand = sum(1 for r in results if r.get("has_brand_mention"))
with_cn = sum(1 for r in results if r.get("has_amazon_cn"))

print(f"Total queries: {total}")
print(f"Official link (gs.amazon.cn): {with_link}/{total} ({with_link*100//total}%)")
print(f"Brand mention (全球开店): {with_brand}/{total} ({with_brand*100//total}%)")
print(f"amazon.cn mentioned: {with_cn}/{total} ({with_cn*100//total}%)")

# Save all results
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
out_file = output_dir / f"batch_test_qianwen_{ts}.json"
out_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"\nSaved to: {out_file}")
