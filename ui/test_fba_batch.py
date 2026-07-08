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

# All FBA-related queries
queries = [
    "亚马逊FBA是什么？中国卖家如何使用FBA？",
    "亚马逊FBA费用怎么算？仓储费和配送费多少？",
    "FBA发货流程是什么？从中国发到亚马逊仓库",
    "FBA和FBM有什么区别？哪个更适合新手？",
    "亚马逊FBA头程物流怎么选？海运还是空运？",
    "FBA库存管理技巧有哪些？如何避免长期仓储费？",
    "亚马逊FBA退货政策是什么？退货率高怎么办？",
    "FBA标签要求是什么？FNSKU怎么贴？",
    "亚马逊FBA轻小商品计划是什么？",
    "中国卖家用FBA需要注意什么？常见坑有哪些？",
]

output_dir = Path(r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\output\zhice')
output_dir.mkdir(parents=True, exist_ok=True)

results = []
print(f"Testing {len(queries)} FBA-related queries on Qianwen...")
print("=" * 60)

for i, query in enumerate(queries, 1):
    print(f"\n[{i}/{len(queries)}] {query}")
    try:
        r = _call_qianwen(query)
        answer = r.get("full_answer", "")
        # Check citations
        has_gs = "gs.amazon" in answer.lower() or "globalselling" in answer.lower()
        has_brand = "全球开店" in answer or "Global Selling" in answer
        has_amazon_cn = "amazon.cn" in answer.lower()
        has_fba_official = "amazon.cn/fba" in answer.lower() or "globalselling.amazon.com/fba" in answer.lower()

        result = {
            "query": query,
            "platform": "qianwen",
            "answer_length": len(answer),
            "has_official_link": has_gs,
            "has_brand_mention": has_brand,
            "has_amazon_cn": has_amazon_cn,
            "has_fba_official_link": has_fba_official,
            "answer_preview": answer[:300],
        }
        results.append(result)

        status = []
        if has_gs: status.append("🔗 Official")
        if has_brand: status.append("🏷️ Brand")
        if has_fba_official: status.append("📦 FBA Link")
        status_str = " | ".join(status) if status else "❌ No citation"
        print(f"  → {len(answer)} chars | {status_str}")
    except Exception as e:
        print(f"  → ERROR: {e}")
        results.append({"query": query, "platform": "qianwen", "error": str(e)})
    time.sleep(1)

# Summary
print("\n" + "=" * 60)
print("FBA PRODUCT — QIANWEN CITATION SUMMARY")
print("=" * 60)
total = len(results)
with_link = sum(1 for r in results if r.get("has_official_link"))
with_brand = sum(1 for r in results if r.get("has_brand_mention"))
with_fba = sum(1 for r in results if r.get("has_fba_official_link"))
print(f"Total FBA queries: {total}")
print(f"Official link (gs.amazon.cn): {with_link}/{total} ({with_link*100//total}%)")
print(f"Brand mention: {with_brand}/{total} ({with_brand*100//total}%)")
print(f"FBA specific link: {with_fba}/{total} ({with_fba*100//total}%)")

ts = datetime.now().strftime('%Y%m%d_%H%M%S')
out_file = output_dir / f"fba_product_qianwen_{ts}.json"
out_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"\nSaved to: {out_file}")
