"""
Ahrefs Brand Radar UI Components for SmartSuite.
Renders Ahrefs data sections in 智库, 智测, and 智析 pages.
Only visible to authorized users (rickylan).

Data sources: ChatGPT, Google AI Overviews, Google AI Mode, Gemini, Perplexity, Copilot
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ahrefs_client import (
    is_user_authorized,
    fetch_all_data,
    overview_to_metrics,
    overview_to_competitor_df,
    history_to_dataframe,
    get_api_key,
    DEFAULT_REPORT_ID,
    COMPETITORS_CONFIG,
)


def _check_access(current_user: str) -> bool:
    """Check if user should see Ahrefs section."""
    if not is_user_authorized(current_user):
        return False
    if not get_api_key():
        return False
    return True


def render_ahrefs_zhiku(current_user: str, is_en: bool = False):
    """Render Ahrefs section for 智库 page — AI visibility overview for query insights."""
    if not _check_access(current_user):
        return

    st.divider()
    with st.expander("🔗 Ahrefs Brand Radar — " + ("AI Visibility Overview" if is_en else "AI 可见度总览"), expanded=False):
        st.caption("Brand mentions across AI platforms (ChatGPT, Gemini, Perplexity, Copilot, Google AI) — insights for query strategy"
                   if is_en else "品牌在 AI 平台的提及情况（ChatGPT、Gemini、Perplexity、Copilot、Google AI）— 检索短语策略参考")

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

        # Metrics
        metrics = overview_to_metrics(overview)
        if "error" in metrics:
            st.warning(f"⚠️ {metrics['error']}")
            return

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Our Brand Only" if is_en else "仅我方品牌提及",
                      metrics.get("only_target_brand", "—"))
        with col2:
            st.metric("Competitors Only" if is_en else "仅竞品提及",
                      metrics.get("only_competitors_brands", "—"))
        with col3:
            st.metric("Both Mentioned" if is_en else "共同提及",
                      metrics.get("target_and_competitors_brands", "—"))
        with col4:
            st.metric("Total Queries" if is_en else "总查询数",
                      metrics.get("total", "—"))

        # Insight
        st.markdown("**💡 " + ("Insight" if is_en else "洞察") + "：**")
        st.caption("Queries where competitors appear but we don't = high-priority 智库 phrases to add. "
                   "Focus on queries with 'only_competitors_brands' to find content gaps."
                   if is_en else
                   "竞品出现但我方缺席的查询 = 高优先级智库短语。关注「仅竞品提及」的查询，挖掘内容 Gap。")


def render_ahrefs_zhice(current_user: str, is_en: bool = False):
    """Render Ahrefs section for 智测 page — official link coverage across AI platforms."""
    if not _check_access(current_user):
        return

    st.divider()
    with st.expander("🔗 Ahrefs Brand Radar — " + ("AI Link Coverage" if is_en else "AI 平台链接覆盖"), expanded=False):
        st.caption("Official link (gs.amazon.com.tw) mentions in AI responses — complement to manual gap testing"
                   if is_en else "官方链接 (gs.amazon.com.tw) 在 AI 回答中的被引用情况 — 补充手动 Gap 验证")

        try:
            data = fetch_all_data()
        except Exception as e:
            st.error(f"Failed to fetch Ahrefs data: {str(e)[:200]}")
            return

        overview = data.get("overview", {})
        if "error" in overview:
            st.warning(f"⚠️ API Error: {overview.get('error', '')}")
            return

        metrics = overview_to_metrics(overview)

        # Key metrics for 智测 context
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Our Brand Mentioned" if is_en else "我方被提及",
                      metrics.get("only_target_brand", metrics.get("brand", "—")))
        with col2:
            st.metric("No Brand Mentioned" if is_en else "无品牌提及（机会）",
                      metrics.get("no_tracked_brands", "—"))
        with col3:
            st.metric("Total AI Queries" if is_en else "AI 查询总数",
                      metrics.get("total", "—"))

        # Competitor comparison
        st.markdown("**" + ("Competitive Landscape in AI Results" if is_en else "AI 结果中的竞争格局") + "**")
        df_comp = overview_to_competitor_df(overview)
        if not df_comp.empty and "Error" not in df_comp.columns:
            st.dataframe(df_comp, use_container_width=True, hide_index=True)

        # Trend (mini)
        st.markdown("**" + ("Mention Trend" if is_en else "提及趋势") + "**")
        df_trend = history_to_dataframe(data.get("history", {}))
        if not df_trend.empty:
            # Show last 30 days
            recent = df_trend.tail(30)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=recent["Date"], y=recent["Mentions"],
                mode="lines+markers", name="Mentions",
                line=dict(color="#00d4aa", width=2),
                marker=dict(size=4),
            ))
            fig.update_layout(
                template="plotly_dark", height=200,
                margin=dict(l=30, r=10, t=10, b=30),
                xaxis_title="", yaxis_title="",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No trend data available" if is_en else "暂无趋势数据")


def render_ahrefs_zhixi(current_user: str, is_en: bool = False):
    """Render Ahrefs section for 智析 page — full dashboard with trends and competitor comparison."""
    if not _check_access(current_user):
        return

    st.divider()
    with st.expander("🔗 Ahrefs Brand Radar — " + ("Full AI Visibility Dashboard" if is_en else "AI 可见度完整看板"), expanded=True):
        st.caption("Complete Brand Radar view — AI visibility metrics, mention trends, competitor share of voice"
                   if is_en else "Brand Radar 全景 — AI 可见度指标、提及趋势、竞品声量占比")

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

            # Weekly/monthly summary
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
                    # Try to make a bar chart
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

        # --- Row 5: Data sources breakdown ---
        st.markdown("#### " + ("Data Sources" if is_en else "数据来源平台"))
        sources_str = "ChatGPT · Google AI Overviews · Google AI Mode · Gemini · Perplexity · Copilot"
        st.caption(f"📡 {sources_str}")
        st.caption(f"🌏 Market: Taiwan (tw) | Report: {DEFAULT_REPORT_ID[:8]}...")
        st.caption(f"🕐 Last fetched: {data.get('fetched_at', '—')[:19]}")

        # Refresh button
        if st.button("🔄 " + ("Refresh Data" if is_en else "刷新数据"), key="ahrefs_refresh_zhixi"):
            cache_key = f"ahrefs_cache_{DEFAULT_REPORT_ID}"
            if cache_key in st.session_state:
                del st.session_state[cache_key]
            st.rerun()
