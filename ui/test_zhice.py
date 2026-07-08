import sys, os
sys.path.insert(0, r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\ui')
os.chdir(r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1')

import os
# Load env manually
env_path = r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\.env'
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ[k.strip()] = v.strip()

from zhice_engine import _call_openai, _call_deepseek, _call_qianwen, _call_kimi, _call_doubao, _call_gemini

query = "亚马逊FBA是什么？中国卖家如何使用FBA？"

platforms = [
    ("DeepSeek", _call_deepseek),
    ("Qianwen", _call_qianwen),
    ("Kimi", _call_kimi),
    ("Doubao", _call_doubao),
    ("OpenAI", _call_openai),
    ("Gemini", _call_gemini),
]

print(f"Query: {query}")
print("=" * 60)

for name, func in platforms:
    print(f"\n--- {name} ---")
    try:
        r = func(query)
        answer = r.get("full_answer", "")
        snippet = answer[:400]
        has_gs = "gs.amazon" in answer.lower() or "globalselling" in answer.lower()
        has_brand = "全球开店" in answer or "Global Selling" in answer
        sources = r.get("sources", [])
        web_search = r.get("_web_search", False)

        print(f"Answer ({len(answer)} chars): {snippet}...")
        print(f"Official link mentioned: {has_gs}")
        print(f"Brand mentioned: {has_brand}")
        if sources:
            print(f"Sources cited: {sources[:5]}")
        if web_search:
            print(f"Web search enabled: True")
        print(f"Status: OK")
    except Exception as e:
        print(f"ERROR: {e}")
