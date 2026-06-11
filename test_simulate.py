"""Test simulate_search_results directly"""
import sys
sys.path.insert(0, "ui")
from zhice_engine import simulate_search_results
import json

queries = {
    "chatgpt": "想了解如何在亚马逊美国站开店",
    "deepseek": "亚马逊美国站开店流程",
}

persona = {
    "name": "张先生",
    "background": "深圳3C卖家",
    "goal": "想开亚马逊美国站",
}

def progress(pct, msg):
    print(f"  [{pct:.0%}] {msg}")

print("=== Calling simulate_search_results ===")
result = simulate_search_results(queries, persona, round_num=1, progress_callback=progress)
print("\n=== RESULT ===")
print(json.dumps(result, ensure_ascii=False, indent=2)[:2000])
