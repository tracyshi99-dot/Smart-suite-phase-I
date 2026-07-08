from pathlib import Path

p = Path(r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\ui\app.py')
lines = p.read_text(encoding='utf-8').splitlines(keepends=True)

# Replace lines 466-541 (0-indexed) with new overview
new_section = '''# ============================================================
# PAGE: Overview
# ============================================================
if page == "\U0001f3e0 \u603b\u89c8":

    _tools = [
        {"id": "zhiku", "icon": "\U0001f4da", "name_en": "Prompt Intelligencer", "name_zh": "\u667a\u5e93 Prompt Intelligencer", "color": "#ffa726", "status": "prod", "page": "\U0001f4da \u667a\u5e93",
         "desc_en": "Connects to 7 mainstream AI search platforms (DeepSeek, Doubao, Kimi, Yuanbao, Qianwen, ChatGPT, Gemini) to capture real-time search phrases with high citation probability.",
         "desc_zh": "\u5bf9\u63a5 7 \u5927\u4e3b\u6d41 AI \u68c0\u7d22\u5e73\u53f0\uff08DeepSeek\u3001\u8c46\u5305\u3001Kimi\u3001\u5143\u5b9d\u3001\u901a\u4e49\u5343\u95ee\u3001ChatGPT\u3001Gemini\uff09\uff0c\u83b7\u53d6\u5b9e\u65f6\u68c0\u7d22\u77ed\u8bed\u3002",
         "caps_en": ["7 AI platforms for real-time trend capture", "Multi-intent query generation", "Bilingual phrase expansion (CN + WW)", "Priority scoring (1-5)"],
         "caps_zh": ["\u5bf9\u63a5 7 \u5927\u4e3b\u6d41 AI \u68c0\u7d22\u5e73\u53f0", "\u591a\u7ef4\u67e5\u8be2\u751f\u6210\uff08\u4fe1\u606f/\u5bfc\u822a/\u4ea4\u6613/\u5bf9\u6bd4\uff09", "\u4e2d\u82f1\u53cc\u8bed\u68c0\u7d22\u77ed\u8bed\u6269\u5c55", "\u4f18\u5148\u7ea7\u8bc4\u5206\u5f15\u64ce (1-5)"],
         "impact": [("7", "AI Platforms"), ("Real-time", "Freshness"), ("3-5x", "Variants"), ("35", "Categories")]},
        {"id": "zhizao", "icon": "\u270d\ufe0f", "name_en": "Content Creator", "name_zh": "\u667a\u9020 Content Creator", "color": "#ffcc02", "status": "prod", "page": "\u270d\ufe0f \u667a\u9020",
         "desc_en": "Produces high-quality GEO-structured content at scale with direct answers, tables, and FAQ modules.",
         "desc_zh": "\u6279\u91cf\u751f\u6210 GEO \u7ed3\u6784\u5316\u5185\u5bb9\uff0c\u542b\u76f4\u63a5\u7b54\u6848\u3001\u8868\u683c\u548c FAQ \u6a21\u5757\u3002",
         "caps_en": ["GEO-first generation (tables + lists + FAQ)", "Knowledge-base grounded (3PKC KMS)", "Inverted pyramid for AI extraction", "Auto brand link insertion"],
         "caps_zh": ["GEO \u4f18\u5148\u751f\u6210\uff08\u8868\u683c+\u5217\u8868+FAQ\uff09", "\u77e5\u8bc6\u5e93\u9a71\u52a8 (3PKC KMS)", "\u9996\u6bb5\u91d1\u5b57\u5854\u539f\u5219", "\u81ea\u52a8\u690d\u5165\u54c1\u724c\u94fe\u63a5"],
         "impact": [("3hrs\\u219210min", "Per Article"), ("800-3000", "Words"), ("100%", "GEO"), ("100+/mo", "Articles")]},
        {"id": "zhiyou", "icon": "\u2b50", "name_en": "Content Optimizer", "name_zh": "\u667a\u4f18 Content Optimizer", "color": "#e91e63", "status": "prod", "page": "\U0001f527 \u667a\u4f18",
         "desc_en": "5-dimension scoring, auto-rewrite based on gaps, and Amazon compliance verification.",
         "desc_zh": "5 \u7ef4\u5ea6\u8bc4\u5206\u3001\u81ea\u52a8\u91cd\u5199\u548c\u4e9a\u9a6c\u900a\u5408\u89c4\u9a8c\u8bc1\u3002",
         "caps_en": ["5-dim AI citation scoring", "Auto rewriting on score gaps", "Amazon compliance auto-fix", "Before/after tracking"],
         "caps_zh": ["5 \u7ef4\u5ea6 AI \u5f15\u7528\u8bc4\u5206", "\u8bc4\u5206\u7f3a\u53e3\u81ea\u52a8\u91cd\u5199", "\u4e9a\u9a6c\u900a\u5408\u89c4\u81ea\u52a8\u4fee\u6b63", "\u4f18\u5316\u524d\u540e\u5bf9\u6bd4\u8ffd\u8e2a"],
         "impact": [("+25%", "Score Uplift"), ("5 dim", "Scoring"), ("100%", "Compliance"), ("Auto", "Rewrite")]},
        {"id": "zhibu", "icon": "\U0001f4e6", "name_en": "Content Publisher", "name_zh": "\u667a\u5e03 Content Publisher", "color": "#29b6f6", "status": "prod", "page": "\U0001f4e6 \u667a\u5e03",
         "desc_en": "Converts content into LEGO CMS JSON format with auto metadata and quality metrics.",
         "desc_zh": "\u8f6c\u6362\u4e3a LEGO CMS JSON \u683c\u5f0f\uff0c\u81ea\u52a8\u586b\u5145\u5143\u6570\u636e\u3002",
         "caps_en": ["LEGO CMS JSON output", "Auto metadata population", "Quality metrics embedded", "Batch + version tracking"],
         "caps_zh": ["LEGO CMS JSON \u8f93\u51fa", "\u5143\u6570\u636e\u81ea\u52a8\u586b\u5145", "\u8d28\u91cf\u6307\u6807\u5d4c\u5165", "\u6279\u91cf\u5904\u7406+\u7248\u672c\u8ffd\u8e2a"],
         "impact": [("30\\u21922 min", "Per Article"), ("0 errors", "Accuracy"), ("Batch", "Processing"), ("JSON", "CMS-Ready")]},
        {"id": "zhichuan", "icon": "\U0001f4e1", "name_en": "Content Distributor", "name_zh": "\u667a\u4f20 Content Distributor", "color": "#26c6da", "status": "dev", "page": None,
         "desc_en": "Automates multi-channel distribution with scheduling and A/B variants.",
         "desc_zh": "\u81ea\u52a8\u5316\u591a\u6e20\u9053\u5206\u53d1\uff0c\u652f\u6301\u5b9a\u65f6\u53d1\u5e03\u548c A/B \u53d8\u4f53\u3002",
         "caps_en": ["Multi-channel distribution", "Scheduled publishing", "A/B variant management", "Cross-platform automation"],
         "caps_zh": ["\u591a\u6e20\u9053\u4e00\u952e\u5206\u53d1", "\u5b9a\u65f6\u53d1\u5e03", "A/B \u53d8\u4f53\u7ba1\u7406", "\u8de8\u5e73\u53f0\u81ea\u52a8\u5316"],
         "impact": [("TBD", "Channels"), ("Auto", "Scheduling"), ("A/B", "Variants"), ("Multi", "Platforms")]},
        {"id": "zhixi", "icon": "\U0001f4ca", "name_en": "Performance Analyzer", "name_zh": "\u667a\u6790 Performance Analyzer", "color": "#ab47bc", "status": "prod", "page": "\U0001f4c8 \u667a\u6790",
         "desc_en": "Real-time E2E data for gap identification, insight discovery, and input effectiveness validation.",
         "desc_zh": "\u5b9e\u65f6\u7aef\u5230\u7aef\u6570\u636e\uff0c\u8bc6\u522b Gap\uff0c\u53d1\u73b0\u6d1e\u5bdf\uff0c\u9a8c\u8bc1 Input \u6709\u6548\u6027\u3002",
         "caps_en": ["Automated multi-dimension reporting", "Gap identification & analysis", "AI citation tracking", "Actionable recommendations"],
         "caps_zh": ["\u591a\u7ef4\u5ea6\u81ea\u52a8\u62a5\u8868", "Gap \u8bc6\u522b\u4e0e\u5206\u6790", "AI \u5f15\u7528\u8ffd\u8e2a", "\u53ef\u6267\u884c\u4f18\u5316\u5efa\u8bae"],
         "impact": [("Real-time", "E2E Data"), ("Input+Output", "Full Funnel"), ("Actionable", "Insights"), ("Validated", "Effectiveness")]},
        {"id": "zhishu", "icon": "\U0001f504", "name_en": "Workflow Orchestrator", "name_zh": "\u667a\u4e2d\u67a2 Workflow Orchestrator", "color": "#ff6b35", "status": "dev", "page": None,
         "desc_en": "Central hub with 7-rule decision engine for automated weekly action plans.",
         "desc_zh": "7 \u6761\u51b3\u7b56\u89c4\u5219\u5f15\u64ce\uff0c\u81ea\u52a8\u751f\u6210\u5468\u5ea6\u884c\u52a8\u8ba1\u5212\u3002",
         "caps_en": ["E2E pipeline orchestration", "7-rule decision engine", "Auto weekly action plans", "Cross-module coordination"],
         "caps_zh": ["\u7aef\u5230\u7aef\u6d41\u6c34\u7ebf\u7f16\u6392", "7 \u6761\u51b3\u7b56\u89c4\u5219\u5f15\u64ce", "\u5468\u5ea6\u81ea\u52a8\u884c\u52a8\u8ba1\u5212", "\u8de8\u6a21\u5757\u6570\u636e\u534f\u8c03"],
         "impact": [("E2E", "Automation"), ("7 rules", "Engine"), ("8 hrs/wk", "Saved"), ("Auto", "Plans")]},
        {"id": "s3", "icon": "\U0001f5c4\ufe0f", "name_en": "S3 Memory Keeper", "name_zh": "S3 Memory Keeper", "color": "#42a5f5", "status": "dev", "page": None,
         "desc_en": "AWS S3-based unified storage for all modules with version control.",
         "desc_zh": "\u57fa\u4e8e S3 \u7684\u5168\u6a21\u5757\u7edf\u4e00\u5b58\u50a8\uff0c\u7248\u672c\u5316\u7ba1\u7406\u3002",
         "caps_en": ["Unified cross-module storage", "Version-controlled repository", "Auto data sync", "Batch archival & retrieval"],
         "caps_zh": ["\u5168\u6a21\u5757\u7edf\u4e00\u5b58\u50a8", "\u7248\u672c\u5316\u4ed3\u5e93", "\u81ea\u52a8\u6570\u636e\u540c\u6b65", "\u6279\u6b21\u5f52\u6863\u4e0e\u68c0\u7d22"],
         "impact": [("\\u221e", "Scalable"), ("99.99%", "Durability"), ("8", "Modules"), ("Versioned", "Audit")]},
    ]

    # Hero
    st.markdown("""
    <div style="text-align:center;padding:30px 0 10px;">
        <div style="width:70px;height:70px;border-radius:50%;background:conic-gradient(from 200deg,#ff6b35,#e91e63,#9c27b0,#2196f3,#00bcd4,#4caf50,#ffeb3b,#ff6b35);margin:0 auto 14px;text-align:center;line-height:70px;font-size:28px;font-weight:900;color:#fff;">\\u667a</div>
        <h1 style="font-size:36px;font-weight:800;background:linear-gradient(135deg,#ff6b35,#e91e63,#9c27b0,#2196f3,#00bcd4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:0;">\\u667a\\u7cfb\\u5217 Smart Suite</h1>
        <p style="color:#8892b0;font-size:15px;margin-top:10px;">From fragmented content workflows to AI-powered end-to-end GEO content intelligence.</p>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    st.markdown("""
    <div style="display:flex;justify-content:center;gap:40px;margin:20px 0 30px;flex-wrap:wrap;">
        <div style="text-align:center;"><div style="font-size:26px;font-weight:700;color:#00bcd4;">8</div><div style="font-size:11px;color:#8892b0;">AI Tools</div></div>
        <div style="text-align:center;"><div style="font-size:26px;font-weight:700;color:#00bcd4;">7+</div><div style="font-size:11px;color:#8892b0;">AI Search Platforms</div></div>
        <div style="text-align:center;"><div style="font-size:26px;font-weight:700;color:#00bcd4;">+65%</div><div style="font-size:11px;color:#8892b0;">YTD Reg Start YoY</div></div>
        <div style="text-align:center;"><div style="font-size:26px;font-weight:700;color:#00bcd4;">+8,400 bps</div><div style="font-size:11px;color:#8892b0;">vs SSR Total Swing</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Render tools
    for tool in _tools:
        _name = tool["name_en"] if is_en else tool["name_zh"]
        _desc = tool["desc_en"] if is_en else tool["desc_zh"]
        _caps = tool["caps_en"] if is_en else tool["caps_zh"]
        badge_color = "#4caf50" if tool["status"] == "prod" else "#ffa726"
        badge_text = "Production" if tool["status"] == "prod" else "In Development"
        caps_html = "".join(f\'<span style="color:#00bcd4;font-weight:700;">+</span> {c}<br/>\' for c in _caps)
        impact_html = "".join(
            f\'<div style="background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);border-radius:10px;padding:14px;text-align:center;">\'
            f\'<div style="font-size:18px;font-weight:700;color:{tool["color"]};">{v}</div>\'
            f\'<div style="font-size:10px;color:#8892b0;text-transform:uppercase;">{l}</div></div>\'
            for v, l in tool["impact"]
        )

        st.markdown(f"""
        <div style="padding:16px 0;">
            <div style="display:grid;grid-template-columns:1.2fr 1fr;gap:30px;align-items:start;">
                <div>
                    <span style="display:inline-block;padding:3px 10px;border-radius:12px;font-size:11px;background:{badge_color}20;border:1px solid {badge_color}50;color:{badge_color};margin-bottom:8px;">{badge_text}</span>
                    <h2 style="font-size:24px;font-weight:800;color:{tool[\'color\']};margin:0 0 6px;">{tool[\'icon\']} {_name}</h2>
                    <p style="font-size:13px;color:#8892b0;line-height:1.7;margin-bottom:10px;">{_desc}</p>
                    <div style="font-size:12px;color:#8892b0;line-height:1.8;">{caps_html}</div>
                </div>
                <div>
                    <p style="font-size:10px;color:#8892b0;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Business Impact</p>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">{impact_html}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if tool["status"] == "prod" and tool["page"]:
            if st.button(f"\\U0001f680 Launch {_name}", key=f"launch_{tool[\'id\']}"):
                st.session_state["nav_radio"] = tool["page"]
                st.rerun()
        else:
            st.markdown("*\\U0001f6a7 Coming Soon*")
        st.divider()

    st.caption("Smart Suite \\u2013 AI-Powered GEO Content Intelligence | Built by GEO Team \\u00b7 Phase I \\u00b7 2025-2026")

    # (End of overview page)

'''

before = lines[:466]
after = lines[542:]
new_lines = before + [new_section] + after
p.write_text(''.join(new_lines), encoding='utf-8')
print(f"Done. New line count: {len(''.join(new_lines).splitlines())}")
