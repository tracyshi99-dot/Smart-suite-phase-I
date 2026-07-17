"""
Smart Suite — 需求提交操作台
流程：执行测试 → 机会点分析 → 执行机会点 → 状态展示 → 闭环看板
每个用户只能看到自己的数据
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

st.set_page_config(page_title="Smart Suite — 需求提交", page_icon="🔄", layout="wide")

st.markdown("""<style>
.main .block-container { padding-top: 1rem; padding-left: 1rem; padding-right: 1rem; max-width: 100%; }
div[data-testid="stMetric"] { background: linear-gradient(135deg, #1a1d2e 0%, #12131a 100%); border: 1px solid #2a2f4a; border-radius: 10px; padding: 12px 16px; }
div[data-testid="stMetric"] label { color: #8892b0 !important; font-size: 12px !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #00bcd4 !important; font-weight: 700 !important; }
</style>""", unsafe_allow_html=True)

PLATFORMS = {
    "qianwen": "通义千问", "deepseek": "DeepSeek", "kimi": "Kimi",
    "doubao": "豆包", "chatgpt": "ChatGPT", "gemini": "Gemini",
}

def load_csv_safe(path: Path):
    if path.exists():
        try:
            return pd.read_csv(path, encoding="utf-8-sig", on_bad_lines="skip")
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

def get_user_dir(user: str) -> Path:
    """Each user has their own directory under output/requests/"""
    d = OUTPUT_PATH / "requests" / user
    d.mkdir(parents=True, exist_ok=True)
    return d

def log_action(user, action, details=""):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = LOGS_DIR / "audit.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{ts} | USER={user} | ACTION={action} | {details}\n")

def get_batches():
    batches = []
    if OUTPUT_PATH.exists():
        for d in sorted(OUTPUT_PATH.iterdir(), reverse=True):
            if d.is_dir() and d.name.startswith("batch_"):
                batches.append(d.name)
    return batches if batches else ["batch_003"]


def recompute_detection(r):
    """Re-compute official link and brand mention from answer text (fixes stale data)."""
    answer = r.get("answer", r.get("answer_preview", r.get("full_answer", "")))
    if answer:
        r["has_official_link"] = ".amazon" in answer.lower()
        r["has_brand_mention"] = "亚马逊" in answer or "amazon" in answer.lower()
    return r


# --- Header & Login ---
st.markdown("""<div style="padding:12px 0 8px;">
<h1 style="font-size:28px;font-weight:800;color:#00bcd4;margin:0;">🔄 Smart Suite — 需求提交</h1>
<p style="color:#8892b0;font-size:13px;margin-top:4px;">执行测试 → 机会点分析 → 执行机会点 → 状态展示 → 闭环看板</p>
</div>""", unsafe_allow_html=True)

# Login gate
user_login = st.text_input("👤 请输入您的 Login", value=st.session_state.get("user_login", ""),
                           placeholder="e.g. yujiashi, joyce, murphy", key="login_input")
if user_login:
    st.session_state["user_login"] = user_login

if not user_login:
    st.warning("⚠️ 请先输入您的 Login 才能继续操作。每个人只能查看自己的数据。")
    st.stop()

# User-specific data directory
USER_DIR = get_user_dir(user_login)
USER_TESTS_FILE = USER_DIR / "tests.json"
USER_OPPS_FILE = USER_DIR / "opportunities.json"
USER_ACTIONS_FILE = USER_DIR / "actions.json"

st.caption(f"👤 当前用户: **{user_login}** | 数据目录: `output/requests/{user_login}/`")
st.divider()

# --- Step navigation (supports auto-jump) ---
STEPS = ["🔬 ① 执行测试", "💡 ② 机会点分析", "🚀 ③ 执行机会点", "📋 ④ 执行状态", "🔄 ⑤ 闭环看板"]
STEP_SHORT = ["① 执行测试", "② 机会点", "③ 执行", "④ 状态", "⑤ 看板"]

# Check if we need to auto-jump
if "current_step" not in st.session_state:
    st.session_state["current_step"] = 0

# Step selector (horizontal buttons with full names)
step_cols = st.columns(5)
for i, step_name in enumerate(STEPS):
    with step_cols[i]:
        is_active = (st.session_state["current_step"] == i)
        btn_type = "primary" if is_active else "secondary"
        if st.button(STEP_SHORT[i], key=f"step_nav_{i}", type=btn_type, use_container_width=True):
            st.session_state["current_step"] = i
            st.rerun()

st.markdown(f"**{STEPS[st.session_state['current_step']]}**")
st.divider()

current_step = st.session_state["current_step"]


# ============================================================
# STEP 1: 执行测试
# ============================================================
if current_step == 0:
    st.markdown("### 🔬 执行测试")
    st.caption("AI 测试 / 手动上传话题 / 手动上传内容")

    sub_tab_ai, sub_tab_topic = st.tabs([
        "🤖 AI 测试", "📋 上传话题"
    ])

    # --- Sub-tab: AI 测试 ---
    with sub_tab_ai:
        st.caption("输入产品/话题 → 自动引用智库 + AI 裂变补充 → 测试 → 查看覆盖结果")
        col_cfg, col_q = st.columns([1, 1.5])

        with col_cfg:
            topic = st.text_input("产品/话题", placeholder="e.g. 亚马逊FBA, 跨境选品", key="sim_topic")
            sim_platforms = st.multiselect("测试平台", list(PLATFORMS.keys()),
                                           default=["qianwen"],
                                           format_func=lambda x: PLATFORMS[x], key="sim_plat")
            num_q = st.slider("总短语数量", 3, 30, 10, key="sim_num")

            if st.button("🎯 生成短语（智库优先 + AI 裂变补充）", key="gen_q"):
                if topic:
                    final_queries = []

                    # Step 1: 从智库引用已有短语
                    zhiku_matches = []
                    for batch_dir in sorted(OUTPUT_PATH.iterdir(), reverse=True):
                        if batch_dir.is_dir() and batch_dir.name.startswith("batch_"):
                            zhiku_file = batch_dir / "01_zhiku" / "zhiku_ai_queries.csv"
                            if zhiku_file.exists():
                                df_zk = load_csv_safe(zhiku_file)
                                if not df_zk.empty and "ai_query" in df_zk.columns:
                                    matches = df_zk[df_zk["ai_query"].astype(str).str.contains(topic, case=False, na=False)]
                                    if not matches.empty:
                                        zhiku_matches = matches["ai_query"].tolist()
                                break

                    if zhiku_matches:
                        final_queries.extend(zhiku_matches[:num_q])
                        st.success(f"📚 智库引用 {len(final_queries)} 条已有短语")

                    # Step 2: AI 裂变补充到目标数量
                    remaining = num_q - len(final_queries)
                    if remaining > 0:
                        try:
                            from engine import call_bedrock_claude
                            existing_str = "\n".join(final_queries) if final_queries else "无"
                            prompt = f"""请为话题「{topic}」生成 {remaining} 个中国卖家可能在 AI 搜索引擎中输入的口语化检索短语。

已有短语（不要重复）：
{existing_str}

要求：
1. 不要重复已有短语的意思
2. 覆盖不同角度：是什么、怎么做、费用、优势、对比、问题、流程、最新变化等
3. 语言自然口语化，像真人提问
4. 包含长尾变体（如"新手""2026""中国卖家"等修饰词）
5. 每行一条，不要编号

直接输出短语，不要其他解释。"""
                            with st.spinner(f"AI 裂变补充 {remaining} 条..."):
                                response = call_bedrock_claude(prompt)
                            new_queries = [q.strip().lstrip("0123456789.-、）) ") for q in response.strip().split("\n")
                                           if q.strip() and len(q.strip()) > 4]
                            final_queries.extend(new_queries[:remaining])
                            st.info(f"🤖 AI 裂变补充 {min(len(new_queries), remaining)} 条")
                        except Exception as e:
                            # Fallback to template
                            fallback = [f"{topic}是什么？", f"{topic}怎么使用？", f"{topic}费用多少？",
                                        f"{topic}有什么优势？", f"{topic}和竞品有什么区别？",
                                        f"{topic}常见问题有哪些？", f"中国卖家如何使用{topic}？",
                                        f"{topic}新手入门指南", f"{topic}最新政策", f"{topic}操作流程",
                                        f"{topic}注意事项", f"{topic}成功案例",
                                        f"2026年{topic}有什么变化？", f"{topic}适合新手吗？"]
                            # Remove duplicates with existing
                            fallback = [q for q in fallback if q not in final_queries]
                            final_queries.extend(fallback[:remaining])
                            st.warning(f"AI 不可用，模板补充 {min(len(fallback), remaining)} 条")

                    st.session_state["sim_queries"] = final_queries[:num_q]

        with col_q:
            if "sim_queries" in st.session_state and st.session_state["sim_queries"]:
                st.markdown(f"**短语列表（{len(st.session_state['sim_queries'])} 条，可编辑）：**")
                edited = []
                for i, q in enumerate(st.session_state["sim_queries"]):
                    edited.append(st.text_input(f"Q{i+1}", value=q, key=f"sq_{i}"))
                st.session_state["sim_queries_final"] = edited

                # Continue expansion button
                col_more, col_run = st.columns(2)
                with col_more:
                    more_count = st.number_input("追加裂变数量", 3, 20, 5, key="more_count")
                    if st.button("➕ 继续裂变", key="more_expand"):
                        try:
                            from engine import call_bedrock_claude
                            existing_str = "\n".join(edited)
                            topic_val = st.session_state.get("sim_topic", "")
                            prompt = f"""请为话题「{topic_val}」再生成 {more_count} 个检索短语。

已有短语（不要重复）：
{existing_str}

要求：与已有短语不重复，覆盖新角度，口语化，每行一条，不要编号。"""
                            with st.spinner(f"继续裂变 {more_count} 条..."):
                                response = call_bedrock_claude(prompt)
                            new_qs = [q.strip().lstrip("0123456789.-、）) ") for q in response.strip().split("\n")
                                      if q.strip() and len(q.strip()) > 4 and q.strip() not in edited]
                            st.session_state["sim_queries"] = edited + new_qs[:more_count]
                            st.rerun()
                        except Exception as e:
                            st.error(f"裂变失败: {str(e)[:80]}")
                with col_run:
                    st.write("")
                    if st.button("✅ 确认并执行测试", type="primary", key="run_test"):
                        st.session_state["test_running"] = True

        # Execute test
        if st.session_state.get("test_running") and st.session_state.get("sim_queries_final"):
            st.divider()
            from zhice_engine import REAL_API_MAP
            queries = st.session_state["sim_queries_final"]
            platforms = st.session_state.get("sim_plat", ["qianwen"])
            results = []
            prog = st.progress(0)
            total = len(queries) * len(platforms)
            done = 0

            for query in queries:
                for plat in platforms:
                    api_func = REAL_API_MAP.get(plat)
                    if api_func:
                        try:
                            r = api_func(query)
                            answer = r.get("full_answer", "")
                            has_gs = ".amazon" in answer.lower()
                            has_brand = "亚马逊" in answer or "amazon" in answer.lower()
                            results.append({"query": query, "platform": plat, "answer": answer,
                                            "answer_length": len(answer), "has_official_link": has_gs,
                                            "has_brand_mention": has_brand,
                                            "has_negative": any(w in answer for w in ["风险","骗局","亏损"])})
                        except Exception as e:
                            results.append({"query": query, "platform": plat, "error": str(e), "answer": ""})
                    done += 1
                    prog.progress(done / total)
                    time.sleep(0.3)

            prog.progress(1.0)
            st.session_state["test_running"] = False
            st.session_state["test_just_completed"] = True

            # Save to user directory
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            test_entry = {"id": f"test_{ts}", "topic": topic, "date": ts,
                          "user": user_login, "results": results}

            existing_tests = json.loads(USER_TESTS_FILE.read_text(encoding="utf-8")) if USER_TESTS_FILE.exists() else []
            existing_tests.insert(0, test_entry)
            USER_TESTS_FILE.write_text(json.dumps(existing_tests, ensure_ascii=False, indent=2), encoding="utf-8")

            shared_file = ZHICE_DIR / f"sim_{topic.replace(' ','_')[:20]}_{ts}.json"
            shared_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
            log_action(user_login, "test_executed", f"topic={topic}, queries={len(queries)}")

            st.success(f"✅ 测试完成！{len(results)} 条结果已保存。")
            for r in results:
                recompute_detection(r)
                icon = "✅" if r.get("has_official_link") else "❌"
                st.markdown(f"{icon} **{r['query']}** ({PLATFORMS.get(r.get('platform',''), r.get('platform',''))}) — {r.get('answer_length',0)} chars")

    # Persistent CTA: show when user has test results
    _user_has_tests = USER_TESTS_FILE.exists() and USER_TESTS_FILE.stat().st_size > 2
    if _user_has_tests:
        st.divider()
        if st.button("➡️ 下一步：查看机会点分析", type="primary", key="cta_to_step2"):
            st.session_state["current_step"] = 1
            st.rerun()

    # --- Sub-tab: 上传话题 ---
    with sub_tab_topic:
        st.caption("手动上传需要测试的话题/检索短语（CSV 或手动输入）")

        st.markdown("**方式一：上传 CSV**")
        st.caption("CSV 需包含 `query` 或 `ai_query` 列")
        uploaded_topics = st.file_uploader("上传话题 CSV", type=["csv"], key="upload_topics")
        if uploaded_topics:
            try:
                df_up = pd.read_csv(uploaded_topics, encoding="utf-8-sig", on_bad_lines="skip")
                # Find query column
                q_col = None
                for col in ["query", "ai_query", "检索短语", "问题", "topic"]:
                    if col in df_up.columns:
                        q_col = col
                        break
                if q_col is None and len(df_up.columns) > 0:
                    q_col = df_up.columns[0]

                if q_col:
                    queries_list = df_up[q_col].dropna().astype(str).tolist()
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                    test_entry = {"id": f"upload_topic_{ts}", "topic": f"上传话题({len(queries_list)}条)",
                                  "date": ts, "user": user_login,
                                  "results": [{"query": q, "platform": "待测试", "answer": "",
                                               "has_official_link": False, "has_brand_mention": False} for q in queries_list]}
                    existing_tests = json.loads(USER_TESTS_FILE.read_text(encoding="utf-8")) if USER_TESTS_FILE.exists() else []
                    existing_tests.insert(0, test_entry)
                    USER_TESTS_FILE.write_text(json.dumps(existing_tests, ensure_ascii=False, indent=2), encoding="utf-8")
                    log_action(user_login, "topics_uploaded", f"count={len(queries_list)}")
                    st.success(f"✅ 上传 {len(queries_list)} 个话题！可在「② 机会点分析」中查看，或回到 AI 测试执行。")
                    st.dataframe(pd.DataFrame({"话题": queries_list}), use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"上传失败: {str(e)}")

        st.divider()
        st.markdown("**方式二：手动输入**")
        st.caption("每行一个话题/问句")
        manual_topics = st.text_area("输入话题（每行一个）", height=150, key="manual_topics",
                                     placeholder="亚马逊FBA是什么？\n亚马逊开店费用多少？\n如何选择物流方案？")
        if st.button("✅ 提交话题", key="submit_manual_topics"):
            lines = [l.strip() for l in manual_topics.strip().split("\n") if l.strip()]
            if lines:
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                test_entry = {"id": f"manual_topic_{ts}", "topic": f"手动输入({len(lines)}条)",
                              "date": ts, "user": user_login,
                              "results": [{"query": q, "platform": "待测试", "answer": "",
                                           "has_official_link": False, "has_brand_mention": False} for q in lines]}
                existing_tests = json.loads(USER_TESTS_FILE.read_text(encoding="utf-8")) if USER_TESTS_FILE.exists() else []
                existing_tests.insert(0, test_entry)
                USER_TESTS_FILE.write_text(json.dumps(existing_tests, ensure_ascii=False, indent=2), encoding="utf-8")
                log_action(user_login, "topics_manual", f"count={len(lines)}")
                st.success(f"✅ 已提交 {len(lines)} 个话题！")

    # --- Step 1: Clear & History ---
    USER_HISTORY_FILE = USER_DIR / "history.json"
    _history = json.loads(USER_HISTORY_FILE.read_text(encoding="utf-8")) if USER_HISTORY_FILE.exists() else []

    with st.expander("🗑️ 清除测试记录 / 📜 历史", expanded=False):
        user_tests_here = json.loads(USER_TESTS_FILE.read_text(encoding="utf-8")) if USER_TESTS_FILE.exists() else []
        if user_tests_here:
            st.caption(f"当前有 {len(user_tests_here)} 条测试记录")
            if st.button("🗑️ 清除所有测试记录（归档）", key="clear_tests_s1"):
                archive = {"archived_at": datetime.now().strftime("%Y-%m-%d %H:%M"), "type": "tests", "count": len(user_tests_here), "data": user_tests_here}
                _history.insert(0, archive)
                USER_HISTORY_FILE.write_text(json.dumps(_history, ensure_ascii=False, indent=2), encoding="utf-8")
                USER_TESTS_FILE.write_text("[]", encoding="utf-8")
                st.success("✅ 已归档")
                st.rerun()
        else:
            st.caption("暂无测试记录")

        # Show history for tests
        test_history = [h for h in _history if h.get("type") == "tests"]
        if test_history:
            st.markdown("**📜 历史记录：**")
            for h in test_history[:5]:
                st.caption(f"🗂️ {h.get('archived_at','')} — {h.get('count',0)} 条测试")


# ============================================================
# STEP 2: 机会点分析
# ============================================================
if current_step == 1:
    st.markdown("### 💡 机会点分析")
    st.caption("基于测试结果，分析缺口和改善机会，确认哪些需要行动")

    # Load user's tests
    user_tests = json.loads(USER_TESTS_FILE.read_text(encoding="utf-8")) if USER_TESTS_FILE.exists() else []

    if not user_tests:
        st.info("暂无测试结果。请先在「① 执行测试」中运行测试。")
    else:
        # Let user select which test to analyze
        test_options = [f"{t['topic']} ({t['date']})" for t in user_tests]
        sel_idx = st.selectbox("选择测试", range(len(test_options)),
                               format_func=lambda i: test_options[i], key="opp_test_sel")

        selected_test = user_tests[sel_idx]
        results = selected_test["results"]

        # Show results table
        st.markdown("**测试结果：**")
        df_r = pd.DataFrame([{
            "Query": r.get("query", ""),
            "Platform": PLATFORMS.get(r.get("platform", ""), r.get("platform", "")),
            "Official Link": "✅" if recompute_detection(r).get("has_official_link") else "❌",
            "Brand": "✅" if r.get("has_brand_mention") else "❌",
            "Gap": "⚠️" if not r.get("has_official_link") else "✅",
        } for r in results if "error" not in r])
        st.dataframe(df_r, use_container_width=True, hide_index=True)

        # Extract gaps
        gaps = [r for r in results if not r.get("has_official_link") and "error" not in r]

        st.divider()
        st.markdown(f"### 发现 **{len(gaps)}** 个机会点")

        if gaps:
            # Show gap details with expandable answers
            opp_list = []
            for i, g in enumerate(gaps):
                with st.expander(f"⚠️ {g['query']} ({PLATFORMS.get(g.get('platform',''), g.get('platform',''))})"):
                    st.markdown("**当前 AI 回答（无我方内容）：**")
                    st.markdown(g.get("answer", "")[:800])
                    st.markdown("---")
                    st.markdown("**建议：** 产出针对此问题的 GEO 优化内容，确保包含官方链接和品牌信息。")

                opp_list.append({
                    "id": f"opp_{i}",
                    "query": g["query"],
                    "platform": g.get("platform", ""),
                    "status": "待执行",
                    "test_id": selected_test["id"],
                })

            # Save opportunities
            st.divider()
            if st.button("✅ 确认机会点，进入执行", type="primary", key="confirm_opps"):
                USER_OPPS_FILE.write_text(json.dumps(opp_list, ensure_ascii=False, indent=2), encoding="utf-8")
                log_action(user_login, "opps_confirmed", f"count={len(opp_list)}")
                st.session_state["current_step"] = 2
                st.rerun()

            # CTA
            if USER_OPPS_FILE.exists():
                st.divider()
                if st.button("➡️ 下一步：执行机会点", type="primary", key="cta_to_step3"):
                    st.session_state["current_step"] = 2
                    st.rerun()
        else:
            st.success("🎉 全部覆盖，无缺口！无需额外行动。")

    # --- Step 2: Clear & History ---
    USER_HISTORY_FILE = USER_DIR / "history.json"
    _history = json.loads(USER_HISTORY_FILE.read_text(encoding="utf-8")) if USER_HISTORY_FILE.exists() else []
    with st.expander("🗑️ 清除机会点 / 📜 历史", expanded=False):
        opps_here = json.loads(USER_OPPS_FILE.read_text(encoding="utf-8")) if USER_OPPS_FILE.exists() else []
        if opps_here:
            st.caption(f"当前有 {len(opps_here)} 条机会点")
            if st.button("🗑️ 清除所有机会点（归档）", key="clear_opps_s2"):
                archive = {"archived_at": datetime.now().strftime("%Y-%m-%d %H:%M"), "type": "opportunities", "count": len(opps_here), "data": opps_here}
                _history.insert(0, archive)
                USER_HISTORY_FILE.write_text(json.dumps(_history, ensure_ascii=False, indent=2), encoding="utf-8")
                USER_OPPS_FILE.write_text("[]", encoding="utf-8")
                st.success("✅ 已归档")
                st.rerun()
        else:
            st.caption("暂无机会点")
        opp_history = [h for h in _history if h.get("type") == "opportunities"]
        if opp_history:
            st.markdown("**📜 历史记录：**")
            for h in opp_history[:5]:
                st.caption(f"🗂️ {h.get('archived_at','')} — {h.get('count',0)} 条机会点")


# ============================================================
# STEP 3: 执行机会点
# ============================================================
if current_step == 2:
    st.markdown("### 🚀 执行机会点")
    st.caption("产出内容 / 上传已有文章（自动匹配机会点）→ 优化 → 发布")

    # Load opportunities
    opps = json.loads(USER_OPPS_FILE.read_text(encoding="utf-8")) if USER_OPPS_FILE.exists() else []

    # --- Upload section: upload existing articles to match opportunities ---
    with st.expander("📄 上传已有文章（自动匹配机会点）", expanded=False):
        st.caption("上传已有内容 → 系统自动匹配对应的检索短语 → 匹配成功的直接进入优化流程")

        upload_mode = st.radio("上传方式", ["CSV 批量上传", "手动粘贴"], horizontal=True, key="upload_mode_s3")

        if upload_mode == "CSV 批量上传":
            uploaded_content = st.file_uploader("上传内容 CSV", type=["csv"], key="upload_content_s3",
                                               help="建议包含列：title, content_draft (或 content/article/body)")
            if uploaded_content:
                try:
                    df_up = pd.read_csv(uploaded_content, encoding="utf-8-sig", on_bad_lines="skip")
                    # Normalize columns
                    col_map = {"content": "content_draft", "article": "content_draft",
                               "body": "content_draft", "query": "ai_query", "text": "content_draft"}
                    for old, new in col_map.items():
                        if old in df_up.columns and new not in df_up.columns:
                            df_up = df_up.rename(columns={old: new})

                    st.dataframe(df_up.head(3), use_container_width=True, hide_index=True)

                    # Smart matching: match uploaded content to opportunity queries
                    if opps and "content_draft" in df_up.columns:
                        st.markdown("**🔍 自动匹配结果：**")
                        pending_queries = [o["query"] for o in opps if o.get("status") == "待执行"]
                        matched = []
                        unmatched = []

                        for _, row in df_up.iterrows():
                            content = str(row.get("content_draft", ""))
                            title = str(row.get("title", row.get("ai_query", "")))
                            # Try to match against pending opportunity queries
                            best_match = None
                            for pq in pending_queries:
                                # Simple keyword matching
                                keywords = [w for w in pq.replace("？", "").replace("?", "").split() if len(w) > 1]
                                if not keywords:
                                    keywords = [pq[:8]]
                                match_score = sum(1 for kw in keywords if kw in content or kw in title)
                                if match_score >= max(1, len(keywords) // 2):
                                    best_match = pq
                                    break
                            if best_match:
                                matched.append({"title": title[:50], "matched_query": best_match, "status": "✅ 匹配"})
                            else:
                                unmatched.append({"title": title[:50], "status": "⚠️ 未匹配"})

                        if matched:
                            st.success(f"✅ 匹配成功 {len(matched)} 篇 — 可直接进入优化")
                            st.dataframe(pd.DataFrame(matched), use_container_width=True, hide_index=True)
                        if unmatched:
                            st.warning(f"⚠️ 未匹配 {len(unmatched)} 篇 — 将作为额外内容上传")

                    if st.button("✅ 确认上传并标记完成", type="primary", key="confirm_upload_s3"):
                        batch = get_batches()[0]
                        zhizao_file = OUTPUT_PATH / batch / "02_zhizao" / "zhizao_draft_content.csv"
                        zhizao_file.parent.mkdir(parents=True, exist_ok=True)

                        if "content_id" not in df_up.columns:
                            df_up["content_id"] = [f"UPLOAD_{user_login}_{i:03d}" for i in range(len(df_up))]
                        if "version" not in df_up.columns:
                            df_up["version"] = "uploaded"
                        if "word_count" not in df_up.columns and "content_draft" in df_up.columns:
                            df_up["word_count"] = df_up["content_draft"].astype(str).str.len()

                        if zhizao_file.exists() and zhizao_file.stat().st_size > 0:
                            try:
                                existing = pd.read_csv(zhizao_file, encoding="utf-8-sig", on_bad_lines="skip")
                                combined = pd.concat([existing, df_up], ignore_index=True)
                                combined.to_csv(zhizao_file, index=False, encoding="utf-8-sig")
                            except Exception:
                                df_up.to_csv(zhizao_file, index=False, encoding="utf-8-sig")
                        else:
                            df_up.to_csv(zhizao_file, index=False, encoding="utf-8-sig")

                        # Mark matched opportunities as done
                        if opps and matched:
                            matched_queries = {m["matched_query"] for m in matched}
                            for o in opps:
                                if o["query"] in matched_queries and o.get("status") == "待执行":
                                    o["status"] = "已完成(上传)"
                                    o["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            USER_OPPS_FILE.write_text(json.dumps(opps, ensure_ascii=False, indent=2), encoding="utf-8")

                        log_action(user_login, "content_uploaded_s3", f"count={len(df_up)}, matched={len(matched) if 'matched' in dir() else 0}")
                        st.success(f"✅ 上传 {len(df_up)} 篇！匹配的机会点已标记完成，可直接走优化流程。")
                        st.rerun()
                except Exception as e:
                    st.error(f"上传失败: {str(e)}")

        else:  # 手动粘贴
            paste_title = st.text_input("文章标题", key="paste_title_s3")
            paste_content = st.text_area("文章内容", height=150, key="paste_content_s3")
            if st.button("✅ 提交", key="submit_paste_s3"):
                if paste_content.strip():
                    batch = get_batches()[0]
                    zhizao_file = OUTPUT_PATH / batch / "02_zhizao" / "zhizao_draft_content.csv"
                    zhizao_file.parent.mkdir(parents=True, exist_ok=True)
                    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                    new_row = pd.DataFrame([{"content_id": f"PASTE_{user_login}_{ts}",
                                             "ai_query": paste_title, "title": paste_title or "Untitled",
                                             "content_draft": paste_content, "word_count": len(paste_content), "version": "uploaded"}])
                    if zhizao_file.exists() and zhizao_file.stat().st_size > 0:
                        try:
                            existing = pd.read_csv(zhizao_file, encoding="utf-8-sig", on_bad_lines="skip")
                            pd.concat([existing, new_row], ignore_index=True).to_csv(zhizao_file, index=False, encoding="utf-8-sig")
                        except Exception:
                            new_row.to_csv(zhizao_file, index=False, encoding="utf-8-sig")
                    else:
                        new_row.to_csv(zhizao_file, index=False, encoding="utf-8-sig")

                    # Try to match and mark opportunity
                    for o in opps:
                        if o.get("status") == "待执行":
                            if any(kw in paste_content or kw in paste_title for kw in o["query"].replace("？","").split() if len(kw) > 1):
                                o["status"] = "已完成(上传)"
                                o["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                                break
                    USER_OPPS_FILE.write_text(json.dumps(opps, ensure_ascii=False, indent=2), encoding="utf-8")
                    log_action(user_login, "content_pasted_s3", f"title={paste_title}")
                    st.success("✅ 已提交！匹配的机会点已标记完成。")
                    st.rerun()

    st.divider()

    # --- Original execution logic ---
    if not opps:
        st.info("暂无机会点。请先在「② 机会点分析」中确认机会点。")
    else:
        pending = [o for o in opps if o.get("status") == "待执行"]
        done_opps = [o for o in opps if o.get("status") != "待执行"]

        st.markdown(f"**待执行：** {len(pending)} 个 | **已完成：** {len(done_opps)} 个")
        st.divider()

        if pending:
            st.markdown("**待执行的机会点：**")
            df_pending = pd.DataFrame([{
                "Query": o["query"],
                "Platform": PLATFORMS.get(o.get("platform", ""), o.get("platform", "")),
                "Status": o["status"],
            } for o in pending])
            st.dataframe(df_pending, use_container_width=True, hide_index=True)

            # Execution options
            st.divider()
            col_ex1, col_ex2 = st.columns(2)
            with col_ex1:
                exec_count = st.number_input("执行篇数", 1, len(pending), min(3, len(pending)), key="exec_count")
            with col_ex2:
                exec_tpl = st.selectbox("模板", ["auto", "registration", "fees", "logistics", "listing"],
                                        format_func=lambda x: {"auto":"智能匹配","registration":"注册流程",
                                                               "fees":"费用成本","logistics":"物流","listing":"Listing"}.get(x,x),
                                        key="exec_tpl")

            if st.button("🚀 开始执行（生产+优化）", type="primary", key="exec_opps"):
                try:
                    from engine import run_zhizao, run_zhiyou_score, run_zhiyou_execute
                    batch = get_batches()[0]
                    prog = st.progress(0)
                    status_text = st.empty()

                    # Ensure queries are in zhiku
                    zhiku_path = OUTPUT_PATH / batch / "01_zhiku" / "zhiku_ai_queries.csv"
                    zhiku_path.parent.mkdir(parents=True, exist_ok=True)
                    existing_zhiku = load_csv_safe(zhiku_path)

                    # Add pending queries to zhiku
                    new_rows = []
                    for o in pending[:exec_count]:
                        new_rows.append({"ai_query": o["query"], "source": f"request_{user_login}",
                                         "is_selected": "TRUE", "priority_score": 4.8,
                                         "category": "", "keyword": o["query"][:20]})
                    df_new = pd.DataFrame(new_rows)
                    combined = pd.concat([existing_zhiku, df_new], ignore_index=True) if not existing_zhiku.empty else df_new
                    if "ai_query" in combined.columns:
                        combined = combined.drop_duplicates(subset=["ai_query"], keep="first")
                    combined.to_csv(zhiku_path, index=False, encoding="utf-8-sig")

                    # Run production
                    status_text.text("正在生成内容...")
                    prog.progress(0.2)
                    r1 = run_zhizao(batch, exec_count, None, exec_tpl)

                    if r1.get("success"):
                        articles = r1.get("articles_generated", 0)
                        status_text.text(f"生成 {articles} 篇，评分中...")
                        prog.progress(0.5)
                        run_zhiyou_score(batch, None)
                        status_text.text("优化中...")
                        prog.progress(0.75)
                        run_zhiyou_execute(batch, None)
                        prog.progress(1.0)
                        status_text.text("")

                        # Update opportunity status
                        for o in pending[:exec_count]:
                            o["status"] = "已完成"
                            o["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        USER_OPPS_FILE.write_text(json.dumps(opps, ensure_ascii=False, indent=2), encoding="utf-8")

                        # Save action record
                        actions = json.loads(USER_ACTIONS_FILE.read_text(encoding="utf-8")) if USER_ACTIONS_FILE.exists() else []
                        actions.insert(0, {"date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                           "action": "content_produced", "count": articles,
                                           "batch": batch, "queries": [o["query"] for o in pending[:exec_count]]})
                        USER_ACTIONS_FILE.write_text(json.dumps(actions, ensure_ascii=False, indent=2), encoding="utf-8")

                        log_action(user_login, "opps_executed", f"batch={batch}, count={articles}")
                        st.success(f"✅ 完成！生成 {articles} 篇，已优化。")
                        st.divider()
                        if st.button("➡️ 下一步：查看执行状态", type="primary", key="cta_to_step4"):
                            st.session_state["current_step"] = 3
                            st.rerun()
                    else:
                        st.error(f"❌ 失败: {r1.get('error', '')}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.success("✅ 所有机会点已执行完毕！")


# ============================================================
# STEP 4: 执行状态
# ============================================================
if current_step == 3:
    st.markdown("### 📋 执行状态")
    st.caption("执行进展 → 提交审批 → 发布状态")

    # Load opportunities
    opps = json.loads(USER_OPPS_FILE.read_text(encoding="utf-8")) if USER_OPPS_FILE.exists() else []
    actions = json.loads(USER_ACTIONS_FILE.read_text(encoding="utf-8")) if USER_ACTIONS_FILE.exists() else []

    # Load publish status (shared file that 8501 writes back to)
    USER_PUBLISH_FILE = USER_DIR / "publish_status.json"
    publish_status = json.loads(USER_PUBLISH_FILE.read_text(encoding="utf-8")) if USER_PUBLISH_FILE.exists() else {}

    if not opps and not actions:
        st.info("暂无执行记录。")
    else:
        # Status KPIs
        total_opps = len(opps)
        done_opps = sum(1 for o in opps if o.get("status") != "待执行")
        pending_opps = total_opps - done_opps
        published = publish_status.get("published_count", 0)

        kc1, kc2, kc3, kc4 = st.columns(4)
        kc1.metric("总机会点", total_opps)
        kc2.metric("已执行", done_opps)
        kc3.metric("待执行", pending_opps)
        kc4.metric("已发布", published, delta="✅" if published > 0 else None)

        # Progress bar
        if total_opps > 0:
            st.progress(done_opps / total_opps)

        st.divider()

        # Opportunity status table (with publish status)
        if opps:
            st.markdown("**机会点状态：**")
            published_queries = set(publish_status.get("published_queries", []))
            df_opps = pd.DataFrame([{
                "Query": o["query"],
                "Platform": PLATFORMS.get(o.get("platform", ""), o.get("platform", "")),
                "内容状态": "✅ 已完成" if o.get("status") != "待执行" else "⏳ 待执行",
                "发布状态": "🟢 已发布" if o["query"] in published_queries else ("🟡 待审批" if o.get("status") != "待执行" else "—"),
                "完成时间": o.get("completed_at", "—"),
            } for o in opps])
            st.dataframe(df_opps, use_container_width=True, hide_index=True)

        # --- Submit to 8501 for approval + publish ---
        st.divider()
        st.markdown("### 📤 提交审批与发布")
        st.caption("执行完成的内容提交到主控台 (8501) 审批，批复后自动发布")

        # Check if all done
        all_done = (done_opps > 0 and pending_opps == 0)
        some_done = done_opps > 0

        if some_done:
            # Write to shared request tracking file for 8501
            REQUEST_TRACKING_FILE = OUTPUT_PATH / "request_tracking.json"
            existing_requests = json.loads(REQUEST_TRACKING_FILE.read_text(encoding="utf-8")) if REQUEST_TRACKING_FILE.exists() else []

            # Check if already submitted
            already_submitted = any(r.get("user") == user_login and r.get("status") != "published" for r in existing_requests)

            if already_submitted:
                current_req = next((r for r in existing_requests if r.get("user") == user_login and r.get("status") != "published"), None)
                if current_req:
                    req_status = current_req.get("status", "pending")
                    if req_status == "approved":
                        st.success("✅ 已批复！正在执行智布+智传...")
                        # Auto-execute zhibu + zhichuan
                        try:
                            from engine import run_zhibu
                            batch = get_batches()[0]
                            zhibu_result = run_zhibu(batch, None)
                            if zhibu_result.get("success"):
                                # Mark as published
                                current_req["status"] = "published"
                                current_req["published_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                                REQUEST_TRACKING_FILE.write_text(json.dumps(existing_requests, ensure_ascii=False, indent=2), encoding="utf-8")

                                # Update user's publish status
                                pub_queries = [o["query"] for o in opps if o.get("status") != "待执行"]
                                publish_status = {"published_count": len(pub_queries),
                                                  "published_queries": pub_queries,
                                                  "published_at": datetime.now().strftime("%Y-%m-%d %H:%M")}
                                USER_PUBLISH_FILE.write_text(json.dumps(publish_status, ensure_ascii=False, indent=2), encoding="utf-8")
                                log_action(user_login, "content_published", f"count={len(pub_queries)}")
                                st.success(f"🎉 已完成发布！{len(pub_queries)} 篇内容已通过智布+智传发布。")
                                st.rerun()
                            else:
                                st.warning(f"智布执行中: {zhibu_result.get('error', '请稍后刷新')}")
                        except Exception as e:
                            # If zhibu not available, just mark as published
                            current_req["status"] = "published"
                            current_req["published_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            REQUEST_TRACKING_FILE.write_text(json.dumps(existing_requests, ensure_ascii=False, indent=2), encoding="utf-8")
                            pub_queries = [o["query"] for o in opps if o.get("status") != "待执行"]
                            publish_status = {"published_count": len(pub_queries),
                                              "published_queries": pub_queries,
                                              "published_at": datetime.now().strftime("%Y-%m-%d %H:%M")}
                            USER_PUBLISH_FILE.write_text(json.dumps(publish_status, ensure_ascii=False, indent=2), encoding="utf-8")
                            st.success(f"🎉 已标记发布完成！{len(pub_queries)} 篇。")
                            st.rerun()
                    elif req_status == "rejected":
                        st.error("❌ 审批被驳回。请修改后重新提交。")
                        if st.button("🔄 重新提交", key="resubmit"):
                            current_req["status"] = "pending"
                            current_req["submitted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            REQUEST_TRACKING_FILE.write_text(json.dumps(existing_requests, ensure_ascii=False, indent=2), encoding="utf-8")
                            st.rerun()
                    else:  # pending
                        st.info("⏳ 已提交，等待 8501 主控台审批中...")
                        st.caption("审批通过后将自动执行智布+智传完成发布。")
            else:
                # Not yet submitted
                completed_queries = [o["query"] for o in opps if o.get("status") != "待执行"]
                st.markdown(f"**{len(completed_queries)} 篇内容已就绪，可提交审批发布**")

                if st.button("📤 提交到主控台审批", type="primary", key="submit_for_approval"):
                    new_request = {
                        "id": f"req_{user_login}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        "user": user_login,
                        "status": "pending",
                        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "queries": completed_queries,
                        "count": len(completed_queries),
                        "batch": get_batches()[0],
                    }
                    existing_requests.append(new_request)
                    REQUEST_TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)
                    REQUEST_TRACKING_FILE.write_text(json.dumps(existing_requests, ensure_ascii=False, indent=2), encoding="utf-8")
                    log_action(user_login, "submitted_for_approval", f"count={len(completed_queries)}")
                    st.success("✅ 已提交审批！等待主控台 (8501) 批复。")
                    st.rerun()

            # Show publish status if published
            if publish_status.get("published_count", 0) > 0:
                st.divider()
                st.markdown("### 🟢 已完成发布")
                st.success(f"🎉 {publish_status['published_count']} 篇内容已发布 ({publish_status.get('published_at', '')})")

        # Action history
        if actions:
            st.divider()
            st.markdown("**执行历史：**")
            for a in actions[:10]:
                st.markdown(f"- **{a['date']}** — {a['action']} | {a.get('count', '')} 篇 | Batch: {a.get('batch', '')}")

    # CTA to dashboard
    st.divider()
    if st.button("➡️ 下一步：查看闭环看板", type="primary", key="cta_to_step5"):
        st.session_state["current_step"] = 4
        st.rerun()


# ============================================================
# STEP 5: 闭环看板（放最后）
# ============================================================
if current_step == 4:
    st.markdown("### 🔄 闭环看板")
    st.caption("整体效果：测试 → 缺口 → 行动 → 结果")

    # Load all user data
    user_tests = json.loads(USER_TESTS_FILE.read_text(encoding="utf-8")) if USER_TESTS_FILE.exists() else []
    opps = json.loads(USER_OPPS_FILE.read_text(encoding="utf-8")) if USER_OPPS_FILE.exists() else []
    actions = json.loads(USER_ACTIONS_FILE.read_text(encoding="utf-8")) if USER_ACTIONS_FILE.exists() else []

    # Load history (archived records)
    USER_HISTORY_FILE = USER_DIR / "history.json"
    history = json.loads(USER_HISTORY_FILE.read_text(encoding="utf-8")) if USER_HISTORY_FILE.exists() else []

    # Summary KPIs
    total_tests = len(user_tests)
    total_queries = sum(len(t.get("results", [])) for t in user_tests)
    total_gaps = len(opps)
    gaps_done = sum(1 for o in opps if o.get("status") != "待执行")
    total_articles = sum(a.get("count", 0) for a in actions)

    st.markdown("#### 📊 整体数据")
    kc1, kc2, kc3, kc4, kc5 = st.columns(5)
    kc1.metric("测试次数", total_tests)
    kc2.metric("测试短语", total_queries)
    kc3.metric("发现缺口", total_gaps)
    kc4.metric("已行动", gaps_done)
    kc5.metric("产出文章", total_articles)

    # Fill rate
    if total_gaps > 0:
        fill_rate = gaps_done / total_gaps
        st.progress(fill_rate)
        st.markdown(f"**缺口填补率：{fill_rate*100:.0f}%**")

    st.divider()

    # Timeline view
    st.markdown("#### 📅 操作时间线")
    timeline = []
    for t in user_tests:
        timeline.append({"date": t.get("date", ""), "type": "🔬 测试",
                         "detail": f"{t.get('topic', '')} ({len(t.get('results',[]))} queries)"})
    for a in actions:
        timeline.append({"date": a.get("date", ""), "type": "🚀 产出",
                         "detail": f"{a.get('count', 0)} 篇"})

    if timeline:
        timeline.sort(key=lambda x: x["date"], reverse=True)
        df_tl = pd.DataFrame(timeline[:20])
        st.dataframe(df_tl, use_container_width=True, hide_index=True)
    else:
        st.info("暂无操作记录。开始执行测试后将在此展示闭环效果。")

    # Before vs After (if multiple tests on same topic)
    st.divider()
    st.markdown("#### 📈 前后效果对比")
    if len(user_tests) >= 2:
        first = user_tests[-1].get("results", [])
        last = user_tests[0].get("results", [])
        if first and last:
            bq = {r.get("query"): r for r in first if "error" not in r}
            aq = {r.get("query"): r for r in last if "error" not in r}
            common = set(bq.keys()) & set(aq.keys())
            if common:
                comp = []
                for q in common:
                    b_ok = bq[q].get("has_official_link") or bq[q].get("has_brand_mention")
                    a_ok = aq[q].get("has_official_link") or aq[q].get("has_brand_mention")
                    change = "🆕 改善" if (not b_ok and a_ok) else ("⚠️ 退步" if (b_ok and not a_ok) else "→ 持平")
                    comp.append({"Query": q, "Before": "✅" if b_ok else "❌",
                                 "After": "✅" if a_ok else "❌", "变化": change})
                df_c = pd.DataFrame(comp)
                st.dataframe(df_c, use_container_width=True, hide_index=True)
                improved = sum(1 for c in comp if c["变化"] == "🆕 改善")
                st.metric("改善数", improved, delta=f"+{improved}")
            else:
                st.info("前后测试无相同短语可对比。建议发布后用相同短语重新测试。")
    else:
        st.info("需要至少 2 次测试才能展示前后效果对比。")

