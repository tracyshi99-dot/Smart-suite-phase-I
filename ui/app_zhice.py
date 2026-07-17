"""
Smart Suite — Closed-Loop Tracking Console (闭环追踪操作台)
团队操作界面：智测→机会→内容→发布→效果 完整闭环
可引用 8501 主控台已有的测试结果和内容产出
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
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Smart Suite — Closed-Loop Console", page_icon="🔄", layout="wide")

st.markdown("""
<style>
.main .block-container { padding-top: 1rem; padding-left: 1rem; padding-right: 1rem; max-width: 100%; }
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1a1d2e 0%, #12131a 100%);
    border: 1px solid #2a2f4a; border-radius: 10px; padding: 12px 16px;
}
div[data-testid="stMetric"] label { color: #8892b0 !important; font-size: 12px !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #00bcd4 !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# --- Platform options ---
PLATFORMS = {
    "qianwen": "通义千问 (Qianwen)",
    "deepseek": "DeepSeek",
    "kimi": "Kimi (Moonshot)",
    "doubao": "豆包 (Doubao)",
    "chatgpt": "ChatGPT (OpenAI)",
    "gemini": "Gemini (Google)",
}


# --- Helper functions ---
def load_csv_safe(path: Path):
    if path.exists():
        try:
            df = pd.read_csv(path, encoding="utf-8-sig", on_bad_lines="skip")
            return df
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


def get_batches():
    batches = []
    if OUTPUT_PATH.exists():
        for d in sorted(OUTPUT_PATH.iterdir(), reverse=True):
            if d.is_dir() and d.name.startswith("batch_"):
                batches.append(d.name)
    return batches if batches else ["batch_003"]


def load_zhice_results():
    """Load all zhice test results from output/zhice/"""
    results = []
    if ZHICE_DIR.exists():
        for f in sorted(ZHICE_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                results.append({"file": f.name, "data": data, "mtime": f.stat().st_mtime,
                                "date": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")})
            except Exception:
                pass
    return results


def log_action(user, action, details=""):
    """Log user action for audit trail"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = LOGS_DIR / "audit.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{ts} | USER={user} | ACTION={action} | {details}\n")


# --- Header ---
st.markdown("""<div style="padding:16px 0 8px;">
<h1 style="font-size:28px;font-weight:800;color:#00bcd4;margin:0;">🔄 Smart Suite — 闭环追踪操作台</h1>
<p style="color:#8892b0;font-size:13px;margin-top:6px;">智测发现 → 机会点 → 内容产出 → 发布情况 → 效果对比 → 总结</p>
</div>""", unsafe_allow_html=True)

# Login
col_login, col_batch = st.columns([1, 1])
with col_login:
    user_login = st.text_input("👤 Your Name", value=st.session_state.get("user_login", ""),
                               key="login_input", placeholder="e.g. yujiashi")
    if user_login:
        st.session_state["user_login"] = user_login
with col_batch:
    batches = get_batches()
    selected_batch = st.selectbox("📦 Batch", batches, key="batch_select")

st.divider()

# --- Tabs ---
tab_loop, tab_test, tab_detail, tab_history = st.tabs([
    "🔄 闭环看板", "🔬 执行测试", "📋 详情", "📜 历史"
])


# ============================================================
# TAB: 闭环看板
# ============================================================
with tab_loop:
    # Load all data (shared with 8501)
    zhice_results = load_zhice_results()

    # Load content from main pipeline (produced via 8501)
    zhizao_file = OUTPUT_PATH / selected_batch / "02_zhizao" / "zhizao_draft_content.csv"
    df_content = load_csv_safe(zhizao_file)

    opt_file = OUTPUT_PATH / selected_batch / "03_zhiyou" / "zhiyou_optimized_content.csv"
    df_optimized = load_csv_safe(opt_file)

    # --- KPI Row ---
    st.markdown("### 📊 Pipeline Status")
    kc1, kc2, kc3, kc4, kc5 = st.columns(5)

    test_count = len(zhice_results)
    total_queries_tested = 0
    gaps_found = 0
    for r in zhice_results:
        data = r["data"]
        if isinstance(data, list):
            total_queries_tested += len(data)
            gaps_found += sum(1 for item in data
                             if not item.get("has_official_link", False)
                             and not item.get("has_amazon_cn", False))

    content_produced = len(df_content) if not df_content.empty else 0
    content_optimized = len(df_optimized) if not df_optimized.empty else 0

    kc1.metric("智测次数", test_count)
    kc2.metric("短语测试", total_queries_tested)
    kc3.metric("发现缺口", gaps_found)
    kc4.metric("内容产出", content_produced)
    kc5.metric("优化完成", content_optimized)

    st.divider()

    # ===== STEP 1: 智测发现 =====
    st.markdown("### 🔍 Step 1: 智测发现 — 之前表现")
    st.caption("AI 平台对目标短语的回答中，我们内容的覆盖情况（引用自 8501 测试结果）")

    if zhice_results:
        latest = zhice_results[0]
        latest_data = latest["data"]
        st.caption(f"📄 Latest: {latest['file']} ({latest['date']})")

        if isinstance(latest_data, list):
            df_test = pd.DataFrame([{
                "Query": item.get("query", ""),
                "Platform": PLATFORMS.get(item.get("platform", ""), item.get("platform", "")),
                "Official Link": "✅" if item.get("has_official_link", False) else "❌",
                "Brand Mention": "✅" if item.get("has_brand_mention", False) else "❌",
                "Status": "✅ Covered" if (item.get("has_official_link", False) or item.get("has_amazon_cn", False)) else "⚠️ Gap",
            } for item in latest_data])
            st.dataframe(df_test, use_container_width=True, hide_index=True)

            gap_count = len(df_test[df_test["Status"] == "⚠️ Gap"])
            covered_count = len(df_test[df_test["Status"] == "✅ Covered"])
            coverage_rate = covered_count / len(df_test) * 100 if len(df_test) > 0 else 0
            col_s1, col_s2, col_s3 = st.columns(3)
            col_s1.metric("覆盖率", f"{coverage_rate:.0f}%")
            col_s2.metric("缺口数", gap_count)
            col_s3.metric("已覆盖", covered_count)
        elif isinstance(latest_data, dict):
            st.json(latest_data)
    else:
        st.info("暂无智测结果。请在「执行测试」标签页运行，或在 8501 主控台执行智测。")

    st.divider()

    # ===== STEP 2: 机会点与建议 =====
    st.markdown("### 💡 Step 2: 机会点与建议")
    st.caption("基于智测缺口，发现的改善机会")

    if zhice_results:
        all_gaps = []
        for r in zhice_results:
            data = r["data"]
            if isinstance(data, list):
                for item in data:
                    if not item.get("has_official_link", False) and not item.get("has_amazon_cn", False):
                        all_gaps.append({
                            "Query": item.get("query", ""),
                            "Platform": PLATFORMS.get(item.get("platform", ""), item.get("platform", "")),
                            "问题": "回答中无官方链接/品牌提及",
                            "建议动作": "产出针对性 GEO 内容",
                            "Source": r["file"],
                        })
        if all_gaps:
            df_gaps = pd.DataFrame(all_gaps[:30])
            st.dataframe(df_gaps, use_container_width=True, hide_index=True)
            st.caption(f"显示前 30 个缺口（共 {len(all_gaps)} 个）")
        else:
            st.success("✅ 未发现缺口 — 覆盖良好！")
    else:
        st.info("执行智测以发现机会点。")

    st.divider()

    # ===== STEP 3: 内容产出与发布（引用 8501 产出） =====
    st.markdown("### ✍️ Step 3: 内容产出与发布")
    st.caption(f"引用自主控台的产出 + 可直接生产新内容 — Batch: {selected_batch}")

    if not df_content.empty:
        # Status summary
        display_cols = [c for c in ["content_id", "ai_query", "title", "word_count", "version"]
                       if c in df_content.columns]
        if display_cols:
            df_show = df_content[display_cols].copy()
            if not df_optimized.empty and "ai_query" in df_optimized.columns:
                optimized_queries = set(df_optimized["ai_query"].dropna().astype(str))
                df_show["Status"] = df_show["ai_query"].apply(
                    lambda q: "✅ 已优化" if str(q) in optimized_queries else "⏳ 草稿"
                ) if "ai_query" in df_show.columns else "⏳ 草稿"
            else:
                df_show["Status"] = "⏳ 草稿"
            st.dataframe(df_show, use_container_width=True, hide_index=True)

        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("已产出", content_produced)
        col_p2.metric("已优化", content_optimized)
        # Check confirmed
        confirmed_count = 0
        if not df_optimized.empty and "confirmed" in df_optimized.columns:
            confirmed_count = len(df_optimized[df_optimized["confirmed"].astype(str).str.upper().isin(["TRUE", "1"])])
        col_p3.metric("确认发布", confirmed_count)
    else:
        st.info("暂无产出内容。")

    # --- Quick Production Panel ---
    st.divider()
    st.markdown("**🚀 快速生产（基于智测缺口）**")
    st.caption("选择数量 → 一键生产 → 自动优化")

    col_prod1, col_prod2, col_prod3 = st.columns(3)
    with col_prod1:
        prod_count = st.number_input("生产篇数", 1, 10, 3, key="prod_count_8503")
    with col_prod2:
        prod_template = st.selectbox("模板", ["auto", "none", "registration", "fees", "logistics"],
                                     format_func=lambda x: {"auto": "智能匹配", "none": "无模板",
                                                            "registration": "注册流程", "fees": "费用成本",
                                                            "logistics": "物流仓储"}.get(x, x),
                                     key="prod_tpl_8503")
    with col_prod3:
        st.write("")  # spacer
        st.write("")
        run_prod = st.button("🚀 开始生产", type="primary", key="run_prod_8503")

    if run_prod:
        try:
            from engine import run_zhizao, run_zhiyou_score, run_zhiyou_execute
            prod_progress = st.progress(0)
            prod_status = st.empty()

            def prod_cb(pct, msg):
                prod_progress.progress(min(1.0, max(0.0, pct)))
                prod_status.text(msg)

            # Step A: Generate content
            prod_status.text("正在生成内容...")
            result = run_zhizao(selected_batch, prod_count, prod_cb, prod_template)

            if result.get("success"):
                articles = result.get("articles_generated", 0)
                prod_progress.progress(0.5)
                prod_status.text(f"✅ 生成 {articles} 篇，正在评分优化...")

                # Step B: Score
                score_result = run_zhiyou_score(selected_batch, prod_cb)
                prod_progress.progress(0.75)

                # Step C: Optimize
                if score_result.get("success"):
                    prod_status.text("正在执行优化...")
                    opt_result = run_zhiyou_execute(selected_batch, prod_cb)
                    prod_progress.progress(1.0)

                    if opt_result.get("success"):
                        prod_status.text("")
                        st.success(f"✅ 完成！生成 {articles} 篇 → 评分 → 优化")
                        log_action(st.session_state.get("user_login", "anonymous"),
                                   "content_produced_8503", f"batch={selected_batch}, count={articles}")
                        st.rerun()
                    else:
                        st.warning(f"生成完成，优化未完成: {opt_result.get('error', '')}")
                else:
                    st.warning(f"生成完成，评分未完成: {score_result.get('error', '')}")
            else:
                prod_status.text("")
                st.error(f"❌ 生成失败: {result.get('error', '')}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    st.divider()

    # ===== STEP 4: 效果对比 =====
    st.markdown("### 📈 Step 4: 效果对比 — 前后变化")
    st.caption("发布后重新测试相同短语，对比改善效果")

    if len(zhice_results) >= 2:
        first_test = zhice_results[-1]["data"]  # oldest
        last_test = zhice_results[0]["data"]    # newest

        if isinstance(first_test, list) and isinstance(last_test, list):
            before_queries = {item.get("query", ""): item for item in first_test}
            after_queries = {item.get("query", ""): item for item in last_test}
            common = set(before_queries.keys()) & set(after_queries.keys())

            if common:
                comparison = []
                for q in common:
                    b = before_queries[q]
                    a = after_queries[q]
                    b_ok = b.get("has_official_link") or b.get("has_amazon_cn") or b.get("has_brand_mention")
                    a_ok = a.get("has_official_link") or a.get("has_amazon_cn") or a.get("has_brand_mention")
                    if not b_ok and a_ok:
                        change = "🆕 改善"
                    elif b_ok and not a_ok:
                        change = "⚠️ 退步"
                    else:
                        change = "→ 持平"
                    comparison.append({"Query": q, "Before": "✅" if b_ok else "❌",
                                       "After": "✅" if a_ok else "❌", "变化": change})

                df_comp = pd.DataFrame(comparison)
                st.dataframe(df_comp, use_container_width=True, hide_index=True)

                improved = sum(1 for c in comparison if c["变化"] == "🆕 改善")
                regressed = sum(1 for c in comparison if c["变化"] == "⚠️ 退步")
                col_e1, col_e2, col_e3 = st.columns(3)
                col_e1.metric("改善", improved, delta=f"+{improved}")
                col_e2.metric("持平", len(comparison) - improved - regressed)
                col_e3.metric("退步", regressed, delta=f"-{regressed}" if regressed else None, delta_color="inverse")
            else:
                st.info("前后测试没有相同短语可对比。请用相同短语测试。")
        else:
            st.info("需要结构化测试数据才能对比。")
    else:
        st.info("需要至少 2 次测试（发布前/后）才能对比。请发布后重新执行智测。")

    st.divider()

    # ===== STEP 5: 总结 =====
    st.markdown("### 📝 Step 5: 总结")

    summary_lines = [
        f"**已执行测试：** {test_count} 次, {total_queries_tested} 个短语",
        f"**发现缺口：** {gaps_found} 个短语未覆盖",
        f"**内容产出：** {content_produced} 篇文章",
        f"**优化完成：** {content_optimized} 篇",
    ]
    if gaps_found > 0 and content_produced > 0:
        fill_rate = min(100, content_produced / gaps_found * 100)
        summary_lines.append(f"**缺口填补率：** {fill_rate:.0f}%")

    for line in summary_lines:
        st.markdown(line)

    # Notes
    st.divider()
    notes_file = OUTPUT_PATH / "loop_tracking_notes.md"
    existing_notes = notes_file.read_text(encoding="utf-8") if notes_file.exists() else ""
    notes = st.text_area("备注 / 观察", value=existing_notes, height=100, key="loop_notes_8503")
    if st.button("💾 保存备注", key="save_notes_8503"):
        notes_file.write_text(notes, encoding="utf-8")
        log_action(st.session_state.get("user_login", "anonymous"), "notes_saved", "loop tracking notes updated")
        st.success("✅ 已保存")


# ============================================================
# TAB: 执行测试
# ============================================================
with tab_test:
    st.markdown("### 🔬 AI Search Simulation")
    st.caption("配置 → 生成问题 → 确认 → 执行 → 查看结果")

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

    # Execute
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
                        negative_words = ["风险", "骗局", "亏损", "不推荐", "不建议"]
                        has_negative = any(w in answer for w in negative_words)
                        all_results.append({
                            "query": query, "platform": platform,
                            "answer": answer, "answer_length": len(answer),
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
        log_action(st.session_state.get("user_login", "anonymous"), "zhice_executed",
                   f"topic={topic_safe}, queries={len(queries)}, platforms={platforms}")

        # Display
        for r in all_results:
            if "error" in r:
                st.error(f"**{r['query']}** ({r['platform']}): {r['error']}")
            else:
                icon = "✅" if r["has_official_link"] else "❌"
                with st.expander(f"{icon} {r['query']} — {PLATFORMS.get(r['platform'], r['platform'])}"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Official Link", "✅" if r["has_official_link"] else "❌")
                    c2.metric("Brand Mention", "✅" if r["has_brand_mention"] else "❌")
                    c3.metric("Negative", "⚠️" if r["has_negative"] else "✅")
                    st.markdown(r["answer"][:1000])

        st.success(f"✅ Saved: {out_file.name}")


# ============================================================
# TAB: 详情
# ============================================================
with tab_detail:
    st.markdown("### 📋 测试详情")
    st.caption("选择测试文件查看完整详情（包含 8501 执行的测试）")

    zhice_results_all = load_zhice_results()
    if zhice_results_all:
        file_options = [f"{r['file']} ({r['date']})" for r in zhice_results_all]
        selected_idx = st.selectbox("选择测试", range(len(file_options)),
                                    format_func=lambda i: file_options[i], key="detail_select")

        selected_data = zhice_results_all[selected_idx]["data"]
        if isinstance(selected_data, list):
            for i, item in enumerate(selected_data):
                with st.expander(f"Q{i+1}: {item.get('query', 'N/A')}", expanded=(i == 0)):
                    col_d1, col_d2, col_d3 = st.columns(3)
                    col_d1.write(f"**Platform:** {PLATFORMS.get(item.get('platform', ''), item.get('platform', ''))}")
                    col_d2.write(f"**Official Link:** {'✅' if item.get('has_official_link') else '❌'}")
                    col_d3.write(f"**Brand:** {'✅' if item.get('has_brand_mention') else '❌'}")
                    answer = item.get("answer_preview", item.get("answer", ""))
                    if answer:
                        st.markdown(answer[:1000])
        else:
            st.json(selected_data)
    else:
        st.info("暂无测试结果。")


# ============================================================
# TAB: 历史
# ============================================================
with tab_history:
    st.markdown("### 📜 全部测试历史")
    st.caption("所有测试记录（包含 8501 和 8503 执行的）")

    zhice_results_all = load_zhice_results()
    if zhice_results_all:
        history_data = []
        for r in zhice_results_all:
            data = r["data"]
            queries_count = len(data) if isinstance(data, list) else 1
            # Determine coverage
            if isinstance(data, list):
                covered = sum(1 for item in data if item.get("has_official_link") or item.get("has_amazon_cn"))
                coverage = f"{covered}/{queries_count}"
            else:
                coverage = "N/A"
            history_data.append({
                "File": r["file"],
                "Date": r["date"],
                "Queries": queries_count,
                "Coverage": coverage,
            })
        df_hist = pd.DataFrame(history_data)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)

        # Delete option
        st.divider()
        del_file = st.selectbox("Delete a test file", [r["file"] for r in zhice_results_all], key="del_select")
        if st.button("🗑️ Delete Selected", key="del_btn"):
            target = ZHICE_DIR / del_file
            if target.exists():
                target.unlink()
                st.success(f"Deleted: {del_file}")
                st.rerun()
    else:
        st.info("暂无历史记录。")
