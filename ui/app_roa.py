"""
Smart Suite ROA Edition - GEO Content Pipeline
For ROA (Rest of Amazon) teams: NA / EU / JP markets only.
No CN-specific platforms, legal requirements, or content rules.

Run: streamlit run app_roa.py
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

import tempfile
import os

if not OUTPUT_PATH.exists():
    OUTPUT_PATH = Path(tempfile.gettempdir()) / "smartsuite_output"
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
if not INPUT_PATH.exists():
    INPUT_PATH = Path(tempfile.gettempdir()) / "smartsuite_input"
    INPUT_PATH.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="Smart Suite ROA",
    page_icon="🌍",
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
h3 { margin-top: 0.5rem !important; padding-bottom: 0.3rem !important; border-bottom: 1px solid #2a2a2a; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# INTERNATIONALIZATION (EN / TW / VN / KR)
# ============================================================

UI_LANGS = {
    "English": "en",
    "繁體中文": "tw",
    "Tiếng Việt": "vi",
    "한국어": "ko",
}

T = {
    "en": {
        "title": "🌍 Smart Suite ROA",
        "subtitle": "GEO Content Pipeline · ROA Edition",
        "nav_overview": "🏠 Overview",
        "nav_query": "📚 Query Generation",
        "nav_content": "✍️ Content Creation",
        "nav_optimize": "🔧 Optimization",
        "nav_publish": "📦 Publishing",
        "nav_metrics": "📈 Metrics & Analytics",
        "nav_simulation": "🔬 AI Search Simulation",
        "nav_mario": "📊 Mario-GEO",
        "nav_settings": "⚙️ Settings",
        "batch": "📂 Current Batch",
        "market": "🌍 Market",
        "content_lang": "🌐 Content Language",
        "kw_limit": "🔑 Keyword Limit",
        "pipeline_status": "📊 Pipeline Status",
        "done": "Done",
        "pending": "Pending",
        "files": "files",
        "quick_actions": "⚡ Quick Actions",
        "run_pipeline": "🚀 Run Full Pipeline (Steps 1-4)",
        "pipeline_info": "Pipeline execution requires AWS Bedrock credentials. Configure in Settings.",
        "output_files": "📥 Output Files",
        "no_output": "Run the pipeline to generate output files.",
        "core_topic": "Core Topic / Keyword",
        "gen_queries": "🚀 Generate Queries",
        "existing_queries": "📋 Existing Queries",
        "no_queries": "No queries generated yet.",
        "articles_gen": "Articles to generate",
        "gen_content": "🚀 Generate Content",
        "generated_articles": "📋 Generated Articles",
        "no_content": "No content generated yet. Run Step 1 first.",
        "score_content": "📊 Score Content",
        "rewrite_content": "✍️ Rewrite Approved Content",
        "compliance_check": "⚖️ Run Compliance Check",
        "gen_json": "📤 Generate JSON Output",
        "gen_word": "📝 Generate Word Documents",
        "no_word": "No content available. Run Steps 1-3 first.",
        "key_metrics": "🎯 Key Metrics (WW)",
        "market_breakdown": "📊 Market Breakdown",
        "weekly_trend": "📈 Weekly Trend — WW Direct (Regstart)",
        "funnel": "📊 Regstart to Clean Launch Funnel (WW)",
        "select_platforms": "🌐 Select AI Platforms",
        "platforms_note": "Only WW platforms available in ROA edition",
        "persona": "👤 Seller Persona",
        "persona_name": "Persona Name",
        "background": "Background",
        "search_goal": "Search Goal",
        "query_language": "Query Language",
        "sim_rounds": "Simulation Rounds",
        "journey": "🔄 Search Journey",
        "ready_start": "📍 Ready to start Round",
        "completed": "Completed",
        "rounds": "rounds",
        "all_complete": "All rounds complete! Generate report below.",
        "edit_queries": "Edit Search Queries",
        "execute": "▶️ Execute Round",
        "skip": "⏭️ Skip",
        "reset": "🔄 Reset",
        "journey_history": "📋 Journey History",
        "our_content": "Our content",
        "no_journey": "No journey data yet. Execute rounds above.",
        "settings_creds": "🔑 AWS Credentials",
        "settings_api": "🌐 AI Platform API Keys",
        "about": "ℹ️ About",
        "save": "Save",
    },
    "tw": {
        "title": "🌍 Smart Suite ROA",
        "subtitle": "GEO 內容流水線 · ROA 版本",
        "nav_overview": "🏠 總覽",
        "nav_query": "📚 查詢生成",
        "nav_content": "✍️ 內容創建",
        "nav_optimize": "🔧 優化",
        "nav_publish": "📦 發佈",
        "nav_metrics": "📈 指標分析",
        "nav_simulation": "🔬 AI 搜尋模擬",
        "nav_mario": "📊 Mario-GEO",
        "nav_settings": "⚙️ 設定",
        "batch": "📂 目前批次",
        "market": "🌍 市場",
        "content_lang": "🌐 內容語言",
        "kw_limit": "🔑 關鍵詞上限",
        "pipeline_status": "📊 流水線狀態",
        "done": "完成",
        "pending": "待處理",
        "files": "個檔案",
        "quick_actions": "⚡ 快捷操作",
        "run_pipeline": "🚀 執行完整流水線 (Steps 1-4)",
        "pipeline_info": "需要 AWS Bedrock 憑證，請在設定中配置。",
        "output_files": "📥 輸出檔案",
        "no_output": "執行流水線後將在此處顯示結果。",
        "core_topic": "核心主題 / 關鍵詞",
        "gen_queries": "🚀 生成查詢",
        "existing_queries": "📋 現有查詢",
        "no_queries": "尚未生成查詢。",
        "articles_gen": "文章生成數量",
        "gen_content": "🚀 生成內容",
        "generated_articles": "📋 已生成文章",
        "no_content": "尚無內容。請先執行 Step 1。",
        "score_content": "📊 內容評分",
        "rewrite_content": "✍️ 重寫已通過內容",
        "compliance_check": "⚖️ 執行合規檢查",
        "gen_json": "📤 生成 JSON 輸出",
        "gen_word": "📝 生成 Word 文檔",
        "no_word": "沒有可用內容。請先執行 Steps 1-3。",
        "key_metrics": "🎯 關鍵指標 (WW)",
        "market_breakdown": "📊 市場細分",
        "weekly_trend": "📈 每週趨勢 — WW Direct (Regstart)",
        "funnel": "📊 Regstart 到 Clean Launch 漏斗 (WW)",
        "select_platforms": "🌐 選擇 AI 平台",
        "platforms_note": "ROA 版本僅提供海外平台",
        "persona": "👤 賣家畫像",
        "persona_name": "人物名稱",
        "background": "背景",
        "search_goal": "搜尋目標",
        "query_language": "查詢語言",
        "sim_rounds": "模擬輪次",
        "journey": "🔄 搜尋旅程",
        "ready_start": "📍 準備開始 Round",
        "completed": "已完成",
        "rounds": "輪",
        "all_complete": "全部輪次已完成！請在下方生成報告。",
        "edit_queries": "編輯搜尋查詢",
        "execute": "▶️ 執行 Round",
        "skip": "⏭️ 跳過",
        "reset": "🔄 重置",
        "journey_history": "📋 旅程記錄",
        "our_content": "我們的內容",
        "no_journey": "尚無旅程資料。請在上方執行。",
        "settings_creds": "🔑 AWS 憑證",
        "settings_api": "🌐 AI 平台 API 金鑰",
        "about": "ℹ️ 關於",
        "save": "儲存",
    },
    "vi": {
        "title": "🌍 Smart Suite ROA",
        "subtitle": "GEO Content Pipeline · Phiên bản ROA",
        "nav_overview": "🏠 Tổng quan",
        "nav_query": "📚 Tạo truy vấn",
        "nav_content": "✍️ Tạo nội dung",
        "nav_optimize": "🔧 Tối ưu hóa",
        "nav_publish": "📦 Xuất bản",
        "nav_metrics": "📈 Chỉ số & Phân tích",
        "nav_simulation": "🔬 Mô phỏng AI Search",
        "nav_mario": "📊 Mario-GEO",
        "nav_settings": "⚙️ Cài đặt",
        "batch": "📂 Batch hiện tại",
        "market": "🌍 Thị trường",
        "content_lang": "🌐 Ngôn ngữ nội dung",
        "kw_limit": "🔑 Giới hạn từ khóa",
        "pipeline_status": "📊 Trạng thái Pipeline",
        "done": "Hoàn thành",
        "pending": "Chờ xử lý",
        "files": "tệp",
        "quick_actions": "⚡ Thao tác nhanh",
        "run_pipeline": "🚀 Chạy toàn bộ Pipeline (Steps 1-4)",
        "pipeline_info": "Cần thông tin xác thực AWS Bedrock. Cấu hình trong Cài đặt.",
        "output_files": "📥 Tệp đầu ra",
        "no_output": "Chạy pipeline để tạo tệp đầu ra.",
        "core_topic": "Chủ đề / Từ khóa chính",
        "gen_queries": "🚀 Tạo truy vấn",
        "existing_queries": "📋 Truy vấn hiện có",
        "no_queries": "Chưa có truy vấn nào.",
        "articles_gen": "Số bài viết tạo",
        "gen_content": "🚀 Tạo nội dung",
        "generated_articles": "📋 Bài viết đã tạo",
        "no_content": "Chưa có nội dung. Chạy Step 1 trước.",
        "score_content": "📊 Chấm điểm nội dung",
        "rewrite_content": "✍️ Viết lại nội dung đã duyệt",
        "compliance_check": "⚖️ Kiểm tra tuân thủ",
        "gen_json": "📤 Tạo JSON",
        "gen_word": "📝 Tạo tài liệu Word",
        "no_word": "Không có nội dung. Chạy Steps 1-3 trước.",
        "key_metrics": "🎯 Chỉ số chính (WW)",
        "market_breakdown": "📊 Phân tích thị trường",
        "weekly_trend": "📈 Xu hướng tuần — WW Direct (Regstart)",
        "funnel": "📊 Phễu Regstart đến Clean Launch (WW)",
        "select_platforms": "🌐 Chọn nền tảng AI",
        "platforms_note": "Phiên bản ROA chỉ có nền tảng WW",
        "persona": "👤 Hồ sơ người bán",
        "persona_name": "Tên nhân vật",
        "background": "Bối cảnh",
        "search_goal": "Mục tiêu tìm kiếm",
        "query_language": "Ngôn ngữ truy vấn",
        "sim_rounds": "Số vòng mô phỏng",
        "journey": "🔄 Hành trình tìm kiếm",
        "ready_start": "📍 Sẵn sàng bắt đầu Round",
        "completed": "Đã hoàn thành",
        "rounds": "vòng",
        "all_complete": "Tất cả các vòng đã hoàn thành! Tạo báo cáo bên dưới.",
        "edit_queries": "Chỉnh sửa truy vấn",
        "execute": "▶️ Thực thi Round",
        "skip": "⏭️ Bỏ qua",
        "reset": "🔄 Đặt lại",
        "journey_history": "📋 Lịch sử hành trình",
        "our_content": "Nội dung của chúng tôi",
        "no_journey": "Chưa có dữ liệu. Thực thi các vòng ở trên.",
        "settings_creds": "🔑 Thông tin AWS",
        "settings_api": "🌐 API Keys nền tảng AI",
        "about": "ℹ️ Giới thiệu",
        "save": "Lưu",
    },
    "ko": {
        "title": "🌍 Smart Suite ROA",
        "subtitle": "GEO 콘텐츠 파이프라인 · ROA 에디션",
        "nav_overview": "🏠 개요",
        "nav_query": "📚 쿼리 생성",
        "nav_content": "✍️ 콘텐츠 생성",
        "nav_optimize": "🔧 최적화",
        "nav_publish": "📦 게시",
        "nav_metrics": "📈 지표 & 분석",
        "nav_simulation": "🔬 AI 검색 시뮬레이션",
        "nav_mario": "📊 Mario-GEO",
        "nav_settings": "⚙️ 설정",
        "batch": "📂 현재 배치",
        "market": "🌍 마켓",
        "content_lang": "🌐 콘텐츠 언어",
        "kw_limit": "🔑 키워드 제한",
        "pipeline_status": "📊 파이프라인 상태",
        "done": "완료",
        "pending": "대기중",
        "files": "파일",
        "quick_actions": "⚡ 빠른 실행",
        "run_pipeline": "🚀 전체 파이프라인 실행 (Steps 1-4)",
        "pipeline_info": "AWS Bedrock 자격증명이 필요합니다. 설정에서 구성하세요.",
        "output_files": "📥 출력 파일",
        "no_output": "파이프라인을 실행하여 출력 파일을 생성하세요.",
        "core_topic": "핵심 주제 / 키워드",
        "gen_queries": "🚀 쿼리 생성",
        "existing_queries": "📋 기존 쿼리",
        "no_queries": "아직 생성된 쿼리가 없습니다.",
        "articles_gen": "생성할 기사 수",
        "gen_content": "🚀 콘텐츠 생성",
        "generated_articles": "📋 생성된 기사",
        "no_content": "아직 콘텐츠가 없습니다. Step 1을 먼저 실행하세요.",
        "score_content": "📊 콘텐츠 평가",
        "rewrite_content": "✍️ 승인된 콘텐츠 재작성",
        "compliance_check": "⚖️ 규정 준수 검사 실행",
        "gen_json": "📤 JSON 출력 생성",
        "gen_word": "📝 Word 문서 생성",
        "no_word": "사용 가능한 콘텐츠가 없습니다. Steps 1-3을 먼저 실행하세요.",
        "key_metrics": "🎯 핵심 지표 (WW)",
        "market_breakdown": "📊 마켓별 분석",
        "weekly_trend": "📈 주간 추이 — WW Direct (Regstart)",
        "funnel": "📊 Regstart → Clean Launch 퍼널 (WW)",
        "select_platforms": "🌐 AI 플랫폼 선택",
        "platforms_note": "ROA 에디션은 WW 플랫폼만 제공",
        "persona": "👤 판매자 페르소나",
        "persona_name": "페르소나 이름",
        "background": "배경",
        "search_goal": "검색 목표",
        "query_language": "쿼리 언어",
        "sim_rounds": "시뮬레이션 라운드",
        "journey": "🔄 검색 여정",
        "ready_start": "📍 Round 시작 준비",
        "completed": "완료됨",
        "rounds": "라운드",
        "all_complete": "모든 라운드 완료! 아래에서 보고서를 생성하세요.",
        "edit_queries": "검색 쿼리 편집",
        "execute": "▶️ Round 실행",
        "skip": "⏭️ 건너뛰기",
        "reset": "🔄 초기화",
        "journey_history": "📋 여정 기록",
        "our_content": "우리 콘텐츠",
        "no_journey": "아직 여정 데이터가 없습니다. 위에서 라운드를 실행하세요.",
        "settings_creds": "🔑 AWS 자격증명",
        "settings_api": "🌐 AI 플랫폼 API 키",
        "about": "ℹ️ 소개",
        "save": "저장",
    },
}


def t(key: str) -> str:
    """Get translated text for current UI language."""
    lang_code = st.session_state.get("ui_lang_code", "en")
    return T.get(lang_code, T["en"]).get(key, T["en"].get(key, key))


# ============================================================
# CONSTANTS - ROA Only (No CN)
# ============================================================

MARKETS = ["NA", "EU", "JP", "AU", "AE", "SA"]

# Only WW AI platforms - no CN engines
AI_PLATFORMS = {
    "chatgpt": {"name": "ChatGPT (OpenAI)", "style": "Conversational, contextual, comprehensive answers"},
    "gemini": {"name": "Gemini (Google)", "style": "Search-enhanced, structured, Google ecosystem"},
    "perplexity": {"name": "Perplexity AI", "style": "Search-augmented, with source citations, academic feel"},
    "copilot": {"name": "Microsoft Copilot", "style": "Bing-integrated, concise, action-oriented"},
}

# Content output languages (what language to generate content in)
CONTENT_LANGUAGES = {
    "English": "en",
    "日本語": "ja",
    "한국어": "ko",
    "Deutsch": "de",
    "Français": "fr",
    "Español": "es",
    "Italiano": "it",
    "Tiếng Việt": "vi",
}


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
        batches = ["batch_001"]
    return batches


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


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    # UI Language selector at top
    ui_lang_choice = st.selectbox("🌐", list(UI_LANGS.keys()), key="ui_lang_select",
                                  label_visibility="collapsed")
    st.session_state["ui_lang_code"] = UI_LANGS[ui_lang_choice]

    st.title(t("title"))
    st.caption(t("subtitle"))
    st.divider()

    # Determine current page from session state override or radio
    nav_items = [
        t("nav_overview"),
        t("nav_query"),
        t("nav_content"),
        t("nav_optimize"),
        t("nav_publish"),
        t("nav_metrics"),
        t("nav_settings"),
    ]

    # Handle page jump from CTA buttons — set radio widget value directly
    if "jump_to_page" in st.session_state:
        idx = st.session_state.pop("jump_to_page")
        st.session_state["nav_radio"] = nav_items[idx]

    page = st.radio(
        "nav",
        nav_items,
        label_visibility="collapsed",
        key="nav_radio",
    )
    st.divider()

    batches = get_batches()
    selected_batch = st.selectbox(t("batch"), batches, key="batch")
    market = st.selectbox(t("market"), MARKETS, key="market")
    content_lang = st.selectbox(t("content_lang"), list(CONTENT_LANGUAGES.keys()), key="content_lang")
    kw_limit = st.number_input(t("kw_limit"), 1, 50, 10)

    st.divider()
    st.caption(f"Path: {BASE_PATH}")


# ============================================================
# PAGE: Overview
# ============================================================
if page == t("nav_overview"):
    st.title(t("nav_overview"))
    st.caption(f"Batch: {selected_batch} | Market: {market}")

    # --- Pipeline Progress ---
    st.subheader(t("pipeline_status"))
    batch_path = OUTPUT_PATH / selected_batch
    steps = [
        ("01_zhiku", "Query Gen", "📚"),
        ("02_zhizao", "Content Creation", "✍️"),
        ("03_zhiyou", "Optimization", "🔧"),
        ("04_zhibu", "Publishing", "📦"),
    ]
    cols = st.columns(4)
    for i, (folder, name, icon) in enumerate(steps):
        step_path = batch_path / folder
        with cols[i]:
            if step_path.exists() and any(step_path.iterdir()):
                files = list(step_path.glob("*.csv")) + list(step_path.glob("*.json"))
                st.success(f"{icon} **{name}**")
                st.caption(f"✅ {t('done')} · {len(files)} {t('files')}")
            else:
                st.warning(f"{icon} **{name}**")
                st.caption(f"⏳ {t('pending')}")

    st.divider()

    # --- Quick Actions ---
    st.subheader(t("quick_actions"))

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button(t("run_pipeline"), type="primary"):
            st.session_state["jump_to_page"] = 1  # Go to Step 1
            st.rerun()
    with col_b:
        st.markdown("**Pipeline Steps:**")
        st.markdown("""
        1. **Query Generation** — Expand keywords into AI-native search queries
        2. **Content Creation** — Generate SEO+GEO optimized articles
        3. **Optimization** — Score, rewrite, and compliance check
        4. **Publishing** — Format for distribution
        """)

    st.divider()

    # --- Output Files ---
    st.subheader(t("output_files"))
    if batch_path.exists():
        for step_dir in sorted(batch_path.iterdir()):
            if step_dir.is_dir():
                files = [f for f in step_dir.iterdir() if f.is_file()]
                if files:
                    with st.expander(f"{step_dir.name} — {len(files)} {t('files')}"):
                        for f in sorted(files):
                            size_kb = f.stat().st_size / 1024
                            col_info, col_btn = st.columns([3, 1])
                            with col_info:
                                st.caption(f"{f.name} ({size_kb:.1f} KB)")
                            with col_btn:
                                mime = "application/json" if f.suffix == ".json" else "text/csv"
                                st.download_button(
                                    "⬇️", f.read_bytes(),
                                    file_name=f.name, mime=mime,
                                    key=f"dl_{f.parent.name}_{f.stem}",
                                )
    else:
        st.caption(t("no_output"))


# ============================================================
# PAGE: Query Generation (Step 1)
# ============================================================
elif page == t("nav_query"):
    st.title(t("nav_query"))
    st.caption("Upload a keyword list, then generate AI-native search queries for each keyword")

    # --- Upload Keyword List ---
    st.subheader("📤 Upload Keyword List")

    uploaded_file = st.file_uploader(
        "Upload CSV with keywords (columns: keyword_id, Keyword, market, keyword_type, priority)",
        type=["csv", "tsv", "txt"],
        key="roa_kw_upload",
    )

    if uploaded_file:
        df_uploaded = pd.read_csv(uploaded_file, encoding="utf-8-sig")
        st.session_state["uploaded_keywords"] = df_uploaded
        st.success(f"✅ Uploaded {len(df_uploaded)} keywords")

    # Show current keywords (uploaded or from file)
    kw_path = INPUT_PATH / "seo_sem_keywords.csv"
    if "uploaded_keywords" in st.session_state:
        df_kw = st.session_state["uploaded_keywords"]
    elif kw_path.exists():
        df_kw = load_csv_safe(kw_path)
    else:
        df_kw = pd.DataFrame()

    if not df_kw.empty:
        # Filter by market
        if market != "ALL" and "market" in df_kw.columns:
            df_kw_filtered = df_kw[df_kw["market"] == market]
        else:
            df_kw_filtered = df_kw

        st.markdown(f"**{len(df_kw_filtered)} keywords** (Market: {market}, Limit: {kw_limit})")
        st.dataframe(df_kw_filtered.head(kw_limit), use_container_width=True, hide_index=True)

        # Save uploaded keywords to input folder
        if "uploaded_keywords" in st.session_state:
            ensure_dir(INPUT_PATH)
            df_kw.to_csv(INPUT_PATH / "seo_sem_keywords.csv", index=False, encoding="utf-8-sig")

        st.divider()

        # --- Generate Queries ---
        st.subheader("🚀 Generate AI Queries from Keywords")

        if st.button(t("gen_queries"), type="primary", key="roa_gen_q"):
            with st.spinner("Generating AI search queries from keyword list..."):
                try:
                    from engine import run_zhiku
                    result = run_zhiku(
                        batch_id=selected_batch,
                        market=market,
                        keyword_limit=kw_limit,
                    )
                    if result.get("success"):
                        st.success(f"✅ Generated queries for {result.get('keywords_processed', 0)} keywords → {result.get('query_count', 0)} total queries")
                        st.session_state["step1_done"] = True
                    else:
                        st.error(f"Failed: {result.get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error: {e}")
    else:
        st.info("👆 Upload a keyword CSV to get started. Required columns: `keyword_id`, `Keyword`, `market`, `keyword_type`, `priority`")

    # --- Show generated queries (editable) ---
    st.divider()
    st.subheader(t("existing_queries"))
    zhiku_path = OUTPUT_PATH / selected_batch / "01_zhiku" / "zhiku_ai_queries.csv"
    df_q = load_csv_safe(zhiku_path)
    if not df_q.empty:
        st.markdown("**Edit, add, or remove queries below.** Changes are saved automatically.")

        # Editable data table
        edited_df = st.data_editor(
            df_q,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",  # Allows adding/deleting rows
            key="roa_query_editor",
        )

        # Save button
        if st.button("💾 Save Changes", key="roa_save_queries"):
            ensure_dir(zhiku_path.parent)
            edited_df.to_csv(zhiku_path, index=False, encoding="utf-8-sig")
            st.success("✅ Queries saved!")
            st.rerun()

        # --- Next Step CTA ---
        st.divider()
        if st.button("✅ Queries ready → Go to Content Creation (Step 2)", type="primary", key="goto_step2"):
            # Save latest edits before moving on
            ensure_dir(zhiku_path.parent)
            edited_df.to_csv(zhiku_path, index=False, encoding="utf-8-sig")
            st.session_state["jump_to_page"] = 2
            st.rerun()
    else:
        st.caption(t("no_queries"))


# ============================================================
# PAGE: Content Creation (Step 2)
# ============================================================
elif page == t("nav_content"):
    st.title(t("nav_content"))
    st.caption("Generate SEO+GEO optimized articles from selected queries")

    content_limit = st.slider(t("articles_gen"), 1, 10, 5, key="roa_climit")

    if st.button(t("gen_content"), type="primary", key="roa_gen_c"):
        with st.spinner("Generating content..."):
            try:
                from engine import run_zhizao
                result = run_zhizao(selected_batch, content_limit=content_limit)
                if result.get("success"):
                    st.success(f"✅ Generated {result.get('articles_generated', 0)} articles")
                    st.session_state["step2_done"] = True
                else:
                    st.error(f"Failed: {result.get('error', '')}")
            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()

    # --- Generated Content: Download / Preview / Re-upload ---
    st.subheader(t("generated_articles"))
    zhizao_path = OUTPUT_PATH / selected_batch / "02_zhizao" / "zhizao_draft_content.csv"
    df_c = load_csv_safe(zhizao_path)

    if not df_c.empty:
        # Download section
        st.markdown("**📥 Download content for offline editing:**")
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv_bytes = df_c.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                "⬇️ Download CSV",
                csv_bytes,
                file_name=f"{selected_batch}_content_draft.csv",
                mime="text/csv",
                key="dl_content_csv",
            )
        with col_dl2:
            try:
                import io
                excel_buf = io.BytesIO()
                df_c.to_excel(excel_buf, index=False, engine="openpyxl")
                st.download_button(
                    "⬇️ Download Excel",
                    excel_buf.getvalue(),
                    file_name=f"{selected_batch}_content_draft.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="dl_content_xlsx",
                )
            except Exception:
                pass

        st.divider()

        # Upload modified version
        st.markdown("**📤 Upload modified content** (edit offline, then re-upload):")
        uploaded_content = st.file_uploader(
            "Upload edited CSV or Excel",
            type=["csv", "xlsx"],
            key="roa_content_upload",
        )
        if uploaded_content:
            try:
                if uploaded_content.name.endswith(".xlsx"):
                    df_uploaded = pd.read_excel(uploaded_content, engine="openpyxl")
                else:
                    df_uploaded = pd.read_csv(uploaded_content, encoding="utf-8-sig")
                # Save back
                ensure_dir(zhizao_path.parent)
                df_uploaded.to_csv(zhizao_path, index=False, encoding="utf-8-sig")
                st.success(f"✅ Uploaded & saved {len(df_uploaded)} articles")
                st.rerun()
            except Exception as e:
                st.error(f"Upload failed: {e}")

        st.divider()

        # Preview articles
        st.markdown("**📖 Preview:**")
        for idx, row in df_c.iterrows():
            with st.expander(f"📄 {row.get('title', f'Article {idx+1}')}"):
                st.markdown(f"**Query:** {row.get('ai_query', '')}")
                st.markdown(f"**Word Count:** {row.get('word_count', 'N/A')}")
                content = str(row.get("content_draft", ""))
                st.markdown(content[:2000] + ("..." if len(content) > 2000 else ""))

        # --- Next Step CTA ---
        st.divider()
        if st.button("✅ Content ready → Go to Optimization (Step 3)", type="primary", key="goto_step3"):
            st.session_state["jump_to_page"] = 3
            st.rerun()
    else:
        st.caption(t("no_content"))


# ============================================================
# PAGE: Optimization (Step 3)
# ============================================================
elif page == t("nav_optimize"):
    st.title(t("nav_optimize"))
    st.caption("One-click: Score → Rewrite → Compliance Check (all automated)")

    st.markdown("""
    **This step runs 3 sub-steps automatically:**
    1. 📊 **Score** — AI Citation Probability Scoring (5 dimensions)
    2. ✍️ **Rewrite** — Optimize content based on scoring feedback
    3. ⚖️ **Compliance** — WW legal/brand compliance check & auto-fix
    """)

    # Single button to run all 3 steps
    if st.button("🚀 Run Full Optimization (Score → Rewrite → Compliance)", type="primary", key="roa_optimize_all"):
        progress = st.progress(0, text="Starting optimization...")

        # Step 3.1: Score
        progress.progress(0.1, text="📊 Step 1/3: Scoring content...")
        try:
            from engine import run_zhiyou_score, run_zhiyou_execute, run_zhiyou_compliance

            result_score = run_zhiyou_score(selected_batch)
            if result_score.get("success"):
                st.success(f"📊 Scored {result_score.get('articles_scored', 0)} articles")
            else:
                st.error(f"Scoring failed: {result_score.get('error', '')}")
                st.stop()

            # Step 3.2: Rewrite
            progress.progress(0.4, text="✍️ Step 2/3: Rewriting content...")
            result_rewrite = run_zhiyou_execute(selected_batch)
            if result_rewrite.get("success"):
                st.success(f"✍️ Rewrote {result_rewrite.get('articles_rewritten', 0)} articles")
            else:
                st.error(f"Rewrite failed: {result_rewrite.get('error', '')}")
                st.stop()

            # Step 3.3: Compliance
            progress.progress(0.75, text="⚖️ Step 3/3: Compliance check...")
            result_comp = run_zhiyou_compliance(selected_batch)
            if result_comp.get("success"):
                st.success("⚖️ Compliance check passed")
            else:
                st.error(f"Compliance failed: {result_comp.get('error', '')}")
                st.stop()

            progress.progress(1.0, text="✅ All optimization steps complete!")
            st.session_state["step3_done"] = True

        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()

    # --- Show Results ---
    st.subheader("📋 Results")

    # Scorecard
    score_path = OUTPUT_PATH / selected_batch / "03_zhiyou" / "zhiyou_scorecard.csv"
    df_sc = load_csv_safe(score_path)
    if not df_sc.empty:
        with st.expander(f"📊 Scorecard ({len(df_sc)} articles)", expanded=False):
            st.dataframe(df_sc, use_container_width=True, hide_index=True)

    # Optimized content
    opt_path = OUTPUT_PATH / selected_batch / "03_zhiyou" / "zhiyou_optimized_content.csv"
    df_opt = load_csv_safe(opt_path)
    if not df_opt.empty:
        with st.expander(f"✍️ Optimized Content ({len(df_opt)} articles)", expanded=False):
            st.dataframe(df_opt, use_container_width=True, hide_index=True)

    # Compliance
    comp_path = OUTPUT_PATH / selected_batch / "03_zhiyou" / "zhiyou_compliance_checked.csv"
    df_comp = load_csv_safe(comp_path)
    if not df_comp.empty:
        with st.expander(f"⚖️ Compliance Results ({len(df_comp)} articles)", expanded=False):
            st.dataframe(df_comp, use_container_width=True, hide_index=True)

    # --- Next Step CTA ---
    if df_sc.empty and df_opt.empty and df_comp.empty:
        st.caption("Click the button above to run optimization.")
    else:
        st.divider()
        if st.button("✅ Optimization done → Go to Publishing (Step 4)", type="primary", key="goto_step4"):
            st.session_state["jump_to_page"] = 4
            st.rerun()


# ============================================================
# PAGE: Publishing (Step 4)
# ============================================================
elif page == t("nav_publish"):
    st.title(t("nav_publish"))
    st.caption("Format content for distribution")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(t("gen_json"), type="primary", key="roa_json"):
            st.info("Generates structured JSON from optimized content")
    with col2:
        if st.button(t("gen_word"), key="roa_word"):
            with st.spinner("Generating Word docs..."):
                try:
                    from engine import generate_word_docs
                    docs = generate_word_docs(selected_batch)
                    if docs:
                        st.success(f"✅ Generated {len(docs)} Word documents")
                        for fname, fbytes in docs:
                            st.download_button(
                                f"⬇️ {fname}", fbytes, file_name=fname,
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"dl_word_{fname}",
                            )
                    else:
                        st.warning(t("no_word"))
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- Next Step CTA ---
    st.divider()
    if st.button("📈 View Metrics & Analytics", type="primary", key="goto_metrics"):
        st.session_state["jump_to_page"] = 5  # Metrics
        st.rerun()


# ============================================================
# PAGE: Metrics & Analytics
# ============================================================
elif page == t("nav_metrics"):
    st.title(t("nav_metrics"))
    st.caption("GEO performance tracking — WW markets only")

    # --- Upload Metrics Data ---
    st.subheader("📤 Upload Metrics Data")
    metrics_upload = st.file_uploader(
        "Upload weekly metrics CSV or Excel (from QuickSight / SSR dashboard)",
        type=["csv", "xlsx"],
        key="roa_metrics_upload",
    )

    METRICS_DIR = OUTPUT_PATH / "metrics"
    ensure_dir(METRICS_DIR)
    metrics_file = METRICS_DIR / "roa_weekly_metrics.csv"

    if metrics_upload:
        try:
            if metrics_upload.name.endswith(".xlsx"):
                df_metrics_new = pd.read_excel(metrics_upload, engine="openpyxl")
            else:
                df_metrics_new = pd.read_csv(metrics_upload, encoding="utf-8-sig")
            df_metrics_new.to_csv(metrics_file, index=False, encoding="utf-8-sig")
            st.success(f"✅ Uploaded {len(df_metrics_new)} rows of metrics data")
        except Exception as e:
            st.error(f"Upload failed: {e}")

    # Load saved metrics
    df_metrics = load_csv_safe(metrics_file)

    st.divider()

    # --- Tabs: Weekly / Monthly / YTD / Input / Learnings & Opportunities ---
    tab_weekly, tab_monthly, tab_ytd, tab_input, tab_learnings = st.tabs([
        "📅 Weekly", "📆 Monthly", "📊 YTD", "📥 Input", "💡 Learnings & Opp"
    ])

    # ---- TAB: Weekly ----
    with tab_weekly:
        st.subheader("📅 Weekly Trend")

        if not df_metrics.empty:
            st.dataframe(df_metrics, use_container_width=True, hide_index=True)
        else:
            # Default hardcoded data
            weeks = [f"WK{i}" for i in range(8, 23)]
            direct_na = [714, 1099, 1334, 1436, 1456, 1331, 1339, 1432, 1476, 1102, 1241, 1599, 1723, 1441, 0]
            direct_eu = [179, 231, 250, 273, 272, 244, 182, 265, 211, 177, 163, 235, 264, 237, 0]
            direct_jp = [30, 69, 58, 42, 79, 59, 59, 54, 52, 51, 49, 82, 66, 64, 0]

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=weeks, y=direct_na, mode="lines+markers", name="NA Direct"))
            fig.add_trace(go.Scatter(x=weeks, y=direct_eu, mode="lines+markers", name="EU Direct"))
            fig.add_trace(go.Scatter(x=weeks, y=direct_jp, mode="lines+markers", name="JP Direct"))
            fig.update_layout(title="WW Direct Regstart by Market", xaxis_title="Week", yaxis_title="Reg Starts")
            st.plotly_chart(fig, use_container_width=True)

    # ---- TAB: Monthly ----
    with tab_monthly:
        st.subheader("📆 Monthly Summary")

        monthly_data = pd.DataFrame({
            "Market": ["NA", "EU", "JP"],
            "Jan": [3878, 765, 322],
            "Feb": [1809, 449, 131],
            "Mar": [5875, 1123, 271],
            "Apr": [5993, 962, 250],
            "May (MTD)": [6141, 919, 263],
        })
        st.dataframe(monthly_data, use_container_width=True, hide_index=True)

        st.caption("Source: SSR Funnel Metrics — Organic → WW Website → Direct")

    # ---- TAB: YTD ----
    with tab_ytd:
        st.subheader("📊 YTD Performance")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("WW GEO (Regstart YTD)", "364", "+94% YoY")
        with col2:
            st.metric("WW Direct EST (YTD)", "29,151", "+66% YoY")
        with col3:
            st.metric("Clean Launch Direct", "5,457", "+132% YoY")
        with col4:
            st.metric("Conversion Rate", "18.7%", "+532 bps")

        st.divider()

        market_data = pd.DataFrame({
            "Market": ["NA", "EU", "JP"],
            "GEO Regstart YTD": [353, 27, 11],
            "GEO YoY": ["+77%", "+200%", "+450%"],
            "Direct Regstart YTD": [23696, 4218, 1237],
            "Direct YoY": ["+67%", "+52%", "+102%"],
            "Clean Launch Direct YTD": [4146, 1137, 174],
            "CL Direct YoY": ["+134%", "+134%", "+78%"],
            "Conversion Rate": ["17.5%", "27.0%", "14.1%"],
        })
        st.dataframe(market_data, use_container_width=True, hide_index=True)

        st.divider()
        st.markdown("**Regstart to Clean Launch Funnel (WW)**")
        funnel_data = pd.DataFrame({
            "Stage": ["Regstart", "Reg Complete", "SIV Pass", "Tax Interview", "KYC Pass", "Chargenow", "RTL", "Clean Launch"],
            "NA YTD": [23696, "~20K", "~15K", "~12K", "~10K", "~8K", "~6K", 4146],
            "EU YTD": [4218, "~3.5K", "~2.5K", "~2K", "~1.8K", "~1.5K", "~1.3K", 1137],
            "JP YTD": [1237, "~1K", "~800", "~600", "~500", "~400", "~350", 174],
        })
        st.dataframe(funnel_data, use_container_width=True, hide_index=True)

    # ---- TAB: Input ----
    with tab_input:
        st.subheader("📥 Input Activities")

        input_metrics_file = METRICS_DIR / "roa_input_activities.csv"
        df_input = load_csv_safe(input_metrics_file)

        # Upload input activities
        input_upload = st.file_uploader(
            "Upload Input Activities CSV (managed queries, content published, etc.)",
            type=["csv", "xlsx"],
            key="roa_input_upload",
        )
        if input_upload:
            try:
                if input_upload.name.endswith(".xlsx"):
                    df_input_new = pd.read_excel(input_upload, engine="openpyxl")
                else:
                    df_input_new = pd.read_csv(input_upload, encoding="utf-8-sig")
                df_input_new.to_csv(input_metrics_file, index=False, encoding="utf-8-sig")
                st.success(f"✅ Uploaded {len(df_input_new)} rows")
                df_input = df_input_new
            except Exception as e:
                st.error(f"Upload failed: {e}")

        if not df_input.empty:
            st.dataframe(df_input, use_container_width=True, hide_index=True)
        else:
            st.markdown("""
            **Suggested columns:**
            - `week` — WK number
            - `managed_queries` — # of search phrases managed
            - `content_created` — # articles created
            - `content_published` — # articles published
            - `ai_engines_covered` — # AI engines with coverage
            - `keyword_coverage_change` — % change in keyword coverage
            """)
            st.caption("Upload a CSV with your input activities data.")

    # ---- TAB: Learnings & Opportunities ----
    with tab_learnings:
        st.subheader("💡 Learnings & Opportunities")

        st.markdown("""
        **🔍 Gaps:**
        - WW GEO absolute value still small (YTD 364) — most AI search traffic doesn't carry referrer
        - EM markets (AE) Direct declining (-61% YoY)
        - Input activity tracking not yet fully established for ROA markets
        - EU/JP GEO coverage remains limited in absolute numbers

        **📚 Learnings:**
        - WW Direct EST +66% YoY vs SSR benchmark -23% — indirect attribution logic validated
        - JP shows fastest growth trajectory (Direct +102% YoY) — AI search penetration accelerating in Japan
        - NA Direct remains largest absolute contributor (+9,918 incremental Reg Starts YTD)
        - Content published 2-3 weeks prior correlates with Direct traffic spikes (lag effect)

        **🚀 Opportunities:**
        - Increase EU/JP search phrase coverage (GEO absolute values still low)
        - Investigate AE Direct decline — potential content gap or market shift
        - Build AU market content strategy (currently underserved)
        - Establish weekly input activity tracking to strengthen attribution chain
        - Expand content coverage for emerging markets (SA, AU)
        - Test multi-language content (DE, FR, IT) for EU market expansion
        """)


# ============================================================
# PAGE: Settings
# ============================================================
elif page == t("nav_settings"):
    st.title(t("nav_settings"))

    st.subheader(t("settings_creds"))
    st.markdown("Configure AWS Bedrock access for content generation.")

    with st.form("aws_creds_form"):
        access_key = st.text_input("AWS Access Key ID", type="password")
        secret_key = st.text_input("AWS Secret Access Key", type="password")
        session_token = st.text_input("AWS Session Token (optional)", type="password")
        region = st.selectbox("Region", ["us-east-1", "us-west-2", "eu-west-1"])

        if st.form_submit_button(t("save")):
            if access_key and secret_key:
                st.session_state["aws_creds"] = {
                    "access_key_id": access_key,
                    "secret_access_key": secret_key,
                    "session_token": session_token if session_token else None,
                    "region": region,
                }
                st.success("✅ Credentials saved for this session")
            else:
                st.warning("Please provide Access Key ID and Secret Access Key")

    st.divider()

    st.subheader(t("settings_api"))
    st.markdown("Configure API keys for real AI platform calls during simulation.")

    with st.form("api_keys_form"):
        openai_key = st.text_input("OpenAI API Key", type="password",
                                   value=os.environ.get("OPENAI_API_KEY", ""))
        gemini_key = st.text_input("Gemini API Key", type="password",
                                   value=os.environ.get("GEMINI_API_KEY", ""))

        if st.form_submit_button(t("save")):
            if openai_key:
                os.environ["OPENAI_API_KEY"] = openai_key
            if gemini_key:
                os.environ["GEMINI_API_KEY"] = gemini_key
            st.success("✅ API keys saved for this session")

    st.divider()
    st.subheader(t("about"))
    st.markdown("""
    **Smart Suite ROA Edition**
    
    Tailored for ROA teams:
    - NA (North America), EU (Europe), JP (Japan)
    - Emerging markets: AU, AE, SA
    
    **What's excluded (CN-specific):**
    - CN AI platforms (DeepSeek, Doubao, Kimi, Yuanbao, Qianwen)
    - CN legal compliance (广告法, 反不正当竞争法, etc.)
    - CN Website channel data
    - CN content intake workflow
    """)
