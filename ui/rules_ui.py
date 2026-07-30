"""
Rules Editor UI Components for Smart Suite.
Renders configurable detection rules in 智库 and 智测 pages.
"""
import streamlit as st
import json
import pandas as pd
from datetime import datetime
from detection_rules import (
    load_rules, save_rules, DEFAULT_RULES,
    get_brand_keywords, get_official_link_patterns, get_zhiku_seeds,
)


def render_zhiku_rules(current_user: str, is_en: bool = False):
    """Render rules section for 智库 page — seed management + download."""
    st.divider()
    with st.expander("⚙️ " + ("Query Rules & Seeds" if is_en else "检索规则与种子词管理"), expanded=False):
        rules = load_rules(current_user)

        # --- Zhiku Seeds ---
        st.markdown("#### " + ("Search Seeds" if is_en else "检索种子词"))
        st.caption("Core seeds for query expansion. Each seed generates 10-15 search phrases."
                   if is_en else "核心种子词，每个种子可裂变生成 10-15 条检索短语。")

        seeds = rules.get("zhiku_seeds", DEFAULT_RULES["zhiku_seeds"])
        current_seeds = seeds.get("seeds", [])

        # Display as editable text area
        seeds_text = st.text_area(
            "Seeds (one per line)" if is_en else "种子词（每行一个）",
            value="\n".join(current_seeds),
            height=200,
            key="zhiku_seeds_edit",
        )

        col_save, col_reset = st.columns(2)
        with col_save:
            if st.button("💾 " + ("Save Seeds" if is_en else "保存种子词"), key="save_zhiku_seeds", type="primary"):
                new_seeds = [s.strip() for s in seeds_text.strip().split("\n") if s.strip()]
                rules.setdefault("zhiku_seeds", {})["seeds"] = new_seeds
                save_rules(rules, current_user)
                st.success(f"✅ {'Saved' if is_en else '已保存'} {len(new_seeds)} {'seeds' if is_en else '个种子词'}")
                st.rerun()
        with col_reset:
            if st.button("🔄 " + ("Reset to Default" if is_en else "恢复默认"), key="reset_zhiku_seeds"):
                rules["zhiku_seeds"] = DEFAULT_RULES["zhiku_seeds"].copy()
                save_rules(rules, current_user)
                st.success("✅ " + ("Reset done" if is_en else "已恢复默认"))
                st.rerun()

        # --- Brand Mention Keywords (preview) ---
        st.markdown("---")
        st.markdown("#### " + ("Brand Mention Keywords (preview)" if is_en else "品牌提及关键词（预览）"))
        brand_kws = get_brand_keywords(current_user)
        st.caption(f"{'Current keywords' if is_en else '当前关键词'}: {', '.join(brand_kws[:10])}{'...' if len(brand_kws) > 10 else ''}")
        st.caption("→ " + ("Edit in 智测 Rules tab" if is_en else "完整编辑请到智测的 Rules 标签"))

        # --- Rules metadata ---
        st.markdown("---")
        st.caption(f"{'Last updated' if is_en else '最后更新'}: {rules.get('updated_at', '—')} by {rules.get('updated_by', '—')}")


def render_zhiku_download(current_user: str, is_en: bool = False, df_zhiku=None):
    """Render download button for full query list in 智库."""
    if df_zhiku is None or df_zhiku.empty:
        return

    st.divider()
    col_dl, col_info = st.columns([1, 3])
    with col_dl:
        csv_data = df_zhiku.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="⬇️ " + ("Download Full Query List" if is_en else "下载完整检索短语列表"),
            data=csv_data,
            file_name=f"zhiku_queries_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key="dl_zhiku_full_list",
            type="primary",
        )
    with col_info:
        st.caption(f"{'Total' if is_en else '共'} {len(df_zhiku)} {'phrases' if is_en else '条短语'} | "
                   f"CSV UTF-8 {'format' if is_en else '格式'}")


def render_zhice_rules(current_user: str, is_en: bool = False):
    """Render rules section for 智测 page — brand mention + official link rules."""
    st.divider()
    with st.expander("⚙️ " + ("Detection Rules" if is_en else "判定规则配置"), expanded=False):
        rules = load_rules(current_user)

        tab_brand, tab_link = st.tabs([
            "🏷️ " + ("Brand Mention Rules" if is_en else "品牌提及判定"),
            "🔗 " + ("Official Link Rules" if is_en else "官方链接判定"),
        ])

        # --- Brand Mention Tab ---
        with tab_brand:
            st.markdown("#### " + ("Brand Mention Detection" if is_en else "品牌提及判定规则"))
            st.caption("Logic: AI answer contains 「亚马逊」or「Amazon」→ Brand Mention. Special overrides available."
                       if is_en else "逻辑：AI 回答中有「亚马逊」或「Amazon」→ 判定为品牌提及。有特殊要求可单独配置。")

            brand_rules = rules.get("brand_mention", DEFAULT_RULES["brand_mention"])
            current_keywords = brand_rules.get("keywords", [])

            # Editable keyword list
            brand_text = st.text_area(
                "Brand keywords (one per line)" if is_en else "品牌关键词（每行一个）",
                value="\n".join(current_keywords),
                height=150,
                key="brand_keywords_edit",
                help="AI answer must contain one of these brand words AND the query's core keyword to count as brand mention"
                     if is_en else "AI 回答必须同时包含这里的品牌词 + 检索短语核心词，才判定为品牌提及",
            )

            # Special overrides
            st.markdown("**" + ("Special Overrides" if is_en else "特殊规则覆盖") + "：**")
            st.caption("For specific queries that need different detection rules"
                       if is_en else "针对特定检索短语可设置不同判定标准")
            special_overrides = brand_rules.get("special_overrides", [])
            special_text = st.text_area(
                "Special rules (JSON format, one override per line)" if is_en else "特殊规则（JSON 格式）",
                value=json.dumps(special_overrides, ensure_ascii=False, indent=2) if special_overrides else "[]",
                height=100,
                key="brand_special_edit",
                help='Example: [{"query_pattern": "FBA", "keywords": ["FBA", "亚马逊物流"]}]',
            )

            # Save
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("💾 " + ("Save Brand Rules" if is_en else "保存品牌规则"), key="save_brand_rules", type="primary"):
                    new_keywords = [k.strip() for k in brand_text.strip().split("\n") if k.strip()]
                    rules.setdefault("brand_mention", {})["keywords"] = new_keywords
                    # Parse special overrides
                    try:
                        new_special = json.loads(special_text) if special_text.strip() else []
                        rules["brand_mention"]["special_overrides"] = new_special
                    except json.JSONDecodeError:
                        st.error("⚠️ Special rules JSON format error" if is_en else "⚠️ 特殊规则 JSON 格式错误")
                    save_rules(rules, current_user)
                    st.success(f"✅ {'Saved' if is_en else '已保存'} {len(new_keywords)} {'keywords' if is_en else '个关键词'}")
                    st.rerun()
            with col_b2:
                if st.button("🔄 " + ("Reset Brand Rules" if is_en else "恢复默认"), key="reset_brand_rules"):
                    rules["brand_mention"] = DEFAULT_RULES["brand_mention"].copy()
                    save_rules(rules, current_user)
                    st.success("✅ " + ("Reset done" if is_en else "已恢复默认"))
                    st.rerun()

        # --- Official Link Tab ---
        with tab_link:
            st.markdown("#### " + ("Official Link Detection" if is_en else "官方链接判定规则"))
            st.caption("Default: any .amazon domain in AI answer → Official Link. Special rules can override."
                       if is_en else "默认：AI 回答中包含 .amazon 域名 → 判定为官方链接。有特殊要求的可单独设置。")

            link_rules = rules.get("official_link", DEFAULT_RULES["official_link"])
            current_patterns = link_rules.get("link_patterns", [])

            # Editable link patterns
            link_text = st.text_area(
                "Official link patterns (one per line)" if is_en else "官方链接模式（每行一个）",
                value="\n".join(current_patterns),
                height=100,
                key="link_patterns_edit",
                help="Default: .amazon covers all Amazon domains. Add more patterns if needed."
                     if is_en else "默认 .amazon 覆盖所有亚马逊域名。如需更多模式可添加。",
            )

            # Special overrides
            st.markdown("**" + ("Special Overrides" if is_en else "特殊规则覆盖") + "：**")
            st.caption("For specific queries that need different link detection patterns"
                       if is_en else "针对特定检索短语可设置不同的链接判定模式")
            link_special = link_rules.get("special_overrides", [])
            link_special_text = st.text_area(
                "Special rules (JSON format)" if is_en else "特殊规则（JSON 格式）",
                value=json.dumps(link_special, ensure_ascii=False, indent=2) if link_special else "[]",
                height=100,
                key="link_special_edit",
                help='Example: [{"query_pattern": "FBA", "patterns": ["amazon.com/fba", "sellercentral.amazon.com"]}]',
            )

            # Save
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                if st.button("💾 " + ("Save Link Rules" if is_en else "保存链接规则"), key="save_link_rules", type="primary"):
                    new_patterns = [p.strip() for p in link_text.strip().split("\n") if p.strip()]
                    rules.setdefault("official_link", {})["link_patterns"] = new_patterns
                    # Parse special overrides
                    try:
                        new_link_special = json.loads(link_special_text) if link_special_text.strip() else []
                        rules["official_link"]["special_overrides"] = new_link_special
                    except json.JSONDecodeError:
                        st.error("⚠️ Special rules JSON format error" if is_en else "⚠️ 特殊规则 JSON 格式错误")
                    save_rules(rules, current_user)
                    st.success(f"✅ {'Saved' if is_en else '已保存'} {len(new_patterns)} {'patterns' if is_en else '个模式'}")
                    st.rerun()
            with col_l2:
                if st.button("🔄 " + ("Reset Link Rules" if is_en else "恢复默认"), key="reset_link_rules"):
                    rules["official_link"] = DEFAULT_RULES["official_link"].copy()
                    save_rules(rules, current_user)
                    st.success("✅ " + ("Reset done" if is_en else "已恢复默认"))
                    st.rerun()

        # --- Rules metadata ---
        st.markdown("---")
        st.caption(f"{'Last updated' if is_en else '最后更新'}: {rules.get('updated_at', '—')} | "
                   f"{'by' if is_en else '修改人'}: {rules.get('updated_by', '—')}")
        st.caption("💡 " + (
            "Rules are per-user. Each user can customize their own detection criteria."
            if is_en else
            "规则按用户独立保存，每人可自定义自己的判定标准。"
        ))
