"""
Smart Suite 智系列 - 多工具独立界面版
Run: streamlit run app_suite.py
每个工具一个独立界面，可单独执行命令
"""
import streamlit as st
from pathlib import Path
import tempfile

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

# Store paths in session state for pages to access
st.session_state["BASE_PATH"] = BASE_PATH
st.session_state["OUTPUT_PATH"] = OUTPUT_PATH
st.session_state["INPUT_PATH"] = INPUT_PATH
st.session_state["METRICS_PATH"] = METRICS_PATH

st.set_page_config(
    page_title="Smart Suite 智系列",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
.main .block-container { padding-top: 1rem; }
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1a2940 0%, #0d1b2a 100%);
    border: 1px solid #2a4a6f; border-radius: 10px; padding: 12px 16px;
}
.tool-card {
    background: linear-gradient(135deg, #1a2940 0%, #0d1b2a 100%);
    border: 1px solid #2a4a6f; border-radius: 12px; padding: 20px;
    text-align: center; transition: all 0.2s;
}
.tool-card:hover { border-color: #4a9eff; transform: translateY(-2px); }
.tool-card h3 { margin: 8px 0 4px 0; }
.tool-card p { color: #94a3b8; font-size: 13px; margin: 0; }
</style>
""", unsafe_allow_html=True)

# --- Pages ---
pages = {
    "总览": [
        st.Page("pages/home.py", title="总览", icon="🏠"),
    ],
    "内容流水线": [
        st.Page("pages/zhiku.py", title="智库", icon="📚"),
        st.Page("pages/zhizao.py", title="智造", icon="✍️"),
        st.Page("pages/zhiyou.py", title="智优", icon="🔧"),
        st.Page("pages/zhibu.py", title="智布", icon="📦"),
        st.Page("pages/zhichuan.py", title="智传", icon="📡"),
    ],
    "分析与决策": [
        st.Page("pages/zhixi.py", title="智析", icon="📈"),
        st.Page("pages/zhongshu.py", title="智中枢", icon="🎯"),
    ],
}

pg = st.navigation(pages)

# --- Sidebar ---
with st.sidebar:
    st.title("🧠 Smart Suite")
    st.caption("智系列 · GEO Content Pipeline")
    st.divider()

    # Batch selection
    batches = sorted([d.name for d in OUTPUT_PATH.iterdir() if d.is_dir() and d.name.startswith("batch_")], reverse=True)
    if not batches:
        batches = ["batch_001"]
    st.session_state["selected_batch"] = st.selectbox("📂 当前批次", batches)
    st.session_state["market"] = st.selectbox("🌍 Market", ["ALL", "CN", "NA", "EU", "JP"])

    st.divider()
    st.caption(f"📁 {BASE_PATH}")

pg.run()
