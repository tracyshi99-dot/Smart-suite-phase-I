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
    page_title="Smart Suite Console",
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
            border_color = "#4a5568"
            bg = "#1a1f2e"
            text_color = "#a0aec0"
            icon_html = '<div style="font-size:14px;margin-bottom:2px;color:#718096;">○</div>'

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
    # Language toggle
    ui_lang = st.selectbox("🌐", ["中文", "English"], key="ui_lang", label_visibility="collapsed")
    is_en = (ui_lang == "English")

    st.title("🧠 Smart Suite")
    st.caption("GEO Content Pipeline · Phase I" if is_en else "智系列 · GEO Content Pipeline · Phase I")
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
    selected_batch = st.selectbox("📂 Current Batch" if is_en else "📂 当前批次", batches, key="batch")
    market = st.selectbox("🌍 Market", ["ALL", "CN", "NA", "EU", "JP"])
    kw_limit = st.number_input("🔑 Keyword Limit", 1, 50, 10)
    week = st.text_input("📅 Week", "WK21")

    st.divider()
    st.caption(f"{'Path' if is_en else '路径'}: {BASE_PATH}")


# ============================================================
# PAGE: 总览
# ============================================================
if page == "🏠 总览":
    st.title("🏠 Smart Suite Overview" if is_en else "🏠 Smart Suite 总览")

    # --- 工具介绍 ---
    st.subheader("🧠 What is Smart Suite?" if is_en else "🧠 Smart Suite 是什么？")
    st.markdown("""
    Smart Suite is an **AI-driven GEO (Generative Engine Optimization) content pipeline tool**
    that helps the Amazon Global Selling team efficiently produce, optimize, and distribute content
    that can be cited by AI search engines (ChatGPT, Perplexity, DeepSeek, etc.).
    """ if is_en else """
    Smart Suite 是一套 **AI 驱动的 GEO (Generative Engine Optimization) 内容流水线工具**，
    帮助亚马逊全球开店团队高效生产、优化和分发能够被 AI 搜索引擎（ChatGPT、Perplexity、DeepSeek 等）引用的内容。
    """)

    # ═══════════════════════════════════════════════════════════
    # ═══════════════════════════════════════════════════════════
    # WORKFLOW: Swimlane style - Pipeline + Feedback in one view
    # ═══════════════════════════════════════════════════════════
    st.divider()
    st.subheader("📋 How Smart Suite Works" if is_en else "📋 Smart Suite 工作原理")

    import streamlit.components.v1 as components
    swimlane_html = '''
    <div style="font-family:-apple-system,sans-serif;padding:24px;background:#0f1419;border-radius:12px;border:1px solid #2d3748;position:relative;cursor:pointer;" onclick="this.requestFullscreen?this.requestFullscreen():this.webkitRequestFullscreen&&this.webkitRequestFullscreen()">

      <!-- Click hint -->
      <div style="position:absolute;top:8px;right:12px;color:#64748b;font-size:10px;">🔍 点击放大</div>

      <!-- LANE 1: Forward Pipeline -->
      <div style="margin-bottom:10px;padding:5px 14px;background:#111820;border-radius:6px;">
        <span style="color:#4a9eff;font-size:13px;font-weight:600;">▶ 正向流水线 (Content Pipeline)</span>
      </div>

      <div style="display:flex;align-items:center;justify-content:center;gap:4px;padding:12px 0 18px 0;flex-wrap:nowrap;">
        <div style="text-align:center;min-width:90px;">
          <div style="background:#1e3a5f;border:2px solid #4a9eff;border-radius:8px;padding:10px 6px;">
            <div style="font-size:18px;">📚</div>
            <div style="color:#fff;font-weight:700;font-size:14px;">智库</div>
          </div>
        </div>
        <div style="color:#4a9eff;font-size:15px;">→</div>
        <div style="text-align:center;min-width:90px;">
          <div style="background:#1e3a5f;border:2px solid #4a9eff;border-radius:8px;padding:10px 6px;">
            <div style="font-size:18px;">✍️</div>
            <div style="color:#fff;font-weight:700;font-size:14px;">智造</div>
          </div>
        </div>
        <div style="color:#4a9eff;font-size:15px;">→</div>
        <div style="text-align:center;min-width:90px;">
          <div style="background:#1a3328;border:2px solid #22c55e;border-radius:8px;padding:10px 6px;">
            <div style="font-size:18px;">🔧</div>
            <div style="color:#fff;font-weight:700;font-size:14px;">智优</div>
          </div>
        </div>
        <div style="color:#4a9eff;font-size:15px;">→</div>
        <div style="text-align:center;min-width:90px;">
          <div style="background:#1a2332;border:2px solid #4a5568;border-radius:8px;padding:10px 6px;">
            <div style="font-size:18px;">📦</div>
            <div style="color:#ccc;font-weight:700;font-size:14px;">智布</div>
          </div>
        </div>
        <div style="color:#4a5568;font-size:15px;">→</div>
        <div style="text-align:center;min-width:90px;">
          <div style="background:#1a2332;border:2px solid #4a5568;border-radius:8px;padding:10px 6px;">
            <div style="font-size:18px;">📡</div>
            <div style="color:#ccc;font-weight:700;font-size:14px;">智传</div>
          </div>
        </div>
        <div style="color:#4a5568;font-size:15px;">→</div>
        <div style="text-align:center;min-width:90px;">
          <div style="background:#2d2305;border:2px solid #f59e0b;border-radius:8px;padding:10px 6px;">
            <div style="font-size:18px;">📈</div>
            <div style="color:#fff;font-weight:700;font-size:14px;">智析</div>
          </div>
        </div>
        <div style="color:#f59e0b;font-size:15px;">→</div>
        <div style="text-align:center;min-width:90px;">
          <div style="background:#2d2305;border:2px solid #f59e0b;border-radius:8px;padding:10px 6px;">
            <div style="font-size:18px;">🎯</div>
            <div style="color:#fff;font-weight:700;font-size:14px;">智中枢</div>
          </div>
        </div>
      </div>

      <!-- DIVIDER -->
      <div style="border-top:1px dashed #f59e0b;margin:6px 0 14px 0;"></div>

      <!-- LANE 2: Feedback Loop -->
      <div style="margin-bottom:10px;padding:5px 14px;background:#1a1500;border-radius:6px;">
        <span style="color:#f59e0b;font-size:13px;font-weight:600;">↩ 进化反馈 (Evolution Feedback)</span>
      </div>

      <div style="display:flex;align-items:flex-start;justify-content:center;gap:12px;padding:10px 0;flex-wrap:wrap;">

        <!-- Source: 智析 -->
        <div style="text-align:center;min-width:160px;">
          <div style="background:#2d2305;border:2px solid #f59e0b;border-radius:8px;padding:12px 10px;">
            <div style="color:#f59e0b;font-weight:700;font-size:14px;">📈 智析</div>
            <div style="color:#fcd34d;font-size:11px;margin-top:6px;line-height:1.5;">
              ① 智测验证结果<br>
              ② SEO/SEM 关键词表现<br>
              ③ GEO 短语转化数据<br>
              ④ AI 引用模式分析
            </div>
          </div>
        </div>

        <div style="color:#f59e0b;font-size:18px;padding-top:30px;">→</div>

        <!-- 智中枢 Decision -->
        <div style="text-align:center;min-width:140px;">
          <div style="background:#2d2305;border:2px solid #f59e0b;border-radius:8px;padding:12px 10px;">
            <div style="color:#f59e0b;font-weight:700;font-size:14px;">🎯 智中枢</div>
            <div style="color:#fcd34d;font-size:11px;margin-top:6px;line-height:1.5;">
              基于数据决策<br>
              调度所有工具
            </div>
          </div>
        </div>

        <div style="color:#f59e0b;font-size:18px;padding-top:30px;">→</div>

        <!-- Targets: ALL tools -->
        <div style="display:flex;flex-direction:column;gap:5px;">
          <div style="background:#1e3a5f;border:1px solid #4a9eff;border-radius:6px;padding:5px 12px;display:flex;align-items:center;gap:8px;">
            <span style="font-size:14px;">📚</span>
            <span style="color:#90cdf4;font-size:12px;">智库：扩展短语 / 填补Gap</span>
          </div>
          <div style="background:#1e3a5f;border:1px solid #4a9eff;border-radius:6px;padding:5px 12px;display:flex;align-items:center;gap:8px;">
            <span style="font-size:14px;">✍️</span>
            <span style="color:#90cdf4;font-size:12px;">智造：按引用模式生成内容</span>
          </div>
          <div style="background:#1a3328;border:1px solid #22c55e;border-radius:6px;padding:5px 12px;display:flex;align-items:center;gap:8px;">
            <span style="font-size:14px;">🔧</span>
            <span style="color:#86efac;font-size:12px;">智优：校准评分 + 重写优化</span>
          </div>
          <div style="background:#1a2332;border:1px solid #4a5568;border-radius:6px;padding:5px 12px;display:flex;align-items:center;gap:8px;">
            <span style="font-size:14px;">📦</span>
            <span style="color:#a0aec0;font-size:12px;">智布：调整输出格式策略</span>
          </div>
          <div style="background:#1a2332;border:1px solid #4a5568;border-radius:6px;padding:5px 12px;display:flex;align-items:center;gap:8px;">
            <span style="font-size:14px;">📡</span>
            <span style="color:#a0aec0;font-size:12px;">智传：优化分发渠道选择</span>
          </div>
        </div>

      </div>

      <!-- Bottom insight -->
      <div style="text-align:center;margin-top:14px;padding:10px;background:#111820;border-radius:6px;">
        <span style="color:#22c55e;font-size:13px;font-weight:600;">✨ 每轮循环：智析整合全部数据 → 智中枢决策调度 → 各工具迭代执行 → 引用率持续提升</span>
      </div>

    </div>
    '''
    components.html(swimlane_html, height=520)

    </div>
    '''
    components.html(swimlane_html, height=380)

    st.markdown("""
    **🎯 The key insight:** We don't guess what AI wants — we observe what it already cites, extract the pattern, and replicate it in our production pipeline. Every cycle makes the output more citable.
    """ if is_en else """
    **🎯 核心逻辑：** 不靠猜测 AI 喜欢什么 — 观察它实际引用了什么 → 提取模式 → 注入到生产流程。每轮循环让产出更容易被引用。
    """)

    st.divider()


    tool_info = [
        ("📚 智库", "Search Phrase Generation & Management" if is_en else "检索短语生成与管理", "Generate AI-native search phrases from SEO/SEM keywords or seed words, with auto-classification, dedup, and scoring" if is_en else "从 SEO/SEM 关键词或核心词根裂变生成 AI 原生检索短语，自动分类、去重、评分"),
        ("✍️ 智造", "Content Generation" if is_en else "内容生成", "AI auto-generates SEO+GEO dual-optimized long articles based on selected search phrases" if is_en else "基于选中的检索短语，AI 自动生成 SEO+GEO 双优化的长文章"),
        ("🔧 智优", "Content Optimization" if is_en else "内容优化", "One-click: AI scoring (5 dimensions) → rewrite optimization → compliance review" if is_en else "一键完成：AI 评分（5维度）→ 重写优化 → 合规审查"),
        ("📦 智布", "Format & Publish" if is_en else "格式化发布", "Convert optimized content to JSON structured data and Word documents for CMS publishing" if is_en else "将优化后的内容转换为 JSON 结构化数据和 Word 文档，用于 CMS 发布"),
        ("📡 智传", "Content Distribution" if is_en else "内容分发", "Distribute content to various channels (website, third-party platforms, etc.) and track publishing status" if is_en else "将内容分发到各个渠道（官网、第三方平台等），追踪发布状态"),
        ("📈 智析", "Performance Analytics" if is_en else "效果分析", "Track GEO + WW Direct Reg Start trends, weekly/monthly/YTD data analysis, attribution analysis" if is_en else "追踪 GEO + WW Direct Reg Start 趋势，周度/月度/YTD 数据分析，归因判断"),
        ("🎯 智中枢", "Decision Engine" if is_en else "决策引擎", "Based on analytics data + 7 decision rules, auto-generate weekly action plans and priority recommendations" if is_en else "基于智析数据 + 7 条决策规则，自动生成周度行动计划和优先级建议"),
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
    st.title("📚 Query Library – AI Search Phrase Generation" if is_en else "📚 智库 – AI 检索短语生成")
    render_pipeline_flow("zhiku", selected_batch)
    st.caption("Step 1: Generate AI-native search phrases from SEO/SEM keywords or seed words" if is_en else "Step 1: 从 SEO/SEM 关键词或核心词根裂变生成 AI 原生检索短语")

    # ─── ① 生成检索短语 ───
    st.subheader("① Generate Search Phrases" if is_en else "① 生成检索短语")

    # Load current zhiku data for progress tracking
    df_q_current = load_zhiku_live(selected_batch)
    current_count = len(df_q_current) if not df_q_current.empty else 0

    st.caption("Use Source A, B individually or together; results auto-merged and deduped" if is_en else "可选 A、B 单独或同时使用，结果自动合并去重")

    col_src_a, col_src_b = st.columns(2)

    # ── 源 A：SEO/SEM 关键词裂变 ──
    with col_src_a:
        st.markdown("**Source A: SEO/SEM Keyword Expansion**" if is_en else "**源 A：SEO/SEM 关键词裂变**")
        uploaded_file = st.file_uploader("Upload Keywords CSV" if is_en else "上传关键词 CSV", type=["csv"], key="kw_upload_zhiku")
        if uploaded_file is not None:
            df_uploaded = pd.read_csv(uploaded_file, on_bad_lines="skip")
            st.session_state["uploaded_keywords"] = df_uploaded
            INPUT_PATH.mkdir(parents=True, exist_ok=True)
            df_uploaded.to_csv(INPUT_PATH / "seo_sem_keywords.csv", index=False, encoding="utf-8-sig")
            st.success(f"✅ {len(df_uploaded)} {'keywords' if is_en else '个关键词'}")

        df_kw = load_keywords()
        kw_count = len(df_kw) if not df_kw.empty else 0
        if kw_count > 0:
            target_a = kw_count * 10
            # Show current progress
            _df_live = load_csv_safe(OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv")
            existing_a = len(_df_live) if not _df_live.empty else 0
            st.caption(f"{kw_count} {'keywords' if is_en else '关键词'} · {'est.' if is_en else '预估'} ~{target_a} {'phrases' if is_en else '条'}")
            if existing_a > 0:
                st.progress(min(1.0, existing_a / target_a), text=f"{'Library' if is_en else '库中'} {existing_a}/{target_a}")
                btn_text_a = f"🔄 {'Continue Expand Source A' if is_en else '继续裂变源 A'}（{'library' if is_en else '库中'} {existing_a} {'phrases' if is_en else '条'}）"
            else:
                btn_text_a = "🚀 Expand Source A" if is_en else "🚀 裂变源 A"
            kw_per_batch = st.select_slider("Keywords per batch" if is_en else "每次处理关键词数", options=[10, 20, 30, 50], value=10, key="kw_per_batch")
            if st.button(btn_text_a, type="primary", key="run_source_a"):
                try:
                    from engine import run_zhiku
                    with st.spinner("Expanding Source A..." if is_en else "源 A 裂变中..."):
                        result = run_zhiku(selected_batch, market, kw_per_batch)
                    if result["success"]:
                        st.success(f"✅ +{result['query_count']} {'phrases' if is_en else '条'}")
                    else:
                        st.error(result['error'])
                except Exception as e:
                    st.error(str(e))

    # ── 源 B：核心词根裂变 ──
    with col_src_b:
        st.markdown("**Source B: Seed Word Expansion**" if is_en else "**源 B：核心词根裂变**")
        seed_words = st.text_area("Seed words (one per line)" if is_en else "核心词根（每行一个）", placeholder="跨境电商\n亚马逊开店\n选品", height=100, key="seed_words_input")
        seeds = [w.strip() for w in seed_words.strip().split("\n") if w.strip()] if seed_words else []

        if seeds:
            st.caption(f"{len(seeds)} {'seeds' if is_en else '个词根'} · {'est.' if is_en else '预估'} ~{len(seeds) * 15} {'phrases' if is_en else '条'}")

        if st.button("🚀 Expand Source B" if is_en else "🚀 裂变源 B", type="primary", key="run_source_b", disabled=(len(seeds) == 0)):
            if seeds:
                try:
                    from engine import run_semantic_expansion
                    total_gen = 0
                    with st.spinner("Expanding Source B..." if is_en else "源 B 裂变中..."):
                        for seed in seeds:
                            r = run_semantic_expansion(seed, market, 15, "zh", selected_batch)
                            if r.get("success"):
                                total_gen += r.get("query_count", 0)
                    if total_gen > 0:
                        st.success(f"✅ +{total_gen} {'phrases' if is_en else '条'}")
                    else:
                        st.warning("No phrases generated" if is_en else "未生成短语")
                except Exception as e:
                    st.error(str(e))

    # Progress bar (full width)
    if current_count > 0:
        col_info, col_clear = st.columns([3, 1])
        with col_info:
            st.caption(f"📊 {'Phrase library has' if is_en else '短语库已有'} {current_count} {'phrases' if is_en else '条'}")
        with col_clear:
            if st.button("🗑️ Clear" if is_en else "🗑️ 清空", key="clear_zhiku"):
                zhiku_file = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
                if zhiku_file.exists():
                    # Archive instead of delete
                    archive_dir = zhiku_file.parent / "archive"
                    archive_dir.mkdir(exist_ok=True)
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    zhiku_file.rename(archive_dir / f"{zhiku_file.stem}_{ts}{zhiku_file.suffix}")
                st.success("Cleared (history archived)" if is_en else "已清空（历史已归档）")

    st.divider()

    # ─── 上传已有短语 ───
    with st.expander("📤 Upload Existing Phrases (Manual)" if is_en else "📤 上传已有检索短语（人工准备）", expanded=False):
        st.caption("Upload prepared search phrase CSV, auto-merged into phrase library" if is_en else "直接上传准备好的检索短语 CSV，自动合并到短语库")
        uploaded_phrases = st.file_uploader("Upload CSV" if is_en else "上传 CSV", type=["csv", "xlsx"], key="upload_existing_phrases")
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
                        st.success(f"✅ {'Imported' if is_en else '导入'} {len(df_import)} {'phrases, after dedup library has' if is_en else '条，合并去重后库中'} {len(df_merged)} {'phrases' if is_en else '条'}")
                    else:
                        df_import.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                        st.success(f"✅ {'Imported' if is_en else '导入'} {len(df_import)} {'phrases' if is_en else '条'}")
                else:
                    df_import.to_csv(zhiku_file, index=False, encoding="utf-8-sig")
                    st.success(f"✅ {'Imported' if is_en else '导入'} {len(df_import)} {'phrases' if is_en else '条'}")
            except Exception as e:
                st.error(f"{'Import failed' if is_en else '导入失败'}: {e}")

    st.divider()

    # ─── ② 短语库 — 分类 & 校对 ───
    st.subheader("② Phrase Library — Classify & Proofread" if is_en else "② 短语库 — 分类 & 校对")

    df_q = load_zhiku_live(selected_batch)

    if df_q.empty:
        st.caption("⏳ Please run Step ① to generate search phrases first" if is_en else "⏳ 请先执行第①步生成检索短语")
    else:
        # Filters — simple selectbox
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            if "category" in df_q.columns:
                cat_options = ["全部"] + sorted(df_q["category"].dropna().unique().tolist())
                cat_filter = st.selectbox("Filter by category" if is_en else "按类别筛选", cat_options, key="cat_filter")
            else:
                cat_filter = "全部"
        with col_f2:
            score_range = st.slider("Filter by score" if is_en else "按综合分筛选", 1.0, 5.0, (1.0, 5.0), 0.5, key="score_filter")

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
                select_action = st.radio("Select action" if is_en else "选中操作", ["不变", "全选", "全不选"], horizontal=True, key="select_action", label_visibility="collapsed")
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
                    "Category" if is_en else "类别", options=CATEGORIES_35, width="medium"
                )
            if "is_selected" in df_display.columns:
                column_config["is_selected"] = st.column_config.CheckboxColumn("Selected" if is_en else "选中")
            if "target_market" in df_display.columns:
                column_config["target_market"] = st.column_config.SelectboxColumn(
                    "Target Market" if is_en else "适用平台", options=["CN", "WW", "Both"]
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
                "📥 Export Filtered CSV" if is_en else "📥 导出筛选结果 CSV", csv_export,
                file_name=f"zhiku_filtered_{selected_batch}.csv", mime="text/csv"
            )
        else:
            st.dataframe(df_display, use_container_width=True, hide_index=True)

        # ─── 📊 类别覆盖看板 ───
        st.divider()
        st.subheader("📊 Category Coverage Dashboard" if is_en else "📊 类别覆盖看板")

        col_k1, col_k2, col_k3, col_k4 = st.columns(4)
        with col_k1:
            st.metric("Total Phrases" if is_en else "总短语", len(df_q))
        with col_k2:
            if "category" in df_q.columns:
                covered = df_q["category"].dropna().nunique()
                st.metric("Categories Covered" if is_en else "已覆盖类别", f"{covered}/35")
            else:
                st.metric("Categories Covered" if is_en else "已覆盖类别", "N/A")
        with col_k3:
            if "category" in df_q.columns:
                empty_cats = 35 - df_q["category"].dropna().nunique()
                st.metric("Empty Categories" if is_en else "空类别", empty_cats)
            else:
                st.metric("Empty Categories" if is_en else "空类别", "N/A")
        with col_k4:
            if "is_selected" in df_q.columns:
                sel_count = df_q[df_q["is_selected"].astype(str).str.upper() == "TRUE"].shape[0]
                st.metric("Selected" if is_en else "已选中", sel_count)
            else:
                st.metric("Selected" if is_en else "已选中", "N/A")

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
    st.subheader("③ Gap Verification" if is_en else "③ Gap 验证")
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
                "Content Mentioned" if is_en else "内容提及", options=["✅", "❌", "⚠️"]
            ),
            "has_link": st.column_config.SelectboxColumn(
                "Has Link" if is_en else "带链接", options=["✅", "❌"]
            ),
        }
        st.data_editor(
            df_gap[gap_cols], column_config=gap_config,
            use_container_width=True, hide_index=True, key="gap_editor"
        )
    elif df_q.empty:
        st.info("Gap verification will show after running Step ①" if is_en else "执行第①步后显示 Gap 验证")

    st.divider()

    # CTA → 智造
    st.subheader("✅ Query Library Complete" if is_en else "✅ 智库完成")
    if st.button("➡️ Go to Content Creation (Step 2)" if is_en else "➡️ 进入智造 (Step 2)", type="primary", key="cta_zhiku_to_zhizao"):
        jump_to("✍️ 智造")
        st.rerun()

    # 📜 历史记录
    with st.expander("📜 History" if is_en else "📜 历史记录"):
        batch_path = OUTPUT_PATH / selected_batch / "01_zhiku"
        all_files = []
        if batch_path.exists():
            all_files.extend([f for f in batch_path.glob("*.csv")])
            archive_path = batch_path / "archive"
            if archive_path.exists():
                all_files.extend([f for f in archive_path.glob("*.csv")])
        if all_files:
            all_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            for f in all_files:
                mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                size_kb = f.stat().st_size / 1024
                col_i, col_d = st.columns([3, 1])
                with col_i:
                    st.caption(f"📄 {f.name} · {size_kb:.1f}KB · 🕐 {mtime}")
                with col_d:
                    st.download_button("⬇️", f.read_bytes(), file_name=f.name, mime="text/csv", key=f"dl_{f.name}")
        else:
            st.caption("No history files" if is_en else "暂无历史文件")


# ============================================================
# PAGE: 智造 (Step 2) — 单页线性流程
# ============================================================
elif page == "✍️ 智造":
    st.title("✍️ Content Creation – Content Generation" if is_en else "✍️ 智造 – Content Generation")
    render_pipeline_flow("zhizao", selected_batch)
    st.caption("Step 2: Generate SEO+GEO dual-optimized content based on AI Queries" if is_en else "Step 2: 基于 AI Queries 生成 SEO+GEO 双优化内容")

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
        btn_label_z = f"✅ {'All done' if is_en else '全部生成完毕'} ({already_generated}/{total_selected})"
    else:
        btn_label_z = "🚀 Run Content Gen" if is_en else "🚀 执行智造"

    if st.button(btn_label_z, type="primary", key="run_zhizao", disabled=(remaining == 0 and already_generated > 0)):
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
                zhizao_file = OUTPUT_PATH / selected_batch / "02_zhizao" / "zhizao_draft_content.csv"
                if zhizao_file.exists():
                    zhizao_file.unlink()
                st.success("Cleared" if is_en else "已清空")

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
                        st.session_state["reuse_zhizao_file"] = str(f)
                        st.success(f"{'Selected for reuse' if is_en else '已选择复用'}: {f.name}")
                with col_d:
                    st.download_button("⬇️", f.read_bytes(), file_name=f.name, mime="text/csv", key=f"dl_zhizao_{f.name}")
        else:
            st.caption("No history" if is_en else "暂无历史")


# ============================================================
# PAGE: 智优 (Step 3) — 一键自动完成
# ============================================================
elif page == "🔧 智优":
    st.title("🔧 Optimization – Score · Rewrite · Compliance" if is_en else "🔧 智优 – Score · Rewrite · Compliance")
    render_pipeline_flow("zhiyou", selected_batch)
    st.caption("Step 3: One-click auto: Score → Rewrite → Compliance Review" if is_en else "Step 3: 一键自动完成 评分 → 重写优化 → 合规审查")

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
        display_cols_in = [c for c in ["title", "ai_query", "word_count", "confirmed"] if c in df_incoming.columns]
        if "confirmed" not in df_incoming.columns:
            df_incoming["confirmed"] = True
        st.data_editor(
            df_incoming[display_cols_in].reset_index(drop=True) if display_cols_in else df_incoming,
            column_config={
                "title": st.column_config.TextColumn("Title" if is_en else "标题", disabled=True),
                "ai_query": st.column_config.TextColumn("Search Phrase" if is_en else "检索短语", disabled=True),
                "word_count": st.column_config.NumberColumn("Words" if is_en else "字数", disabled=True),
                "confirmed": st.column_config.CheckboxColumn("Include" if is_en else "纳入优化"),
            },
            use_container_width=True, hide_index=True,
            key="zhiyou_incoming_editor",
        )
        st.caption(f"{len(df_incoming)} {'articles from Content Creation' if is_en else '篇来自智造'}")
    else:
        st.caption("No content from Content Creation. Upload or run Content Creation first." if is_en else "暂无智造内容，请先上传或执行智造。")

    st.divider()

    # One-click execution
    st.subheader("▶️ One-Click Full Optimization" if is_en else "▶️ 一键执行智优全流程")
    st.markdown("Auto-execute in order: **Score → Rewrite → Compliance Review**" if is_en else "自动按顺序执行：**评分 → 重写 → 合规审查**")

    # Show progress
    df_opt_existing = load_optimized(selected_batch)
    df_incoming_count = len(df_incoming) if not df_incoming.empty else 0
    opt_done = len(df_opt_existing) if not df_opt_existing.empty else 0

    if df_incoming_count > 0:
        st.progress(min(1.0, opt_done / df_incoming_count), text=f"{'Optimized' if is_en else '已优化'} {opt_done}/{df_incoming_count} {'articles' if is_en else '篇'}")

    if opt_done > 0 and opt_done < df_incoming_count:
        btn_zhiyou = f"🔄 {'Continue optimizing remaining' if is_en else '继续优化剩余'} {df_incoming_count - opt_done} {'articles' if is_en else '篇'} ({opt_done}/{df_incoming_count})"
    elif opt_done >= df_incoming_count and opt_done > 0:
        btn_zhiyou = f"✅ {'All optimized' if is_en else '全部优化完毕'} ({opt_done}/{df_incoming_count})"
    else:
        btn_zhiyou = "🚀 One-Click Full Optimization" if is_en else "🚀 一键智优全流程"

    if st.button(btn_zhiyou, type="primary", key="run_zhiyou_all", disabled=(opt_done >= df_incoming_count and opt_done > 0)):
        try:
            from engine import run_zhiyou_score, run_zhiyou_execute, run_zhiyou_compliance
            progress_bar = st.progress(0)
            status_text = st.empty()

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

    # CTA → 智布
    st.divider()
    if st.button("➡️ Go to Publishing (Step 4)" if is_en else "➡️ 进入智布 (Step 4)", type="primary", key="cta_zhiyou_to_zhibu"):
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
                        st.session_state["reuse_zhiyou_file"] = str(f)
                        st.success(f"{'Selected for reuse' if is_en else '已选择复用'}: {f.name}")
                with col_d:
                    st.download_button("⬇️", f.read_bytes(), file_name=f.name, mime="text/csv", key=f"dl_zhiyou_{f.name}")
        else:
            st.caption("No history" if is_en else "暂无历史")


# ============================================================
# PAGE: 智布 (Step 4)
# ============================================================
elif page == "📦 智布":
    st.title("📦 Publishing – JSON / Word Formatting" if is_en else "📦 智布 – JSON / Word Formatting")
    render_pipeline_flow("zhibu", selected_batch)
    st.caption("Step 4: Convert optimized content to structured JSON and Word documents" if is_en else "Step 4: 将优化内容转换为结构化 JSON 和 Word 文档")

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
            sel_idx = st.selectbox(
                "Select item" if is_en else "选择条目", range(len(items)),
                format_func=lambda i: items[i].get("meta", {}).get("title", f"Item {i}"),
                key="zhibu_preview_select"
            )
            st.json(items[sel_idx])
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
                        st.session_state["reuse_zhibu_file"] = str(f)
                        st.success(f"{'Selected for reuse' if is_en else '已选择复用'}: {f.name}")
                with col_d:
                    mime = "application/json" if f.suffix == ".json" else "text/csv"
                    st.download_button("⬇️", f.read_bytes(), file_name=f.name, mime=mime, key=f"dl_zhibu_{f.name}")
        else:
            st.caption("No history" if is_en else "暂无历史")


# ============================================================
# ============================================================
# PAGE: 智析 (Step 6) — 重构版
# ============================================================
elif page == "📈 智析":
    st.title("📈 Analytics – Performance & Gap Analysis" if is_en else "📈 智析 – Performance & Gap Analysis")
    render_pipeline_flow("zhixi", selected_batch)
    st.caption("Performance Analysis: Output trends · Input tracking · AI citation monitoring · Gap opportunities" if is_en else "效果分析：Output 趋势 · Input 产出追踪 · AI 引用监控 · Gap 机会点")

    # --- Upload metrics data ---
    with st.expander("📤 Upload Data (manual metrics import)" if is_en else "📤 上传数据（手动导入 metrics）", expanded=False):
        st.caption("Optional: Upload weekly/monthly metrics CSV" if is_en else "可选：上传 weekly/monthly metrics CSV")
        upload_zhixi = st.file_uploader("Upload Metrics CSV" if is_en else "上传 Metrics CSV", type=["csv", "xlsx"], key="zhixi_direct_upload")
        if upload_zhixi:
            try:
                if upload_zhixi.name.endswith(".xlsx"):
                    df_up = pd.read_excel(upload_zhixi, engine="openpyxl")
                else:
                    df_up = pd.read_csv(upload_zhixi, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
                metrics_dir = OUTPUT_PATH / "metrics"
                metrics_dir.mkdir(parents=True, exist_ok=True)
                df_up.to_csv(metrics_dir / "uploaded_metrics.csv", index=False, encoding="utf-8-sig")
                st.success(f"✅ {'Uploaded' if is_en else '已上传'} {len(df_up)} {'rows' if is_en else '行数据'}")
            except Exception as e:
                st.error(f"{'Upload failed' if is_en else '上传失败'}: {e}")

    # --- 4 Tabs ---
    tab_output, tab_input, tab_citation, tab_gap = st.tabs([
        "📊 Output Trends" if is_en else "📊 Output 趋势",
        "📥 Input Production" if is_en else "📥 Input 产出",
        "🔗 AI Citation Tracking" if is_en else "🔗 AI 引用追踪",
        "💡 Gap & Opportunities" if is_en else "💡 Gap & 机会点",
    ])

    # ============================================================
    # TAB 1: Output 趋势
    # ============================================================
    with tab_output:
        sub_weekly, sub_monthly, sub_ytd = st.tabs(["Weekly", "Monthly", "YTD"])

        with sub_weekly:
            st.subheader("📅 Weekly Trends" if is_en else "📅 Weekly 趋势")
            df_w = get_weekly_metrics()
            # Week selector
            all_weeks = df_w["Week"].tolist()
            week_range = st.select_slider("Select week range" if is_en else "选择周范围", options=all_weeks,
                                          value=(all_weeks[0], all_weeks[-1]), key="zhixi_week_range")
            start_idx = all_weeks.index(week_range[0])
            end_idx = all_weeks.index(week_range[1])
            df_w_filtered = df_w.iloc[start_idx:end_idx+1]

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_w_filtered["Week"], y=df_w_filtered["Total"], mode="lines+markers", name="Total", line=dict(color="#4a9eff", width=3)))
            fig.add_trace(go.Scatter(x=df_w_filtered["Week"], y=df_w_filtered["WW_Direct_EST"], mode="lines+markers", name="WW Direct EST", line=dict(color="#52b788", width=2)))
            fig.add_trace(go.Scatter(x=df_w_filtered["Week"], y=df_w_filtered["CN_GEO"], mode="lines+markers", name="CN GEO", line=dict(color="#fbbf24", width=2)))
            fig.add_trace(go.Scatter(x=df_w_filtered["Week"], y=df_w_filtered["WW_GEO"], mode="lines+markers", name="WW GEO", line=dict(color="#a78bfa", width=2)))
            fig.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.15), yaxis_title="Reg Starts")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_w_filtered, use_container_width=True, hide_index=True)

        with sub_monthly:
            st.subheader("📆 Monthly Trends" if is_en else "📆 Monthly 趋势")
            monthly_data = pd.DataFrame({
                "Channel": ["CN GEO", "WW GEO", "WW Direct EST", "WW Direct EM", "Total"],
                "M1 (Jan)": [89, 51, 4965, 326, 5431],
                "M2 (Feb)": [65, 49, 2389, 326, 2829],
                "M3 (Mar)": [165, 91, 7269, 649, 8174],
                "M4 (Apr)": [164, 71, 7205, 340, 7780],
                "M5 (MTD)": [159, 88, 7323, 255, 7825],
            })
            st.dataframe(monthly_data, use_container_width=True, hide_index=True)

            # Monthly trend chart
            months = ["Jan", "Feb", "Mar", "Apr", "May"]
            fig_m = go.Figure()
            fig_m.add_trace(go.Bar(name="CN GEO", x=months, y=[89, 65, 165, 164, 159], marker_color="#fbbf24"))
            fig_m.add_trace(go.Bar(name="WW GEO", x=months, y=[51, 49, 91, 71, 88], marker_color="#a78bfa"))
            fig_m.add_trace(go.Bar(name="WW Direct EST", x=months, y=[4965, 2389, 7269, 7205, 7323], marker_color="#4a9eff"))
            fig_m.update_layout(barmode="group", height=300, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.15))
            st.plotly_chart(fig_m, use_container_width=True)

        with sub_ytd:
            st.subheader("📊 YTD Comparison" if is_en else "📊 YTD 对比")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("GEO+Direct Total", "28,741", "+55% YoY")
            with col2:
                st.metric("CN GEO", "574", "+452%")
            with col3:
                st.metric("WW Direct EST", "25,863", "+62%")
            with col4:
                st.metric("vs Benchmark" if is_en else "vs 大盘", "+78 ppts", "Outperforming SSR" if is_en else "跑赢 SSR")

            st.divider()
            df_ytd = get_ytd_metrics()
            df_ytd["增量"] = df_ytd["YTD_Actual"] - df_ytd["YTD_PY"]
            st.dataframe(df_ytd, use_container_width=True, hide_index=True)

            # Bar chart
            df_bar = df_ytd[df_ytd["Channel"] != "Total"].copy()
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(name="YTD Actual", x=df_bar["Channel"], y=df_bar["YTD_Actual"], marker_color="#4a9eff"))
            fig_bar.add_trace(go.Bar(name="YTD PY", x=df_bar["Channel"], y=df_bar["YTD_PY"], marker_color="#555"))
            fig_bar.update_layout(barmode="group", height=300, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=-0.15))
            st.plotly_chart(fig_bar, use_container_width=True)

    # ============================================================
    # TAB 2: Input 产出
    # ============================================================
    with tab_input:
        st.subheader("📥 Content Production Tracking" if is_en else "📥 内容产出追踪")

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
    # TAB 3: AI 引用追踪 (矩阵式)
    # ============================================================
    with tab_citation:
        st.subheader("🔗 AI Citation Tracking" if is_en else "🔗 AI 引用追踪")
        st.markdown("Overview of citation status for each Topic across AI platforms" if is_en else "每个 Topic 在各 AI 平台的引用状态一览")

        AI_PLATFORMS_LIST = ["ChatGPT", "Perplexity", "Gemini", "DeepSeek", "豆包", "Kimi", "千问"]
        STATUS_OPTIONS = ["未检测", "✅ 提及+链接", "✅ 提及无链接", "❌ 未提及"]

        citation_file = OUTPUT_PATH / "citation_matrix.csv"

        # Load or create matrix
        if citation_file.exists():
            df_matrix = load_csv_safe(citation_file)
        else:
            df_matrix = pd.DataFrame()

        # If empty, initialize with topics from articles
        if df_matrix.empty:
            df_articles = load_zhizao(selected_batch)
            if not df_articles.empty and "category" in df_articles.columns:
                topics = sorted(df_articles["category"].dropna().unique().tolist())
            else:
                topics = CATEGORIES_35[:10]  # Default sample
            rows = []
            for topic in topics:
                row = {"Topic": topic}
                for platform in AI_PLATFORMS_LIST:
                    row[platform] = "未检测"
                rows.append(row)
            df_matrix = pd.DataFrame(rows)

        # Filter by topic
        if "Topic" in df_matrix.columns:
            topic_filter = st.selectbox("Filter Topic" if is_en else "筛选 Topic", ["全部"] + df_matrix["Topic"].tolist(), key="matrix_topic_filter")
            if topic_filter != "全部":
                df_matrix_display = df_matrix[df_matrix["Topic"] == topic_filter]
            else:
                df_matrix_display = df_matrix
        else:
            df_matrix_display = df_matrix

        # Editable matrix
        col_config = {"Topic": st.column_config.TextColumn("Topic", disabled=True, width="large")}
        for platform in AI_PLATFORMS_LIST:
            if platform in df_matrix_display.columns:
                col_config[platform] = st.column_config.SelectboxColumn(
                    platform, options=STATUS_OPTIONS, width="small"
                )

        edited_matrix = st.data_editor(
            df_matrix_display,
            column_config=col_config,
            use_container_width=True,
            hide_index=True,
            key="citation_matrix_editor",
        )

        # Auto-save
        citation_file.parent.mkdir(parents=True, exist_ok=True)
        # Merge edits back
        if topic_filter == "全部":
            edited_matrix.to_csv(citation_file, index=False, encoding="utf-8-sig")
        else:
            # Update only filtered rows
            df_matrix.loc[df_matrix["Topic"] == topic_filter, AI_PLATFORMS_LIST] = edited_matrix[AI_PLATFORMS_LIST].values
            df_matrix.to_csv(citation_file, index=False, encoding="utf-8-sig")

        # Summary KPIs
        st.divider()
        if "Topic" in df_matrix.columns:
            total_cells = len(df_matrix) * len(AI_PLATFORMS_LIST)
            mentioned_cells = 0
            linked_cells = 0
            for platform in AI_PLATFORMS_LIST:
                if platform in df_matrix.columns:
                    mentioned_cells += df_matrix[platform].astype(str).str.contains("✅").sum()
                    linked_cells += df_matrix[platform].astype(str).str.contains("链接").sum()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Topics", len(df_matrix))
            with col2:
                st.metric("Mentioned" if is_en else "有提及", mentioned_cells)
            with col3:
                st.metric("With Link" if is_en else "带链接", linked_cells)
            with col4:
                coverage = mentioned_cells / total_cells * 100 if total_cells > 0 else 0
                st.metric("Coverage" if is_en else "覆盖率", f"{coverage:.1f}%")

        # Add new topic row
        st.divider()
        with st.expander("➕ Add Topic" if is_en else "➕ 新增 Topic"):
            new_topic = st.selectbox("Select Topic" if is_en else "选择 Topic", [t for t in CATEGORIES_35 if t not in df_matrix.get("Topic", pd.Series()).tolist()], key="add_matrix_topic")
            if st.button("Add" if is_en else "添加", key="add_matrix_row"):
                new_row = {"Topic": new_topic}
                for p in AI_PLATFORMS_LIST:
                    new_row[p] = "未检测"
                df_matrix = pd.concat([df_matrix, pd.DataFrame([new_row])], ignore_index=True)
                df_matrix.to_csv(citation_file, index=False, encoding="utf-8-sig")
                st.success(f"✅ {'Added' if is_en else '已添加'}: {new_topic}")

    # TAB 4: Gap & 机会点
    # ============================================================
    with tab_gap:
        st.subheader("💡 Gap & Opportunities" if is_en else "💡 Gap & 机会点")
        st.markdown("Identify optimization opportunities based on citation tracking and content coverage analysis" if is_en else "基于引用追踪和内容覆盖分析，识别优化机会")

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
                col_i, col_d = st.columns([4, 1])
                with col_i:
                    st.caption(f"📄 {f.name} · {f.stat().st_size/1024:.1f}KB · 🕐 {mtime}")
                with col_d:
                    st.download_button("⬇️", f.read_bytes(), file_name=f.name, mime="text/csv", key=f"dl_zhixi_{f.name}")
        else:
            st.caption("No history" if is_en else "暂无历史")

# PAGE: 智中枢
# ============================================================
elif page == "🎯 智中枢":
    st.title("🎯 Decision Engine" if is_en else "🎯 智中枢 – Decision Engine")
    render_pipeline_flow("zhongshu", selected_batch)
    st.caption("Based on analytics data + 7 decision rules, generate weekly action plan" if is_en else "基于智析数据 + 7 条决策规则，生成周度行动计划")

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
elif page == "📊 批次对比":
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
elif page == "📌 发布追踪":
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
elif page == "📝 需求中心":
    st.title("📝 Request Center" if is_en else "📝 需求中心")
    st.caption("Intake + Journey Research — Product request submission, user journey research, request tracking" if is_en else "Intake + 智测合并 — 产品需求提交、用户旅程调研、需求追踪")

    tab_geo, tab_zhice, tab_tracking = st.tabs([
        "🚀 Product GEO Request" if is_en else "🚀 产品 GEO 需求",
        "🔬 User Journey Research" if is_en else "🔬 用户旅程调研 (智测)",
        "📋 Request Progress Tracking" if is_en else "📋 需求进展追踪",
    ])

    with tab_geo:
        st.subheader("🚀 Product GEO Request" if is_en else "🚀 产品 GEO 需求")
        st.markdown("Submit product name → Expand → Generate → Publish" if is_en else "提交产品名 → 裂变 → 生成 → 发布")

        with st.form("geo_intake_form"):
            product_name = st.text_input("Product Name" if is_en else "产品名称", placeholder="例如：亚马逊FBA物流服务")
            product_desc = st.text_area("Product Description" if is_en else "产品简述", placeholder="简要描述产品特点和目标受众")
            target_market_intake = st.multiselect("Target Market" if is_en else "目标市场", ["CN", "NA", "EU", "JP", "AU"])
            priority_intake = st.select_slider("Priority" if is_en else "优先级", options=["低", "中", "高", "紧急"], value="中")
            submitted_geo = st.form_submit_button("Submit Request" if is_en else "提交需求", type="primary")

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
                st.success(f"✅ {'Request submitted' if is_en else '需求已提交'}: {product_name}")

    with tab_zhice:
        st.subheader("🔬 User Journey Research" if is_en else "🔬 用户旅程调研 (智测)")
        st.markdown("Set persona → Simulate journey → Output gaps" if is_en else "设定 persona → 模拟旅程 → 输出 gap")

        persona_name = st.text_input("Persona Name" if is_en else "用户画像名称", placeholder="例如：深圳3C配件卖家")
        persona_goal = st.text_area("User Goal" if is_en else "用户目标", placeholder="想开亚马逊美国站，寻找入门路径")
        platforms = st.multiselect(
            "AI Search Platforms" if is_en else "AI 检索平台",
            ["chatgpt", "perplexity", "gemini", "deepseek", "doubao", "kimi", "yuanbao", "qianwen"],
            default=["chatgpt", "perplexity", "deepseek"],
        )
        rounds_count = st.number_input("Simulation Rounds" if is_en else "模拟轮次", 3, 10, 5, key="zhice_rounds")

        if st.button("🚀 Start Journey Simulation" if is_en else "🚀 开始模拟旅程", type="primary", key="run_zhice"):
            try:
                from zhice_engine import run_zhice_journey
                with st.spinner("Simulating user journey..." if is_en else "正在模拟用户旅程..."):
                    result = run_zhice_journey(
                        persona_name=persona_name,
                        persona_goal=persona_goal,
                        platforms=platforms,
                        rounds=rounds_count,
                    )
                if result.get("success"):
                    st.success("✅ Journey simulation complete!" if is_en else "✅ 旅程模拟完成！")
                    st.json(result.get("summary", {}))
                else:
                    st.error(f"❌ {'Failed' if is_en else '失败'}: {result.get('error', '')}")
            except ImportError:
                st.error("zhice_engine module not ready" if is_en else "zhice_engine 模块未就绪")

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
elif page == "🔍 引用分析":
    st.title("🔍 Citation Analysis" if is_en else "🔍 引用分析")
    st.caption("Analyze AI search engine citation of our content" if is_en else "分析 AI 搜索引擎对内容的引用情况")

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
elif page == "⚙️ Settings":
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
