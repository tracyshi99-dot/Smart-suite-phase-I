"""
Smart Suite 智系列控制台 - Streamlit UI (方案3 完整版)
覆盖全部智系列：智库 → 智造 → 智优 → 智布 → 智测(智析) → 智中枢
Run: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
from datetime import datetime

# --- Config ---
BASE_PATH = Path(__file__).parent.parent
OUTPUT_PATH = BASE_PATH / "output"
INPUT_PATH = BASE_PATH / "input"
METRICS_PATH = OUTPUT_PATH / "metrics"

st.set_page_config(
    page_title="Smart Suite 智系列控制台",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
.main .block-container { padding-top: 1.2rem; }
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1a2940 0%, #0d1b2a 100%);
    border: 1px solid #2a4a6f; border-radius: 10px; padding: 12px 16px;
}
.pipeline-step {
    border-radius: 8px; padding: 12px; margin: 4px 0;
    border-left: 4px solid #4a9eff;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_batches():
    batches = []
    if OUTPUT_PATH.exists():
        for d in sorted(OUTPUT_PATH.iterdir(), reverse=True):
            if d.is_dir() and d.name.startswith("batch_"):
                batches.append(d.name)
    if not batches:
        batches = ["batch_003", "batch_002", "batch_001"]
    return batches


def get_batch_status(batch_id: str) -> dict:
    batch_path = OUTPUT_PATH / batch_id
    steps = [
        ("01_zhiku", "智库", "📚", "AI Query Generation"),
        ("02_zhizao", "智造", "✍️", "Content Generation"),
        ("03_zhiyou", "智优", "🔧", "Score + Rewrite + Compliance"),
        ("04_zhibu", "智布", "📦", "JSON Formatting"),
    ]
    status = {}
    for folder, name, icon, desc in steps:
        step_path = batch_path / folder
        if step_path.exists() and any(step_path.iterdir()):
            files = list(step_path.glob("*.csv")) + list(step_path.glob("*.json"))
            status[folder] = {"name": name, "icon": icon, "desc": desc,
                              "done": True, "files": len(files)}
        else:
            status[folder] = {"name": name, "icon": icon, "desc": desc,
                              "done": False, "files": 0}
    return status


def load_csv_safe(path: Path):
    if path.exists():
        try:
            return pd.read_csv(path, encoding="utf-8-sig")
        except Exception:
            try:
                return pd.read_csv(path, encoding="utf-8")
            except Exception:
                return pd.DataFrame()
    return pd.DataFrame()


def is_cloud():
    """Detect if running on Streamlit Community Cloud."""
    import os
    return os.environ.get("STREAMLIT_SHARING_MODE") == "true" or not OUTPUT_PATH.exists()


def load_keywords():
    df = load_csv_safe(INPUT_PATH / "seo_sem_keywords.csv")
    if df.empty and is_cloud():
        from demo_data import get_demo_keywords
        return get_demo_keywords()
    return df


def load_zhiku(batch_id: str):
    df = load_csv_safe(OUTPUT_PATH / batch_id / "01_zhiku" / "zhiku_ai_queries.csv")
    if df.empty and is_cloud():
        from demo_data import get_demo_zhiku
        return get_demo_zhiku()
    return df


def load_zhizao(batch_id: str):
    """Load zhizao draft content - try main file then parts."""
    main = OUTPUT_PATH / batch_id / "02_zhizao" / "zhizao_draft_content.csv"
    if main.exists():
        return load_csv_safe(main)
    # Try loading parts
    parts_dir = OUTPUT_PATH / batch_id / "02_zhizao"
    if parts_dir.exists():
        parts = sorted(parts_dir.glob("zhizao_draft_content_p*.csv"))
        if parts:
            dfs = [load_csv_safe(p) for p in parts]
            return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()


def load_scorecard(batch_id: str):
    df = load_csv_safe(OUTPUT_PATH / batch_id / "03_zhiyou" / "zhiyou_scorecard.csv")
    if df.empty and is_cloud():
        from demo_data import get_demo_scorecard
        return get_demo_scorecard()
    return df


def load_optimized(batch_id: str):
    return load_csv_safe(OUTPUT_PATH / batch_id / "03_zhiyou" / "zhiyou_optimized_content.csv")


def load_compliance(batch_id: str):
    return load_csv_safe(OUTPUT_PATH / batch_id / "03_zhiyou" / "zhiyou_compliance_checked.csv")


def load_zhibu(batch_id: str):
    """Load zhibu JSON output."""
    zhibu_dir = OUTPUT_PATH / batch_id / "04_zhibu"
    if zhibu_dir.exists():
        jsons = list(zhibu_dir.glob("*.json"))
        if jsons:
            try:
                with open(jsons[0], encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return None


def load_batch_summary(batch_id: str):
    df = load_csv_safe(OUTPUT_PATH / "Batch_Summary_Report" / f"{batch_id}_summary.csv")
    if df.empty and is_cloud():
        from demo_data import get_demo_batch_summary
        return get_demo_batch_summary()
    return df


def get_weekly_metrics():
    return pd.DataFrame({
        "Week": ["WK17", "WK18", "WK19", "WK20"],
        "CN_GEO": [32, 33, 33, 41],
        "WW_GEO": [15, 18, 22, 31],
        "WW_Direct_EST": [1739, 1330, 1454, 1914],
        "WW_Direct_EM": [97, 64, 59, 61],
        "Total": [1883, 1445, 1568, 2047],
    })


def get_ytd_metrics():
    return pd.DataFrame({
        "Channel": ["CN GEO", "WW GEO", "WW Direct EST", "WW Direct EM", "Total"],
        "YTD_Actual": [574, 364, 25863, 1940, 28741],
        "YTD_PY": [104, 188, 15945, 2312, 18549],
        "YoY": ["+452%", "+94%", "+62%", "-16%", "+55%"],
    })


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.title("🧠 Smart Suite")
    st.caption("智系列 · GEO Content Pipeline · Phase I")
    st.divider()

    page = st.radio(
        "导航",
        [
            "🏠 总览",
            "📚 智库 (Step 1)",
            "✍️ 智造 (Step 2)",
            "🔧 智优 (Step 3)",
            "📦 智布 (Step 4)",
            "📈 智析 (Step 6)",
            "🎯 智中枢",
        ],
        label_visibility="collapsed",
    )
    st.divider()

    batches = get_batches()
    selected_batch = st.selectbox("📂 当前批次", batches, key="batch")
    market = st.selectbox("🌍 Market", ["ALL", "CN", "NA", "EU", "JP"])
    kw_limit = st.number_input("🔑 Keyword Limit", 1, 50, 10)
    week = st.text_input("📅 Week", "WK21")

    st.divider()
    st.caption(f"路径: {BASE_PATH}")


# ============================================================
# PAGE: 总览
# ============================================================
if page == "🏠 总览":
    st.title("🏠 Smart Suite 总览")
    st.caption(f"批次: {selected_batch} | 全流程状态一览")

    # --- Pipeline Progress ---
    st.subheader("📊 流水线进度")
    status = get_batch_status(selected_batch)
    cols = st.columns(4)
    for i, (folder, info) in enumerate(status.items()):
        with cols[i]:
            if info["done"]:
                st.success(f"{info['icon']} **{info['name']}**")
                st.caption(f"✅ 完成 · {info['files']} 文件")
            else:
                st.warning(f"{info['icon']} **{info['name']}**")
                st.caption("⏳ 待执行")

    st.divider()

    # --- KPI Summary ---
    st.subheader("📈 Output KPI (WK20)")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("GEO+Direct YTD", "28,741", "+55% YoY")
    with c2:
        st.metric("CN GEO YTD", "574", "+452%")
    with c3:
        st.metric("WW Direct EST", "25,863", "+62%")
    with c4:
        st.metric("vs 大盘", "+78 ppts", "跑赢 SSR")

    st.divider()

    # --- Batch Summary ---
    st.subheader("📋 批次汇总")
    df_summary = load_batch_summary(selected_batch)
    if not df_summary.empty:
        row = df_summary.iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("关键词", int(row.get("total_keywords", 0)))
        with c2:
            st.metric("AI Queries", int(row.get("total_queries", 0)))
        with c3:
            st.metric("生成内容", int(row.get("generated_content", 0)))
        with c4:
            st.metric("平均评分", f"{row.get('avg_overall_score', 0):.2f}/5")
        with c5:
            st.metric("完成率", row.get("completion_rate", "N/A"))
    else:
        st.info("暂无批次汇总，执行 Step 5 生成。")

    # --- Quick Actions ---
    st.divider()
    st.subheader("⚡ 快捷指令")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.code(f"全流程执行 {selected_batch}，market={market}，keyword_limit={kw_limit}", language=None)
        st.caption("全流程 Steps 1-5")
    with col_b:
        st.code(f"智中枢决策 {week}，生成周度计划", language=None)
        st.caption("智中枢决策")
    with col_c:
        st.code(f"生成智析报告 {week}", language=None)
        st.caption("智析报告")


# ============================================================
# PAGE: 智库 (Step 1)
# ============================================================
elif page == "📚 智库 (Step 1)":
    st.title("📚 智库 – AI Query Generation")
    st.caption("Step 1: 从 SEO/SEM 关键词生成 AI 原生搜索查询")

    tab_input, tab_output, tab_exec = st.tabs(["📥 输入 (关键词库)", "📤 输出 (AI Queries)", "▶️ 执行"])

    with tab_input:
        df_kw = load_keywords()
        if not df_kw.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总关键词", len(df_kw))
            with col2:
                if "market" in df_kw.columns:
                    st.metric("Markets", df_kw["market"].nunique())
            with col3:
                if "keyword_type" in df_kw.columns:
                    st.metric("类型", df_kw["keyword_type"].nunique())

            # Filters
            st.subheader("关键词筛选")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                mkt_filter = st.multiselect("Market", df_kw["market"].unique().tolist(),
                                            default=df_kw["market"].unique().tolist(), key="kw_mkt")
            with col_f2:
                type_filter = st.multiselect("Type", df_kw["keyword_type"].unique().tolist(),
                                             default=df_kw["keyword_type"].unique().tolist(), key="kw_type")
            filtered = df_kw[(df_kw["market"].isin(mkt_filter)) & (df_kw["keyword_type"].isin(type_filter))]
            st.dataframe(filtered, use_container_width=True, hide_index=True)
        else:
            st.warning("未找到 input/seo_sem_keywords.csv")

    with tab_output:
        df_q = load_zhiku(selected_batch)
        if not df_q.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总 Queries", len(df_q))
            with col2:
                if "is_selected" in df_q.columns:
                    sel = df_q[df_q["is_selected"].astype(str).str.upper() == "TRUE"].shape[0]
                    st.metric("已选中", sel)
            with col3:
                if "intent_type" in df_q.columns:
                    st.metric("意图类型", df_q["intent_type"].nunique())

            # Intent distribution
            if "intent_type" in df_q.columns:
                fig = px.pie(df_q, names="intent_type", title="Intent Type 分布",
                             color_discrete_sequence=px.colors.qualitative.Set3, hole=0.35)
                fig.update_layout(height=280, margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig, use_container_width=True)

            display_cols = [c for c in ["keyword", "ai_query", "intent_type", "priority_score", "is_selected"]
                           if c in df_q.columns]
            st.dataframe(df_q[display_cols], use_container_width=True, hide_index=True)
        else:
            st.info(f"批次 {selected_batch} 暂无智库输出")

    with tab_exec:
        st.subheader("▶️ 执行智库")
        st.markdown(f"""
        **参数：**
        - 批次: `{selected_batch}`
        - Market: `{market}`
        - Keyword Limit: `{kw_limit}`
        """)
        cmd = f"执行智库 {selected_batch}，market={market}，keyword_limit={kw_limit}"
        st.code(cmd, language=None)
        st.caption("复制上方指令到 Kiro 对话框执行")


# ============================================================
# PAGE: 智造 (Step 2)
# ============================================================
elif page == "✍️ 智造 (Step 2)":
    st.title("✍️ 智造 – Content Generation")
    st.caption("Step 2: 基于 AI Queries 生成 SEO+GEO 双优化内容")

    tab_output, tab_quality, tab_exec = st.tabs(["📤 内容列表", "📊 质量概览", "▶️ 执行"])

    with tab_output:
        df_z = load_zhizao(selected_batch)
        if not df_z.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("生成文章数", len(df_z))
            with col2:
                if "word_count" in df_z.columns:
                    st.metric("平均字数", f"{df_z['word_count'].mean():.0f}")
            with col3:
                if "version" in df_z.columns:
                    st.metric("版本", df_z["version"].iloc[0] if len(df_z) > 0 else "N/A")

            # Article list
            display_cols = [c for c in ["content_id", "ai_query", "title", "word_count", "version"]
                           if c in df_z.columns]
            if display_cols:
                st.dataframe(df_z[display_cols], use_container_width=True, hide_index=True)

            # Preview single article
            if "title" in df_z.columns and len(df_z) > 0:
                st.subheader("📖 文章预览")
                titles = df_z["title"].tolist()
                sel_title = st.selectbox("选择文章", titles, key="zhizao_preview")
                row = df_z[df_z["title"] == sel_title].iloc[0]
                if "content_draft" in df_z.columns:
                    with st.expander("展开正文", expanded=False):
                        st.markdown(str(row.get("content_draft", ""))[:3000])
        else:
            st.info(f"批次 {selected_batch} 暂无智造输出")

    with tab_quality:
        df_z = load_zhizao(selected_batch)
        if not df_z.empty and "word_count" in df_z.columns:
            st.subheader("字数分布")
            fig_wc = px.bar(df_z, x=df_z.get("title", df_z.get("content_id", df_z.index)),
                            y="word_count", color="word_count",
                            color_continuous_scale=["#f87171", "#fbbf24", "#52b788"])
            fig_wc.add_hline(y=800, line_dash="dash", line_color="red",
                             annotation_text="最低要求 800字")
            fig_wc.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0),
                                 showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_wc, use_container_width=True)

            # Compliance checklist
            st.subheader("内容合规检查")
            for _, row in df_z.iterrows():
                title = row.get("title", row.get("content_id", "Unknown"))
                wc = row.get("word_count", 0)
                status = "✅" if wc >= 800 else "❌"
                st.text(f"{status} {title} — {wc} 字")
        else:
            st.info("暂无数据")

    with tab_exec:
        st.subheader("▶️ 执行智造")
        st.markdown(f"**批次:** `{selected_batch}`")
        cmd = f"执行智造 {selected_batch}，生成内容"
        st.code(cmd, language=None)
        st.caption("复制上方指令到 Kiro 对话框执行")


# ============================================================
# PAGE: 智优 (Step 3 / 3.5 / 3.6)
# ============================================================
elif page == "🔧 智优 (Step 3)":
    st.title("🔧 智优 – Score · Rewrite · Compliance")
    st.caption("Step 3: 评分 → Step 3.5: 重写优化 → Step 3.6: 合规审查")

    tab_score, tab_rewrite, tab_compliance, tab_exec = st.tabs(
        ["📊 评分卡 (3)", "✍️ 优化重写 (3.5)", "⚖️ 合规审查 (3.6)", "▶️ 执行"]
    )

    with tab_score:
        df_sc = load_scorecard(selected_batch)
        if not df_sc.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("评分文章数", len(df_sc))
            with col2:
                if "overall_score" in df_sc.columns:
                    st.metric("平均总分", f"{df_sc['overall_score'].mean():.2f}/5")
            with col3:
                if "is_approved" in df_sc.columns:
                    approved = df_sc[df_sc["is_approved"].astype(str).str.upper() == "TRUE"].shape[0]
                    st.metric("通过数", f"{approved}/{len(df_sc)}")

            # Radar chart
            score_cols = [c for c in df_sc.columns if c.endswith("_score") and c != "overall_score"]
            if score_cols:
                avg_scores = df_sc[score_cols].mean()
                labels = [c.replace("_score", "").replace("_", " ").title() for c in score_cols]
                fig_r = go.Figure()
                fig_r.add_trace(go.Scatterpolar(
                    r=avg_scores.values.tolist() + [avg_scores.values[0]],
                    theta=labels + [labels[0]],
                    fill="toself", line=dict(color="#4a9eff"),
                ))
                fig_r.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                    height=320, margin=dict(l=40, r=40, t=20, b=20),
                )
                st.plotly_chart(fig_r, use_container_width=True)

            st.dataframe(df_sc, use_container_width=True, hide_index=True)
        else:
            st.info(f"批次 {selected_batch} 暂无评分卡")

    with tab_rewrite:
        df_opt = load_optimized(selected_batch)
        if not df_opt.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("优化文章数", len(df_opt))
            with col2:
                if "word_count" in df_opt.columns:
                    st.metric("平均字数", f"{df_opt['word_count'].mean():.0f}")
            with col3:
                if "version" in df_opt.columns:
                    st.metric("版本", df_opt["version"].iloc[0])

            display_cols = [c for c in ["content_id", "optimized_title", "word_count",
                                        "table_count", "list_count", "link_count", "version"]
                           if c in df_opt.columns]
            if display_cols:
                st.dataframe(df_opt[display_cols], use_container_width=True, hide_index=True)

            # Changes applied
            if "changes_applied" in df_opt.columns:
                st.subheader("应用的优化建议")
                for _, row in df_opt.iterrows():
                    title = row.get("optimized_title", row.get("content_id", ""))
                    with st.expander(f"📝 {title}"):
                        st.text(str(row.get("changes_applied", "")))
        else:
            st.info(f"批次 {selected_batch} 暂无优化重写输出")

    with tab_compliance:
        df_comp = load_compliance(selected_batch)
        if not df_comp.empty:
            col1, col2, col3 = st.columns(3)
            if "compliance_status" in df_comp.columns:
                with col1:
                    st.metric("PASS", (df_comp["compliance_status"] == "PASS").sum())
                with col2:
                    st.metric("FIXED", (df_comp["compliance_status"] == "FIXED").sum())
                with col3:
                    st.metric("BLOCKED", (df_comp["compliance_status"] == "BLOCKED").sum())

            st.dataframe(df_comp, use_container_width=True, hide_index=True)
        else:
            st.info(f"批次 {selected_batch} 暂无合规审查结果")

    with tab_exec:
        st.subheader("▶️ 执行智优系列")
        st.markdown("按顺序执行：评分 → 重写 → 合规审查")

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("**Step 3: 评分**")
            st.code(f"执行智优评分 {selected_batch}", language=None)
        with col_b:
            st.markdown("**Step 3.5: 重写**")
            st.code(f"执行智优执行 {selected_batch}，基于评分建议重写", language=None)
        with col_c:
            st.markdown("**Step 3.6: 合规**")
            st.code(f"执行合规审查 {selected_batch}", language=None)


# ============================================================
# PAGE: 智布 (Step 4)
# ============================================================
elif page == "📦 智布 (Step 4)":
    st.title("📦 智布 – JSON Formatting")
    st.caption("Step 4: 将优化内容转换为结构化 JSON 发布格式")

    tab_output, tab_preview, tab_exec = st.tabs(["📤 输出概览", "🔍 JSON 预览", "▶️ 执行"])

    with tab_output:
        data = load_zhibu(selected_batch)
        if data:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总条目", data.get("total_items", 0))
            with col2:
                st.metric("批次", data.get("batch_id", "N/A"))
            with col3:
                kws = data.get("source_keywords", [])
                st.metric("源关键词", len(kws))

            # Items table
            items = data.get("items", [])
            if items:
                rows = []
                for item in items:
                    rows.append({
                        "content_id": item.get("content_id", ""),
                        "title": item.get("meta", {}).get("title", ""),
                        "word_count": item.get("quality_metrics", {}).get("word_count", 0),
                        "overall_score": item.get("ai_friendly", {}).get("overall_score", 0),
                        "compliance": item.get("compliance", {}).get("status", ""),
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info(f"批次 {selected_batch} 暂无智布输出")

    with tab_preview:
        data = load_zhibu(selected_batch)
        if data:
            items = data.get("items", [])
            if items:
                sel_idx = st.selectbox("选择条目", range(len(items)),
                                       format_func=lambda i: items[i].get("meta", {}).get("title", f"Item {i}"))
                st.json(items[sel_idx])
        else:
            st.info("暂无 JSON 数据")

    with tab_exec:
        st.subheader("▶️ 执行智布")
        st.code(f"执行智布 {selected_batch}，生成JSON", language=None)
        st.caption("复制上方指令到 Kiro 对话框执行")


# ============================================================
# PAGE: 智析 (Step 6)
# ============================================================
elif page == "📈 智析 (Step 6)":
    st.title("📈 智析 – Performance Report")
    st.caption("Step 6: GEO + WW Direct Reg Start 趋势分析")

    tab_trend, tab_ytd, tab_attribution, tab_exec = st.tabs(
        ["📊 Weekly 趋势", "📋 YTD 对比", "🎯 归因分析", "▶️ 执行"]
    )

    with tab_trend:
        df_w = get_weekly_metrics()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_w["Week"], y=df_w["Total"],
                                 mode="lines+markers", name="Total",
                                 line=dict(color="#4a9eff", width=3), marker=dict(size=8)))
        fig.add_trace(go.Scatter(x=df_w["Week"], y=df_w["WW_Direct_EST"],
                                 mode="lines+markers", name="WW Direct EST",
                                 line=dict(color="#52b788", width=2)))
        fig.add_trace(go.Scatter(x=df_w["Week"], y=df_w["CN_GEO"],
                                 mode="lines+markers", name="CN GEO",
                                 line=dict(color="#fbbf24", width=2)))
        fig.add_trace(go.Scatter(x=df_w["Week"], y=df_w["WW_GEO"],
                                 mode="lines+markers", name="WW GEO",
                                 line=dict(color="#a78bfa", width=2)))
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0),
                          legend=dict(orientation="h", y=-0.15), yaxis_title="Reg Starts")
        st.plotly_chart(fig, use_container_width=True)

        # WoW bar
        st.subheader("WoW 变化率 (WK20 vs WK19)")
        df_wow = pd.DataFrame({
            "Channel": ["CN GEO", "WW GEO", "WW Direct EST", "WW Direct EM", "Total"],
            "WoW%": [24, 41, 32, 3, 31],
        })
        fig_wow = px.bar(df_wow, x="Channel", y="WoW%", text="WoW%",
                         color="WoW%", color_continuous_scale=["#f87171", "#fbbf24", "#52b788"])
        fig_wow.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_wow.update_layout(height=260, margin=dict(l=0, r=0, t=10, b=0),
                              showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_wow, use_container_width=True)

    with tab_ytd:
        df_ytd = get_ytd_metrics()
        df_ytd["增量"] = df_ytd["YTD_Actual"] - df_ytd["YTD_PY"]

        # Bar chart comparison
        df_bar = df_ytd[df_ytd["Channel"] != "Total"].copy()
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(name="YTD Actual", x=df_bar["Channel"], y=df_bar["YTD_Actual"],
                                 marker_color="#4a9eff"))
        fig_bar.add_trace(go.Bar(name="YTD PY", x=df_bar["Channel"], y=df_bar["YTD_PY"],
                                 marker_color="#555"))
        fig_bar.update_layout(barmode="group", height=300, margin=dict(l=0, r=0, t=10, b=0),
                              legend=dict(orientation="h", y=-0.15))
        st.plotly_chart(fig_bar, use_container_width=True)

        st.dataframe(df_ytd, use_container_width=True, hide_index=True)

        # Benchmark
        st.subheader("vs SSR 大盘")
        bench = pd.DataFrame({
            "维度": ["GEO + WW Direct", "Net (含 CN Direct+SEO)", "SSR Total 大盘"],
            "YTD YoY": ["+55%", "-10%", "-23%"],
            "vs 大盘": ["+78 ppts", "+13 ppts", "Benchmark"],
        })
        st.dataframe(bench, use_container_width=True, hide_index=True)

    with tab_attribution:
        st.subheader("🎯 WK20 归因分析")
        st.markdown("""
**Output 变化：**
- WK20 GEO + WW Direct = **2,047**，WoW **+31%**
- CN GEO 连续 4 周增长：32→33→33→41
- WW Direct EST 全面反弹：NA +29%, EU +42%, JP +67%
- WW Direct EM 持平，SA/AE 微降

**归因判断：**
| 渠道 | 判断 | 原因 |
|---|---|---|
| CN GEO | 🟢 持续增长 | AI search 带 referrer 流量稳步提升 |
| WW Direct EST | 🟢 全面反弹 | 前几周发布内容被 AI 引擎收录（滞后效应）|
| JP Direct | 🟢 +67% WoW | 日本 AI search 渗透加速 |
| WW Direct EM | 🟡 持平 | SA/AE 微降，需排查 |
        """)

        st.subheader("🚀 Opportunities")
        st.markdown("""
- 增加 EU/JP 检索短语覆盖（GEO 绝对值低）
- 排查 AE Direct 下降原因（YoY -61%）
- 建立 input 活动周度追踪，完善归因链路
- 增加 EM 市场内容覆盖（特别是 AU）
        """)

    with tab_exec:
        st.subheader("▶️ 执行智析")
        st.code(f"生成智析报告 {week}", language=None)
        st.caption("复制上方指令到 Kiro 对话框执行")

        st.subheader("📂 已有报告")
        if METRICS_PATH.exists():
            reports = sorted(METRICS_PATH.glob("zhixi_report_*.xlsx"), reverse=True)
            for r in reports[:5]:
                st.text(f"📄 {r.name}  ({r.stat().st_size/1024:.1f} KB)")


# ============================================================
# PAGE: 智中枢
# ============================================================
elif page == "🎯 智中枢":
    st.title("🎯 智中枢 – Decision Engine")
    st.caption("基于智析数据 + 7 条决策规则，生成周度行动计划")

    tab_rules, tab_plan, tab_exec = st.tabs(["📜 决策规则", "📋 本周计划", "▶️ 执行"])

    with tab_rules:
        st.subheader("7 条决策规则")
        rules = [
            ("Rule 1: Growth Acceleration", "渠道 WoW > +30% 连续2周", "增加该渠道内容产出", "🟢"),
            ("Rule 2: Decline Alert", "渠道 WoW < -20%", "暂停新内容，排查原因", "🔴"),
            ("Rule 3: Low Absolute Volume", "GEO 周 < 50 且 YoY > +50%", "扩大关键词覆盖", "🟡"),
            ("Rule 4: High-Performing Site", "站点 YoY > +100%", "优先扩展该站点内容", "🟢"),
            ("Rule 5: Content Gap", "市场有流量但2周无新内容", "重启全流程", "🟡"),
            ("Rule 6: Benchmark Comparison", "我方 YoY < 大盘 YoY", "策略复盘", "🔴"),
            ("Rule 7: Input-Output Lag", "内容发布2-3周无提升", "检查内容质量/重写", "🟡"),
        ]
        for name, condition, action, emoji in rules:
            with st.expander(f"{emoji} {name}"):
                st.markdown(f"**触发条件:** {condition}")
                st.markdown(f"**执行动作:** {action}")

    with tab_plan:
        st.subheader(f"📋 Smart Suite Weekly Plan - {week}")
        st.markdown(f"Based on 智析 data (WK20):")

        st.markdown("""
**🟢 ACCELERATE:**
- CN GEO: 连续4周增长 → 增加 CN 关键词覆盖
- JP Direct: +67% WoW, +103% YoY → 优先扩展 JP 内容
- WW Direct EST: +32% WoW → 保持当前节奏

**🟡 MONITOR:**
- WW Direct EM: 基本持平 → 观察下周趋势
- EU GEO: 绝对值低(5/月) → 扩大 EU 检索短语

**🔴 INVESTIGATE:**
- AE Direct: YoY -61% → 排查下降原因
        """)

        st.divider()
        st.markdown(f"""
**📝 THIS WEEK'S EXECUTION PLAN:**
- 智库: 15 new keywords (JP×5, CN×5, EU×5)
- 智造: 6 articles (JP×2, CN×2, EU×2)
- 智优: Review all 6 articles
- 智布: Publish 6 articles

**⏰ ESTIMATED TIME:** 4-6 hours
        """)

    with tab_exec:
        st.subheader("▶️ 执行智中枢")
        st.code(f"智中枢决策 {week}，生成周度计划", language=None)
        st.caption("复制上方指令到 Kiro 对话框执行")

        st.divider()
        st.subheader("🚀 全流程快捷指令")
        pipeline_cmds = [
            ("1. 智库", f"执行智库 {selected_batch}，market={market}，keyword_limit={kw_limit}"),
            ("2. 智造", f"执行智造 {selected_batch}，生成内容"),
            ("3. 智优评分", f"执行智优评分 {selected_batch}"),
            ("3.5 智优执行", f"执行智优执行 {selected_batch}，基于评分建议重写"),
            ("3.6 合规审查", f"执行合规审查 {selected_batch}"),
            ("4. 智布", f"执行智布 {selected_batch}，生成JSON"),
            ("5. 批次报告", f"生成批次报告 {selected_batch}"),
            ("6. 智析", f"生成智析报告 {week}"),
        ]
        for label, cmd in pipeline_cmds:
            st.text(f"📌 {label}")
            st.code(cmd, language=None)


# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption(
    f"Smart Suite Phase I · 智系列控制台 · "
    f"{datetime.now().strftime('%Y-%m-%d %H:%M')} · "
    f"Batches: {len(batches)}"
)
