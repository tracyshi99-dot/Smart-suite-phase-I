"""
Smart Suite 智库 Agent - 画像推演引擎
基于客户画像矩阵组合推演检索短语，按优先级排序后送智测验证。

两条路径：
  路径A（正面收集）: SEO/SEM → AI下拉 → 逆向召回 → 社区原生 → 校准验证
  路径B（画像推演）: 画像矩阵 × 生命周期 × 话题 → 预测短语 → 热度预估 → 优先级排序 → 智测验证
"""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from itertools import product as itertools_product
from typing import Optional, Callable

BASE_PATH = Path(__file__).parent.parent
INPUT_PATH = BASE_PATH / "input"
OUTPUT_PATH = BASE_PATH / "output"


def load_persona_matrix() -> dict:
    """Load persona matrix configuration."""
    matrix_file = INPUT_PATH / "persona_matrix.json"
    if matrix_file.exists():
        return json.loads(matrix_file.read_text(encoding="utf-8"))
    return {}


def calculate_priority(identity: str, topic: str, site: str, matrix: dict) -> float:
    """Calculate priority score for a combination."""
    base = matrix.get("基础画像", {})
    interest = matrix.get("兴趣画像", {})

    id_weight = base.get("身份", {}).get("priority_weight", {}).get(identity, 3)
    topic_weight = interest.get("内容分类", {}).get("priority_weight", {}).get(topic, 3)
    site_weight = interest.get("站点", {}).get("priority_weight", {}).get(site, 3)

    # Lifecycle match bonus
    lifecycle_map = interest.get("内容分类", {}).get("lifecycle_relevance", {})
    relevant_identities = lifecycle_map.get(topic, [])
    lifecycle_match = 5 if identity in relevant_identities else 2

    score = (id_weight * 0.3) + (topic_weight * 0.3) + (site_weight * 0.2) + (lifecycle_match * 0.2)
    return round(score, 2)


def estimate_volume(identity: str, topic: str, site: str, matrix: dict) -> int:
    """Estimate search volume for a combination."""
    base = matrix.get("基础画像", {})
    interest = matrix.get("兴趣画像", {})
    rules = matrix.get("推演规则", {}).get("volume_estimation", {})

    base_vol = rules.get("base_volume", {}).get(topic, 1000)
    id_mult = base.get("身份", {}).get("search_volume_multiplier", {}).get(identity, 1.0)
    site_mult = interest.get("站点", {}).get("search_volume_multiplier", {}).get(site, 1.0)

    return int(base_vol * id_mult * site_mult)


def check_conflicts(identity: str, topic: str, site: str, enterprise: str, matrix: dict) -> bool:
    """Check if a combination violates conflict rules. Returns True if valid."""
    rules = matrix.get("推演规则", {}).get("conflict_rules", [])

    for rule in rules:
        rule_text = rule.get("rule", "")
        # Simple rule matching
        if "身份=服务商" in rule_text and identity == "服务商" and "新手指南" in rule_text and topic == "新手指南":
            return False
        if "身份=3年以上卖家" in rule_text and identity == "3年以上卖家" and "新手指南" in rule_text and topic == "新手指南":
            return False
        if "年销售额=1亿以上" in rule_text and "新卖家" in identity:
            return False
        if "站点=印度站" in rule_text and site == "印度站" and "企业购" in rule_text and topic == "企业购":
            return False

    return True


def get_lifecycle_stage(identity: str) -> str:
    """Map identity to lifecycle stage."""
    stage_map = {
        "新卖家(P2L以前)": "认知期",
        "新卖家(P2L)": "决策期",
        "新卖家(L2L)": "注册期",
        "1年以下卖家": "新手期",
        "1-2年卖家": "成长期",
        "2-3年卖家": "成熟期",
        "3年以上卖家": "成熟期",
        "服务商": "成熟期",
    }
    return stage_map.get(identity, "新手期")


def generate_query_from_template(template: str, identity: str, topic: str, site: str,
                                  enterprise: str = "", delivery: str = "") -> str:
    """Fill in a query template with actual values."""
    query = template
    query = query.replace("{站点}", site.replace("站", ""))
    query = query.replace("{内容分类}", topic)
    query = query.replace("{企业类型}", enterprise if enterprise else "中国卖家")
    query = query.replace("{发货方式}", delivery if delivery else "FBA")
    query = query.replace("{年销售额}", "")
    query = query.replace("{竞品}", "Shopee")
    query = query.replace("{年份}", "2026")
    return query.strip()


def run_persona_prediction(
    priority_level: str = "P0",
    max_queries: int = 50,
    target_sites: list = None,
    target_topics: list = None,
    progress_callback: Optional[Callable] = None,
) -> dict:
    """
    Run persona-based query prediction.

    Args:
        priority_level: "P0" (top), "P1", "P2", or "ALL"
        max_queries: Maximum number of queries to generate
        target_sites: Filter to specific sites (None = all)
        target_topics: Filter to specific topics (None = all)
        progress_callback: Optional progress callback

    Returns:
        dict with success status and generated queries
    """
    matrix = load_persona_matrix()
    if not matrix:
        return {"success": False, "error": "画像矩阵文件不存在: input/persona_matrix.json"}

    if progress_callback:
        progress_callback(0.1, "加载画像矩阵...")

    base = matrix.get("基础画像", {})
    interest = matrix.get("兴趣画像", {})
    journey = matrix.get("推演规则", {}).get("lifecycle_journey", {})

    identities = base.get("身份", {}).get("params", [])
    enterprises = base.get("企业类型", {}).get("params", [])
    sites = interest.get("站点", {}).get("params", [])
    topics = interest.get("内容分类", {}).get("params", [])
    deliveries = base.get("计划发货方式", {}).get("params", [])

    # Apply filters
    if target_sites:
        sites = [s for s in sites if s in target_sites]
    if target_topics:
        topics = [t for t in topics if t in target_topics]

    if progress_callback:
        progress_callback(0.2, "推演组合...")

    # Generate all valid combinations with priority scores
    all_predictions = []

    for identity in identities:
        stage = get_lifecycle_stage(identity)
        stage_templates = journey.get(stage, {}).get("典型问题模式", [])

        for site in sites:
            for topic in topics:
                # Check conflicts
                if not check_conflicts(identity, topic, site, "", matrix):
                    continue

                # Calculate priority
                priority = calculate_priority(identity, topic, site, matrix)
                volume = estimate_volume(identity, topic, site, matrix)

                # Determine priority level
                if priority >= 4.0:
                    p_level = "P0"
                elif priority >= 3.0:
                    p_level = "P1"
                elif priority >= 2.0:
                    p_level = "P2"
                else:
                    p_level = "P3"

                # Filter by requested priority level
                if priority_level != "ALL" and p_level != priority_level:
                    continue

                # For P0: expand with enterprise types + delivery methods
                # For P1/P2: use simple defaults (faster)
                if p_level == "P0":
                    ent_list = [e for e in enterprises
                                if base.get("企业类型", {}).get("priority_weight", {}).get(e, 0) >= 4]
                    dlv_list = [d for d in deliveries
                                if base.get("计划发货方式", {}).get("priority_weight", {}).get(d, 0) >= 4]
                    if not ent_list:
                        ent_list = ["中国卖家"]
                    if not dlv_list:
                        dlv_list = ["FBA"]
                else:
                    ent_list = [""]
                    dlv_list = [""]

                for enterprise in ent_list:
                    for delivery in dlv_list:
                        for template in stage_templates:
                            query = generate_query_from_template(
                                template, identity, topic, site, enterprise, delivery
                            )
                            if len(query) > 5:
                                all_predictions.append({
                                    "ai_query": query,
                                    "identity": identity,
                                    "lifecycle_stage": stage,
                                    "site": site,
                                    "topic": topic,
                                    "priority_score": priority,
                                    "estimated_volume": volume,
                                    "priority_level": p_level,
                                    "source": f"predicted_{p_level.lower()}",
                                    "is_selected": "FALSE",
                                    "verified": "FALSE",
                                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                })

    if progress_callback:
        progress_callback(0.5, "规则推演完成，开始 AI 扩展裂变...")

    # --- AI Expansion: take top seeds and generate variants ---
    # Sort first, then expand top N seeds
    all_predictions.sort(key=lambda x: (-x["priority_score"], -x["estimated_volume"]))

    # Deduplicate
    seen_queries = set()
    unique_predictions = []
    for p in all_predictions:
        q_normalized = p["ai_query"].strip().lower()
        if q_normalized not in seen_queries:
            seen_queries.add(q_normalized)
            unique_predictions.append(p)

    # AI expansion: take top seeds and generate 3 variants each
    ai_expanded = []
    seeds_to_expand = unique_predictions[:min(20, len(unique_predictions))]  # Expand top 20

    if seeds_to_expand and progress_callback:
        progress_callback(0.6, f"AI 扩展 {len(seeds_to_expand)} 条种子短语...")

    if seeds_to_expand:
        try:
            from engine import call_claude
            # Batch expand: send 10 seeds at a time
            batch_size = 10
            for batch_start in range(0, len(seeds_to_expand), batch_size):
                batch = seeds_to_expand[batch_start:batch_start + batch_size]
                seed_list = "\n".join([f"- {s['ai_query']}" for s in batch])

                expand_prompt = f"""以下是一组 AI 检索短语种子。请为每条种子生成 3 个口语化变体（用户可能的不同表达方式）。

种子短语：
{seed_list}

要求：
- 每条种子生成 3 个变体
- 变体必须保持相同语义但不同表达
- 模拟真实用户在 AI 搜索引擎的口语化提问
- 格式：每行一条，前面标序号（1.1, 1.2, 1.3, 2.1, 2.2...）
- 只输出短语，不要其他解释"""

                try:
                    result = call_claude("你是 AI 搜索短语裂变专家。", expand_prompt, max_tokens=1000)
                    # Parse expanded queries
                    for line in result.strip().split("\n"):
                        line = line.strip().lstrip("0123456789.-、） ").strip()
                        if len(line) > 5 and line not in seen_queries:
                            seen_queries.add(line.lower())
                            # Inherit priority from nearest seed
                            seed_idx = min(batch_start, len(seeds_to_expand) - 1)
                            parent = seeds_to_expand[seed_idx] if seed_idx < len(batch) else batch[0]
                            ai_expanded.append({
                                "ai_query": line,
                                "identity": parent["identity"],
                                "lifecycle_stage": parent["lifecycle_stage"],
                                "site": parent["site"],
                                "topic": parent["topic"],
                                "priority_score": parent["priority_score"] - 0.1,  # Slightly lower than seed
                                "estimated_volume": int(parent["estimated_volume"] * 0.8),
                                "priority_level": parent["priority_level"],
                                "source": f"predicted_{parent['priority_level'].lower()}_ai_expanded",
                                "is_selected": "FALSE",
                                "verified": "FALSE",
                                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            })
                except Exception:
                    pass  # AI expansion is best-effort

                if progress_callback:
                    progress_callback(0.6 + 0.2 * (batch_start / len(seeds_to_expand)), "AI 扩展中...")
        except ImportError:
            pass  # No engine available, skip AI expansion

    # Merge: original + AI expanded
    unique_predictions.extend(ai_expanded)
    unique_predictions.sort(key=lambda x: (-x["priority_score"], -x["estimated_volume"]))

    # Limit output
    unique_predictions = unique_predictions[:max_queries]

    if progress_callback:
        progress_callback(0.9, "保存结果...")

    # Save to output (cumulative: append to master file + save timestamped copy)
    if unique_predictions:
        df = pd.DataFrame(unique_predictions)
        output_dir = OUTPUT_PATH / "zhiku_predictions"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save timestamped copy (for history)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"predicted_{priority_level}_{ts}.csv"
        df.to_csv(output_file, index=False, encoding="utf-8-sig")

        # Append to cumulative master file (deduplicated)
        master_file = output_dir / "predictions_master.csv"
        if master_file.exists():
            df_master = pd.read_csv(master_file, encoding="utf-8-sig")
            df_combined = pd.concat([df_master, df], ignore_index=True)
            df_combined = df_combined.drop_duplicates(subset=["ai_query"], keep="last")
            df_combined.to_csv(master_file, index=False, encoding="utf-8-sig")
            total_in_master = len(df_combined)
        else:
            df.to_csv(master_file, index=False, encoding="utf-8-sig")
            total_in_master = len(df)

        if progress_callback:
            progress_callback(1.0, f"推演完成 ✅ 本次 +{len(unique_predictions)} 条，累计 {total_in_master} 条")

        return {
            "success": True,
            "total_generated": len(unique_predictions),
            "total_cumulative": total_in_master,
            "priority_distribution": {
                "P0": len([p for p in unique_predictions if p["priority_level"] == "P0"]),
                "P1": len([p for p in unique_predictions if p["priority_level"] == "P1"]),
                "P2": len([p for p in unique_predictions if p["priority_level"] == "P2"]),
            },
            "output_file": str(output_file),
            "predictions": unique_predictions,
        }

    if progress_callback:
        progress_callback(1.0, "无有效组合")

    return {"success": False, "error": "没有生成有效的预测短语，请检查筛选条件"}


def export_to_zhiku(predictions: list, batch_id: str = "batch_003") -> dict:
    """Export predicted queries to zhiku for verification pipeline."""
    if not predictions:
        return {"success": False, "error": "无预测短语可导出"}

    zhiku_dir = OUTPUT_PATH / batch_id / "01_zhiku"
    zhiku_dir.mkdir(parents=True, exist_ok=True)
    zhiku_file = zhiku_dir / "zhiku_ai_queries.csv"

    # Convert to zhiku format
    zhiku_rows = []
    for p in predictions:
        zhiku_rows.append({
            "keyword_id": f"PRED_{predictions.index(p)+1:03d}",
            "keyword": p.get("topic", ""),
            "query_id": f"PRED_{predictions.index(p)+1:03d}_Q01",
            "ai_query": p["ai_query"],
            "intent_type": "informational",
            "query_type": "generic",
            "priority_score": p["priority_score"],
            "estimated_volume": p["estimated_volume"],
            "category": p.get("topic", ""),
            "language": "zh-CN",
            "market": "CN",
            "source": p.get("source", "predicted_p0"),
            "is_selected": "TRUE",  # Auto-select for verification
            "created_at": p["created_at"],
        })

    df_new = pd.DataFrame(zhiku_rows)

    # Append to existing
    if zhiku_file.exists():
        existing = pd.read_csv(zhiku_file, encoding="utf-8-sig")
        merged = pd.concat([existing, df_new], ignore_index=True)
        if "ai_query" in merged.columns:
            merged = merged.drop_duplicates(subset=["ai_query"], keep="first")
        merged.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
    else:
        df_new.to_csv(zhiku_file, index=False, encoding="utf-8-sig")

    return {
        "success": True,
        "exported": len(zhiku_rows),
        "file": str(zhiku_file),
    }
