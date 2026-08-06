"""
Ahrefs Brand Radar UI Components for SmartSuite.
Renders Ahrefs data sections in 智库, 智测, and 智析 pages.
Only visible to authorized users (rickylan).

Deep integration with query-level data from ai-responses endpoint:
- 智库: Show monitored queries, import to zhiku CSV
- 智测: Show coverage data, mark queries as "已验证(Ahrefs)"
- 智析: Full dashboard + query-level analysis (gaps, coverage rates)

Data sources: ChatGPT, Google AI Overviews, Google AI Mode, Gemini, Perplexity, Copilot
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
from ahrefs_client import (
    is_user_authorized,
    fetch_all_data,
    get_ahrefs_queries_df,
    overview_to_metrics,
    overview_to_competitor_df,
    history_to_dataframe,
    get_api_key,
    DEFAULT_REPORT_ID,
    COMPETITORS_CONFIG,
)


# --- Paths for zhiku CSV import ---
BASE_PATH = Path(__file__).parent.parent
ZHIKU_CSV_DIR = BASE_PATH / "output" / "batch_001" / "01_zhiku"


def _check_access(current_user: str) -> bool:
    """Check if user should see Ahrefs section."""
    if not is_user_authorized(current_user):
        return False
    if not get_api_key():
        return False
    return True


# ============================================================
# 智库 PAGE — Ahrefs Monitored Queries
# ============================================================

def render_ahrefs_zhiku(current_user: str, is_en: bool = False):
    """Render Ahrefs summary for 智库 page — compact info since data is merged into main table."""
    if not _check_access(current_user):
        return

    try:
        df_queries = get_ahrefs_queries_df()
    except Exception:
        return

    if df_queries.empty:
        return

    # Determine region label
    _region_label = "TW"
    try:
        from region_adapter import get_user_sub_region
        _usr = get_user_sub_region(current_user)
        if _usr:
            _region_label = _usr
    except Exception:
        pass

    # Show compact summary (data is already merged into main table)
    total_queries = len(df_queries)
    platforms = df_queries["data_source"].nunique()
    with_link = int(df_queries["has_official_link"].sum())
    st.caption(
        f"🔗 Ahrefs [{_region_label}]: {total_queries} queries from {platforms} AI platforms merged (source=ahrefs) | "
        f"{with_link}/{total_queries} have official links"
        if is_en else
        f"🔗 Ahrefs [{_region_label}]: 已合并 {total_queries} 条短语（来自 {platforms} 个 AI 平台，来源=ahrefs）| "
        f"{with_link}/{total_queries} 条含官方链接"
    )


def _import_to_zhiku(df_ahrefs: pd.DataFrame, is_en: bool = False):
    """Import Ahrefs queries into zhiku CSV, deduplicating against existing ai_query values."""
    csv_path = ZHIKU_CSV_DIR / "zhiku_ai_queries.csv"

    try:
        if csv_path.exists():
            df_existing = pd.read_csv(csv_path, encoding="utf-8")
        else:
            ZHIKU_CSV_DIR.mkdir(parents=True, exist_ok=True)
            df_existing = pd.DataFrame(columns=[
                "keyword_id", "keyword", "query_id", "ai_query", "intent_type",
                "query_type", "priority_score", "language", "market", "is_selected", "created_at",
            ])

        existing_queries = set(df_existing["ai_query"].str.lower().tolist()) if "ai_query" in df_existing.columns else set()

        # Filter new queries not already in zhiku
        new_queries = df_ahrefs[~df_ahrefs["ai_query"].str.lower().isin(existing_queries)].copy()

        if new_queries.empty:
            st.info("✅ " + ("All queries already exist in 智库. No new imports." if is_en else "所有短语已存在于智库中，无需导入。"))
            return

        # Build rows for CSV
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        max_id_num = 0
        if not df_existing.empty and "query_id" in df_existing.columns:
            try:
                nums = df_existing["query_id"].str.extract(r"(\d+)").astype(float).max().values[0]
                max_id_num = int(nums) if pd.notna(nums) else 0
            except Exception:
                max_id_num = len(df_existing)

        new_rows = []
        for i, row in new_queries.iterrows():
            max_id_num += 1
            new_rows.append({
                "keyword_id": "WK_AHREFS",
                "keyword": "ahrefs_import",
                "query_id": f"Q_AHR_{max_id_num:04d}",
                "ai_query": row["ai_query"],
                "intent_type": "informational",
                "query_type": "branded" if row.get("has_brand_mention", False) else "generic",
                "priority_score": 4 if row.get("has_brand_mention", False) else 3,
                "language": "zh-TW",
                "market": "TW",
                "is_selected": "TRUE",
                "created_at": now_str,
            })

        df_new = pd.DataFrame(new_rows)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_csv(csv_path, index=False, encoding="utf-8")

        st.success(
            f"✅ Imported {len(new_rows)} new queries to 智库 (skipped {len(df_ahrefs) - len(new_rows)} duplicates)"
            if is_en else
            f"✅ 已导入 {len(new_rows)} 条新短语到智库（跳过 {len(df_ahrefs) - len(new_rows)} 条重复）"
        )
    except Exception as e:
        st.error(f"Import failed: {str(e)[:300]}")


# ============================================================
# 智测 PAGE — Ahrefs Coverage Data
# ============================================================

def render_ahrefs_zhice(current_user: str, is_en: bool = False):
    """Render Ahrefs summary for 智测 page — compact info since data is merged into verification results."""
    if not _check_access(current_user):
        return

    try:
        df_queries = get_ahrefs_queries_df()
    except Exception:
        return

    if df_queries.empty:
        return

    # Compact summary (data is merged into main verification flow)
    total = len(df_queries)
    with_link = int(df_queries["has_official_link"].sum())
    with_mention = int(df_queries["has_brand_mention"].sum())
    platforms = df_queries["data_source"].nunique()
    st.caption(
        f"🔗 Ahrefs: {total} queries pre-verified across {platforms} platforms | "
        f"Official links: {with_link}/{total} | Brand mentions: {with_mention}/{total}"
        if is_en else
        f"🔗 Ahrefs: {total} 条短语已有验证数据（{platforms} 个平台）| "
        f"官方链接: {with_link}/{total} | 品牌提及: {with_mention}/{total}"
    )


# ============================================================
# 智析 PAGE — Full Dashboard + Query-Level Analysis
# ============================================================

def render_ahrefs_zhixi(current_user: str, is_en: bool = False):
    """Render Ahrefs section for 智析 page — full dashboard with trends, competitor comparison, and query-level analysis."""
    if not _check_access(current_user):
        return

    # Determine region from user
    _region_label = "🇹🇼 TW"  # Currently TW only; will expand to other regions
    try:
        from region_adapter import get_user_region, get_user_sub_region
        _ur = get_user_region(current_user)
        _usr = get_user_sub_region(current_user)
        if _usr:
            _region_map = {"TW": "🇹🇼 TW", "KR": "🇰🇷 KR", "VN": "🇻🇳 VN"}
            _region_label = _region_map.get(_usr, f"🌏 {_usr}")
        elif _ur == "NA":
            _region_label = "🇺🇸 NA"
        elif _ur == "EU":
            _region_label = "🇪🇺 EU"
        elif _ur == "CN":
            _region_label = "🇨🇳 CN"
    except Exception:
        pass

    st.divider()
    with st.expander(f"🔗 Ahrefs Brand Radar [{_region_label}] — " + ("Full AI Visibility Dashboard" if is_en else "AI 可见度完整看板"), expanded=True):
        st.caption(
            f"Region: {_region_label} | " + (
            "Complete Brand Radar view — AI visibility metrics, mention trends, competitor share of voice, query-level gap analysis"
            if is_en else
            "Brand Radar 全景 — AI 可见度指标、提及趋势、竞品声量占比、查询级 Gap 分析")
        )

        try:
            data = fetch_all_data()
        except Exception as e:
            st.error(f"Failed to fetch Ahrefs data: {str(e)[:200]}")
            return

        overview = data.get("overview", {})
        if "error" in overview:
            st.warning(f"⚠️ API Error: {overview.get('error', '')}")
            st.caption(f"Detail: {overview.get('detail', '')[:300]}")
            return

        metrics = overview_to_metrics(overview)

        # --- Row 1: Key Metrics ---
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Our Brand Only" if is_en else "仅我方",
                      metrics.get("only_target_brand", "—"))
        with col2:
            st.metric("Competitors Only" if is_en else "仅竞品",
                      metrics.get("only_competitors_brands", "—"))
        with col3:
            st.metric("Both" if is_en else "共同提及",
                      metrics.get("target_and_competitors_brands", "—"))
        with col4:
            st.metric("No Brand" if is_en else "无品牌",
                      metrics.get("no_tracked_brands", "—"))
        with col5:
            st.metric("Total" if is_en else "总计",
                      metrics.get("total", "—"))

        # --- Row 2: Share of Voice calculation ---
        try:
            our = int(metrics.get("only_target_brand", 0) or 0) + int(metrics.get("target_and_competitors_brands", 0) or 0)
            total = int(metrics.get("total", 1) or 1)
            sov = round(our / total * 100, 1) if total > 0 else 0
            st.markdown(f"**📊 Share of Voice: {sov}%** " +
                        ("(our brand present in this % of total AI queries)" if is_en
                         else f"（我方品牌出现在 {sov}% 的 AI 查询结果中）"))
        except (ValueError, TypeError):
            pass

        st.markdown("---")

        # --- Row 3: Mention Trend Chart ---
        st.markdown("#### " + ("Brand Mention Trend (12 months)" if is_en else "品牌提及趋势（12个月）"))
        df_trend = history_to_dataframe(data.get("history", {}))
        if not df_trend.empty:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_trend["Date"], y=df_trend["Mentions"],
                mode="lines+markers",
                name="Brand Mentions" if is_en else "品牌提及",
                line=dict(color="#ffa726", width=2.5),
                marker=dict(size=4),
                fill="tozeroy",
                fillcolor="rgba(255,167,38,0.1)",
            ))
            fig.update_layout(
                template="plotly_dark", height=300,
                margin=dict(l=40, r=20, t=20, b=40),
                xaxis_title="",
                yaxis_title="Mentions" if is_en else "提及次数",
                hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)

            # Weekly summary
            if len(df_trend) >= 7:
                last_7 = df_trend.tail(7)["Mentions"].sum()
                prev_7 = df_trend.iloc[-14:-7]["Mentions"].sum() if len(df_trend) >= 14 else 0
                wow_change = ((last_7 - prev_7) / prev_7 * 100) if prev_7 > 0 else 0
                st.caption(f"Last 7 days: {last_7} mentions | WoW: {wow_change:+.1f}%")
        else:
            st.caption("No trend data available" if is_en else "暂无趋势数据")

        st.markdown("---")

        # --- Row 4: Competitor Comparison ---
        st.markdown("#### " + ("Competitor Share Comparison" if is_en else "竞品声量对比"))
        df_comp = overview_to_competitor_df(overview)
        if not df_comp.empty and "Error" not in df_comp.columns:
            col_table, col_chart = st.columns([1, 1])
            with col_table:
                st.dataframe(df_comp, use_container_width=True, hide_index=True)
            with col_chart:
                if "Brand" in df_comp.columns and "Total" in df_comp.columns:
                    try:
                        df_chart = df_comp.copy()
                        df_chart["Total"] = pd.to_numeric(df_chart["Total"], errors="coerce")
                        df_chart = df_chart.dropna(subset=["Total"])
                        if not df_chart.empty:
                            colors = ["#ffa726" if "Amazon" in str(b) or "我方" in str(b) else "#4a5568"
                                      for b in df_chart["Brand"]]
                            fig_bar = go.Figure(go.Bar(
                                x=df_chart["Brand"], y=df_chart["Total"],
                                marker_color=colors,
                            ))
                            fig_bar.update_layout(
                                template="plotly_dark", height=280,
                                margin=dict(l=20, r=20, t=30, b=60),
                                title="Total Mentions" if is_en else "总提及数",
                                xaxis_tickangle=-30,
                            )
                            st.plotly_chart(fig_bar, use_container_width=True)
                    except Exception:
                        pass
        else:
            st.caption("No competitor data available" if is_en else "暂无竞品对比数据")

        st.markdown("---")

        # --- Row 5: Query-Level Analysis (NEW) ---
        st.markdown("#### " + ("Query-Level Analysis" if is_en else "查询级分析"))

        ai_responses = data.get("ai_responses", [])
        if ai_responses:
            total_queries = len(ai_responses)
            official_link_count = sum(1 for r in ai_responses if r.get("has_official_link", False))
            brand_mention_count = sum(1 for r in ai_responses if r.get("has_brand_mention", False))
            link_rate = round(official_link_count / total_queries * 100, 1) if total_queries > 0 else 0
            mention_rate = round(brand_mention_count / total_queries * 100, 1) if total_queries > 0 else 0

            # Metrics row
            qcol1, qcol2, qcol3 = st.columns(3)
            with qcol1:
                st.metric(
                    "Total Queries Monitored" if is_en else "监控短语总数",
                    total_queries
                )
            with qcol2:
                st.metric(
                    "Official Link Coverage" if is_en else "官方链接覆盖率",
                    f"{link_rate}%",
                    help=f"{official_link_count}/{total_queries} queries have .amazon links"
                )
            with qcol3:
                st.metric(
                    "Brand Mention Rate" if is_en else "品牌提及率",
                    f"{mention_rate}%",
                    help=f"{brand_mention_count}/{total_queries} queries mention Amazon/亚马逊"
                )

            # Gap table: queries WITHOUT official links
            gaps = [r for r in ai_responses if not r.get("has_official_link", False)]
            if gaps:
                st.markdown(
                    f"**🚨 Queries without official links ({len(gaps)} gaps to fix):**"
                    if is_en else
                    f"**🚨 缺少官方链接的短语（{len(gaps)} 个 Gap 待修复）：**"
                )
                gap_rows = []
                for g in gaps:
                    gap_rows.append({
                        "ai_query": g.get("question", ""),
                        "data_source": g.get("data_source", ""),
                        "has_brand_mention": "✅" if g.get("has_brand_mention", False) else "❌",
                        "links_count": g.get("links_count", 0),
                    })
                df_gaps = pd.DataFrame(gap_rows)
                df_gaps.columns = (
                    ["Query", "Platform", "Brand Mentioned", "Links Count"]
                    if is_en else
                    ["检索短语", "平台", "品牌提及", "链接数"]
                )
                st.dataframe(df_gaps, use_container_width=True, hide_index=True, height=250)
            else:
                st.success(
                    "🎉 All monitored queries have official links!"
                    if is_en else
                    "🎉 所有监控短语均已有官方链接！"
                )
        else:
            st.caption(
                "No query-level data available (ai-responses endpoint returned empty)"
                if is_en else
                "暂无查询级数据（ai-responses 端点返回为空）"
            )

        st.markdown("---")

        # --- Row 6: Data sources & refresh ---
        st.markdown("#### " + ("Data Sources" if is_en else "数据来源平台"))
        sources_str = "ChatGPT · Google AI Overviews · Google AI Mode · Gemini · Perplexity · Copilot"
        st.caption(f"📡 {sources_str}")
        st.caption(f"🌏 Market: Taiwan (tw) | Report: {DEFAULT_REPORT_ID[:8]}...")
        st.caption(f"🕐 Last fetched: {data.get('fetched_at', '—')[:19]}")

        # Refresh button
        if st.button("🔄 " + ("Refresh Data" if is_en else "刷新数据"), key="ahrefs_refresh_zhixi"):
            cache_key = f"ahrefs_cache_{DEFAULT_REPORT_ID}"
            cache_time_key = f"ahrefs_cache_time_{DEFAULT_REPORT_ID}"
            queries_cache_key = f"ahrefs_queries_cache_{DEFAULT_REPORT_ID}"
            queries_cache_time_key = f"ahrefs_queries_cache_time_{DEFAULT_REPORT_ID}"
            for k in [cache_key, cache_time_key, queries_cache_key, queries_cache_time_key]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()
