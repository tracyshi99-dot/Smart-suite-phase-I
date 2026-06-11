"""
Smart Suite 智系列控制台 - Streamlit UI (重构版)
单页线性流程，统一风格，CTA 跳转
Run: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
from datetime import datetime
import tempfile
import os

# --- Config ---
BASE_PATH = Path(__file__).parent.parent
OUTPUT_PATH = BASE_PATH / "output"
INPUT_PATH = BASE_PATH / "input"
METRICS_PATH = OUTPUT_PATH / "metrics"

if not OUTPUT_PATH.exists():
    _CLOUD_OUTPUT = Path(tempfile.gettempdir()) / "smartsuite_output"
    _CLOUD_OUTPUT.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH = _CLOUD_OUTPUT
    METRICS_PATH = OUTPUT_PATH / "metrics"
    if not INPUT_PATH.exists():
        INPUT_PATH = Path(tempfile.gettempdir()) / "smartsuite_input"
        INPUT_PATH.mkdir(parents=True, exist_ok=True)

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
</style>
""", unsafe_allow_html=True)


# --- Pipeline Flow Visual Component ---
PIPELINE_STEPS = [
    {"id": "zhiku", "name": "智库", "page": "📚 智库"},
    {"id": "zhizao", "name": "智造", "page": "✍️ 智造"},
    {"id": "zhiyou", "name": "智优", "page": "🔧 智优"},
    {"id": "zhibu", "name": "智布", "page": "📦 智布"},
    {"id": "zhichuan", "name": "智传", "page": "📡 智传"},
    {"id": "zhixi", "name": "智析", "page": "📈 智析"},
    {"id": "zhongshu", "name": "智中枢", "page": "🎯 智中枢"},
]


def render_pipeline_flow(current_step_id: str, batch_id: str = ""):
    """Render pipeline: current step bright, all others dimmed gray."""
    import streamlit.components.v1 as components

    # Build HTML cards — only current is highlighted, rest are gray
    cards_html = ""
    for i, step in enumerate(PIPELINE_STEPS):
        sid = step["id"]
        is_current = (sid == current_step_id)

        if is_current:
            border_color = "#4a9eff"
            bg = "#1a2940"
            text_color = "#fff"
            icon_html = '<div style="font-size:14px;margin-bottom:2px;">🔵</div>'
        else:
            border_color = "#555"
            bg = "#1a1f2e"
            text_color = "#777"
            icon_html = '<div style="font-size:14px;margin-bottom:2px;color:#666;">○</div>'

        cards_html += f'''
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    width:56px;height:56px;border-radius:10px;border:2px solid {border_color};
                    background:{bg};">
            {icon_html}
            <div style="font-size:11px;font-weight:600;color:{text_color};">{step["name"]}</div>
        </div>
        '''
        if i < len(PIPELINE_STEPS) - 1:
            arrow_color = "#4a9eff" if is_current else "#555"
            cards_html += f'<div style="color:{arrow_color};font-size:12px;margin:0 4px;">→</div>'

    html = f'''
    <div style="display:flex;align-items:center;justify-content:center;padding:10px 0;gap:0;">
        {cards_html}
    </div>
    '''
    components.html(html, height=85, scrolling=False)


# --- 35 Categories ---
CATEGORIES_35 = [
    "跨境电商知识早知道",
    "跨境电商行业入门了解",
    "跨境电商怎么样",
    "怎么做跨境电商及流程费用了解",
    "做跨境电商的准备工作",
]
CATEGORIES_35 += [
    "如何选择渠道及目的地",
    "跨境电商成熟站点优势介绍",
    "跨境电商新兴站点优势介绍",
    "亚马逊商城基础情况了解",
    "亚马逊商城怎么样",
    "跨境电商选品方法及趋势",
    "跨境电商热门品类解析",
    "新卖家入门实操宝典",
    "站点综合信息及选品建议",
    "北美站点情况及选品思路",
    "欧洲站点情况及选品思路",
    "日本站点情况及选品思路",
    "新兴站点情况及选品思路",
    "新手怎么注册亚马逊",
    "亚马逊开店成本费用详解",
    "开店审核常见问题解答",
    "亚马逊物流仓储科普",
    "欧洲增值税VAT介绍",
    "其他站点税务要求",
    "合规政策及操作流程",
    "教你打造优质Listing",
    "如何做好品牌营销",
    "店铺运营提升全攻略",
    "店铺运营基础知识",
    "官方服务与运营工具盘点",
    "亚马逊广告基础知识大全",
    "亚马逊广告实操技巧",
    "关键节点如何推广引流",
    "了解旺季节点与如何引流",
    "卖家运营经验分享",
]


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
    """Load CSV with robust error handling for malformed files."""
    if path.exists():
        try:
            return pd.read_csv(path, encoding="utf-8-sig", on_bad_lines="skip")
        except Exception:
            # Fallback: read with Python engine which is more forgiving
            try:
                return pd.read_csv(path, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
            except Exception:
                # Last resort: read line by line
                try:
                    import csv
                    with open(path, encoding="utf-8-sig", newline="") as f:
                        reader = csv.reader(f)
                        rows = []
                        header = next(reader, None)
                        if header:
                            for row in reader:
                                if len(row) == len(header):
                                    rows.append(row)
                            if rows:
                                return pd.DataFrame(rows, columns=header)
                except Exception:
                    pass
                return pd.DataFrame()
    return pd.DataFrame()


def load_keywords():
    if "uploaded_keywords" in st.session_state:
        return st.session_state["uploaded_keywords"]
    df = load_csv_safe(INPUT_PATH / "seo_sem_keywords.csv")
    return df


def load_zhiku(batch_id: str):
    return load_csv_safe(OUTPUT_PATH / batch_id / "01_zhiku" / "zhiku_ai_queries.csv")


def load_zhiku_live(batch_id: str):
    """Load zhiku from file at call time (for progress tracking)."""
    return load_csv_safe(OUTPUT_PATH / batch_id / "01_zhiku" / "zhiku_ai_queries.csv")


def load_zhizao(batch_id: str):
    main = OUTPUT_PATH / batch_id / "02_zhizao" / "zhizao_draft_content.csv"
    if main.exists():
        return load_csv_safe(main)
    parts_dir = OUTPUT_PATH / batch_id / "02_zhizao"
    if parts_dir.exists():
        parts = sorted(parts_dir.glob("zhizao_draft_content_p*.csv"))
        if parts:
            dfs = [load_csv_safe(p) for p in parts]
            return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()


def load_scorecard(batch_id: str):
    return load_csv_safe(OUTPUT_PATH / batch_id / "03_zhiyou" / "zhiyou_scorecard.csv")


def load_optimized(batch_id: str):
    return load_csv_safe(OUTPUT_PATH / batch_id / "03_zhiyou" / "zhiyou_optimized_content.csv")


def load_compliance(batch_id: str):
    return load_csv_safe(OUTPUT_PATH / batch_id / "03_zhiyou" / "zhiyou_compliance_checked.csv")


def load_zhibu(batch_id: str):
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
    return load_csv_safe(OUTPUT_PATH / "Batch_Summary_Report" / f"{batch_id}_summary.csv")


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


def jump_to(page_name: str):
    """Set session state to jump to a page on next rerun."""
    st.session_state["jump_to_page"] = page_name


# ============================================================
# NAVIGATION PAGES
# ============================================================
NAV_PAGES = [
    "🏠 总览",
    "📚 智库",
    "✍️ 智造",
    "🔧 智优",
    "📦 智布",
    "📡 智传",
    "📈 智析",
    "🎯 智中枢",
    "───────────",
    "📝 需求中心",
    "🔍 引用分析",
    "⚙️ Settings",
]


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.title("🧠 Smart Suite")
    st.caption("智系列 · GEO Content Pipeline · Phase I")
    st.divider()

    # Handle jump_to_page
    if "jump_to_page" in st.session_state:
        target = st.session_state.pop("jump_to_page")
        if target in NAV_PAGES:
            st.session_state["nav_radio"] = target

    page = st.radio(
        "导航",
        NAV_PAGES,
        label_visibility="collapsed",
        key="nav_radio",
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

    # --- 工具介绍 ---
    st.subheader("🧠 Smart Suite 是什么？")
    st.markdown("""
    Smart Suite 是一套 **AI 驱动的 GEO (Generative Engine Optimization) 内容流水线工具**，
    帮助亚马逊全球开店团队高效生产、优化和分发能够被 AI 搜索引擎（ChatGPT、Perplexity、DeepSeek 等）引用的内容。

    **使用方法：** 按照 7 步流程从左到右执行，每一步完成后点击 CTA 跳转到下一步。也可以跳过中间步骤直接执行任意工具。
    """)

    st.divider()
    st.subheader("🔧 7 个 AI 工具")

    tool_info = [
        ("📚 智库", "检索短语生成与管理", "从 SEO/SEM 关键词或核心词根裂变生成 AI 原生检索短语，自动分类、去重、评分"),
        ("✍️ 智造", "内容生成", "基于选中的检索短语，AI 自动生成 SEO+GEO 双优化的长文章"),
        ("🔧 智优", "内容优化", "一键完成：AI 评分（5维度）→ 重写优化 → 合规审查"),
        ("📦 智布", "格式化发布", "将优化后的内容转换为 JSON 结构化数据和 Word 文档，用于 CMS 发布"),
        ("📡 智传", "内容分发", "将内容分发到各个渠道（官网、第三方平台等），追踪发布状态"),
        ("📈 智析", "效果分析", "追踪 GEO + WW Direct Reg Start 趋势，周度/月度/YTD 数据分析，归因判断"),
        ("🎯 智中枢", "决策引擎", "基于智析数据 + 7 条决策规则，自动生成周度行动计划和优先级建议"),
    ]

    for icon_name, subtitle, desc in tool_info:
        with st.expander(f"{icon_name} — {subtitle}"):
            st.markdown(desc)

    st.divider()

    # (End of overview page)


# ============================================================
# PAGE: 智库 (Step 1) — 单页线性流程
# ============================================================
elif page == "📚 智库":
    st.title("📚 智库 – AI 检索短语生成")
    render_pipeline_flow("zhiku", selected_batch)
    st.caption("Step 1: 从 SEO/SEM 关键词或核心词根裂变生成 AI 原生检索短语")

    # ─── ① 生成检索短语 ───
    st.subheader("① 生成检索短语")

    # Load current zhiku data for progress tracking
    df_q_current = load_zhiku_live(selected_batch)
    current_count = len(df_q_current) if not df_q_current.empty else 0

    st.caption("可选 A、B 单独或同时使用，结果自动合并去重")

    col_src_a, col_src_b = st.columns(2)

    # ── 源 A：SEO/SEM 关键词裂变 ──
    with col_src_a:
        st.markdown("**源 A：SEO/SEM 关键词裂变**")
        uploaded_file = st.file_uploader("上传关键词 CSV", type=["csv"], key="kw_upload_zhiku")
        if uploaded_file is not None:
            df_uploaded = pd.read_csv(uploaded_file, on_bad_lines="skip")
            st.session_state["uploaded_keywords"] = df_uploaded
            INPUT_PATH.mkdir(parents=True, exist_ok=True)
            df_uploaded.to_csv(INPUT_PATH / "seo_sem_keywords.csv", index=False, encoding="utf-8-sig")
            st.success(f"✅ {len(df_uploaded)} 个关键词")

        df_kw = load_keywords()
        kw_count = len(df_kw) if not df_kw.empty else 0
        if kw_count > 0:
            target_a = kw_count * 10
            # Show current progress
            _df_live = load_csv_safe(OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv")
            existing_a = len(_df_live) if not _df_live.empty else 0
            st.caption(f"{kw_count} 关键词 · 预估 ~{target_a} 条")
            if existing_a > 0:
                st.progress(min(1.0, existing_a / target_a), text=f"库中 {existing_a}/{target_a}")
                btn_text_a = f"🔄 继续裂变源 A（库中 {existing_a} 条）"
            else:
                btn_text_a = "🚀 裂变源 A"
            kw_per_batch = st.select_slider("每次处理关键词数", options=[10, 20, 30, 50], value=10, key="kw_per_batch")
            if st.button(btn_text_a, type="primary", key="run_source_a"):
                try:
                    from engine import run_zhiku
                    with st.spinner("源 A 裂变中..."):
                        result = run_zhiku(selected_batch, market, kw_per_batch)
                    if result["success"]:
                        st.success(f"✅ +{result['query_count']} 条")
                    else:
                        st.error(result['error'])
                except Exception as e:
                    st.error(str(e))

    # ── 源 B：核心词根裂变 ──
    with col_src_b:
        st.markdown("**源 B：核心词根裂变**")
        seed_words = st.text_area("核心词根（每行一个）", placeholder="跨境电商\n亚马逊开店\n选品", height=100, key="seed_words_input")
        seeds = [w.strip() for w in seed_words.strip().split("\n") if w.strip()] if seed_words else []

        if seeds:
            st.caption(f"{len(seeds)} 个词根 · 预估 ~{len(seeds) * 15} 条")

        if st.button("🚀 裂变源 B", type="primary", key="run_source_b", disabled=(len(seeds) == 0)):
            if seeds:
                try:
                    from engine import run_semantic_expansion
                    total_gen = 0
                    with st.spinner("源 B 裂变中..."):
                        for seed in seeds:
                            r = run_semantic_expansion(seed, market, 15, "zh", selected_batch)
                            if r.get("success"):
                                total_gen += r.get("query_count", 0)
                    if total_gen > 0:
                        st.success(f"✅ +{total_gen} 条")
                    else:
                        st.warning("未生成短语")
                except Exception as e:
                    st.error(str(e))

    # Progress bar (full width)
    if current_count > 0:
        col_info, col_clear = st.columns([3, 1])
        with col_info:
            st.caption(f"📊 短语库已有 {current_count} 条")
        with col_clear:
            if st.button("🗑️ 清空", key="clear_zhiku"):
                zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                if zhiku_file.exists():
                    zhiku_file.unlink()
                st.success("已清空")

    st.divider()

    # ─── 上传已有短语 ───
    with st.expander("📤 上传已有检索短语（人工准备）", expanded=False):
        st.caption("直接上传准备好的检索短语 CSV，自动合并到短语库")
        uploaded_phrases = st.file_uploader("上传 CSV", type=["csv", "xlsx"], key="upload_existing_phrases")
        if uploaded_phrases:
            try:
                if uploaded_phrases.name.endswith(".xlsx"):
                    df_import = pd.read_excel(uploaded_phrases, engine="openpyxl")
                else:
                    df_import = pd.read_csv(uploaded_phrases, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
                zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                if zhiku_file.exists():
                    df_existing = load_csv_safe(zhiku_file)
                    if not df_existing.empty:
                        df_merged = pd.concat([df_existing, df_import], ignore_index=True)
                        if "ai_query" in df_merged.columns:
                            df_merged = df_merged.drop_duplicates(subset=["ai_query"], keep="first")
                        df_merged.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                        st.success(f"✅ 导入 {len(df_import)} 条，合并去重后库中 {len(df_merged)} 条")
                    else:
                        df_import.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                        st.success(f"✅ 导入 {len(df_import)} 条")
                else:
                    df_import.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                    st.success(f"✅ 导入 {len(df_import)} 条")
            except Exception as e:
                st.error(f"导入失败: {e}")

    st.divider()

    # ─── ② 短语库 — 分类 & 校对 ───
    st.subheader("② 短语库 — 分类 & 校对")

    df_q = load_zhiku_live(selected_batch)

    if df_q.empty:
        st.caption("⏳ 请先执行第①步生成检索短语")
    else:
        # Filters — simple selectbox
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            if "category" in df_q.columns:
                cat_options = ["全部"] + sorted(df_q["category"].dropna().unique().tolist())
                cat_filter = st.selectbox("按类别筛选", cat_options, key="cat_filter")
            else:
                cat_filter = "全部"
        with col_f2:
            score_range = st.slider("按综合分筛选", 1.0, 5.0, (1.0, 5.0), 0.5, key="score_filter")

        # Apply filters
        df_display = df_q.copy()
        if cat_filter != "全部" and "category" in df_display.columns:
            df_display = df_display[df_display["category"] == cat_filter]
        if "priority_score" in df_display.columns:
            df_display["priority_score"] = pd.to_numeric(df_display["priority_score"], errors="coerce")
            df_display = df_display[
                (df_display["priority_score"] >= score_range[0]) &
                (df_display["priority_score"] <= score_range[1])
            ]

        # Editable table columns
        edit_cols = [c for c in [
            "ai_query", "category", "priority_score", "estimated_volume",
            "ai_fit_score", "target_market", "is_selected"
        ] if c in df_display.columns]

        if edit_cols:
            # Select all/none toggle
            if "is_selected" in df_display.columns:
                select_action = st.radio("选中操作", ["不变", "全选", "全不选"], horizontal=True, key="select_action", label_visibility="collapsed")
                if select_action == "全选":
                    output_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                    df_q["is_selected"] = "TRUE"
                    df_q.to_csv(output_file, index=False, encoding="utf-8-sig")
                    st.rerun()
                elif select_action == "全不选":
                    output_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                    df_q["is_selected"] = "FALSE"
                    df_q.to_csv(output_file, index=False, encoding="utf-8-sig")
                    st.rerun()

            # Configure column types for data editor
            column_config = {}
            if "category" in df_display.columns:
                column_config["category"] = st.column_config.SelectboxColumn(
                    "类别", options=CATEGORIES_35, width="medium"
                )
            if "is_selected" in df_display.columns:
                column_config["is_selected"] = st.column_config.CheckboxColumn("选中")
            if "target_market" in df_display.columns:
                column_config["target_market"] = st.column_config.SelectboxColumn(
                    "适用平台", options=["CN", "WW", "Both"]
                )

            edited_df = st.data_editor(
                df_display[edit_cols],
                column_config=column_config,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                key="zhiku_editor",
            )

            # Auto-save: write edits back to file immediately
            output_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            try:
                for col in edit_cols:
                    if col in edited_df.columns and col in df_q.columns:
                        if len(edited_df) <= len(df_q):
                            df_q.loc[df_q.index[:len(edited_df)], col] = edited_df[col].values
                df_q.to_csv(output_file, index=False, encoding="utf-8-sig")
            except Exception:
                pass

            # Export button
            csv_export = df_display.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 导出筛选结果 CSV", csv_export,
                file_name=f"zhiku_filtered_{selected_batch}.csv", mime="text/csv"
            )
        else:
            st.dataframe(df_display, use_container_width=True, hide_index=True)

        # ─── 📊 类别覆盖看板 ───
        st.divider()
        st.subheader("📊 类别覆盖看板")

        col_k1, col_k2, col_k3, col_k4 = st.columns(4)
        with col_k1:
            st.metric("总短语", len(df_q))
        with col_k2:
            if "category" in df_q.columns:
                covered = df_q["category"].dropna().nunique()
                st.metric("已覆盖类别", f"{covered}/35")
            else:
                st.metric("已覆盖类别", "N/A")
        with col_k3:
            if "category" in df_q.columns:
                empty_cats = 35 - df_q["category"].dropna().nunique()
                st.metric("空类别", empty_cats)
            else:
                st.metric("空类别", "N/A")
        with col_k4:
            if "is_selected" in df_q.columns:
                sel_count = df_q[df_q["is_selected"].astype(str).str.upper() == "TRUE"].shape[0]
                st.metric("已选中", sel_count)
            else:
                st.metric("已选中", "N/A")

        if "category" in df_q.columns:
            cat_counts = df_q["category"].value_counts().reset_index()
            cat_counts.columns = ["类别", "短语数"]
            fig_cat = px.bar(cat_counts, x="类别", y="短语数", color="短语数",
                             color_continuous_scale=["#f87171", "#fbbf24", "#52b788"])
            fig_cat.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0),
                                  showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_cat, use_container_width=True)

    st.divider()

    # ─── ③ Gap 验证 ───
    st.subheader("③ Gap 验证")
    if not df_q.empty and "priority_score" in df_q.columns:
        df_gap = df_q.sort_values("priority_score", ascending=False).head(20).copy()
        gap_cols = ["ai_query", "priority_score"]
        if "category" in df_gap.columns:
            gap_cols.append("category")
        # Add gap verification columns if not present
        if "content_mentioned" not in df_gap.columns:
            df_gap["content_mentioned"] = "⚠️"
        if "has_link" not in df_gap.columns:
            df_gap["has_link"] = "❌"
        gap_cols += ["content_mentioned", "has_link"]

        gap_config = {
            "content_mentioned": st.column_config.SelectboxColumn(
                "内容提及", options=["✅", "❌", "⚠️"]
            ),
            "has_link": st.column_config.SelectboxColumn(
                "带链接", options=["✅", "❌"]
            ),
        }
        st.data_editor(
            df_gap[gap_cols], column_config=gap_config,
            use_container_width=True, hide_index=True, key="gap_editor"
        )
    elif df_q.empty:
        st.info("执行第①步后显示 Gap 验证")

    st.divider()

    # CTA → 智造
    st.subheader("✅ 智库完成")
    if st.button("➡️ 进入智造 (Step 2)", type="primary", key="cta_zhiku_to_zhizao"):
        jump_to("✍️ 智造")
        st.rerun()

    # 📜 历史记录
    with st.expander("📜 历史记录"):
        batch_path = OUTPUT_PATH / selected_batch / "01_zhiku"
        if batch_path.exists():
            files = sorted(batch_path.glob("*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
            if files:
                for f in files:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    size_kb = f.stat().st_size / 1024
                    col_i, col_d = st.columns([3, 1])
                    with col_i:
                        st.caption(f"📄 {f.name} · {size_kb:.1f}KB · 🕐 {mtime}")
                    with col_d:
                        st.download_button("⬇️", f.read_bytes(), file_name=f.name, mime="text/csv", key=f"dl_{f.name}")
            else:
                st.caption("暂无历史文件")
        else:
            st.caption("暂无历史文件")


# ============================================================
# PAGE: 智造 (Step 2) — 单页线性流程
# ============================================================
elif page == "✍️ 智造":
    st.title("✍️ 智造 – Content Generation")
    render_pipeline_flow("zhizao", selected_batch)
    st.caption("Step 2: 基于 AI Queries 生成 SEO+GEO 双优化内容")

    # --- Upload custom phrases directly ---
    with st.expander("📤 上传检索短语（跳过智库直接生产内容）", expanded=False):
        st.caption("可选：如果已有准备好的检索短语 CSV/Excel，上传到此处后点击执行智造即可直接生产内容，无需经过智库裂变流程")
        upload_direct = st.file_uploader("上传 CSV（需包含 ai_query 列）", type=["csv", "xlsx"], key="zhizao_direct_upload")
        if upload_direct:
            try:
                if upload_direct.name.endswith(".xlsx"):
                    df_direct = pd.read_excel(upload_direct, engine="openpyxl")
                else:
                    df_direct = pd.read_csv(upload_direct, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
                # Save to zhiku folder so run_zhizao can find it
                zhiku_dir = OUTPUT_PATH / selected_batch / "01_zhiku"
                zhiku_dir.mkdir(parents=True, exist_ok=True)
                zhiku_file = zhiku_dir / "zhiku_ai_queries.csv"
                # Mark all as selected
                if "is_selected" not in df_direct.columns:
                    df_direct["is_selected"] = "TRUE"
                else:
                    df_direct["is_selected"] = "TRUE"
                df_direct.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                st.success(f"✅ 已上传 {len(df_direct)} 条检索短语，点击下方执行智造")
            except Exception as e:
                st.error(f"上传失败: {e}")

    # Execution
    st.subheader("▶️ 生成内容")
    content_limit = st.number_input("生成文章数上限", 1, 20, 5, key="zhizao_limit")

    if st.button("🚀 执行智造", type="primary", key="run_zhizao"):
        try:
            from engine import run_zhizao
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress_z(pct, msg):
                progress_bar.progress(min(1.0, max(0.0, pct)))
                status_text.text(msg)

            with st.spinner("正在调用 Bedrock Claude 生成内容..."):
                result = run_zhizao(selected_batch, content_limit, update_progress_z)

            if result["success"]:
                st.success(f"✅ 智造完成！生成 {result['articles_generated']} 篇文章")
            else:
                st.error(f"❌ 失败: {result['error']}")
        except ImportError:
            st.error("engine 模块未就绪")

    st.divider()

    # Content display
    df_z = load_zhizao(selected_batch)
    if not df_z.empty:
        st.subheader("📤 生成内容列表")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("生成文章数", len(df_z))
        with col2:
            if "word_count" in df_z.columns:
                st.metric("平均字数", f"{df_z['word_count'].mean():.0f}")
        with col3:
            if "version" in df_z.columns:
                st.metric("版本", df_z["version"].iloc[0] if len(df_z) > 0 else "N/A")

        display_cols = [c for c in ["content_id", "ai_query", "title", "word_count", "version"]
                       if c in df_z.columns]
        if display_cols:
            st.dataframe(df_z[display_cols], use_container_width=True, hide_index=True)

        # Download / Upload
        st.divider()
        col_dl, col_ul, col_cl = st.columns(3)
        with col_dl:
            csv_bytes = df_z.to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 下载 CSV", csv_bytes,
                               file_name=f"zhizao_{selected_batch}.csv", mime="text/csv")
        with col_ul:
            uploaded_zhizao = st.file_uploader(
                "📤 上传修改后文件", type=["csv"], key="upload_zhizao_edit"
            )
            if uploaded_zhizao is not None:
                df_new = pd.read_csv(uploaded_zhizao, on_bad_lines="skip")
                out_path = OUTPUT_PATH / selected_batch / "02_zhizao" / "zhizao_draft_content.csv"
                out_path.parent.mkdir(parents=True, exist_ok=True)
                df_new.to_csv(out_path, index=False, encoding="utf-8-sig")
                st.success(f"✅ 已上传覆盖 {len(df_new)} 条记录")
        with col_cl:
            if st.button("🗑️ 清空历史", key="clear_zhizao"):
                zhizao_file = OUTPUT_PATH / selected_batch / "02_zhizao" / "zhizao_draft_content.csv"
                if zhizao_file.exists():
                    zhizao_file.unlink()
                st.success("已清空")

        # Article preview — all articles (editable)
        st.divider()
        st.subheader(f"📖 文章预览 & 编辑（{len(df_z)} 篇）")
        st.caption("可直接在下方编辑文章内容，修改后自动保存")
        if "title" in df_z.columns:
            zhizao_file = OUTPUT_PATH / selected_batch / "02_zhizao" / "zhizao_draft_content.csv"
            content_changed = False
            for idx, row in df_z.iterrows():
                title = str(row.get("title", f"文章 {idx+1}"))
                word_count = row.get("word_count", "?")
                with st.expander(f"📄 {title} ({word_count} 字)"):
                    if "ai_query" in df_z.columns:
                        st.caption(f"检索短语: {row.get('ai_query', '')}")
                    if "content_draft" in df_z.columns:
                        original = str(row.get("content_draft", ""))
                        edited_content = st.text_area(
                            "正文内容",
                            value=original,
                            height=300,
                            key=f"edit_article_{idx}",
                            label_visibility="collapsed",
                        )
                        if edited_content != original:
                            df_z.at[idx, "content_draft"] = edited_content
                            df_z.at[idx, "word_count"] = len(edited_content)
                            content_changed = True
            # Auto-save if any content changed
            if content_changed:
                df_z.to_csv(zhizao_file, index=False, encoding="utf-8-sig")
                st.success("✅ 修改已自动保存")

        # --- 文章确认环节 ---
        st.divider()
        st.subheader("✅ 文章确认")
        st.caption("勾选确认通过的文章，只有确认的文章才会进入智优优化")

        # Add confirmed column if not exists
        if "confirmed" not in df_z.columns:
            df_z["confirmed"] = True  # Default all confirmed

        confirm_cols = ["title", "word_count", "confirmed"] if "word_count" in df_z.columns else ["title", "confirmed"]
        confirm_cols = [c for c in confirm_cols if c in df_z.columns]
        if "confirmed" not in df_z.columns:
            df_z["confirmed"] = True
        confirm_cols.append("confirmed") if "confirmed" not in confirm_cols else None

        df_confirm = df_z[["title", "confirmed"]].copy() if "title" in df_z.columns else df_z[["confirmed"]].copy()
        if "title" in df_z.columns:
            df_confirm_edit = st.data_editor(
                df_z[["title", "confirmed"]].reset_index(drop=True),
                column_config={
                    "title": st.column_config.TextColumn("文章标题", disabled=True),
                    "confirmed": st.column_config.CheckboxColumn("确认通过"),
                },
                use_container_width=True,
                hide_index=True,
                key="zhizao_confirm_editor",
            )

            confirmed_count = df_confirm_edit["confirmed"].sum()
            total_count = len(df_confirm_edit)
            st.markdown(f"**已确认 {confirmed_count} / {total_count} 篇**")

            # Auto-save confirmation status
            zhizao_file = OUTPUT_PATH / selected_batch / "02_zhizao" / "zhizao_draft_content.csv"
            df_z["confirmed"] = df_confirm_edit["confirmed"].values
            df_z.to_csv(zhizao_file, index=False, encoding="utf-8-sig")
    else:
        st.info(f"批次 {selected_batch} 暂无智造输出，请先执行生成。")

    # CTA → 智优
    st.divider()
    if st.button("➡️ 进入智优 (Step 3)", type="primary", key="cta_zhizao_to_zhiyou"):
        jump_to("🔧 智优")
        st.rerun()

    # 📜 历史记录 + 清空
    with st.expander("📜 历史记录"):
        zhizao_dir = OUTPUT_PATH / selected_batch / "02_zhizao"
        col_h1, col_h2 = st.columns([4, 1])
        with col_h2:
            if st.button("🗑️ 清空全部", key="clear_zhizao_hist"):
                if zhizao_dir.exists():
                    for f in zhizao_dir.glob("*.csv"):
                        f.unlink()
                    st.success("已清空")
        if zhizao_dir.exists():
            files = sorted(zhizao_dir.glob("*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
            for f in files:
                mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                col_i, col_r, col_d = st.columns([3, 1, 1])
                with col_i:
                    st.caption(f"📄 {f.name} · {f.stat().st_size/1024:.1f}KB · 🕐 {mtime}")
                with col_r:
                    if st.button("♻️ 复用", key=f"reuse_zhizao_{f.name}"):
                        st.session_state["reuse_zhizao_file"] = str(f)
                        st.success(f"已选择复用: {f.name}")
                with col_d:
                    st.download_button("⬇️", f.read_bytes(), file_name=f.name, mime="text/csv", key=f"dl_zhizao_{f.name}")
        else:
            st.caption("暂无历史")


# ============================================================
# PAGE: 智优 (Step 3) — 一键自动完成
# ============================================================
elif page == "🔧 智优":
    st.title("🔧 智优 – Score · Rewrite · Compliance")
    render_pipeline_flow("zhiyou", selected_batch)
    st.caption("Step 3: 一键自动完成 评分 → 重写优化 → 合规审查")

    # --- Upload content directly (skip 智造) ---
    with st.expander("📤 上传内容（跳过智造直接优化）", expanded=False):
        st.caption("可选：上传已有文章 CSV，直接进行评分/重写/合规审查")
        upload_zhiyou = st.file_uploader("上传 CSV（需含 content_draft 列）", type=["csv", "xlsx"], key="zhiyou_direct_upload")
        if upload_zhiyou:
            try:
                if upload_zhiyou.name.endswith(".xlsx"):
                    df_up = pd.read_excel(upload_zhiyou, engine="openpyxl")
                else:
                    df_up = pd.read_csv(upload_zhiyou, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
                out_dir = OUTPUT_PATH / selected_batch / "02_zhizao"
                out_dir.mkdir(parents=True, exist_ok=True)
                df_up.to_csv(out_dir / "zhizao_draft_content.csv", index=False, encoding="utf-8-sig")
                st.success(f"✅ 已上传 {len(df_up)} 篇文章，可执行智优")
            except Exception as e:
                st.error(f"上传失败: {e}")

    # One-click execution
    st.subheader("▶️ 一键执行智优全流程")
    st.markdown("自动按顺序执行：**评分 → 重写 → 合规审查**")

    if st.button("🚀 一键智优全流程", type="primary", key="run_zhiyou_all"):
        try:
            from engine import run_zhiyou_score, run_zhiyou_execute, run_zhiyou_compliance
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("Step 3: 评分中...")
            progress_bar.progress(0.1)
            r1 = run_zhiyou_score(selected_batch)
            if not r1["success"]:
                st.error(f"评分失败: {r1['error']}")
            else:
                progress_bar.progress(0.4)
                status_text.text("Step 3.5: 重写中...")
                r2 = run_zhiyou_execute(selected_batch)
                if not r2["success"]:
                    st.error(f"重写失败: {r2['error']}")
                else:
                    progress_bar.progress(0.7)
                    status_text.text("Step 3.6: 合规审查中...")
                    r3 = run_zhiyou_compliance(selected_batch)
                    if not r3["success"]:
                        st.error(f"合规失败: {r3['error']}")
                    else:
                        progress_bar.progress(1.0)
                        status_text.text("")
                        st.success("✅ 智优全流程完成！")
        except ImportError:
            st.error("engine 模块未就绪")

    st.divider()

    # Results display (expanders)
    st.subheader("📊 结果查看")

    # Scorecard
    with st.expander("📊 评分卡 (Step 3)", expanded=False):
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
            st.info("暂无评分卡")

    # Rewrite
    with st.expander("✍️ 优化重写 (Step 3.5)", expanded=False):
        df_opt = load_optimized(selected_batch)
        if not df_opt.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("优化文章数", len(df_opt))
            with col2:
                if "word_count" in df_opt.columns:
                    st.metric("平均字数", f"{df_opt['word_count'].mean():.0f}")

            display_cols = [c for c in ["content_id", "optimized_title", "word_count",
                                        "table_count", "list_count", "link_count", "version"]
                           if c in df_opt.columns]
            if display_cols:
                st.dataframe(df_opt[display_cols], use_container_width=True, hide_index=True)
        else:
            st.info("暂无优化重写输出")

    # Compliance
    with st.expander("⚖️ 合规审查 (Step 3.6)", expanded=False):
        df_comp = load_compliance(selected_batch)
        if not df_comp.empty:
            col1, col2, col3 = st.columns(3)
            if "compliance_status" in df_comp.columns:
                with col1:
                    st.metric("PASS", int((df_comp["compliance_status"] == "PASS").sum()))
                with col2:
                    st.metric("FIXED", int((df_comp["compliance_status"] == "FIXED").sum()))
                with col3:
                    st.metric("BLOCKED", int((df_comp["compliance_status"] == "BLOCKED").sum()))
            st.dataframe(df_comp, use_container_width=True, hide_index=True)
        else:
            st.info("暂无合规审查结果")

    # --- 文章预览 & 编辑 + 确认 ---
    st.divider()
    df_opt = load_optimized(selected_batch)
    if not df_opt.empty:
        st.subheader(f"📖 优化后文章预览 & 编辑（{len(df_opt)} 篇）")
        st.caption("可直接编辑优化后的文章内容，修改自动保存")

        opt_file = OUTPUT_PATH / selected_batch / "03_zhiyou" / "zhiyou_optimized_content.csv"
        content_col = "optimized_content" if "optimized_content" in df_opt.columns else "content_draft"
        title_col = "optimized_title" if "optimized_title" in df_opt.columns else "title"

        content_changed = False
        for idx, row in df_opt.iterrows():
            title = str(row.get(title_col, f"文章 {idx+1}"))
            word_count = row.get("word_count", "?")
            with st.expander(f"📄 {title} ({word_count} 字)"):
                if "ai_query" in df_opt.columns:
                    st.caption(f"检索短语: {row.get('ai_query', '')}")
                if content_col in df_opt.columns:
                    original = str(row.get(content_col, ""))
                    edited = st.text_area("内容", value=original, height=300,
                                          key=f"zhiyou_edit_{idx}", label_visibility="collapsed")
                    if edited != original:
                        df_opt.at[idx, content_col] = edited
                        df_opt.at[idx, "word_count"] = len(edited)
                        content_changed = True

        if content_changed:
            df_opt.to_csv(opt_file, index=False, encoding="utf-8-sig")
            st.success("✅ 修改已自动保存")

        # 确认环节
        st.divider()
        st.subheader("✅ 文章确认")
        st.caption("勾选确认通过的文章，确认后进入智布发布")

        if "confirmed" not in df_opt.columns:
            df_opt["confirmed"] = True

        if title_col in df_opt.columns:
            df_confirm = st.data_editor(
                df_opt[[title_col, "confirmed"]].reset_index(drop=True),
                column_config={
                    title_col: st.column_config.TextColumn("文章标题", disabled=True),
                    "confirmed": st.column_config.CheckboxColumn("确认通过"),
                },
                use_container_width=True, hide_index=True,
                key="zhiyou_confirm_editor",
            )
            confirmed_count = df_confirm["confirmed"].sum()
            st.markdown(f"**已确认 {confirmed_count} / {len(df_confirm)} 篇**")

            # Auto-save confirmation
            df_opt["confirmed"] = df_confirm["confirmed"].values
            df_opt.to_csv(opt_file, index=False, encoding="utf-8-sig")

    # CTA → 智布
    st.divider()
    if st.button("➡️ 进入智布 (Step 4)", type="primary", key="cta_zhiyou_to_zhibu"):
        jump_to("📦 智布")
        st.rerun()

    # 📜 历史记录 + 清空
    with st.expander("📜 历史记录"):
        zhiyou_dir = OUTPUT_PATH / selected_batch / "03_zhiyou"
        col_h1, col_h2 = st.columns([4, 1])
        with col_h2:
            if st.button("🗑️ 清空全部", key="clear_zhiyou_hist"):
                if zhiyou_dir.exists():
                    for f in zhiyou_dir.glob("*.csv"):
                        f.unlink()
                    st.success("已清空")
        if zhiyou_dir.exists():
            files = sorted(zhiyou_dir.glob("*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
            for f in files:
                mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                col_i, col_r, col_d = st.columns([3, 1, 1])
                with col_i:
                    st.caption(f"📄 {f.name} · {f.stat().st_size/1024:.1f}KB · 🕐 {mtime}")
                with col_r:
                    if st.button("♻️ 复用", key=f"reuse_zhiyou_{f.name}"):
                        st.session_state["reuse_zhiyou_file"] = str(f)
                        st.success(f"已选择复用: {f.name}")
                with col_d:
                    st.download_button("⬇️", f.read_bytes(), file_name=f.name, mime="text/csv", key=f"dl_zhiyou_{f.name}")
        else:
            st.caption("暂无历史")


# ============================================================
# PAGE: 智布 (Step 4)
# ============================================================
elif page == "📦 智布":
    st.title("📦 智布 – JSON / Word Formatting")
    render_pipeline_flow("zhibu", selected_batch)
    st.caption("Step 4: 将优化内容转换为结构化 JSON 和 Word 文档")

    # --- Upload content directly (skip 智优) ---
    with st.expander("📤 上传内容（跳过智优直接发布格式化）", expanded=False):
        st.caption("可选：上传已优化完成的文章 CSV，直接生成 JSON/Word")
        upload_zhibu = st.file_uploader("上传 CSV（需含 optimized_content 列）", type=["csv", "xlsx"], key="zhibu_direct_upload")
        if upload_zhibu:
            try:
                if upload_zhibu.name.endswith(".xlsx"):
                    df_up = pd.read_excel(upload_zhibu, engine="openpyxl")
                else:
                    df_up = pd.read_csv(upload_zhibu, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
                out_dir = OUTPUT_PATH / selected_batch / "03_zhiyou"
                out_dir.mkdir(parents=True, exist_ok=True)
                df_up.to_csv(out_dir / "zhiyou_optimized_content.csv", index=False, encoding="utf-8-sig")
                st.success(f"✅ 已上传 {len(df_up)} 篇，可执行智布")
            except Exception as e:
                st.error(f"上传失败: {e}")

    # Execution
    st.subheader("▶️ 生成发布格式")
    col_exec1, col_exec2 = st.columns(2)
    with col_exec1:
        if st.button("🚀 生成 JSON", type="primary", key="run_zhibu"):
            try:
                from engine import run_zhibu
                with st.spinner("正在生成 JSON..."):
                    result = run_zhibu(selected_batch)
                if result["success"]:
                    st.success(f"✅ 智布完成！{result['items_count']} 条目")
                else:
                    st.error(f"❌ 失败: {result['error']}")
            except ImportError:
                st.error("engine 模块未就绪")
    with col_exec2:
        if st.button("📄 生成 Word 文档", key="run_word"):
            try:
                from engine import generate_word_docs
                with st.spinner("正在生成 Word 文档..."):
                    result = generate_word_docs(selected_batch)
                if result["success"]:
                    st.success(f"✅ Word 生成完成！{result.get('doc_count', 0)} 篇")
                else:
                    st.error(f"❌ 失败: {result['error']}")
            except ImportError:
                st.error("engine.generate_word_docs 未实现")

    st.divider()

    # Output display
    data = load_zhibu(selected_batch)
    if data:
        col_title, col_clear = st.columns([4, 1])
        with col_title:
            st.subheader("📤 输出概览")
        with col_clear:
            if st.button("🗑️ 清空预览", key="clear_zhibu_preview"):
                zhibu_dir = OUTPUT_PATH / selected_batch / "04_zhibu"
                if zhibu_dir.exists():
                    # Move current files to archive (rename with timestamp)
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    archive_dir = zhibu_dir / "archive"
                    archive_dir.mkdir(exist_ok=True)
                    for f in list(zhibu_dir.glob("*.json")):
                        f.rename(archive_dir / f"{f.stem}_{ts}{f.suffix}")
                st.success("已清空预览（历史已归档）")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("总条目", data.get("total_items", 0))
        with col2:
            st.metric("批次", data.get("batch_id", "N/A"))
        with col3:
            kws = data.get("source_keywords", [])
            st.metric("源关键词", len(kws) if isinstance(kws, list) else 0)

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
                    "selected": True,
                })
            df_items = pd.DataFrame(rows)
            edited_items = st.data_editor(
                df_items,
                column_config={
                    "content_id": st.column_config.TextColumn("ID", disabled=True),
                    "title": st.column_config.TextColumn("标题", disabled=True),
                    "word_count": st.column_config.NumberColumn("字数", disabled=True),
                    "overall_score": st.column_config.NumberColumn("评分", disabled=True),
                    "compliance": st.column_config.TextColumn("合规", disabled=True),
                    "selected": st.column_config.CheckboxColumn("选中"),
                },
                use_container_width=True, hide_index=True,
                key="zhibu_select_editor",
            )
            selected_count = edited_items["selected"].sum()
            st.caption(f"已选中 {selected_count} / {len(edited_items)} 篇")

        # JSON preview
        st.divider()
        st.subheader("🔍 JSON 预览")
        if items:
            sel_idx = st.selectbox(
                "选择条目", range(len(items)),
                format_func=lambda i: items[i].get("meta", {}).get("title", f"Item {i}"),
                key="zhibu_preview_select"
            )
            st.json(items[sel_idx])
    else:
        st.info(f"批次 {selected_batch} 暂无智布输出")

    # Word docs display — only show 智优 Final version
    word_dir_opt = OUTPUT_PATH / selected_batch / "03_zhiyou_word"
    if word_dir_opt.exists():
        docs = list(word_dir_opt.glob("*.docx"))
        if docs:
            st.divider()
            st.subheader("📄 Final Word 文档")
            for doc in docs:
                st.download_button(
                    f"📄 {doc.name}", doc.read_bytes(),
                    file_name=doc.name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"dl_word_{doc.name}"
                )

    # CTA → 智析
    st.divider()
    if st.button("➡️ 查看智析 (Step 6)", type="primary", key="cta_zhibu_to_zhixi"):
        jump_to("📈 智析")
        st.rerun()

    # 📜 历史记录（不清空，带复用）
    with st.expander("📜 历史记录"):
        zhibu_dir = OUTPUT_PATH / selected_batch / "04_zhibu"
        all_hist_files = []
        if zhibu_dir.exists():
            # Current files
            all_hist_files.extend([f for f in zhibu_dir.iterdir() if f.is_file()])
            # Archived files
            archive_dir = zhibu_dir / "archive"
            if archive_dir.exists():
                all_hist_files.extend([f for f in archive_dir.iterdir() if f.is_file()])
        if all_hist_files:
            all_hist_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            for f in all_hist_files:
                mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                col_i, col_r, col_d = st.columns([3, 1, 1])
                with col_i:
                    st.caption(f"📄 {f.name} · {f.stat().st_size/1024:.1f}KB · 🕐 {mtime}")
                with col_r:
                    if st.button("♻️ 复用", key=f"reuse_zhibu_{f.name}"):
                        st.session_state["reuse_zhibu_file"] = str(f)
                        st.success(f"已选择复用: {f.name}")
                with col_d:
                    mime = "application/json" if f.suffix == ".json" else "text/csv"
                    st.download_button("⬇️", f.read_bytes(), file_name=f.name, mime=mime, key=f"dl_zhibu_{f.name}")
        else:
            st.caption("暂无历史")


# ============================================================
# PAGE: 智析 (Step 6)
# ============================================================
elif page == "📈 智析":
    st.title("📈 智析 – Performance Report")
    render_pipeline_flow("zhixi", selected_batch)
    st.caption("Step 6: GEO + WW Direct Reg Start 趋势分析")

    # --- Upload metrics data directly ---
    with st.expander("📤 上传数据（手动导入 metrics 数据）", expanded=False):
        st.caption("可选：上传 weekly/monthly metrics CSV，用于自定义分析展示")
        upload_zhixi = st.file_uploader("上传 Metrics CSV", type=["csv", "xlsx"], key="zhixi_direct_upload")
        if upload_zhixi:
            try:
                if upload_zhixi.name.endswith(".xlsx"):
                    df_up = pd.read_excel(upload_zhixi, engine="openpyxl")
                else:
                    df_up = pd.read_csv(upload_zhixi, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
                metrics_dir = OUTPUT_PATH / "metrics"
                metrics_dir.mkdir(parents=True, exist_ok=True)
                df_up.to_csv(metrics_dir / "uploaded_metrics.csv", index=False, encoding="utf-8-sig")
                st.success(f"✅ 已上传 {len(df_up)} 行数据")
            except Exception as e:
                st.error(f"上传失败: {e}")

    # Weekly Trend
    st.subheader("📊 Weekly 趋势")
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

    st.divider()

    # YTD
    st.subheader("📋 YTD 对比")
    df_ytd = get_ytd_metrics()
    df_ytd["增量"] = df_ytd["YTD_Actual"] - df_ytd["YTD_PY"]

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

    # vs Benchmark
    st.subheader("vs SSR 大盘")
    bench = pd.DataFrame({
        "维度": ["GEO + WW Direct", "Net (含 CN Direct+SEO)", "SSR Total 大盘"],
        "YTD YoY": ["+55%", "-10%", "-23%"],
        "vs 大盘": ["+78 ppts", "+13 ppts", "Benchmark"],
    })
    st.dataframe(bench, use_container_width=True, hide_index=True)

    st.divider()

    # Attribution
    st.subheader("🎯 WK20 归因分析")
    st.markdown("""
**Output 变化：**
- WK20 GEO + WW Direct = **2,047**，WoW **+31%**
- CN GEO 连续 4 周增长：32→33→33→41
- WW Direct EST 全面反弹：NA +29%, EU +42%, JP +67%

**归因判断：**
| 渠道 | 判断 | 原因 |
|---|---|---|
| CN GEO | 🟢 持续增长 | AI search 带 referrer 流量稳步提升 |
| WW Direct EST | 🟢 全面反弹 | 前几周发布内容被 AI 引擎收录（滞后效应）|
| JP Direct | 🟢 +67% WoW | 日本 AI search 渗透加速 |

**🚀 Opportunities:**
- 增加 EU/JP 检索短语覆盖（GEO 绝对值低）
- 排查 AE Direct 下降原因（YoY -61%）
- 建立 input 活动周度追踪，完善归因链路
    """)

    # 📜 历史记录 (no reuse)
    with st.expander("📜 历史记录"):
        metrics_dir = OUTPUT_PATH / "metrics"
        col_h1, col_h2 = st.columns([4, 1])
        with col_h2:
            if st.button("🗑️ 清空", key="clear_zhixi_hist"):
                if metrics_dir.exists():
                    for f in metrics_dir.glob("*.csv"):
                        f.unlink()
                    st.success("已清空")
        if metrics_dir.exists():
            files = sorted(metrics_dir.glob("*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
            for f in files:
                mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                col_i, col_d = st.columns([4, 1])
                with col_i:
                    st.caption(f"📄 {f.name} · {f.stat().st_size/1024:.1f}KB · 🕐 {mtime}")
                with col_d:
                    st.download_button("⬇️", f.read_bytes(), file_name=f.name, mime="text/csv", key=f"dl_zhixi_{f.name}")
        else:
            st.caption("暂无历史")


# ============================================================
# PAGE: 智中枢
# ============================================================
elif page == "🎯 智中枢":
    st.title("🎯 智中枢 – Decision Engine")
    render_pipeline_flow("zhongshu", selected_batch)
    st.caption("基于智析数据 + 7 条决策规则，生成周度行动计划")

    # Decision Rules
    st.subheader("📜 7 条决策规则")
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

    st.divider()

    # Weekly Plan
    st.subheader(f"📋 Smart Suite Weekly Plan - {week}")
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

    st.divider()
    st.subheader("🚀 全流程快捷指令")
    pipeline_cmds = [
        ("1. 智库", f"执行智库 {selected_batch}，market={market}，keyword_limit={kw_limit}"),
        ("2. 智造", f"执行智造 {selected_batch}，生成内容"),
        ("3. 智优", f"一键智优 {selected_batch}"),
        ("4. 智布", f"执行智布 {selected_batch}，生成JSON"),
        ("6. 智析", f"生成智析报告 {week}"),
    ]
    for label, cmd in pipeline_cmds:
        st.text(f"📌 {label}")
        st.code(cmd, language=None)


# ============================================================
# PAGE: 批次对比
# ============================================================
elif page == "📊 批次对比":
    st.title("📊 批次对比")
    st.caption("对比不同批次的产出效果")

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        batch_a = st.selectbox("批次 A", batches, index=0, key="compare_a")
    with col_b2:
        batch_b = st.selectbox("批次 B", batches, index=min(1, len(batches) - 1), key="compare_b")

    st.divider()

    # Compare zhiku counts
    df_a = load_zhiku(batch_a)
    df_b = load_zhiku(batch_b)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"📚 {batch_a}")
        st.metric("智库短语数", len(df_a))
        df_za = load_zhizao(batch_a)
        st.metric("智造文章数", len(df_za))
        df_sa = load_scorecard(batch_a)
        if not df_sa.empty and "overall_score" in df_sa.columns:
            st.metric("平均评分", f"{df_sa['overall_score'].mean():.2f}")
        else:
            st.metric("平均评分", "N/A")

    with col2:
        st.subheader(f"📚 {batch_b}")
        st.metric("智库短语数", len(df_b))
        df_zb = load_zhizao(batch_b)
        st.metric("智造文章数", len(df_zb))
        df_sb = load_scorecard(batch_b)
        if not df_sb.empty and "overall_score" in df_sb.columns:
            st.metric("平均评分", f"{df_sb['overall_score'].mean():.2f}")
        else:
            st.metric("平均评分", "N/A")


# ============================================================
# PAGE: 发布追踪
# ============================================================
elif page == "📌 发布追踪":
    st.title("📌 发布追踪")
    st.caption("追踪已发布内容的引用和效果")

    # Look for published tracking data
    tracking_file = OUTPUT_PATH / "publish_tracking.csv"
    if tracking_file.exists():
        df_track = load_csv_safe(tracking_file)
        if not df_track.empty:
            st.dataframe(df_track, use_container_width=True, hide_index=True)
        else:
            st.info("追踪数据为空")
    else:
        st.info("暂无发布追踪数据。发布后系统将自动记录。")

    st.divider()
    st.subheader("手动添加发布记录")
    with st.form("add_publish_record"):
        pub_title = st.text_input("文章标题")
        pub_url = st.text_input("发布 URL")
        pub_date = st.date_input("发布日期")
        pub_platform = st.selectbox("平台", ["官网", "知乎", "微信公众号", "其他"])
        submitted = st.form_submit_button("添加记录")
        if submitted and pub_title:
            new_row = pd.DataFrame([{
                "title": pub_title,
                "url": pub_url,
                "publish_date": str(pub_date),
                "platform": pub_platform,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }])
            if tracking_file.exists():
                df_existing = load_csv_safe(tracking_file)
                df_combined = pd.concat([df_existing, new_row], ignore_index=True)
            else:
                tracking_file.parent.mkdir(parents=True, exist_ok=True)
                df_combined = new_row
            df_combined.to_csv(tracking_file, index=False, encoding="utf-8-sig")
            st.success(f"✅ 已添加: {pub_title}")


# ============================================================
# PAGE: 需求中心 (Intake + 智测)
# ============================================================
elif page == "📝 需求中心":
    st.title("📝 需求中心")
    st.caption("Intake + 智测合并 — 产品需求提交、用户旅程调研、需求追踪")

    tab_geo, tab_zhice, tab_tracking = st.tabs([
        "🚀 产品 GEO 需求",
        "🔬 用户旅程调研 (智测)",
        "📋 需求进展追踪",
    ])

    with tab_geo:
        st.subheader("🚀 产品 GEO 需求")
        st.markdown("提交产品名 → 裂变 → 生成 → 发布")

        with st.form("geo_intake_form"):
            product_name = st.text_input("产品名称", placeholder="例如：亚马逊FBA物流服务")
            product_desc = st.text_area("产品简述", placeholder="简要描述产品特点和目标受众")
            target_market_intake = st.multiselect("目标市场", ["CN", "NA", "EU", "JP", "AU"])
            priority_intake = st.select_slider("优先级", options=["低", "中", "高", "紧急"], value="中")
            submitted_geo = st.form_submit_button("提交需求", type="primary")

            if submitted_geo and product_name:
                intake_file = OUTPUT_PATH / "intake_requests.csv"
                new_req = pd.DataFrame([{
                    "product_name": product_name,
                    "description": product_desc,
                    "target_market": ",".join(target_market_intake),
                    "priority": priority_intake,
                    "status": "待处理",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }])
                if intake_file.exists():
                    df_existing = load_csv_safe(intake_file)
                    df_combined = pd.concat([df_existing, new_req], ignore_index=True)
                else:
                    intake_file.parent.mkdir(parents=True, exist_ok=True)
                    df_combined = new_req
                df_combined.to_csv(intake_file, index=False, encoding="utf-8-sig")
                st.success(f"✅ 需求已提交: {product_name}")

    with tab_zhice:
        st.subheader("🔬 用户旅程调研 (智测)")
        st.markdown("设定 persona → 模拟旅程 → 输出 gap")

        persona_name = st.text_input("用户画像名称", placeholder="例如：深圳3C配件卖家")
        persona_goal = st.text_area("用户目标", placeholder="想开亚马逊美国站，寻找入门路径")
        platforms = st.multiselect(
            "AI 检索平台",
            ["chatgpt", "perplexity", "gemini", "deepseek", "doubao", "kimi", "yuanbao", "qianwen"],
            default=["chatgpt", "perplexity", "deepseek"],
        )
        rounds_count = st.number_input("模拟轮次", 3, 10, 5, key="zhice_rounds")

        if st.button("🚀 开始模拟旅程", type="primary", key="run_zhice"):
            try:
                from zhice_engine import run_zhice_journey
                with st.spinner("正在模拟用户旅程..."):
                    result = run_zhice_journey(
                        persona_name=persona_name,
                        persona_goal=persona_goal,
                        platforms=platforms,
                        rounds=rounds_count,
                    )
                if result.get("success"):
                    st.success("✅ 旅程模拟完成！")
                    st.json(result.get("summary", {}))
                else:
                    st.error(f"❌ 失败: {result.get('error', '')}")
            except ImportError:
                st.error("zhice_engine 模块未就绪")

    with tab_tracking:
        st.subheader("📋 需求进展追踪")
        intake_file = OUTPUT_PATH / "intake_requests.csv"
        if intake_file.exists():
            df_intake = load_csv_safe(intake_file)
            if not df_intake.empty:
                st.dataframe(df_intake, use_container_width=True, hide_index=True)
            else:
                st.info("暂无需求记录")
        else:
            st.info("暂无需求记录，请在「产品 GEO 需求」标签页提交。")


# ============================================================
# PAGE: 引用分析
# ============================================================
elif page == "🔍 引用分析":
    st.title("🔍 引用分析")
    st.caption("分析 AI 搜索引擎对内容的引用情况")

    st.subheader("AI 引擎引用监控")
    st.markdown("""
    追踪我们的内容在以下 AI 搜索平台的被引用情况：
    - **CN**: DeepSeek / 豆包 / Kimi / 元宝 / 通义千问
    - **WW**: ChatGPT / Perplexity / Gemini
    """)

    # Check for citation data
    citation_file = OUTPUT_PATH / "citation_tracking.csv"
    if citation_file.exists():
        df_cite = load_csv_safe(citation_file)
        if not df_cite.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总引用次数", len(df_cite))
            with col2:
                if "platform" in df_cite.columns:
                    st.metric("引用平台数", df_cite["platform"].nunique())
            with col3:
                if "content_id" in df_cite.columns:
                    st.metric("被引用内容数", df_cite["content_id"].nunique())
            st.dataframe(df_cite, use_container_width=True, hide_index=True)
        else:
            st.info("暂无引用数据")
    else:
        st.info("暂无引用追踪数据。运行智测后将自动生成引用分析。")


# ============================================================
# PAGE: Settings
# ============================================================
elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    st.caption("系统配置")

    st.subheader("🔑 API 配置")
    st.markdown("""
    - **AWS Bedrock**: 使用本地 AWS credentials（SSO / env vars）
    - **Model**: Claude 3.5 Sonnet (`anthropic.claude-sonnet-4-20250514`)
    - **Region**: us-east-1
    """)

    st.divider()
    st.subheader("📂 路径配置")
    st.text(f"项目根目录: {BASE_PATH}")
    st.text(f"输出目录: {OUTPUT_PATH}")
    st.text(f"输入目录: {INPUT_PATH}")

    st.divider()
    st.subheader("📊 批次管理")
    new_batch = st.text_input("创建新批次", placeholder="batch_004", key="new_batch_input")
    if st.button("创建批次", key="create_batch"):
        if new_batch:
            new_path = OUTPUT_PATH / new_batch
            new_path.mkdir(parents=True, exist_ok=True)
            (new_path / "01_zhiku").mkdir(exist_ok=True)
            (new_path / "02_zhizao").mkdir(exist_ok=True)
            (new_path / "03_zhiyou").mkdir(exist_ok=True)
            (new_path / "04_zhibu").mkdir(exist_ok=True)
            st.success(f"✅ 已创建批次: {new_batch}")

    st.divider()
    st.subheader("🏷️ 类别体系 (35类)")
    for i, cat in enumerate(CATEGORIES_35, 1):
        st.text(f"{i:2d}. {cat}")


# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption(
    f"Smart Suite Phase I · 智系列控制台 · "
    f"{datetime.now().strftime('%Y-%m-%d %H:%M')} · "
    f"Batches: {len(batches)}"
)
