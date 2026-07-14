"""
Smart Suite 智析 - Auto-Attribution Engine
自动归因：根据 Output 变化 + Input 活动，推断涨跌原因。
"""
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

BASE_PATH = Path(__file__).parent.parent
OUTPUT_PATH = BASE_PATH / "output"
METRICS_PATH = OUTPUT_PATH / "metrics"


def get_input_activity_by_week() -> dict:
    """Get input activities grouped by approximate week."""
    activities = {
        "phrases_added": 0,
        "articles_created": 0,
        "articles_optimized": 0,
        "articles_published": 0,
        "verifications_run": 0,
        "last_activity_date": None,
    }

    if not OUTPUT_PATH.exists():
        return activities

    # Count across all batches
    for batch_dir in OUTPUT_PATH.iterdir():
        if not batch_dir.is_dir() or not batch_dir.name.startswith("batch_"):
            continue

        # Zhiku
        zhiku_f = batch_dir / "01_zhiku" / "zhiku_ai_queries.csv"
        if zhiku_f.exists():
            try:
                df = pd.read_csv(zhiku_f, encoding="utf-8-sig", on_bad_lines="skip")
                if "created_at" in df.columns:
                    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
                    week_ago = datetime.now() - timedelta(days=7)
                    recent = df[df["created_at"] >= week_ago]
                    activities["phrases_added"] += len(recent)
                else:
                    activities["phrases_added"] += len(df)
            except Exception:
                pass

        # Zhizao
        zhizao_f = batch_dir / "02_zhizao" / "zhizao_draft_content.csv"
        if zhizao_f.exists():
            try:
                df = pd.read_csv(zhizao_f, encoding="utf-8-sig", on_bad_lines="skip")
                activities["articles_created"] += len(df)
            except Exception:
                pass

        # Zhiyou
        opt_f = batch_dir / "03_zhiyou" / "zhiyou_optimized_content.csv"
        if opt_f.exists():
            try:
                df = pd.read_csv(opt_f, encoding="utf-8-sig", on_bad_lines="skip")
                activities["articles_optimized"] += len(df)
            except Exception:
                pass

        # Zhibu
        zhibu_dir = batch_dir / "04_zhibu"
        if zhibu_dir.exists():
            activities["articles_published"] += len(list(zhibu_dir.glob("*.json"))) + len(list(zhibu_dir.glob("*.docx")))

    # Zhice verifications
    zhice_dir = OUTPUT_PATH.parent / "zhice"
    if zhice_dir.exists():
        activities["verifications_run"] = len(list(zhice_dir.glob("gap_result_*.csv")))

    return activities


def generate_attribution(df_weekly: pd.DataFrame, activities: dict) -> list:
    """
    Generate attribution insights based on output trends + input activities.
    Returns list of attribution strings.
    """
    attributions = []

    if df_weekly.empty or len(df_weekly) < 2:
        return ["数据不足，至少需要 2 周数据才能归因"]

    # Get latest 2 weeks
    latest = df_weekly.iloc[-1]
    previous = df_weekly.iloc[-2]

    # Calculate WoW changes
    channels = {
        "CN_GEO": "CN GEO",
        "WW_GEO": "WW GEO",
        "WW_Direct": "WW Direct",
        "Total": "Total",
    }

    for col, name in channels.items():
        if col in df_weekly.columns:
            curr = float(latest.get(col, 0))
            prev = float(previous.get(col, 0))
            if prev > 0:
                wow = (curr - prev) / prev * 100
            else:
                wow = 0

            if wow > 20:
                # Strong growth — attribute to recent activities
                reasons = []
                if activities["articles_published"] > 0:
                    reasons.append(f"本周发布 {activities['articles_published']} 篇内容（滞后效应）")
                if activities["articles_optimized"] > 0:
                    reasons.append(f"已优化 {activities['articles_optimized']} 篇（GEO 信号增强）")
                if activities["verifications_run"] > 0:
                    reasons.append(f"已验证 {activities['verifications_run']} 批（覆盖面扩大）")
                if not reasons:
                    reasons.append("可能为自然增长或外部因素")
                attributions.append(f"↑ {name} WoW +{wow:.0f}% — 可能原因：{'；'.join(reasons)}")

            elif wow < -15:
                # Decline — flag potential issues
                reasons = []
                if activities["articles_published"] == 0:
                    reasons.append("本周无新内容发布")
                if activities["phrases_added"] == 0:
                    reasons.append("无新短语入库")
                reasons.append("建议检查内容是否被 de-index 或竞品新内容上线")
                attributions.append(f"⚠️ ↓ {name} WoW {wow:.0f}% — 可能原因：{'；'.join(reasons)}")

            elif abs(wow) <= 5:
                attributions.append(f"→ {name} WoW {wow:+.0f}% — 基本持平")

    # Overall assessment
    total_curr = float(latest.get("Total", 0))
    total_prev = float(previous.get("Total", 0))
    if total_prev > 0:
        total_wow = (total_curr - total_prev) / total_prev * 100
        if total_wow > 10:
            attributions.insert(0, f"📊 Output 判定：🟢 POSITIVE（Total WoW +{total_wow:.0f}%）")
        elif total_wow < -10:
            attributions.insert(0, f"📊 Output 判定：🔴 NEGATIVE（Total WoW {total_wow:.0f}%）")
        else:
            attributions.insert(0, f"📊 Output 判定：🟡 NEUTRAL（Total WoW {total_wow:+.0f}%）")

    return attributions


def generate_action_items(df_weekly: pd.DataFrame, activities: dict) -> list:
    """Generate next-week action items based on current state."""
    actions = []

    if activities["articles_published"] == 0:
        actions.append("🔴 本周无发布。优先将已优化内容推入智布发布。")

    if activities["phrases_added"] < 10:
        actions.append("🟡 短语库增长缓慢。考虑运行画像推演生成更多预测短语。")

    if activities["verifications_run"] == 0:
        actions.append("🟡 本周未运行智测验证。建议验证已发布内容的 AI 引用效果。")

    if activities["articles_optimized"] > activities["articles_published"]:
        diff = activities["articles_optimized"] - activities["articles_published"]
        actions.append(f"📦 有 {diff} 篇已优化内容等待发布，请尽快进入智布。")

    if not actions:
        actions.append("✅ 当前流程健康，保持节奏。")

    return actions


def get_published_queries(batch_ids: list = None) -> list:
    """Get queries that have been published (have zhibu output)."""
    published_queries = []

    if not OUTPUT_PATH.exists():
        return published_queries

    for batch_dir in OUTPUT_PATH.iterdir():
        if not batch_dir.is_dir() or not batch_dir.name.startswith("batch_"):
            continue
        if batch_ids and batch_dir.name not in batch_ids:
            continue

        # Check if batch has published content
        zhibu_dir = batch_dir / "04_zhibu"
        if not zhibu_dir.exists() or not any(zhibu_dir.iterdir()):
            continue

        # Get the queries from zhizao
        zhizao_f = batch_dir / "02_zhizao" / "zhizao_draft_content.csv"
        if zhizao_f.exists():
            try:
                df = pd.read_csv(zhizao_f, encoding="utf-8-sig", on_bad_lines="skip")
                if "ai_query" in df.columns:
                    for q in df["ai_query"].dropna().tolist():
                        published_queries.append({
                            "ai_query": q,
                            "batch": batch_dir.name,
                            "status": "published",
                        })
            except Exception:
                pass

    return published_queries


def compare_pre_post_verification(tracking_file: Path, published_queries: list) -> pd.DataFrame:
    """Compare brand mention rate before and after content publication.
    Returns DataFrame with pre/post comparison."""
    if not tracking_file.exists():
        return pd.DataFrame()

    df_track = pd.read_csv(tracking_file, encoding="utf-8-sig")
    if df_track.empty or "ai_query" not in df_track.columns:
        return pd.DataFrame()

    # Get published query texts
    pub_queries = set(p["ai_query"] for p in published_queries)
    if not pub_queries:
        return pd.DataFrame()

    # Filter tracking to published queries only
    df_pub = df_track[df_track["ai_query"].isin(pub_queries)].copy()
    if df_pub.empty:
        return pd.DataFrame()

    # Ensure bool
    df_pub["has_brand_mention"] = df_pub["has_brand_mention"].astype(str).str.upper().isin(["TRUE", "1"])
    df_pub["date"] = pd.to_datetime(df_pub["date"], errors="coerce")

    # For each query, get earliest and latest check
    comparison = []
    for q in pub_queries:
        q_data = df_pub[df_pub["ai_query"] == q].sort_values("date")
        if len(q_data) >= 2:
            first_check = q_data.iloc[0]
            last_check = q_data.iloc[-1]
            comparison.append({
                "ai_query": q,
                "first_date": first_check["date"].strftime("%Y-%m-%d") if pd.notna(first_check["date"]) else "",
                "first_brand": first_check["has_brand_mention"],
                "last_date": last_check["date"].strftime("%Y-%m-%d") if pd.notna(last_check["date"]) else "",
                "last_brand": last_check["has_brand_mention"],
                "improvement": "✅ 提升" if (last_check["has_brand_mention"] and not first_check["has_brand_mention"]) else
                              ("➡️ 维持" if last_check["has_brand_mention"] == first_check["has_brand_mention"] else "❌ 下降"),
            })

    return pd.DataFrame(comparison) if comparison else pd.DataFrame()
