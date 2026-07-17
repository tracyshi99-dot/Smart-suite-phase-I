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

# --- Tabs (flow order) ---
tab_test, tab_opps, tab_execute, tab_status, tab_dashboard = st.tabs([
    "🔬 ① 执行测试",
    "💡 ② 机会点分析",
    "🚀 ③ 执行机会点",
    "📋 ④ 执行状态",
    "🔄 ⑤ 闭环看板",
])


# ============================================================
# TAB 1: 执行测试
# ============================================================
with tab_test:
    st.markdown("### 🔬 执行测试")
    st.caption("输入产品/话题 → 生成问题 → 在 AI 平台测试 → 查看覆盖结果")

    col_cfg, col_q = st.columns([1, 1.5])

    with col_cfg:
        topic = st.text_input("产品/话题", placeholder="e.g. 亚马逊FBA, 跨境选品", key="sim_topic")
        sim_platforms = st.multiselect("测试平台", list(PLATFORMS.keys()),
                                       default=["qianwen"],
                                       format_func=lambda x: PLATFORMS[x], key="sim_plat")
        num_q = st.slider("问题数量", 1, 10, 5, key="sim_num")

        if st.button("🎯 生成问题", key="gen_q"):
            if topic:
                base = [f"{topic}是什么？", f"{topic}怎么使用？", f"{topic}费用多少？",
                        f"{topic}有什么优势？", f"{topic}和竞品有什么区别？",
                        f"{topic}常见问题有哪些？", f"中国卖家如何使用{topic}？",
                        f"{topic}新手入门指南", f"{topic}最新政策", f"{topic}操作流程"]
                st.session_state["sim_queries"] = base[:num_q]

    with col_q:
        if "sim_queries" in st.session_state and st.session_state["sim_queries"]:
            st.markdown("**问题列表（可编辑）：**")
            edited = []
            for i, q in enumerate(st.session_state["sim_queries"]):
                edited.append(st.text_input(f"Q{i+1}", value=q, key=f"sq_{i}"))
            st.session_state["sim_queries_final"] = edited

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
                        has_gs = "gs.amazon" in answer.lower() or "globalselling" in answer.lower()
                        has_brand = "全球开店" in answer or "Global Selling" in answer
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

        # Save to user directory
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        test_entry = {"id": f"test_{ts}", "topic": topic, "date": ts,
                      "user": user_login, "results": results}

        # Append to user's tests
        existing_tests = json.loads(USER_TESTS_FILE.read_text(encoding="utf-8")) if USER_TESTS_FILE.exists() else []
        existing_tests.insert(0, test_entry)
        USER_TESTS_FILE.write_text(json.dumps(existing_tests, ensure_ascii=False, indent=2), encoding="utf-8")

        # Also save to shared zhice dir
        shared_file = ZHICE_DIR / f"sim_{topic.replace(' ','_')[:20]}_{ts}.json"
        shared_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        log_action(user_login, "test_executed", f"topic={topic}, queries={len(queries)}")

        st.success(f"✅ 测试完成！{len(results)} 条结果已保存。请前往「② 机会点分析」查看。")

        # Quick preview
        for r in results:
            icon = "✅" if r.get("has_official_link") else "❌"
            st.markdown(f"{icon} **{r['query']}** ({PLATFORMS.get(r.get('platform',''), r.get('platform',''))}) — {r.get('answer_length',0)} chars")


# ============================================================
# TAB 2: 机会点分析
# ============================================================
with tab_opps:
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
            "Official Link": "✅" if r.get("has_official_link") else "❌",
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
                st.success(f"✅ 已确认 {len(opp_list)} 个机会点！请前往「③ 执行机会点」。")
        else:
            st.success("🎉 全部覆盖，无缺口！无需额外行动。")


# ============================================================
# TAB 3: 执行机会点
# ============================================================
with tab_execute:
    st.markdown("### 🚀 执行机会点")
    st.caption("针对确认的缺口，产出内容 → 优化 → 准备发布")

    # Load opportunities
    opps = json.loads(USER_OPPS_FILE.read_text(encoding="utf-8")) if USER_OPPS_FILE.exists() else []

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
                        st.rerun()
                    else:
                        st.error(f"❌ 失败: {r1.get('error', '')}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.success("✅ 所有机会点已执行完毕！")


# ============================================================
# TAB 4: 执行状态
# ============================================================
with tab_status:
    st.markdown("### 📋 执行状态")
    st.caption("查看机会点执行进展和内容产出状态")

    # Load opportunities
    opps = json.loads(USER_OPPS_FILE.read_text(encoding="utf-8")) if USER_OPPS_FILE.exists() else []
    actions = json.loads(USER_ACTIONS_FILE.read_text(encoding="utf-8")) if USER_ACTIONS_FILE.exists() else []

    if not opps and not actions:
        st.info("暂无执行记录。")
    else:
        # Status KPIs
        total_opps = len(opps)
        done_opps = sum(1 for o in opps if o.get("status") != "待执行")
        pending_opps = total_opps - done_opps

        kc1, kc2, kc3 = st.columns(3)
        kc1.metric("总机会点", total_opps)
        kc2.metric("已执行", done_opps)
        kc3.metric("待执行", pending_opps)

        # Progress bar
        if total_opps > 0:
            st.progress(done_opps / total_opps)

        st.divider()

        # Opportunity status table
        if opps:
            st.markdown("**机会点状态：**")
            df_opps = pd.DataFrame([{
                "Query": o["query"],
                "Platform": PLATFORMS.get(o.get("platform", ""), o.get("platform", "")),
                "Status": "✅ 已完成" if o.get("status") != "待执行" else "⏳ 待执行",
                "完成时间": o.get("completed_at", "—"),
            } for o in opps])
            st.dataframe(df_opps, use_container_width=True, hide_index=True)

        # Action history
        if actions:
            st.divider()
            st.markdown("**执行历史：**")
            for a in actions[:10]:
                st.markdown(f"- **{a['date']}** — {a['action']} | {a.get('count', '')} 篇 | Batch: {a.get('batch', '')}")


# ============================================================
# TAB 5: 闭环看板（放最后）
# ============================================================
with tab_dashboard:
    st.markdown("### 🔄 闭环看板")
    st.caption("整体效果：测试 → 缺口 → 行动 → 结果")

    # Load all user data
    user_tests = json.loads(USER_TESTS_FILE.read_text(encoding="utf-8")) if USER_TESTS_FILE.exists() else []
    opps = json.loads(USER_OPPS_FILE.read_text(encoding="utf-8")) if USER_OPPS_FILE.exists() else []
    actions = json.loads(USER_ACTIONS_FILE.read_text(encoding="utf-8")) if USER_ACTIONS_FILE.exists() else []

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
