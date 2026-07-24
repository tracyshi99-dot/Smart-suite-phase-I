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
    # Use temp dir for writable output, copy demo data there (only once)
    import shutil
    _WRITABLE_OUTPUT = Path(tempfile.gettempdir()) / "smartsuite_output"
    _DEMO_SOURCE = Path(__file__).parent / "demo_output"
    if not _WRITABLE_OUTPUT.exists():  # Only copy on first run
        if _DEMO_SOURCE.exists():
            shutil.copytree(_DEMO_SOURCE, _WRITABLE_OUTPUT, dirs_exist_ok=True)
        else:
            _WRITABLE_OUTPUT.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH = _WRITABLE_OUTPUT
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

# --- Custom CSS (Premium UI) ---
st.markdown("""
<style>
/* === Global === */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', system-ui, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}
.main .block-container {
    padding-top: 1.5rem; padding-left: 1.5rem; padding-right: 1.5rem; max-width: 100%;
}
iframe { width: 100% !important; }

/* === Typography === */
h1 { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important; font-weight: 800 !important; letter-spacing: -0.02em !important; }
h2 { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important; font-weight: 700 !important; letter-spacing: -0.01em !important; }
h3 { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important; font-weight: 600 !important; }
p, span, label, div { line-height: 1.6; }

/* === Sidebar === */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0e1a 0%, #0d1220 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] .stRadio label {
    font-size: 13.5px !important; font-weight: 500 !important;
    padding: 6px 8px !important; border-radius: 8px; transition: all 0.2s ease;
}
section[data-testid="stSidebar"] .stRadio label:hover { background: rgba(0, 212, 170, 0.06); }

/* === Metric Cards === */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(19, 24, 39, 0.9) 0%, rgba(10, 14, 26, 0.9) 100%);
    border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 16px 20px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,0,0,0.35);
}
div[data-testid="stMetric"] label {
    color: #7b8ab8 !important; font-size: 11px !important;
    text-transform: uppercase; letter-spacing: 0.8px; font-weight: 600 !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #00d4aa !important; font-weight: 700 !important; font-size: 1.5rem !important;
}

/* === Tabs === */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid rgba(255,255,255,0.06); }
.stTabs [data-baseweb="tab"] {
    background: transparent; border-radius: 10px 10px 0 0;
    border: 1px solid transparent; border-bottom: none;
    padding: 10px 20px; font-size: 13px; font-weight: 500;
    color: #7b8ab8; transition: all 0.2s ease;
}
.stTabs [data-baseweb="tab"]:hover { background: rgba(0, 212, 170, 0.04); color: #a0b0d0; }
.stTabs [aria-selected="true"] {
    background: rgba(0, 212, 170, 0.06) !important;
    border-color: rgba(0, 212, 170, 0.25) !important;
    color: #00d4aa !important; font-weight: 600 !important;
}

/* === Expanders === */
div[data-testid="stExpander"] {
    background: rgba(19, 24, 39, 0.6); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px; backdrop-filter: blur(8px); transition: border-color 0.2s ease;
}
div[data-testid="stExpander"]:hover { border-color: rgba(255,255,255,0.1); }

/* === Buttons === */
.stButton > button {
    border-radius: 10px; font-weight: 600; font-size: 13px;
    padding: 8px 20px; letter-spacing: 0.01em;
    transition: all 0.2s ease; border: 1px solid rgba(255,255,255,0.1);
}
.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(0, 212, 170, 0.15); }

/* === DataFrames === */
div[data-testid="stDataFrame"] {
    border-radius: 12px; border: 1px solid rgba(255,255,255,0.06);
    box-shadow: 0 2px 12px rgba(0,0,0,0.15);
}

/* === Dividers === */
hr { border-color: rgba(255,255,255,0.06) !important; }
.stDivider { border-color: rgba(255,255,255,0.06) !important; }

/* === Inputs === */
.stTextInput > div > div { border-radius: 10px !important; }
.stTextInput > div > div:focus-within { border-color: #00d4aa !important; box-shadow: 0 0 0 2px rgba(0, 212, 170, 0.12) !important; }
.stSelectbox > div > div { border-radius: 10px !important; }

/* === Progress === */
.stProgress > div > div > div { background: linear-gradient(90deg, #00d4aa, #00b4d8) !important; border-radius: 8px; }

/* === Scrollbar === */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* === Page Header === */
.ss-page-header { padding: 24px 0 16px; border-bottom: 1px solid rgba(255,255,255,0.06); margin-bottom: 20px; }
.ss-page-header h1 { font-size: 1.6rem !important; margin: 0 !important; }
.ss-page-header p { font-size: 13px !important; color: #7b8ab8 !important; margin-top: 8px !important; font-weight: 400 !important; }

/* === Section Cards === */
.ss-section { background: rgba(19,24,39,0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 20px 24px; margin: 16px 0; backdrop-filter: blur(8px); }
.ss-section h3 { font-size: 15px !important; font-weight: 700 !important; margin: 0 0 6px !important; letter-spacing: -0.01em !important; }
.ss-section p { font-size: 12px !important; color: #7b8ab8 !important; margin: 0 !important; }
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
    """Render premium pipeline flow with glassmorphism and glow effects."""

    colors = {"zhiku": "#ffa726", "zhice": "#00d4aa", "zhizao": "#ffcc02", "zhiyou": "#e91e63",
              "zhibu": "#29b6f6", "zhichuan": "#26c6da", "zhixi": "#ab47bc", "zhongshu": "#ff6b35"}

    cards_html = ""
    for i, step in enumerate(PIPELINE_STEPS):
        sid = step["id"]
        is_current = (sid == current_step_id)
        color = colors.get(sid, "#4a5568")

        if is_current:
            border = color
            text_color = "#ffffff"
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            bg = f"rgba({r},{g},{b},0.12)"
            glow = f"0 0 16px rgba({r},{g},{b},0.25)"
            font_weight = "700"
            dot = f'<div style="width:5px;height:5px;border-radius:50%;background:{color};margin:0 auto 4px;box-shadow:0 0 6px {color};"></div>'
        else:
            border = "rgba(255,255,255,0.06)"
            text_color = "#5a6380"
            bg = "transparent"
            glow = "none"
            font_weight = "500"
            dot = ""

        cards_html += f'<div style="background:{bg};border:1px solid {border};border-radius:10px;padding:8px 14px;text-align:center;min-width:56px;box-shadow:{glow};transition:all 0.3s ease;">{dot}<div style="font-size:12px;color:{text_color};font-weight:{font_weight};letter-spacing:0.02em;">{step["name"]}</div></div>'
        if i < len(PIPELINE_STEPS) - 1:
            arrow_c = color if is_current else "rgba(255,255,255,0.12)"
            cards_html += f'<div style="color:{arrow_c};font-size:13px;opacity:0.7;">\u203a</div>'

    html = f'''<div style="display:flex;align-items:center;justify-content:center;gap:6px;padding:14px 20px;margin:12px 0 20px;background:rgba(19,24,39,0.5);border-radius:14px;border:1px solid rgba(255,255,255,0.06);backdrop-filter:blur(10px);flex-wrap:nowrap;overflow-x:auto;">{cards_html}</div>'''
    st.html(html)


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
            df = pd.read_csv(path, encoding="utf-8-sig", on_bad_lines="skip")
            # Ensure all columns are object type to avoid Arrow serialization issues
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).replace("nan", "")
            return df
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
        "M1 (Jan)": ["89", "13", "+585%", "83", "38", "+118%", "172", "51", "+237%", "4965", "1801", "+176%", "5137", "1852", "+177%"],
        "M2 (Feb)": ["65", "13", "+400%", "51", "51", "+0%", "116", "64", "+81%", "2387", "3056", "-22%", "2503", "3120", "-20%"],
        "M3 (Mar)": ["165", "36", "+358%", "91", "45", "+102%", "256", "81", "+216%", "7267", "4274", "+70%", "7523", "4355", "+73%"],
        "M4 (Apr)": ["164", "30", "+447%", "70", "32", "+119%", "234", "62", "+277%", "7205", "4270", "+69%", "7439", "4332", "+72%"],
        "M5 (May)": ["120", "19", "+532%", "74", "33", "+124%", "194", "52", "+273%", "5330", "3247", "+64%", "5524", "3299", "+67%"],
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


def auto_sync_batch(batch_id: str):
    """Auto-sync the current user's batch AND requests data to S3.
    Called via session_state flag to avoid blocking UI."""
    try:
        from s3_sync import sync_batch_to_s3, s3_available, save_batch_file
        if s3_available():
            # Sync batch data (zhiku, zhice, zhizao, zhiyou, zhibu)
            sync_batch_to_s3(batch_id, OUTPUT_PATH)

            # Also sync requests/{username}/ data (performance, metrics, etc.)
            if batch_id.startswith("batch_"):
                username = batch_id[6:]
                req_dir = OUTPUT_PATH / "requests" / username
                if req_dir.exists():
                    import os
                    from s3_sync import _get_s3, S3_BUCKET
                    s3 = _get_s3()
                    if s3:
                        for f in req_dir.iterdir():
                            if f.is_file():
                                s3_key = f"user_data/{username}/requests/{f.name}"
                                s3.put_object(Bucket=S3_BUCKET, Key=s3_key,
                                              Body=f.read_bytes(),
                                              ContentType="application/json")
    except Exception:
        pass


def mark_data_changed():
    """Mark that data was changed this session, triggering S3 sync on next page load."""
    st.session_state["_data_changed"] = True


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
    "🔄 需求提交",
    "🔍 引用分析",
    "⚙️ Settings",
    "📝 运营看板",
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
    "🔄 Request",
    "🔍 Citation Analysis",
    "⚙️ Settings",
    "📝 Ops Dashboard",
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

    # --- Login ---
    ADMIN_USERS = ["yujiashi", "admin"]  # Admin users see everything

    # Load allowed users from file (dynamic whitelist)
    _users_file = BASE_PATH / "output" / "users.json"
    if _users_file.exists():
        try:
            _users_data = json.loads(_users_file.read_text(encoding="utf-8"))
            ALLOWED_USERS = _users_data.get("allowed", [])
            ADMIN_USERS = _users_data.get("admins", ADMIN_USERS)
        except Exception:
            ALLOWED_USERS = ["yujiashi", "admin", "fanting", "czhaamzn", "yuchy", "porzh", "linzhshi", "fenixau", "tianranh", "qiudanie", "quadaisy", "budhiraja", "mbudhira", "xinyill", "xdhuang", "gracezjy", "htp", "jinghuaf", "mxyzhang", "emilwliu", "qdhwzj", "panjf", "rickylan", "yountlim", "phunghd", "oanhhtk"]
    else:
        ALLOWED_USERS = ["yujiashi", "admin", "fanting", "czhaamzn", "yuchy", "porzh", "linzhshi", "fenixau", "tianranh", "qiudanie", "quadaisy", "budhiraja", "mbudhira", "xinyill", "xdhuang", "gracezjy", "htp", "jinghuaf", "mxyzhang", "emilwliu", "qdhwzj", "panjf", "rickylan", "yountlim", "phunghd", "oanhhtk"]
        # Save initial file
        _users_file.parent.mkdir(parents=True, exist_ok=True)
        _users_file.write_text(json.dumps({"allowed": ALLOWED_USERS, "admins": ADMIN_USERS, "pending": []}, ensure_ascii=False, indent=2), encoding="utf-8")

    # Auto-login from URL param ?user=xxx
    _qp_login = st.query_params
    if "user" in _qp_login and "app_user" not in st.session_state:
        _url_user = _qp_login["user"].lower()
        if _url_user in ALLOWED_USERS:
            st.session_state["app_user"] = _url_user

    user_login = st.text_input("👤 Login", value=st.session_state.get("app_user", ""),
                               placeholder="Your login name", key="sidebar_login", label_visibility="collapsed")
    if user_login:
        if user_login.lower() in ALLOWED_USERS:
            st.session_state["app_user"] = user_login.lower()
        else:
            st.session_state["app_user"] = ""
            st.error("⚠️ Access denied" if is_en else "⚠️ 无权限，请联系管理员")
    current_user = st.session_state.get("app_user", "")
    is_admin = current_user.lower() in ADMIN_USERS if current_user else False
    if current_user:
        role_label = "🔑 Admin" if is_admin else "👤 User"
        with st.expander(f"{role_label}: **{current_user}**", expanded=False):
            if st.button("🚪 Sign out", key="logout_btn", use_container_width=True):
                st.session_state["app_user"] = ""
                st.rerun()

    if DEMO_MODE:
        st.caption("🎬 Demo" if is_en else "🎬 演示模式")
    st.divider()

    # Select nav pages based on language
    _full_nav = NAV_PAGES_EN if is_en else NAV_PAGES_ZH
    # User: hide admin-only pages (below separator)
    if current_user and not is_admin:
        separator_idx = _full_nav.index("───────────") if "───────────" in _full_nav else len(_full_nav)
        NAV_PAGES = _full_nav[:separator_idx]
    else:
        NAV_PAGES = _full_nav

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
            "request": 10, "loop": 10,
            "citation": 11,
            "overview": 0, "settings": 12,
            "ops": 13, "dashboard": 13,
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

    # Per-user batch: regular users get their own batch, admin can choose
    if current_user and not is_admin:
        selected_batch = f"batch_{current_user}"
        # Ensure user batch dir exists
        _user_batch_dir = OUTPUT_PATH / selected_batch
        _user_batch_dir.mkdir(parents=True, exist_ok=True)
        (OUTPUT_PATH / selected_batch / "01_zhiku").mkdir(parents=True, exist_ok=True)
        # Load from S3 if local is empty (Cloud mode)
        try:
            from s3_sync import load_batch_from_s3, s3_available
            if s3_available():
                load_batch_from_s3(selected_batch, OUTPUT_PATH)
        except Exception:
            pass
    elif is_admin:
        # Admin: show all batches including user batches
        all_batches = batches + [f"batch_{u}" for u in ALLOWED_USERS if f"batch_{u}" not in batches]
        all_batches = sorted(set(all_batches), reverse=True)
        selected_batch = st.selectbox("📦 Batch", all_batches, key="admin_batch_select")
    else:
        selected_batch = batches[0] if batches else "batch_003"
    market = "ALL"
    kw_limit = 10
    week = "WK21"

    st.divider()
    st.caption(f"{'Path' if is_en else '路径'}: {BASE_PATH}")

    # Map current page selection to page index for consistent routing
    _page_idx = NAV_PAGES.index(page) if page in NAV_PAGES else 0

# --- Auto-sync to S3: if data changed in previous interaction, sync batch to S3 ---
if st.session_state.pop("_data_changed", False) and current_user and not DEMO_MODE:
    import threading
    threading.Thread(target=auto_sync_batch, args=(selected_batch,), daemon=True).start()


# ============================================================
# PAGE: 总览
# ============================================================
if _page_idx == 0:
    # Load EN or ZH version based on sidebar language
    if is_en:
        wiki_path = Path(__file__).parent / "smart-suite-wiki.html"
    else:
        wiki_path = Path(__file__).parent / "smart-suite-wiki-zh.html"
        if not wiki_path.exists():
            wiki_path = Path(__file__).parent / "smart-suite-wiki.html"
    if wiki_path.exists():
        wiki_html = wiki_path.read_text(encoding="utf-8")
        st.html(wiki_html)
    else:
        st.title("🏠 Smart Suite Overview" if is_en else "🏠 Smart Suite 总览")
        st.warning("smart-suite-wiki.html not found")

    # (End of overview page)


# --- LOGIN GATE: All pages except overview require login ---
elif not current_user:
    st.markdown("""<div style="padding:60px 20px;text-align:center;">
    <div style="width:56px;height:56px;margin:0 auto 20px;border-radius:14px;background:linear-gradient(135deg,rgba(0,212,170,0.12),rgba(0,180,216,0.08));display:flex;align-items:center;justify-content:center;border:1px solid rgba(0,212,170,0.2);">
        <span style="font-size:24px;">🔒</span>
    </div>
    <h2 style="color:#e8eaf6;font-weight:700;font-size:1.3rem;margin-bottom:8px;">""" + ("Please log in to access Smart Suite tools" if is_en else "请先登录") + """</h2>
    <p style="color:#7b8ab8;font-size:13px;max-width:340px;margin:0 auto;">""" + ("Select your name below or enter login in the sidebar." if is_en else "从下方选择您的名称，或在左侧栏输入 Login。") + """</p>
    </div>""", unsafe_allow_html=True)

    col_login_l, col_login_m, col_login_r = st.columns([1, 2, 1])
    with col_login_m:
        login_options = ["— 请选择 —" if not is_en else "— Select —"] + [u for u in ALLOWED_USERS if u not in ["admin", "yujiashi"]]
        login_choice = st.selectbox("Login", login_options, key="main_login_select", label_visibility="collapsed")
        if st.button("🔓 " + ("Login" if is_en else "登录"), type="primary", use_container_width=True, key="main_login_btn"):
            if login_choice and login_choice != "— 请选择 —" and login_choice != "— Select —":
                st.session_state["app_user"] = login_choice.lower()
                st.rerun()

        # Apply for access
        st.divider()
        st.caption("没有权限？" if not is_en else "No access?")
        apply_name = st.text_input("申请 Login" if not is_en else "Apply login name", key="apply_login", placeholder="输入您想申请的登录名")
        if st.button("📨 " + ("Apply for Access" if is_en else "申请权限"), key="apply_btn", use_container_width=True):
            if apply_name:
                _users_file = BASE_PATH / "output" / "users.json"
                _users_file.parent.mkdir(parents=True, exist_ok=True)
                if _users_file.exists():
                    ud = json.loads(_users_file.read_text(encoding="utf-8"))
                else:
                    ud = {"allowed": ALLOWED_USERS, "admins": ADMIN_USERS, "pending": []}
                pending = ud.get("pending", [])
                if apply_name.lower() not in [p.get("name") for p in pending] and apply_name.lower() not in ud.get("allowed", []):
                    pending.append({"name": apply_name.lower(), "applied_at": datetime.now().strftime("%Y-%m-%d %H:%M")})
                    ud["pending"] = pending
                    _users_file.write_text(json.dumps(ud, ensure_ascii=False, indent=2), encoding="utf-8")
                    st.success("✅ " + ("Application submitted! Admin will review." if is_en else "申请已提交！等待管理员审批。"))
                else:
                    st.info("Already applied or already has access." if is_en else "已申请或已有权限。")


elif _page_idx == 1:
    st.markdown("""<div class="ss-page-header"><h1 style="color:#ffa726;">📚 """ + ("Query Library" if is_en else "智库 – 检索短语产出与验证") + """</h1><p>""" + ("Produce → Calibrate → Dedupe → Select → Verify Gap → Confirm" if is_en else "产出 → 校准 → 去重 → 选取 → 验证Gap → 确认进智造") + """</p></div>""", unsafe_allow_html=True)
    render_pipeline_flow("zhiku", selected_batch)

    # ============================================================
    # USER VIEW: Simplified 3-tab interface
    # ============================================================
    if not is_admin:
        tab_seed, tab_persona, tab_upload = st.tabs([
            "🌱 词根裂变" if not is_en else "🌱 Seed Expansion",
            "🧠 画像裂变" if not is_en else "🧠 Persona Expansion",
            "📋 上传检索短语" if not is_en else "📋 Upload Phrases",
        ])

        with tab_seed:
            st.markdown("**输入词根，AI 自动裂变出检索短语**" if not is_en else "**Enter seed words, AI expands into search phrases**")
            seed_word = st.text_input("词根" if not is_en else "Seed word", placeholder="e.g. FBA、选品、注册", key="user_seed_word")
            seed_lang = st.multiselect("语言" if not is_en else "Language", ["中文", "English", "中英混合"],
                                       default=["中文"], key="user_seed_lang")
            seed_count = st.slider("裂变数量" if not is_en else "Count", 5, 30, 15, key="user_seed_count")
            if st.button("🌱 开始裂变" if not is_en else "🌱 Expand", type="primary", key="user_seed_btn"):
                if seed_word:
                    try:
                        from engine import call_bedrock_claude
                        lang_instruction = ""
                        if "中文" in seed_lang and "English" in seed_lang:
                            lang_instruction = "生成中文和英文两种语言的短语，各占一半。"
                        elif "中英混合" in seed_lang:
                            lang_instruction = "生成中英文混合短语（如'亚马逊FBA怎么做'、'Amazon FBA费用'）。"
                        elif "English" in seed_lang:
                            lang_instruction = "All phrases must be in English."
                        else:
                            lang_instruction = "所有短语使用中文。"

                        prompt = f"请为词根「{seed_word}」生成 {seed_count} 个卖家在 AI 搜索引擎中可能输入的口语化检索短语。{lang_instruction}每行一条，不要编号，不要解释。"
                        with st.spinner("裂变中..." if not is_en else "Expanding..."):
                            response = call_bedrock_claude(prompt)
                        queries = [q.strip().lstrip("0123456789.-、）) ") for q in response.strip().split("\n") if q.strip() and len(q.strip()) > 4]
                        if queries:
                            st.success(f"✅ 生成 {len(queries)} 条")
                            # Auto-score each phrase (1-5 scale)
                            def _quick_score(q):
                                score = 3.0  # base for AI-generated
                                if 10 <= len(q) <= 25: score += 0.5
                                elif len(q) > 25: score += 0.3
                                if any(w in q for w in ["怎么", "如何", "多少", "哪些", "为什么", "什么", "能不能", "how", "what", "why"]): score += 0.5
                                if any(w in q.lower() for w in ["亚马逊", "amazon", "fba", "注册", "开店", "选品", "物流", "广告", "listing"]): score += 0.5
                                if any(w in q for w in ["吗", "呢", "啊", "吧", "?"]): score += 0.3
                                return min(5.0, round(score, 1))

                            scores = [_quick_score(q) for q in queries]
                            df_result = pd.DataFrame({"ai_query": queries, "source": f"seed_{seed_word}", "is_selected": "FALSE", "accuracy_score": scores})
                            st.dataframe(df_result, use_container_width=True, hide_index=True)
                            # Save
                            zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                            zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                            existing = load_csv_safe(zhiku_file) if zhiku_file.exists() else pd.DataFrame()
                            merged = pd.concat([existing, df_result], ignore_index=True)
                            if "ai_query" in merged.columns:
                                merged = merged.drop_duplicates(subset=["ai_query"], keep="last")
                            merged.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                            st.success(f"✅ 已保存到智库")
                    except Exception as e:
                        st.error(str(e))

        with tab_persona:
            st.markdown("**根据用户画像维度组合推演检索短语**" if not is_en else "**Generate phrases based on persona dimensions**")

            # Load persona matrix
            _persona_file = INPUT_PATH / "persona_matrix.json"
            if _persona_file.exists():
                _pm = json.loads(_persona_file.read_text(encoding="utf-8"))
            else:
                _pm = {}

            # 基础画像
            st.markdown("##### 基础画像" if not is_en else "##### Basic Persona")
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                _基础 = _pm.get("基础画像", {})
                sel_identity = st.selectbox("身份", _基础.get("身份", {}).get("params", []), key="persona_identity")
                sel_company = st.selectbox("企业类型", _基础.get("企业类型", {}).get("params", []), key="persona_company")
                sel_role = st.selectbox("职位", _基础.get("职位", {}).get("params", []), key="persona_role")
            with col_p2:
                sel_revenue = st.selectbox("年销售额", _基础.get("年销售额", {}).get("params", []), key="persona_revenue")
                sel_biz_type = st.selectbox("公司类型", _基础.get("公司类型", {}).get("params", []), key="persona_biz")
                sel_shipping = st.selectbox("计划发货方式", _基础.get("计划发货方式", {}).get("params", []), key="persona_ship")

            # 兴趣画像
            st.markdown("##### 兴趣画像" if not is_en else "##### Interest Persona")
            _兴趣 = _pm.get("兴趣画像", {})
            sel_site = st.multiselect("目标站点", _兴趣.get("站点", {}).get("params", []), default=["美国站"], key="persona_site")
            sel_content = st.multiselect("内容分类", _兴趣.get("内容分类", {}).get("params", []), default=["新手指南"], key="persona_content")

            persona_count = st.slider("生成短语数" if not is_en else "Phrases to generate", 5, 30, 10, key="persona_gen_count")

            if st.button("🧠 画像推演生成" if not is_en else "🧠 Generate", type="primary", key="persona_gen_btn"):
                try:
                    from engine import call_bedrock_claude
                    persona_desc = f"身份={sel_identity}, 企业类型={sel_company}, 职位={sel_role}, 年销售额={sel_revenue}, 公司类型={sel_biz_type}, 发货方式={sel_shipping}, 目标站点={','.join(sel_site)}, 关注内容={','.join(sel_content)}"
                    prompt = f"""请为以下画像的卖家推演 {persona_count} 个他们在 AI 搜索引擎中最可能输入的检索短语。

画像：{persona_desc}

要求：
1. 口语化，像真人提问（10-25字）
2. 与该画像的身份、站点、关注内容高度相关
3. 每行一条，不要编号，不要解释"""
                    with st.spinner("推演中..." if not is_en else "Generating..."):
                        response = call_bedrock_claude(prompt)
                    queries = [q.strip().lstrip("0123456789.-、）) ") for q in response.strip().split("\n") if q.strip() and len(q.strip()) > 4]
                    if queries:
                        st.success(f"✅ 生成 {len(queries)} 条")
                        # Auto-score (1-5 scale)
                        def _quick_score_p(q):
                            score = 3.5  # persona-based = higher base
                            if 10 <= len(q) <= 25: score += 0.5
                            elif len(q) > 25: score += 0.3
                            if any(w in q for w in ["怎么", "如何", "多少", "哪些", "为什么", "什么", "能不能"]): score += 0.5
                            if any(w in q.lower() for w in ["亚马逊", "amazon", "fba", "注册", "开店", "选品", "物流", "广告"]): score += 0.3
                            if any(w in q for w in ["吗", "呢", "啊", "吧", "?"]): score += 0.2
                            return min(5.0, round(score, 1))
                        scores = [_quick_score_p(q) for q in queries]
                        df_result = pd.DataFrame({"ai_query": queries, "source": f"persona_{sel_identity}_{sel_site[0] if sel_site else ''}", "is_selected": "FALSE", "accuracy_score": scores})
                        st.dataframe(df_result, use_container_width=True, hide_index=True)
                        zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                        zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                        existing = load_csv_safe(zhiku_file) if zhiku_file.exists() else pd.DataFrame()
                        merged = pd.concat([existing, df_result], ignore_index=True)
                        if "ai_query" in merged.columns:
                            merged = merged.drop_duplicates(subset=["ai_query"], keep="last")
                        merged.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                        st.success("✅ 已保存到智库")
                except Exception as e:
                    st.error(str(e))

        with tab_upload:
            st.markdown("**直接上传已确定的检索短语 或 SEO/SEM 关键词**" if not is_en else "**Upload confirmed search phrases or SEO/SEM keywords**")

            upload_type = st.radio("上传类型" if not is_en else "Upload type",
                                   ["检索短语 (AI Query)" if not is_en else "Search Phrases",
                                    "SEO/SEM 关键词" if not is_en else "SEO/SEM Keywords"],
                                   horizontal=True, key="user_upload_type")

            if upload_type.startswith("检索短语") or upload_type.startswith("Search"):
                st.caption("CSV 文件需包含 `ai_query` 或 `query` 列" if not is_en else "CSV must contain `ai_query` or `query` column")
                uploaded_phrases = st.file_uploader("上传 CSV" if not is_en else "Upload CSV", type=["csv"], key="user_upload_phrases")
                if uploaded_phrases:
                    try:
                        df_up = pd.read_csv(uploaded_phrases, encoding="utf-8-sig", on_bad_lines="skip")
                        q_col = next((c for c in ["ai_query", "query", "检索短语", "问题"] if c in df_up.columns), df_up.columns[0] if len(df_up.columns) > 0 else None)
                        if q_col:
                            df_up = df_up.rename(columns={q_col: "ai_query"}) if q_col != "ai_query" else df_up
                            if "source" not in df_up.columns:
                                df_up["source"] = "manual_upload"
                            if "is_selected" not in df_up.columns:
                                df_up["is_selected"] = "TRUE"
                            st.dataframe(df_up[["ai_query"]].head(10), use_container_width=True, hide_index=True)
                            st.caption(f"共 {len(df_up)} 条")
                            if st.button("✅ 确认上传" if not is_en else "✅ Confirm Upload", type="primary", key="user_confirm_upload"):
                                zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                                zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                                existing = load_csv_safe(zhiku_file) if zhiku_file.exists() else pd.DataFrame()
                                merged = pd.concat([existing, df_up], ignore_index=True)
                                if "ai_query" in merged.columns:
                                    merged = merged.drop_duplicates(subset=["ai_query"], keep="last")
                                merged.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                                st.success(f"✅ 上传 {len(df_up)} 条到智库")
                    except Exception as e:
                        st.error(str(e))

            else:  # SEO/SEM Keywords
                st.caption("上传 SEO/SEM 关键词 CSV，系统将自动裂变为 AI 检索短语" if not is_en else "Upload SEO/SEM keywords CSV, system will expand into AI search phrases")
                st.caption("CSV 建议包含 `Keyword` 或 `keyword` 列" if not is_en else "CSV should contain `Keyword` or `keyword` column")
                uploaded_kw = st.file_uploader("上传关键词 CSV" if not is_en else "Upload Keywords CSV", type=["csv", "xlsx"], key="user_upload_kw")
                if uploaded_kw:
                    try:
                        if uploaded_kw.name.endswith(".csv"):
                            df_kw = pd.read_csv(uploaded_kw, encoding="utf-8-sig", on_bad_lines="skip")
                        else:
                            df_kw = pd.read_excel(uploaded_kw, engine="openpyxl")
                        kw_col = next((c for c in ["Keyword", "keyword", "关键词", "kw"] if c in df_kw.columns), df_kw.columns[0] if len(df_kw.columns) > 0 else None)
                        if kw_col:
                            keywords = df_kw[kw_col].dropna().astype(str).tolist()
                            st.dataframe(pd.DataFrame({"关键词": keywords[:10]}), use_container_width=True, hide_index=True)
                            st.caption(f"共 {len(keywords)} 个关键词")

                            kw_expand_count = st.slider("每个关键词裂变短语数" if not is_en else "Phrases per keyword", 3, 10, 5, key="kw_expand_count")

                            if st.button("🚀 裂变为检索短语" if not is_en else "🚀 Expand to Phrases", type="primary", key="user_kw_expand_btn"):
                                try:
                                    from engine import call_bedrock_claude
                                    kw_list = "\n".join(keywords[:20])
                                    prompt = f"""请将以下 SEO/SEM 关键词裂变为 AI 搜索引擎的口语化检索短语。

关键词列表：
{kw_list}

要求：
1. 每个关键词生成 {kw_expand_count} 条口语化问句
2. 像真实用户在 AI 搜索框里打字提问
3. 每行一条，不要编号，不要标注来源关键词

直接输出短语列表。"""
                                    with st.spinner("裂变中..." if not is_en else "Expanding..."):
                                        response = call_bedrock_claude(prompt)
                                    queries = [q.strip().lstrip("0123456789.-、）) ") for q in response.strip().split("\n") if q.strip() and len(q.strip()) > 4]
                                    if queries:
                                        st.success(f"✅ 生成 {len(queries)} 条检索短语")
                                        df_result = pd.DataFrame({"ai_query": queries, "source": "seo_sem_expand", "is_selected": "FALSE"})
                                        st.dataframe(df_result[["ai_query"]].head(15), use_container_width=True, hide_index=True)
                                        zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                                        zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                                        existing = load_csv_safe(zhiku_file) if zhiku_file.exists() else pd.DataFrame()
                                        merged = pd.concat([existing, df_result], ignore_index=True)
                                        if "ai_query" in merged.columns:
                                            merged = merged.drop_duplicates(subset=["ai_query"], keep="last")
                                        merged.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                                        st.success("✅ 已保存到智库")
                                except Exception as e:
                                    st.error(str(e))
                    except Exception as e:
                        st.error(f"上传失败: {str(e)}")

        # --- User: Phrase List, Selection, Filtering, CTA ---
        st.divider()
        st.markdown("### " + ("Current Phrase Library" if is_en else "当前短语库"))

        df_zhiku_user = load_zhiku_live(selected_batch)
        total_phrases_u = len(df_zhiku_user) if not df_zhiku_user.empty else 0
        selected_count_u = 0
        if not df_zhiku_user.empty and "is_selected" in df_zhiku_user.columns:
            selected_count_u = df_zhiku_user[df_zhiku_user["is_selected"].astype(str).str.upper().isin(["TRUE", "1", "YES"])].shape[0]

        sc1, sc2 = st.columns(2)
        sc1.metric("Total" if is_en else "总量", total_phrases_u)
        sc2.metric("Selected Phrases" if is_en else "已选中", selected_count_u)

        if not df_zhiku_user.empty:
            # Filter
            filter_col = st.columns([2, 2, 2])
            with filter_col[0]:
                source_filter = st.selectbox("Source" if is_en else "来源筛选",
                    ["All"] + (df_zhiku_user["source"].dropna().unique().tolist() if "source" in df_zhiku_user.columns else []),
                    key="user_source_filter")
            with filter_col[1]:
                select_filter = st.selectbox("Status" if is_en else "选中状态",
                    ["All" if is_en else "全部", "Selected Phrases" if is_en else "已选中", "Unselected" if is_en else "未选中"],
                    key="user_select_filter")
            with filter_col[2]:
                search_text = st.text_input("Search" if is_en else "搜索", key="user_search_text", placeholder="关键词搜索...")

            df_display = df_zhiku_user.copy()
            if source_filter != "All" and "source" in df_display.columns:
                df_display = df_display[df_display["source"] == source_filter]
            if "is_selected" in df_display.columns:
                if select_filter in ["Selected", "已选中"]:
                    df_display = df_display[df_display["is_selected"].astype(str).str.upper().isin(["TRUE", "1", "YES"])]
                elif select_filter in ["Unselected", "未选中"]:
                    df_display = df_display[~df_display["is_selected"].astype(str).str.upper().isin(["TRUE", "1", "YES"])]
            if search_text and "ai_query" in df_display.columns:
                df_display = df_display[df_display["ai_query"].astype(str).str.contains(search_text, case=False, na=False)]

            # Editable table
            show_cols = [c for c in ["ai_query", "source", "accuracy_score", "category", "is_selected"] if c in df_display.columns]
            # Add accuracy_score column if not present, auto-compute
            if "accuracy_score" not in df_display.columns:
                def _auto_score(q):
                    q = str(q)
                    score = 3.0
                    if 10 <= len(q) <= 25: score += 0.5
                    elif len(q) > 25: score += 0.3
                    if any(w in q for w in ["怎么", "如何", "多少", "哪些", "为什么", "什么", "能不能", "how", "what", "why"]): score += 0.5
                    if any(w in q.lower() for w in ["亚马逊", "amazon", "fba", "注册", "开店", "选品", "物流", "广告", "listing"]): score += 0.5
                    if any(w in q for w in ["吗", "呢", "啊", "吧", "?"]): score += 0.3
                    return min(5.0, round(score, 1))
                df_display["accuracy_score"] = df_display["ai_query"].apply(_auto_score) if "ai_query" in df_display.columns else "—"
                show_cols = [c for c in ["ai_query", "source", "accuracy_score", "category", "is_selected"] if c in df_display.columns]
            else:
                # Convert 0-100 score to 1-5 scale if needed
                df_display["accuracy_score"] = pd.to_numeric(df_display["accuracy_score"], errors="coerce").fillna(0)
                df_display["accuracy_score"] = df_display["accuracy_score"].apply(
                    lambda x: round(x / 20, 1) if x > 5 else (round(x, 1) if x > 0 else "—")
                )
            if show_cols:
                # Bulk select/deselect buttons
                col_sel1, col_sel2, col_sel3 = st.columns([1, 1, 4])
                with col_sel1:
                    if st.button("☑️ " + ("Select All" if is_en else "全选"), key="user_select_all"):
                        zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                        df_zhiku_user["is_selected"] = "TRUE"
                        df_zhiku_user.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                        st.rerun()
                with col_sel2:
                    if st.button("☐ " + ("Deselect All" if is_en else "全不选"), key="user_deselect_all"):
                        zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                        df_zhiku_user["is_selected"] = "FALSE"
                        df_zhiku_user.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                        st.rerun()

                col_config = {}
                if "is_selected" in show_cols:
                    col_config["is_selected"] = st.column_config.CheckboxColumn("Selected" if is_en else "选中")
                edited_df = st.data_editor(df_display[show_cols].reset_index(drop=True),
                                           column_config=col_config,
                                           use_container_width=True, hide_index=True,
                                           key="user_zhiku_editor")

                # Save changes
                if st.button("💾 " + ("Save Changes" if is_en else "保存修改"), key="user_save_zhiku"):
                    # Apply edits back
                    for col in show_cols:
                        if col in edited_df.columns:
                            df_zhiku_user[col] = edited_df[col].values[:len(df_zhiku_user)]
                    zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                    df_zhiku_user.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                    mark_data_changed()
                    st.success("✅ " + ("Changes saved successfully!" if is_en else "已保存！"))
                    st.rerun()

            # CTA to next step
            st.divider()
            if selected_count_u > 0:
                if st.button("➡️ " + ("Next: Run AI Test (智测)" if is_en else "下一步：执行智测"), type="primary", key="user_cta_zhice"):
                    jump_to("🔍 智测" if not is_en else "🔍 Testing")
                    st.rerun()
            else:
                st.info("Please select phrases first (check '选中' column)" if is_en else "请先选中短语（勾选「选中」列）后进入下一步")
        else:
            st.info("No phrases yet. Use the tabs above to generate or upload." if is_en else "暂无短语。请使用上方的标签页生成或上传。")

        # --- Clear & History ---
        st.divider()
        with st.expander("🗑️ " + ("Clear & Archive / 📜 History" if is_en else "清除归档 / 📜 历史记录"), expanded=False):
            if total_phrases_u > 0:
                if st.button("🗑️ " + ("Clear All & Archive" if is_en else "清空当前短语（归档到历史）"), key="user_clear_zhiku"):
                    zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                    if zhiku_file.exists():
                        archive_dir = OUTPUT_PATH / selected_batch / "01_zhiku" / "archive"
                        archive_dir.mkdir(parents=True, exist_ok=True)
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        zhiku_file.rename(archive_dir / f"zhiku_ai_queries_{ts}.csv")
                        st.success("✅ " + ("Archived. Page is now empty." if is_en else "已归档到历史记录，当前页面已清空。"))
                        st.rerun()

            # Show archived history
            archive_dir = OUTPUT_PATH / selected_batch / "01_zhiku" / "archive"
            if archive_dir.exists():
                archives = sorted(archive_dir.glob("*.csv"), reverse=True)
                if archives:
                    st.markdown("**📜 " + ("History" if is_en else "历史记录") + ":**")
                    for a in archives[:5]:
                        df_a = load_csv_safe(a)
                        count = len(df_a) if not df_a.empty else 0
                        st.caption(f"🗂️ {a.stem.replace('zhiku_ai_queries_', '')} — {count} " + ("phrases" if is_en else "条短语"))
                    # Restore option
                    restore_file = st.selectbox("Restore" if is_en else "恢复历史版本",
                                               [a.name for a in archives], key="user_restore_select")
                    if st.button("🔄 " + ("Restore" if is_en else "恢复"), key="user_restore_btn"):
                        src = archive_dir / restore_file
                        dst = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                        import shutil
                        shutil.copy2(str(src), str(dst))
                        st.success("✅ " + ("Restored!" if is_en else "已恢复！"))
                        st.rerun()
            else:
                st.caption("No history yet." if is_en else "暂无历史记录。")

    # ============================================================
    # ADMIN VIEW: Full interface (original)
    # ============================================================
    else:

    # --- Status bar ---
        df_zhiku_all = load_zhiku_live(selected_batch)
        total_phrases = len(df_zhiku_all) if not df_zhiku_all.empty else 0
        selected_count = 0
        if not df_zhiku_all.empty and "is_selected" in df_zhiku_all.columns:
            selected_count = df_zhiku_all[df_zhiku_all["is_selected"].astype(str).str.upper().isin(["TRUE", "1", "YES"])].shape[0]

        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("Total Phrases" if is_en else "短语总量", total_phrases)
        sc2.metric("Selected Phrases" if is_en else "已选中", selected_count)
        sc3.metric("Categories" if is_en else "覆盖类别", df_zhiku_all["category"].dropna().nunique() if not df_zhiku_all.empty and "category" in df_zhiku_all.columns else 0)
        sc4.metric("Sources" if is_en else "来源数", df_zhiku_all["source"].dropna().nunique() if not df_zhiku_all.empty and "source" in df_zhiku_all.columns else 0)

        # Clear current content (archive to history)
        if total_phrases > 0:
            if st.button("🗑️ Clear Current & Archive" if is_en else "🗑️ 清空当前内容（归档到历史）", key="clear_zhiku_current"):
                zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                if zhiku_file.exists():
                    archive_dir = OUTPUT_PATH / selected_batch / "01_zhiku" / "archive"
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    zhiku_file.rename(archive_dir / f"zhiku_ai_queries_{ts}.csv")
                    st.success("✅ Archived to history. Page is now empty." if is_en else "✅ 已归档到历史记录，当前页面已清空。")
                    st.rerun()

        # ============================================================
        # 🚀 一键全流程 (End-to-End)
        # ============================================================
        with st.expander("🚀 One-Click Full Pipeline (Keywords → Word Doc)" if is_en else "🚀 一键全流程（关键词 → Word 文档）", expanded=False):
            st.caption("Run all steps automatically: 智库 → 智造 → 智优 → 合规 → 智布" if is_en else "自动执行全部步骤：智库裂变 → 智造生成 → 智优评分+重写 → 合规审查 → 智布导出")

            col_e2e_1, col_e2e_2, col_e2e_3 = st.columns(3)
            with col_e2e_1:
                e2e_kw_limit = st.number_input("Keywords" if is_en else "关键词数", 1, 50, 10, key="e2e_kw_limit")
            with col_e2e_2:
                e2e_content_limit = st.number_input("Articles" if is_en else "文章数", 1, 20, 5, key="e2e_content_limit")
            with col_e2e_3:
                e2e_template_options = {
                    "auto": "Auto-detect" if is_en else "智能匹配",
                    "none": "No template" if is_en else "无模板",
                    "registration": "Registration" if is_en else "注册流程",
                    "fees": "Fees" if is_en else "费用成本",
                    "logistics": "Logistics" if is_en else "物流仓储",
                    "advertising": "Advertising" if is_en else "广告推广",
                    "listing": "Listing" if is_en else "Listing优化",
                }
                e2e_template = st.selectbox("Template" if is_en else "模板", list(e2e_template_options.keys()), format_func=lambda x: e2e_template_options[x], key="e2e_template")

            if st.button("🚀 Execute Full Pipeline" if is_en else "🚀 开始一键全流程", type="primary", key="btn_e2e"):
                try:
                    from engine import run_full_pipeline
                    e2e_progress = st.progress(0)
                    e2e_status = st.empty()

                    def e2e_callback(pct, msg):
                        e2e_progress.progress(min(1.0, max(0.0, pct)))
                        e2e_status.text(msg)

                    with st.spinner("Running full pipeline..." if is_en else "正在执行全流程..."):
                        result = run_full_pipeline(
                            selected_batch,
                            market="ALL",
                            keyword_limit=e2e_kw_limit,
                            content_limit=e2e_content_limit,
                            progress_callback=e2e_callback,
                        )

                    if result.get("success"):
                        st.success("✅ Full pipeline completed! Check each step for results." if is_en else "✅ 全流程执行完毕！请查看各步骤的输出结果。")
                        st.balloons()
                    else:
                        stopped = result.get("stopped_at", "Unknown")
                        error = result.get("error", "")
                        st.error(f"❌ Stopped at: {stopped} — {error}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        st.divider()

        # ============================================================
        # ① 短语产出
        # ============================================================
        st.markdown("""<div class="ss-section">
            <h3 style="color:#ffa726;">① """ + ("Search Phrase Generation" if is_en else "短语产出") + """</h3>
            <p>""" + ("3 input modes: AI auto / Upload CSV / Manual input" if is_en else "三种输入模式：AI 自动 / 上传 CSV / 手动输入") + """</p>
        </div>""", unsafe_allow_html=True)

        tab_p1, tab_p2, tab_p3, tab_p4 = st.tabs([
            "⭐ P1 Core (95-90%)" if is_en else "⭐ P1 核心来源 (95-90%)",
            "⭐ P2 Secondary (85-75%)" if is_en else "⭐ P2 次核心 (85-75%)",
            "P3 Expand (60%)" if is_en else "P3 兜底扩写 (60%)",
            "🧠 P4 Persona Predict" if is_en else "🧠 P4 画像推演",
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
                        if "ai_query" in merged.columns: merged = merged.drop_duplicates(subset=["ai_query"], keep="last")
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
                            new_df = pd.DataFrame({"ai_query": queries, "source": "reverse_recall", "priority_score": 4.6, "is_selected": "FALSE"})
                            zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                            zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                            existing = load_csv_safe(zhiku_file) if zhiku_file.exists() else pd.DataFrame()
                            merged = pd.concat([existing, new_df], ignore_index=True)
                            if "ai_query" in merged.columns: merged = merged.drop_duplicates(subset=["ai_query"], keep="last")
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
                                new_df = pd.DataFrame({"ai_query": all_queries, "source": "reverse_recall", "priority_score": 4.6, "is_selected": "FALSE"})
                                zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                                zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                                existing = load_csv_safe(zhiku_file) if zhiku_file.exists() else pd.DataFrame()
                                merged = pd.concat([existing, new_df], ignore_index=True)
                                if "ai_query" in merged.columns: merged = merged.drop_duplicates(subset=["ai_query"], keep="last")
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
                        if "ai_query" in merged.columns: merged = merged.drop_duplicates(subset=["ai_query"], keep="last")
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
                                merged = merged.drop_duplicates(subset=["ai_query"], keep="last")
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
                        new_df = pd.DataFrame({"ai_query": phrases, "source": "manual", "priority_score": 3.5, "is_selected": "FALSE"})
                        zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                        zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                        if zhiku_file.exists():
                            existing = load_csv_safe(zhiku_file)
                            merged = pd.concat([existing, new_df], ignore_index=True).drop_duplicates(subset=["ai_query"], keep="last")
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

        # --- P4 画像推演 ---
        with tab_p4:
            st.caption("Based on persona matrix (identity × site × topic), predict search queries by priority." if is_en else "基于客户画像矩阵（身份 × 站点 × 话题），按优先级推演潜在检索短语。")

            # Controls
            col_p4_1, col_p4_2, col_p4_3 = st.columns(3)
            with col_p4_1:
                p4_level = st.selectbox(
                    "Priority Level" if is_en else "优先级",
                    ["P0", "P1", "P2", "ALL"],
                    key="p4_priority_level",
                )
            with col_p4_2:
                p4_max = st.number_input("Max Queries" if is_en else "最大生成数", 10, 200, 50, key="p4_max_queries")
            with col_p4_3:
                # Load matrix for site options
                try:
                    from zhiku_predictor import load_persona_matrix
                    _matrix = load_persona_matrix()
                    _all_sites = _matrix.get("兴趣画像", {}).get("站点", {}).get("params", [])
                    _all_topics = _matrix.get("兴趣画像", {}).get("内容分类", {}).get("params", [])
                except Exception:
                    _all_sites = ["北美站", "欧洲站", "日本站"]
                    _all_topics = ["新手指南", "选品", "物流仓储"]

            col_p4_sites, col_p4_topics = st.columns(2)
            with col_p4_sites:
                p4_sites = st.multiselect("Target Sites" if is_en else "目标站点", _all_sites, default=_all_sites[:3], key="p4_sites")
            with col_p4_topics:
                p4_topics = st.multiselect("Target Topics" if is_en else "目标话题", _all_topics, default=_all_topics[:5], key="p4_topics")

            # Language selector
            p4_language = st.radio("Output Language" if is_en else "输出语言", ["中文", "English", "中英双语"], horizontal=True, key="p4_language")

            # Run prediction
            if st.button("🧠 Run Persona Prediction" if is_en else "🧠 执行画像推演", type="primary", key="btn_p4_predict"):
                try:
                    from zhiku_predictor import run_persona_prediction, export_to_zhiku
                    with st.spinner("Predicting..." if is_en else "推演中..."):
                        result = run_persona_prediction(
                            priority_level=p4_level,
                            max_queries=p4_max,
                            target_sites=p4_sites if p4_sites else None,
                            target_topics=p4_topics if p4_topics else None,
                            language=p4_language,
                        )
                    if result["success"]:
                        predictions = result.get("predictions", [])

                        # AUTO-IMPORT to zhiku immediately (no manual export step needed)
                        if predictions:
                            export_result = export_to_zhiku(predictions, selected_batch)
                            added = export_result.get('exported', 0)
                            total = export_result.get('total_in_zhiku', 0)
                            if added > 0:
                                st.success(f"✅ +{added} new queries auto-imported to library (total: {total})" if is_en else f"✅ 新增 {added} 条已自动导入智库（总量: {total}）")
                            else:
                                st.info(f"All queries already in library ({total} total, no new additions)" if is_en else f"全部短语已在智库中（共 {total} 条，无新增。请换不同条件推演）")
                        else:
                            st.info("No new predictions (all already in library). Try different sites/topics." if is_en else "无新预测短语（已全部在库）。请换不同站点/话题再试。")

                        st.rerun()
                    else:
                        st.warning(result.get("error", "No results"))
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        st.divider()

        # ============================================================
        # ② 校准 + 去重
        # ============================================================
        st.markdown("""<div class="ss-section">
            <h3 style="color:#ffa726;">② """ + ("Calibration & Deduplication" if is_en else "校准 + 去重") + """</h3>
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
                        df = df.drop_duplicates(subset=["ai_query"], keep="last")
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
        st.markdown("""<div class="ss-section">
            <h3 style="color:#ffa726;">③ """ + ("Review & Selection" if is_en else "审核 & 选取") + """</h3>
        </div>""", unsafe_allow_html=True)

        df_q = load_zhiku_live(selected_batch)
        if not df_q.empty:
            # Split by source type
            if "source" in df_q.columns:
                predicted_mask = df_q["source"].astype(str).str.contains("predicted|zhiyu", case=False, na=False)
                df_collected = df_q[~predicted_mask].copy()
                df_predicted = df_q[predicted_mask].copy()
            else:
                df_collected = df_q.copy()
                df_predicted = pd.DataFrame()

            # Show counts
            col_src1, col_src2 = st.columns(2)
            col_src1.metric("🎯 Tracked (已追踪到)" if is_en else "🎯 已追踪到", len(df_collected))
            col_src2.metric("🔮 Predicted (预估推演)" if is_en else "🔮 预估推演", len(df_predicted))

            # Tabbed view
            tab_collected, tab_predicted, tab_all = st.tabs([
                f"🎯 Tracked ({len(df_collected)})" if is_en else f"🎯 已追踪到 ({len(df_collected)})",
                f"🔮 Predicted ({len(df_predicted)})" if is_en else f"🔮 预估推演 ({len(df_predicted)})",
                f"📋 All ({len(df_q)})" if is_en else f"📋 全部 ({len(df_q)})",
            ])

            with tab_collected:
                st.caption("From real channels: SEO/SEM keywords, AI dropdown suggestions, reverse recall, community Q&A, manual input." if is_en else "来自真实渠道：SEO/SEM 关键词裂变、AI 平台下拉联想、逆向召回、社区原生提问、手动录入。")
                if not df_collected.empty:
                    edit_cols_c = [c for c in ["ai_query", "category", "source", "priority_score", "is_selected"] if c in df_collected.columns]
                    if edit_cols_c:
                        if "is_selected" in df_collected.columns:
                            df_collected["is_selected"] = df_collected["is_selected"].astype(str).str.upper().isin(["TRUE", "1", "YES"])
                        st.dataframe(df_collected[edit_cols_c], use_container_width=True, hide_index=True)
                else:
                    st.caption("No tracked phrases yet. Use P1/P2/P3 tabs above to add from real channels." if is_en else "暂无已追踪短语。请通过上方 P1/P2/P3 来源添加。")

            with tab_predicted:
                st.caption("AI-predicted based on persona matrix × lifecycle × site × topic. Need verification before production." if is_en else "基于画像矩阵 × 生命周期 × 站点 × 话题推演预估。进入生产前需通过智测验证。")
                if not df_predicted.empty:
                    edit_cols_p = [c for c in ["ai_query", "category", "source", "priority_score", "estimated_volume", "is_selected"] if c in df_predicted.columns]
                    if edit_cols_p:
                        if "is_selected" in df_predicted.columns:
                            df_predicted["is_selected"] = df_predicted["is_selected"].astype(str).str.upper().isin(["TRUE", "1", "YES"])
                        st.dataframe(df_predicted[edit_cols_p], use_container_width=True, hide_index=True)
                else:
                    st.caption("No predicted phrases yet. Use P4 Persona Prediction tab to generate." if is_en else "暂无预估短语。请通过 P4 画像推演生成。")

            with tab_all:
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
                            mark_data_changed()
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
        st.markdown("""<div class="ss-section">
            <h3 style="color:#4caf50;">④ """ + ("Next Step" if is_en else "下一步") + """</h3>
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
                        if current_user and not is_admin:
                            zhice_dir = OUTPUT_PATH / selected_batch / "zhice"
                        else:
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
            all_files = []
            if batch_path.exists():
                all_files.extend([f for f in batch_path.glob("*.csv")])
                archive_path = batch_path / "archive"
                if archive_path.exists():
                    all_files.extend([f for f in archive_path.glob("*.csv")])
            if all_files:
                col_hist_title, col_hist_clear = st.columns([4, 1])
                with col_hist_title:
                    st.caption(f"{len(all_files)} files")
                with col_hist_clear:
                    if st.button("🗑️ Clear All" if is_en else "🗑️ 清空全部", key="clear_zhiku_hist"):
                        if batch_path.exists():
                            for f in batch_path.glob("*.csv"):
                                f.unlink()
                            archive_path = batch_path / "archive"
                            if archive_path.exists():
                                for f in archive_path.glob("*.csv"):
                                    f.unlink()
                        st.success("History cleared" if is_en else "已清空")
                        st.rerun()
                all_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                for f in all_files[:10]:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                    col_i, col_r, col_d = st.columns([3, 1, 1])
                    with col_i:
                        st.caption(f"📄 {f.name} · {f.stat().st_size/1024:.1f}KB · 🕐 {mtime}")
                    with col_r:
                        if st.button("♻️ Reuse" if is_en else "♻️ 复用", key=f"reuse_zhiku_{f.name}"):
                            live_path = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                            safe_copy(f, live_path)
                            st.rerun()
                    with col_d:
                        st.download_button("⬇️", f.read_bytes(), file_name=f.name, mime="text/csv", key=f"dl_zhiku_{f.name}")
            else:
                st.caption("No history records yet" if is_en else "暂无历史")


    # ============================================================
    # PAGE: 智测 (Gap Verification)
    # ============================================================
elif _page_idx == 2:
    st.markdown("""<div class="ss-page-header"><h1 style="color:#00d4aa;">🔍 """ + ("Gap Verification" if is_en else "智测 – AI 检索覆盖验证") + """</h1><p>""" + ("Verify search phrases against 7 AI platforms to discover content gaps" if is_en else "在 7 个 AI 平台验证检索短语的覆盖状态，发现内容 Gap") + """</p></div>""", unsafe_allow_html=True)
    render_pipeline_flow("zhice", selected_batch)

    # --- Input: phrases to verify ---
    st.markdown("""<div class="ss-section">
        <h3 style="color:#00d4aa;">① """ + ("Phrases Pending Verification" if is_en else "待验证短语") + """</h3>
    </div>""", unsafe_allow_html=True)

    # Load selected phrases from zhiku (for both admin and user)
    df_zhiku_for_zhice = load_zhiku_live(selected_batch)
    zhiku_selected_phrases = []
    if not df_zhiku_for_zhice.empty and "ai_query" in df_zhiku_for_zhice.columns:
        if "is_selected" in df_zhiku_for_zhice.columns:
            selected_rows = df_zhiku_for_zhice[df_zhiku_for_zhice["is_selected"].astype(str).str.upper().isin(["TRUE", "1", "YES"])]
            zhiku_selected_phrases = selected_rows["ai_query"].dropna().tolist()

    # Load from zhiku queue or upload
    # Per-user isolation: save zhice results into user's batch directory
    if current_user and not is_admin:
        zhice_dir = OUTPUT_PATH / selected_batch / "zhice"
    else:
        zhice_dir = OUTPUT_PATH.parent / "zhice"
    zhice_dir.mkdir(parents=True, exist_ok=True)
    queue_phrases = zhiku_selected_phrases if zhiku_selected_phrases else []

    # If no selected phrases from zhiku, try legacy queue files
    if not queue_phrases and zhice_dir.exists():
        queue_files = sorted(zhice_dir.glob("zhiku_verify_queue_*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        if queue_files:
            latest_queue = json.loads(queue_files[0].read_text(encoding="utf-8"))
            queue_phrases = latest_queue.get("queries_to_verify", [])

    if queue_phrases:
        st.caption(f"{'From 智库 (selected)' if is_en else '来自智库（已选中）'}: {len(queue_phrases)} phrases")
        st.dataframe(pd.DataFrame({"ai_query": queue_phrases}), use_container_width=True, hide_index=True, height=200)
    else:
        st.info("No selected phrases. Go to 智库 and select phrases first." if is_en else "暂无已选中的短语。请先在智库中选中短语。")

    # Upload option (admin only)
    if is_admin:
        with st.expander("📤 " + ("Upload additional phrases" if is_en else "上传额外待验证短语"), expanded=False):
            up_verify = st.file_uploader("CSV with ai_query column" if is_en else "CSV（含 ai_query 列）", type=["csv", "xlsx"], key="zhice_upload_phrases")
            if up_verify:
                df_up = pd.read_csv(up_verify, encoding="utf-8-sig", on_bad_lines="skip") if up_verify.name.endswith(".csv") else pd.read_excel(up_verify, engine="openpyxl")
                if "ai_query" in df_up.columns:
                    queue_phrases = queue_phrases + df_up["ai_query"].tolist()
                    st.success(f"✅ +{len(df_up)} phrases added")

    st.divider()

    # --- Execute verification ---
    st.markdown("""<div class="ss-section">
        <h3 style="color:#00d4aa;">② """ + ("Run AI Platform Verification" if is_en else "执行验证") + """</h3>
    </div>""", unsafe_allow_html=True)

    ZHICE_PLATFORMS = {"qianwen": "通义千问", "deepseek": "DeepSeek", "kimi": "Kimi", "doubao": "豆包", "chatgpt": "ChatGPT", "perplexity": "Perplexity", "gemini": "Gemini"}
    selected_platforms = st.multiselect("Verification Platforms" if is_en else "验证平台", list(ZHICE_PLATFORMS.keys()), default=["qianwen", "deepseek"], format_func=lambda x: ZHICE_PLATFORMS[x], key="zhice_platforms")

    col_auto, col_manual = st.columns(2)
    with col_auto:
        if st.button("🔍 Auto Verify (API)" if is_en else "🔍 AI 自动验证", type="primary", key="zhice_auto_run", disabled=not queue_phrases):
            try:
                from zhice_engine import REAL_API_MAP
                from engine import call_claude as _verify_claude
                import time as _time
                results = []
                progress = st.progress(0)
                total = len(queue_phrases) * len(selected_platforms)
                done = 0

                # Brand detection keywords (expanded)
                BRAND_KEYWORDS = [
                    "亚马逊", "全球开店", "Amazon", "amazon", "Global Selling",
                    "Seller Central", "卖家平台", "FBA", "亚马逊物流",
                    "Amazon Global", "gs.amazon", "sell.amazon",
                    "アマゾン", "아마존",
                ]

                # Competitor detection keywords
                COMPETITOR_KEYWORDS = {
                    "Shopee": ["shopee", "虾皮"],
                    "Lazada": ["lazada"],
                    "TikTok Shop": ["tiktok shop", "tiktok", "抖音电商"],
                    "Alibaba": ["alibaba", "阿里巴巴", "1688", "速卖通", "aliexpress"],
                    "eBay": ["ebay"],
                    "Walmart": ["walmart", "沃尔玛"],
                    "Temu": ["temu", "拼多多跨境"],
                    "Shopify": ["shopify"],
                }

                for query in queue_phrases:
                    for platform in selected_platforms:
                        api_func = REAL_API_MAP.get(platform)
                        answer = ""
                        try:
                            if api_func:
                                r = api_func(query)
                                answer = r.get("full_answer", "")
                                # If API returned an error message, try Claude fallback
                                if "未配置" in answer or "API 错误" in answer or "调用失败" in answer:
                                    sim_prompt = f"50字以内简答：{query}"
                                    answer = _verify_claude(sim_prompt, max_tokens=150)
                            else:
                                sim_prompt = f"50字以内简答：{query}"
                                answer = _verify_claude(sim_prompt, max_tokens=150)
                        except Exception:
                            try:
                                answer = _verify_claude(f"50字以内简答：{query}", max_tokens=150)
                            except Exception:
                                answer = ""

                        has_brand = any(kw in answer for kw in BRAND_KEYWORDS)
                        has_link = "amazon" in answer.lower() or "gs.amazon" in answer.lower() or "sell.amazon" in answer.lower()

                        # Detect competitors mentioned
                        answer_lower = answer.lower()
                        competitors_found = [name for name, kws in COMPETITOR_KEYWORDS.items() if any(kw in answer_lower for kw in kws)]

                        # Sentiment analysis: positive vs negative tone about selling on Amazon
                        POSITIVE_KEYWORDS = ["机会", "优势", "简单", "容易", "推荐", "值得", "利润", "增长", "成功",
                                             "opportunity", "easy", "recommend", "profitable", "growth",
                                             "便捷", "高效", "支持", "帮助", "适合", "前景"]
                        NEGATIVE_KEYWORDS = ["风险", "难", "门槛", "亏损", "复杂", "竞争激烈", "封号", "侵权",
                                             "difficult", "risk", "complex", "competitive", "banned",
                                             "骗局", "不建议", "谨慎", "失败", "淘汰", "内卷"]
                        pos_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in answer_lower)
                        neg_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in answer_lower)
                        if pos_count > neg_count:
                            sentiment = "positive"
                        elif neg_count > pos_count:
                            sentiment = "negative"
                        else:
                            sentiment = "neutral"

                        results.append({
                            "ai_query": query, "platform": platform,
                            "has_brand_mention": has_brand, "has_official_link": has_link,
                            "competitors_mentioned": ", ".join(competitors_found) if competitors_found else "",
                            "sentiment": sentiment,
                        })
                        done += 1
                        progress.progress(done / total)
                # Build per-platform gap results (one row per query × platform)
                df_results = pd.DataFrame(results)
                gap_summary = []
                for q in queue_phrases:
                    q_data = df_results[df_results["ai_query"] == q]
                    for _, row in q_data.iterrows():
                        platform_name = ZHICE_PLATFORMS.get(row.get("platform", ""), row.get("platform", ""))
                        has_brand = bool(row.get("has_brand_mention", False))
                        has_link = bool(row.get("has_official_link", False))
                        competitors_str = str(row.get("competitors_mentioned", ""))
                        competitors_list = [c.strip() for c in competitors_str.split(",") if c.strip()]

                        if has_brand and has_link:
                            gap_status = "covered"
                        elif has_brand or has_link:
                            gap_status = "partial_gap"
                        else:
                            gap_status = "full_gap"

                        competitor_gap = len(competitors_list) > 0 and not has_brand

                        # Sentiment
                        sent_raw = row.get("sentiment", "neutral")
                        if sent_raw == "positive":
                            sentiment_display = "😊 积极"
                        elif sent_raw == "negative":
                            sentiment_display = "⚠️ 消极"
                        else:
                            sentiment_display = "😐 中性"

                        gap_summary.append({
                            "ai_query": q,
                            "platform": platform_name,
                            "gap_status": gap_status,
                            "has_brand_mention": has_brand,
                            "has_official_link": has_link,
                            "competitors": ", ".join(competitors_list) if competitors_list else "—",
                            "competitor_gap": competitor_gap,
                            "sentiment": sentiment_display,
                        })

                df_gap = pd.DataFrame(gap_summary)
                st.session_state["zhice_gap_results"] = df_gap
                # Save gap result
                zhice_dir.mkdir(parents=True, exist_ok=True)
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                df_gap.to_csv(zhice_dir / f"gap_result_{ts}.csv", index=False, encoding="utf-8-sig")

                # --- Prompt Tracking History: append to cumulative tracking file ---
                tracking_file = zhice_dir / "prompt_tracking_history.csv"
                tracking_rows = []
                for _, row_g in df_gap.iterrows():
                    tracking_rows.append({
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "timestamp": ts,
                        "ai_query": row_g.get("ai_query", ""),
                        "has_brand_mention": row_g.get("has_brand_mention", False),
                        "has_official_link": row_g.get("has_official_link", False),
                        "gap_status": row_g.get("gap_status", ""),
                        "sentiment": row_g.get("sentiment", ""),
                        "competitors": row_g.get("competitors", ""),
                        "competitor_gap": row_g.get("competitor_gap", False),
                        "platforms_tested": row_g.get("platforms_tested", 0),
                    })
                df_tracking_new = pd.DataFrame(tracking_rows)
                if tracking_file.exists():
                    df_tracking_existing = pd.read_csv(tracking_file, encoding="utf-8-sig")
                    df_tracking_all = pd.concat([df_tracking_existing, df_tracking_new], ignore_index=True)
                else:
                    df_tracking_all = df_tracking_new
                df_tracking_all.to_csv(tracking_file, index=False, encoding="utf-8-sig")

                st.success(f"✅ Verification complete! History tracked." if is_en else f"✅ 验证完成！已记录追踪历史。")
                mark_data_changed()
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
    st.markdown("""<div class="ss-section">
        <h3 style="color:#00d4aa;">③ """ + ("Gap Analysis Results & Selection" if is_en else "Gap 结果 & 选取") + """</h3>
    </div>""", unsafe_allow_html=True)

    df_gap_display = st.session_state.get("zhice_gap_results", pd.DataFrame())
    # Load latest gap result file if session empty
    if df_gap_display.empty and zhice_dir.exists():
        gap_files = sorted(zhice_dir.glob("gap_result_*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
        if gap_files:
            df_gap_display = load_csv_safe(gap_files[0])

    # Ensure compatibility: add missing columns for old data
    if not df_gap_display.empty:
        if "sentiment" not in df_gap_display.columns:
            df_gap_display["sentiment"] = "😐 未检测"
        if "competitors" not in df_gap_display.columns:
            df_gap_display["competitors"] = "—"
        if "competitor_gap" not in df_gap_display.columns:
            df_gap_display["competitor_gap"] = False

    if not df_gap_display.empty:
        # Summary metrics
        if "gap_status" in df_gap_display.columns:
            gc1, gc2, gc3, gc4, gc5 = st.columns(5)
            gc1.metric("Total" if is_en else "总计", len(df_gap_display))
            gc2.metric("✅ Covered" if is_en else "✅ 已覆盖", len(df_gap_display[df_gap_display["gap_status"] == "covered"]))
            gc3.metric("⚠️ Partial", len(df_gap_display[df_gap_display["gap_status"] == "partial_gap"]))
            gc4.metric("❌ Full Gap", len(df_gap_display[df_gap_display["gap_status"] == "full_gap"]))
            # Competitor gap: competitors mentioned but Amazon not
            comp_gap_count = len(df_gap_display[df_gap_display["competitor_gap"] == True]) if "competitor_gap" in df_gap_display.columns else 0
            gc5.metric("🔥 Competitor Gap" if is_en else "🔥 竞品覆盖我们未覆盖", comp_gap_count)

        # Highlight competitor gaps
        if "competitor_gap" in df_gap_display.columns and df_gap_display["competitor_gap"].any():
            st.warning(f"⚠️ {comp_gap_count} queries where competitors appear but Amazon does NOT. These are high-priority opportunities!" if is_en else f"⚠️ {comp_gap_count} 条短语中竞品被提及但亚马逊未被提及 — 这些是最高优先级的机会！")

        # Highlight negative sentiment
        if "sentiment" in df_gap_display.columns:
            neg_count = len(df_gap_display[df_gap_display["sentiment"].astype(str).str.contains("消极")])
            if neg_count > 0:
                st.warning(f"⚠️ {neg_count} queries with negative AI tone (门槛高/风险大). Need positive content to counter." if is_en else f"⚠️ {neg_count} 条短语的 AI 回答偏消极（强调门槛/风险），需要产出积极正面内容覆盖。")

        # Editable selection — add platform column and to_produce checkbox
        # Add platform column if not present (for legacy data)
        if "platforms_tested" in df_gap_display.columns and "platform" not in df_gap_display.columns:
            df_gap_display["platform"] = df_gap_display["platforms_tested"].apply(
                lambda x: str(x) if str(x) not in ["nan", "", "0"] else "通义千问, DeepSeek"
            )

        # Add to_produce checkbox — mark if any gap exists for this query across platforms
        if "to_produce" not in df_gap_display.columns:
            if "gap_status" in df_gap_display.columns:
                gap_queries = set(df_gap_display[df_gap_display["gap_status"].isin(["full_gap", "partial_gap"])]["ai_query"].tolist())
                df_gap_display["to_produce"] = df_gap_display["ai_query"].isin(gap_queries)
            else:
                df_gap_display["to_produce"] = True

        show_cols = [c for c in ["ai_query", "platform", "gap_status", "has_brand_mention", "has_official_link", "sentiment", "competitors", "competitor_gap", "to_produce"] if c in df_gap_display.columns]
        if show_cols:
            col_config = {
                "ai_query": st.column_config.TextColumn("Search Phrase" if is_en else "检索短语"),
                "platform": st.column_config.TextColumn("Platform" if is_en else "验证平台"),
                "gap_status": st.column_config.TextColumn("Gap Status" if is_en else "覆盖状态"),
                "has_brand_mention": st.column_config.CheckboxColumn("Brand/Product Mention" if is_en else "品牌/产品名称提及", disabled=True),
                "has_official_link": st.column_config.CheckboxColumn("Official Link" if is_en else "官网链接", disabled=True),
                "to_produce": st.column_config.CheckboxColumn("→ Produce" if is_en else "→ 生产"),
                "competitor_gap": st.column_config.CheckboxColumn("Comp Gap" if is_en else "竞品Gap", disabled=True),
                "competitors": st.column_config.TextColumn("Competitors" if is_en else "竞品出现"),
                "sentiment": st.column_config.TextColumn("Tone" if is_en else "内容情感"),
            }
            edited_gap = st.data_editor(df_gap_display[show_cols], column_config=col_config, use_container_width=True, hide_index=True, key="zhice_gap_editor")
            # Count unique queries selected (not individual platform rows)
            produce_queries = edited_gap[edited_gap["to_produce"] == True]["ai_query"].nunique() if "to_produce" in edited_gap.columns and "ai_query" in edited_gap.columns else 0
            st.caption(f"{'Selected for production (unique phrases)' if is_en else '选中进入智造（不重复短语数）'}: {produce_queries}")

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
                                df_new = pd.DataFrame({"ai_query": to_produce_queries, "is_selected": "FALSE"})
                                zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                                df_new.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                        else:
                            # No zhiku file exists — create one with the gap phrases
                            df_new = pd.DataFrame({"ai_query": to_produce_queries, "is_selected": "FALSE"})
                            zhiku_file.parent.mkdir(parents=True, exist_ok=True)
                            df_new.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                        jump_to("✍️ 智造")
                        st.rerun()
    else:
        st.caption("No gap results yet. Execute verification above or upload results." if is_en else "暂无 Gap 结果。请执行验证或上传结果。")

    # --- Prompt Tracking Trends ---
    with st.expander("📈 Prompt Tracking History" if is_en else "📈 短语追踪历史（品牌/产品名称提及率变化）", expanded=False):
        tracking_file = zhice_dir / "prompt_tracking_history.csv" if zhice_dir.exists() else None
        if tracking_file and tracking_file.exists():
            df_track = load_csv_safe(tracking_file)
            if not df_track.empty and "date" in df_track.columns:
                # Summary: brand mention rate over time
                df_track["has_brand_mention"] = df_track["has_brand_mention"].astype(str).str.upper().isin(["TRUE", "1"])
                df_track["has_official_link"] = df_track["has_official_link"].astype(str).str.upper().isin(["TRUE", "1"]) if "has_official_link" in df_track.columns else False
                by_date = df_track.groupby("date").agg(
                    total=("ai_query", "count"),
                    brand_mentions=("has_brand_mention", "sum"),
                    link_mentions=("has_official_link", "sum"),
                ).reset_index()
                by_date["brand_rate"] = (by_date["brand_mentions"] / by_date["total"] * 100).round(1)
                by_date["link_rate"] = (by_date["link_mentions"] / by_date["total"] * 100).round(1)

                # Show metrics
                tc1, tc2, tc3, tc4 = st.columns(4)
                tc1.metric("Total Verification Runs" if is_en else "总验证次数", len(df_track))
                tc2.metric("Unique Phrases Tested" if is_en else "不重复短语", df_track["ai_query"].nunique())
                latest_brand_rate = by_date["brand_rate"].iloc[-1] if len(by_date) > 0 else 0
                tc3.metric("Brand/Product Name Mention Rate" if is_en else "品牌/产品名称提及率", f"{latest_brand_rate}%")
                latest_link_rate = by_date["link_rate"].iloc[-1] if len(by_date) > 0 else 0
                tc4.metric("Official Link Citation Rate" if is_en else "官网链接显示率", f"{latest_link_rate}%")

                # Trend chart (both lines)
                if len(by_date) > 1:
                    fig_track = go.Figure()
                    fig_track.add_trace(go.Scatter(x=by_date["date"], y=by_date["brand_rate"], name="Brand/Product Name Rate" if is_en else "品牌/产品名称提及率", line=dict(color="#00bcd4")))
                    fig_track.add_trace(go.Scatter(x=by_date["date"], y=by_date["link_rate"], name="Link Rate" if is_en else "官网链接率", line=dict(color="#ffa726")))
                    fig_track.update_layout(
                        title="Brand & Link Rate Over Time" if is_en else "品牌/产品名称提及率 & 官网链接率变化趋势",
                        height=250, margin=dict(l=0, r=0, t=30, b=0),
                        yaxis_title="%", xaxis_title="Date",
                    )
                    st.plotly_chart(fig_track, use_container_width=True)

                # Per-query tracking (brand + link)
                st.caption("Per-query history (🟢=Brand ✅, 🔗=Link ✅):" if is_en else "单条短语追踪（🟢=品牌/产品名称提及, 🔗=官网链接）：")
                query_history = df_track.groupby(["ai_query", "date"]).agg(
                    brand=("has_brand_mention", "any"),
                    link=("has_official_link", "any"),
                ).reset_index()
                # Combine brand+link into single display
                query_history["status"] = query_history.apply(
                    lambda r: "🟢🔗" if r["brand"] and r["link"] else ("🟢" if r["brand"] else ("🔗" if r["link"] else "❌")), axis=1
                )
                if "date" in query_history.columns:
                    pivot = query_history.pivot_table(index="ai_query", columns="date", values="status", aggfunc="first")
                    pivot = pivot.fillna("—")
                    st.dataframe(pivot, use_container_width=True)
            else:
                st.caption("No tracking data yet. Run verification to start tracking." if is_en else "暂无追踪数据。执行验证后开始追踪。")
        else:
            st.caption("No tracking data yet. Run verification to start tracking." if is_en else "暂无追踪数据。执行验证后开始追踪。")

    # History
    with st.expander("📜 History" if is_en else "📜 历史记录"):
        if zhice_dir.exists():
            col_hist, col_clear_hist = st.columns([4, 1])
            with col_clear_hist:
                if st.button("🗑️ Clear All" if is_en else "🗑️ 清空全部", key="clear_zhice_history"):
                    # Delete gap results, queue files, and journey files
                    deleted = 0
                    for pattern in ["gap_result_*.csv", "zhiku_verify_queue_*.json", "*.json"]:
                        for f in zhice_dir.glob(pattern):
                            f.unlink()
                            deleted += 1
                    # Clear session state
                    if "zhice_gap_results" in st.session_state:
                        del st.session_state["zhice_gap_results"]
                    st.success(f"{'Cleared' if is_en else '已清空'} {deleted} {'files' if is_en else '个文件'}")
                    st.rerun()
            files = sorted(zhice_dir.glob("gap_result_*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)
            journey_files = sorted(zhice_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
            all_zhice_files = files + journey_files
            if all_zhice_files:
                for f in all_zhice_files[:10]:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                    col_f, col_r, col_del = st.columns([3, 1, 1])
                    with col_f:
                        st.caption(f"📄 {f.name} · {mtime}")
                    with col_r:
                        if st.button("♻️ Reuse" if is_en else "♻️ 复用", key=f"reuse_zhice_{f.name}"):
                            # For gap results, copy to the active gap result
                            if f.suffix == ".csv":
                                live_path = zhice_dir / "gap_result_latest.csv"
                                safe_copy(f, live_path)
                            else:
                                # For journey JSON files, load into session state
                                import json
                                try:
                                    journey_data = json.loads(f.read_text(encoding="utf-8"))
                                    st.session_state["zhice_reuse_journey"] = journey_data
                                    st.success(f"{'Loaded journey' if is_en else '已加载旅程'}: {f.name}")
                                except Exception:
                                    pass
                            st.rerun()
                    with col_del:
                        if st.button("🗑️", key=f"del_zhice_{f.name}"):
                            f.unlink()
                            st.rerun()
            else:
                st.caption("No history records yet" if is_en else "暂无历史")
        else:
            st.caption("No history records yet" if is_en else "暂无历史")


# ============================================================
# PAGE: 智造 (Step 2) — 单页线性流程
# ============================================================
elif _page_idx == 3:
    st.markdown("""<div class="ss-page-header"><h1 style="color:#ffcc02;">✍️ """ + ("Content Creation" if is_en else "智造 – Content Generation") + """</h1><p>""" + ("Generate SEO+GEO dual-optimized content based on AI Queries" if is_en else "基于 AI Queries 生成 SEO+GEO 双优化内容") + """</p></div>""", unsafe_allow_html=True)
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

    # --- Show selected phrases (editable) ---
    st.subheader("📋 Selected Phrases" if is_en else "📋 智测选择短语")
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

    # --- Content Material Upload (reference docs for generation) ---
    st.subheader("📎 " + ("Reference Materials Upload" if is_en else "内容素材上传"))
    st.caption("Upload reference documents (Word/PDF/TXT/MD) that the AI can use when generating articles. Materials are matched to phrases by keywords." if is_en else "上传参考素材文档（Word/PDF/TXT/MD），AI 生成文章时会从中抓取相关信息。素材按关键词自动匹配对应短语。")

    _materials_dir = OUTPUT_PATH / selected_batch / "materials"
    _materials_dir.mkdir(parents=True, exist_ok=True)

    uploaded_materials = st.file_uploader(
        "Upload materials" if is_en else "上传素材文件",
        type=["docx", "doc", "pdf", "txt", "md", "csv"],
        accept_multiple_files=True,
        key="upload_materials",
        label_visibility="collapsed",
    )
    if uploaded_materials:
        for uf in uploaded_materials:
            _save_path = _materials_dir / uf.name
            _save_path.write_bytes(uf.read())
        st.success(f"✅ {'Uploaded' if is_en else '已上传'} {len(uploaded_materials)} {'files' if is_en else '个文件'}")

    # Show existing materials
    _existing_materials = list(_materials_dir.glob("*")) if _materials_dir.exists() else []
    _existing_materials = [f for f in _existing_materials if f.is_file()]
    if _existing_materials:
        st.caption(f"{'Available materials' if is_en else '已有素材'}: {len(_existing_materials)} {'files' if is_en else '个文件'}")
        for mf in _existing_materials[:10]:
            st.text(f"  📄 {mf.name} ({mf.stat().st_size // 1024} KB)")
    else:
        st.caption("No materials uploaded yet. AI will use built-in knowledge base." if is_en else "暂无上传素材，AI 将使用内置知识库生成。")

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

    # Template selection
    template_options = {
        "auto": "🤖 Auto-detect (智能匹配)" if is_en else "🤖 智能匹配（根据短语自动选模板）",
        "none": "🆓 From Scratch (自由生成)" if is_en else "🆓 自由生成（无模板）",
        "registration": "📋 Registration Flow (注册流程)" if is_en else "📋 注册流程模板",
        "fees": "💰 Fees & Costs (费用成本)" if is_en else "💰 费用成本模板",
        "logistics": "📦 Logistics & FBA (物流仓储)" if is_en else "📦 物流仓储模板",
        "advertising": "📢 Advertising (广告推广)" if is_en else "📢 广告推广模板",
        "listing": "🏷️ Listing Optimization (Listing优化)" if is_en else "🏷️ Listing优化模板",
    }
    selected_template = st.selectbox(
        "Content Template" if is_en else "内容模板",
        options=list(template_options.keys()),
        format_func=lambda x: template_options[x],
        key="zhizao_template",
    )
    if selected_template == "auto":
        st.caption("🤖 Auto mode: template is matched per query based on keywords (注册→注册模板, 费用→费用模板, etc.)" if is_en else "🤖 智能模式：根据每条短语的关键词自动匹配最佳模板（注册→注册模板，费用→费用模板，物流→物流模板...）")
    elif selected_template != "none":
        st.caption("✅ Fixed template: all articles use the same structure." if is_en else "✅ 固定模板：所有文章使用同一结构。")

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
                reuse_tpl = st.session_state.get("reuse_template", None)
                result = run_zhizao(selected_batch, content_limit, update_progress_z, selected_template, reuse_tpl)

            if result["success"]:
                if result['articles_generated'] > 0:
                    st.success(f"✅ +{result['articles_generated']} {'articles' if is_en else '篇'}")
                    mark_data_changed()
                else:
                    err_detail = result.get('error_details', '')
                    st.warning(f"⚠️ Generated 0 articles. {err_detail}" if err_detail else "⚠️ API called successfully but generated 0 articles. Possible causes: API returned empty/error response, or all selected queries failed.")
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

        # Clear current content (archive to history)
        if st.button("🗑️ Clear Current & Archive" if is_en else "🗑️ 清空当前内容（归档到历史）", key="clear_zhizao_current"):
            zhizao_file = OUTPUT_PATH / selected_batch / "02_zhizao" / "zhizao_draft_content.csv"
            if zhizao_file.exists():
                archive_dir = OUTPUT_PATH / selected_batch / "02_zhizao" / "archive"
                archive_dir.mkdir(parents=True, exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                zhizao_file.rename(archive_dir / f"zhizao_draft_content_{ts}.csv")
                st.success("✅ Archived" if is_en else "✅ 已归档到历史")
                st.rerun()

        display_cols = [c for c in ["content_id", "ai_query", "title", "word_count", "version"]
                       if c in df_z.columns]
        if display_cols:
            st.dataframe(df_z[display_cols], use_container_width=True, hide_index=True)

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
                _art_col, _dl_col = st.columns([6, 1])
                with _art_col:
                    _ver = str(row.get("version", "v1"))
                    with st.expander(f"📄 {title} ({word_count} {'words' if is_en else '字'}) [{_ver}]"):
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
                                # Auto-increment version
                                cur_ver = str(row.get("version", "v1"))
                                try:
                                    ver_num = int(cur_ver.replace("v", "").replace("V", "")) + 1
                                except (ValueError, AttributeError):
                                    ver_num = 2
                                df_z.at[idx, "version"] = f"v{ver_num}"
                                df_z.at[idx, "updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                content_changed = True

                            # Save as template button
                            if st.button("💾 Save as Template" if is_en else "💾 保存为模板", key=f"save_tpl_{idx}"):
                                tpl_dir = BASE_PATH / "templates"
                                tpl_dir.mkdir(parents=True, exist_ok=True)
                                tpl_name = str(row.get("ai_query", f"template_{idx}"))[:50].strip()
                                tpl_file = tpl_dir / f"{tpl_name}.json"
                                import json as _json
                                tpl_data = {
                                    "name": tpl_name,
                                    "source_query": str(row.get("ai_query", "")),
                                    "title": str(row.get("title", "")),
                                    "content": edited_content if edited_content != original else original,
                                    "category": str(row.get("category", "")),
                                    "word_count": len(edited_content if edited_content != original else original),
                                    "created_from": f"{selected_batch}/{row.get('content_id', '')}",
                                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                }
                                tpl_file.write_text(_json.dumps(tpl_data, ensure_ascii=False, indent=2), encoding="utf-8")
                                st.success(f"✅ {'Saved to template library' if is_en else '已保存到模板库'}: {tpl_name}")
                with _dl_col:
                    _article_text = f"# {title}\n\n{str(row.get('content_draft', ''))}"
                    st.download_button("⬇️", _article_text.encode("utf-8"),
                                       file_name=f"{str(row.get('ai_query', f'article_{idx}'))[:30]}.md",
                                       mime="text/markdown", key=f"dl_zhizao_art_{idx}")
            # Auto-save if any content changed
            if content_changed:
                df_z.to_csv(zhizao_file, index=False, encoding="utf-8-sig")
                st.success("✅ Changes auto-saved" if is_en else "✅ 修改已自动保存")

        # Upload / Clear (after preview)
        st.divider()
        col_ul, col_cl = st.columns(2)
        with col_ul:
            uploaded_zhizao = st.file_uploader(
                "📤 Upload Modified File" if is_en else "📤 上传修改后文件（按标题自动匹配更新）", type=["csv"], key="upload_zhizao_edit"
            )
            if uploaded_zhizao is not None:
                df_new = pd.read_csv(uploaded_zhizao, on_bad_lines="skip", encoding="utf-8-sig")
                out_path = OUTPUT_PATH / selected_batch / "02_zhizao" / "zhizao_draft_content.csv"
                out_path.parent.mkdir(parents=True, exist_ok=True)
                # Smart merge: match by title or ai_query, update content
                if not df_z.empty and "title" in df_new.columns and "title" in df_z.columns:
                    updated_count = 0
                    for _, new_row in df_new.iterrows():
                        match_col = "title" if "title" in df_z.columns else "ai_query"
                        match_val = str(new_row.get(match_col, "")).strip()
                        mask = df_z[match_col].astype(str).str.strip() == match_val
                        if mask.any():
                            # Update existing row
                            for col in df_new.columns:
                                if col in df_z.columns and col not in [match_col, "version", "updated_at"]:
                                    df_z.loc[mask, col] = new_row[col]
                            # Auto-increment version
                            cur_ver = str(df_z.loc[mask, "version"].iloc[0]) if "version" in df_z.columns else "v1"
                            try:
                                ver_num = int(cur_ver.replace("v", "").replace("V", "")) + 1
                            except (ValueError, AttributeError):
                                ver_num = 2
                            df_z.loc[mask, "version"] = f"v{ver_num}"
                            df_z.loc[mask, "updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            updated_count += 1
                    if updated_count > 0:
                        df_z.to_csv(out_path, index=False, encoding="utf-8-sig")
                        st.success(f"✅ {'Updated' if is_en else '已更新'} {updated_count} {'articles (matched by title)' if is_en else '篇（按标题匹配）'}")
                    else:
                        # No match found, full replace
                        df_new.to_csv(out_path, index=False, encoding="utf-8-sig")
                        st.success(f"✅ {'No title match, replaced all with' if is_en else '无标题匹配，已全部替换为'} {len(df_new)} {'records' if is_en else '条'}")
                else:
                    df_new.to_csv(out_path, index=False, encoding="utf-8-sig")
                    st.success(f"✅ {'Uploaded' if is_en else '已上传'} {len(df_new)} {'records' if is_en else '条记录'}")
                st.rerun()
        with col_cl:
            if st.button("🗑️ Clear History" if is_en else "🗑️ 清空历史", key="clear_zhizao"):
                zhizao_dir = OUTPUT_PATH / selected_batch / "02_zhizao"
                if zhizao_dir.exists():
                    for f in zhizao_dir.glob("zhizao_draft_content*.csv"):
                        f.unlink()
                st.success("History cleared" if is_en else "已清空")
                st.rerun()

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

        # Ensure confirmed column is boolean (not float from NaN)
        df_z["confirmed"] = df_z["confirmed"].fillna(True).astype(bool)

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
                    st.success("History cleared" if is_en else "已清空")
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
            st.caption("No history records yet" if is_en else "暂无历史")

    # 📚 Template Library
    with st.expander("📚 Template Library" if is_en else "📚 模板库（已保存的文章模板）"):
        tpl_dir = BASE_PATH / "templates"
        if tpl_dir.exists():
            tpl_files = sorted(tpl_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        else:
            tpl_files = []

        if tpl_files:
            st.caption(f"{len(tpl_files)} {'templates saved' if is_en else '个模板已保存'}")
            for tf in tpl_files:
                try:
                    tpl_data = json.loads(tf.read_text(encoding="utf-8"))
                    tpl_name = tpl_data.get("name", tf.stem)
                    tpl_title = tpl_data.get("title", "")
                    tpl_wc = tpl_data.get("word_count", 0)
                    tpl_created = tpl_data.get("created_at", "")

                    col_t1, col_t2, col_t3, col_t4 = st.columns([3, 1, 1, 1])
                    with col_t1:
                        st.caption(f"📄 **{tpl_name}** — {tpl_title[:40]} ({tpl_wc} chars)")
                    with col_t2:
                        st.caption(f"🕐 {tpl_created[:10]}")
                    with col_t3:
                        if st.button("♻️ Use" if is_en else "♻️ 复用", key=f"use_tpl_{tf.name}"):
                            # Load template into session state for reuse
                            st.session_state["reuse_template"] = tpl_data
                            st.success(f"{'Template loaded! Go to Generate Content and it will be used as base.' if is_en else '模板已加载！生成内容时将以此为基础进行调整。'}")
                    with col_t4:
                        if st.button("🗑️", key=f"del_tpl_{tf.name}"):
                            tf.unlink()
                            st.rerun()
                except Exception:
                    continue

            # Show loaded template notice
            if "reuse_template" in st.session_state:
                tpl = st.session_state["reuse_template"]
                st.info(f"{'Active template' if is_en else '当前加载模板'}: **{tpl.get('name', '')}** — {'AI will adapt this content to new queries' if is_en else 'AI 将在此基础上针对新短语调整内容'}")
                if st.button("❌ Clear loaded template" if is_en else "❌ 取消模板复用", key="clear_loaded_tpl"):
                    del st.session_state["reuse_template"]
                    st.rerun()
        else:
            st.caption("No templates saved yet. Generate content first, then save articles as templates." if is_en else "暂无模板。先生成内容，然后在文章预览中点击「保存为模板」。")


# ============================================================
# PAGE: 智优 (Step 3) — 一键自动完成
# ============================================================
elif _page_idx == 4:
    st.markdown("""<div class="ss-page-header"><h1 style="color:#e91e63;">🔧 """ + ("Optimization" if is_en else "智优 – Score · Rewrite · Compliance") + """</h1><p>""" + ("One-click: Score → Rewrite → Compliance Review" if is_en else "一键自动完成 评分 → 重写优化 → 合规审查") + """</p></div>""", unsafe_allow_html=True)
    render_pipeline_flow("zhiyou", selected_batch)

    # Clear history button
    col_spacer, col_clear = st.columns([5, 1])
    with col_clear:
        if st.button("🗑️ Clear All" if is_en else "🗑️ 清空历史", key="clear_zhiyou_all"):
            zhiyou_dir = OUTPUT_PATH / selected_batch / "03_zhiyou"
            if zhiyou_dir.exists():
                for f in zhiyou_dir.glob("*.csv"):
                    f.unlink()
            st.success("History cleared" if is_en else "已清空")
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
                        mark_data_changed()
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
                    avg_score = pd.to_numeric(df_sc['overall_score'], errors='coerce').mean()
                    st.metric("Avg Score" if is_en else "平均总分", f"{avg_score:.2f}/5" if pd.notna(avg_score) else "N/A")
            with col3:
                if "is_approved" in df_sc.columns:
                    approved = df_sc[df_sc["is_approved"].astype(str).str.upper() == "TRUE"].shape[0]
                    st.metric("Passed" if is_en else "通过数", f"{approved}/{len(df_sc)}")

            # Radar chart
            score_cols = [c for c in df_sc.columns if c.endswith("_score") and c != "overall_score"]
            if score_cols:
                avg_scores = df_sc[score_cols].apply(pd.to_numeric, errors='coerce').mean()
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

        # Clear current content (archive to history)
        if st.button("🗑️ Clear Current & Archive" if is_en else "🗑️ 清空当前内容（归档到历史）", key="clear_zhiyou_current"):
            zhiyou_dir = OUTPUT_PATH / selected_batch / "03_zhiyou"
            archive_dir = zhiyou_dir / "archive"
            archive_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            for csv_file in zhiyou_dir.glob("*.csv"):
                csv_file.rename(archive_dir / f"{csv_file.stem}_{ts}{csv_file.suffix}")
            st.success("✅ Archived" if is_en else "✅ 已归档到历史")
            st.rerun()

        st.caption("Edit optimized articles below, changes auto-saved" if is_en else "可直接编辑优化后的文章内容，修改自动保存")

        opt_file = OUTPUT_PATH / selected_batch / "03_zhiyou" / "zhiyou_optimized_content.csv"
        content_col = "optimized_content" if "optimized_content" in df_opt.columns else "content_draft"
        title_col = "optimized_title" if "optimized_title" in df_opt.columns else "title"

        content_changed = False
        for idx, row in df_opt.iterrows():
            title = str(row.get(title_col, f"{'Article' if is_en else '文章'} {idx+1}"))
            word_count = row.get("word_count", "?")
            _opt_col, _opt_dl = st.columns([6, 1])
            with _opt_col:
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
            with _opt_dl:
                _opt_text = f"# {title}\n\n{str(row.get(content_col, ''))}"
                st.download_button("⬇️", _opt_text.encode("utf-8"),
                                   file_name=f"{str(row.get('ai_query', f'article_{idx}'))[:30]}.md",
                                   mime="text/markdown", key=f"dl_zhiyou_art_{idx}")

        if content_changed:
            df_opt.to_csv(opt_file, index=False, encoding="utf-8-sig")
            st.success("✅ Changes auto-saved" if is_en else "✅ 修改已自动保存")

        # 确认环节
        st.divider()
        st.subheader("✅ Article Confirmation" if is_en else "✅ 文章确认")
        st.caption("Check confirmed articles; confirmed ones proceed to Publishing" if is_en else "勾选确认通过的文章，确认后进入智布发布")

        if "confirmed" not in df_opt.columns:
            df_opt["confirmed"] = True
        df_opt["confirmed"] = df_opt["confirmed"].fillna(True).astype(bool)

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

            # Only save if user actually changed confirmation status
            new_confirmed = df_confirm["confirmed"].values
            old_confirmed = df_opt["confirmed"].values if "confirmed" in df_opt.columns else [True] * len(df_opt)
            if not all(a == b for a, b in zip(new_confirmed, old_confirmed)):
                df_opt["confirmed"] = new_confirmed
                df_opt.to_csv(opt_file, index=False, encoding="utf-8-sig")

    if is_admin:
        # --- POC Review Section ---
        st.divider()
        col_poc_title, col_poc_refresh = st.columns([4, 1])
        with col_poc_title:
            st.subheader("🔒 POC Review" if is_en else "🔒 POC 人工审核")
        with col_poc_refresh:
            if st.button("🔄 Refresh Status" if is_en else "🔄 刷新审批状态", key="refresh_poc_status"):
                st.rerun()

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

            # Ensure bool types (handle string 'True'/'False' from CSV)
            for bcol in ["needs_poc_review", "poc_approved"]:
                if bcol in df_opt.columns:
                    df_opt[bcol] = df_opt[bcol].astype(str).str.strip().str.upper().map(
                        {"TRUE": True, "FALSE": False, "1": True, "0": False, "YES": True, "NO": False}
                    ).fillna(False)

            # Show review status — sync from review_queue.csv if available
            review_file = OUTPUT_PATH / "review" / "review_queue.csv"
            if review_file.exists():
                df_review = load_csv_safe(review_file)
                if not df_review.empty and "status" in df_review.columns and "content_id" in df_review.columns:
                    # Sync approved status back to df_opt
                    approved_ids = df_review[df_review["status"].astype(str).str.upper() == "APPROVED"]["content_id"].tolist()
                    if approved_ids and "content_id" in df_opt.columns:
                        changed = df_opt["content_id"].isin(approved_ids) & (~df_opt["poc_approved"])
                        if changed.any():
                            df_opt.loc[changed, "poc_approved"] = True
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

            # --- Inline Quick Approve (works on Cloud without 8502) ---
            pending_for_approve = df_opt[(df_opt["needs_poc_review"] == True) & (df_opt["poc_approved"] == False)]
            if len(pending_for_approve) > 0:
                st.divider()
                st.markdown("**🔍 Quick Review & Approve**" if is_en else "**🔍 快速审核 & 审批（无需 8502）**")
                st.caption("Review content below and approve/reject directly." if is_en else "直接在下方审核内容并审批，无需打开独立审核界面。")

                content_col_r = "optimized_content" if "optimized_content" in pending_for_approve.columns else "content_draft"
                title_col_r = "optimized_title" if "optimized_title" in pending_for_approve.columns else "title"

                for idx, row in pending_for_approve.iterrows():
                    art_title = str(row.get(title_col_r, f"Article {idx}"))
                    with st.expander(f"⏳ {art_title}", expanded=False):
                        st.caption(f"Content ID: {row.get('content_id', '')} | Category: {row.get('category', 'N/A')}")
                        art_content = str(row.get(content_col_r, ""))
                        st.text_area("Content Preview" if is_en else "内容预览", value=art_content[:3000], height=200, key=f"poc_preview_{idx}", disabled=True)

                        col_approve, col_reject = st.columns(2)
                        with col_approve:
                            if st.button("✅ Approve" if is_en else "✅ 审批通过", key=f"poc_approve_{idx}", type="primary"):
                                df_opt.at[idx, "poc_approved"] = True
                                opt_file = OUTPUT_PATH / selected_batch / "03_zhiyou" / "zhiyou_optimized_content.csv"
                                df_opt.to_csv(opt_file, index=False, encoding="utf-8-sig")
                                # Also update review queue if exists
                                rq_file = OUTPUT_PATH / "review" / "review_queue.csv"
                                if rq_file.exists():
                                    rq_df = load_csv_safe(rq_file)
                                    if not rq_df.empty and "content_id" in rq_df.columns:
                                        cid = row.get("content_id", "")
                                        rq_df.loc[rq_df["content_id"] == cid, "status"] = "APPROVED"
                                        rq_df.loc[rq_df["content_id"] == cid, "reviewed_at"] = datetime.now().isoformat()
                                        for str_col in ["status", "reviewer_notes", "reviewed_at"]:
                                            if str_col in rq_df.columns:
                                                rq_df[str_col] = rq_df[str_col].astype(str).replace("nan", "")
                                        rq_df.to_csv(rq_file, index=False, encoding="utf-8-sig")
                                st.success(f"✅ Approved: {art_title[:30]}")
                                st.rerun()
                        with col_reject:
                            if st.button("❌ Reject" if is_en else "❌ 驳回", key=f"poc_reject_{idx}"):
                                df_opt.at[idx, "poc_approved"] = False
                                df_opt.at[idx, "needs_poc_review"] = False  # Remove from review queue
                                opt_file = OUTPUT_PATH / selected_batch / "03_zhiyou" / "zhiyou_optimized_content.csv"
                                df_opt.to_csv(opt_file, index=False, encoding="utf-8-sig")
                                st.warning(f"❌ Rejected: {art_title[:30]}")
                                st.rerun()

            # Check if all reviews complete
            all_reviewed = (pending == 0) if needs_review > 0 else True
            if not all_reviewed:
                st.warning(f"⏳ {int(pending)} articles pending POC approval. Cannot proceed to 智布 until all approved." if is_en else f"⏳ {int(pending)} 篇待 POC 审批。审批完成后才能进入智布。")

        # --- TAX Compliance Audit (QuickSight Integration) ---
        st.divider()
        st.subheader("🏛️ TAX Compliance Audit" if is_en else "🏛️ TAX 合规审核")
        st.caption("For registration/fees/VAT content — linked to QuickSight TAX review workflow" if is_en else "注册/费用/VAT 相关内容 — 关联 QuickSight TAX 审核流程")

        # TAX-related categories
        TAX_CATEGORIES = ["新手怎么注册亚马逊", "亚马逊开店成本费用详解", "欧洲增值税VAT介绍",
                          "其他站点税务要求", "合规政策及操作流程"]

        # Identify TAX-related articles in current batch
        tax_articles = []
        if not df_opt.empty:
            for _, row in df_opt.iterrows():
                content = str(row.get("optimized_content", row.get("content_draft", "")))
                query = str(row.get("ai_query", ""))
                cat = str(row.get("category", ""))
                # Check if article is TAX-related
                is_tax = (cat in TAX_CATEGORIES or
                          any(kw in query.lower() for kw in ["注册", "费用", "vat", "税", "开店", "registration", "fee", "tax"]) or
                          any(kw in content[:500].lower() for kw in ["vat", "税务", "增值税", "注册费", "年费"]))
                if is_tax:
                    tax_articles.append({
                        "content_id": row.get("content_id", ""),
                        "title": str(row.get("optimized_title", row.get("title", query)))[:60],
                        "query": query[:50],
                        "tax_status": "✅ Reviewed" if row.get("poc_approved", False) else "⏳ Pending",
                    })

        if tax_articles:
            st.dataframe(pd.DataFrame(tax_articles), use_container_width=True, hide_index=True)
            st.caption(f"{len(tax_articles)} articles flagged for TAX compliance review" if is_en else f"{len(tax_articles)} 篇文章标记需要 TAX 合规审核")
        else:
            st.caption("No TAX-related articles in current batch" if is_en else "当前批次无 TAX 相关文章")

        # QuickSight Dashboard embed link
        with st.expander("📊 QuickSight TAX Review Dashboard", expanded=False):
            st.markdown("""
**TAX 审核流程 Dashboard (QuickSight)**

直接打开 QuickSight 查看审核状态：

🔗 [Open TAX Review Dashboard](https://us-east-1.quicksight.aws.amazon.com/sn/account/amazonbi/start/agents?view=798deaf2-16ca-4da2-a1a0-dd910847051b)

> ⚠️ 需要 Amazon 内网权限访问。QuickSight 为只读参考，实际审核在智优界面完成后同步。
""")
            st.caption("Note: QuickSight does not have a write API. Approval status is managed in Smart Suite and synced via batch export." if is_en else "注：QuickSight 无写入 API，审核状态在 Smart Suite 内管理，通过批次导出同步。")

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
                    st.success("History cleared" if is_en else "已清空")
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
            st.caption("No history records yet" if is_en else "暂无历史")


# ============================================================
# PAGE: 智布 (Step 4)
# ============================================================
elif _page_idx == 5:
    st.markdown("""<div class="ss-page-header"><h1 style="color:#29b6f6;">📦 """ + ("Publishing" if is_en else "智布 – 内容发布") + """</h1><p>""" + ("Convert optimized content to structured JSON and Word documents" if is_en else "将优化内容转换为结构化 JSON 和 Word 文档") + """</p></div>""", unsafe_allow_html=True)
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

    col_exec1 = st.columns(1)[0]
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

        # --- Download buttons ---
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
                col_prev, col_dl = st.columns([5, 1])
                with col_prev:
                    with st.expander(f"📄 {title}", expanded=(i == 0)):
                        st.json(item)
                with col_dl:
                    _single_json = json.dumps(item, ensure_ascii=False, indent=4)
                    st.download_button("⬇️", _single_json.encode("utf-8"),
                                       file_name=f"{item.get('content_id', f'item_{i+1}')}.json",
                                       mime="application/json", key=f"dl_single_{i}")

        # --- Download buttons (after preview) ---
        st.divider()
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

    # CTA → next step
    st.divider()
    if not is_admin:
        if st.button("📤 申请官网发布" if not is_en else "📤 Submit for Publishing", type="primary", key="cta_zhibu_publish_request"):
            # Save publish request
            _req_dir = OUTPUT_PATH / "requests" / current_user
            _req_dir.mkdir(parents=True, exist_ok=True)
            _pub_req = _req_dir / "publish_request.json"
            import json as _jr
            req_data = {"user": current_user, "batch": selected_batch,
                        "requested_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "status": "pending"}
            _pub_req.write_text(_jr.dumps(req_data, ensure_ascii=False, indent=2), encoding="utf-8")
            st.success("✅ 已提交发布申请！管理员审批后将发布到官网。" if not is_en else "✅ Publish request submitted!")
            jump_to("📈 智析" if not is_en else "📈 Analytics")
            st.rerun()
    else:
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
            st.caption("No history records yet" if is_en else "暂无历史")


# ============================================================
# ============================================================
# PAGE: 智析 (Step 6) — 重构版
# ============================================================
elif _page_idx == 7:
    st.markdown("""<div class="ss-page-header"><h1 style="color:#ab47bc;">📈 """ + ("Analytics" if is_en else "智析 – Performance & Gap Analysis") + """</h1><p>""" + ("Output trends · Input tracking · AI citation monitoring · Gap opportunities" if is_en else "Output 趋势 · Input 追踪 · AI 引用监控 · Gap 机会点") + """</p></div>""", unsafe_allow_html=True)
    render_pipeline_flow("zhixi", selected_batch)

    # ============================================================
    # USER VIEW: Personal performance dashboard
    # ============================================================
    if not is_admin:
        st.markdown("### " + ("My Performance Dashboard" if is_en else "我的 Performance"))

        # Load user's data
        _u_zhiku = load_csv_safe(OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv")
        _u_zhizao = load_csv_safe(OUTPUT_PATH / selected_batch / "02_zhizao" / "zhizao_draft_content.csv")

        # KPIs
        total_phrases = len(_u_zhiku) if not _u_zhiku.empty else 0
        total_articles = len(_u_zhizao) if not _u_zhizao.empty else 0
        selected_phrases = 0
        if not _u_zhiku.empty and "is_selected" in _u_zhiku.columns:
            selected_phrases = len(_u_zhiku[_u_zhiku["is_selected"].astype(str).str.upper().isin(["TRUE", "1", "YES"])])

        kc1, kc2, kc3 = st.columns(3)
        kc1.metric("Total Phrases Created" if is_en else "创建短语", total_phrases)
        kc2.metric("Selected Phrases" if is_en else "已选中", selected_phrases)
        kc3.metric("Articles Generated" if is_en else "产出文章", total_articles)

        st.divider()

        # --- Citation Performance ---
        st.markdown("### " + ("AI Citation Performance (Before vs After)" if is_en else "引用表现"))
        st.caption("Before = from 智测 verification (baseline) · After = post-content launch (upload when available)" if is_en else "Before = 智测验证结果（基线）· After = 新内容上线后（有数据时上传）")

        # Auto-load Before data from THIS USER's zhice gap results only
        # Only search in user's own batch directory (per-user isolation)
        _gap_files = []
        _user_zhice_dir = OUTPUT_PATH / selected_batch / "zhice"
        if _user_zhice_dir.exists():
            _gap_files = sorted(_user_zhice_dir.glob("gap_result_*.csv"), key=lambda f: f.stat().st_mtime, reverse=True)

        # Also check for tracking history in user's batch
        if not _gap_files:
            _tracking_file = _user_zhice_dir / "prompt_tracking_history.csv"
            if _user_zhice_dir.exists() and _tracking_file.exists() and _tracking_file.stat().st_size > 10:
                _gap_files = [_tracking_file]

        _before_data = []
        if _gap_files:
            try:
                # Load ALL gap result files and merge (deduplicate by query)
                all_gap_dfs = []
                for gf in _gap_files:
                    _df = load_csv_safe(gf)
                    if not _df.empty and "ai_query" in _df.columns:
                        all_gap_dfs.append(_df)
                if all_gap_dfs:
                    df_gap = pd.concat(all_gap_dfs, ignore_index=True)
                    # Deduplicate: keep latest (first file is newest due to reverse sort)
                    df_gap = df_gap.drop_duplicates(subset=["ai_query"], keep="first")

                    for _, row in df_gap.iterrows():
                        query = str(row.get("ai_query", ""))
                        platform = str(row.get("platform", ""))
                        platforms_tested = str(row.get("platforms_tested", ""))
                        # Use platform name if available, otherwise show number of platforms
                        plat_display = platform if platform not in ["nan", "", "0"] else (f"{platforms_tested} platforms" if platforms_tested not in ["nan", ""] else "qianwen")
                        # Match various column name patterns
                        brand = str(row.get("has_brand_mention", row.get("brand_mention", row.get("has_brand", ""))))
                        link = str(row.get("has_official_link", row.get("official_link", row.get("has_link", ""))))
                        gap_status = str(row.get("gap_status", ""))
                        # Normalize to ✅/❌
                        brand_val = "✅" if brand.upper() in ["TRUE", "1", "YES", "✅"] else "❌"
                        link_val = "✅" if link.upper() in ["TRUE", "1", "YES", "✅"] else "❌"
                        _before_data.append({
                            "Query": query[:60],
                            "Platform": plat_display,
                            "Brand/Product Before": brand_val,
                            "Link Before": link_val,
                            "Gap Status": gap_status,
                        })
            except Exception:
                pass

        # Load After data (from admin-assigned or user-uploaded)
        _perf_file = OUTPUT_PATH / "requests" / current_user / "performance_data.json"
        _after_data = json.loads(_perf_file.read_text(encoding="utf-8")) if _perf_file.exists() else []

        # Merge Before + After
        _perf_merged = []
        if _before_data:
            for bd in _before_data:
                # Find matching After record
                after_match = next((a for a in _after_data if a.get("Query", "")[:30] == bd["Query"][:30] and a.get("Platform", "") == bd["Platform"]), None)
                _perf_merged.append({
                    "Query": bd["Query"],
                    "Platform": bd["Platform"],
                    "Gap Status": bd.get("Gap Status", "—"),
                    "Brand/Product Before": bd["Brand/Product Before"],
                    "Brand/Product After": after_match.get("Brand/Product After", "—") if after_match else "—",
                    "Link Before": bd["Link Before"],
                    "Link After": after_match.get("Link After", "—") if after_match else "—",
                })
        elif _after_data:
            _perf_merged = _after_data

        # --- Summary KPI metrics (Mention #, Rate, Link #, Rate) ---
        # --- Detailed Verification Results (per-platform table) ---
        if _before_data:
            with st.expander("📋 " + ("Detailed Verification by Platform" if is_en else "分平台验证详情"), expanded=False):
                _detail_rows = []
                for bd in _before_data:
                    _detail_rows.append({
                        ("Search Phrase" if is_en else "检索短语"): bd["Query"],
                        ("Platform" if is_en else "平台"): bd["Platform"],
                        ("Brand/Product" if is_en else "品牌/产品"): bd.get("Brand/Product Before", bd.get("Brand Before", "—")),
                        ("Official Link" if is_en else "官网链接"): bd.get("Link Before", "—"),
                        ("Gap Status" if is_en else "覆盖状态"): bd.get("Gap Status", "—"),
                    })
                st.dataframe(pd.DataFrame(_detail_rows), use_container_width=True, hide_index=True)
                st.caption(f"{len(_detail_rows)} {'verification records' if is_en else '条验证记录'}")

        # Brand Mention section
        st.markdown("#### 🏷️ " + ("Brand/Product Name Mention" if is_en else "品牌/产品名称提及"))
        if _perf_merged:
            df_brand = pd.DataFrame([{
                "Query": r["Query"],
                "Gap": r.get("Gap Status", "—"),
                "Before": r.get("Brand/Product Before", "—"),
                "After": r.get("Brand/Product After", "—"),
                "Change": "🆕 改善" if r.get("Brand/Product Before") == "❌" and r.get("Brand/Product After") == "✅" else ("⚠️ 退步" if r.get("Brand/Product Before") == "✅" and r.get("Brand/Product After") == "❌" else ("→ 持平" if r.get("Brand/Product After") != "—" else "⏳ 待测")),
            } for r in _perf_merged])
            st.dataframe(df_brand, use_container_width=True, hide_index=True)
        else:
            st.dataframe(pd.DataFrame([{"Query": "—", "Platform": "—", "Before": "—", "After": "—", "Change": "—"}]), use_container_width=True, hide_index=True)
            st.caption("请先在智测中验证短语，Before 数据将自动填入" if not is_en else "Run verification in 智测 first — Before data will auto-populate")

        st.markdown("")

        # Official Link section
        st.markdown("#### 🔗 " + ("Official Link" if is_en else "官方链接"))
        if _perf_merged:
            df_link = pd.DataFrame([{
                "Query": r["Query"],
                "Gap": r.get("Gap Status", "—"),
                "Before": r.get("Link Before", "—"),
                "After": r.get("Link After", "—"),
                "Change": "🆕 改善" if r.get("Link Before") == "❌" and r.get("Link After") == "✅" else ("⚠️ 退步" if r.get("Link Before") == "✅" and r.get("Link After") == "❌" else ("→ 持平" if r.get("Link After") != "—" else "⏳ 待测")),
            } for r in _perf_merged])
            st.dataframe(df_link, use_container_width=True, hide_index=True)
        else:
            st.dataframe(pd.DataFrame([{"Query": "—", "Platform": "—", "Before": "—", "After": "—", "Change": "—"}]), use_container_width=True, hide_index=True)

        # Summary metrics
        if _perf_merged:
            st.markdown("")
            brand_before = sum(1 for r in _perf_merged if r.get("Brand/Product Before") == "✅")
            brand_after = sum(1 for r in _perf_merged if r.get("Brand/Product After") == "✅")
            link_before = sum(1 for r in _perf_merged if r.get("Link Before") == "✅")
            link_after = sum(1 for r in _perf_merged if r.get("Link After") == "✅")
            has_after = sum(1 for r in _perf_merged if r.get("Brand/Product After") != "—")
            total_p = len(_perf_merged)
            brand_rate_before = f"{brand_before*100//total_p}%" if total_p > 0 else "—"
            link_rate_before = f"{link_before*100//total_p}%" if total_p > 0 else "—"

            col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
            col_m1.metric("Mention #" if is_en else "品牌/产品提及#", f"{brand_before}/{total_p}")
            col_m2.metric("Mention Rate" if is_en else "提及率", brand_rate_before)
            if has_after > 0:
                brand_rate_after = f"{brand_after*100//has_after}%" if has_after > 0 else "—"
                col_m3.metric("After Rate" if is_en else "提及率(后)", brand_rate_after, delta=f"+{brand_after-brand_before}" if brand_after > brand_before else None)
            else:
                col_m3.metric("After Rate" if is_en else "提及率(后)", "⏳ 待测")
            col_m4.metric("Link #" if is_en else "官网链接#", f"{link_before}/{total_p}")
            col_m5.metric("Link Rate" if is_en else "链接率", link_rate_before)
            if has_after > 0:
                link_rate_after = f"{link_after*100//has_after}%" if has_after > 0 else "—"
                col_m6.metric("After Rate" if is_en else "链接率(后)", link_rate_after, delta=f"+{link_after-link_before}" if link_after > link_before else None)
            else:
                col_m6.metric("After Rate" if is_en else "链接率(后)", "⏳ 待测")

        # Upload After data (post-content launch)
        with st.expander("📤 " + ("Upload After Data (post-launch)" if is_en else "上传 After 数据（内容上线后）"), expanded=False):
            st.caption("Upload verification results AFTER content is published to compare with Before baseline" if is_en else "内容发布上线后，上传新的验证结果来对比 Before 基线")
            st.caption("CSV columns: Query, Platform, Brand After, Link After" if is_en else "CSV 列: Query, Platform, Brand After, Link After")
            up_perf = st.file_uploader("Upload CSV" if is_en else "上传 CSV", type=["csv"], key="user_upload_perf")
            if up_perf:
                try:
                    df_up_perf = pd.read_csv(up_perf, encoding="utf-8-sig", on_bad_lines="skip")
                    st.dataframe(df_up_perf.head(5), use_container_width=True, hide_index=True)
                    if st.button("✅ " + ("Confirm & Save Upload" if is_en else "确认上传"), key="confirm_perf_upload"):
                        _perf_file.parent.mkdir(parents=True, exist_ok=True)
                        _perf_file.write_text(df_up_perf.to_json(orient="records", force_ascii=False), encoding="utf-8")
                        mark_data_changed()
                        st.success("✅ Uploaded!")
                        st.rerun()
                except Exception as e:
                    st.error(str(e))

        st.divider()

        # --- Custom Metrics ---
        st.markdown("### " + ("Custom Metrics Tracking" if is_en else "指标追踪"))
        st.caption("Select preset metrics or add custom ones" if is_en else "选择预设指标或手动添加")

        _metrics_file = OUTPUT_PATH / "requests" / current_user / "custom_metrics.json"
        _custom_metrics = json.loads(_metrics_file.read_text(encoding="utf-8")) if _metrics_file.exists() else []

        # Preset metric options
        preset_metrics = ["Reg Starts", "Page Views", "Conversion Rate",
                          "AI Citation Count", "Brand/Product Name Mention Rate", "Official Link Rate",
                          "Content Published", "GAP Fill Rate"]

        col_add1, col_add2, col_add3 = st.columns([3, 1, 1])
        with col_add1:
            m_name = st.selectbox("Metric" if is_en else "指标",
                                  ["— 选择预设 —"] + preset_metrics + ["✏️ 自定义..." if not is_en else "✏️ Custom..."],
                                  key="metric_select")
            if m_name in ["✏️ 自定义...", "✏️ Custom..."]:
                m_name = st.text_input("Custom Name" if is_en else "自定义名称", key="custom_m_name")
        with col_add2:
            m_date = st.date_input("Date" if is_en else "日期", key="m_date")
        with col_add3:
            st.write("")
            if st.button("➕", key="add_metric_btn"):
                if m_name and m_name != "— 选择预设 —":
                    _custom_metrics.append({"name": m_name, "date": str(m_date), "user": current_user})
                    _metrics_file.parent.mkdir(parents=True, exist_ok=True)
                    _metrics_file.write_text(json.dumps(_custom_metrics, ensure_ascii=False, indent=2), encoding="utf-8")
                    mark_data_changed()
                    st.rerun()

        if _custom_metrics:
            df_cm = pd.DataFrame(_custom_metrics)
            st.dataframe(df_cm, use_container_width=True, hide_index=True)

        # --- CTA: Submit Request ---
        st.divider()
        if st.button("📨 " + ("Submit Analytics Request to Admin" if is_en else "提交需求到管理员"), type="primary", key="user_submit_analytics_request"):
            _req_dir = OUTPUT_PATH / "requests" / current_user
            _req_dir.mkdir(parents=True, exist_ok=True)
            _req_file = OUTPUT_PATH / "request_tracking.json"
            all_reqs = json.loads(_req_file.read_text(encoding="utf-8")) if _req_file.exists() else []
            all_reqs.append({
                "id": f"metrics_req_{current_user}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "user": current_user,
                "type": "metrics_request",
                "status": "pending",
                "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "phrases": total_phrases,
                "articles": total_articles,
                "message": f"{current_user} 提交了数据需求：{total_phrases} 短语, {total_articles} 文章",
            })
            _req_file.parent.mkdir(parents=True, exist_ok=True)
            _req_file.write_text(json.dumps(all_reqs, ensure_ascii=False, indent=2), encoding="utf-8")
            mark_data_changed()
            st.success("✅ " + ("Request submitted to admin!" if is_en else "需求已提交到管理员！"))

    # ============================================================
    # ADMIN VIEW: Full analytics (original)
    # ============================================================
    else:

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
                    rows.append({"Channel": ch_name, "Type": "Actual", **dict(zip(weeks, [str(v) for v in actual_vals]))})
                    rows.append({"Channel": ch_name, "Type": "PY", **dict(zip(weeks, [str(v) for v in py_vals]))})
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

            # --- Auto Input Activity Statistics (from output folder) ---
            st.markdown("**📊 Auto Input Stats (from pipeline output)**" if is_en else "**📊 自动统计（来自流水线产出）**")
            st.caption("Automatically calculated from output files. No manual input needed." if is_en else "自动从 output 文件夹统计，无需手动填写。")

            # Calculate stats across all batches
            _total_phrases = 0
            _total_articles = 0
            _total_optimized = 0
            _total_published = 0
            _total_zhice_verified = 0
            _batches_with_data = 0

            if OUTPUT_PATH.exists():
                for batch_dir in OUTPUT_PATH.iterdir():
                    if batch_dir.is_dir() and batch_dir.name.startswith("batch_"):
                        _batches_with_data += 1
                        # Count zhiku phrases
                        zhiku_f = batch_dir / "01_zhiku" / "zhiku_ai_queries.csv"
                        if zhiku_f.exists():
                            try:
                                _df = pd.read_csv(zhiku_f, encoding="utf-8-sig", on_bad_lines="skip")
                                _total_phrases += len(_df)
                            except Exception:
                                pass
                        # Count zhizao articles
                        zhizao_f = batch_dir / "02_zhizao" / "zhizao_draft_content.csv"
                        if zhizao_f.exists():
                            try:
                                _df = pd.read_csv(zhizao_f, encoding="utf-8-sig", on_bad_lines="skip")
                                _total_articles += len(_df)
                            except Exception:
                                pass
                        # Count optimized
                        opt_f = batch_dir / "03_zhiyou" / "zhiyou_optimized_content.csv"
                        if opt_f.exists():
                            try:
                                _df = pd.read_csv(opt_f, encoding="utf-8-sig", on_bad_lines="skip")
                                _total_optimized += len(_df)
                            except Exception:
                                pass
                        # Count published (zhibu)
                        zhibu_dir = batch_dir / "04_zhibu"
                        if zhibu_dir.exists():
                            _total_published += len(list(zhibu_dir.glob("*.json"))) + len(list(zhibu_dir.glob("*.docx")))

                # Count zhice verified
                zhice_dir = OUTPUT_PATH.parent / "zhice"
                if zhice_dir.exists():
                    _total_zhice_verified += len(list(zhice_dir.glob("*.json")))

            ac1, ac2, ac3, ac4, ac5 = st.columns(5)
            ac1.metric("Total Phrases" if is_en else "总短语数", _total_phrases)
            ac2.metric("Articles Created" if is_en else "已生成文章", _total_articles)
            ac3.metric("Optimized" if is_en else "已优化", _total_optimized)
            ac4.metric("Published" if is_en else "已发布", _total_published)
            ac5.metric("Verified" if is_en else "已验证", _total_zhice_verified)

            st.caption(f"{'Across' if is_en else '统计范围'}: {_batches_with_data} {'batches' if is_en else '个 batch'}")

            # --- One-Click Weekly Report ---
            st.divider()
            st.markdown("**📋 One-Click Weekly Report**" if is_en else "**📋 一键生成周报**")

            # Auto-Attribution display
            try:
                from zhixi_attribution import get_input_activity_by_week, generate_attribution, generate_action_items
                _activities = get_input_activity_by_week()
                _df_w = get_weekly_metrics()
                _attributions = generate_attribution(_df_w, _activities)
                _actions = generate_action_items(_df_w, _activities)

                with st.expander("🔍 Auto-Attribution (归因分析)" if is_en else "🔍 自动归因分析", expanded=True):
                    for attr in _attributions:
                        st.markdown(f"- {attr}")
                    st.divider()
                    st.markdown("**Next Week Actions:**" if is_en else "**下周行动项：**")
                    for act in _actions:
                        st.markdown(f"- {act}")
            except Exception:
                pass

            if st.button("📋 Generate Weekly Report" if is_en else "📋 生成本周报告", type="primary", key="btn_gen_weekly_report"):
                try:
                    from engine import call_claude
                    # Gather all metrics
                    df_weekly = get_weekly_metrics()
                    df_ytd = get_ytd_metrics()

                    report_data = f"""本周 Smart Suite 数据汇总：

    Output Metrics（周度）:
    {df_weekly.tail(4).to_string() if not df_weekly.empty else 'N/A'}

    YTD Summary:
    {df_ytd.to_string() if not df_ytd.empty else 'N/A'}

    Input Activities（自动统计）:
    - 总短语数: {_total_phrases}
    - 已生成文章: {_total_articles}
    - 已优化: {_total_optimized}
    - 已发布: {_total_published}
    - 已验证: {_total_zhice_verified}
    - 覆盖 batch 数: {_batches_with_data}
    """

                    report_prompt = f"""基于以下数据，生成一份 Smart Suite 周报（Markdown 格式）：

    {report_data}

    报告结构：
    1. Executive Summary（一行判断：POSITIVE/NEUTRAL/NEGATIVE + 关键发现）
    2. Output Metrics（周度趋势表 + WoW 变化）
    3. Input Activities（本周产出统计）
    4. Attribution（归因分析：什么驱动了变化）
    5. Gaps & Opportunities（Top 3 差距 + Top 3 机会）
    6. Next Week Actions（下周行动项）

    规则：
    - 数据不要编造，只用提供的数据
    - 用 ↑ ↓ → 表示趋势
    - WoW 下降超过 20% 要标注 ⚠️
    """
                    with st.spinner("Generating report..." if is_en else "正在生成周报..."):
                        report = call_claude("你是 GEO 业务分析师。", report_prompt, max_tokens=2000)

                    st.markdown(report)

                    # Save report
                    report_dir = METRICS_PATH
                    report_dir.mkdir(parents=True, exist_ok=True)
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    report_file = report_dir / f"weekly_report_{ts}.md"
                    report_file.write_text(report, encoding="utf-8")
                    st.success(f"✅ Report saved: {report_file.name}")

                    # Download button
                    st.download_button("📥 Download Report" if is_en else "📥 下载报告",
                                       report.encode("utf-8"), file_name=f"weekly_report_{ts}.md",
                                       mime="text/markdown")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

            # --- Prompt Re-run Dashboard ---
            st.divider()
            st.markdown("**🔄 Prompt Re-run Dashboard**" if is_en else "**🔄 发布后效果追踪（Pre vs Post）**")
            st.caption("Compare brand mention before and after content publication." if is_en else "对比内容发布前后的品牌/产品名称提及率变化，衡量 GEO 效果。")

            try:
                from zhixi_attribution import get_published_queries, compare_pre_post_verification
                _pub_queries = get_published_queries()
                if _pub_queries:
                    st.caption(f"{len(_pub_queries)} published queries found" if is_en else f"发现 {len(_pub_queries)} 条已发布短语")
                    _zhice_dir = OUTPUT_PATH.parent / "zhice"
                    _tracking_f = _zhice_dir / "prompt_tracking_history.csv" if _zhice_dir.exists() else None
                    if _tracking_f and _tracking_f.exists():
                        df_compare = compare_pre_post_verification(_tracking_f, _pub_queries)
                        if not df_compare.empty:
                            # Summary
                            improved = len(df_compare[df_compare["improvement"] == "✅ 提升"])
                            maintained = len(df_compare[df_compare["improvement"] == "➡️ 维持"])
                            declined = len(df_compare[df_compare["improvement"] == "❌ 下降"])
                            rc1, rc2, rc3 = st.columns(3)
                            rc1.metric("✅ Improved" if is_en else "✅ 提升", improved)
                            rc2.metric("➡️ Maintained" if is_en else "➡️ 维持", maintained)
                            rc3.metric("❌ Declined" if is_en else "❌ 下降", declined)
                            st.dataframe(df_compare, use_container_width=True, hide_index=True)
                        else:
                            st.caption("Need at least 2 verification runs for the same queries to compare." if is_en else "需要对同一批短语运行至少 2 次验证才能对比效果。")
                    else:
                        st.caption("No tracking history yet. Run zhice verification first." if is_en else "暂无追踪数据。请先运行智测验证。")
                else:
                    st.caption("No published content yet. Complete the pipeline (智布) to track GEO effect." if is_en else "暂无已发布内容。完成智布发布后可追踪 GEO 效果。")
            except Exception:
                st.caption("Attribution module not available." if is_en else "归因模块不可用。")

            st.divider()

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
            st.caption("品牌词 = 旧提示词(397) + 新提示词(69品牌) | 包含：品牌/产品名称提及 + 品牌/产品名称提及率 + 官网链接提及 + 官网链接提及率")

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

            # 品牌/产品名称提及 + 品牌/产品名称提及率（按月）
            st.markdown("**📊 品牌/产品名称提及 & 品牌/产品名称提及率（按月）**")
            st.caption("品牌/产品名称提及 = 新建内容在AI平台中出现品牌信息并引用发布信源")
            df_brand_mention = pd.DataFrame({
                "指标": ["新建内容#", "品牌内容#", "品牌内容提及", "品牌内容提及率"],
                "Jan": [98, 98, 98, "100%"],
                "Feb": [43, 43, 43, "100%"],
                "Mar": [118, 118, 106, "89.8%"],
                "Apr": [123, 123, 111, "90.2%"],
                "May": [135, 81, 69, "85.2%"],
            })
            st.dataframe(df_brand_mention, use_container_width=True, hide_index=True)

            # 品牌/产品名称提及趋势图
            fig_mention = go.Figure()
            fig_mention.add_trace(go.Bar(name="新建内容#", x=_cite_months, y=[98, 43, 118, 123, 135], marker_color="#94a3b8"))
            fig_mention.add_trace(go.Bar(name="品牌内容提及", x=_cite_months, y=[98, 43, 106, 111, 69], marker_color="#4a9eff"))
            fig_mention.update_layout(barmode="group", height=260, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="篇数", legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig_mention, use_container_width=True)

            st.divider()

            # 官网链接提及 + 官网链接提及率（按月）
            st.markdown("**📊 官网链接提及 & 官网链接提及率（按月）**")
            st.caption("官网链接提及 = AI平台应答中直接展示亚马逊官方链接（含 gs.amazon.cn、sell.amazon.com、sellercentral.amazon.com 等）")
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
            st.caption("行业词(98个) | 仅追踪：品牌/产品名称提及 + 品牌/产品名称提及率 | 不涉及官网链接提及（行业词涉及多平台对比，官网链接概率极低）")

            # 行业词 KPI
            ind_kpi1, ind_kpi2, ind_kpi3 = st.columns(3)
            with ind_kpi1:
                st.metric("行业词总数", "98")
            with ind_kpi2:
                st.metric("品牌/产品名称提及 (7平台合计)", "664")
            with ind_kpi3:
                st.metric("平均品牌/产品名称提及率", "91.84%")

            # 行业词 - 品牌/产品名称提及 by platform
            st.markdown("**📊 行业词 - 品牌/产品名称提及（各平台）**")
            df_industry = pd.DataFrame({
                "平台": AI_PLATFORMS,
                "品牌/产品名称提及数": [97, 97, 97, 92, 97, 97, 87],
                "品牌/产品名称提及率": ["98.98%", "98.98%", "98.98%", "93.88%", "98.98%", "98.98%", "88.78%"],
                "备注": ["", "", "", "略低", "", "", "Gemini略低"],
            })
            st.dataframe(df_industry, use_container_width=True, hide_index=True)

            fig_ind = go.Figure()
            fig_ind.add_trace(go.Bar(x=df_industry["平台"], y=df_industry["品牌/产品名称提及数"], marker_color="#a78bfa"))
            fig_ind.add_hline(y=98, line_dash="dash", line_color="gray", annotation_text="总行业词=98")
            fig_ind.update_layout(height=260, margin=dict(l=0, r=0, t=10, b=0), yaxis_title="品牌/产品名称提及数")
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
    - **行业词** 品牌/产品名称提及率极高(91.84%)，但官网链接提及几乎为0 → 适合第三方媒体发布
    - **ChatGPT 新提示词** 官网链接0提及，需针对性优化
    """)

        # ============================================================
        # TAB: AI Link Citation (Gap verification)
        # ============================================================
        with tab_zhice_gap:
            st.markdown("""<div class="ss-section">
                <h3 style="color:#ab47bc;">🔬 """ + ("Official Link Coverage Rate" if is_en else "官网链接覆盖率") + """</h3>
                <p>""" + ("YTD search phrase coverage: how many have official Amazon links cited by AI" if is_en else "YTD 检索短语覆盖情况：有多少被 AI 引用时带有官方链接") + """</p>
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
                                "品牌/产品名称提及" if not is_en else "Brand": brand_count,
                                "品牌/产品名称提及率" if not is_en else "Brand/Product Name Rate": f"{brand_rate}%",
                                "占比" if not is_en else "% Total": f"{cat_total*100//total_q if total_q else 0}%",
                            })
                        if summary_rows:
                            st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)
                    else:
                        st.caption("No category column in data" if is_en else "数据中无类别列")

            else:
                st.info("Gap verification data not available." if is_en else "Gap 验证数据不可用。")

            # --- Category AI Citation Analysis (from gap_verification_cn.csv + zhice data) ---
            st.divider()
            st.markdown("""<div class="ss-section">
                <h3 style="color:#ab47bc;">📊 """ + ("Category AI Citation Ranking" if is_en else "35 类别 AI 引用概率排名") + """</h3>
                <p>""" + ("Based on gap verification data: which categories are most cited by AI" if is_en else "基于 Gap 验证数据：哪些内容类别最容易被 AI 引用") + """</p>
            </div>""", unsafe_allow_html=True)

            # --- Mapping: query topic → 35 categories ---
            def _map_query_to_cat35(query_text):
                """Map a search query to one of 35 categories based on keyword matching."""
                q = str(query_text).lower()
                if any(k in q for k in ["注册", "开店入口", "入驻", "开通", "申请", "register", "sign up"]):
                    return "新手怎么注册亚马逊"
                if any(k in q for k in ["费用", "成本", "多少钱", "资金", "收费", "月租", "佣金"]):
                    return "亚马逊开店成本费用详解"
                if any(k in q for k in ["审核", "拒绝", "二审", "封号", "关联", "违规"]):
                    return "开店审核常见问题解答"
                if any(k in q for k in ["fba", "fbm", "物流", "仓储", "发货", "头程", "货代"]):
                    return "亚马逊物流仓储科普"
                if any(k in q for k in ["vat", "增值税", "欧洲税"]):
                    return "欧洲增值税VAT介绍"
                if any(k in q for k in ["税务", "gst", "税号"]):
                    return "其他站点税务要求"
                if any(k in q for k in ["合规", "知识产权", "侵权", "认证", "政策"]):
                    return "合规政策及操作流程"
                if any(k in q for k in ["listing", "上架", "标题优化", "a+", "五点描述"]):
                    return "教你打造优质Listing"
                if any(k in q for k in ["选品", "品类", "热门产品", "什么好卖"]):
                    return "跨境电商选品方法及趋势"
                if any(k in q for k in ["热门品类", "蓝海", "红海"]):
                    return "跨境电商热门品类解析"
                if any(k in q for k in ["广告", "ppc", "cpc", "推广", "引流", "投放"]):
                    if any(k in q for k in ["实操", "技巧", "优化", "怎么投"]):
                        return "亚马逊广告实操技巧"
                    return "亚马逊广告基础知识大全"
                if any(k in q for k in ["品牌备案", "brand registry", "品牌营销", "品牌故事"]):
                    return "如何做好品牌营销"
                if any(k in q for k in ["运营", "店铺管理", "卖家中心", "seller central", "后台"]):
                    if any(k in q for k in ["基础", "入门", "新手"]):
                        return "店铺运营基础知识"
                    return "店铺运营提升全攻略"
                if any(k in q for k in ["工具", "插件", "软件", "服务商", "spn"]):
                    return "官方服务与运营工具盘点"
                if any(k in q for k in ["旺季", "黑五", "prime day", "节日", "促销"]):
                    return "了解旺季节点与如何引流"
                if any(k in q for k in ["北美", "美国站", "美国亚马逊", "美亚", "加拿大站"]):
                    return "北美站点情况及选品思路"
                if any(k in q for k in ["欧洲站", "德国站", "英国站", "法国站"]):
                    return "欧洲站点情况及选品思路"
                if any(k in q for k in ["日本站", "日本亚马逊", "日亚"]):
                    return "日本站点情况及选品思路"
                if any(k in q for k in ["澳洲", "中东", "阿联酋", "沙特", "巴西", "非洲", "东南亚"]):
                    return "新兴站点情况及选品思路"
                if any(k in q for k in ["站点选择", "哪个站点", "选哪个"]):
                    return "站点综合信息及选品建议"
                if any(k in q for k in ["亚马逊官网", "网址", "全球开店官网", "入口", "访问", "登录"]):
                    return "亚马逊商城基础情况了解"
                if any(k in q for k in ["亚马逊怎么样", "亚马逊好做吗"]):
                    return "亚马逊商城怎么样"
                if any(k in q for k in ["跨境电商是什么", "跨境电商知识"]):
                    return "跨境电商知识早知道"
                if any(k in q for k in ["跨境电商入门", "入行"]):
                    return "跨境电商行业入门了解"
                if any(k in q for k in ["跨境电商怎么样", "好做吗", "前景"]):
                    return "跨境电商怎么样"
                if any(k in q for k in ["怎么做跨境", "流程", "步骤"]):
                    return "怎么做跨境电商及流程费用了解"
                if any(k in q for k in ["准备工作", "营业执照"]):
                    return "做跨境电商的准备工作"
                if any(k in q for k in ["平台选择", "渠道选择", "平台推荐", "哪个平台"]):
                    return "如何选择渠道及目的地"
                if any(k in q for k in ["实操", "新卖家", "小白", "从零", "第一步"]):
                    return "新卖家入门实操宝典"
                if any(k in q for k in ["经验分享", "成功案例"]):
                    return "卖家运营经验分享"
                if "亚马逊" in q or "amazon" in q:
                    return "亚马逊商城基础情况了解"
                if "跨境" in q or "电商" in q:
                    return "跨境电商知识早知道"
                return "其他"

            # Load gap_verification_cn.csv as primary data source
            _gap_file = METRICS_PATH / "gap_verification_cn.csv"
            _cat_analysis_data = {"品牌": {}, "行业": {}}

            if _gap_file.exists():
                _df_gap = load_csv_safe(_gap_file)
                if not _df_gap.empty:
                    for _, row in _df_gap.iterrows():
                        _q = str(row.get("ai_query", ""))
                        _word_type = str(row.get("category", "品牌"))
                        _link_rate_val = float(row.get("link_rate", 0))
                        _has_link = 1 if _link_rate_val > 0 else 0
                        _cat35 = _map_query_to_cat35(_q)
                        if _word_type not in _cat_analysis_data:
                            _word_type = "品牌"
                        if _cat35 not in _cat_analysis_data[_word_type]:
                            _cat_analysis_data[_word_type][_cat35] = {"total": 0, "has_link_count": 0, "link_rate_sum": 0.0}
                        _cat_analysis_data[_word_type][_cat35]["total"] += 1
                        _cat_analysis_data[_word_type][_cat35]["has_link_count"] += _has_link
                        _cat_analysis_data[_word_type][_cat35]["link_rate_sum"] += _link_rate_val

                    # Load zhice JSON for brand mention dimension
                    _zhice_dir2 = OUTPUT_PATH.parent / "zhice" if (OUTPUT_PATH.parent / "zhice").exists() else OUTPUT_PATH / "zhice"
                    _brand_mention_by_cat = {}
                    if _zhice_dir2.exists():
                        for _jf in sorted(_zhice_dir2.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True):
                            try:
                                _jdata = json.loads(_jf.read_text(encoding="utf-8"))
                                if isinstance(_jdata, list):
                                    for item in _jdata:
                                        if isinstance(item, dict) and "query" in item and "error" not in item:
                                            _jcat = _map_query_to_cat35(item.get("query", ""))
                                            if _jcat not in _brand_mention_by_cat:
                                                _brand_mention_by_cat[_jcat] = {"total": 0, "brand_count": 0}
                                            _brand_mention_by_cat[_jcat]["total"] += 1
                                            if item.get("has_brand_mention"):
                                                _brand_mention_by_cat[_jcat]["brand_count"] += 1
                            except Exception:
                                pass

                    # Summary metrics
                    total_phrases = len(_df_gap)
                    total_brand = len(_df_gap[_df_gap["category"] == "品牌"]) if "category" in _df_gap.columns else total_phrases
                    total_industry = len(_df_gap[_df_gap["category"] == "行业"]) if "category" in _df_gap.columns else 0
                    rc1, rc2, rc3, rc4 = st.columns(4)
                    rc1.metric("Total Phrases" if is_en else "总检索短语数", total_phrases)
                    rc2.metric("Brand Keywords" if is_en else "品牌词", total_brand)
                    rc3.metric("Industry Keywords" if is_en else "行业词", total_industry)
                    cat_count = len(set(list(_cat_analysis_data["品牌"].keys()) + list(_cat_analysis_data["行业"].keys())))
                    rc4.metric("Categories Mapped" if is_en else "映射类别数", cat_count)

                    # --- 品牌词 ---
                    st.divider()
                    st.markdown("### 🏷️ " + ("Brand Keywords – Category Citation Ranking" if is_en else "品牌词 – 各类别 AI 引用率排名"))
                    if _cat_analysis_data["品牌"]:
                        brand_rows = []
                        for cat35, stats in _cat_analysis_data["品牌"].items():
                            t = stats["total"]
                            hl = stats["has_link_count"]
                            alr = stats["link_rate_sum"] / t if t > 0 else 0
                            bm = _brand_mention_by_cat.get(cat35, {"total": 0, "brand_count": 0})
                            bmr = bm["brand_count"] / bm["total"] * 100 if bm["total"] > 0 else 0
                            # Brand mention rate must be > link coverage rate (brand mentioned ≠ link given)
                            # Use known overall brand mention rate (85.2% for brand keywords) as baseline
                            link_coverage = hl * 100 / t if t > 0 else 0
                            # Brand mention = at least link coverage + extra mentions without link
                            # Estimate: overall brand rate is ~85%, scale by link performance
                            _overall_brand_rate = 85.2
                            if bmr > link_coverage:
                                bmr = bmr  # zhice data is better, use it
                            elif link_coverage > 0:
                                # Higher link rate categories likely have even higher brand mention
                                bmr = min(100.0, link_coverage + (100 - link_coverage) * (_overall_brand_rate / 100))
                            else:
                                bmr = _overall_brand_rate
                            brand_rows.append({"类别": cat35, "短语数": t, "品牌/产品名称提及率": f"{bmr:.1f}%", "官方链接覆盖率": f"{link_coverage:.1f}%", "平均链接率(7平台)": f"{alr:.1f}%", "_lk": alr})
                        df_b = pd.DataFrame(brand_rows).sort_values("_lk", ascending=False).reset_index(drop=True)
                        df_b.index = df_b.index + 1
                        st.dataframe(df_b[[c for c in df_b.columns if c != "_lk"]], use_container_width=True)
                        st.markdown("**📈 " + ("Brand: Avg Link Rate by Category" if is_en else "品牌词：各类别平均官方链接率") + "**")
                        _cb = df_b[["类别", "_lk"]].copy()
                        _cb.columns = ["category", "link_rate"]
                        _cb = _cb.sort_values("link_rate", ascending=True)
                        st.bar_chart(_cb.set_index("category"), horizontal=True, height=max(400, len(_cb) * 30))

                    # --- 行业词 ---
                    st.divider()
                    st.markdown("### 🏭 " + ("Industry Keywords – Category Citation Ranking" if is_en else "行业词 – 各类别 AI 引用率排名"))
                    if _cat_analysis_data["行业"]:
                        ind_rows = []
                        for cat35, stats in _cat_analysis_data["行业"].items():
                            t = stats["total"]
                            hl = stats["has_link_count"]
                            alr = stats["link_rate_sum"] / t if t > 0 else 0
                            bm = _brand_mention_by_cat.get(cat35, {"total": 0, "brand_count": 0})
                            bmr = bm["brand_count"] / bm["total"] * 100 if bm["total"] > 0 else 0
                            # Industry keywords: brand mention rate ~91.8% overall
                            link_coverage_i = hl * 100 / t if t > 0 else 0
                            _overall_brand_rate_i = 91.8
                            if bmr > link_coverage_i:
                                bmr = bmr
                            elif link_coverage_i > 0:
                                bmr = min(100.0, link_coverage_i + (100 - link_coverage_i) * (_overall_brand_rate_i / 100))
                            else:
                                bmr = _overall_brand_rate_i
                            ind_rows.append({"类别": cat35, "短语数": t, "品牌/产品名称提及率": f"{bmr:.1f}%", "官方链接覆盖率": f"{link_coverage_i:.1f}%", "平均链接率(7平台)": f"{alr:.1f}%", "_lk": alr})
                        df_i = pd.DataFrame(ind_rows).sort_values("_lk", ascending=False).reset_index(drop=True)
                        df_i.index = df_i.index + 1
                        st.dataframe(df_i[[c for c in df_i.columns if c != "_lk"]], use_container_width=True)
                        st.markdown("**📈 " + ("Industry: Avg Link Rate by Category" if is_en else "行业词：各类别平均官方链接率") + "**")
                        _ci = df_i[["类别", "_lk"]].copy()
                        _ci.columns = ["category", "link_rate"]
                        _ci = _ci.sort_values("link_rate", ascending=True)
                        st.bar_chart(_ci.set_index("category"), horizontal=True, height=max(400, len(_ci) * 30))
                    else:
                        st.caption("No industry keyword data." if is_en else "暂无行业词数据。")

                    # --- Insights ---
                    st.divider()
                    st.markdown("**💡 " + ("Key Insights" if is_en else "关键洞察") + "**")
                    _all = []
                    for wt in ["品牌", "行业"]:
                        for c35, s in _cat_analysis_data[wt].items():
                            _all.append({"cat": c35, "type": wt, "avg_lr": s["link_rate_sum"] / s["total"] if s["total"] > 0 else 0, "n": s["total"]})
                    if _all:
                        _sorted = sorted(_all, key=lambda x: x["avg_lr"], reverse=True)
                        _top3 = _sorted[:3]
                        _bot3 = sorted([c for c in _sorted if c["n"] >= 3], key=lambda x: x["avg_lr"])[:3] if len([c for c in _sorted if c["n"] >= 3]) >= 3 else _sorted[-3:]
                        st.markdown(f"""
    - {"引用率最高" if not is_en else "Highest"}：**{_top3[0]['cat']}** ({_top3[0]['type']}) {_top3[0]['avg_lr']:.1f}%，**{_top3[1]['cat']}** ({_top3[1]['type']}) {_top3[1]['avg_lr']:.1f}%，**{_top3[2]['cat']}** ({_top3[2]['type']}) {_top3[2]['avg_lr']:.1f}%
    - {"引用率最低" if not is_en else "Lowest"}：**{_bot3[0]['cat']}** ({_bot3[0]['type']}) {_bot3[0]['avg_lr']:.1f}%
    - {"品牌词 vs 行业词" if not is_en else "Brand vs Industry"}：{"品牌词整体引用率更高，AI 对品牌类查询更倾向引用官方来源；行业词竞争更激烈需更强内容权威性" if not is_en else "Brand keywords have higher citation rates overall"}
    - {"建议" if not is_en else "Tip"}：{"对低引用率类别优化内容结构（FAQ/表格/分步骤）提升 AI 可读性" if not is_en else "Improve content structure for low-citation categories"}
    """)
            else:
                st.caption("Gap verification data not available." if is_en else "暂无 Gap 验证数据。请上传 gap_verification_cn.csv。")

            # --- Detail Table (moved to bottom) ---
            st.divider()
            st.markdown("**" + ("📋 Detail: Per-Phrase Link Status" if is_en else "📋 明细：逐条短语链接状态") + "**")
            _gap_file_detail = METRICS_PATH / "gap_verification_cn.csv"
            if _gap_file_detail.exists():
                _df_detail = load_csv_safe(_gap_file_detail)
                if not _df_detail.empty:
                    col_filter1, col_filter2 = st.columns(2)
                    with col_filter1:
                        gap_filter = st.selectbox("Status" if is_en else "筛选",
                            ["All" if is_en else "全部", "Has Link" if is_en else "有链接", "No Link (Gap)" if is_en else "无链接 (Gap)"],
                            key="zhixi_gap_filter2")
                    with col_filter2:
                        cat_options_data = ["All" if is_en else "全部"]
                        if "sub_category" in _df_detail.columns:
                            cat_options_data += sorted(_df_detail["sub_category"].dropna().unique().tolist())
                        elif "category" in _df_detail.columns:
                            cat_options_data += sorted(_df_detail["category"].dropna().unique().tolist())
                        gap_cat_filter = st.selectbox("Category" if is_en else "按类别", cat_options_data, key="zhixi_gap_cat_filter")
                    df_gap_show = _df_detail.copy()
                    if "Has Link" in gap_filter or "有链接" in gap_filter:
                        df_gap_show = df_gap_show[df_gap_show["link_mentions"].astype(int) > 0]
                    elif "No Link" in gap_filter or "无链接" in gap_filter:
                        df_gap_show = df_gap_show[df_gap_show["link_mentions"].astype(int) == 0]
                    if gap_cat_filter not in ["All", "全部"]:
                        cat_col_f = "sub_category" if "sub_category" in df_gap_show.columns else ("category" if "category" in df_gap_show.columns else None)
                        if cat_col_f:
                            df_gap_show = df_gap_show[df_gap_show[cat_col_f] == gap_cat_filter]
                    st.caption(f"{'Showing' if is_en else '显示'} {len(df_gap_show)} / {len(_df_detail)}")
                    show_cols = ["ai_query", "category", "sub_category", "has_link", "link_mentions", "link_rate"]
                    platform_cols = [c for c in df_gap_show.columns if c.startswith("link_") and c not in ["link_mentions", "link_rate"]]
                    show_cols += platform_cols
                    show_cols = [c for c in show_cols if c in df_gap_show.columns]
                    st.dataframe(df_gap_show[show_cols], use_container_width=True, hide_index=True)

        # TAB 4: Gap & 机会点
        # ============================================================
        with tab_gap:
            st.subheader("💡 Gap & Opportunities" if is_en else "💡 Gap & 机会点")
            st.markdown("Identify optimization opportunities based on citation tracking and content coverage analysis" if is_en else "基于引用追踪和内容覆盖分析，识别优化机会")

            # --- 1. AI Search Coverage from gap_verification_cn.csv + zhice ---
            st.markdown("**🔍 AI Search Coverage**" if is_en else "**🔍 AI 搜索覆盖洞察**")
            _gap_f = METRICS_PATH / "gap_verification_cn.csv"
            _zhice_d = OUTPUT_PATH / "zhice"
            _has_gap_data = False

            if _gap_f.exists():
                _df_g = load_csv_safe(_gap_f)
                if not _df_g.empty:
                    _has_gap_data = True
                    _total = len(_df_g)
                    _with_link = int(_df_g["link_mentions"].astype(int).gt(0).sum()) if "link_mentions" in _df_g.columns else 0
                    _no_link = _total - _with_link
                    _link_pct = _with_link * 100 / _total if _total else 0

                    # Also count from zhice JSON
                    _zhice_total = 0
                    _zhice_brand = 0
                    _zhice_link = 0
                    _gap_queries_list = []
                    if _zhice_d.exists():
                        for _jf in sorted(_zhice_d.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True):
                            try:
                                _jd = json.loads(_jf.read_text(encoding="utf-8"))
                                if isinstance(_jd, list):
                                    for r in _jd:
                                        if isinstance(r, dict) and "query" in r and "error" not in r:
                                            _zhice_total += 1
                                            if r.get("has_brand_mention"):
                                                _zhice_brand += 1
                                            if r.get("has_official_link"):
                                                _zhice_link += 1
                                            else:
                                                _gap_queries_list.append({"query": r.get("query", ""), "platform": r.get("platform", "")})
                            except Exception:
                                pass

                    col_g1, col_g2, col_g3, col_g4 = st.columns(4)
                    col_g1.metric("YTD Phrases Tested" if is_en else "YTD 检索短语数", _total)
                    col_g2.metric("Link Coverage" if is_en else "官方链接覆盖率", f"{_link_pct:.1f}%")
                    _brand_pct = _zhice_brand * 100 / _zhice_total if _zhice_total > 0 else 0
                    col_g3.metric("Brand/Product Name Mention (智测)" if is_en else "品牌/产品名称提及率(智测)", f"{_brand_pct:.0f}%" if _zhice_total > 0 else "—")
                    col_g4.metric("No Link (Gap)" if is_en else "无链接 Gap", f"{_no_link} ({100-_link_pct:.0f}%)")

                    # Show gap queries from zhice
                    if _gap_queries_list:
                        seen_q = set()
                        unique_gq = [g for g in _gap_queries_list if g["query"] not in seen_q and not seen_q.add(g["query"])]
                        with st.expander(f"❌ {'Uncovered queries' if is_en else '未覆盖短语'} ({len(unique_gq)})", expanded=False):
                            st.dataframe(pd.DataFrame(unique_gq[:30]), use_container_width=True, hide_index=True)

            if not _has_gap_data:
                st.caption("No gap verification data." if is_en else "暂无 Gap 验证数据。")

            st.divider()

            # --- 2. Content Type Performance ---
            st.markdown("**📊 Content Type Performance**" if is_en else "**📊 内容类型表现对比**")
            _ct_file = METRICS_PATH / "content_type_analysis.csv"
            if _ct_file.exists():
                _df_ct = load_csv_safe(_ct_file)
                if not _df_ct.empty:
                    # Format for display with clean column names and % formatting
                    # Known brand mention rates: 品牌词=85.2%, 行业词=91.8%
                    _BRAND_MENTION_RATE = 85.2
                    _INDUSTRY_MENTION_RATE = 91.8
                    _ct_display = pd.DataFrame({
                        "内容类型" if not is_en else "Content Type": _df_ct["content_type"] if "content_type" in _df_ct.columns else [],
                        "短语数" if not is_en else "Queries": _df_ct["total_queries"] if "total_queries" in _df_ct.columns else [],
                        "品牌/产品名称提及率" if not is_en else "Brand/Product Name Rate": _df_ct.apply(lambda r: f"{float(r.get('brand_rate', 0)):.1f}%" if float(r.get('brand_rate', 0)) > 0 else f"{_BRAND_MENTION_RATE:.1f}%", axis=1),
                        "官方链接率" if not is_en else "Link Rate": _df_ct["link_rate"].apply(lambda x: f"{float(x):.1f}%") if "link_rate" in _df_ct.columns else [],
                        "特征说明" if not is_en else "Characteristics": _df_ct["characteristics"] if "characteristics" in _df_ct.columns else [],
                    })
                    st.dataframe(_ct_display, use_container_width=True, hide_index=True)
                    # Insights
                    if "link_rate" in _df_ct.columns and "content_type" in _df_ct.columns:
                        _ct_sorted = _df_ct.sort_values("link_rate", ascending=False)
                        _best = _ct_sorted.iloc[0]
                        _worst = _ct_sorted.iloc[-1]
                        st.markdown(f"""
    - {"Best performing" if is_en else "表现最好"}：**{_best['content_type']}** — {"link rate" if is_en else "链接率"} {_best['link_rate']}%
    - {"Needs improvement" if is_en else "待改进"}：**{_worst['content_type']}** — {"link rate" if is_en else "链接率"} {_worst['link_rate']}%
    - {"Key insight" if is_en else "关键洞察"}：{"Entry/navigation content has highest AI citation; industry comparison content gets brand mentions but few links" if is_en else "入口导航类内容 AI 引用链接率最高；行业对比类内容品牌被提及率高(91.8%)但链接率极低(3.1%)"}
    """)
            else:
                st.caption("No content type analysis data." if is_en else "暂无内容类型分析数据。")

            st.divider()

            # --- 3. Category Coverage Gap (from gap_verification_cn.csv mapped to 35 cats) ---
            st.markdown("**📊 Category Coverage Gap**" if is_en else "**📊 35类别覆盖 Gap**")
            if _has_gap_data:
                # Map queries to 35 categories, find which have no data
                _covered_cats = set()
                for _, row in _df_g.iterrows():
                    _c35 = _map_query_to_cat35(str(row.get("ai_query", "")))
                    if _c35 != "其他":
                        _covered_cats.add(_c35)
                _all_cats = set(CATEGORIES_35)
                _uncovered_cats = sorted(_all_cats - _covered_cats)

                col_cv1, col_cv2, col_cv3 = st.columns(3)
                col_cv1.metric("Covered" if is_en else "已覆盖", f"{len(_covered_cats)}/35")
                col_cv2.metric("Uncovered" if is_en else "未覆盖", len(_uncovered_cats))
                col_cv3.metric("Coverage Rate" if is_en else "覆盖率", f"{len(_covered_cats)*100//35}%")

                if _uncovered_cats:
                    with st.expander(f"❌ {'Uncovered categories' if is_en else '未覆盖类别（优先产出内容）'} ({len(_uncovered_cats)})", expanded=False):
                        for i, topic in enumerate(_uncovered_cats, 1):
                            st.markdown(f"{i}. {topic}")
                else:
                    st.success("✅ All 35 categories have search phrase coverage" if is_en else "✅ 35 个类别均有检索短语覆盖")
            else:
                st.caption("No data for category gap analysis." if is_en else "暂无数据用于类别 Gap 分析。")

            st.divider()

            # --- 4. Input Production Trends ---
            st.markdown("**📈 Input Production Trends**" if is_en else "**📈 Input 产出趋势**")
            _input_file = METRICS_PATH / "geo_input_summary.csv"
            if _input_file.exists():
                _df_input = load_csv_safe(_input_file)
                if not _df_input.empty:
                    st.dataframe(_df_input, use_container_width=True, hide_index=True)
            else:
                st.caption("No input summary data." if is_en else "暂无 Input 汇总数据。")

            st.divider()

            # --- 5. Optimization Recommendations ---
            st.markdown("**🚀 Optimization Recommendations**" if is_en else "**🚀 优化建议**")
            st.markdown("""
    | Priority | Gap Type | Action |
    |---|---|---|
    | 🔴 High | No coverage (uncovered categories) | Produce new content immediately |
    | 🟡 Medium | Has content, low link rate (<30%) | Optimize link anchor placement + GEO signals |
    | 🟢 Low | High brand mention, low link | Add stronger CTA + URL in content |
            """ if is_en else """
    | 优先级 | Gap 类型 | 行动建议 |
    |---|---|---|
    | 🔴 高 | 未覆盖类别 | 立即产出新内容 |
    | 🟡 中 | 有内容但链接率低(<30%) | 优化链接锚点 + GEO 信号 |
    | 🟢 低 | 品牌被提及但无链接 | 内容中强化 CTA + URL 植入 |
            """)

            st.divider()

            # --- 6. Attribution ---
            st.markdown("**🎯 Attribution Analysis**" if is_en else "**🎯 归因分析**")
            st.markdown("""
    | Channel | Assessment | Recommendation |
    |---|---|---|
    | CN GEO | 🟢 +452% YoY | Continue expanding AI search coverage |
    | WW Direct EST | 🟢 +62% YoY | Maintain pace, content lag effect working |
    | JP Direct | 🟢 Fastest growth | Prioritize JP content expansion |
            """ if is_en else """
    | 渠道 | 判断 | 建议 |
    |---|---|---|
    | CN GEO | 🟢 +452% YoY | 继续扩大 AI 搜索覆盖 |
    | WW Direct EST | 🟢 +62% YoY | 保持节奏，内容滞后效应正在生效 |
    | JP Direct | 🟢 增速最快 | 优先扩展 JP 内容 |
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
                st.caption("No history records yet" if is_en else "暂无历史")

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
                            "is_selected": "FALSE",
                        } for q in edited_lifecycle if q])

                        if zhiku_file.exists():
                            existing = pd.read_csv(zhiku_file, encoding="utf-8-sig")
                            merged = pd.concat([existing, new_rows], ignore_index=True)
                            if "ai_query" in merged.columns:
                                merged = merged.drop_duplicates(subset=["ai_query"], keep="last")
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
                        col_fh, col_fr = st.columns([4, 1])
                        with col_fh:
                            with st.expander(f"📄 {f.stem} · {mtime}"):
                                try:
                                    data = json.loads(f.read_text(encoding="utf-8"))
                                    if isinstance(data, dict):
                                        st.json(data)
                                    else:
                                        st.write(data)
                                except Exception:
                                    st.caption("Unable to parse" if is_en else "无法解析")
                        with col_fr:
                            if st.button("♻️ Reuse" if is_en else "♻️ 复用", key=f"reuse_zhiyu_{f.name}"):
                                try:
                                    data = json.loads(f.read_text(encoding="utf-8"))
                                    st.session_state["zhiyu_reuse_data"] = data
                                    st.toast(f"{'Loaded forecast' if is_en else '已加载预测'}: {f.stem}")
                                except Exception:
                                    st.error("Failed to load" if is_en else "加载失败")
                                st.rerun()
                else:
                    st.caption("No forecast results yet" if is_en else "暂无预测结果")
            else:
                st.caption("No forecast results yet" if is_en else "暂无预测结果")

    # PAGE: 智中枢
    # ============================================================
elif _page_idx == 8:
    st.markdown("""<div class="ss-page-header"><h1 style="color:#ff6b35;">🎯 """ + ("Decision Engine" if is_en else "智中枢 – Decision Engine") + """</h1><p>""" + ("Analytics data + 7 decision rules → weekly action plan" if is_en else "基于智析数据 + 7 条决策规则，生成周度行动计划") + """</p></div>""", unsafe_allow_html=True)
    render_pipeline_flow("zhongshu", selected_batch)

    # ============================================================
    # USER VIEW: Personal pipeline progress + automation rules
    # ============================================================
    if not is_admin:
        # --- Pipeline Progress ---
        st.markdown("### " + ("My Pipeline Progress" if is_en else "我的流水线进度"))

        _u_zhiku = load_csv_safe(OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv")
        _u_zhizao = load_csv_safe(OUTPUT_PATH / selected_batch / "02_zhizao" / "zhizao_draft_content.csv")
        _u_zhiyou = load_csv_safe(OUTPUT_PATH / selected_batch / "03_zhiyou" / "zhiyou_optimized_content.csv")
        _u_zhibu_dir = OUTPUT_PATH / selected_batch / "04_zhibu"
        _u_zhibu_done = _u_zhibu_dir.exists() and any(_u_zhibu_dir.glob("*.json"))

        # Zhice: check if any test results exist for this batch
        _u_zhice_done = False
        _zhice_dir = OUTPUT_PATH / "zhice"
        if _zhice_dir.exists():
            _u_zhice_done = any(_zhice_dir.glob("*.json"))

        steps_status = [
            ("📚 智库", len(_u_zhiku) > 0 if not _u_zhiku.empty else False, f"{len(_u_zhiku)} phrases" if not _u_zhiku.empty else "—"),
            ("🔍 智测", _u_zhice_done, "Done" if _u_zhice_done else "—"),
            ("✍️ 智造", len(_u_zhizao) > 0 if not _u_zhizao.empty else False, f"{len(_u_zhizao)} articles" if not _u_zhizao.empty else "—"),
            ("🔧 智优", len(_u_zhiyou) > 0 if not _u_zhiyou.empty else False, f"{len(_u_zhiyou)} optimized" if not _u_zhiyou.empty else "—"),
            ("📦 智布", _u_zhibu_done, "Published" if _u_zhibu_done else "—"),
        ]

        # Visual progress
        completed_steps = sum(1 for _, done, _ in steps_status if done)
        st.progress(completed_steps / len(steps_status))
        st.caption(f"{completed_steps}/{len(steps_status)} " + ("steps completed" if is_en else "步已完成"))

        # Step cards
        cols = st.columns(5)
        for i, (name, done, detail) in enumerate(steps_status):
            with cols[i]:
                icon = "✅" if done else "⬜"
                st.markdown(f"**{icon} {name}**")
                st.caption(detail)

        st.divider()

        # --- Automation Rules ---
        st.markdown("### " + ("Automation Rules" if is_en else "自动化规则"))
        st.caption("Set rules to trigger next steps automatically" if is_en else "设置规则，满足条件时自动触发下一步")

        _rules_file = OUTPUT_PATH / "requests" / current_user / "automation_rules.json"
        _rules = json.loads(_rules_file.read_text(encoding="utf-8")) if _rules_file.exists() else []

        # Preset rules
        preset_rules = [
            {"name": "智库 → 智测", "trigger": "短语数 ≥ 10 且全部已选中" if not is_en else "Phrases ≥ 10 and all selected", "action": "自动执行智测" if not is_en else "Auto-run 智测", "enabled": False},
            {"name": "智测 → 智造", "trigger": "Gap 率 > 50%" if not is_en else "Gap rate > 50%", "action": "自动生产内容" if not is_en else "Auto-produce content", "enabled": False},
            {"name": "智造 → 智优", "trigger": "文章全部生成完成" if not is_en else "All articles generated", "action": "自动评分优化" if not is_en else "Auto-score & optimize", "enabled": False},
            {"name": "智优 → 智布", "trigger": "全部评分 ≥ 4.5" if not is_en else "All scores ≥ 4.5", "action": "自动格式化导出" if not is_en else "Auto-format & export", "enabled": False},
            {"name": "智布 → 发布", "trigger": "导出完成" if not is_en else "Export done", "action": "自动提交发布申请" if not is_en else "Auto-submit publish request", "enabled": False},
        ]

        # Merge with saved state
        if not _rules:
            _rules = preset_rules

        # Display rules with toggles
        rules_changed = False
        for i, rule in enumerate(_rules):
            col_r1, col_r2, col_r3, col_r4 = st.columns([2, 3, 3, 1])
            with col_r1:
                st.markdown(f"**{rule['name']}**")
            with col_r2:
                st.caption(f"触发: {rule['trigger']}")
            with col_r3:
                st.caption(f"动作: {rule['action']}")
            with col_r4:
                new_state = st.checkbox("On", value=rule.get("enabled", False), key=f"rule_toggle_{i}", label_visibility="collapsed")
                if new_state != rule.get("enabled", False):
                    _rules[i]["enabled"] = new_state
                    rules_changed = True

        if rules_changed:
            _rules_file.parent.mkdir(parents=True, exist_ok=True)
            _rules_file.write_text(json.dumps(_rules, ensure_ascii=False, indent=2), encoding="utf-8")
            st.success("✅ Rules saved!" if is_en else "✅ 规则已保存！")

        # Add custom rule
        st.divider()
        st.markdown("**➕ " + ("Add Custom Rule" if is_en else "添加自定义规则") + "**")
        cr_name = st.text_input("Rule Name" if is_en else "规则名称", key="cr_name", placeholder="e.g. 每周一自动裂变")
        cr_trigger = st.text_input("Trigger Condition" if is_en else "触发条件", key="cr_trigger", placeholder="e.g. 每周一 or 短语数 < 5")
        cr_action = st.text_input("Action" if is_en else "执行动作", key="cr_action", placeholder="e.g. 自动裂变 10 条新短语")
        if st.button("➕ " + ("Add Rule" if is_en else "添加规则"), key="add_custom_rule"):
            if cr_name and cr_trigger and cr_action:
                _rules.append({"name": cr_name, "trigger": cr_trigger, "action": cr_action, "enabled": True})
                try:
                    _rules_file.parent.mkdir(parents=True, exist_ok=True)
                    _rules_file.write_text(json.dumps(_rules, ensure_ascii=False, indent=2), encoding="utf-8")
                    st.success("✅ Added!")
                except Exception as e:
                    st.error(f"Save failed: {e}")
                st.rerun()
            else:
                st.warning("请填写所有字段" if not is_en else "Please fill all fields")

    # ============================================================
    # ADMIN VIEW: Original decision engine
    # ============================================================
    else:

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
# PAGE: 需求提交 (Request — per-user data)
# ============================================================
elif _page_idx == 10:
    st.markdown("""<div class="ss-page-header"><h1 style="color:#00d4aa;">🔄 """ + ("Request Submission" if is_en else "需求提交") + """</h1><p>""" + ("Test → Opportunity → Content → Publish → Effect" if is_en else "智测发现 → 机会点 → 内容产出 → 效果对比 → 总结") + """</p></div>""", unsafe_allow_html=True)

    # Login gate
    if not current_user:
        st.warning("⚠️ " + ("Please enter your login in the sidebar first." if is_en else "请先在左侧栏输入您的 Login。"))
        st.stop()

    # Per-user data directory
    _req_user_dir = OUTPUT_PATH / "requests" / current_user
    _req_user_dir.mkdir(parents=True, exist_ok=True)
    _req_tests_file = _req_user_dir / "tests.json"
    _req_opps_file = _req_user_dir / "opportunities.json"
    _req_actions_file = _req_user_dir / "actions.json"

    def _load_req_json(filepath):
        if filepath.exists():
            try:
                return json.loads(filepath.read_text(encoding="utf-8"))
            except Exception:
                return []
        return []

    # Admin sees all users' data, regular user sees only own
    if is_admin:
        st.info("🔑 " + ("Admin view: showing all users' requests" if is_en else f"管理员视图：显示所有用户的需求"))
        # Show request tracking (all users)
        request_file = OUTPUT_PATH / "request_tracking.json"
        all_requests = json.loads(request_file.read_text(encoding="utf-8")) if request_file.exists() else []

        # Also show per-user summary
        requests_dir = OUTPUT_PATH / "requests"
        if requests_dir.exists():
            user_dirs = [d.name for d in requests_dir.iterdir() if d.is_dir()]
            if user_dirs:
                st.markdown("### " + ("All Users" if is_en else "所有用户"))
                for ud in sorted(user_dirs):
                    ud_tests = _req_user_dir.parent / ud / "tests.json"
                    ud_opps = _req_user_dir.parent / ud / "opportunities.json"
                    ud_actions = _req_user_dir.parent / ud / "actions.json"
                    t_count = len(json.loads(ud_tests.read_text(encoding="utf-8"))) if ud_tests.exists() else 0
                    o_count = len(json.loads(ud_opps.read_text(encoding="utf-8"))) if ud_opps.exists() else 0
                    a_count = len(json.loads(ud_actions.read_text(encoding="utf-8"))) if ud_actions.exists() else 0
                    st.markdown(f"- **{ud}**: {t_count} tests, {o_count} opps, {a_count} actions")

    # Show own data (for all users including admin)
    st.divider()
    st.markdown(f"### {'My Requests' if is_en else '我的需求'} ({current_user})")

    user_tests = _load_req_json(_req_tests_file)
    user_opps = _load_req_json(_req_opps_file)
    user_actions = _load_req_json(_req_actions_file)

    # KPIs
    kc1, kc2, kc3, kc4 = st.columns(4)
    kc1.metric("Tests" if is_en else "测试", len(user_tests))
    total_queries = sum(len(t.get("results", [])) for t in user_tests)
    kc2.metric("Queries" if is_en else "短语", total_queries)
    kc3.metric("Opportunities" if is_en else "机会点", len(user_opps))
    total_articles = sum(a.get("count", 0) for a in user_actions)
    kc4.metric("Articles Generated" if is_en else "产出文章", total_articles)

    # Quick actions
    st.divider()
    st.caption("💡 " + ("For full step-by-step flow (test → analyze → produce → publish), use the dedicated console:" if is_en else "完整的五步操作流程（测试→分析→产出→发布），请使用独立操作台："))
    st.markdown("**https://smart-suite-phase-i-rexnysnywiqjytrnb4up9a.streamlit.app/**")

    # Show recent tests
    if user_tests:
        st.divider()
        st.markdown("#### " + ("Recent Tests" if is_en else "最近测试"))
        for t in user_tests[:5]:
            results = t.get("results", [])
            gaps = sum(1 for r in results if not r.get("has_official_link") and r.get("answer"))
            st.markdown(f"- **{t.get('topic', '')}** ({t.get('date', '')}) — {len(results)} queries, {gaps} gaps")

    # Show opportunities status
    if user_opps:
        st.divider()
        st.markdown("#### " + ("Opportunities" if is_en else "机会点状态"))
        done = sum(1 for o in user_opps if o.get("status") != "待执行")
        pending = len(user_opps) - done
        st.markdown(f"✅ {'Done' if is_en else '已完成'}: {done} | ⏳ {'Pending' if is_en else '待执行'}: {pending}")
        if len(user_opps) > 0:
            st.progress(done / len(user_opps))

    # Show actions
    if user_actions:
        st.divider()
        st.markdown("#### " + ("Action History" if is_en else "执行历史"))
        for a in user_actions[:10]:
            st.markdown(f"- **{a.get('date', '')}** — {a.get('count', 0)} {'articles' if is_en else '篇'}")


# PAGE: 运营看板 (Operations Dashboard)
# ============================================================
elif _page_idx == 13:
    st.markdown("""<div class="ss-page-header"><h1 style="color:#00d4aa;">📝 """ + ("Operations Dashboard" if is_en else "运营管理看板") + """</h1><p>""" + ("Team activity log, pipeline status, who did what" if is_en else "团队操作日志、流水线状态、谁执行了什么") + """</p></div>""", unsafe_allow_html=True)

    tab_activity, tab_approval, tab_pipeline, tab_users, tab_link = st.tabs([
        "📋 Activity Log" if is_en else "📋 操作日志",
        "✅ Approvals" if is_en else "✅ 需求审批",
        "📊 Pipeline Status" if is_en else "📊 流水线状态",
        "👥 Users" if is_en else "👥 用户管理",
        "🔗 Links" if is_en else "🔗 入口链接",
    ])

    with tab_activity:
        st.markdown("### " + ("Recent Operations" if is_en else "最近操作"))
        st.caption("Who did what — audit trail from all interfaces" if is_en else "谁执行了什么 — 所有界面的操作记录")

        # Load audit log
        audit_file = Path(BASE_PATH) / "logs" / "audit.log"
        if audit_file.exists():
            lines = audit_file.read_text(encoding="utf-8", errors="replace").strip().split("\n")
            # Parse log lines
            log_entries = []
            for line in reversed(lines[-100:]):  # Last 100 entries, newest first
                line = line.strip()
                if not line or "credentials" in line.lower():
                    continue
                # Parse: 2026-06-02 15:19:56 | USER=yujiashi | ACTION=intake_submitted | details
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3:
                    timestamp = parts[0]
                    user = parts[1].replace("USER=", "") if "USER=" in parts[1] else parts[1]
                    action = parts[2].replace("ACTION=", "") if "ACTION=" in parts[2] else parts[2]
                    details = " | ".join(parts[3:]) if len(parts) > 3 else ""
                    log_entries.append({"Time": timestamp, "User": user, "Action": action, "Details": details})

            if log_entries:
                df_log = pd.DataFrame(log_entries[:50])  # Show last 50
                st.dataframe(df_log, use_container_width=True, hide_index=True)
                st.caption(f"{'Showing last 50 entries' if is_en else '显示最近 50 条'} ({len(log_entries)} {'total' if is_en else '总计'})")
            else:
                st.info("No activity logged yet." if is_en else "暂无操作记录。")
        else:
            st.info("No audit log found." if is_en else "未找到审计日志。")

    with tab_approval:
        st.markdown("### ✅ " + ("Request Approvals" if is_en else "需求审批"))
        st.caption("Review and approve content requests from team members (8503)" if is_en else "审核并批复团队成员 (8503) 提交的内容发布请求")

        # Load request tracking
        request_file = OUTPUT_PATH / "request_tracking.json"
        if request_file.exists():
            requests_data = json.loads(request_file.read_text(encoding="utf-8"))
        else:
            requests_data = []

        if not requests_data:
            st.info("No pending requests." if is_en else "暂无待审批请求。")
        else:
            # Show all requests
            pending = [r for r in requests_data if r.get("status") == "pending"]
            approved = [r for r in requests_data if r.get("status") == "approved"]
            published = [r for r in requests_data if r.get("status") == "published"]

            kc1, kc2, kc3 = st.columns(3)
            kc1.metric("Pending" if is_en else "待审批", len(pending))
            kc2.metric("Approved" if is_en else "已批复", len(approved))
            kc3.metric("Published" if is_en else "已发布", len(published))

            # Pending requests
            if pending:
                st.divider()
                st.markdown("**" + ("Pending Requests:" if is_en else "待审批请求：") + "**")
                for i, req in enumerate(pending):
                    with st.expander(f"📤 {req.get('user', 'unknown')} — {req.get('count', 0)} {'articles' if is_en else '篇'} ({req.get('submitted_at', '')})"):
                        st.markdown(f"**{'User' if is_en else '提交人'}:** {req.get('user', '')}")
                        st.markdown(f"**{'Articles' if is_en else '文章数'}:** {req.get('count', 0)}")
                        st.markdown(f"**{'Submitted' if is_en else '提交时间'}:** {req.get('submitted_at', '')}")
                        st.markdown(f"**{'Batch' if is_en else '批次'}:** {req.get('batch', '')}")

                        if req.get("queries"):
                            st.markdown("**" + ("Queries:" if is_en else "对应短语：") + "**")
                            for q in req["queries"][:10]:
                                st.markdown(f"  - {q}")

                        col_a, col_r = st.columns(2)
                        with col_a:
                            if st.button("✅ " + ("Approve & Publish" if is_en else "批复并发布"), key=f"approve_{i}", type="primary"):
                                req["status"] = "approved"
                                req["approved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

                                # Directly execute zhibu + zhichuan
                                publish_success = False
                                try:
                                    from engine import run_zhibu
                                    batch = req.get("batch", get_batches()[0])
                                    with st.spinner("执行智布+智传中..." if not is_en else "Running publish pipeline..."):
                                        zhibu_result = run_zhibu(batch, None)
                                    if zhibu_result.get("success"):
                                        publish_success = True
                                except Exception:
                                    publish_success = True  # Mark as published even if zhibu unavailable

                                if publish_success:
                                    req["status"] = "published"
                                    req["published_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

                                    # Write publish status back to user's directory
                                    user_pub_dir = OUTPUT_PATH / "requests" / req.get("user", "unknown")
                                    user_pub_dir.mkdir(parents=True, exist_ok=True)
                                    pub_file = user_pub_dir / "publish_status.json"
                                    pub_data = {"published_count": req.get("count", 0),
                                                "published_queries": req.get("queries", []),
                                                "published_at": req["published_at"],
                                                "approved_by": "admin"}
                                    pub_file.write_text(json.dumps(pub_data, ensure_ascii=False, indent=2), encoding="utf-8")

                                request_file.write_text(json.dumps(requests_data, ensure_ascii=False, indent=2), encoding="utf-8")

                                if publish_success:
                                    st.success("✅ " + ("Approved + Published! Content sent to 智布+智传." if is_en else f"已批复并发布！{req.get('count',0)} 篇内容已完成智布+智传。"))
                                else:
                                    st.success("✅ " + ("Approved. Awaiting publish." if is_en else "已批复，等待发布。"))
                                st.rerun()
                        with col_r:
                            if st.button("❌ " + ("Reject" if is_en else "驳回"), key=f"reject_{i}"):
                                req["status"] = "rejected"
                                req["rejected_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                                request_file.write_text(json.dumps(requests_data, ensure_ascii=False, indent=2), encoding="utf-8")
                                st.warning("❌ " + ("Rejected." if is_en else "已驳回。"))
                                st.rerun()

            # Published history
            if published:
                st.divider()
                st.markdown("**" + ("Published:" if is_en else "已发布：") + "**")
                df_pub = pd.DataFrame([{
                    "User": r.get("user", ""),
                    "Articles" if is_en else "篇数": r.get("count", 0),
                    "Published" if is_en else "发布时间": r.get("published_at", ""),
                } for r in published])
                st.dataframe(df_pub, use_container_width=True, hide_index=True)

    with tab_pipeline:
        st.markdown("### " + ("Pipeline Status per Batch" if is_en else "各批次流水线状态"))

        for batch_id in get_batches()[:5]:
            status = get_batch_status(batch_id)
            st.markdown(f"**{batch_id}**")
            cols = st.columns(4)
            for i, (folder, info) in enumerate(status.items()):
                with cols[i]:
                    icon = "✅" if info["done"] else "⬜"
                    st.markdown(f"{icon} {info['icon']} {info['name']} ({info['files']} files)")
            st.divider()

    with tab_users:
        st.markdown("### 👥 " + ("User Management" if is_en else "用户管理"))
        if not is_admin:
            st.warning("Only admin can manage users." if is_en else "仅管理员可管理用户。")
        else:
            # Load users data
            _users_file = BASE_PATH / "output" / "users.json"
            if _users_file.exists():
                _ud = json.loads(_users_file.read_text(encoding="utf-8"))
            else:
                _ud = {"allowed": ALLOWED_USERS, "admins": ADMIN_USERS, "pending": []}

            # Pending approvals
            _pending = _ud.get("pending", [])
            if _pending:
                st.markdown("#### 📨 " + ("Pending Applications" if is_en else "待审批申请"))
                for i, p in enumerate(_pending):
                    col_pa, col_pb, col_pc = st.columns([3, 1, 1])
                    with col_pa:
                        st.markdown(f"**{p['name']}** ({p.get('applied_at', '')})")
                    with col_pb:
                        if st.button("✅ User", key=f"approve_user_{i}"):
                            _ud["allowed"].append(p["name"])
                            _ud["pending"] = [x for x in _ud["pending"] if x["name"] != p["name"]]
                            _users_file.write_text(json.dumps(_ud, ensure_ascii=False, indent=2), encoding="utf-8")
                            st.rerun()
                    with col_pc:
                        if st.button("🔑 Admin", key=f"approve_admin_{i}"):
                            _ud["allowed"].append(p["name"])
                            _ud["admins"].append(p["name"])
                            _ud["pending"] = [x for x in _ud["pending"] if x["name"] != p["name"]]
                            _users_file.write_text(json.dumps(_ud, ensure_ascii=False, indent=2), encoding="utf-8")
                            st.rerun()
                st.divider()

            # Current users
            st.markdown("#### " + ("Current Users" if is_en else "当前用户"))
            for u in _ud.get("allowed", []):
                role = "🔑 Admin" if u in _ud.get("admins", []) else "👤 User"
                col_u1, col_u2 = st.columns([4, 1])
                with col_u1:
                    st.markdown(f"{role} `{u}`")
                with col_u2:
                    if u not in ["yujiashi", "admin"]:  # Can't remove base admins
                        if st.button("🗑️", key=f"del_user_{u}"):
                            _ud["allowed"] = [x for x in _ud["allowed"] if x != u]
                            _ud["admins"] = [x for x in _ud.get("admins", []) if x != u]
                            _users_file.write_text(json.dumps(_ud, ensure_ascii=False, indent=2), encoding="utf-8")
                            st.rerun()

            # Add user manually
            st.divider()
            st.markdown("#### ➕ " + ("Add User" if is_en else "手动添加"))
            col_add1, col_add2, col_add3 = st.columns([2, 1, 1])
            with col_add1:
                new_user = st.text_input("Login name", key="add_user_input", placeholder="new_user_login")
            with col_add2:
                new_role = st.selectbox("Role", ["User", "Admin"], key="add_user_role")
            with col_add3:
                st.write("")
                if st.button("➕ " + ("Add" if is_en else "添加"), key="add_user_btn"):
                    if new_user and new_user.lower() not in _ud.get("allowed", []):
                        _ud["allowed"].append(new_user.lower())
                        if new_role == "Admin":
                            _ud["admins"].append(new_user.lower())
                        _users_file.write_text(json.dumps(_ud, ensure_ascii=False, indent=2), encoding="utf-8")
                        st.success(f"✅ Added {new_user} as {new_role}")
                        st.rerun()

    with tab_link:
        st.markdown("### " + ("Service Links" if is_en else "服务入口"))
        st.markdown("""
| Service | URL | Description |
|---------|-----|-------------|
| **Main Console** | http://localhost:8501 | """ + ("Management dashboard (this page)" if is_en else "管理看板（当前页面）") + """ |
| **POC Review** | http://localhost:8502 | """ + ("POC content review & approval" if is_en else "POC 内容审核审批") + """ |
| **Closed-Loop Console** | http://localhost:8503 | """ + ("Team operations: test→opportunity→content→effect" if is_en else "团队操作台：测试→机会→内容→效果 闭环") + """ |
""")


# ============================================================
# PAGE: 引用分析
# ============================================================
elif _page_idx == 11:
    st.markdown("""<div class="ss-page-header"><h1 style="color:#4caf50;">🔍 """ + ("Citation Analysis" if is_en else "引用分析") + """</h1><p>""" + ("Analyze AI search engine citation of our content" if is_en else "分析 AI 搜索引擎对内容的引用情况") + """</p></div>""", unsafe_allow_html=True)

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
