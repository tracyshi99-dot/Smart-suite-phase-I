"""
Smart Suite — AI Search Simulation Console (智测操作台)
独立界面，可自定义检索短语、选择平台、编辑问题、逐条或批量执行
Run: streamlit run app_zhice.py --server.port 8503
"""
import streamlit as st
import pandas as pd
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

# Load env
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

OUTPUT_PATH = Path(__file__).parent.parent / "output"
ZHICE_DIR = OUTPUT_PATH / "zhice"
ZHICE_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Smart Suite — AI Search Console", page_icon="🔬", layout="wide")

st.markdown("""
<style>
.main .block-container { padding-top: 1rem; padding-left: 1rem; padding-right: 1rem; max-width: 100%; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""<div style="padding:16px 0 8px;">
<h1 style="font-size:28px;font-weight:800;color:#00bcd4;margin:0;">🔬 Smart Suite — Request & Testing Console</h1>
<p style="color:#8892b0;font-size:13px;margin-top:6px;">Submit content requests, test AI search visibility, and track citation gaps</p>
</div>""", unsafe_allow_html=True)

with st.expander("ℹ️ What is this tool? How to use it?", expanded=False):
    st.markdown("""
**What:** This is Smart Suite's public-facing console for submitting GEO content requests and testing AI search visibility.

**Who:** For all team members (Product, Marketing, Content, Operations) who want to:
- Request new content to be created for their product/topic
- Test how AI search engines (Qianwen, DeepSeek, Kimi, ChatGPT, etc.) respond to specific queries
- Check if our official content is being cited by AI platforms

**How to use:**
1. **Submit Request** — Enter your product/topic → We'll create GEO-optimized content for it
2. **Single Query** — Test one search phrase across AI platforms → See what AI returns
3. **Batch Test** — Test multiple phrases at once → Get coverage report
4. **History** — View past test results

**What happens after you submit:**
- Your request enters the production pipeline (智库→智造→智优→智布)
- You can track progress in the dashboard
- Content will be published after quality review
""")

# Login
if "user_login" not in st.session_state:
    st.session_state["user_login"] = ""

user_login = st.text_input("👤 Your Login / Name", value=st.session_state.get("user_login", ""), key="login_input", placeholder="e.g. yujiashi, joyce, murphy")
if user_login:
    st.session_state["user_login"] = user_login

# Platform options
PLATFORMS = {
    "qianwen": "通义千问 (Qianwen)",
    "deepseek": "DeepSeek",
    "kimi": "Kimi (Moonshot)",
    "doubao": "豆包 (Doubao)",
    "chatgpt": "ChatGPT (OpenAI)",
    "gemini": "Gemini (Google)",
}

# Shared intake file
INTAKE_FILE = OUTPUT_PATH / "intake_requests.csv"

def load_intake():
    if INTAKE_FILE.exists():
        return pd.read_csv(INTAKE_FILE, encoding="utf-8-sig")
    return pd.DataFrame(columns=["id", "submitter", "product", "description", "market", "priority", "status", "submitted_at"])

def save_intake(df):
    INTAKE_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(INTAKE_FILE, index=False, encoding="utf-8-sig")

# Tabs
tab_simulate, tab_dashboard, tab_history = st.tabs(["🔬 AI Simulation", "📊 Dashboard", "📜 History"])

with tab_simulate:
    st.markdown("### 🔬 AI Search Simulation")
    st.caption("Configure simulation → Review generated queries → Confirm → Execute → View results")

    # Step 1: Configuration
    col_config, col_preview = st.columns([1, 1.5])

    with col_config:
        st.markdown("**Configuration**")
        topic = st.text_input("Topic / Product", placeholder="e.g. Amazon FBA", key="sim_topic")
        sim_platforms = st.multiselect("AI Platforms", list(PLATFORMS.keys()),
                                       default=["qianwen"],
                                       format_func=lambda x: PLATFORMS[x],
                                       key="sim_platforms")
        num_rounds = st.slider("Number of questions", 1, 10, 5, key="sim_rounds")

        if st.button("🎯 Generate Questions", key="gen_questions"):
            if topic:
                # Generate simulated questions
                base_queries = [
                    f"{topic}是什么？",
                    f"{topic}怎么使用？",
                    f"{topic}费用多少？",
                    f"{topic}有什么优势？",
                    f"{topic}和竞品有什么区别？",
                    f"{topic}常见问题有哪些？",
                    f"中国卖家如何使用{topic}？",
                    f"{topic}新手入门指南",
                    f"{topic}最新政策变化",
                    f"{topic}操作流程详解",
                ]
                st.session_state["sim_queries"] = base_queries[:num_rounds]

    with col_preview:
        if "sim_queries" in st.session_state and st.session_state["sim_queries"]:
            st.markdown("**Generated Questions (editable):**")
            edited_queries = []
            for i, q in enumerate(st.session_state["sim_queries"]):
                edited = st.text_input(f"Q{i+1}", value=q, key=f"sim_q_{i}")
                edited_queries.append(edited)
            st.session_state["sim_queries_final"] = edited_queries

            st.divider()
            if st.button("✅ Confirm & Execute", type="primary", key="confirm_execute"):
                st.session_state["sim_running"] = True

    # Step 2: Execute and show results
    if st.session_state.get("sim_running") and st.session_state.get("sim_queries_final"):
        st.divider()
        st.markdown("### 📋 Results")

        from zhice_engine import REAL_API_MAP
        queries = st.session_state["sim_queries_final"]
        platforms = st.session_state.get("sim_platforms", ["qianwen"])

        all_results = []
        progress = st.progress(0)
        total = len(queries) * len(platforms)
        done = 0

        for query in queries:
            for platform in platforms:
                api_func = REAL_API_MAP.get(platform)
                if api_func:
                    try:
                        r = api_func(query)
                        answer = r.get("full_answer", "")
                        has_gs = "gs.amazon" in answer.lower() or "globalselling" in answer.lower()
                        has_brand = "全球开店" in answer or "Global Selling" in answer or "亚马逊" in answer
                        # Check for negative sentiment
                        negative_words = ["风险", "骗局", "亏损", "不推荐", "不建议", "缺点", "劣势", "差评", "投诉"]
                        has_negative = any(w in answer for w in negative_words)
                        all_results.append({
                            "query": query,
                            "platform": platform,
                            "answer": answer,
                            "answer_length": len(answer),
                            "has_official_link": has_gs,
                            "has_brand_mention": has_brand,
                            "has_negative": has_negative,
                        })
                    except Exception as e:
                        all_results.append({"query": query, "platform": platform, "error": str(e), "answer": ""})
                done += 1
                progress.progress(done / total)
                time.sleep(0.5)

        progress.progress(1.0)
        st.session_state["sim_running"] = False

        # Save results
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        topic_safe = st.session_state.get("sim_topic", "unknown").replace(" ", "_")[:20]
        out_file = ZHICE_DIR / f"sim_{topic_safe}_{ts}.json"
        out_file.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding='utf-8')

        # Display results
        for r in all_results:
            if "error" in r:
                st.error(f"**{r['query']}** ({r['platform']}): {r['error']}")
            else:
                with st.expander(f"{'✅' if r['has_official_link'] else '❌'} {r['query']} — {PLATFORMS.get(r['platform'], r['platform'])} ({r['answer_length']} chars)"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Official Link", "✅" if r["has_official_link"] else "❌")
                    c2.metric("Brand Mention", "✅" if r["has_brand_mention"] else "❌")
                    c3.metric("Negative Content", "⚠️" if r["has_negative"] else "✅ Clean")
                    st.markdown(r["answer"])

        st.success(f"✅ Saved to: {out_file.name}")

with tab_dashboard:
    st.markdown("### 📊 Citation Monitoring Dashboard")
    st.caption("Aggregated results from all simulation runs")

    if ZHICE_DIR.exists():
        all_files = sorted(ZHICE_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        if all_files:
            # Aggregate all results
            all_data = []
            for f in all_files[:20]:  # Last 20 runs
                try:
                    with open(f, encoding="utf-8") as fh:
                        data = json.load(fh)
                    if isinstance(data, list):
                        all_data.extend(data)
                    elif isinstance(data, dict) and "results" in data:
                        for rd in data["results"]:
                            if "results" in rd:
                                for p, rv in rd["results"].items():
                                    if isinstance(rv, dict) and "answer_length" in rv:
                                        rv["platform"] = p
                                        all_data.append(rv)
                except Exception:
                    pass

            if all_data:
                total = len(all_data)
                with_link = sum(1 for r in all_data if r.get("has_official_link"))
                with_brand = sum(1 for r in all_data if r.get("has_brand_mention"))
                with_negative = sum(1 for r in all_data if r.get("has_negative"))

                # KPIs
                kc1, kc2, kc3, kc4 = st.columns(4)
                kc1.metric("Total Queries Tested", total)
                kc2.metric("Official Link Citation", f"{with_link}/{total} ({with_link*100//total if total else 0}%)")
                kc3.metric("Brand Mentioned", f"{with_brand}/{total} ({with_brand*100//total if total else 0}%)")
                kc4.metric("Negative Content Found", f"{with_negative}/{total}")

                st.divider()

                # Negative samples
                if with_negative > 0:
                    st.markdown("#### ⚠️ Negative Content Samples")
                    st.caption("Answers containing potentially negative mentions about our product/brand")
                    neg_samples = [r for r in all_data if r.get("has_negative")][:5]
                    for ns in neg_samples:
                        with st.expander(f"⚠️ {ns.get('query', 'N/A')} ({ns.get('platform', '')})"):
                            st.markdown(ns.get("answer", ns.get("answer_preview", "")))

                st.divider()

                # Gap analysis
                st.markdown("#### ❌ Citation Gaps — No Official Link")
                gap_samples = [r for r in all_data if not r.get("has_official_link") and r.get("query")][:10]
                if gap_samples:
                    df_gaps = pd.DataFrame(gap_samples)
                    show_cols = [c for c in ["query", "platform", "answer_length"] if c in df_gaps.columns]
                    if show_cols:
                        st.dataframe(df_gaps[show_cols], use_container_width=True, hide_index=True)
                else:
                    st.success("No gaps found — all queries have official link citation!")
            else:
                st.info("No aggregated data available yet. Run some simulations first.")
        else:
            st.info("No test runs yet. Go to AI Simulation tab to start testing.")
    else:
        st.info("No test data yet.")

with tab_history:
    st.markdown("### Test History")
    if ZHICE_DIR.exists():
        files = sorted(ZHICE_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        if files:
            selected = st.selectbox("Select test run", [f.stem for f in files], key="hist_select")
            sel_path = ZHICE_DIR / f"{selected}.json"
            if sel_path.exists():
                with open(sel_path, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    results_list = data
                else:
                    results_list = [data]

                total = len(results_list)
                with_link = sum(1 for r in results_list if r.get("has_official_link"))
                kc1, kc2, kc3 = st.columns(3)
                kc1.metric("Queries", total)
                kc2.metric("Official Link", f"{with_link}/{total}")
                kc3.metric("Coverage", f"{with_link*100//total if total else 0}%")

                df_h = pd.DataFrame(results_list)
                show_cols = [c for c in ["query", "platform", "answer_length", "has_official_link", "has_brand_mention"] if c in df_h.columns]
                if show_cols:
                    df_hs = df_h[show_cols].copy()
                    if "has_official_link" in df_hs.columns:
                        df_hs["has_official_link"] = df_hs["has_official_link"].apply(lambda x: "✅" if x else "❌")
                    if "has_brand_mention" in df_hs.columns:
                        df_hs["has_brand_mention"] = df_hs["has_brand_mention"].apply(lambda x: "✅" if x else "❌")
                    st.dataframe(df_hs, use_container_width=True, hide_index=True)

                with st.expander("View Full Answers"):
                    for r in results_list:
                        st.markdown(f"**{r.get('query', '')}** ({r.get('platform', '')})")
                        st.markdown(r.get("answer", r.get("answer_preview", r.get("full_answer", ""))))
                        st.divider()
        else:
            st.info("No test history yet.")
    else:
        st.info("No test history yet.")
