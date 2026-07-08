SIMULATE_CODE = '''
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
'''

DASHBOARD_CODE = '''
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
'''

# Write to file
from pathlib import Path
p = Path(r'c:\\Users\\yujiashi\\Desktop\\SmartSuite_Phase1\\ui\\app_zhice.py')
content = p.read_text(encoding='utf-8')
content = content.replace('PLACEHOLDER_SIMULATE', SIMULATE_CODE.strip())
content = content.replace('PLACEHOLDER_DASHBOARD', DASHBOARD_CODE.strip())
p.write_text(content, encoding='utf-8')
print("Done - replaced placeholders")
