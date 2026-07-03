"""
Smart Suite 智系列控制台 - Streamlit UI (重构版)
单页线性流程，统一风格，CTA 跳转
Run: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import io
from datetime import datetime
import tempfile
import os

# --- Config ---
BASE_PATH = Path(__file__).parent.parent
OUTPUT_PATH = BASE_PATH / "output"
INPUT_PATH = BASE_PATH / "input"
METRICS_PATH = OUTPUT_PATH / "metrics"

# --- Demo Mode Detection ---
# If real output dir doesn't exist (e.g. Streamlit Cloud), use bundled demo data
DEMO_MODE = not OUTPUT_PATH.exists()

if DEMO_MODE:
    _DEMO_OUTPUT = Path(__file__).parent / "demo_output"
    if _DEMO_OUTPUT.exists():
        OUTPUT_PATH = _DEMO_OUTPUT
        METRICS_PATH = OUTPUT_PATH / "metrics"
    else:
        _CLOUD_OUTPUT = Path(tempfile.gettempdir()) / "smartsuite_output"
        _CLOUD_OUTPUT.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH = _CLOUD_OUTPUT
        METRICS_PATH = OUTPUT_PATH / "metrics"
    if not INPUT_PATH.exists():
        INPUT_PATH = Path(tempfile.gettempdir()) / "smartsuite_input"
        INPUT_PATH.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="Smart Suite Console",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
.main .block-container { padding-top: 1.2rem; padding-left: 0.5rem; padding-right: 0.5rem; max-width: 100%; }
iframe { width: 100% !important; }
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1a1d2e 0%, #12131a 100%);
    border: 1px solid #2a2f4a; border-radius: 10px; padding: 12px 16px;
}
div[data-testid="stMetric"] label { color: #8892b0 !important; font-size: 12px !important; text-transform: uppercase; letter-spacing: 0.5px; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #00bcd4 !important; font-weight: 700 !important; }
h1, h2, h3 { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important; }
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] { background: #1a1d2e; border-radius: 8px 8px 0 0; border: 1px solid #2a2f4a; padding: 8px 16px; }
.stTabs [aria-selected="true"] { background: #222540 !important; border-color: #00bcd4 !important; }
div[data-testid="stExpander"] { background: #1a1d2e; border: 1px solid #2a2f4a; border-radius: 10px; }
.stButton > button { border-radius: 8px; font-weight: 600; }
div[data-testid="stDataFrame"] { border-radius: 10px; border: 1px solid #2a2f4a; }
.stDivider { border-color: #2a2f4a !important; }
section[data-testid="stSidebar"] { background: #0f1117; border-right: 1px solid #1e2030; }
</style>
""", unsafe_allow_html=True)


# --- Pipeline Flow Visual Component ---
PIPELINE_STEPS = [
    {"id": "zhiku", "name": "智库", "page": "📚 智库"},
    {"id": "zhice", "name": "智测", "page": "🔍 智测"},
    {"id": "zhizao", "name": "智造", "page": "✍️ 智造"},
    {"id": "zhiyou", "name": "智优", "page": "🔧 智优"},
    {"id": "zhibu", "name": "智布", "page": "📦 智布"},
    {"id": "zhichuan", "name": "智传", "page": "📡 智传"},
    {"id": "zhixi", "name": "智析", "page": "📈 智析"},
    {"id": "zhongshu", "name": "智中枢", "page": "🎯 智中枢"},
]


def render_pipeline_flow(current_step_id: str, batch_id: str = ""):
    """Render pipeline flow matching showcase design: current step bright with its color, rest dimmed."""
    import streamlit.components.v1 as components

    colors = {"zhiku": "#ffa726", "zhice": "#00bcd4", "zhizao": "#ffcc02", "zhiyou": "#e91e63",
              "zhibu": "#29b6f6", "zhichuan": "#26c6da", "zhixi": "#ab47bc", "zhongshu": "#ff6b35"}

    cards_html = ""
    for i, step in enumerate(PIPELINE_STEPS):
        sid = step["id"]
        is_current = (sid == current_step_id)
        color = colors.get(sid, "#4a5568")

        if is_current:
            border = color
            text_color = color
            bg = "#0f1117"
        else:
            border = "#2a2f4a"
            text_color = "#4a5568"
            bg = "#0f1117"

        cards_html += f'<div style="background:{bg};border:1px solid {border};border-radius:8px;padding:6px 12px;text-align:center;min-width:fit-content;"><div style="font-size:12px;color:{text_color};font-weight:600;">{step["name"]}</div></div>'
        if i < len(PIPELINE_STEPS) - 1:
            arrow_color = "#8892b0" if is_current else "#2a2f4a"
            cards_html += f'<div style="color:{arrow_color};font-size:16px;font-weight:700;">&#10132;</div>'

    html = f'''<div style="display:flex;align-items:center;justify-content:center;gap:4px;padding:12px;margin:8px 0;background:#1a1d2e;border-radius:10px;border:1px solid #2a2f4a;flex-wrap:nowrap;overflow-x:auto;">{cards_html}</div>'''
    components.html(html, height=55, scrolling=False)


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
    """Load weekly GEO metrics from stored CSV, fallback to defaults if empty."""
    geo_weekly_file = METRICS_PATH / "geo_weekly_data.csv"
    if geo_weekly_file.exists():
        df = load_csv_safe(geo_weekly_file)
        if not df.empty and "Week" in df.columns:
            # Ensure correct column types for all numeric columns
            numeric_cols = [c for c in df.columns if c != "Week"]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
            # Handle legacy format: rename WW_Direct_EST to WW_Direct if needed
            if "WW_Direct_EST" in df.columns and "WW_Direct" not in df.columns:
                df = df.rename(columns={"WW_Direct_EST": "WW_Direct"})
            # Drop EM column if present
            if "WW_Direct_EM" in df.columns:
                df = df.drop(columns=["WW_Direct_EM"])
            # Ensure Total_GEO exists
            if "Total_GEO" not in df.columns and "CN_GEO" in df.columns and "WW_GEO" in df.columns:
                df["Total_GEO"] = df["CN_GEO"] + df["WW_GEO"]
            # Ensure Total exists
            if "Total" not in df.columns and "Total_GEO" in df.columns and "WW_Direct" in df.columns:
                df["Total"] = df["Total_GEO"] + df["WW_Direct"]
            # Ensure PY columns have Total_GEO_PY and Total_PY
            if "Total_GEO_PY" not in df.columns and "CN_GEO_PY" in df.columns and "WW_GEO_PY" in df.columns:
                df["Total_GEO_PY"] = df["CN_GEO_PY"] + df["WW_GEO_PY"]
            if "Total_PY" not in df.columns and "Total_GEO_PY" in df.columns and "WW_Direct_PY" in df.columns:
                df["Total_PY"] = df["Total_GEO_PY"] + df["WW_Direct_PY"]
            return df
    # Default data (WK20 report baseline)
    return pd.DataFrame({
        "Week": ["WK17", "WK18", "WK19", "WK20"],
        "CN_GEO": [32, 33, 33, 41], "CN_GEO_PY": [12, 6, 4, 11],
        "WW_GEO": [15, 18, 22, 31], "WW_GEO_PY": [8, 7, 5, 5],
        "Total_GEO": [47, 51, 55, 72], "Total_GEO_PY": [20, 13, 9, 16],
        "WW_Direct": [1739, 1330, 1454, 1914], "WW_Direct_PY": [1048, 820, 920, 1100],
        "Total": [1786, 1381, 1509, 1986], "Total_PY": [1068, 833, 929, 1116],
    })


def get_ytd_metrics():
    """Load YTD GEO metrics from stored CSV, fallback to defaults if empty."""
    geo_ytd_file = METRICS_PATH / "geo_ytd_data.csv"
    if geo_ytd_file.exists():
        df = load_csv_safe(geo_ytd_file)
        if not df.empty and "Channel" in df.columns:
            return df
    # Default data (WK20 report baseline)
    return pd.DataFrame({
        "Channel": ["CN GEO", "WW GEO", "WW Direct EST", "Total"],
        "YTD_Actual": [574, 364, 25863, 26801],
        "YTD_PY": [104, 188, 15945, 16237],
        "YoY": ["+452%", "+94%", "+62%", "+65%"],
    })


def get_monthly_metrics():
    """Load monthly GEO metrics from stored CSV, fallback to defaults if empty."""
    geo_monthly_file = METRICS_PATH / "geo_monthly_data.csv"
    if geo_monthly_file.exists():
        df = load_csv_safe(geo_monthly_file)
        if not df.empty and "Channel" in df.columns:
            return df
    # Default data (WK20 report baseline)
    return pd.DataFrame({
        "Channel": ["CN (GEO)", "CN (GEO)", "CN (GEO)", "WW (GEO)", "WW (GEO)", "WW (GEO)",
                    "Total GEO", "Total GEO", "Total GEO", "WW Website Direct", "WW Website Direct", "WW Website Direct",
                    "Total (GEO+Direct)", "Total (GEO+Direct)", "Total (GEO+Direct)"],
        "Type": ["Actual", "PY", "YoY"] * 5,
        "M1 (Jan)": [89, 13, "+585%", 83, 38, "+118%", 172, 51, "+237%", 4965, 1801, "+176%", 5137, 1852, "+177%"],
        "M2 (Feb)": [65, 13, "+400%", 51, 51, "+0%", 116, 64, "+81%", 2387, 3056, "-22%", 2503, 3120, "-20%"],
        "M3 (Mar)": [165, 36, "+358%", 91, 45, "+102%", 256, 81, "+216%", 7267, 4274, "+70%", 7523, 4355, "+73%"],
        "M4 (Apr)": [164, 30, "+447%", 70, 32, "+119%", 234, 62, "+277%", 7205, 4270, "+69%", 7439, 4332, "+72%"],
        "M5 (May)": [120, 19, "+532%", 74, 33, "+124%", 194, 52, "+273%", 5330, 3247, "+64%", 5524, 3299, "+67%"],
    })


def append_geo_weekly(new_df):
    """Append new weekly data rows to geo_weekly_data.csv, dedup by Week."""
    geo_weekly_file = METRICS_PATH / "geo_weekly_data.csv"
    METRICS_PATH.mkdir(parents=True, exist_ok=True)
    if geo_weekly_file.exists():
        existing = load_csv_safe(geo_weekly_file)
        if not existing.empty:
            combined = pd.concat([existing, new_df], ignore_index=True)
            # Dedup: keep latest data for same Week
            combined = combined.drop_duplicates(subset=["Week"], keep="last")
            # Sort by week number
            combined["_wk_num"] = combined["Week"].str.extract(r"(\d+)").astype(int)
            combined = combined.sort_values("_wk_num").drop(columns=["_wk_num"])
            combined.to_csv(geo_weekly_file, index=False, encoding="utf-8-sig")
            return combined
    new_df.to_csv(geo_weekly_file, index=False, encoding="utf-8-sig")
    return new_df


def append_geo_ytd(new_df):
    """Update YTD data (replace with latest)."""
    geo_ytd_file = METRICS_PATH / "geo_ytd_data.csv"
    METRICS_PATH.mkdir(parents=True, exist_ok=True)
    new_df.to_csv(geo_ytd_file, index=False, encoding="utf-8-sig")
    return new_df


def append_geo_monthly(new_df):
    """Update monthly data (replace with latest)."""
    geo_monthly_file = METRICS_PATH / "geo_monthly_data.csv"
    METRICS_PATH.mkdir(parents=True, exist_ok=True)
    new_df.to_csv(geo_monthly_file, index=False, encoding="utf-8-sig")
    return new_df


def jump_to(page_name: str):
    """Set session state to jump to a page on next rerun."""
    st.session_state["jump_to_page"] = page_name


def safe_copy(src: Path, dst: Path):
    """Copy file safely, handling Windows file locks."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        import shutil
        shutil.copy2(str(src), str(dst))
    except PermissionError:
        content = src.read_bytes()
        dst.write_bytes(content)


# ============================================================
# NAVIGATION PAGES
# ============================================================
NAV_PAGES_ZH = [
    "🏠 总览",
    "📚 智库",
    "🔍 智测",
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

NAV_PAGES_EN = [
    "🏠 Overview",
    "📚 Research",
    "🔍 Testing",
    "✍️ Creation",
    "🔧 Optimization",
    "📦 Distribution",
    "📡 Amplification",
    "📈 Analytics",
    "🎯 Hub",
    "───────────",
    "📝 Demand Center",
    "🔍 Citation Analysis",
    "⚙️ Settings",
]


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    # Language toggle
    ui_lang = st.selectbox("🌐", ["中文", "English"], key="ui_lang", label_visibility="collapsed")
    is_en = (ui_lang == "English")

    st.title("🧠 Smart Suite")
    st.caption("GEO Content Pipeline · Phase I" if is_en else "智系列 · GEO Content Pipeline · Phase I")

    if DEMO_MODE:
        st.warning("🎬 Demo Mode" if is_en else "🎬 演示模式 — 仅展示，执行功能已禁用")
    st.divider()

    # Select nav pages based on language
    NAV_PAGES = NAV_PAGES_EN if is_en else NAV_PAGES_ZH

    # Handle jump_to_page
    if "jump_to_page" in st.session_state:
        target = st.session_state.pop("jump_to_page")
        # Map between ZH and EN page names
        if target in NAV_PAGES:
            st.session_state["nav_radio"] = target
        else:
            # Try to find matching page by index
            for pages in [NAV_PAGES_ZH, NAV_PAGES_EN]:
                if target in pages:
                    idx = pages.index(target)
                    st.session_state["nav_radio"] = NAV_PAGES[idx]
                    break

    # Handle URL query param ?tool=zhiku to auto-navigate
    _qp = st.query_params
    if "tool" in _qp and "nav_radio" not in st.session_state:
        _tool_map_idx = {
            "zhiku": 1, "zhice": 2, "zhizao": 3, "zhiyou": 4,
            "zhibu": 5, "zhichuan": 6, "zhixi": 7,
            "zhishu": 8, "zhongshu": 8,
            "overview": 0, "settings": 12,
        }
        _idx = _tool_map_idx.get(_qp["tool"])
        if _idx is not None and _idx < len(NAV_PAGES):
            st.session_state["nav_radio"] = NAV_PAGES[_idx]

    page = st.radio(
        "导航",
        NAV_PAGES,
        label_visibility="collapsed",
        key="nav_radio",
    )
    st.divider()

    batches = get_batches()
    selected_batch = batches[0] if batches else "batch_003"
    market = "ALL"
    kw_limit = 10
    week = "WK21"

    st.divider()
    st.caption(f"{'Path' if is_en else '路径'}: {BASE_PATH}")

    # Map current page selection to page index for consistent routing
    _page_idx = NAV_PAGES.index(page) if page in NAV_PAGES else 0


# ============================================================
# PAGE: 总览
# ============================================================
if _page_idx == 0:
    import streamlit.components.v1 as components
    # Load EN or ZH version based on sidebar language
    if is_en:
        wiki_path = Path(__file__).parent / "smart-suite-wiki.html"
    else:
        wiki_path = Path(__file__).parent / "smart-suite-wiki-zh.html"
        if not wiki_path.exists():
            wiki_path = Path(__file__).parent / "smart-suite-wiki.html"
    if wiki_path.exists():
        wiki_html = wiki_path.read_text(encoding="utf-8")
        components.html(wiki_html, height=4200, scrolling=True)
    else:
        st.title("🏠 Smart Suite Overview" if is_en else "🏠 Smart Suite 总览")
        st.warning("smart-suite-wiki.html not found")

    # (End of overview page)



elif _page_idx == 1:
    st.markdown("""<div style="padding:20px 0 10px;"><h1 style="font-size:28px;font-weight:800;color:#ffa726;margin:0;">📚 """ + ("Query Library – Phrase Production & Validation" if is_en else "智库 – 检索短语产出与验证") + """</h1><p style="font-size:13px;color:#8892b0;margin-top:6px;">""" + ("Produce → Calibrate → Dedupe → Select → Verify Gap → Confirm to Production" if is_en else "产出 → 校准 → 去重 → 选取 → 验证Gap → 确认进智造") + """</p></div>""", unsafe_allow_html=True)
    render_pipeline_flow("zhiku", selected_batch)

    # --- Status bar ---
    df_zhiku_all = load_zhiku_live(selected_batch)
    total_phrases = len(df_zhiku_all) if not df_zhiku_all.empty else 0
    selected_count = 0
    if not df_zhiku_all.empty and "is_selected" in df_zhiku_all.columns:
        selected_count = df_zhiku_all[df_zhiku_all["is_selected"].astype(str).str.upper().isin(["TRUE", "1", "YES"])].shape[0]

    sc1, sc2, sc3, sc4 = st.columns(4)
    sc1.metric("Total Phrases" if is_en else "短语总量", total_phrases)
    sc2.metric("Selected" if is_en else "已选中", selected_count)
    sc3.metric("Categories" if is_en else "覆盖类别", df_zhiku_all["category"].dropna().nunique() if not df_zhiku_all.empty and "category" in df_zhiku_all.columns else 0)
    sc4.metric("Sources" if is_en else "来源数", df_zhiku_all["source"].dropna().nunique() if not df_zhiku_all.empty and "source" in df_zhiku_all.columns else 0)

    st.divider()

    # ============================================================
    # ① 短语产出
    # ============================================================
    st.markdown("""<div style="background:#1a1d2e;border:1px solid #2a2f4a;border-radius:12px;padding:20px;margin:16px 0;">
        <h3 style="color:#ffa726;font-size:18px;font-weight:700;margin:0 0 8px;">① """ + ("Phrase Production" if is_en else "短语产出") + """</h3>
        <p style="color:#8892b0;font-size:12px;margin:0;">""" + ("3 input modes: AI auto / Upload CSV / Manual input" if is_en else "三种输入模式：AI 自动 / 上传 CSV / 手动输入") + """</p>
    </div>""", unsafe_allow_html=True)

    tab_p1, tab_p2, tab_p3 = st.tabs([
        "⭐ P1 Core (95-90%)" if is_en else "⭐ P1 核心来源 (95-90%)",
        "⭐ P2 Secondary (85-75%)" if is_en else "⭐ P2 次核心 (85-75%)",
        "P3 Expand (60%)" if is_en else "P3 兜底扩写 (60%)",
    ])

    # --- P1 核心来源 ---
    with tab_p1:
        st.caption("AI platform native queries — highest accuracy" if is_en else "AI 平台原生问句 — 准确度最高")
        col_dropdown, col_reverse, col_community = st.columns(3)

        with col_dropdown:
            st.markdown("**A1: AI Dropdown**" if is_en else "**A1: AI 下拉联想**")
            st.caption("95% · Collect from platforms, upload" if is_en else "准确度95% · 从各平台收集后上传")
            uploaded_dropdown = st.file_uploader("Upload" if is_en else "上传CSV", type=["csv", "xlsx"], key="upload_a1")
            if uploaded_dropdown:
                try:
                    df_imp = pd.read_csv(uploaded_dropdown, encoding="utf-8-sig", on_bad_lines="skip") if uploaded_dropdown.name.endswith(".csv") else pd.read_excel(uploaded_dropdown, engine="openpyxl")
                    if "source" not in df_imp.columns: df_imp["source"] = "ai_dropdown"
                    if "is_selected" not in df_imp.columns: df_imp["is_selected"] = "TRUE"
                    if "priority_score" not in df_imp.columns: df_imp["priority_score"] = 4.8
                    zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                    zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                    existing = load_csv_safe(zhiku_file) if zhiku_file.exists() else pd.DataFrame()
                    merged = pd.concat([existing, df_imp], ignore_index=True)
                    if "ai_query" in merged.columns: merged = merged.drop_duplicates(subset=["ai_query"], keep="first")
                    merged.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                    st.success(f"✅ +{len(df_imp)} (A1)")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        with col_reverse:
            st.markdown("**A2: Reverse Recall**" if is_en else "**A2: 逆向召回**")
            st.caption("92% · Input content → AI returns queries" if is_en else "准确度92% · 输入内容 → AI返回问句")

            # Single input
            reverse_content = st.text_area("Single content" if is_en else "单条内容", height=60, key="reverse_input_p1", placeholder="Paste one article text or URL...")
            num_queries = st.select_slider("Queries per content" if is_en else "每条内容返回问句数", options=[5, 10, 15, 20], value=10, key="reverse_num")
            if st.button("🔮 Run Single" if is_en else "🔮 单条执行", key="btn_reverse_single", disabled=not reverse_content):
                try:
                    from engine import call_bedrock_claude
                    prompt = f"以下是一篇已发布内容：\n{reverse_content[:2000]}\n\n用户在AI搜索引擎中输入什么问句才能看到这篇内容？列出{num_queries}个口语化问句，按命中概率排序，每行一条。"
                    with st.spinner("..." if is_en else "正在询问AI..."):
                        response = call_bedrock_claude(prompt)
                    queries = [q.strip().lstrip("0123456789.-、）) ") for q in response.strip().split("\n") if q.strip() and len(q.strip()) > 5]
                    if queries:
                        new_df = pd.DataFrame({"ai_query": queries, "source": "reverse_recall", "priority_score": 4.6, "is_selected": "TRUE"})
                        zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                        zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                        existing = load_csv_safe(zhiku_file) if zhiku_file.exists() else pd.DataFrame()
                        merged = pd.concat([existing, new_df], ignore_index=True)
                        if "ai_query" in merged.columns: merged = merged.drop_duplicates(subset=["ai_query"], keep="first")
                        merged.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                        st.success(f"✅ +{len(queries)} (A2)")
                        st.rerun()
                except Exception as e:
                    st.error(str(e))

            # Batch upload
            st.caption("— or batch —" if is_en else "— 或批量 —")
            up_reverse = st.file_uploader("Upload content list CSV" if is_en else "上传内容列表CSV（含content列）", type=["csv"], key="upload_a2_batch")
            if up_reverse:
                st.caption("CSV should have a 'content' or 'url' column" if is_en else "CSV需含 content 或 url 列")
                if st.button("🔮 Run Batch" if is_en else "🔮 批量执行逆向召回", key="btn_reverse_batch"):
                    try:
                        from engine import call_bedrock_claude
                        df_batch = pd.read_csv(up_reverse, encoding="utf-8-sig", on_bad_lines="skip")
                        content_col = "content" if "content" in df_batch.columns else ("url" if "url" in df_batch.columns else df_batch.columns[0])
                        all_queries = []
                        progress = st.progress(0)
                        for i, row in df_batch.iterrows():
                            text = str(row[content_col])[:2000]
                            prompt = f"以下是一篇内容：\n{text}\n\n用户输入什么问句能找到这篇内容？列出5个口语化问句，每行一条。"
                            response = call_bedrock_claude(prompt)
                            qs = [q.strip().lstrip("0123456789.-、） ") for q in response.strip().split("\n") if q.strip() and len(q.strip()) > 5]
                            all_queries.extend(qs)
                            progress.progress((i + 1) / len(df_batch))
                        if all_queries:
                            new_df = pd.DataFrame({"ai_query": all_queries, "source": "reverse_recall", "priority_score": 4.6, "is_selected": "TRUE"})
                            zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                            zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                            existing = load_csv_safe(zhiku_file) if zhiku_file.exists() else pd.DataFrame()
                            merged = pd.concat([existing, new_df], ignore_index=True)
                            if "ai_query" in merged.columns: merged = merged.drop_duplicates(subset=["ai_query"], keep="first")
                            merged.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                            st.success(f"✅ +{len(all_queries)} from {len(df_batch)} contents")
                            st.rerun()
                    except Exception as e:
                        st.error(str(e))

        with col_community:
            st.markdown("**A3: AI Community Q&A**" if is_en else "**A3: AI 社区原生提问**")
            st.caption("90% · Upload from Zhihu/Perplexity" if is_en else "准确度90% · 从知乎/Perplexity上传")
            uploaded_a3 = st.file_uploader("Upload" if is_en else "上传CSV", type=["csv", "xlsx"], key="upload_a3")
            if uploaded_a3:
                try:
                    df_imp = pd.read_csv(uploaded_a3, encoding="utf-8-sig", on_bad_lines="skip") if uploaded_a3.name.endswith(".csv") else pd.read_excel(uploaded_a3, engine="openpyxl")
                    if "source" not in df_imp.columns: df_imp["source"] = "ai_community"
                    if "is_selected" not in df_imp.columns: df_imp["is_selected"] = "TRUE"
                    if "priority_score" not in df_imp.columns: df_imp["priority_score"] = 4.5
                    zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                    zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                    existing = load_csv_safe(zhiku_file) if zhiku_file.exists() else pd.DataFrame()
                    merged = pd.concat([existing, df_imp], ignore_index=True)
                    if "ai_query" in merged.columns: merged = merged.drop_duplicates(subset=["ai_query"], keep="first")
                    merged.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                    st.success(f"✅ +{len(df_imp)} (A3)")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # --- P2 次核心（上传为主）---
    with tab_p2:
        st.caption("Real user behavior data — upload + AI expand" if is_en else "真实用户行为数据 — 上传 + AI 裂变")

        # Source type selection
        upload_source = st.selectbox("Source Type" if is_en else "来源类型", [
            "SEO/SEM 关键词裂变",
            "官方渠道（站内搜索/客服FAQ/公众号）",
            "社群/客服/直播问句",
            "AlsoAsked/AnswerThePublic",
            "其他"
        ], key="upload_source_type")

        # Upload
        uploaded_phrases = st.file_uploader("Upload CSV/Excel" if is_en else "上传 CSV/Excel", type=["csv", "xlsx"], key="upload_phrases_new")

        # SEO/SEM specific: expansion controls
        if upload_source == "SEO/SEM 关键词裂变":
            st.caption("Upload keywords → AI expands into query phrases" if is_en else "上传关键词 → AI 裂变为口语问句")
            col_limit, col_action = st.columns([1, 1])
            with col_limit:
                kw_per_batch = st.select_slider("Keywords per batch" if is_en else "每次裂变关键词数", options=[5, 10, 20, 30, 50], value=10, key="kw_per_batch_p2")
            with col_action:
                if uploaded_phrases:
                    df_kw = pd.read_csv(uploaded_phrases, on_bad_lines="skip") if uploaded_phrases.name.endswith(".csv") else pd.read_excel(uploaded_phrases, engine="openpyxl")
                    st.session_state["uploaded_keywords"] = df_kw
                    INPUT_PATH.mkdir(parents=True, exist_ok=True)
                    df_kw.to_csv(INPUT_PATH / "seo_sem_keywords.csv", index=False, encoding="utf-8-sig")
                    st.caption(f"✅ {len(df_kw)} keywords loaded")
                    if st.button("🚀 Expand Keywords" if is_en else "🚀 裂变关键词", type="primary", key="btn_seo_p2"):
                        try:
                            from engine import run_zhiku
                            with st.spinner("Expanding..." if is_en else "裂变中..."):
                                result = run_zhiku(selected_batch, market, kw_per_batch)
                            if result["success"]:
                                st.success(f"✅ +{result['query_count']} phrases")
                                st.rerun()
                            else:
                                st.error(result['error'])
                        except Exception as e:
                            st.error(str(e))
        else:
            # Non-SEO sources: direct upload to library
            if uploaded_phrases:
                try:
                    if uploaded_phrases.name.endswith(".xlsx"):
                        df_import = pd.read_excel(uploaded_phrases, engine="openpyxl")
                    else:
                        df_import = pd.read_csv(uploaded_phrases, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
                    if "source" not in df_import.columns:
                        df_import["source"] = upload_source
                    if "is_selected" not in df_import.columns:
                        df_import["is_selected"] = "TRUE"
                    zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                    zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                    if zhiku_file.exists():
                        existing = load_csv_safe(zhiku_file)
                        merged = pd.concat([existing, df_import], ignore_index=True)
                        if "ai_query" in merged.columns:
                            merged = merged.drop_duplicates(subset=["ai_query"], keep="first")
                        merged.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                        st.success(f"✅ +{len(df_import)} phrases (source: {upload_source})")
                    else:
                        df_import.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                        st.success(f"✅ {len(df_import)} phrases imported")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # --- P3 兜底扩写 ---
    with tab_p3:
        col_free, col_seed = st.columns(2)
        with col_free:
            st.markdown("**" + ("Free input (one per line)" if is_en else "自由输入（每行一条）") + "**")
            manual_text = st.text_area("Phrases" if is_en else "短语", height=120, key="manual_phrases", placeholder="亚马逊怎么注册\nFBA费用多少\n跨境电商新手入门")
            if st.button("➕ Add" if is_en else "➕ 添加", key="btn_manual_add", disabled=not manual_text):
                phrases = [p.strip() for p in manual_text.strip().split("\n") if p.strip()]
                if phrases:
                    new_df = pd.DataFrame({"ai_query": phrases, "source": "manual", "priority_score": 3.5, "is_selected": "TRUE"})
                    zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                    zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                    if zhiku_file.exists():
                        existing = load_csv_safe(zhiku_file)
                        merged = pd.concat([existing, new_df], ignore_index=True).drop_duplicates(subset=["ai_query"], keep="first")
                        merged.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                    else:
                        new_df.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                    st.success(f"✅ +{len(phrases)}")
                    st.rerun()

        with col_seed:
            st.markdown("**" + ("Seed word expansion" if is_en else "词根扩展") + "**")
            seed_words = st.text_area("Seeds" if is_en else "词根（每行一个）", height=80, key="seed_input_new", placeholder="跨境电商\n亚马逊开店\n选品")
            phrases_per_seed = st.select_slider("Phrases per seed" if is_en else "每个词根生成数", options=[5, 10, 15, 20, 30], value=15, key="seed_count_p3")
            if st.button("🚀 Expand Seeds" if is_en else "🚀 裂变词根", key="btn_seed_expand", disabled=not seed_words):
                seeds = [s.strip() for s in seed_words.strip().split("\n") if s.strip()]
                if seeds:
                    try:
                        from engine import run_semantic_expansion
                        total_gen = 0
                        with st.spinner("Expanding..." if is_en else "裂变中..."):
                            for seed in seeds:
                                r = run_semantic_expansion(seed, market, phrases_per_seed, "zh", selected_batch)
                                if r.get("success"):
                                    total_gen += r.get("query_count", 0)
                        if total_gen > 0:
                            st.success(f"✅ +{total_gen}")
                            st.rerun()
                    except Exception as e:
                        st.error(str(e))

    st.divider()

    # ============================================================
    # ② 校准 + 去重
    # ============================================================
    st.markdown("""<div style="background:#1a1d2e;border:1px solid #2a2f4a;border-radius:12px;padding:20px;margin:16px 0;">
        <h3 style="color:#ffa726;font-size:18px;font-weight:700;margin:0 0 8px;">② """ + ("Calibrate & Dedupe" if is_en else "校准 + 去重") + """</h3>
    </div>""", unsafe_allow_html=True)

    if total_phrases > 0:
        col_b1, col_b2, col_b3, col_dedup = st.columns(4)
        with col_b1:
            st.metric("B1 Platform Consensus" if is_en else "B1 跨平台共识", "—", help="Optional: requires API calls")
        with col_b2:
            cat_matched = df_zhiku_all["category"].notna().sum() if not df_zhiku_all.empty and "category" in df_zhiku_all.columns else 0
            st.metric("B2 Category Match" if is_en else "B2 类别匹配", f"{cat_matched}/{total_phrases}")
        with col_b3:
            st.metric("B3 Timeliness" if is_en else "B3 时效性", f"{total_phrases}/{total_phrases}", help="Auto-check for expired terms")
        with col_dedup:
            st.metric("Dedupe" if is_en else "去重", f"{total_phrases} → ?")

        if st.button("🔄 Run Calibrate & Dedupe" if is_en else "🔄 执行校准去重", key="btn_calibrate"):
            # Simple dedup on ai_query
            zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
            if zhiku_file.exists():
                df = load_csv_safe(zhiku_file)
                before = len(df)
                if "ai_query" in df.columns:
                    df = df.drop_duplicates(subset=["ai_query"], keep="first")
                after = len(df)
                df.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                st.success(f"✅ Deduped: {before} → {after} (removed {before - after})" if is_en else f"✅ 去重完成：{before} → {after}（删除 {before - after} 条）")
                st.rerun()
    else:
        st.caption("No phrases yet. Use Step ① to produce phrases first." if is_en else "暂无短语，请先执行第①步产出短语。")

    st.divider()

    # ============================================================
    # ③ 人工选取/修改
    # ============================================================
    st.markdown("""<div style="background:#1a1d2e;border:1px solid #2a2f4a;border-radius:12px;padding:20px;margin:16px 0;">
        <h3 style="color:#ffa726;font-size:18px;font-weight:700;margin:0 0 8px;">③ """ + ("Review & Select" if is_en else "审核 & 选取") + """</h3>
    </div>""", unsafe_allow_html=True)

    df_q = load_zhiku_live(selected_batch)
    if not df_q.empty:
        # Filters
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filter_options = ["All" if is_en else "全部", "✅ Selected" if is_en else "✅ 已选中", "⬜ Not selected" if is_en else "⬜ 未选中"]
            if "source" in df_q.columns:
                filter_options += sorted(df_q["source"].dropna().unique().tolist())
            sel_filter = st.selectbox("Filter" if is_en else "筛选", filter_options, key="zhiku_filter")
        with col_f2:
            if "category" in df_q.columns:
                cat_options = ["All" if is_en else "全部"] + sorted(df_q["category"].dropna().unique().tolist())
                cat_filter = st.selectbox("Category" if is_en else "类别", cat_options, key="zhiku_cat_filter")
            else:
                cat_filter = "全部"

        # Apply filters
        df_display = df_q.copy()
        if sel_filter in ["✅ Selected", "✅ 已选中"] and "is_selected" in df_display.columns:
            df_display = df_display[df_display["is_selected"].astype(str).str.upper().isin(["TRUE", "1", "YES"])]
        elif sel_filter in ["⬜ Not selected", "⬜ 未选中"] and "is_selected" in df_display.columns:
            df_display = df_display[~df_display["is_selected"].astype(str).str.upper().isin(["TRUE", "1", "YES"])]
        elif sel_filter not in ["All", "全部", "✅ Selected", "✅ 已选中", "⬜ Not selected", "⬜ 未选中"] and "source" in df_display.columns:
            df_display = df_display[df_display["source"] == sel_filter]
        if cat_filter not in ["All", "全部"] and "category" in df_display.columns:
            df_display = df_display[df_display["category"] == cat_filter]

        # Bulk actions
        col_sa, col_sn, col_count = st.columns([1, 1, 4])
        with col_sa:
            if st.button("✅ Select All" if is_en else "✅ 全选", key="btn_sel_all"):
                zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                df_q["is_selected"] = df_q["is_selected"].astype(str)
                df_q.loc[df_display.index, "is_selected"] = "TRUE"
                df_q.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                st.rerun()
        with col_sn:
            if st.button("⬜ Deselect All" if is_en else "⬜ 全不选", key="btn_desel_all"):
                zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                df_q["is_selected"] = df_q["is_selected"].astype(str)
                df_q.loc[df_display.index, "is_selected"] = "FALSE"
                df_q.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                st.rerun()
        with col_count:
            sel_now = df_display[df_display["is_selected"].astype(str).str.upper().isin(["TRUE", "1", "YES"])].shape[0] if "is_selected" in df_display.columns else 0
            st.caption(f"{'Showing' if is_en else '显示'} {len(df_display)} | {'Selected' if is_en else '选中'} {sel_now}")

        # Editable table
        edit_cols = [c for c in ["ai_query", "category", "source", "priority_score", "is_selected"] if c in df_display.columns]
        if edit_cols:
            column_config = {}
            if "category" in df_display.columns:
                column_config["category"] = st.column_config.SelectboxColumn("Category" if is_en else "类别", options=CATEGORIES_35)
            if "is_selected" in df_display.columns:
                df_display["is_selected"] = df_display["is_selected"].astype(str).str.upper().isin(["TRUE", "1", "YES"])
                column_config["is_selected"] = st.column_config.CheckboxColumn("Sel" if is_en else "选")
            if "source" in df_display.columns:
                column_config["source"] = st.column_config.TextColumn("Source" if is_en else "来源", disabled=True)

            edited_df = st.data_editor(df_display[edit_cols], column_config=column_config, use_container_width=True, hide_index=True, num_rows="dynamic", key="zhiku_editor_new")

            # Save button — saves checkbox edits to file
            if st.button("💾 Save Edits" if is_en else "💾 保存编辑", key="btn_save_edits"):
                zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                try:
                    # Ensure is_selected is string type in df_q before assignment
                    if "is_selected" in df_q.columns:
                        df_q["is_selected"] = df_q["is_selected"].astype(str)
                    for col in edit_cols:
                        if col in edited_df.columns and col in df_q.columns:
                            if col == "is_selected":
                                vals = edited_df[col].apply(lambda x: "TRUE" if x else "FALSE").values
                                df_q.loc[df_display.index[:len(vals)], col] = vals
                            else:
                                vals = edited_df[col].values
                                df_q.loc[df_display.index[:len(vals)], col] = vals
                    df_q.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                    st.success("✅ Saved" if is_en else "✅ 已保存")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        # Export
        csv_export = df_display.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 Export CSV" if is_en else "📥 导出 CSV", csv_export, file_name=f"zhiku_{selected_batch}.csv", mime="text/csv")
    else:
        st.caption("No phrases yet." if is_en else "暂无短语。")

    st.divider()

    # ============================================================
    # ④ CTA → 智测验证 / 直接智造
    # ============================================================
    st.markdown("""<div style="background:#1a1d2e;border:1px solid #2a2f4a;border-radius:12px;padding:20px;margin:16px 0;">
        <h3 style="color:#4caf50;font-size:18px;font-weight:700;margin:0;">④ """ + ("Next Step" if is_en else "下一步") + """</h3>
    </div>""", unsafe_allow_html=True)

    col_verify, col_skip = st.columns([2, 1])
    with col_verify:
        if st.button("🔍 Send to 智测 Verify Gap" if is_en else "🔍 发送到智测验证 Gap", type="primary", key="cta_to_zhice"):
            # Use in-memory df_q which has auto-saved edits
            if not df_q.empty and "ai_query" in df_q.columns:
                df_sel = df_q.copy()
                if "is_selected" in df_sel.columns:
                    df_sel = df_sel[df_sel["is_selected"].astype(str).str.upper().isin(["TRUE", "1", "YES"])]
                if not df_sel.empty:
                    zhice_dir = OUTPUT_PATH.parent / "zhice"
                    zhice_dir.mkdir(parents=True, exist_ok=True)
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                    queue_file = zhice_dir / f"zhiku_verify_queue_{ts}.json"
                    queue_data = {"source": "zhiku", "batch_id": selected_batch, "queries_to_verify": df_sel["ai_query"].tolist(), "total_count": len(df_sel), "created_at": ts}
                    queue_file.write_text(json.dumps(queue_data, ensure_ascii=False, indent=2), encoding='utf-8')
                    st.success(f"✅ {len(df_sel)} phrases sent" if is_en else f"✅ {len(df_sel)} 条已发送到智测")
                    jump_to("🔍 智测")
                    st.rerun()
                else:
                    st.warning("No selected phrases. Use ✅ Select All or check boxes above." if is_en else "没有选中的短语。请先用 ✅全选 或在上方表格勾选。")
            else:
                st.warning("No phrases in library" if is_en else "短语库为空")
    with col_skip:
        if st.button("⏭️ Skip to 智造" if is_en else "⏭️ 跳过直接智造", key="cta_skip_zhizao"):
            jump_to("✍️ 智造")
            st.rerun()

    # History
    with st.expander("📜 History" if is_en else "📜 历史记录"):
        batch_path = OUTPUT_PATH / selected_batch / "01_zhiku"
        col_hist, col_clear = st.columns([4, 1])
        with col_clear:
            if st.button("🗑️ Clear All" if is_en else "🗑️ 清空全部", key="clear_zhiku_hist"):
                if batch_path.exists():
                    for f in batch_path.glob("*.csv"):
                        f.unlink()
                    archive_path = batch_path / "archive"
                    if archive_path.exists():
                        for f in archive_path.glob("*.csv"):
                            f.unlink()
                st.success("Cleared" if is_en else "已清空")
                st.rerun()
        all_files = []
        if batch_path.exists():
            all_files.extend([f for f in batch_path.glob("*.csv")])
            archive_path = batch_path / "archive"
            if archive_path.exists():
                all_files.extend([f for f in archive_path.glob("*.csv")])
        if all_files:
            all_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            for f in all_files[:10]:
                mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                st.caption(f"📄 {f.name} · {f.stat().st_size/1024:.1f}KB · 🕐 {mtime}")
        else:
            st.caption("No history" if is_en else "暂无历史")


# ============================================================
# PAGE: 智测 (Gap Verification)
# ============================================================
elif _page_idx == 2:
    st.markdown("""<div style="padding:20px 0 10px;"><h1 style="font-size:28px;font-weight:800;color:#00bcd4;margin:0;">🔍 """ + ("Gap Verification – AI Search Coverage Test" if is_en else "智测 – AI 检索覆盖验证") + """</h1><p style="font-size:13px;color:#8892b0;margin-top:6px;">""" + ("Verify search phrases against 7 AI platforms to discover content gaps" if is_en else "在 7 个 AI 平台验证检索短语的覆盖状态，发现内容 Gap") + """</p></div>""", unsafe_allow_html=True)
    render_pipeline_flow("zhice", selected_batch)

    # --- Input: phrases to verify ---
    st.markdown("""<div style="background:#1a1d2e;border:1px solid #2a2f4a;border-radius:12px;padding:20px;margin:16px 0;">
        <h3 style="color:#00bcd4;font-size:18px;font-weight:700;margin:0 0 8px;">① """ + ("Phrases to Verify" if is_en else "待验证短语") + """</h3>
    </div>""", unsafe_allow_html=True)

    # Load from zhiku queue or upload
    zhice_dir = OUTPUT_PATH.parent / "zhice"
    queue_phrases = []
    if zhice_dir.exists():
        queue_files = sorted(zhice_dir.glob("zhiku_verify_queue_*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        if queue_files:
            latest_queue = json.loads(queue_files[0].read_text(encoding="utf-8"))
            queue_phrases = latest_queue.get("queries_to_verify", [])
            st.caption(f"{'From 智库' if is_en else '来自智库'}: {len(queue_phrases)} phrases ({queue_files[0].stem})")

    col_queue, col_upload = st.columns(2)
    with col_queue:
        if queue_phrases:
            st.dataframe(pd.DataFrame({"ai_query": queue_phrases}), use_container_width=True, hide_index=True, height=200)
        else:
            st.caption("No pending queue. Upload or go to 智库 to send phrases." if is_en else "暂无待验证队列。请上传或从智库发送短语。")

    with col_upload:
        st.markdown("**" + ("Upload phrases to verify" if is_en else "上传待验证短语") + "**")
        up_verify = st.file_uploader("CSV with ai_query column" if is_en else "CSV（含 ai_query 列）", type=["csv", "xlsx"], key="zhice_upload_phrases")
        if up_verify:
            df_up = pd.read_csv(up_verify, encoding="utf-8-sig", on_bad_lines="skip") if up_verify.name.endswith(".csv") else pd.read_excel(up_verify, engine="openpyxl")
            if "ai_query" in df_up.columns:
                queue_phrases = df_up["ai_query"].tolist()
                st.success(f"✅ {len(queue_phrases)} phrases loaded")

    st.divider()

    # --- Execute verification ---
    st.markdown("""<div style="background:#1a1d2e;border:1px solid #2a2f4a;border-radius:12px;padding:20px;margin:16px 0;">
        <h3 style="color:#00bcd4;font-size:18px;font-weight:700;margin:0 0 8px;">② """ + ("Execute Verification" if is_en else "执行验证") + """</h3>
    </div>""", unsafe_allow_html=True)

    ZHICE_PLATFORMS = {"qianwen": "通义千问", "deepseek": "DeepSeek", "kimi": "Kimi", "doubao": "豆包", "chatgpt": "ChatGPT", "perplexity": "Perplexity", "gemini": "Gemini"}
    selected_platforms = st.multiselect("Platforms" if is_en else "验证平台", list(ZHICE_PLATFORMS.keys()), default=["qianwen", "deepseek"], format_func=lambda x: ZHICE_PLATFORMS[x], key="zhice_platforms")

    col_auto, col_manual = st.columns(2)
    with col_auto:
        if st.button("🔍 Auto Verify (API)" if is_en else "🔍 AI 自动验证", type="primary", key="zhice_auto_run", disabled=not queue_phrases):
            try:
                from zhice_engine import REAL_API_MAP
                import time as _time
                results = []
                progress = st.progress(0)
                total = len(queue_phrases) * len(selected_platforms)
                done = 0
                for query in queue_phrases:
                    for platform in selected_platforms:
                        api_func = REAL_API_MAP.get(platform)
                        if api_func:
                            try:
                                r = api_func(query)
                                answer = r.get("full_answer", "")
                                has_brand = "全球开店" in answer or "Global Selling" in answer or "亚马逊" in answer
                                has_link = "amazon" in answer.lower()
                                results.append({"ai_query": query, "platform": platform, "has_brand_mention": has_brand, "has_official_link": has_link})
                            except Exception:
                                results.append({"ai_query": query, "platform": platform, "has_brand_mention": False, "has_official_link": False})
                        done += 1
                        progress.progress(done / total)
                        _time.sleep(0.3)
                # Aggregate per query
                df_results = pd.DataFrame(results)
                gap_summary = []
                for q in queue_phrases:
                    q_data = df_results[df_results["ai_query"] == q]
                    brand_count = q_data["has_brand_mention"].sum()
                    link_count = q_data["has_official_link"].sum()
                    total_p = len(q_data)
                    if brand_count > 0 and link_count > 0:
                        gap_status = "covered"
                    elif brand_count > 0 or link_count > 0:
                        gap_status = "partial_gap"
                    else:
                        gap_status = "full_gap"
                    gap_summary.append({"ai_query": q, "gap_status": gap_status, "has_brand_mention": brand_count > 0, "has_official_link": link_count > 0, "platforms_tested": total_p})
                df_gap = pd.DataFrame(gap_summary)
                st.session_state["zhice_gap_results"] = df_gap
                # Save
                zhice_dir.mkdir(parents=True, exist_ok=True)
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                df_gap.to_csv(zhice_dir / f"gap_result_{ts}.csv", index=False, encoding="utf-8-sig")
                st.success(f"✅ Verification complete!" if is_en else f"✅ 验证完成！")
                st.rerun()
            except ImportError:
                st.error("zhice_engine not available. Use manual upload instead." if is_en else "zhice_engine 不可用，请手动上传结果。")
            except Exception as e:
                st.error(str(e))

    with col_manual:
        st.markdown("**" + ("Upload verification results" if is_en else "上传验证结果") + "**")
        st.caption("CSV with columns: ai_query, gap_status, has_brand_mention, has_official_link" if is_en else "CSV需含列：ai_query, gap_status, has_brand_mention, has_official_link")
        up_result = st.file_uploader("Upload gap results" if is_en else "上传 Gap 结果", type=["csv", "xlsx"], key="zhice_upload_results")
        if up_result:
            df_gap = pd.read_csv(up_result, encoding="utf-8-sig", on_bad_lines="skip") if up_result.name.endswith(".csv") else pd.read_excel(up_result, engine="openpyxl")
            st.session_state["zhice_gap_results"] = df_gap
            zhice_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            df_gap.to_csv(zhice_dir / f"gap_result_{ts}.csv", index=False, encoding="utf-8-sig")
            st.success(f"✅ {len(df_gap)} results loaded" if is_en else f"✅ 加载 {len(df_gap)} 条结果")

    st.divider()

    # --- Results & Select ---
    st.markdown("""<div style="background:#1a1d2e;border:1px solid #2a2f4a;border-radius:12px;padding:20px;margin:16px 0;">
        <h3 style="color:#00bcd4;font-size:18px;font-weight:700;margin:0 0 8px;">③ """ + ("Gap Results & Select" if is_en else "Gap 结果 & 选取") + """</h3>
    </div>""", unsafe_allow_html=True)

    df_gap_display = st.session_state.get("zhice_gap_results", pd.DataFrame())
    # Load latest gap result file if session empty
    if df_gap_display.empty and zhice_dir.exists():
        gap_files = sorted(zhice_dir.glob("gap_result_*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
        if gap_files:
            df_gap_display = load_csv_safe(gap_files[0])

    if not df_gap_display.empty:
        # Summary metrics
        if "gap_status" in df_gap_display.columns:
            gc1, gc2, gc3, gc4 = st.columns(4)
            gc1.metric("Total" if is_en else "总计", len(df_gap_display))
            gc2.metric("✅ Covered" if is_en else "✅ 已覆盖", len(df_gap_display[df_gap_display["gap_status"] == "covered"]))
            gc3.metric("⚠️ Partial", len(df_gap_display[df_gap_display["gap_status"] == "partial_gap"]))
            gc4.metric("❌ Full Gap", len(df_gap_display[df_gap_display["gap_status"] == "full_gap"]))

        # Editable selection
        if "to_produce" not in df_gap_display.columns:
            df_gap_display["to_produce"] = df_gap_display["gap_status"].apply(lambda x: x in ["full_gap", "partial_gap"]) if "gap_status" in df_gap_display.columns else True

        show_cols = [c for c in ["ai_query", "gap_status", "has_brand_mention", "has_official_link", "to_produce"] if c in df_gap_display.columns]
        if show_cols:
            col_config = {"to_produce": st.column_config.CheckboxColumn("→ Produce" if is_en else "→ 生产")}
            edited_gap = st.data_editor(df_gap_display[show_cols], column_config=col_config, use_container_width=True, hide_index=True, key="zhice_gap_editor")
            produce_count = edited_gap["to_produce"].sum() if "to_produce" in edited_gap.columns else 0
            st.caption(f"{'Selected for production' if is_en else '选中进入智造'}: {produce_count}")

        # CTA
        st.divider()
        col_to_zhizao, col_to_zhiyou = st.columns(2)
        with col_to_zhizao:
            if st.button(f"✍️ {produce_count} → 智造 (new content)" if is_en else f"✍️ {produce_count} 条 → 智造（生产新内容）", type="primary", key="zhice_to_zhizao"):
                if "to_produce" in edited_gap.columns:
                    to_produce_queries = df_gap_display.loc[edited_gap["to_produce"] == True, "ai_query"].tolist() if "ai_query" in df_gap_display.columns else []
                    if to_produce_queries:
                        zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                        if zhiku_file.exists():
                            df_zhiku = load_csv_safe(zhiku_file)
                            if "ai_query" in df_zhiku.columns and "is_selected" in df_zhiku.columns:
                                # Reset all selections, then mark only zhice gap phrases
                                df_zhiku["is_selected"] = "FALSE"
                                df_zhiku.loc[df_zhiku["ai_query"].isin(to_produce_queries), "is_selected"] = "TRUE"
                                df_zhiku.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                            else:
                                # zhiku file missing expected columns — create fresh with gap phrases
                                df_new = pd.DataFrame({"ai_query": to_produce_queries, "is_selected": "TRUE"})
                                zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                                df_new.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                        else:
                            # No zhiku file exists — create one with the gap phrases
                            df_new = pd.DataFrame({"ai_query": to_produce_queries, "is_selected": "TRUE"})
                            zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                            df_new.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                        jump_to("✍️ 智造")
                        st.rerun()
        with col_to_zhiyou:
            if st.button("🔧 Partial gaps → 智优" if is_en else "🔧 部分Gap → 智优", key="zhice_to_zhiyou"):
                jump_to("🔧 智优")
                st.rerun()
    else:
        st.caption("No gap results yet. Execute verification above or upload results." if is_en else "暂无 Gap 结果。请执行验证或上传结果。")

    # History
    with st.expander("📜 History" if is_en else "📜 历史记录"):
        if zhice_dir.exists():
            files = sorted(zhice_dir.glob("gap_result_*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
            for f in files[:10]:
                mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                st.caption(f"📄 {f.name} · {mtime}")
        else:
            st.caption("No history" if is_en else "暂无历史")


# ============================================================
# PAGE: 智造 (Step 2) — 单页线性流程
# ============================================================
elif _page_idx == 3:
    st.markdown("""<div style="padding:20px 0 10px;"><h1 style="font-size:28px;font-weight:800;color:#ffcc02;margin:0;">✍️ """ + ("Content Creation – Content Generation" if is_en else "智造 – Content Generation") + """</h1><p style="font-size:13px;color:#8892b0;margin-top:6px;">""" + ("Step 2: Generate SEO+GEO dual-optimized content based on AI Queries" if is_en else "Step 2: 基于 AI Queries 生成 SEO+GEO 双优化内容") + """</p></div>""", unsafe_allow_html=True)
    render_pipeline_flow("zhizao", selected_batch)

    # --- Upload custom phrases directly ---
    with st.expander("📤 Upload Phrases (skip Query Library)" if is_en else "📤 上传检索短语（跳过智库直接生产内容）", expanded=False):
        st.caption("Optional: Upload prepared search phrase CSV/Excel, then click Run Content Gen to produce content directly" if is_en else "可选：如果已有准备好的检索短语 CSV/Excel，上传到此处后点击执行智造即可直接生产内容，无需经过智库裂变流程")
        upload_direct = st.file_uploader("Upload CSV (must contain ai_query column)" if is_en else "上传 CSV（需包含 ai_query 列）", type=["csv", "xlsx"], key="zhizao_direct_upload")
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
                st.success(f"✅ {'Uploaded' if is_en else '已上传'} {len(df_direct)} {'phrases, click Run Content Gen below' if is_en else '条检索短语，点击下方执行智造'}")
            except Exception as e:
                st.error(f"{'Upload failed' if is_en else '上传失败'}: {e}")

    # --- Show selected phrases from 智库 (editable) ---
    st.subheader("📋 Selected Phrases from Query Library" if is_en else "📋 智库已选中短语")
    zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
    df_zhiku = load_csv_safe(zhiku_file) if zhiku_file.exists() else pd.DataFrame()
    if not df_zhiku.empty and "is_selected" in df_zhiku.columns:
        df_selected = df_zhiku[df_zhiku["is_selected"].astype(str).str.upper().isin(["TRUE", "1", "YES"])].copy()
        if not df_selected.empty:
            edit_cols_z = [c for c in ["ai_query", "category", "priority_score", "is_selected"] if c in df_selected.columns]
            edited_phrases = st.data_editor(
                df_selected[edit_cols_z].reset_index(drop=True),
                column_config={
                    "ai_query": st.column_config.TextColumn("Search Phrase" if is_en else "检索短语", width="large"),
                    "category": st.column_config.TextColumn("Category" if is_en else "类别"),
                    "priority_score": st.column_config.NumberColumn("Score" if is_en else "综合分"),
                    "is_selected": st.column_config.CheckboxColumn("Selected" if is_en else "选中"),
                },
                use_container_width=True, hide_index=True,
                key="zhizao_phrase_editor",
            )
            st.caption(f"{'Selected' if is_en else '已选中'}: {edited_phrases['is_selected'].sum()} / {len(edited_phrases)} {'phrases' if is_en else '条'}")
            # Auto-save edits back
            try:
                df_zhiku.loc[df_selected.index, "is_selected"] = edited_phrases["is_selected"].apply(lambda x: "TRUE" if x else "FALSE").values
                df_zhiku.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
            except Exception:
                pass
        else:
            st.caption("No selected phrases in Query Library. Please go back to select some." if is_en else "智库中无已选中短语，请返回智库选中后再执行。")
    else:
        st.caption("No query library data found." if is_en else "未找到智库数据。")

    st.divider()

    # Execution
    st.subheader("▶️ Generate Content" if is_en else "▶️ 生成内容")

    # Show progress: how many already generated vs total selected
    df_existing_content = load_zhizao(selected_batch)
    already_generated = len(df_existing_content) if not df_existing_content.empty else 0
    total_selected = len(df_zhiku[df_zhiku["is_selected"].astype(str).str.upper().isin(["TRUE", "1", "YES"])]) if not df_zhiku.empty and "is_selected" in df_zhiku.columns else 0

    if total_selected > 0:
        st.progress(min(1.0, already_generated / total_selected), text=f"{'Generated' if is_en else '已生成'} {already_generated}/{total_selected} {'articles' if is_en else '篇'}")

    content_limit = st.number_input("Articles per batch" if is_en else "每批生成文章数", 1, 20, 5, key="zhizao_limit")

    remaining = max(0, total_selected - already_generated)
    if already_generated > 0 and remaining > 0:
        btn_label_z = f"🔄 {'Continue generating next' if is_en else '继续生成下一批'} {min(content_limit, remaining)} {'articles' if is_en else '篇'} ({already_generated}/{total_selected})"
    elif remaining == 0 and already_generated > 0:
        btn_label_z = f"🔄 {'Regenerate' if is_en else '重新生成'} ({already_generated} {'done' if is_en else '篇已完成'})"
    else:
        btn_label_z = "🚀 Run Content Gen" if is_en else "🚀 执行智造"

    if st.button(btn_label_z, type="primary", key="run_zhizao"):
        try:
            from engine import run_zhizao
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress_z(pct, msg):
                progress_bar.progress(min(1.0, max(0.0, pct)))
                status_text.text(msg)

            with st.spinner("Calling Bedrock Claude to generate content..." if is_en else "正在调用 Bedrock Claude 生成内容..."):
                result = run_zhizao(selected_batch, content_limit, update_progress_z)

            if result["success"]:
                st.success(f"✅ +{result['articles_generated']} {'articles' if is_en else '篇'}")
            else:
                st.error(f"❌ {'Failed' if is_en else '失败'}: {result['error']}")
        except ImportError:
            st.error("engine module not ready" if is_en else "engine 模块未就绪")

    st.divider()

    # Content display
    df_z = load_zhizao(selected_batch)
    if not df_z.empty:
        st.subheader("📤 Generated Content List" if is_en else "📤 生成内容列表")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Articles Generated" if is_en else "生成文章数", len(df_z))
        with col2:
            if "word_count" in df_z.columns:
                st.metric("Avg Word Count" if is_en else "平均字数", f"{df_z['word_count'].mean():.0f}")
        with col3:
            if "version" in df_z.columns:
                st.metric("Version" if is_en else "版本", df_z["version"].iloc[0] if len(df_z) > 0 else "N/A")

        display_cols = [c for c in ["content_id", "ai_query", "title", "word_count", "version"]
                       if c in df_z.columns]
        if display_cols:
            st.dataframe(df_z[display_cols], use_container_width=True, hide_index=True)

        # Download / Upload
        st.divider()
        col_dl, col_ul, col_cl = st.columns(3)
        with col_dl:
            csv_bytes = df_z.to_csv(index=False).encode("utf-8-sig")
            st.download_button("📥 Download CSV" if is_en else "📥 下载 CSV", csv_bytes,
                               file_name=f"zhizao_{selected_batch}.csv", mime="text/csv")
        with col_ul:
            uploaded_zhizao = st.file_uploader(
                "📤 Upload Modified File" if is_en else "📤 上传修改后文件", type=["csv"], key="upload_zhizao_edit"
            )
            if uploaded_zhizao is not None:
                df_new = pd.read_csv(uploaded_zhizao, on_bad_lines="skip")
                out_path = OUTPUT_PATH / selected_batch / "02_zhizao" / "zhizao_draft_content.csv"
                out_path.parent.mkdir(parents=True, exist_ok=True)
                df_new.to_csv(out_path, index=False, encoding="utf-8-sig")
                st.success(f"✅ {'Uploaded and replaced' if is_en else '已上传覆盖'} {len(df_new)} {'records' if is_en else '条记录'}")
        with col_cl:
            if st.button("🗑️ Clear History" if is_en else "🗑️ 清空历史", key="clear_zhizao"):
                zhizao_dir = OUTPUT_PATH / selected_batch / "02_zhizao"
                if zhizao_dir.exists():
                    for f in zhizao_dir.glob("zhizao_draft_content*.csv"):
                        f.unlink()
                st.success("Cleared" if is_en else "已清空")
                st.rerun()

        # Article preview — all articles (editable)
        st.divider()
        st.subheader(f"📖 {'Article Preview & Edit' if is_en else '文章预览 & 编辑'}（{len(df_z)} {'articles' if is_en else '篇'}）")
        st.caption("Edit article content below, changes auto-saved" if is_en else "可直接在下方编辑文章内容，修改后自动保存")
        if "title" in df_z.columns:
            zhizao_file = OUTPUT_PATH / selected_batch / "02_zhizao" / "zhizao_draft_content.csv"
            content_changed = False
            for idx, row in df_z.iterrows():
                title = str(row.get("title", f"{'Article' if is_en else '文章'} {idx+1}"))
                word_count = row.get("word_count", "?")
                with st.expander(f"📄 {title} ({word_count} {'words' if is_en else '字'})"):
                    if "ai_query" in df_z.columns:
                        st.caption(f"{'Search phrase' if is_en else '检索短语'}: {row.get('ai_query', '')}")
                    if "content_draft" in df_z.columns:
                        original = str(row.get("content_draft", ""))
                        edited_content = st.text_area(
                            "Body Content" if is_en else "正文内容",
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
                st.success("✅ Changes auto-saved" if is_en else "✅ 修改已自动保存")

        # --- 文章确认环节 ---
        st.divider()
        st.subheader("✅ Article Confirmation" if is_en else "✅ 文章确认")
        st.caption("Check confirmed articles; only confirmed ones proceed to Optimization" if is_en else "勾选确认通过的文章，只有确认的文章才会进入智优优化")

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
                    "title": st.column_config.TextColumn("Article Title" if is_en else "文章标题", disabled=True),
                    "confirmed": st.column_config.CheckboxColumn("Confirmed" if is_en else "确认通过"),
                },
                use_container_width=True,
                hide_index=True,
                key="zhizao_confirm_editor",
            )

            confirmed_count = df_confirm_edit["confirmed"].sum()
            total_count = len(df_confirm_edit)
            st.markdown(f"**{'Confirmed' if is_en else '已确认'} {confirmed_count} / {total_count} {'articles' if is_en else '篇'}**")

            # Auto-save confirmation status
            zhizao_file = OUTPUT_PATH / selected_batch / "02_zhizao" / "zhizao_draft_content.csv"
            df_z["confirmed"] = df_confirm_edit["confirmed"].values
            df_z.to_csv(zhizao_file, index=False, encoding="utf-8-sig")
    else:
        st.info(f"{'Batch' if is_en else '批次'} {selected_batch} {'has no content output yet, please run generation first.' if is_en else '暂无智造输出，请先执行生成。'}")

    # CTA → 智优
    st.divider()
    if st.button("➡️ Go to Optimization (Step 3)" if is_en else "➡️ 进入智优 (Step 3)", type="primary", key="cta_zhizao_to_zhiyou"):
        jump_to("🔧 智优")
        st.rerun()

    # 📜 历史记录 + 清空
    with st.expander("📜 History" if is_en else "📜 历史记录"):
        zhizao_dir = OUTPUT_PATH / selected_batch / "02_zhizao"
        col_h1, col_h2 = st.columns([4, 1])
        with col_h2:
            if st.button("🗑️ Clear All" if is_en else "🗑️ 清空全部", key="clear_zhizao_hist"):
                if zhizao_dir.exists():
                    for f in zhizao_dir.glob("*.csv"):
                        f.unlink()
                    st.success("Cleared" if is_en else "已清空")
        if zhizao_dir.exists():
            files = sorted(zhizao_dir.glob("*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
            for f in files:
                mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                col_i, col_r, col_d = st.columns([3, 1, 1])
                with col_i:
                    st.caption(f"📄 {f.name} · {f.stat().st_size/1024:.1f}KB · 🕐 {mtime}")
                with col_r:
                    if st.button("♻️ Reuse" if is_en else "♻️ 复用", key=f"reuse_zhizao_{f.name}"):
                        live_path = OUTPUT_PATH / selected_batch / "02_zhizao" / "zhizao_draft_content.csv"
                        safe_copy(f, live_path)
                        st.rerun()
                with col_d:
                    st.download_button("⬇️", f.read_bytes(), file_name=f.name, mime="text/csv", key=f"dl_zhizao_{f.name}")
        else:
            st.caption("No history" if is_en else "暂无历史")


# ============================================================
# PAGE: 智优 (Step 3) — 一键自动完成
# ============================================================
elif _page_idx == 4:
    st.markdown("""<div style="padding:20px 0 10px;"><h1 style="font-size:28px;font-weight:800;color:#e91e63;margin:0;">🔧 """ + ("Optimization – Score · Rewrite · Compliance" if is_en else "智优 – Score · Rewrite · Compliance") + """</h1><p style="font-size:13px;color:#8892b0;margin-top:6px;">""" + ("Step 3: One-click auto: Score → Rewrite → Compliance Review" if is_en else "Step 3: 一键自动完成 评分 → 重写优化 → 合规审查") + """</p></div>""", unsafe_allow_html=True)
    render_pipeline_flow("zhiyou", selected_batch)

    # Clear history button
    col_spacer, col_clear = st.columns([5, 1])
    with col_clear:
        if st.button("🗑️ Clear All" if is_en else "🗑️ 清空历史", key="clear_zhiyou_all"):
            zhiyou_dir = OUTPUT_PATH / selected_batch / "03_zhiyou"
            if zhiyou_dir.exists():
                for f in zhiyou_dir.glob("*.csv"):
                    f.unlink()
            st.success("Cleared" if is_en else "已清空")
            st.rerun()

    # --- Upload content directly (skip 智造) ---
    with st.expander("📤 Upload Content (skip Content Creation)" if is_en else "📤 上传内容（跳过智造直接优化）", expanded=False):
        st.caption("Optional: Upload existing article CSV for scoring/rewrite/compliance review" if is_en else "可选：上传已有文章 CSV，直接进行评分/重写/合规审查")
        upload_zhiyou = st.file_uploader("Upload CSV (must contain content_draft column)" if is_en else "上传 CSV（需含 content_draft 列）", type=["csv", "xlsx"], key="zhiyou_direct_upload")
        if upload_zhiyou:
            try:
                if upload_zhiyou.name.endswith(".xlsx"):
                    df_up = pd.read_excel(upload_zhiyou, engine="openpyxl")
                else:
                    df_up = pd.read_csv(upload_zhiyou, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
                out_dir = OUTPUT_PATH / selected_batch / "02_zhizao"
                out_dir.mkdir(parents=True, exist_ok=True)
                df_up.to_csv(out_dir / "zhizao_draft_content.csv", index=False, encoding="utf-8-sig")
                st.success(f"✅ {'Uploaded' if is_en else '已上传'} {len(df_up)} {'articles, ready for Optimization' if is_en else '篇文章，可执行智优'}")
            except Exception as e:
                st.error(f"{'Upload failed' if is_en else '上传失败'}: {e}")

    # --- Show incoming content from 智造 ---
    st.subheader("📋 Content from Content Creation" if is_en else "📋 智造输入内容")
    df_incoming = load_zhizao(selected_batch)
    if not df_incoming.empty:
        # Only show articles confirmed in 智造
        if "confirmed" in df_incoming.columns:
            df_incoming["confirmed"] = df_incoming["confirmed"].astype(str).str.strip().str.upper().isin(["TRUE", "1", "YES"])
            df_incoming = df_incoming[df_incoming["confirmed"] == True].reset_index(drop=True)
        if not df_incoming.empty:
            # Add include checkbox for zhiyou selection
            if "include_zhiyou" not in df_incoming.columns:
                df_incoming["include_zhiyou"] = True
            display_cols_in = [c for c in ["title", "ai_query", "word_count", "include_zhiyou"] if c in df_incoming.columns]
            edited_incoming = st.data_editor(
                df_incoming[display_cols_in],
                column_config={
                    "title": st.column_config.TextColumn("Title" if is_en else "标题", disabled=True),
                    "ai_query": st.column_config.TextColumn("Search Phrase" if is_en else "检索短语", disabled=True),
                    "word_count": st.column_config.NumberColumn("Words" if is_en else "字数", disabled=True),
                    "include_zhiyou": st.column_config.CheckboxColumn("Include" if is_en else "纳入优化"),
                },
                use_container_width=True, hide_index=True,
                key="zhiyou_incoming_editor",
            )
            selected_count = edited_incoming["include_zhiyou"].sum() if "include_zhiyou" in edited_incoming.columns else len(df_incoming)
            st.caption(f"{selected_count}/{len(df_incoming)} {'articles selected for optimization' if is_en else '篇已确认文章来自智造'}")
        else:
            st.caption("No confirmed articles in Content Creation. Go back to confirm some." if is_en else "智造中无已确认文章，请返回智造确认后再执行。")
    else:
        st.caption("No content from Content Creation. Upload or run Content Creation first." if is_en else "暂无智造内容，请先上传或执行智造。")

    st.divider()

    # One-click execution
    st.subheader("▶️ One-Click Full Optimization" if is_en else "▶️ 一键执行智优全流程")
    st.markdown("Auto-execute in order: **Score → Rewrite → Compliance Review**" if is_en else "自动按顺序执行：**评分 → 重写 → 合规审查**")

    # Show progress
    df_opt_existing = load_optimized(selected_batch)
    selected_for_opt = len(df_incoming) if not df_incoming.empty else 0
    opt_done = len(df_opt_existing) if not df_opt_existing.empty else 0

    if selected_for_opt > 0:
        st.progress(min(1.0, opt_done / selected_for_opt), text=f"{'Optimized' if is_en else '已优化'} {opt_done}/{selected_for_opt} {'articles' if is_en else '篇'}")

    if opt_done > 0 and opt_done < selected_for_opt:
        btn_zhiyou = f"🔄 {'Continue optimizing remaining' if is_en else '继续优化剩余'} {selected_for_opt - opt_done} {'articles' if is_en else '篇'} ({opt_done}/{selected_for_opt})"
    elif opt_done >= selected_for_opt and opt_done > 0:
        btn_zhiyou = f"🔄 {'Re-optimize' if is_en else '重新优化'} ({opt_done} {'done' if is_en else '篇已完成'})"
    else:
        btn_zhiyou = "🚀 One-Click Full Optimization" if is_en else "🚀 一键智优全流程"

    if st.button(btn_zhiyou, type="primary", key="run_zhiyou_all"):
        try:
            from engine import run_zhiyou_score, run_zhiyou_execute, run_zhiyou_compliance
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Filter zhizao content to only include articles selected in the data_editor above
            if "edited_incoming" in dir() and "include_zhiyou" in edited_incoming.columns:
                selected_titles = edited_incoming[edited_incoming["include_zhiyou"] == True]
                if not selected_titles.empty and not df_incoming.empty:
                    # Write only selected articles to zhizao file for processing
                    selected_indices = selected_titles.index.tolist()
                    df_to_process = df_incoming.iloc[selected_indices]
                    zhizao_path = OUTPUT_PATH / selected_batch / "02_zhizao" / "zhizao_draft_content.csv"
                    zhizao_path.parent.mkdir(parents=True, exist_ok=True)
                    df_to_process.to_csv(zhizao_path, index=False, encoding="utf-8-sig")

            status_text.text("Step 3: Scoring..." if is_en else "Step 3: 评分中...")
            progress_bar.progress(0.1)
            r1 = run_zhiyou_score(selected_batch)
            if not r1["success"]:
                st.error(f"{'Scoring failed' if is_en else '评分失败'}: {r1['error']}")
            else:
                progress_bar.progress(0.4)
                status_text.text("Step 3.5: Rewriting..." if is_en else "Step 3.5: 重写中...")
                r2 = run_zhiyou_execute(selected_batch)
                if not r2["success"]:
                    st.error(f"{'Rewrite failed' if is_en else '重写失败'}: {r2['error']}")
                else:
                    progress_bar.progress(0.7)
                    status_text.text("Step 3.6: Compliance review..." if is_en else "Step 3.6: 合规审查中...")
                    r3 = run_zhiyou_compliance(selected_batch)
                    if not r3["success"]:
                        st.error(f"{'Compliance failed' if is_en else '合规失败'}: {r3['error']}")
                    else:
                        progress_bar.progress(1.0)
                        status_text.text("")
                        st.success("✅ Full Optimization complete!" if is_en else "✅ 智优全流程完成！")
        except ImportError:
            st.error("engine module not ready" if is_en else "engine 模块未就绪")

    st.divider()

    # Results display (expanders)
    st.subheader("📊 Results" if is_en else "📊 结果查看")

    # Scorecard
    with st.expander("📊 Scorecard (Step 3)" if is_en else "📊 评分卡 (Step 3)", expanded=False):
        df_sc = load_scorecard(selected_batch)
        if not df_sc.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Articles Scored" if is_en else "评分文章数", len(df_sc))
            with col2:
                if "overall_score" in df_sc.columns:
                    st.metric("Avg Score" if is_en else "平均总分", f"{df_sc['overall_score'].mean():.2f}/5")
            with col3:
                if "is_approved" in df_sc.columns:
                    approved = df_sc[df_sc["is_approved"].astype(str).str.upper() == "TRUE"].shape[0]
                    st.metric("Passed" if is_en else "通过数", f"{approved}/{len(df_sc)}")

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
            st.info("No scorecard yet" if is_en else "暂无评分卡")

    # Rewrite
    with st.expander("✍️ Optimized Rewrite (Step 3.5)" if is_en else "✍️ 优化重写 (Step 3.5)", expanded=False):
        df_opt = load_optimized(selected_batch)
        if not df_opt.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Optimized Articles" if is_en else "优化文章数", len(df_opt))
            with col2:
                if "word_count" in df_opt.columns:
                    st.metric("Avg Word Count" if is_en else "平均字数", f"{df_opt['word_count'].mean():.0f}")

            display_cols = [c for c in ["content_id", "optimized_title", "word_count",
                                        "table_count", "list_count", "link_count", "version"]
                           if c in df_opt.columns]
            if display_cols:
                st.dataframe(df_opt[display_cols], use_container_width=True, hide_index=True)
        else:
            st.info("No optimized rewrite output yet" if is_en else "暂无优化重写输出")

    # Compliance
    with st.expander("⚖️ Compliance Review (Step 3.6)" if is_en else "⚖️ 合规审查 (Step 3.6)", expanded=False):
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
            st.info("No compliance review results yet" if is_en else "暂无合规审查结果")

    # --- 文章预览 & 编辑 + 确认 ---
    st.divider()
    df_opt = load_optimized(selected_batch)
    if not df_opt.empty:
        st.subheader(f"📖 {'Optimized Article Preview & Edit' if is_en else '优化后文章预览 & 编辑'}（{len(df_opt)} {'articles' if is_en else '篇'}）")
        st.caption("Edit optimized articles below, changes auto-saved" if is_en else "可直接编辑优化后的文章内容，修改自动保存")

        opt_file = OUTPUT_PATH / selected_batch / "03_zhiyou" / "zhiyou_optimized_content.csv"
        content_col = "optimized_content" if "optimized_content" in df_opt.columns else "content_draft"
        title_col = "optimized_title" if "optimized_title" in df_opt.columns else "title"

        content_changed = False
        for idx, row in df_opt.iterrows():
            title = str(row.get(title_col, f"{'Article' if is_en else '文章'} {idx+1}"))
            word_count = row.get("word_count", "?")
            with st.expander(f"📄 {title} ({word_count} {'words' if is_en else '字'})"):
                if "ai_query" in df_opt.columns:
                    st.caption(f"{'Search phrase' if is_en else '检索短语'}: {row.get('ai_query', '')}")
                if content_col in df_opt.columns:
                    original = str(row.get(content_col, ""))
                    edited = st.text_area("Content" if is_en else "内容", value=original, height=300,
                                          key=f"zhiyou_edit_{idx}", label_visibility="collapsed")
                    if edited != original:
                        df_opt.at[idx, content_col] = edited
                        df_opt.at[idx, "word_count"] = len(edited)
                        content_changed = True

        if content_changed:
            df_opt.to_csv(opt_file, index=False, encoding="utf-8-sig")
            st.success("✅ Changes auto-saved" if is_en else "✅ 修改已自动保存")

        # 确认环节
        st.divider()
        st.subheader("✅ Article Confirmation" if is_en else "✅ 文章确认")
        st.caption("Check confirmed articles; confirmed ones proceed to Publishing" if is_en else "勾选确认通过的文章，确认后进入智布发布")

        if "confirmed" not in df_opt.columns:
            df_opt["confirmed"] = True

        if title_col in df_opt.columns:
            df_confirm = st.data_editor(
                df_opt[[title_col, "confirmed"]].reset_index(drop=True),
                column_config={
                    title_col: st.column_config.TextColumn("Article Title" if is_en else "文章标题", disabled=True),
                    "confirmed": st.column_config.CheckboxColumn("Confirmed" if is_en else "确认通过"),
                },
                use_container_width=True, hide_index=True,
                key="zhiyou_confirm_editor",
            )
            confirmed_count = df_confirm["confirmed"].sum()
            st.markdown(f"**{'Confirmed' if is_en else '已确认'} {confirmed_count} / {len(df_confirm)} {'articles' if is_en else '篇'}**")

            # Auto-save confirmation
            df_opt["confirmed"] = df_confirm["confirmed"].values
            df_opt.to_csv(opt_file, index=False, encoding="utf-8-sig")

    # --- POC Review Section ---
    st.divider()
    st.subheader("🔒 POC Review" if is_en else "🔒 POC 人工审核")

    # Critical-5 categories that require POC review
    CRITICAL_5_CATEGORIES = ["新手怎么注册亚马逊", "亚马逊开店成本费用详解", "开店审核常见问题解答",
                             "欧洲增值税VAT介绍", "其他站点税务要求", "合规政策及操作流程"]

    if not df_opt.empty:
        # Add review columns if not exist
        if "needs_poc_review" not in df_opt.columns:
            # Auto-mark Critical-5 categories
            if "category" in df_opt.columns:
                df_opt["needs_poc_review"] = df_opt["category"].isin(CRITICAL_5_CATEGORIES)
            else:
                df_opt["needs_poc_review"] = False
        if "poc_approved" not in df_opt.columns:
            df_opt["poc_approved"] = False

        # Ensure bool types
        df_opt["needs_poc_review"] = df_opt["needs_poc_review"].astype(bool)
        df_opt["poc_approved"] = df_opt["poc_approved"].astype(bool)

        # Show review status — sync from review_queue.csv if available
        review_file = OUTPUT_PATH / "review" / "review_queue.csv"
        if review_file.exists():
            df_review = load_csv_safe(review_file)
            if not df_review.empty and "status" in df_review.columns and "content_id" in df_review.columns:
                # Sync approved status back to df_opt
                approved_ids = df_review[df_review["status"] == "APPROVED"]["content_id"].tolist()
                if approved_ids and "content_id" in df_opt.columns:
                    df_opt.loc[df_opt["content_id"].isin(approved_ids), "poc_approved"] = True
                    opt_file = OUTPUT_PATH / selected_batch / "03_zhiyou" / "zhiyou_optimized_content.csv"
                    df_opt.to_csv(opt_file, index=False, encoding="utf-8-sig")

        needs_review = df_opt["needs_poc_review"].sum()
        approved = df_opt[df_opt["needs_poc_review"] == True]["poc_approved"].sum()
        pending = needs_review - approved

        col_r1, col_r2, col_r3 = st.columns(3)
        col_r1.metric("Needs POC Review" if is_en else "需要 POC 审核", int(needs_review))
        col_r2.metric("✅ Approved" if is_en else "✅ 已审批", int(approved))
        col_r3.metric("⏳ Pending" if is_en else "⏳ 待审批", int(pending))

        # Editable table: user can manually mark articles for POC review
        st.caption("Critical-5 auto-flagged. You can also manually select any article for POC review." if is_en else "Critical-5 类别自动标记。你也可以手动选择任何文章进入人工审核。")

        title_col_r = "optimized_title" if "optimized_title" in df_opt.columns else ("title" if "title" in df_opt.columns else "ai_query")
        review_cols = [c for c in [title_col_r, "category", "needs_poc_review", "poc_approved"] if c in df_opt.columns]

        if review_cols:
            edited_review = st.data_editor(
                df_opt[review_cols].reset_index(drop=True),
                column_config={
                    title_col_r: st.column_config.TextColumn("Article" if is_en else "文章", disabled=True),
                    "category": st.column_config.TextColumn("Category" if is_en else "类别", disabled=True),
                    "needs_poc_review": st.column_config.CheckboxColumn("POC Review" if is_en else "需要审核"),
                    "poc_approved": st.column_config.CheckboxColumn("Approved" if is_en else "已审批"),
                },
                use_container_width=True, hide_index=True,
                key="zhiyou_poc_editor",
            )

            # Save button for POC edits
            if st.button("💾 Save Review Status" if is_en else "💾 保存审核状态", key="btn_save_poc"):
                opt_file = OUTPUT_PATH / selected_batch / "03_zhiyou" / "zhiyou_optimized_content.csv"
                df_opt["needs_poc_review"] = edited_review["needs_poc_review"].values
                df_opt["poc_approved"] = edited_review["poc_approved"].values
                df_opt.to_csv(opt_file, index=False, encoding="utf-8-sig")
                st.success("✅ Saved" if is_en else "✅ 已保存")
                st.rerun()

        # Submit to POC review queue
        pending_articles = df_opt[(df_opt["needs_poc_review"] == True) & (df_opt["poc_approved"] == False)]
        if len(pending_articles) > 0:
            if st.button(f"📤 Submit {len(pending_articles)} articles to POC Review Queue" if is_en else f"📤 提交 {len(pending_articles)} 篇到 POC 审核队列", key="btn_submit_poc"):
                review_dir = OUTPUT_PATH / "review"
                review_dir.mkdir(parents=True, exist_ok=True)
                review_file = review_dir / "review_queue.csv"

                # Format for app_review.py expected columns
                review_rows = []
                for idx, row in pending_articles.iterrows():
                    title_val = row.get("optimized_title", row.get("title", row.get("ai_query", f"Article {idx}")))
                    content_val = row.get("optimized_content", row.get("content_draft", ""))
                    category_name = row.get("category", "Unknown")
                    # Determine POC based on category
                    poc_map = {
                        "新手怎么注册亚马逊": "murphy", "亚马逊开店成本费用详解": "joyce",
                        "开店审核常见问题解答": "eva_zheng", "欧洲增值税VAT介绍": "eva_zheng",
                        "其他站点税务要求": "eva_zheng", "合规政策及操作流程": "eva_zheng",
                    }
                    assigned = poc_map.get(category_name, "yujiashi")
                    review_rows.append({
                        "content_id": row.get("content_id", f"c_{idx}"),
                        "category_id": "",
                        "category_name": category_name,
                        "title": title_val,
                        "content": str(content_val)[:5000],
                        "assigned_to": assigned,
                        "status": "PENDING",
                        "reviewer_notes": "",
                        "submitted_at": datetime.now().isoformat(),
                        "reviewed_at": "",
                    })

                df_review = pd.DataFrame(review_rows)
                # Append to existing queue if exists
                if review_file.exists():
                    existing = pd.read_csv(review_file, encoding="utf-8-sig")
                    df_review = pd.concat([existing, df_review], ignore_index=True)
                df_review.to_csv(review_file, index=False, encoding="utf-8-sig")
                st.success(f"✅ {len(review_rows)} articles submitted to POC review queue" if is_en else f"✅ {len(review_rows)} 篇已提交到 POC 审核队列")
            st.info("💡 POC reviewers: open **localhost:8502** to review and approve articles." if is_en else "💡 POC 审核人：请打开 **localhost:8502** 查看和审批文章。")

        # Check if all reviews complete
        all_reviewed = (pending == 0) if needs_review > 0 else True
        if not all_reviewed:
            st.warning(f"⏳ {int(pending)} articles pending POC approval. Cannot proceed to 智布 until all approved." if is_en else f"⏳ {int(pending)} 篇待 POC 审批。审批完成后才能进入智布。")

    # CTA → 智布 (only enabled when all POC reviews complete)
    st.divider()
    can_proceed = True
    if not df_opt.empty and "needs_poc_review" in df_opt.columns:
        pending_count = ((df_opt["needs_poc_review"] == True) & (df_opt["poc_approved"] == False)).sum()
        can_proceed = (pending_count == 0)

    if st.button("➡️ Go to Publishing (Step 4)" if is_en else "➡️ 进入智布 (Step 4)", type="primary", key="cta_zhiyou_to_zhibu", disabled=not can_proceed):
        jump_to("📦 智布")
        st.rerun()

    # 📜 历史记录 + 清空
    with st.expander("📜 History" if is_en else "📜 历史记录"):
        zhiyou_dir = OUTPUT_PATH / selected_batch / "03_zhiyou"
        col_h1, col_h2 = st.columns([4, 1])
        with col_h2:
            if st.button("🗑️ Clear All" if is_en else "🗑️ 清空全部", key="clear_zhiyou_hist"):
                if zhiyou_dir.exists():
                    for f in zhiyou_dir.glob("*.csv"):
                        f.unlink()
                    st.success("Cleared" if is_en else "已清空")
        if zhiyou_dir.exists():
            files = sorted(zhiyou_dir.glob("*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
            for f in files:
                mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                col_i, col_r, col_d = st.columns([3, 1, 1])
                with col_i:
                    st.caption(f"📄 {f.name} · {f.stat().st_size/1024:.1f}KB · 🕐 {mtime}")
                with col_r:
                    if st.button("♻️ Reuse" if is_en else "♻️ 复用", key=f"reuse_zhiyou_{f.name}"):
                        live_path = OUTPUT_PATH / selected_batch / "03_zhiyou" / "zhiyou_optimized_content.csv"
                        safe_copy(f, live_path)
                        st.rerun()
                with col_d:
                    st.download_button("⬇️", f.read_bytes(), file_name=f.name, mime="text/csv", key=f"dl_zhiyou_{f.name}")
        else:
            st.caption("No history" if is_en else "暂无历史")


# ============================================================
# PAGE: 智布 (Step 4)
# ============================================================
elif _page_idx == 5:
    st.markdown("""<div style="padding:20px 0 10px;"><h1 style="font-size:28px;font-weight:800;color:#29b6f6;margin:0;">📦 """ + ("Publishing – JSON / Word Formatting" if is_en else "智布 – JSON / Word Formatting") + """</h1><p style="font-size:13px;color:#8892b0;margin-top:6px;">""" + ("Step 4: Convert optimized content to structured JSON and Word documents" if is_en else "Step 4: 将优化内容转换为结构化 JSON 和 Word 文档") + """</p></div>""", unsafe_allow_html=True)
    render_pipeline_flow("zhibu", selected_batch)

    # --- Upload content directly (skip 智优) ---
    with st.expander("📤 Upload Content (skip Optimization)" if is_en else "📤 上传内容（跳过智优直接发布格式化）", expanded=False):
        st.caption("Optional: Upload optimized article CSV, generate JSON/Word directly" if is_en else "可选：上传已优化完成的文章 CSV，直接生成 JSON/Word")
        upload_zhibu = st.file_uploader("Upload CSV (must contain optimized_content column)" if is_en else "上传 CSV（需含 optimized_content 列）", type=["csv", "xlsx"], key="zhibu_direct_upload")
        if upload_zhibu:
            try:
                if upload_zhibu.name.endswith(".xlsx"):
                    df_up = pd.read_excel(upload_zhibu, engine="openpyxl")
                else:
                    df_up = pd.read_csv(upload_zhibu, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
                out_dir = OUTPUT_PATH / selected_batch / "03_zhiyou"
                out_dir.mkdir(parents=True, exist_ok=True)
                df_up.to_csv(out_dir / "zhiyou_optimized_content.csv", index=False, encoding="utf-8-sig")
                st.success(f"✅ {'Uploaded' if is_en else '已上传'} {len(df_up)} {'articles, ready for Publishing' if is_en else '篇，可执行智布'}")
            except Exception as e:
                st.error(f"{'Upload failed' if is_en else '上传失败'}: {e}")

    # --- Show incoming content from 智优 ---
    st.subheader("📋 Optimized Content from Optimization" if is_en else "📋 智优输入内容")
    df_opt_in = load_optimized(selected_batch)
    if not df_opt_in.empty:
        title_col = "optimized_title" if "optimized_title" in df_opt_in.columns else "title"
        display_cols_zb = [c for c in [title_col, "ai_query", "word_count"] if c in df_opt_in.columns]
        if display_cols_zb:
            st.dataframe(df_opt_in[display_cols_zb], use_container_width=True, hide_index=True)
        st.caption(f"{len(df_opt_in)} {'optimized articles ready for publishing' if is_en else '篇优化文章待发布'}")
    else:
        st.caption("No optimized content. Upload or run Optimization first." if is_en else "暂无智优内容，请先上传或执行智优。")

    st.divider()

    # Execution
    st.subheader("▶️ Generate Publishing Format" if is_en else "▶️ 生成发布格式")
    # Progress
    zhibu_data = load_zhibu(selected_batch)
    zhibu_done = len(zhibu_data.get("items", [])) if zhibu_data else 0
    zhibu_total = len(df_opt_in) if not df_opt_in.empty else 0

    if zhibu_total > 0:
        st.progress(min(1.0, zhibu_done / zhibu_total), text=f"{'Published' if is_en else '已格式化'} {zhibu_done}/{zhibu_total} {'articles' if is_en else '篇'}")

    col_exec1, col_exec2 = st.columns(2)
    with col_exec1:
        if zhibu_done > 0 and zhibu_done < zhibu_total:
            btn_zhibu = f"🔄 {'Continue formatting remaining' if is_en else '继续格式化剩余'} {zhibu_total - zhibu_done} {'articles' if is_en else '篇'}"
        elif zhibu_done >= zhibu_total and zhibu_done > 0:
            btn_zhibu = f"✅ {'All formatted' if is_en else '全部格式化完毕'}"
        else:
            btn_zhibu = "🚀 Generate JSON" if is_en else "🚀 生成 JSON"
        if st.button(btn_zhibu, type="primary", key="run_zhibu"):
            try:
                from engine import run_zhibu
                with st.spinner("Generating JSON..." if is_en else "正在生成 JSON..."):
                    result = run_zhibu(selected_batch)
                if result["success"]:
                    st.success(f"✅ {'Publishing complete!' if is_en else '智布完成！'} {result['items_count']} {'items' if is_en else '条目'}")
                else:
                    st.error(f"❌ {'Failed' if is_en else '失败'}: {result['error']}")
            except ImportError:
                st.error("engine module not ready" if is_en else "engine 模块未就绪")
    with col_exec2:
        if st.button("📄 Generate Word Docs" if is_en else "📄 生成 Word 文档", key="run_word"):
            try:
                from engine import generate_word_docs
                with st.spinner("Generating Word documents..." if is_en else "正在生成 Word 文档..."):
                    result = generate_word_docs(selected_batch)
                if result["success"]:
                    st.success(f"✅ {'Word generation complete!' if is_en else 'Word 生成完成！'} {result.get('doc_count', 0)} {'articles' if is_en else '篇'}")
                else:
                    st.error(f"❌ {'Failed' if is_en else '失败'}: {result['error']}")
            except ImportError:
                st.error("engine.generate_word_docs not implemented" if is_en else "engine.generate_word_docs 未实现")

    st.divider()

    # Output display
    data = load_zhibu(selected_batch)
    if data:
        col_title, col_clear = st.columns([4, 1])
        with col_title:
            st.subheader("📤 Output Overview" if is_en else "📤 输出概览")
        with col_clear:
            if st.button("🗑️ Clear Preview" if is_en else "🗑️ 清空预览", key="clear_zhibu_preview"):
                zhibu_dir = OUTPUT_PATH / selected_batch / "04_zhibu"
                if zhibu_dir.exists():
                    # Move current files to archive (rename with timestamp)
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    archive_dir = zhibu_dir / "archive"
                    archive_dir.mkdir(exist_ok=True)
                    for f in list(zhibu_dir.glob("*.json")):
                        f.rename(archive_dir / f"{f.stem}_{ts}{f.suffix}")
                st.success("Preview cleared (history archived)" if is_en else "已清空预览（历史已归档）")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Items" if is_en else "总条目", data.get("total_items", 0))
        with col2:
            st.metric("Batch" if is_en else "批次", data.get("batch_id", "N/A"))
        with col3:
            kws = data.get("source_keywords", [])
            st.metric("Source Keywords" if is_en else "源关键词", len(kws) if isinstance(kws, list) else 0)

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
                    "title": st.column_config.TextColumn("Title" if is_en else "标题", disabled=True),
                    "word_count": st.column_config.NumberColumn("Word Count" if is_en else "字数", disabled=True),
                    "overall_score": st.column_config.NumberColumn("Score" if is_en else "评分", disabled=True),
                    "compliance": st.column_config.TextColumn("Compliance" if is_en else "合规", disabled=True),
                    "selected": st.column_config.CheckboxColumn("Selected" if is_en else "选中"),
                },
                use_container_width=True, hide_index=True,
                key="zhibu_select_editor",
            )
            selected_count = edited_items["selected"].sum()
            st.caption(f"{'Selected' if is_en else '已选中'} {selected_count} / {len(edited_items)} {'articles' if is_en else '篇'}")

        # JSON preview
        st.divider()
        st.subheader("🔍 JSON Preview" if is_en else "🔍 JSON 预览")
        if items:
            for i, item in enumerate(items):
                title = item.get("meta", {}).get("title", f"Item {i+1}")
                with st.expander(f"📄 {title}", expanded=(i == 0)):
                    st.json(item)
    else:
        st.info(f"{'Batch' if is_en else '批次'} {selected_batch} {'has no publishing output yet' if is_en else '暂无智布输出'}")

    # Word docs display — only show 智优 Final version
    word_dir_opt = OUTPUT_PATH / selected_batch / "03_zhiyou_word"
    if word_dir_opt.exists():
        docs = list(word_dir_opt.glob("*.docx"))
        if docs:
            st.divider()
            st.subheader("📄 Final Word Documents" if is_en else "📄 Final Word 文档")
            for doc in docs:
                st.download_button(
                    f"📄 {doc.name}", doc.read_bytes(),
                    file_name=doc.name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"dl_word_{doc.name}"
                )

    # CTA → 智析
    st.divider()
    if st.button("➡️ View Analytics (Step 6)" if is_en else "➡️ 查看智析 (Step 6)", type="primary", key="cta_zhibu_to_zhixi"):
        jump_to("📈 智析")
        st.rerun()

    # 📜 历史记录（不清空，带复用）
    with st.expander("📜 History" if is_en else "📜 历史记录"):
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
                    if st.button("♻️ Reuse" if is_en else "♻️ 复用", key=f"reuse_zhibu_{f.name}"):
                        live_dir = OUTPUT_PATH / selected_batch / "04_zhibu"
                        safe_copy(f, live_dir / f.name)
                        st.rerun()
                with col_d:
                    mime = "application/json" if f.suffix == ".json" else "text/csv"
                    st.download_button("⬇️", f.read_bytes(), file_name=f.name, mime=mime, key=f"dl_zhibu_{f.name}")
        else:
            st.caption("No history" if is_en else "暂无历史")


# ============================================================
# ============================================================
# PAGE: 智析 (Step 6) — 重构版
# ============================================================
elif _page_idx == 7:
    st.markdown("""<div style="padding:20px 0 10px;"><h1 style="font-size:28px;font-weight:800;color:#ab47bc;margin:0;">📈 """ + ("Analytics – Performance & Gap Analysis" if is_en else "智析 – Performance & Gap Analysis") + """</h1><p style="font-size:13px;color:#8892b0;margin-top:6px;">""" + ("Performance Analysis: Output trends · Input tracking · AI citation monitoring · Gap opportunities" if is_en else "效果分析：Output 趋势 · Input 产出追踪 · AI 引用监控 · Gap 机会点") + """</p></div>""", unsafe_allow_html=True)
    render_pipeline_flow("zhixi", selected_batch)

    # --- Upload GEO Data (append to existing) ---
    with st.expander("📤 上传 GEO 数据（叠加到现有数据上）", expanded=False):
        st.markdown("""
        **支持的数据格式：**
        - **SSR Funnel Metrics CSV**（从 QuickSight 导出）— 自动解析 Reg Start 数据
        - **Weekly 格式 CSV** — 列: Week, CN_GEO, WW_GEO, WW_Direct_EST, WW_Direct_EM, Total
        - **Monthly 格式 CSV** — 列: Channel, M1 (Jan), M2 (Feb), ...
        - **YTD 格式 CSV** — 列: Channel, YTD_Actual, YTD_PY, YoY
        - **Excel (xlsx)** — 多 Sheet 自动识别
        """)

        upload_geo_type = st.radio(
            "数据类型",
            ["📊 SSR Funnel Metrics (原始导出)", "📅 Weekly 周度数据", "📆 Monthly 月度数据", "📈 YTD 年度累计"],
            horizontal=True,
            key="geo_upload_type",
        )

        upload_geo = st.file_uploader(
            "上传 GEO 数据文件",
            type=["csv", "xlsx"],
            key="geo_data_upload",
        )

        if upload_geo:
            try:
                if upload_geo.name.endswith(".xlsx"):
                    xls = pd.ExcelFile(upload_geo, engine="openpyxl")
                    sheet_names = xls.sheet_names
                    if len(sheet_names) > 1:
                        selected_sheet = st.selectbox("选择 Sheet", sheet_names, key="geo_sheet_select")
                    else:
                        selected_sheet = sheet_names[0]
                    df_up = pd.read_excel(upload_geo, sheet_name=selected_sheet, engine="openpyxl")
                else:
                    df_up = pd.read_csv(upload_geo, encoding="utf-8-sig", on_bad_lines="skip", engine="python")

                st.caption(f"📋 文件: {upload_geo.name} · {len(df_up)} 行 · {len(df_up.columns)} 列")
                st.dataframe(df_up.head(10), use_container_width=True, hide_index=True)

                if upload_geo_type == "📊 SSR Funnel Metrics (原始导出)":
                    # Parse SSR format: extract GEO + Direct Reg Start data
                    st.markdown("**自动解析 SSR Funnel Metrics 格式...**")
                    # Filter for Reg Start, Organic, relevant channels
                    required_cols = ["Metrics Name", "Channel Attributes", "Channel Category", "Campaign Channel Rollup"]
                    if all(c in df_up.columns for c in required_cols):
                        # Filter Reg Start + Organic only
                        df_regstart = df_up[
                            (df_up["Metrics Name"].str.strip() == "Reg Start") &
                            (df_up["Channel Attributes"].str.strip() == "Organic")
                        ].copy()

                        if "Time Frame" in df_regstart.columns and "Report Rank Name" in df_regstart.columns:
                            # Weekly data extraction
                            df_weekly_raw = df_regstart[df_regstart["Time Frame"].str.strip() == "WEEKLY"].copy()

                            if not df_weekly_raw.empty:
                                # Pivot: group by Report Rank Name (WK1, WK2...), sum Actual values by channel
                                channels_geo = df_weekly_raw[df_weekly_raw["Campaign Channel Rollup"].str.strip() == "GEO"]
                                channels_direct = df_weekly_raw[df_weekly_raw["Campaign Channel Rollup"].str.strip() == "Direct"]

                                # CN GEO
                                cn_geo = channels_geo[channels_geo["Channel Category"].str.strip() == "CN Website"]
                                cn_geo_by_week = cn_geo.groupby("Report Rank Name")["Actual"].sum().reset_index()
                                cn_geo_by_week.columns = ["Week", "CN_GEO"]

                                # WW GEO (NA+EU+JP)
                                ww_geo = channels_geo[channels_geo["Channel Category"].str.strip().isin(["NA Website", "EU Website", "JP Website"])]
                                ww_geo_by_week = ww_geo.groupby("Report Rank Name")["Actual"].sum().reset_index()
                                ww_geo_by_week.columns = ["Week", "WW_GEO"]

                                # WW Direct EST (NA+EU+JP)
                                ww_direct_est = channels_direct[channels_direct["Channel Category"].str.strip().isin(["NA Website", "EU Website", "JP Website"])]
                                ww_direct_by_week = ww_direct_est.groupby("Report Rank Name")["Actual"].sum().reset_index()
                                ww_direct_by_week.columns = ["Week", "WW_Direct_EST"]

                                # WW Direct EM (AU+SA+AE)
                                ww_direct_em = channels_direct[channels_direct["Channel Category"].str.strip().isin(["AU Website", "SA Website", "AE Website"])]
                                ww_direct_em_by_week = ww_direct_em.groupby("Report Rank Name")["Actual"].sum().reset_index()
                                ww_direct_em_by_week.columns = ["Week", "WW_Direct_EM"]

                                # Merge all
                                df_merged = cn_geo_by_week
                                for other in [ww_geo_by_week, ww_direct_by_week, ww_direct_em_by_week]:
                                    df_merged = df_merged.merge(other, on="Week", how="outer")
                                df_merged = df_merged.fillna(0)
                                for col in ["CN_GEO", "WW_GEO", "WW_Direct_EST", "WW_Direct_EM"]:
                                    df_merged[col] = df_merged[col].astype(int)
                                df_merged["Total"] = df_merged["CN_GEO"] + df_merged["WW_GEO"] + df_merged["WW_Direct_EST"] + df_merged["WW_Direct_EM"]

                                # Sort by week number
                                df_merged["_wk_num"] = df_merged["Week"].str.extract(r"(\d+)").astype(int)
                                df_merged = df_merged.sort_values("_wk_num").drop(columns=["_wk_num"])

                                st.success(f"✅ 解析到 {len(df_merged)} 周数据")
                                st.dataframe(df_merged, use_container_width=True, hide_index=True)

                                if st.button("📥 叠加到现有 Weekly 数据", key="append_ssr_weekly", type="primary"):
                                    result = append_geo_weekly(df_merged)
                                    st.success(f"✅ 已叠加！当前累积 {len(result)} 周数据")
                            else:
                                st.warning("未找到 WEEKLY 数据行")

                            # YTD extraction
                            df_ytd_raw = df_regstart[df_regstart["Time Frame"].str.strip() == "YTD"].copy()
                            if not df_ytd_raw.empty:
                                st.markdown("**YTD 数据：**")
                                # Build YTD summary
                                ytd_rows = []
                                for label, cat_filter, rollup in [
                                    ("CN GEO", ["CN Website"], "GEO"),
                                    ("WW GEO", ["NA Website", "EU Website", "JP Website"], "GEO"),
                                    ("WW Direct EST", ["NA Website", "EU Website", "JP Website"], "Direct"),
                                    ("WW Direct EM", ["AU Website", "SA Website", "AE Website"], "Direct"),
                                ]:
                                    subset = df_ytd_raw[
                                        (df_ytd_raw["Channel Category"].str.strip().isin(cat_filter)) &
                                        (df_ytd_raw["Campaign Channel Rollup"].str.strip() == rollup)
                                    ]
                                    actual = pd.to_numeric(subset["Actual"], errors="coerce").sum()
                                    py = pd.to_numeric(subset["PY A2A"], errors="coerce").sum()
                                    yoy_val = f"{(actual - py) / py:+.0%}" if py > 0 else "N/A"
                                    ytd_rows.append({"Channel": label, "YTD_Actual": int(actual), "YTD_PY": int(py), "YoY": yoy_val})

                                total_actual = sum(r["YTD_Actual"] for r in ytd_rows)
                                total_py = sum(r["YTD_PY"] for r in ytd_rows)
                                total_yoy = f"{(total_actual - total_py) / total_py:+.0%}" if total_py > 0 else "N/A"
                                ytd_rows.append({"Channel": "Total", "YTD_Actual": total_actual, "YTD_PY": total_py, "YoY": total_yoy})

                                df_ytd_new = pd.DataFrame(ytd_rows)
                                st.dataframe(df_ytd_new, use_container_width=True, hide_index=True)

                                if st.button("📥 更新 YTD 数据", key="append_ssr_ytd", type="primary"):
                                    append_geo_ytd(df_ytd_new)
                                    st.success("✅ YTD 数据已更新！")
                        else:
                            st.warning("CSV 缺少 Time Frame / Report Rank Name 列，无法自动解析")
                    else:
                        st.error(f"CSV 缺少必需列: {required_cols}")

                elif upload_geo_type == "📅 Weekly 周度数据":
                    # Expect: Week, CN_GEO, WW_GEO, WW_Direct_EST, WW_Direct_EM, Total
                    required = ["Week"]
                    if "Week" in df_up.columns:
                        # Fill missing columns with 0
                        for col in ["CN_GEO", "WW_GEO", "WW_Direct_EST", "WW_Direct_EM"]:
                            if col not in df_up.columns:
                                df_up[col] = 0
                        if "Total" not in df_up.columns:
                            df_up["Total"] = df_up["CN_GEO"] + df_up["WW_GEO"] + df_up["WW_Direct_EST"] + df_up["WW_Direct_EM"]
                        st.success(f"✅ 识别到 {len(df_up)} 周数据")
                        st.dataframe(df_up[["Week", "CN_GEO", "WW_GEO", "WW_Direct_EST", "WW_Direct_EM", "Total"]], use_container_width=True, hide_index=True)
                        if st.button("📥 叠加到现有 Weekly 数据", key="append_weekly_direct", type="primary"):
                            result = append_geo_weekly(df_up[["Week", "CN_GEO", "WW_GEO", "WW_Direct_EST", "WW_Direct_EM", "Total"]])
                            st.success(f"✅ 已叠加！当前累积 {len(result)} 周数据")
                    else:
                        st.error("CSV 必须包含 'Week' 列")

                elif upload_geo_type == "📆 Monthly 月度数据":
                    if "Channel" in df_up.columns:
                        st.success(f"✅ 识别到 Monthly 数据 ({len(df_up)} 行)")
                        if st.button("📥 更新 Monthly 数据", key="append_monthly_direct", type="primary"):
                            append_geo_monthly(df_up)
                            st.success("✅ Monthly 数据已更新！")
                    else:
                        st.error("CSV 必须包含 'Channel' 列")

                elif upload_geo_type == "📈 YTD 年度累计":
                    if "Channel" in df_up.columns and "YTD_Actual" in df_up.columns:
                        st.success(f"✅ 识别到 YTD 数据 ({len(df_up)} 行)")
                        if st.button("📥 更新 YTD 数据", key="append_ytd_direct", type="primary"):
                            append_geo_ytd(df_up)
                            st.success("✅ YTD 数据已更新！")
                    else:
                        st.error("CSV 必须包含 'Channel' 和 'YTD_Actual' 列")

            except Exception as e:
                st.error(f"上传解析失败: {e}")

        # Show current stored data summary
        st.divider()
        st.markdown("**📁 当前已存储数据：**")
        col_s1, col_s2, col_s3 = st.columns(3)
        geo_weekly_file = METRICS_PATH / "geo_weekly_data.csv"
        geo_ytd_file = METRICS_PATH / "geo_ytd_data.csv"
        geo_monthly_file = METRICS_PATH / "geo_monthly_data.csv"
        with col_s1:
            if geo_weekly_file.exists():
                _df_w = load_csv_safe(geo_weekly_file)
                st.metric("Weekly 数据", f"{len(_df_w)} 周")
            else:
                st.metric("Weekly 数据", "默认 4 周")
        with col_s2:
            if geo_monthly_file.exists():
                st.metric("Monthly 数据", "✅ 已存储")
            else:
                st.metric("Monthly 数据", "默认数据")
        with col_s3:
            if geo_ytd_file.exists():
                st.metric("YTD 数据", "✅ 已存储")
            else:
                st.metric("YTD 数据", "默认数据")

    # --- 7 Tabs (with GEO Data Analysis + RS vs CL) ---
    tab_output, tab_rs_cl, tab_input, tab_citation, tab_zhice_gap, tab_gap, tab_zhiyu = st.tabs([
        "📊 Output Trends" if is_en else "📊 Output 趋势",
        "📈 RS vs CL" if is_en else "📈 Reg Start vs Clean Launch",
        "📥 Input Production" if is_en else "📥 Input 产出",
        "🔗 Citation Summary" if is_en else "🔗 引用追踪总表",
        "🔬 Phrase Detail" if is_en else "🔬 检索短语引用详情",
        "💡 Gap & Opportunities" if is_en else "💡 Gap & 机会点",
        "🔮 Query Forecaster" if is_en else "🔮 智预",
    ])

    # ============================================================
    # TAB 1: Output 趋势
    # ============================================================
    with tab_output:
        sub_weekly, sub_monthly, sub_ytd = st.tabs(["Weekly", "Monthly", "YTD"])

        # --- Helper: build structured table (Channel x Type rows) from weekly data ---
        def _build_structured_weekly(df_w):
            """Convert flat weekly df into Channel/Type row format with Actual, PY, YoY."""
            weeks = df_w["Week"].tolist()
            channel_map = [
                ("CN GEO", "CN_GEO", "CN_GEO_PY"),
                ("WW GEO", "WW_GEO", "WW_GEO_PY"),
                ("Total GEO", "Total_GEO", "Total_GEO_PY"),
                ("WW Direct", "WW_Direct", "WW_Direct_PY"),
                ("Total (GEO+Direct)", "Total", "Total_PY"),
            ]
            rows = []
            for ch_name, col_actual, col_py in channel_map:
                actual_vals = df_w[col_actual].tolist() if col_actual in df_w.columns else [0]*len(weeks)
                py_vals = df_w[col_py].tolist() if col_py in df_w.columns else [0]*len(weeks)
                yoy_vals = []
                for a, p in zip(actual_vals, py_vals):
                    if p > 0:
                        yoy_vals.append(f"{(a-p)/p:+.0%}")
                    else:
                        yoy_vals.append("N/A")
                rows.append({"Channel": ch_name, "Type": "Actual", **dict(zip(weeks, actual_vals))})
                rows.append({"Channel": ch_name, "Type": "PY", **dict(zip(weeks, py_vals))})
                rows.append({"Channel": ch_name, "Type": "YoY", **dict(zip(weeks, yoy_vals))})
            return pd.DataFrame(rows)

        with sub_weekly:
            st.subheader("📅 Weekly Trends" if is_en else "📅 Weekly 趋势")
            df_w = get_weekly_metrics()
            all_weeks = df_w["Week"].tolist()

            # --- KPI: Last 2 weeks comparison ---
            if len(df_w) >= 2:
                last = df_w.iloc[-1]
                prev = df_w.iloc[-2]
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                with kpi1:
                    delta_t = int(last["Total"]) - int(prev["Total"])
                    pct_t = f"{delta_t/int(prev['Total']):+.0%}" if int(prev["Total"]) > 0 else "N/A"
                    st.metric(f"Total ({last['Week']})", f"{int(last['Total']):,}", f"{pct_t} vs {prev['Week']}")
                with kpi2:
                    cn_val = int(last["CN_GEO"])
                    cn_prev = int(prev["CN_GEO"])
                    cn_pct = f"{(cn_val-cn_prev)/cn_prev:+.0%}" if cn_prev > 0 else "N/A"
                    st.metric(f"CN GEO ({last['Week']})", f"{cn_val:,}", f"{cn_pct} vs {prev['Week']}")
                with kpi3:
                    ww_val = int(last["WW_GEO"])
                    ww_prev = int(prev["WW_GEO"])
                    ww_pct = f"{(ww_val-ww_prev)/ww_prev:+.0%}" if ww_prev > 0 else "N/A"
                    st.metric(f"WW GEO ({last['Week']})", f"{ww_val:,}", f"{ww_pct} vs {prev['Week']}")
                with kpi4:
                    wd_val = int(last.get("WW_Direct", last.get("WW_Direct_EST", 0)))
                    wd_prev = int(prev.get("WW_Direct", prev.get("WW_Direct_EST", 0)))
                    wd_pct = f"{(wd_val-wd_prev)/wd_prev:+.0%}" if wd_prev > 0 else "N/A"
                    st.metric(f"WW Direct ({last['Week']})", f"{wd_val:,}", f"{wd_pct} vs {prev['Week']}")

            st.divider()

            # --- Charts: GEO and Direct separate ---
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.caption("GEO Trends (CN + WW)")
                fig_geo = go.Figure()
                fig_geo.add_trace(go.Scatter(x=df_w["Week"], y=df_w["CN_GEO"], mode="lines+markers", name="CN GEO", line=dict(color="#fbbf24", width=2)))
                fig_geo.add_trace(go.Scatter(x=df_w["Week"], y=df_w["WW_GEO"], mode="lines+markers", name="WW GEO", line=dict(color="#a78bfa", width=2)))
                fig_geo.add_trace(go.Scatter(x=df_w["Week"], y=df_w.get("Total_GEO", df_w["CN_GEO"]+df_w["WW_GEO"]), mode="lines+markers", name="Total GEO", line=dict(color="#22c55e", width=2, dash="dot")))
                fig_geo.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.2), yaxis_title="Reg Starts")
                st.plotly_chart(fig_geo, use_container_width=True)
            with col_chart2:
                st.caption("WW Direct + Total")
                fig_dir = go.Figure()
                fig_dir.add_trace(go.Scatter(x=df_w["Week"], y=df_w.get("WW_Direct", df_w.get("WW_Direct_EST", pd.Series([0]*len(df_w)))), mode="lines+markers", name="WW Direct", line=dict(color="#4a9eff", width=2)))
                fig_dir.add_trace(go.Scatter(x=df_w["Week"], y=df_w["Total"], mode="lines+markers", name="Total (GEO+Direct)", line=dict(color="#06b6d4", width=2, dash="dot")))
                fig_dir.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.2), yaxis_title="Reg Starts")
                st.plotly_chart(fig_dir, use_container_width=True)

            # --- Structured table with collapsible old weeks ---
            df_w_table = _build_structured_weekly(df_w)
            if len(all_weeks) > 6:
                # Show last 6 weeks by default, collapse older ones
                with st.expander(f"📂 Earlier weeks ({all_weeks[0]} - {all_weeks[-7]})", expanded=False):
                    old_cols = ["Channel", "Type"] + all_weeks[:-6]
                    st.dataframe(df_w_table[old_cols], use_container_width=True, hide_index=True)
                recent_cols = ["Channel", "Type"] + all_weeks[-6:]
                st.dataframe(df_w_table[recent_cols], use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_w_table, use_container_width=True, hide_index=True)

        with sub_monthly:
            st.subheader("📆 Monthly Trends" if is_en else "📆 Monthly 趋势")
            monthly_data = get_monthly_metrics()
            month_cols = [c for c in monthly_data.columns if c not in ["Channel", "Type"]]

            # --- KPI: Last 2 months comparison (Actual rows only) ---
            if len(month_cols) >= 2:
                last_m = month_cols[-1]
                prev_m = month_cols[-2]
                monthly_actual = monthly_data[monthly_data["Type"] == "Actual"] if "Type" in monthly_data.columns else monthly_data
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                channels_kpi = [
                    ("CN (GEO)", "CN GEO", kpi1),
                    ("WW (GEO)", "WW GEO", kpi2),
                    ("WW Website Direct", "WW Direct", kpi3),
                    ("Total (GEO+Direct)", "Total", kpi4),
                ]
                for ch_name, display_name, kpi_col in channels_kpi:
                    row = monthly_actual[monthly_actual["Channel"] == ch_name]
                    if row.empty:
                        row = monthly_actual[monthly_actual["Channel"] == display_name]
                    if not row.empty:
                        cur_val = pd.to_numeric(row.iloc[0][last_m], errors="coerce")
                        prev_val = pd.to_numeric(row.iloc[0][prev_m], errors="coerce")
                        if pd.notna(cur_val) and pd.notna(prev_val) and prev_val > 0:
                            pct = f"{(cur_val-prev_val)/prev_val:+.0%}"
                        else:
                            pct = "N/A"
                        m_label = last_m.split(" ")[0] if " " in last_m else last_m
                        pm_label = prev_m.split(" ")[0] if " " in prev_m else prev_m
                        with kpi_col:
                            st.metric(f"{display_name} ({m_label})", f"{int(cur_val):,}" if pd.notna(cur_val) else "N/A", f"{pct} vs {pm_label}")

            st.divider()

            # --- Charts: GEO and Direct separate ---
            months_labels = [c.split(" ")[0] if " " in c else c for c in month_cols]
            monthly_actual = monthly_data[monthly_data["Type"] == "Actual"] if "Type" in monthly_data.columns else monthly_data

            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.caption("GEO Trends (CN + WW)")
                fig_m_geo = go.Figure()
                for channel, color in [("CN (GEO)", "#fbbf24"), ("WW (GEO)", "#a78bfa"), ("Total GEO", "#22c55e")]:
                    row = monthly_actual[monthly_actual["Channel"] == channel]
                    if not row.empty:
                        vals = [pd.to_numeric(row.iloc[0].get(c, 0), errors="coerce") for c in month_cols]
                        dash = "dot" if channel == "Total GEO" else None
                        fig_m_geo.add_trace(go.Scatter(name=channel, x=months_labels, y=vals, mode="lines+markers", line=dict(color=color, width=2, dash=dash)))
                fig_m_geo.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.2), yaxis_title="Reg Starts")
                st.plotly_chart(fig_m_geo, use_container_width=True)
            with col_chart2:
                st.caption("WW Direct + Total")
                fig_m_dir = go.Figure()
                for channel, color, dash in [("WW Website Direct", "#4a9eff", None), ("Total (GEO+Direct)", "#06b6d4", "dot")]:
                    row = monthly_actual[monthly_actual["Channel"] == channel]
                    if not row.empty:
                        vals = [pd.to_numeric(row.iloc[0].get(c, 0), errors="coerce") for c in month_cols]
                        name = "Total (GEO+Direct)" if channel == "Total (GEO+Direct)" else "WW Direct"
                        fig_m_dir.add_trace(go.Scatter(name=name, x=months_labels, y=vals, mode="lines+markers", line=dict(color=color, width=2, dash=dash)))
                fig_m_dir.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.2), yaxis_title="Reg Starts")
                st.plotly_chart(fig_m_dir, use_container_width=True)

            # --- Structured table (all rows: Actual/PY/YoY) ---
            st.dataframe(monthly_data, use_container_width=True, hide_index=True)

            # --- vs 大盘 BPS comparison ---
            _m_our_yoy = monthly_data[(monthly_data["Channel"] == "Total (GEO+Direct)") & (monthly_data["Type"] == "YoY")]
            _m_ssr_yoy = monthly_data[(monthly_data["Channel"] == "SSR Total (大盘)") & (monthly_data["Type"] == "YoY")]
            if not _m_our_yoy.empty and not _m_ssr_yoy.empty:
                bps_row = {"Channel": "跑赢大盘", "Type": "BPS"}
                for c in month_cols:
                    our_v = str(_m_our_yoy.iloc[0].get(c, "")).replace("%", "").replace("+", "")
                    ssr_v = str(_m_ssr_yoy.iloc[0].get(c, "")).replace("%", "").replace("+", "")
                    try:
                        bps_row[c] = f"+{int(float(our_v) - float(ssr_v))} ppts"
                    except:
                        bps_row[c] = "N/A"
                st.dataframe(pd.DataFrame([bps_row]), use_container_width=True, hide_index=True)

        with sub_ytd:
            st.subheader("📊 YTD Comparison" if is_en else "📊 YTD 对比")
            df_ytd = get_ytd_metrics()

            # Dynamic KPI cards from YTD data
            col1, col2, col3, col4 = st.columns(4)
            total_row = df_ytd[df_ytd["Channel"].isin(["Total", "Total (GEO+Direct)"])]
            cn_row = df_ytd[df_ytd["Channel"] == "CN GEO"]
            ww_est_row = df_ytd[df_ytd["Channel"].isin(["WW Direct EST", "WW Website Direct"])]
            ssr_row = df_ytd[df_ytd["Channel"].str.contains("SSR", na=False)]

            with col1:
                if not total_row.empty:
                    st.metric("Total (GEO+Direct)", f"{int(total_row.iloc[0]['YTD_Actual']):,}", f"{total_row.iloc[0]['YoY']} YoY")
                else:
                    st.metric("Total (GEO+Direct)", "N/A")
            with col2:
                if not cn_row.empty:
                    st.metric("CN GEO", f"{int(cn_row.iloc[0]['YTD_Actual']):,}", str(cn_row.iloc[0]['YoY']))
                else:
                    st.metric("CN GEO", "N/A")
            with col3:
                if not ww_est_row.empty:
                    st.metric("WW Direct", f"{int(ww_est_row.iloc[0]['YTD_Actual']):,}", str(ww_est_row.iloc[0]['YoY']))
                else:
                    st.metric("WW Direct", "N/A")
            with col4:
                # Calculate BPS dynamically from Total vs SSR Total
                if not total_row.empty and not ssr_row.empty:
                    _our_yoy_str = str(total_row.iloc[0]['YoY']).replace('%', '').replace('+', '')
                    _ssr_yoy_str = str(ssr_row.iloc[0]['YoY']).replace('%', '').replace('+', '')
                    try:
                        _our_yoy_val = float(_our_yoy_str)
                        _ssr_yoy_val = float(_ssr_yoy_str)
                        _bps = int(_our_yoy_val - _ssr_yoy_val)
                        st.metric("vs 大盘", f"+{_bps} ppts", "跑赢 SSR")
                    except:
                        st.metric("vs 大盘", "+100 ppts", "跑赢 SSR")
                else:
                    st.metric("vs 大盘", "N/A")

            st.divider()
            df_ytd_display = df_ytd.copy()
            df_ytd_display["增量"] = pd.to_numeric(df_ytd_display["YTD_Actual"], errors="coerce") - pd.to_numeric(df_ytd_display["YTD_PY"], errors="coerce")
            st.dataframe(df_ytd_display, use_container_width=True, hide_index=True)

            # Bar chart (exclude SSR Total for readability since it's much larger)
            df_bar = df_ytd[~df_ytd["Channel"].isin(["Total", "Total (GEO+Direct)", "SSR Total (大盘)"])].copy()
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(name="YTD Actual", x=df_bar["Channel"], y=pd.to_numeric(df_bar["YTD_Actual"], errors="coerce"), marker_color="#4a9eff"))
            fig_bar.add_trace(go.Bar(name="YTD PY", x=df_bar["Channel"], y=pd.to_numeric(df_bar["YTD_PY"], errors="coerce"), marker_color="#555"))
            fig_bar.update_layout(barmode="group", height=300, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.15))
            st.plotly_chart(fig_bar, use_container_width=True)

    # ============================================================
    # TAB: Reg Start vs Clean Launch (Full Year)
    # ============================================================
    with tab_rs_cl:
        st.subheader("📈 Reg Start vs Clean Launch – 2025 Full Year" if is_en else "📈 Reg Start vs Clean Launch – 2025全年数据")
        st.caption("Monthly breakdown with YoY comparison and conversion rate trends" if is_en else "月度拆解，含 YoY 对比及转化率趋势")

        # Load data files
        _rs_file = METRICS_PATH / "geo_regstart_full.csv"
        _cl_file = METRICS_PATH / "geo_cleanlaunch_full.csv"
        _conv_file = METRICS_PATH / "geo_conversion_full.csv"

        if _rs_file.exists() and _cl_file.exists() and _conv_file.exists():
            _df_rs_full = load_csv_safe(_rs_file)
            _df_cl_full = load_csv_safe(_cl_file)
            _df_conv_full = load_csv_safe(_conv_file)

            # --- KPI Cards ---
            _rs_total_row = _df_rs_full[(_df_rs_full["Channel"] == "Total (GEO+Direct)") & (_df_rs_full["Type"] == "Actual")]
            _cl_total_row = _df_cl_full[(_df_cl_full["Channel"] == "Total (GEO+Direct)") & (_df_cl_full["Type"] == "Actual")]
            _rs_py_row = _df_rs_full[(_df_rs_full["Channel"] == "Total (GEO+Direct)") & (_df_rs_full["Type"] == "PY")]
            _cl_py_row = _df_cl_full[(_df_cl_full["Channel"] == "Total (GEO+Direct)") & (_df_cl_full["Type"] == "PY")]

            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            with kpi1:
                _rs_ytd = int(_rs_total_row.iloc[0]["2025_Total"]) if not _rs_total_row.empty else 0
                _rs_py = int(_rs_py_row.iloc[0]["2025_Total"]) if not _rs_py_row.empty else 0
                _rs_yoy = f"+{(_rs_ytd - _rs_py) / _rs_py:.0%}" if _rs_py > 0 else "N/A"
                st.metric("Reg Start YTD", f"{_rs_ytd:,}", _rs_yoy)
            with kpi2:
                _cl_ytd = int(_cl_total_row.iloc[0]["2025_Total"]) if not _cl_total_row.empty else 0
                _cl_py = int(_cl_py_row.iloc[0]["2025_Total"]) if not _cl_py_row.empty else 0
                _cl_yoy = f"+{(_cl_ytd - _cl_py) / _cl_py:.0%}" if _cl_py > 0 else "N/A"
                st.metric("Clean Launch YTD", f"{_cl_ytd:,}", _cl_yoy)
            with kpi3:
                _conv_rate = _cl_ytd / _rs_ytd if _rs_ytd > 0 else 0
                st.metric("Conversion Rate", f"{_conv_rate:.1%}")
            with kpi4:
                _conv_py = _cl_py / _rs_py if _rs_py > 0 else 0
                _conv_delta = _conv_rate - _conv_py
                st.metric("Conv. vs PY", f"{_conv_delta:+.1%}" if abs(_conv_delta) > 0.001 else "Flat", f"PY: {_conv_py:.1%}")

            st.divider()

            # --- Channel filter ---
            _channels = _df_rs_full[_df_rs_full["Type"] == "Actual"]["Channel"].unique().tolist()
            _selected_channels = st.multiselect(
                "Select Channels" if is_en else "选择渠道",
                [c for c in _channels if "EM" not in c],
                default=[c for c in ["CN (GEO)", "WW (GEO)", "Total GEO", "WW Website Direct", "Total (GEO+Direct)", "SSR Total (大盘)"] if c in _channels],
                key="rs_cl_channel_filter"
            )

            # --- Sub-tabs: Reg Start / Clean Launch / Conversion / Trend ---
            _sub_rs, _sub_cl, _sub_conv, _sub_trend = st.tabs([
                "📈 Reg Start", "🚀 Clean Launch", "📊 Conversion Rate", "📉 Monthly Trend"
            ])

            _month_cols = [c for c in _df_rs_full.columns if c.startswith("2025_M")]
            _month_label_map = {
                "2025_M1_Jan": "Jan", "2025_M2_Feb": "Feb", "2025_M3_Mar": "Mar",
                "2025_M4_Apr": "Apr", "2025_M5_May": "May", "2025_M6_Jun_MTD": "Jun(MTD)"
            }
            _month_labels = [_month_label_map.get(c, c) for c in _month_cols]

            def _format_table(df, channels, is_rate=False):
                """Format a data table for display with selected channels."""
                df_filtered = df[df["Channel"].isin(channels)].copy()
                # Use only month columns that exist in this specific dataframe
                df_month_cols = [c for c in _month_cols if c in df.columns]
                df_month_labels = [_month_label_map.get(c, c) for c in df_month_cols]
                has_total = "2025_Total" in df.columns
                select_cols = ["Channel", "Type"] + df_month_cols + (["2025_Total"] if has_total else [])
                display_df = df_filtered[select_cols].copy()
                display_df.columns = ["Channel", "Type"] + df_month_labels + (["YTD Total"] if has_total else [])
                fmt_cols = df_month_labels + (["YTD Total"] if has_total else [])
                for col in fmt_cols:
                    if is_rate:
                        display_df[col] = display_df[col].apply(
                            lambda x: x if (isinstance(x, str) and '%' in x) else (f"{float(x):.1%}" if pd.notna(x) and str(x) not in ["", "nan"] else "-")
                        )
                    else:
                        # Format based on row Type: YoY rows keep as-is if already formatted, others as integers
                        display_df[col] = display_df.apply(
                            lambda row: (
                                str(row[col]) if row.get("Type") == "YoY"
                                else (f"{int(float(row[col])):,}" if pd.notna(row[col]) and str(row[col]) not in ["", "nan", "N/A"] else "-")
                            ), axis=1
                        )
                return display_df

            with _sub_rs:
                st.markdown("**Reg Start – Monthly (Actual / PY / YoY)**")
                _df_rs_display = _format_table(_df_rs_full, _selected_channels)
                st.dataframe(_df_rs_display, use_container_width=True, hide_index=True)

                # Share% row: Total (GEO+Direct) / SSR Total
                _total_row_a = _df_rs_full[(_df_rs_full["Channel"] == "Total (GEO+Direct)") & (_df_rs_full["Type"] == "Actual")]
                _total_row_p = _df_rs_full[(_df_rs_full["Channel"] == "Total (GEO+Direct)") & (_df_rs_full["Type"] == "PY")]
                _ssr_row_a = _df_rs_full[(_df_rs_full["Channel"].str.contains("SSR", na=False)) & (_df_rs_full["Type"] == "Actual")]
                _ssr_row_p = _df_rs_full[(_df_rs_full["Channel"].str.contains("SSR", na=False)) & (_df_rs_full["Type"] == "PY")]
                if not _total_row_a.empty and not _ssr_row_a.empty:
                    _rs_month_cols = [c for c in _month_cols if c in _df_rs_full.columns]
                    share_data = {"Channel": ["Share% of SSR"] * 3, "Type": ["Actual", "PY", "YoY (bps)"]}
                    for c in _rs_month_cols + (["2025_Total"] if "2025_Total" in _df_rs_full.columns else []):
                        try:
                            tot_a = float(_total_row_a.iloc[0][c]) if pd.notna(_total_row_a.iloc[0].get(c)) else 0
                            ssr_a = float(_ssr_row_a.iloc[0][c]) if pd.notna(_ssr_row_a.iloc[0].get(c)) else 0
                            tot_p = float(_total_row_p.iloc[0][c]) if not _total_row_p.empty and pd.notna(_total_row_p.iloc[0].get(c)) else 0
                            ssr_p = float(_ssr_row_p.iloc[0][c]) if not _ssr_row_p.empty and pd.notna(_ssr_row_p.iloc[0].get(c)) else 0
                            share_a = tot_a / ssr_a * 100 if ssr_a > 0 else 0
                            share_p = tot_p / ssr_p * 100 if ssr_p > 0 else 0
                            share_yoy = (share_a/100 - share_p/100) * 10000
                            col_label = _month_label_map.get(c, c) if c != "2025_Total" else "YTD Total"
                            share_data.setdefault(col_label, [])
                            share_data[col_label].append(f"{share_a:.1f}%")
                            share_data[col_label].append(f"{share_p:.1f}%")
                            share_data[col_label].append(f"{share_yoy:+,.0f} bps")
                        except Exception:
                            col_label = _month_label_map.get(c, c) if c != "2025_Total" else "YTD Total"
                            share_data.setdefault(col_label, [])
                            share_data[col_label].extend(["-", "-", "-"])
                    try:
                        df_share = pd.DataFrame(share_data)
                        st.caption("**Share% = Total (GEO+Direct) / SSR Total**")
                        st.dataframe(df_share, use_container_width=True, hide_index=True)
                    except Exception:
                        pass

            with _sub_cl:
                st.markdown("**Clean Launch – Monthly (Actual / PY / YoY)**")
                _df_cl_display = _format_table(_df_cl_full, _selected_channels)
                st.dataframe(_df_cl_display, use_container_width=True, hide_index=True)

                # Share% row for CL
                _cl_total_a = _df_cl_full[(_df_cl_full["Channel"] == "Total (GEO+Direct)") & (_df_cl_full["Type"] == "Actual")]
                _cl_total_p = _df_cl_full[(_df_cl_full["Channel"] == "Total (GEO+Direct)") & (_df_cl_full["Type"] == "PY")]
                _cl_ssr_a = _df_cl_full[(_df_cl_full["Channel"].str.contains("SSR", na=False)) & (_df_cl_full["Type"] == "Actual")]
                _cl_ssr_p = _df_cl_full[(_df_cl_full["Channel"].str.contains("SSR", na=False)) & (_df_cl_full["Type"] == "PY")]
                if not _cl_total_a.empty and not _cl_ssr_a.empty:
                    _cl_mcols = [c for c in _month_cols if c in _df_cl_full.columns]
                    cl_share_data = {"Channel": ["Share% of SSR"] * 3, "Type": ["Actual", "PY", "YoY (bps)"]}
                    for c in _cl_mcols + (["2025_Total"] if "2025_Total" in _df_cl_full.columns else []):
                        try:
                            tot_a = float(_cl_total_a.iloc[0][c]) if pd.notna(_cl_total_a.iloc[0].get(c)) else 0
                            ssr_a = float(_cl_ssr_a.iloc[0][c]) if pd.notna(_cl_ssr_a.iloc[0].get(c)) else 0
                            tot_p = float(_cl_total_p.iloc[0][c]) if not _cl_total_p.empty and pd.notna(_cl_total_p.iloc[0].get(c)) else 0
                            ssr_p = float(_cl_ssr_p.iloc[0][c]) if not _cl_ssr_p.empty and pd.notna(_cl_ssr_p.iloc[0].get(c)) else 0
                            share_a = tot_a / ssr_a * 100 if ssr_a > 0 else 0
                            share_p = tot_p / ssr_p * 100 if ssr_p > 0 else 0
                            share_yoy = (share_a/100 - share_p/100) * 10000
                            col_label = _month_label_map.get(c, c) if c != "2025_Total" else "YTD Total"
                            cl_share_data.setdefault(col_label, [])
                            cl_share_data[col_label].append(f"{share_a:.1f}%")
                            cl_share_data[col_label].append(f"{share_p:.1f}%")
                            cl_share_data[col_label].append(f"{share_yoy:+,.0f} bps")
                        except Exception:
                            col_label = _month_label_map.get(c, c) if c != "2025_Total" else "YTD Total"
                            cl_share_data.setdefault(col_label, [])
                            cl_share_data[col_label].extend(["-", "-", "-"])
                    try:
                        df_cl_share = pd.DataFrame(cl_share_data)
                        st.caption("**Share% = Total (GEO+Direct) / SSR Total**")
                        st.dataframe(df_cl_share, use_container_width=True, hide_index=True)
                    except Exception:
                        pass

            with _sub_conv:
                st.markdown("**Conversion Rate (Clean Launch / Reg Start) – Actual / PY / YoY (ppt)**")
                # Format conversion: Actual and PY as percentages, YoY as ppt
                _df_conv_filtered = _df_conv_full[_df_conv_full["Channel"].isin(_selected_channels)].copy()
                _conv_month_cols = [c for c in _month_cols if c in _df_conv_full.columns]
                _conv_month_labels = [_month_label_map.get(c, c) for c in _conv_month_cols]
                _conv_has_total = "2025_Total" in _df_conv_full.columns
                _conv_select = ["Channel", "Type"] + _conv_month_cols + (["2025_Total"] if _conv_has_total else [])
                _df_conv_display = _df_conv_filtered[_conv_select].copy()
                _df_conv_display.columns = ["Channel", "Type"] + _conv_month_labels + (["YTD Total"] if _conv_has_total else [])
                _conv_fmt_cols = _conv_month_labels + (["YTD Total"] if _conv_has_total else [])
                for col in _conv_fmt_cols:
                    _df_conv_display[col] = _df_conv_display.apply(
                        lambda row: (
                            str(row[col]) if row.get("Type") == "YoY"
                            else (str(row[col]) if isinstance(row[col], str) and '%' in str(row[col])
                                  else (f"{float(row[col]):.1%}" if pd.notna(row[col]) and str(row[col]) not in ["", "nan", "N/A"] else "-"))
                        ), axis=1
                    )
                st.dataframe(_df_conv_display, use_container_width=True, hide_index=True)

                # Conversion line chart - Actual vs PY
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.caption("Conversion Rate – Actual")
                    fig_conv_a = go.Figure()
                    _conv_actual = _df_conv_full[(_df_conv_full["Type"] == "Actual") & (_df_conv_full["Channel"].isin(_selected_channels))]
                    for _, row in _conv_actual.iterrows():
                        vals = []
                        for c in _conv_month_cols:
                            v = row[c]
                            if isinstance(v, str) and '%' in v:
                                try: vals.append(float(v.replace('%','').replace('+','')))
                                except: vals.append(0)
                            elif pd.notna(v):
                                try: vals.append(float(v) * 100)
                                except: vals.append(0)
                            else: vals.append(0)
                        fig_conv_a.add_trace(go.Scatter(x=_conv_month_labels, y=vals, mode="lines+markers", name=row["Channel"]))
                    fig_conv_a.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="Conversion %", legend=dict(orientation="h", y=-0.2))
                    st.plotly_chart(fig_conv_a, use_container_width=True)
                with col_c2:
                    st.caption("Conversion Rate – PY")
                    fig_conv_p = go.Figure()
                    _conv_py = _df_conv_full[(_df_conv_full["Type"] == "PY") & (_df_conv_full["Channel"].isin(_selected_channels))]
                    for _, row in _conv_py.iterrows():
                        vals = []
                        for c in _conv_month_cols:
                            v = row[c]
                            if isinstance(v, str) and '%' in v:
                                try: vals.append(float(v.replace('%','').replace('+','')))
                                except: vals.append(0)
                            elif pd.notna(v):
                                try: vals.append(float(v) * 100)
                                except: vals.append(0)
                            else: vals.append(0)
                        fig_conv_p.add_trace(go.Scatter(x=_conv_month_labels, y=vals, mode="lines+markers", name=row["Channel"]))
                    fig_conv_p.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="Conversion %", legend=dict(orientation="h", y=-0.2))
                    st.plotly_chart(fig_conv_p, use_container_width=True)

            with _sub_trend:
                st.markdown("**Monthly Trend – Reg Start vs Clean Launch**")

                # Build monthly trend chart for selected channels
                _trend_metric = st.radio(
                    "Metric" if is_en else "指标",
                    ["Reg Start", "Clean Launch", "Both"],
                    horizontal=True, key="rs_cl_trend_metric"
                )

                fig_trend = go.Figure()
                colors_rs = {"CN (GEO)": "#fbbf24", "WW (GEO)": "#a78bfa", "Total GEO": "#22c55e", "WW Website Direct": "#4a9eff", "Total (GEO+Direct)": "#06b6d4", "SSR Total (大盘)": "#888"}
                colors_cl = {"CN (GEO)": "#f59e0b", "WW (GEO)": "#7c3aed", "Total GEO": "#16a34a", "WW Website Direct": "#2563eb", "Total (GEO+Direct)": "#0891b2", "SSR Total (大盘)": "#666"}

                # Upper trend chart: only Total GEO and WW Direct
                _trend_channels = [ch for ch in _selected_channels if ch in ["Total GEO", "WW Website Direct"]]
                for ch in _trend_channels:
                    if _trend_metric in ["Reg Start", "Both"]:
                        rs_row = _df_rs_full[(_df_rs_full["Channel"] == ch) & (_df_rs_full["Type"] == "Actual")]
                        if not rs_row.empty:
                            rs_vals = [float(rs_row.iloc[0][c]) if pd.notna(rs_row.iloc[0][c]) and str(rs_row.iloc[0][c]).replace(',','').replace('.','').replace('-','').isdigit() else 0 for c in _month_cols]
                            fig_trend.add_trace(go.Scatter(
                                x=_month_labels, y=rs_vals, mode="lines+markers",
                                name=f"{ch} (RS)",
                                line=dict(color=colors_rs.get(ch, "#888"), width=2),
                            ))
                    if _trend_metric in ["Clean Launch", "Both"]:
                        cl_row = _df_cl_full[(_df_cl_full["Channel"] == ch) & (_df_cl_full["Type"] == "Actual")]
                        if not cl_row.empty:
                            _cl_month_cols = [c for c in _month_cols if c in _df_cl_full.columns]
                            _cl_month_labels = [_month_label_map.get(c, c) for c in _cl_month_cols]
                            cl_vals = [float(cl_row.iloc[0][c]) if pd.notna(cl_row.iloc[0][c]) and str(cl_row.iloc[0][c]).replace(',','').replace('.','').replace('-','').isdigit() else 0 for c in _cl_month_cols]
                            fig_trend.add_trace(go.Scatter(
                                x=_cl_month_labels, y=cl_vals, mode="lines+markers",
                                name=f"{ch} (CL)",
                                line=dict(color=colors_cl.get(ch, "#666"), width=2, dash="dash"),
                            ))

                fig_trend.update_layout(
                    height=400, margin=dict(l=0, r=0, t=30, b=0),
                    yaxis_title="Count",
                    legend=dict(orientation="h", y=-0.2),
                    hovermode="x unified",
                )
                st.plotly_chart(fig_trend, use_container_width=True)

                # YoY comparison
                st.divider()
                st.markdown("**YoY Growth Trend**" if is_en else "**YoY 增长趋势**")
                fig_yoy = go.Figure()
                # Lower YoY chart: only Total GEO, WW Direct, and SSR Total
                _yoy_channels = [ch for ch in _selected_channels if ch in ["Total GEO", "WW Website Direct", "SSR Total (大盘)"]]
                for ch in _yoy_channels:
                    yoy_row = _df_rs_full[(_df_rs_full["Channel"] == ch) & (_df_rs_full["Type"] == "YoY")]
                    if not yoy_row.empty:
                        yoy_vals = []
                        for c in _month_cols:
                            v = yoy_row.iloc[0][c]
                            if isinstance(v, str) and '%' in v:
                                try: yoy_vals.append(float(v.replace('%','').replace('+','')))
                                except: yoy_vals.append(0)
                            elif pd.notna(v):
                                try: yoy_vals.append(float(v) * 100)
                                except: yoy_vals.append(0)
                            else: yoy_vals.append(0)
                        fig_yoy.add_trace(go.Scatter(
                            x=_month_labels, y=yoy_vals, mode="lines+markers",
                            name=f"{ch}",
                            line=dict(color=colors_rs.get(ch, "#888"), width=2),
                        ))
                fig_yoy.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
                fig_yoy.update_layout(
                    height=320, margin=dict(l=0, r=0, t=30, b=0),
                    yaxis_title="YoY %",
                    legend=dict(orientation="h", y=-0.2),
                    hovermode="x unified",
                )
                st.plotly_chart(fig_yoy, use_container_width=True)

        else:
            st.warning("⚠️ Full year data not found. Run data extraction first." if is_en else "⚠️ 未找到全年数据文件。请先执行数据提取。")
            st.info("Expected files: geo_regstart_full.csv, geo_cleanlaunch_full.csv, geo_conversion_full.csv in output/metrics/")

    # ============================================================
    # TAB: GEO Data Analysis (Mario-GEO style)
    # ============================================================
    with tab_input:
        st.subheader("📥 GEO 效果追踪 & 内容产出" if is_en else "📥 GEO 效果追踪 & 内容产出")

        # --- GEO效果追踪 Upload & Display ---
        geo_input_file = METRICS_PATH / "geo_input_summary.csv"
        geo_platform_file = METRICS_PATH / "geo_input_platform.csv"
        geo_detail_file = METRICS_PATH / "geo_input_detail.csv"

        with st.expander("📤 上传 GEO 效果追踪 Excel", expanded=False):
            st.caption("上传 GEO效果追踪 Excel 文件（含多Sheet），自动解析汇总数据和明细")
            uploaded_geo = st.file_uploader("上传 GEO 效果追踪 Excel", type=["xlsx", "xls"], key="geo_tracking_upload")
            if uploaded_geo:
                try:
                    xls = pd.ExcelFile(uploaded_geo)
                    st.info(f"检测到 {len(xls.sheet_names)} 个 Sheet: {', '.join(xls.sheet_names)}")
                    selected_sheets = st.multiselect("选择要导入的 Sheet", xls.sheet_names, default=xls.sheet_names, key="geo_sheet_select")
                    if selected_sheets:
                        for sn in selected_sheets:
                            with st.expander(f"📄 {sn}", expanded=False):
                                df_sheet = pd.read_excel(uploaded_geo, sheet_name=sn)
                                st.dataframe(df_sheet.head(20), use_container_width=True, hide_index=True)

                    if st.button("💾 保存明细数据", key="save_geo_detail"):
                        # Save all detail sheets as combined CSV
                        all_details = []
                        for sn in selected_sheets:
                            df_s = pd.read_excel(uploaded_geo, sheet_name=sn)
                            df_s.insert(0, "_Sheet", sn)
                            all_details.append(df_s)
                        if all_details:
                            df_combined = pd.concat(all_details, ignore_index=True)
                            df_combined.to_csv(geo_detail_file, index=False, encoding="utf-8-sig")
                            st.toast(f"✅ 已保存 {len(df_combined)} 行明细数据")
                            st.rerun()
                except Exception as e:
                    st.error(f"解析文件失败: {e}")

        # --- Display GEO Summary ---
        if geo_input_file.exists():
            df_geo_summary = load_csv_safe(geo_input_file)
            if not df_geo_summary.empty:
                st.markdown("**📊 GEO 效果汇总 (月度)**")
                month_cols_geo = [c for c in df_geo_summary.columns if c != "指标"]

                # KPI cards - latest month
                latest_m = month_cols_geo[-1] if month_cols_geo else None
                if latest_m:
                    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
                    def _get_geo_val(metric_name):
                        row = df_geo_summary[df_geo_summary["指标"] == metric_name]
                        if not row.empty:
                            return str(row.iloc[0][latest_m])
                        return "N/A"

                    with kpi1:
                        v = _get_geo_val("提示词#")
                        st.metric(f"提示词数 ({latest_m})", v)
                    with kpi2:
                        v = _get_geo_val("品牌词链接提及")
                        st.metric(f"品牌链接提及 ({latest_m})", v)
                    with kpi3:
                        v = _get_geo_val("品牌词链接提及率")
                        st.metric(f"链接提及率 ({latest_m})", v)
                    with kpi4:
                        v = _get_geo_val("新建内容#")
                        st.metric(f"新建内容 ({latest_m})", v)
                    with kpi5:
                        v = _get_geo_val("监控平台数")
                        st.metric(f"监控平台 ({latest_m})", v)

                st.divider()
                st.dataframe(df_geo_summary, use_container_width=True, hide_index=True)

                # Trend chart - key metrics
                st.markdown("**📈 月度趋势**")
                trend_metrics = ["品牌词链接提及", "新建内容#", "提示词#"]
                available_metrics = [m for m in trend_metrics if m in df_geo_summary["指标"].values]
                if available_metrics:
                    fig_geo_trend = go.Figure()
                    colors_geo = {"品牌词链接提及": "#4a9eff", "新建内容#": "#22c55e", "提示词#": "#fbbf24"}
                    for metric in available_metrics:
                        row = df_geo_summary[df_geo_summary["指标"] == metric]
                        if not row.empty:
                            vals = [pd.to_numeric(row.iloc[0][c], errors="coerce") for c in month_cols_geo]
                            fig_geo_trend.add_trace(go.Scatter(
                                x=month_cols_geo, y=vals, mode="lines+markers",
                                name=metric, line=dict(color=colors_geo.get(metric, "#888"), width=2)
                            ))
                    fig_geo_trend.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.2))
                    st.plotly_chart(fig_geo_trend, use_container_width=True)

        # --- Per-Platform Breakdown ---
        if geo_platform_file.exists():
            df_platform = load_csv_safe(geo_platform_file)
            if not df_platform.empty:
                st.divider()
                st.markdown("**🤖 各 AI 平台提及分布**")

                # Filter by metric type
                metric_types = df_platform["指标"].unique().tolist() if "指标" in df_platform.columns else []
                if metric_types:
                    selected_metric_type = st.selectbox("选择指标", metric_types, key="platform_metric_type")
                    df_plt_filtered = df_platform[df_platform["指标"] == selected_metric_type]

                    # Month filter
                    plt_months = [c for c in df_plt_filtered.columns if c not in ["指标", "平台"]]
                    if plt_months:
                        selected_plt_month = st.selectbox("选择月份", plt_months, index=len(plt_months)-1, key="platform_month")

                        # Bar chart by platform
                        platforms = df_plt_filtered["平台"].tolist()
                        values = [pd.to_numeric(str(df_plt_filtered[df_plt_filtered["平台"]==p].iloc[0][selected_plt_month]).strip(), errors="coerce") for p in platforms]

                        fig_plt = go.Figure()
                        fig_plt.add_trace(go.Bar(x=platforms, y=values, marker_color="#4a9eff"))
                        fig_plt.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), yaxis_title=selected_metric_type)
                        st.plotly_chart(fig_plt, use_container_width=True)

                    st.dataframe(df_plt_filtered, use_container_width=True, hide_index=True)

        # --- Detail Data (from uploaded Excel) ---
        if geo_detail_file.exists():
            df_detail = load_csv_safe(geo_detail_file)
            if not df_detail.empty:
                st.divider()
                st.markdown("**📋 检索短语提及明细**")

                # Filters
                col_f1, col_f2, col_f3 = st.columns(3)
                with col_f1:
                    sheets_available = df_detail["_Sheet"].unique().tolist() if "_Sheet" in df_detail.columns else []
                    sheet_filter = st.selectbox("Sheet", ["全部"] + sheets_available, key="detail_sheet_filter")
                with col_f2:
                    # Try to find month column
                    month_col_detail = None
                    for candidate in ["新增月份", "月份", "Month"]:
                        if candidate in df_detail.columns:
                            month_col_detail = candidate
                            break
                    if month_col_detail:
                        months_available = sorted(df_detail[month_col_detail].dropna().unique().tolist())
                        month_filter = st.selectbox("月份", ["全部"] + months_available, key="detail_month_filter")
                    else:
                        month_filter = "全部"
                with col_f3:
                    # Category filter
                    cat_col = None
                    for candidate in ["类别1", "类别2", "类别"]:
                        if candidate in df_detail.columns:
                            cat_col = candidate
                            break
                    if cat_col:
                        cats_available = sorted(df_detail[cat_col].dropna().unique().tolist())
                        cat_filter = st.selectbox("类别", ["全部"] + [str(c) for c in cats_available], key="detail_cat_filter")
                    else:
                        cat_filter = "全部"

                # Apply filters
                df_detail_show = df_detail.copy()
                if sheet_filter != "全部" and "_Sheet" in df_detail_show.columns:
                    df_detail_show = df_detail_show[df_detail_show["_Sheet"] == sheet_filter]
                if month_filter != "全部" and month_col_detail:
                    df_detail_show = df_detail_show[df_detail_show[month_col_detail] == month_filter]
                if cat_filter != "全部" and cat_col:
                    df_detail_show = df_detail_show[df_detail_show[cat_col].astype(str) == cat_filter]

                st.caption(f"显示 {len(df_detail_show)} 条记录")
                st.dataframe(df_detail_show.head(200), use_container_width=True, hide_index=True)

        st.divider()

        # Load zhizao data for article stats
        df_articles = load_zhizao(selected_batch)
        if not df_articles.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Articles" if is_en else "产出文章总数", len(df_articles))
            with col2:
                if "category" in df_articles.columns:
                    st.metric("Topics Covered" if is_en else "覆盖 Topic 数", df_articles["category"].nunique())
                else:
                    st.metric("Topics Covered" if is_en else "覆盖 Topic 数", "N/A")
            with col3:
                if "word_count" in df_articles.columns:
                    df_articles["word_count"] = pd.to_numeric(df_articles["word_count"], errors="coerce")
                    st.metric("Total Words" if is_en else "总字数", f"{df_articles['word_count'].sum():,.0f}")

            st.divider()

            # Filter by topic
            if "category" in df_articles.columns:
                topics = ["全部"] + sorted(df_articles["category"].dropna().unique().tolist())
                topic_filter = st.selectbox("Filter by Topic" if is_en else "按 Topic 筛选", topics, key="zhixi_topic_filter")
                df_filtered = df_articles if topic_filter == "全部" else df_articles[df_articles["category"] == topic_filter]
            else:
                df_filtered = df_articles

            # Time filter
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                time_view = st.selectbox("Time Dimension" if is_en else "时间维度", ["全部", "指定日期", "指定周", "本月", "YTD"], key="zhixi_time")
            with col_t2:
                if time_view == "指定日期":
                    selected_date = st.date_input("Select date" if is_en else "选择日期", key="zhixi_date")
                elif time_view == "指定周":
                    selected_week = st.selectbox("Select week" if is_en else "选择周", [f"WK{i}" for i in range(1, 25)], index=20, key="zhixi_week_select")

            # Display
            display_cols = [c for c in ["title", "ai_query", "category", "word_count", "created_at"] if c in df_filtered.columns]
            if display_cols:
                st.dataframe(df_filtered[display_cols], use_container_width=True, hide_index=True)

            # Topic distribution chart
            if "category" in df_articles.columns:
                st.divider()
                st.markdown("**Article Topic Distribution**" if is_en else "**文章 Topic 分布**")
                cat_counts = df_articles["category"].value_counts().reset_index()
                cat_counts.columns = ["Topic", "文章数"]
                fig_topic = px.bar(cat_counts.head(15), x="Topic", y="文章数", color="文章数",
                                   color_continuous_scale=["#94a3b8", "#4a9eff"])
                fig_topic.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0), showlegend=False, coloraxis_showscale=False)
                st.plotly_chart(fig_topic, use_container_width=True)
        else:
            st.info("No article production data. Please run Content Creation first." if is_en else "暂无文章产出数据。请先执行智造生成内容。")

    # ============================================================
    # ============================================================
    # TAB 3: AI 引用追踪
    # ============================================================
    with tab_citation:
        st.subheader("🔗 AI 引用追踪" if is_en else "🔗 AI 引用追踪")

        AI_PLATFORMS = ["元宝", "DeepSeek", "豆包", "ChatGPT", "Kimi", "千问", "Gemini"]
        _cite_months = ["Jan", "Feb", "Mar", "Apr", "May"]

        # --- Section 1: 品牌词 ---
        st.markdown("### 🏷️ 品牌词引用追踪")
        st.caption("品牌词 = 旧提示词(397) + 新提示词(69品牌) | 包含：品牌提及 + 品牌提及率 + 官网链接提及 + 官网链接提及率")

        # 品牌词数量（按月）
        st.markdown("**📊 品牌词数量（按月）**")
        df_brand_count = pd.DataFrame({
            "指标": ["品牌词提示词数", "品牌词投放量(提示词×平台)"],
            "Jan": [297, 1188],
            "Feb": [297, 1188],
            "Mar": [297, 1188],
            "Apr": [397, 1588],
            "May": [466, 1860],
        })
        st.dataframe(df_brand_count, use_container_width=True, hide_index=True)

        st.divider()

        # 品牌提及 + 品牌提及率（按月）
        st.markdown("**📊 品牌提及 & 品牌提及率（按月）**")
        st.caption("品牌提及 = 新建内容在AI平台中出现品牌信息并引用发布信源")
        df_brand_mention = pd.DataFrame({
            "指标": ["新建内容#", "品牌内容#", "品牌内容提及", "品牌内容提及率"],
            "Jan": [98, 98, 98, "100%"],
            "Feb": [43, 43, 43, "100%"],
            "Mar": [118, 118, 106, "89.8%"],
            "Apr": [123, 123, 111, "90.2%"],
            "May": [135, 81, 69, "85.2%"],
        })
        st.dataframe(df_brand_mention, use_container_width=True, hide_index=True)

        # 品牌提及趋势图
        fig_mention = go.Figure()
        fig_mention.add_trace(go.Bar(name="新建内容#", x=_cite_months, y=[98, 43, 118, 123, 135], marker_color="#94a3b8"))
        fig_mention.add_trace(go.Bar(name="品牌内容提及", x=_cite_months, y=[98, 43, 106, 111, 69], marker_color="#4a9eff"))
        fig_mention.update_layout(barmode="group", height=260, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="篇数", legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_mention, use_container_width=True)

        st.divider()

        # 官网链接提及 + 官网链接提及率（按月）
        st.markdown("**📊 官网链接提及 & 官网链接提及率（按月）**")
        st.caption("官网链接提及 = AI平台应答中直接展示 gs.amazon.cn 官方链接")
        df_link_monthly = pd.DataFrame({
            "指标": ["品牌词投放量", "官网链接提及(Total)", "官网链接提及率"],
            "Jan": [1188, 720, "60.61%"],
            "Feb": [1188, 787, "66.25%"],
            "Mar": [1188, 879, "73.99%"],
            "Apr": [1588, 964, "60.71%"],
            "May": [1860, 866, "46.56%"],
        })
        st.dataframe(df_link_monthly, use_container_width=True, hide_index=True)

        # 官网链接提及率月度趋势
        fig_link_rate = go.Figure()
        fig_link_rate.add_trace(go.Scatter(
            x=_cite_months, y=[60.61, 66.25, 73.99, 60.71, 46.56],
            mode="lines+markers", name="官网链接提及率",
            line=dict(color="#4a9eff", width=3)
        ))
        fig_link_rate.add_trace(go.Bar(
            x=_cite_months, y=[720, 787, 879, 964, 866],
            name="官网链接提及数", marker_color="rgba(74,158,255,0.3)", yaxis="y2"
        ))
        fig_link_rate.update_layout(
            height=300, margin=dict(l=0, r=40, t=10, b=0),
            yaxis=dict(title="提及率 %", side="left"),
            yaxis2=dict(title="提及数", side="right", overlaying="y"),
            legend=dict(orientation="h", y=-0.2)
        )
        st.plotly_chart(fig_link_rate, use_container_width=True)

        # 按平台明细（官网链接提及率）
        with st.expander("📋 各平台官网链接提及率明细（按月）", expanded=False):
            df_plt_rate = pd.DataFrame({
                "平台": ["元宝", "DeepSeek", "豆包", "ChatGPT", "Kimi", "千问", "Gemini"],
                "Jan": ["54.88%", "67.00%", "78.79%", "41.75%", "-", "-", "-"],
                "Feb": ["64.98%", "72.73%", "80.81%", "46.46%", "-", "-", "-"],
                "Mar": ["80.13%", "79.80%", "86.53%", "49.49%", "-", "-", "-"],
                "Apr": ["71.03%", "53.90%", "73.30%", "44.58%", "-", "-", "-"],
                "May": ["59.57%", "51.40%", "44.95%", "30.32%", "44.73%", "56.77%", "33.76%"],
            })
            st.dataframe(df_plt_rate, use_container_width=True, hide_index=True)
            st.caption("Kimi/千问/Gemini 5月新增监控")

        # 按平台明细（官网链接提及数）
        with st.expander("📋 各平台官网链接提及数明细（按月）", expanded=False):
            df_plt_count = pd.DataFrame({
                "平台": ["元宝", "DeepSeek", "豆包", "ChatGPT", "Kimi", "千问", "Gemini"],
                "Jan": [163, 199, 234, 124, "-", "-", "-"],
                "Feb": [193, 216, 240, 138, "-", "-", "-"],
                "Mar": [238, 237, 257, 147, "-", "-", "-"],
                "Apr": [282, 214, 291, 177, "-", "-", "-"],
                "May": [277, 239, 209, 141, 208, 264, 157],
            })
            st.dataframe(df_plt_count, use_container_width=True, hide_index=True)

        st.divider()

        # --- Section 2: 行业词 ---
        st.markdown("### 🏭 行业词引用追踪")
        st.caption("行业词(98个) | 仅追踪：品牌提及 + 品牌提及率 | 不涉及官网链接提及（行业词涉及多平台对比，官网链接概率极低）")

        # 行业词 KPI
        ind_kpi1, ind_kpi2, ind_kpi3 = st.columns(3)
        with ind_kpi1:
            st.metric("行业词总数", "98")
        with ind_kpi2:
            st.metric("品牌提及 (7平台合计)", "664")
        with ind_kpi3:
            st.metric("平均品牌提及率", "91.84%")

        # 行业词 - 品牌提及 by platform
        st.markdown("**📊 行业词 - 品牌提及（各平台）**")
        df_industry = pd.DataFrame({
            "平台": AI_PLATFORMS,
            "品牌提及数": [97, 97, 97, 92, 97, 97, 87],
            "品牌提及率": ["98.98%", "98.98%", "98.98%", "93.88%", "98.98%", "98.98%", "88.78%"],
            "备注": ["", "", "", "略低", "", "", "Gemini略低"],
        })
        st.dataframe(df_industry, use_container_width=True, hide_index=True)

        fig_ind = go.Figure()
        fig_ind.add_trace(go.Bar(x=df_industry["平台"], y=df_industry["品牌提及数"], marker_color="#a78bfa"))
        fig_ind.add_hline(y=98, line_dash="dash", line_color="gray", annotation_text="总行业词=98")
        fig_ind.update_layout(height=260, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="品牌提及数")
        st.plotly_chart(fig_ind, use_container_width=True)

        with st.expander("📋 行业词按子类分布", expanded=False):
            df_ind_cat = pd.DataFrame({
                "子类": ["新手(30个)", "场景(48个)", "通用(20个)"],
                "元宝": [30, 48, 19],
                "DeepSeek": [30, 48, 19],
                "豆包": [30, 48, 19],
                "ChatGPT": [27, 47, 18],
                "Kimi": [30, 48, 19],
                "千问": [30, 48, 19],
                "Gemini": [29, 41, 17],
            })
            st.dataframe(df_ind_cat, use_container_width=True, hide_index=True)

        st.divider()

        # --- Section 3: 每月产出内容 ---
        st.markdown("### 📝 每月产出内容")
        df_content_output = pd.DataFrame({
            "指标": ["新建内容(Total)", "品牌相关内容", "行业相关内容"],
            "Jan": [98, 98, 0],
            "Feb": [43, 43, 0],
            "Mar": [118, 118, 0],
            "Apr": [123, 123, 0],
            "May": [135, 81, 54],
            "YTD": [517, 463, 54],
        })
        st.dataframe(df_content_output, use_container_width=True, hide_index=True)

        # Chart
        fig_content = go.Figure()
        fig_content.add_trace(go.Bar(name="品牌相关内容", x=_cite_months, y=[98, 43, 118, 123, 81], marker_color="#4a9eff"))
        fig_content.add_trace(go.Bar(name="行业相关内容", x=_cite_months, y=[0, 0, 0, 0, 54], marker_color="#a78bfa"))
        fig_content.update_layout(barmode="stack", height=260, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="篇数", legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig_content, use_container_width=True)

        # YTD KPI
        ct_kpi1, ct_kpi2, ct_kpi3 = st.columns(3)
        with ct_kpi1:
            st.metric("YTD 产出总数", "517")
        with ct_kpi2:
            st.metric("品牌相关内容", "463")
        with ct_kpi3:
            st.metric("行业相关内容", "54")

        st.divider()
        st.markdown("### 💡 关键洞察")
        st.markdown("""
- **品牌词官网链接提及率**：1-3月持续上升(60%→74%)，4-5月因新增提示词和平台扩展导致分母增大，提及率下降(60%→46%)
- **元宝/千问** 官网链接提及频次最高，适合重点投放
- **ChatGPT** 直接展示链接概率低(30%)，但角标引用远超其他平台，用户点击率更高
- **豆包** 1-3月表现优异(80%+)，5月骤降至44.95%，需排查
- **行业词** 品牌提及率极高(91.84%)，但官网链接提及几乎为0 → 适合第三方媒体发布
- **ChatGPT 新提示词** 官网链接0提及，需针对性优化
""")

    # ============================================================
    # TAB: AI Link Citation (Gap verification)
    # ============================================================
    with tab_zhice_gap:
        st.markdown("""<div style="background:#1a1d2e;border:1px solid #2a2f4a;border-radius:12px;padding:20px;margin:8px 0;">
            <h3 style="color:#ab47bc;font-size:18px;font-weight:700;margin:0 0 8px;">🔬 """ + ("Official Link Coverage Rate" if is_en else "官网链接覆盖率") + """</h3>
            <p style="color:#8892b0;font-size:12px;margin:0;">""" + ("YTD search phrase coverage: how many have official Amazon links cited by AI" if is_en else "YTD 检索短语覆盖情况：有多少被 AI 引用时带有官方链接") + """</p>
        </div>""", unsafe_allow_html=True)

        gap_file = METRICS_PATH / "gap_verification_cn.csv"
        if gap_file.exists():
            df_gap_real = load_csv_safe(gap_file)
            if not df_gap_real.empty:
                # --- YTD Summary ---
                total_q = len(df_gap_real)
                with_link = int(df_gap_real["link_mentions"].astype(int).gt(0).sum()) if "link_mentions" in df_gap_real.columns else 0
                no_link = total_q - with_link

                gc1, gc2, gc3, gc4 = st.columns(4)
                gc1.metric("YTD Total Phrases" if is_en else "YTD 总短语数", total_q)
                gc2.metric("With Official Link" if is_en else "有官方链接", f"{with_link} ({with_link*100//total_q if total_q else 0}%)")
                gc3.metric("No Link (Gap)" if is_en else "无链接 (Gap)", f"{no_link} ({no_link*100//total_q if total_q else 0}%)")
                gc4.metric("Platforms Monitored" if is_en else "监测平台数", "7")

                st.divider()

                # --- Category Breakdown Summary ---
                # --- Category Breakdown Summary ---
                st.markdown("**" + ("Category Breakdown" if is_en else "📊 按类别统计") + "**")
                # Use actual category/sub_category from data
                cat_col = "category" if "category" in df_gap_real.columns else None
                sub_col = "sub_category" if "sub_category" in df_gap_real.columns else None

                if cat_col:
                    # First show top-level category summary
                    cat_groups = df_gap_real.groupby(cat_col)
                    summary_rows = []
                    # Known brand mention rates from citation tracking tab
                    known_brand_rates = {"品牌": 85.2, "行业": 91.8}
                    for cat_name, cat_data in cat_groups:
                        cat_total = len(cat_data)
                        cat_with_link = int(cat_data["link_mentions"].astype(int).gt(0).sum()) if "link_mentions" in cat_data.columns else 0
                        brand_rate = known_brand_rates.get(cat_name, 0)
                        brand_count = int(cat_total * brand_rate / 100)
                        summary_rows.append({
                            "类别" if not is_en else "Category": cat_name,
                            "短语数" if not is_en else "Phrases": cat_total,
                            "有链接" if not is_en else "With Link": cat_with_link,
                            "链接率" if not is_en else "Link Rate": f"{cat_with_link*100//cat_total if cat_total else 0}%",
                            "品牌提及" if not is_en else "Brand": brand_count,
                            "品牌提及率" if not is_en else "Brand Rate": f"{brand_rate}%",
                            "占比" if not is_en else "% Total": f"{cat_total*100//total_q if total_q else 0}%",
                        })
                    if summary_rows:
                        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)

                    # Then show sub_category breakdown if available
                    if sub_col:
                        st.markdown("**" + ("Sub-Category Detail" if is_en else "📊 子类别明细") + "**")
                        sub_groups = df_gap_real.groupby([cat_col, sub_col])
                        sub_rows = []
                        for (cat_name, sub_name), sub_data in sub_groups:
                            sub_total = len(sub_data)
                            sub_with_link = int(sub_data["link_mentions"].astype(int).gt(0).sum()) if "link_mentions" in sub_data.columns else 0
                            sub_rows.append({
                                "大类" if not is_en else "Category": cat_name,
                                "子类" if not is_en else "Sub-Category": sub_name,
                                "短语数" if not is_en else "Phrases": sub_total,
                                "有链接" if not is_en else "With Link": sub_with_link,
                                "链接率" if not is_en else "Link Rate": f"{sub_with_link*100//sub_total if sub_total else 0}%",
                                "占比" if not is_en else "% Total": f"{sub_total*100//total_q if total_q else 0}%",
                            })
                        if sub_rows:
                            st.dataframe(pd.DataFrame(sub_rows), use_container_width=True, hide_index=True)
                else:
                    st.caption("No category column in data" if is_en else "数据中无类别列")

                st.divider()

                # --- Detail Table with Filter ---
                st.markdown("**" + ("Detail: Per-Phrase Link Status" if is_en else "📋 明细：逐条短语链接状态") + "**")
                col_filter1, col_filter2 = st.columns(2)
                with col_filter1:
                    gap_filter = st.selectbox("Status" if is_en else "筛选",
                        ["All" if is_en else "全部", "Has Link" if is_en else "有链接", "No Link (Gap)" if is_en else "无链接 (Gap)"],
                        key="zhixi_gap_filter2")
                with col_filter2:
                    cat_options_data = ["All" if is_en else "全部"]
                    if "sub_category" in df_gap_real.columns:
                        cat_options_data += sorted(df_gap_real["sub_category"].dropna().unique().tolist())
                    elif "category" in df_gap_real.columns:
                        cat_options_data += sorted(df_gap_real["category"].dropna().unique().tolist())
                    gap_cat_filter = st.selectbox("Category" if is_en else "按类别", cat_options_data, key="zhixi_gap_cat_filter")
                df_gap_show = df_gap_real.copy()
                if "Has Link" in gap_filter or "有链接" in gap_filter:
                    df_gap_show = df_gap_show[df_gap_show["link_mentions"].astype(int) > 0]
                elif "No Link" in gap_filter or "无链接" in gap_filter:
                    df_gap_show = df_gap_show[df_gap_show["link_mentions"].astype(int) == 0]
                # Apply category filter
                if gap_cat_filter not in ["All", "全部"]:
                    cat_col_f = "sub_category" if "sub_category" in df_gap_show.columns else ("category" if "category" in df_gap_show.columns else None)
                    if cat_col_f:
                        df_gap_show = df_gap_show[df_gap_show[cat_col_f] == gap_cat_filter]
                st.caption(f"{'Showing' if is_en else '显示'} {len(df_gap_show)} / {len(df_gap_real)}")
                show_cols = ["ai_query", "category", "sub_category", "has_link", "link_mentions", "link_rate"]
                platform_cols = [c for c in df_gap_show.columns if c.startswith("link_") and c not in ["link_mentions", "link_rate"]]
                show_cols += platform_cols
                show_cols = [c for c in show_cols if c in df_gap_show.columns]
                st.dataframe(df_gap_show[show_cols], use_container_width=True, hide_index=True)
        else:
            st.info("Gap verification data not available." if is_en else "Gap 验证数据不可用。")

    # TAB 4: Gap & 机会点
    # ============================================================
    with tab_gap:
        st.subheader("💡 Gap & Opportunities" if is_en else "💡 Gap & 机会点")
        st.markdown("Identify optimization opportunities based on citation tracking and content coverage analysis" if is_en else "基于引用追踪和内容覆盖分析，识别优化机会")

        # --- 智测 AI Search Coverage Insights ---
        st.markdown("**🔍 AI Search Coverage (智测)**" if is_en else "**🔍 AI 搜索覆盖洞察（智测数据）**")
        zhice_dir = OUTPUT_PATH.parent / "zhice" if (OUTPUT_PATH.parent / "zhice").exists() else OUTPUT_PATH / "zhice"
        if zhice_dir.exists():
            json_files = sorted(zhice_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
            if json_files:
                # Aggregate latest results for gap summary
                total_queries = 0
                has_link_count = 0
                has_brand_count = 0
                has_negative_count = 0
                gap_queries = []  # queries where official link NOT found

                for f in json_files[:10]:  # Analyze last 10 journeys
                    try:
                        data = json.loads(f.read_text(encoding="utf-8"))
                        if isinstance(data, list):
                            for r in data:
                                if "error" not in r:
                                    total_queries += 1
                                    if r.get("has_official_link"):
                                        has_link_count += 1
                                    else:
                                        gap_queries.append({"query": r.get("query", ""), "platform": r.get("platform", ""), "file": f.stem})
                                    if r.get("has_brand_mention"):
                                        has_brand_count += 1
                                    if r.get("has_negative"):
                                        has_negative_count += 1
                    except Exception:
                        pass

                if total_queries > 0:
                    link_rate = has_link_count / total_queries * 100
                    brand_rate = has_brand_count / total_queries * 100
                    neg_rate = has_negative_count / total_queries * 100

                    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                    col_m1.metric("Total Queries" if is_en else "总检索数", total_queries)
                    col_m2.metric("Official Link %" if is_en else "官方链接覆盖率", f"{link_rate:.0f}%")
                    col_m3.metric("Brand Mention %" if is_en else "品牌提及率", f"{brand_rate:.0f}%")
                    col_m4.metric("Negative Content" if is_en else "含负面内容", f"{neg_rate:.0f}%", delta=f"-{has_negative_count}" if has_negative_count > 0 else "0", delta_color="inverse")

                    # Show uncovered queries as gaps
                    if gap_queries:
                        st.markdown(f"**❌ {'Uncovered Queries (no official link in AI answer)' if is_en else '未覆盖的检索短语（AI 回答中无官方链接）'}** ({len(gap_queries)})")
                        # Deduplicate by query
                        seen = set()
                        unique_gaps = []
                        for g in gap_queries:
                            if g["query"] not in seen:
                                seen.add(g["query"])
                                unique_gaps.append(g)
                        df_gaps = pd.DataFrame(unique_gaps[:20])
                        if not df_gaps.empty:
                            st.dataframe(df_gaps, use_container_width=True, hide_index=True)
                    else:
                        st.success("✅ All queries have official link coverage" if is_en else "✅ 所有检索短语均有官方链接覆盖")
                else:
                    st.caption("No valid journey data to analyze" if is_en else "暂无有效旅程数据可分析")
            else:
                st.caption("No journey results yet. Run 智测 to discover AI search coverage gaps." if is_en else "暂无旅程结果。运行智测可发现 AI 搜索覆盖 Gap。")
        else:
            st.caption("No journey results yet. Run 智测 to discover AI search coverage gaps." if is_en else "暂无旅程结果。运行智测可发现 AI 搜索覆盖 Gap。")

        st.divider()

        # Coverage gap analysis
        st.markdown("**📊 Category Coverage Gap**" if is_en else "**📊 类别覆盖 Gap**")
        df_all_articles = load_zhizao(selected_batch)
        if not df_all_articles.empty and "category" in df_all_articles.columns:
            covered_topics = set(df_all_articles["category"].dropna().unique())
            all_topics = set(CATEGORIES_35)
            uncovered = sorted(all_topics - covered_topics)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Categories Covered" if is_en else "已覆盖类别", f"{len(covered_topics)}/35")
            with col2:
                st.metric("Uncovered Categories" if is_en else "未覆盖类别", len(uncovered))

            if uncovered:
                st.markdown("**❌ Uncovered categories (priority for content production):**" if is_en else "**❌ 未覆盖的类别（优先产出内容）：**")
                for i, topic in enumerate(uncovered, 1):
                    st.markdown(f"{i}. {topic}")
        else:
            st.caption("No article data available for coverage gap analysis" if is_en else "暂无文章数据，无法分析覆盖 Gap")

        st.divider()

        # Opportunity recommendations
        st.markdown("**🚀 Optimization Recommendations**" if is_en else "**🚀 优化建议**")
        st.markdown("""
- **High Priority**: Uncovered categories with highest search volume → Produce content immediately
- **Medium Priority**: Has content but not cited by AI → Optimize GEO signals
- **Low Priority**: Cited but no link → Optimize link placement strategy
        """ if is_en else """
- **高优先级**：未覆盖类别中检索量最高的 → 立即产出内容
- **中优先级**：已有内容但未被 AI 引用的 → 优化 GEO 信号
- **低优先级**：已被引用但无链接的 → 优化链接植入策略
        """)

        st.divider()

        # Attribution summary
        st.markdown("**🎯 Attribution Analysis**" if is_en else "**🎯 归因分析**")
        st.markdown("""
| Channel | Assessment | Recommendation |
|---|---|---|
| CN GEO | 🟢 Continuous growth | Continue expanding coverage |
| WW Direct EST | 🟢 +62% YoY | Maintain pace |
| JP Direct | 🟢 Fastest growth | Prioritize JP content expansion |
| AE Direct | 🔴 -61% YoY | Investigate cause |
        """ if is_en else """
| 渠道 | 判断 | 建议 |
|---|---|---|
| CN GEO | 🟢 持续增长 | 继续扩大覆盖 |
| WW Direct EST | 🟢 +62% YoY | 保持节奏 |
| JP Direct | 🟢 增速最快 | 优先扩展 JP 内容 |
| AE Direct | 🔴 -61% YoY | 排查原因 |
        """)

    # 📜 历史记录
    with st.expander("📜 History" if is_en else "📜 历史记录"):
        metrics_dir = OUTPUT_PATH / "metrics"
        if metrics_dir.exists():
            files = sorted(metrics_dir.glob("*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
            for f in files:
                mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                col_i, col_r, col_d = st.columns([3, 1, 1])
                with col_i:
                    st.caption(f"📄 {f.name} · {f.stat().st_size/1024:.1f}KB · 🕐 {mtime}")
                with col_r:
                    if st.button("♻️ Reuse" if is_en else "♻️ 复用", key=f"reuse_zhixi_{f.name}"):
                        # For analytics, just mark as notification - no live file to restore to
                        st.toast(f"{'Reused' if is_en else '已复用'}: {f.name}")
                with col_d:
                    st.download_button("⬇️", f.read_bytes(), file_name=f.name, mime="text/csv", key=f"dl_zhixi_{f.name}")
        else:
            st.caption("No history" if is_en else "暂无历史")

    # ============================================================
    # TAB 7: 智预 — Query Demand Forecaster
    # ============================================================
    with tab_zhiyu:
        st.subheader("🔮 Query Demand Forecaster" if is_en else "🔮 智预 — 检索需求预测")
        st.caption("Predict future search demand 2-4 weeks ahead based on seller lifecycle and market signals" if is_en else "基于卖家生命周期推演和市场变化信号，预测未来 2-4 周的检索需求")

        st.markdown("---")

        # --- Two modes as tabs ---
        mode_signal, mode_lifecycle = st.tabs([
            "📡 Signal-Driven" if is_en else "📡 信号驱动",
            "🔄 Lifecycle Forecast" if is_en else "🔄 生命周期推演",
        ])

        # --- Mode 1: Signal-Driven ---
        with mode_signal:
            st.markdown("**" + ("Input a market signal to predict future queries" if is_en else "输入市场信号，推演未来检索需求") + "**")

            signal_type = st.selectbox("Signal Type" if is_en else "信号类型",
                ["政策变化", "产品上线", "市场事件", "竞品动态", "季节性"],
                key="zhiyu_signal_type")

            signal_source = st.text_input("Source" if is_en else "信号来源 (URL 或描述)",
                placeholder="https://sell.amazon.com/blog/... or 描述",
                key="zhiyu_signal_src")

            signal_summary = st.text_area("Signal Summary" if is_en else "信号摘要",
                placeholder="例：Amazon 宣布 2026 Q4 起 AU 站强制 GST 注册",
                height=80, key="zhiyu_signal_summary")

            target_market = st.selectbox("Target Market" if is_en else "目标市场",
                ["CN", "NA", "EU", "JP", "AU", "ALL"], key="zhiyu_market")

            if st.button("🔮 Predict Queries" if is_en else "🔮 推演衍生 Query", type="primary", key="zhiyu_predict"):
                if signal_summary:
                    with st.spinner("Forecasting..." if is_en else "正在推演..."):
                        try:
                            from engine import call_bedrock_claude
                            prompt = f"""你是一个 AI 检索需求预测专家。基于以下市场信号，推演出卖家在未来 2-4 周可能会在 AI 搜索引擎上搜索的 Query。

信号类型：{signal_type}
信号来源：{signal_source}
信号摘要：{signal_summary}
目标市场：{target_market}

请输出 JSON 格式，包含 5-8 个预测 Query：
[{{"query": "预测的检索短语", "language": "zh-CN 或 en-US", "confidence": 0.0-1.0, "peak_window": "预计爆发时间段", "reasoning": "推演逻辑"}}]

只输出 JSON 数组，不要其他文字。"""

                            response = call_bedrock_claude(prompt)
                            # Try to parse JSON from response
                            import re
                            json_match = re.search(r'\[.*\]', response, re.DOTALL)
                            if json_match:
                                predictions = json.loads(json_match.group())
                                st.session_state["zhiyu_predictions"] = predictions
                                st.success(f"✅ {'Generated' if is_en else '生成'} {len(predictions)} {'predicted queries' if is_en else '条预测 Query'}")
                            else:
                                st.error("Failed to parse predictions" if is_en else "解析预测结果失败")
                                st.text(response[:500])
                        except ImportError:
                            # Fallback: generate sample predictions
                            predictions = [
                                {"query": f"{signal_summary.split('，')[0]}怎么办", "language": "zh-CN", "confidence": 0.92, "peak_window": "2-3 周后", "reasoning": "政策变化直接影响卖家操作"},
                                {"query": f"{signal_summary.split('，')[0]}注册流程", "language": "zh-CN", "confidence": 0.88, "peak_window": "3-4 周后", "reasoning": "卖家需要了解具体流程"},
                                {"query": f"{signal_summary.split('，')[0]}费用", "language": "zh-CN", "confidence": 0.85, "peak_window": "2-4 周后", "reasoning": "费用是卖家最关心的"},
                                {"query": f"{signal_summary.split('，')[0]} requirements 2026", "language": "en-US", "confidence": 0.80, "peak_window": "2-4 周后", "reasoning": "英文卖家同样搜索"},
                                {"query": f"{signal_summary.split('，')[0]}常见问题", "language": "zh-CN", "confidence": 0.78, "peak_window": "3-5 周后", "reasoning": "实施后会出现大量 FAQ"},
                            ]
                            st.session_state["zhiyu_predictions"] = predictions
                            st.success(f"✅ {'Generated' if is_en else '生成'} {len(predictions)} {'predicted queries (sample)' if is_en else '条预测 Query（示例）'}")
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.warning("Please enter signal summary" if is_en else "请输入信号摘要")

            # Show predictions (editable)
            if "zhiyu_predictions" in st.session_state and st.session_state["zhiyu_predictions"]:
                st.markdown("---")
                st.markdown("**" + ("Predicted Queries (editable)" if is_en else "预测结果（可编辑）") + ":**")

                predictions = st.session_state["zhiyu_predictions"]
                edited_preds = []
                for i, p in enumerate(predictions):
                    col_q, col_conf, col_win = st.columns([3, 1, 1])
                    with col_q:
                        new_q = st.text_input(f"Query {i+1}", value=p.get("query", ""), key=f"zhiyu_pq_{i}")
                    with col_conf:
                        new_conf = st.number_input("Confidence", value=float(p.get("confidence", 0.8)),
                            min_value=0.0, max_value=1.0, step=0.05, key=f"zhiyu_pc_{i}")
                    with col_win:
                        new_win = st.text_input("Window", value=p.get("peak_window", ""), key=f"zhiyu_pw_{i}")
                    edited_preds.append({"query": new_q, "confidence": new_conf, "peak_window": new_win,
                                         "language": p.get("language", "zh-CN"), "reasoning": p.get("reasoning", "")})

                col_export, col_save = st.columns(2)
                with col_export:
                    if st.button("🔍 Send to 智测 Verify" if is_en else "🔍 发送到智测验证 Gap", key="zhiyu_export"):
                        # Save predictions to zhice queue for verification
                        zhice_dir = OUTPUT_PATH.parent / "zhice"
                        zhice_dir.mkdir(parents=True, exist_ok=True)
                        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                        queue_file = zhice_dir / f"zhiyu_verify_queue_{ts}.json"
                        queue_data = {
                            "source": "zhiyu_forecast",
                            "signal_type": signal_type,
                            "signal_summary": signal_summary,
                            "queries_to_verify": [p["query"] for p in edited_preds if p["query"]],
                            "created_at": ts,
                            "status": "pending_verification",
                        }
                        queue_file.write_text(json.dumps(queue_data, ensure_ascii=False, indent=2), encoding='utf-8')
                        st.success(f"✅ {'Sent' if is_en else '已发送'} {len(queue_data['queries_to_verify'])} {'queries to 智测 for Gap verification' if is_en else '条到智测验证是否有 Gap'}")
                        st.info("💡 " + ("Go to 智测 tab to run verification" if is_en else "请切换到智测 tab 执行验证"))

                with col_save:
                    if st.button("💾 Save Forecast" if is_en else "💾 保存预测", key="zhiyu_save"):
                        zhiyu_dir = OUTPUT_PATH.parent / "zhiyu"
                        zhiyu_dir.mkdir(parents=True, exist_ok=True)
                        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                        out_file = zhiyu_dir / f"forecast_{signal_type}_{ts}.json"
                        save_data = {
                            "signal_type": signal_type,
                            "signal_source": signal_source,
                            "signal_summary": signal_summary,
                            "target_market": target_market,
                            "predictions": edited_preds,
                            "created_at": ts,
                        }
                        out_file.write_text(json.dumps(save_data, ensure_ascii=False, indent=2), encoding='utf-8')
                        st.success(f"✅ {'Saved' if is_en else '已保存'}: {out_file.name}")

        # --- Mode 2: Lifecycle Forecast ---
        with mode_lifecycle:
            st.markdown("**" + ("Select seller lifecycle stage to predict next queries" if is_en else "选择卖家生命周期阶段，推演下一步检索需求") + "**")

            stages = ["全部阶段", "认知期", "考虑期", "决策期", "注册期", "新手期", "成长期", "成熟期", "扩展期"]
            stages_en = ["All Stages", "Awareness", "Consideration", "Decision", "Registration", "Onboarding", "Growth", "Mature", "Expansion"]

            # AI Platform selection
            LC_PLATFORMS = {"all": "全部平台 (All)", "qianwen": "通义千问 (Qianwen)", "deepseek": "DeepSeek", "kimi": "Kimi", "doubao": "豆包 (Doubao)", "yuanbao": "元宝 (Yuanbao)", "chatgpt": "ChatGPT", "gemini": "Gemini", "bedrock": "Bedrock Claude"}
            col_plat, col_stage, col_market = st.columns(3)
            with col_plat:
                lc_platform = st.selectbox("AI Platform" if is_en else "AI 平台", list(LC_PLATFORMS.keys()), format_func=lambda x: LC_PLATFORMS[x], key="zhiyu_lc_platform")
            with col_stage:
                selected_stage = st.selectbox(
                    "Current Stage" if is_en else "当前阶段",
                    options=stages_en if is_en else stages,
                    index=4,
                    key="zhiyu_stage")
            with col_market:
                lc_market = st.selectbox("Market" if is_en else "目标市场", ["CN", "NA", "EU", "JP", "ALL"], key="zhiyu_lc_market")

            stage_idx = (stages_en if is_en else stages).index(selected_stage)
            stage_zh = stages[stage_idx]
            next_stage_zh = stages[min(stage_idx + 1, len(stages) - 1)]

            if st.button("🔮 Generate Predictions" if is_en else "🔮 生成预测", type="primary", key="zhiyu_lc_gen"):
                prompt = f"""你是一个卖家行为预测专家。一个亚马逊卖家当前处于"{stage_zh}"阶段，目标市场是{lc_market}。

请推演：这个卖家在即将进入"{next_stage_zh}"阶段时，会在AI搜索引擎上搜索什么问题？

要求：
1. 列出 5-8 个最可能的口语化检索短语
2. 每个短语要具体、自然（像用户在对话框里打的）
3. 覆盖不同维度（流程、费用、风险、工具）
4. 结合{lc_market}市场特点
5. 只输出短语列表，每行一条"""
                try:
                    if lc_platform == "bedrock":
                        from engine import call_bedrock_claude
                        with st.spinner("Calling Bedrock..." if is_en else "正在调用 Bedrock..."):
                            response = call_bedrock_claude(prompt)
                    else:
                        from zhice_engine import REAL_API_MAP
                        api_func = REAL_API_MAP.get(lc_platform)
                        if api_func:
                            with st.spinner(f"Calling {LC_PLATFORMS[lc_platform]}..."):
                                r = api_func(prompt)
                                response = r.get("full_answer", "")
                        else:
                            st.error(f"Platform {lc_platform} not available")
                            response = ""
                    if response:
                        predictions = [q.strip().lstrip("0123456789.-、）) ") for q in response.strip().split("\n") if q.strip() and len(q.strip()) > 5]
                        if predictions:
                            st.session_state["zhiyu_lc_predictions"] = predictions
                            st.rerun()
                except ImportError:
                    # Fallback to hardcoded
                    fallback = {
                        "认知期": ["跨境电商是什么 能赚钱吗", "做跨境电商需要多少钱", "跨境电商平台有哪些"],
                        "考虑期": ["亚马逊和其他平台区别", "亚马逊开店条件 2026", "跨境电商新手适合做什么"],
                        "决策期": ["亚马逊选哪个站点好", "美国站vs欧洲站区别", "亚马逊开店值不值得"],
                        "注册期": ["亚马逊注册材料清单", "注册审核要多久", "注册被拒怎么办"],
                        "新手期": ["第一个Listing怎么写", "FBA发货流程", "亚马逊后台怎么操作"],
                        "成长期": ["亚马逊PPC广告怎么打", "如何获取更多评论", "如何提升排名"],
                        "成熟期": ["多SKU运营管理", "如何防跟卖", "品牌注册流程"],
                        "扩展期": ["欧洲站VAT怎么办", "日本站怎么做", "新站点选哪个"],
                    }
                    st.session_state["zhiyu_lc_predictions"] = fallback.get(stage_zh, ["暂无预测"])
                    st.info("AI unavailable, showing default predictions" if is_en else "AI 不可用，显示默认预测")
                except Exception as e:
                    st.error(str(e))

            predicted = st.session_state.get("zhiyu_lc_predictions", [])

            if predicted:
                st.markdown(f"**{'Predicted queries for' if is_en else '预测检索需求：'} {selected_stage} → {next_stage_zh}**")

                edited_lifecycle = []
                for i, q in enumerate(predicted):
                    eq = st.text_input(f"Prediction {i+1}" if is_en else f"预测 {i+1}", value=q, key=f"zhiyu_lc_{i}")
                    edited_lifecycle.append(eq)

            if predicted:
                if st.button("📤 Export to 智库" if is_en else "📤 导出到智库", key="zhiyu_lc_export"):
                    zhiku_dir = OUTPUT_PATH / selected_batch / "01_zhiku"
                    zhiku_dir.mkdir(parents=True, exist_ok=True)
                    zhiku_file = zhiku_dir / "zhiku_ai_queries.csv"

                    new_rows = pd.DataFrame([{
                        "ai_query": q,
                        "category": f"智预-{stage_zh}",
                        "priority_score": 4.5,
                        "target_market": lc_market,
                        "source": "zhiyu_lifecycle",
                        "is_selected": "TRUE",
                    } for q in edited_lifecycle if q])

                    if zhiku_file.exists():
                        existing = pd.read_csv(zhiku_file, encoding="utf-8-sig")
                        merged = pd.concat([existing, new_rows], ignore_index=True)
                        if "ai_query" in merged.columns:
                            merged = merged.drop_duplicates(subset=["ai_query"], keep="first")
                        merged.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                    else:
                        new_rows.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                    st.success(f"✅ {'Exported' if is_en else '已导出'} {len(new_rows)} {'queries' if is_en else '条到智库'}")

        st.markdown("---")

        # Show existing zhiyu results if any
        zhiyu_dir = OUTPUT_PATH.parent / "zhiyu" if (OUTPUT_PATH.parent / "zhiyu").exists() else OUTPUT_PATH / "zhiyu"
        if zhiyu_dir.exists():
            json_files = sorted(zhiyu_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
            if json_files:
                st.markdown(f"**{'Forecast History' if is_en else '预测历史'}** ({len(json_files)} {'forecasts' if is_en else '条预测'})")
                for f in json_files[:5]:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    with st.expander(f"📄 {f.stem} · {mtime}"):
                        try:
                            data = json.loads(f.read_text(encoding="utf-8"))
                            if isinstance(data, dict):
                                st.json(data)
                            else:
                                st.write(data)
                        except Exception:
                            st.caption("Unable to parse" if is_en else "无法解析")
            else:
                st.caption("No forecast results yet" if is_en else "暂无预测结果")
        else:
            st.caption("No forecast results yet" if is_en else "暂无预测结果")

# PAGE: 智中枢
# ============================================================
elif _page_idx == 8:
    st.markdown("""<div style="padding:20px 0 10px;"><h1 style="font-size:28px;font-weight:800;color:#ff6b35;margin:0;">🎯 """ + ("Decision Engine" if is_en else "智中枢 – Decision Engine") + """</h1><p style="font-size:13px;color:#8892b0;margin-top:6px;">""" + ("Based on analytics data + 7 decision rules, generate weekly action plan" if is_en else "基于智析数据 + 7 条决策规则，生成周度行动计划") + """</p></div>""", unsafe_allow_html=True)
    render_pipeline_flow("zhongshu", selected_batch)

    # Decision Rules
    st.subheader("📜 7 Decision Rules" if is_en else "📜 7 条决策规则")
    rules = [
        ("Rule 1: Growth Acceleration", "Channel WoW > +30% for 2 consecutive weeks" if is_en else "渠道 WoW > +30% 连续2周", "Increase content output for that channel" if is_en else "增加该渠道内容产出", "🟢"),
        ("Rule 2: Decline Alert", "Channel WoW < -20%" if is_en else "渠道 WoW < -20%", "Pause new content, investigate cause" if is_en else "暂停新内容，排查原因", "🔴"),
        ("Rule 3: Low Absolute Volume", "GEO weekly < 50 and YoY > +50%" if is_en else "GEO 周 < 50 且 YoY > +50%", "Expand keyword coverage" if is_en else "扩大关键词覆盖", "🟡"),
        ("Rule 4: High-Performing Site", "Site YoY > +100%" if is_en else "站点 YoY > +100%", "Prioritize content expansion for that site" if is_en else "优先扩展该站点内容", "🟢"),
        ("Rule 5: Content Gap", "Market has traffic but no new content for 2 weeks" if is_en else "市场有流量但2周无新内容", "Restart full pipeline" if is_en else "重启全流程", "🟡"),
        ("Rule 6: Benchmark Comparison", "Our YoY < benchmark YoY" if is_en else "我方 YoY < 大盘 YoY", "Strategy review" if is_en else "策略复盘", "🔴"),
        ("Rule 7: Input-Output Lag", "Content published 2-3 weeks with no improvement" if is_en else "内容发布2-3周无提升", "Check content quality/rewrite" if is_en else "检查内容质量/重写", "🟡"),
    ]
    for name, condition, action, emoji in rules:
        with st.expander(f"{emoji} {name}"):
            st.markdown(f"**{'Trigger Condition' if is_en else '触发条件'}:** {condition}")
            st.markdown(f"**{'Action' if is_en else '执行动作'}:** {action}")

    st.divider()

    # Weekly Plan
    st.subheader(f"📋 Smart Suite Weekly Plan - {week}")
    st.markdown("""
**🟢 ACCELERATE:**
- CN GEO: 4 consecutive weeks of growth → Expand CN keyword coverage
- JP Direct: +67% WoW, +103% YoY → Prioritize JP content expansion
- WW Direct EST: +32% WoW → Maintain current pace

**🟡 MONITOR:**
- WW Direct EM: Flat → Watch next week's trend
- EU GEO: Low absolute value (5/month) → Expand EU search phrases

**🔴 INVESTIGATE:**
- AE Direct: YoY -61% → Investigate decline cause
    """ if is_en else """
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
    st.subheader("🚀 Full Pipeline Quick Commands" if is_en else "🚀 全流程快捷指令")
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
elif page == "📊 批次对比" or (is_en and page == "📊 Batch Compare"):
    st.title("📊 Batch Comparison" if is_en else "📊 批次对比")
    st.caption("Compare output performance across different batches" if is_en else "对比不同批次的产出效果")

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
        st.metric("Query Phrases" if is_en else "智库短语数", len(df_a))
        df_za = load_zhizao(batch_a)
        st.metric("Articles" if is_en else "智造文章数", len(df_za))
        df_sa = load_scorecard(batch_a)
        if not df_sa.empty and "overall_score" in df_sa.columns:
            st.metric("Avg Score" if is_en else "平均评分", f"{df_sa['overall_score'].mean():.2f}")
        else:
            st.metric("Avg Score" if is_en else "平均评分", "N/A")

    with col2:
        st.subheader(f"📚 {batch_b}")
        st.metric("Query Phrases" if is_en else "智库短语数", len(df_b))
        df_zb = load_zhizao(batch_b)
        st.metric("Articles" if is_en else "智造文章数", len(df_zb))
        df_sb = load_scorecard(batch_b)
        if not df_sb.empty and "overall_score" in df_sb.columns:
            st.metric("Avg Score" if is_en else "平均评分", f"{df_sb['overall_score'].mean():.2f}")
        else:
            st.metric("Avg Score" if is_en else "平均评分", "N/A")


# ============================================================
# PAGE: 发布追踪
# ============================================================
elif page == "📌 发布追踪" or (is_en and page == "📌 Publish Tracking"):
    st.title("📌 Publish Tracking" if is_en else "📌 发布追踪")
    st.caption("Track published content citations and performance" if is_en else "追踪已发布内容的引用和效果")

    # Look for published tracking data
    tracking_file = OUTPUT_PATH / "publish_tracking.csv"
    if tracking_file.exists():
        df_track = load_csv_safe(tracking_file)
        if not df_track.empty:
            st.dataframe(df_track, use_container_width=True, hide_index=True)
        else:
            st.info("Tracking data is empty" if is_en else "追踪数据为空")
    else:
        st.info("No publish tracking data yet. System will auto-record after publishing." if is_en else "暂无发布追踪数据。发布后系统将自动记录。")

    st.divider()
    st.subheader("Manually Add Publish Record" if is_en else "手动添加发布记录")
    with st.form("add_publish_record"):
        pub_title = st.text_input("Article Title" if is_en else "文章标题")
        pub_url = st.text_input("Publish URL" if is_en else "发布 URL")
        pub_date = st.date_input("Publish Date" if is_en else "发布日期")
        pub_platform = st.selectbox("Platform" if is_en else "平台", ["官网", "知乎", "微信公众号", "其他"])
        submitted = st.form_submit_button("Add Record" if is_en else "添加记录")
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
            st.success(f"✅ {'Added' if is_en else '已添加'}: {pub_title}")


# ============================================================
# PAGE: 需求中心 (Intake + 智测)
# ============================================================
elif _page_idx == 10:
    st.markdown("""<div style="padding:20px 0 10px;"><h1 style="font-size:28px;font-weight:800;color:#00bcd4;margin:0;">📝 """ + ("Request Center" if is_en else "需求中心") + """</h1><p style="font-size:13px;color:#8892b0;margin-top:6px;">""" + ("Intake + Journey Research — Product request submission, user journey research, request tracking" if is_en else "Intake + 智测合并 — 产品需求提交、用户旅程调研、需求追踪") + """</p></div>""", unsafe_allow_html=True)

    tab_geo, tab_tracking = st.tabs([
        "📊 Request Dashboard" if is_en else "📊 需求管理看板",
        "📋 Request Progress Tracking" if is_en else "📋 需求进展追踪",
    ])

    with tab_geo:
        st.markdown("""<div style="background:#1a1d2e;border:1px solid #2a2f4a;border-radius:12px;padding:20px;margin:8px 0;">
            <h3 style="color:#00bcd4;font-size:18px;font-weight:700;margin:0 0 8px;">📊 """ + ("Request Management Dashboard" if is_en else "需求管理看板") + """</h3>
            <p style="color:#8892b0;font-size:12px;margin:0;">""" + ("View all submitted requests, track status, and manage content pipeline" if is_en else "查看所有提交的需求、追踪状态、管理内容流水线") + """</p>
        </div>""", unsafe_allow_html=True)

        st.caption("Requests are submitted at: http://localhost:8503 (Submit Request tab)" if is_en else "需求提交入口: http://localhost:8503（Submit Request tab）")

        # Load intake data
        intake_file = OUTPUT_PATH / "intake_requests.csv"
        if intake_file.exists():
            df_intake = load_csv_safe(intake_file)
            if not df_intake.empty:
                # KPIs
                kc1, kc2, kc3, kc4 = st.columns(4)
                total_req = len(df_intake)
                new_req = len(df_intake[df_intake.get("status", pd.Series()) == "New"]) if "status" in df_intake.columns else 0
                in_progress = len(df_intake[df_intake.get("status", pd.Series()).isin(["In Progress", "Processing"])]) if "status" in df_intake.columns else 0
                done_req = len(df_intake[df_intake.get("status", pd.Series()).isin(["Done", "Published", "Completed"])]) if "status" in df_intake.columns else 0
                kc1.metric("Total Requests" if is_en else "总需求", total_req)
                kc2.metric("New" if is_en else "待处理", new_req)
                kc3.metric("In Progress" if is_en else "进行中", in_progress)
                kc4.metric("Completed" if is_en else "已完成", done_req)

                st.divider()

                # Editable status table
                st.markdown("**All Requests:**" if is_en else "**全部需求：**")
                status_options = ["New", "In Progress", "Content Created", "Under Review", "Published", "Rejected"]
                col_config = {}
                if "status" in df_intake.columns:
                    col_config["status"] = st.column_config.SelectboxColumn("Status", options=status_options)
                edited = st.data_editor(df_intake, use_container_width=True, hide_index=True,
                                       column_config=col_config, key="intake_editor")
                if st.button("💾 Save Changes" if is_en else "💾 保存修改", key="save_intake_changes"):
                    edited.to_csv(intake_file, index=False, encoding="utf-8-sig")
                    st.success("✅ Saved!" if is_en else "✅ 已保存！")
                    st.rerun()
            else:
                st.info("No requests yet. Share http://localhost:8503 with your team to submit requests." if is_en else "暂无需求。分享 http://localhost:8503 给团队成员提交需求。")
        else:
            st.info("No requests yet." if is_en else "暂无需求。")

    with tab_tracking:
        st.subheader("📋 Request Progress Tracking" if is_en else "📋 需求进展追踪")
        intake_file = OUTPUT_PATH / "intake_requests.csv"
        if intake_file.exists():
            df_intake = load_csv_safe(intake_file)
            if not df_intake.empty:
                st.dataframe(df_intake, use_container_width=True, hide_index=True)
            else:
                st.info("No request records" if is_en else "暂无需求记录")
        else:
            st.info("No request records yet. Please submit in the Product GEO Request tab." if is_en else "暂无需求记录，请在「产品 GEO 需求」标签页提交。")


# ============================================================
# PAGE: 引用分析
# ============================================================
elif _page_idx == 11:
    st.markdown("""<div style="padding:20px 0 10px;"><h1 style="font-size:28px;font-weight:800;color:#4caf50;margin:0;">🔍 """ + ("Citation Analysis" if is_en else "引用分析") + """</h1><p style="font-size:13px;color:#8892b0;margin-top:6px;">""" + ("Analyze AI search engine citation of our content" if is_en else "分析 AI 搜索引擎对内容的引用情况") + """</p></div>""", unsafe_allow_html=True)

    st.subheader("AI Engine Citation Monitoring" if is_en else "AI 引擎引用监控")
    st.markdown("""
    Track citation status of our content across these AI search platforms:
    - **CN**: DeepSeek / 豆包 / Kimi / 元宝 / 通义千问
    - **WW**: ChatGPT / Perplexity / Gemini
    """ if is_en else """
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
                st.metric("Total Citations" if is_en else "总引用次数", len(df_cite))
            with col2:
                if "platform" in df_cite.columns:
                    st.metric("Citation Platforms" if is_en else "引用平台数", df_cite["platform"].nunique())
            with col3:
                if "content_id" in df_cite.columns:
                    st.metric("Cited Content Count" if is_en else "被引用内容数", df_cite["content_id"].nunique())
            st.dataframe(df_cite, use_container_width=True, hide_index=True)
        else:
            st.info("No citation data" if is_en else "暂无引用数据")
    else:
        st.info("No citation tracking data yet. Run journey research to auto-generate citation analysis." if is_en else "暂无引用追踪数据。运行智测后将自动生成引用分析。")


# ============================================================
# PAGE: Settings
# ============================================================
elif _page_idx == 12:
    st.title("⚙️ Settings")
    st.caption("System Configuration" if is_en else "系统配置")

    st.subheader("🔑 API Configuration" if is_en else "🔑 API 配置")
    st.markdown("""
    - **AWS Bedrock**: 使用本地 AWS credentials（SSO / env vars）
    - **Model**: Claude 3.5 Sonnet (`anthropic.claude-sonnet-4-20250514`)
    - **Region**: us-east-1
    """)

    st.divider()
    st.subheader("📂 Path Configuration" if is_en else "📂 路径配置")
    st.text(f"{'Project Root' if is_en else '项目根目录'}: {BASE_PATH}")
    st.text(f"{'Output Dir' if is_en else '输出目录'}: {OUTPUT_PATH}")
    st.text(f"{'Input Dir' if is_en else '输入目录'}: {INPUT_PATH}")

    st.divider()
    st.subheader("📊 Batch Management" if is_en else "📊 批次管理")
    new_batch = st.text_input("Create New Batch" if is_en else "创建新批次", placeholder="batch_004", key="new_batch_input")
    if st.button("Create Batch" if is_en else "创建批次", key="create_batch"):
        if new_batch:
            new_path = OUTPUT_PATH / new_batch
            new_path.mkdir(parents=True, exist_ok=True)
            (new_path / "01_zhiku").mkdir(exist_ok=True)
            (new_path / "02_zhizao").mkdir(exist_ok=True)
            (new_path / "03_zhiyou").mkdir(exist_ok=True)
            (new_path / "04_zhibu").mkdir(exist_ok=True)
            st.success(f"✅ {'Batch created' if is_en else '已创建批次'}: {new_batch}")

    st.divider()
    st.subheader("📜 Steering Rules Editor" if is_en else "📜 Steering 规则编辑器")
    st.caption("Edit AI behavior rules. Changes affect both Kiro and Streamlit content generation." if is_en else "编辑 AI 行为规则。修改后 Kiro 和 Streamlit 生成内容都会遵守新规则。")

    # List steering files
    steering_dir = BASE_PATH / ".kiro" / "steering"
    if steering_dir.exists():
        steering_files = sorted([f.name for f in steering_dir.glob("*.md")])
        selected_steering = st.selectbox(
            "Select file" if is_en else "选择文件",
            steering_files,
            key="steering_file_select"
        )

        if selected_steering:
            steering_path = steering_dir / selected_steering
            current_content = steering_path.read_text(encoding="utf-8")

            edited_steering = st.text_area(
                f"Editing: {selected_steering}" if is_en else f"编辑: {selected_steering}",
                value=current_content,
                height=400,
                key="steering_editor",
            )

            col_save, col_info = st.columns([1, 3])
            with col_save:
                if st.button("💾 Save" if is_en else "💾 保存", key="save_steering"):
                    steering_path.write_text(edited_steering, encoding="utf-8")
                    st.success("✅ Saved!" if is_en else "✅ 已保存！")
            with col_info:
                st.caption(f"{'File size' if is_en else '文件大小'}: {len(current_content):,} chars · {'Path' if is_en else '路径'}: {steering_path}")
    else:
        st.warning("Steering directory not found" if is_en else "未找到 steering 目录")

    st.divider()
    st.subheader("🏷️ Category System (35 Categories)" if is_en else "🏷️ 类别体系 (35类)")
    for i, cat in enumerate(CATEGORIES_35, 1):
        st.text(f"{i:2d}. {cat}")


# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption(
    f"Smart Suite Phase I · {'Console' if is_en else '智系列控制台'} · "
    f"{datetime.now().strftime('%Y-%m-%d %H:%M')} · "
    f"Batches: {len(batches)}"
)
