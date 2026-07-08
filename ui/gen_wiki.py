from pathlib import Path

logo_b64 = Path(r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\ui\logo_b64.txt').read_text()

tools = [
    {'id':'zhiku','name':'&#26234;&#24211; Prompt Intelligencer','color':'#ffa726','status':'prod',
     'desc':'Connects to 7 mainstream AI search platforms (DeepSeek, Doubao, Kimi, Yuanbao, Qianwen, ChatGPT, Gemini) to capture real-time, high-precision search phrases with high citation probability.',
     'caps':['7 AI platforms for real-time trend capture','Multi-intent query generation','Bilingual phrase expansion (CN + WW)','Priority scoring (1-5) for high-value filtering'],
     'impact':[('7','AI Platforms'),('Real-time','Phrase Freshness'),('3-5x','Variants/Topic'),('35','Categories')]},
    {'id':'zhizao','name':'&#26234;&#36896; Content Creator','color':'#ffcc02','status':'prod',
     'desc':'Produces high-quality GEO-structured content at scale. Each article maximizes AI engine citation probability with direct answers, tables, and FAQ modules.',
     'caps':['GEO-first generation (tables + lists + FAQ)','Knowledge-base grounded (3PKC KMS)','Inverted pyramid for AI extraction','Auto brand link insertion'],
     'impact':[('3hrs to 10min','Per Article'),('800-3000','Words/Article'),('100%','GEO Compliance'),('100+/mo','Articles Monthly')]},
    {'id':'zhiyou','name':'&#26234;&#20248; Content Optimizer','color':'#e91e63','status':'prod',
     'desc':'5-dimension scoring, auto-rewrite based on gaps, and Amazon compliance verification in one pipeline.',
     'caps':['5-dim AI citation scoring','Auto rewriting on score gaps','Amazon compliance auto-fix','Before/after tracking'],
     'impact':[('+25%','Score Uplift'),('5 dim','Scoring'),('100%','Compliance'),('Auto','Score-Rewrite-Verify')]},
    {'id':'zhibu','name':'&#26234;&#24067; Content Publisher','color':'#29b6f6','status':'prod',
     'desc':'Converts optimized content into LEGO CMS JSON format with auto metadata and quality metrics.',
     'caps':['LEGO CMS JSON output','Auto metadata population','Quality metrics embedded','Batch + version tracking'],
     'impact':[('30 to 2 min','Per Article'),('0 errors','Accuracy'),('Batch','Processing'),('JSON','CMS-Ready')]},
    {'id':'zhichuan','name':'&#26234;&#20256; Content Distributor','color':'#26c6da','status':'dev',
     'desc':'Automates multi-channel distribution with scheduling, A/B variants, and cross-platform workflows.',
     'caps':['Multi-channel one-click distribution','Scheduled publishing','A/B variant management','Cross-platform automation'],
     'impact':[('TBD','Channels'),('Auto','Scheduling'),('A/B','Variants'),('Multi','Platforms')]},
    {'id':'zhixi','name':'&#26234;&#26512; Performance Analyzer','color':'#ab47bc','status':'prod',
     'desc':'Real-time E2E data connection for gap identification, insight discovery, and input effectiveness validation.',
     'caps':['Automated multi-dimension reporting','Gap identification and analysis','AI citation tracking','Actionable optimization recommendations'],
     'impact':[('Real-time','E2E Data'),('Input+Output','Full Funnel'),('Actionable','Insights'),('Validated','Input Effectiveness')]},
    {'id':'zhishu','name':'&#26234;&#20013;&#26530; Workflow Orchestrator','color':'#ff6b35','status':'dev',
     'desc':'Central hub connecting all modules with 7-rule decision engine for automated weekly action plans.',
     'caps':['E2E pipeline orchestration','7-rule decision engine','Auto weekly action plans','Cross-module coordination'],
     'impact':[('E2E','Full Automation'),('7 rules','Decision Engine'),('8 hrs/wk','Time Saved'),('Auto','Action Plans')]},
    {'id':'s3','name':'S3 Memory Keeper','color':'#42a5f5','status':'dev',
     'desc':'AWS S3-based storage serving as unified data foundation for all modules with version control.',
     'caps':['Unified cross-module storage','Version-controlled repository','Auto data sync','Batch archival and retrieval'],
     'impact':[('Infinite','Scalable'),('99.99%','Durability'),('8 modules','Connected'),('Versioned','Audit Trail')]},
]

nav_items = ''.join(
    f'<a href="#{t["id"]}" style="padding:8px 14px;border-radius:6px;font-size:13px;font-weight:500;color:#00bcd4;text-decoration:none;white-space:nowrap;border:1px solid #00bcd430;background:rgba(0,188,212,.08);">{t["name"]}</a>'
    for t in tools
)

sections = ''
for t in tools:
    if t['status'] == 'prod':
        badge = '<span style="display:inline-block;padding:3px 10px;border-radius:12px;font-size:11px;background:rgba(76,175,80,.15);border:1px solid rgba(76,175,80,.3);color:#4caf50;margin-bottom:12px;">Production</span>'
    else:
        badge = '<span style="display:inline-block;padding:3px 10px;border-radius:12px;font-size:11px;background:rgba(255,167,38,.15);border:1px solid rgba(255,167,38,.3);color:#ffa726;margin-bottom:12px;">In Development</span>'

    caps_html = ''.join(f'<p style="margin:4px 0;color:#8892b0;font-size:12px;"><span style="color:#00bcd4;font-weight:700;">+</span> {c}</p>' for c in t['caps'])

    impact_html = ''.join(
        f'<div style="background:#1a1d2e;border:1px solid #2a2f4a;border-radius:10px;padding:16px;"><div style="font-size:18px;font-weight:700;color:{t["color"]};">{v}</div><div style="font-size:10px;color:#7a82a0;text-transform:uppercase;">{l}</div></div>'
        for v, l in t['impact']
    )

    if t['status'] == 'prod':
        cta = f'<span style="display:inline-block;padding:7px 16px;border-radius:6px;font-size:12px;font-weight:500;color:{t["color"]};background:rgba(255,255,255,.04);border:1px solid {t["color"]}40;">&#9654; Use via sidebar navigation</span>'
    else:
        cta = '<span style="display:inline-block;padding:7px 16px;border-radius:6px;font-size:12px;font-weight:600;color:#5a6380;background:rgba(255,255,255,.03);border:1px solid #1e2030;">Coming Soon</span>'

    sections += f'''
<div id="{t['id']}" style="padding:14px 8px;border-top:1px solid #2a2f4a;">
<div style="display:grid;grid-template-columns:1.3fr 1fr;gap:20px;">
<div>
{badge}
<h2 style="font-size:28px;font-weight:800;color:{t['color']};margin:0 0 4px;">{t['name']}</h2>
<p style="font-size:13px;color:#8892b0;line-height:1.7;margin:10px 0 14px;">{t['desc']}</p>
{caps_html}
<div style="margin-top:16px;">{cta}</div>
<p style="margin-top:10px;font-size:11px;color:#5a6380;">Contact <strong>@yujiashi</strong> to request access</p>
</div>
<div>
<p style="font-size:11px;color:#5a6380;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">BUSINESS IMPACT</p>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">{impact_html}</div>
</div>
</div>
</div>'''

html = f'''<div style="font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;background:#0f1117;color:#fff;padding:0;border-radius:12px;max-width:100%;margin:0 auto;">

<div style="text-align:center;padding:16px 16px 8px;">
<img src="/bin/download/SmartSuite-GEO/WebHome/SmartSuite%20Logo.png" style="width:80px;height:80px;margin:0 auto 12px;display:block;border-radius:50%;" />
<h1 style="font-size:36px;font-weight:800;background:linear-gradient(135deg,#ff6b35,#e91e63,#9c27b0,#2196f3,#00bcd4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:0;">&#26234;&#31995;&#21015; Smart Suite</h1>
<p style="color:#8892b0;font-size:15px;margin-top:8px;max-width:600px;margin-left:auto;margin-right:auto;">From fragmented content workflows to AI-powered end-to-end GEO content intelligence, optimization, and performance tracking.</p>
</div>

<div style="display:flex;justify-content:center;gap:32px;margin:16px 0 20px;flex-wrap:wrap;">
<div style="text-align:center;"><div style="font-size:24px;font-weight:700;color:#00bcd4;">8</div><div style="font-size:11px;color:#5a6380;">AI Tools</div></div>
<div style="text-align:center;"><div style="font-size:24px;font-weight:700;color:#00bcd4;">7+</div><div style="font-size:11px;color:#5a6380;">AI Search Platforms</div></div>
<div style="text-align:center;"><div style="font-size:24px;font-weight:700;color:#00bcd4;">+65%</div><div style="font-size:11px;color:#5a6380;">YTD Reg Start YoY</div></div>
<div style="text-align:center;"><div style="font-size:24px;font-weight:700;color:#00bcd4;">+8,400 bps</div><div style="font-size:11px;color:#5a6380;">vs SSR Total Swing</div></div>
</div>

<div style="margin:0 8px 16px;background:#1a1d2e;border-radius:12px;border:1px solid #2a2f4a;padding:32px 24px;">
<p style="font-size:12px;color:#5a6380;text-transform:uppercase;letter-spacing:1px;margin-bottom:20px;text-align:center;">End-to-End Closed-Loop Workflow</p>
<div style="display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:nowrap;margin-bottom:20px;overflow-x:auto;">
<a href="#zhiku" style="text-decoration:none;background:#0f1117;border:1px solid #ffa726;border-radius:8px;padding:8px 14px;text-align:center;min-width:fit-content;display:inline-block;"><div style="font-size:11px;color:#ffa726;font-weight:600;">Intelligencer</div></a>
<div style="color:#8892b0;font-size:18px;font-weight:700;">&#10132;</div>
<a href="#zhizao" style="text-decoration:none;background:#0f1117;border:1px solid #ffcc02;border-radius:8px;padding:8px 14px;text-align:center;min-width:fit-content;display:inline-block;"><div style="font-size:11px;color:#ffcc02;font-weight:600;">Creator</div></a>
<div style="color:#8892b0;font-size:18px;font-weight:700;">&#10132;</div>
<a href="#zhiyou" style="text-decoration:none;background:#0f1117;border:1px solid #e91e63;border-radius:8px;padding:8px 14px;text-align:center;min-width:fit-content;display:inline-block;"><div style="font-size:11px;color:#e91e63;font-weight:600;">Optimizer</div></a>
<div style="color:#8892b0;font-size:18px;font-weight:700;">&#10132;</div>
<a href="#zhibu" style="text-decoration:none;background:#0f1117;border:1px solid #29b6f6;border-radius:8px;padding:8px 14px;text-align:center;min-width:fit-content;display:inline-block;"><div style="font-size:11px;color:#29b6f6;font-weight:600;">Publisher</div></a>
<div style="color:#8892b0;font-size:18px;font-weight:700;">&#10132;</div>
<a href="#zhichuan" style="text-decoration:none;background:#0f1117;border:1px solid #26c6da;border-radius:8px;padding:8px 14px;text-align:center;min-width:fit-content;display:inline-block;"><div style="font-size:11px;color:#26c6da;font-weight:600;">Distributor</div></a>
<div style="color:#8892b0;font-size:18px;font-weight:700;">&#10132;</div>
<a href="#zhixi" style="text-decoration:none;background:#0f1117;border:1px solid #ab47bc;border-radius:8px;padding:8px 14px;text-align:center;min-width:fit-content;display:inline-block;"><div style="font-size:11px;color:#ab47bc;font-weight:600;">Analyzer</div></a>
<div style="color:#8892b0;font-size:18px;font-weight:700;">&#10132;</div>
<a href="#zhishu" style="text-decoration:none;background:#0f1117;border:1px solid #ff6b35;border-radius:8px;padding:8px 14px;text-align:center;min-width:fit-content;display:inline-block;"><div style="font-size:11px;color:#ff6b35;font-weight:600;">Orchestrator</div></a>
</div>
<div style="text-align:center;margin-top:12px;padding:10px;background:#0f1117;border-radius:8px;border:1px solid #2a2f4a;">
<p style="color:#00bcd4;font-size:12px;font-weight:600;margin:0;">&#8635; Analyzer feeds insights to Orchestrator &#8594; Orchestrator triggers Intelligencer/Creator/Optimizer/Publisher/Distributor to improve performance and fill gaps</p>
</div>
</div>

{sections}

<div style="padding:24px 40px;border-top:1px solid #1e2030;text-align:center;">
<p style="color:#5a6380;font-size:11px;">Smart Suite - AI-Powered GEO Content Intelligence | Built by GEO Team | Contact @yujiashi</p>
</div>

</div>'''

out = Path(r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\ui\smart-suite-wiki.html')
out.write_text(html, encoding='utf-8')
print(f"Generated EN: {len(html)} chars -> {out}")

# Generate ZH version
nav_items_zh = ''.join(
    f'<a href="#{t["id"]}" style="padding:8px 14px;border-radius:6px;font-size:13px;font-weight:500;color:#00bcd4;text-decoration:none;white-space:nowrap;border:1px solid #00bcd430;background:rgba(0,188,212,.08);">{t["name"].split(" ")[0] if " " in t["name"] else t["name"]}</a>'
    for t in tools
)

sections_zh = ''
zh_names = {'zhiku':'\u667a\u5e93','zhizao':'\u667a\u9020','zhiyou':'\u667a\u4f18','zhibu':'\u667a\u5e03','zhichuan':'\u667a\u4f20','zhixi':'\u667a\u6790','zhishu':'\u667a\u4e2d\u67a2','s3':'S3'}
zh_descs = {
    'zhiku': '\u5bf9\u63a5 7 \u5927\u4e3b\u6d41 AI \u68c0\u7d22\u5e73\u53f0\uff08DeepSeek\u3001\u8c46\u5305\u3001Kimi\u3001\u5143\u5b9d\u3001\u901a\u4e49\u5343\u95ee\u3001ChatGPT\u3001Gemini\uff09\uff0c\u83b7\u53d6\u5b9e\u65f6\u6027\u66f4\u5f3a\u3001\u76f8\u5bf9\u7cbe\u51c6\u7684\u68c0\u7d22\u77ed\u8bed\u3002',
    'zhizao': '\u57fa\u4e8e\u9ad8\u4ef7\u503c\u68c0\u7d22\u77ed\u8bed\u6279\u91cf\u751f\u6210\u9ad8\u8d28\u91cf GEO \u7ed3\u6784\u5316\u5185\u5bb9\uff0c\u6700\u5927\u5316 AI \u5f15\u64ce\u5f15\u7528\u6982\u7387\u3002',
    'zhiyou': '5 \u7ef4\u5ea6\u8bc4\u5206\u3001\u57fa\u4e8e\u8bc4\u5206\u7f3a\u53e3\u81ea\u52a8\u91cd\u5199\u3001\u4e9a\u9a6c\u900a\u5408\u89c4\u9a8c\u8bc1\u4e00\u4f53\u5316\u6d41\u7a0b\u3002',
    'zhibu': '\u5c06\u4f18\u5316\u5185\u5bb9\u8f6c\u6362\u4e3a LEGO CMS JSON \u683c\u5f0f\uff0c\u81ea\u52a8\u586b\u5145\u5143\u6570\u636e\u548c\u8d28\u91cf\u6307\u6807\u3002',
    'zhichuan': '\u81ea\u52a8\u5316\u591a\u6e20\u9053\u5206\u53d1\uff0c\u652f\u6301\u5b9a\u65f6\u53d1\u5e03\u548c A/B \u53d8\u4f53\u7ba1\u7406\u3002',
    'zhixi': '\u5b9e\u65f6\u7aef\u5230\u7aef\u6570\u636e\u5bf9\u63a5\uff0c\u8bc6\u522b Gap\uff0c\u53d1\u73b0\u6d1e\u5bdf\uff0c\u9a8c\u8bc1 Input \u6709\u6548\u6027\u3002',
    'zhishu': '\u5168\u6d41\u7a0b\u7f16\u6392\u4e2d\u5fc3\uff0c\u5185\u7f6e 7 \u6761\u51b3\u7b56\u89c4\u5219\u5f15\u64ce\uff0c\u81ea\u52a8\u751f\u6210\u5468\u5ea6\u884c\u52a8\u8ba1\u5212\u3002',
    's3': '\u57fa\u4e8e AWS S3 \u7684\u5168\u6a21\u5757\u7edf\u4e00\u5b58\u50a8\uff0c\u7248\u672c\u5316\u7ba1\u7406\u3002',
}
zh_caps = {
    'zhiku': ['\u5bf9\u63a5 7 \u5927\u4e3b\u6d41 AI \u68c0\u7d22\u5e73\u53f0', '\u591a\u7ef4\u67e5\u8be2\u751f\u6210', '\u4e2d\u82f1\u53cc\u8bed\u68c0\u7d22\u77ed\u8bed\u6269\u5c55', '\u4f18\u5148\u7ea7\u8bc4\u5206 (1-5)'],
    'zhizao': ['GEO \u4f18\u5148\u751f\u6210', '\u77e5\u8bc6\u5e93\u9a71\u52a8 (3PKC KMS)', '\u9996\u6bb5\u91d1\u5b57\u5854\u539f\u5219', '\u81ea\u52a8\u690d\u5165\u54c1\u724c\u94fe\u63a5'],
    'zhiyou': ['5 \u7ef4\u5ea6 AI \u5f15\u7528\u8bc4\u5206', '\u8bc4\u5206\u7f3a\u53e3\u81ea\u52a8\u91cd\u5199', '\u4e9a\u9a6c\u900a\u5408\u89c4\u81ea\u52a8\u4fee\u6b63', '\u4f18\u5316\u524d\u540e\u5bf9\u6bd4'],
    'zhibu': ['LEGO CMS JSON \u8f93\u51fa', '\u5143\u6570\u636e\u81ea\u52a8\u586b\u5145', '\u8d28\u91cf\u6307\u6807\u5d4c\u5165', '\u6279\u91cf+\u7248\u672c\u8ffd\u8e2a'],
    'zhichuan': ['\u591a\u6e20\u9053\u4e00\u952e\u5206\u53d1', '\u5b9a\u65f6\u53d1\u5e03', 'A/B \u53d8\u4f53\u7ba1\u7406', '\u8de8\u5e73\u53f0\u81ea\u52a8\u5316'],
    'zhixi': ['\u591a\u7ef4\u5ea6\u81ea\u52a8\u62a5\u8868', 'Gap \u8bc6\u522b\u4e0e\u5206\u6790', 'AI \u5f15\u7528\u8ffd\u8e2a', '\u53ef\u6267\u884c\u4f18\u5316\u5efa\u8bae'],
    'zhishu': ['\u7aef\u5230\u7aef\u6d41\u6c34\u7ebf\u7f16\u6392', '7 \u6761\u51b3\u7b56\u89c4\u5219\u5f15\u64ce', '\u5468\u5ea6\u81ea\u52a8\u884c\u52a8\u8ba1\u5212', '\u8de8\u6a21\u5757\u6570\u636e\u534f\u8c03'],
    's3': ['\u5168\u6a21\u5757\u7edf\u4e00\u5b58\u50a8', '\u7248\u672c\u5316\u4ed3\u5e93', '\u81ea\u52a8\u6570\u636e\u540c\u6b65', '\u6279\u6b21\u5f52\u6863\u4e0e\u68c0\u7d22'],
}

zh_impact = {
    'zhiku': [('7','AI 平台'),('Real-time','短语时效'),('3-5x','每主题变体'),('35','话题类别')],
    'zhizao': [('3hrs→10min','单篇生成'),('800-3000','每篇字数'),('100%','GEO 合规'),('100+/月','月产文章')],
    'zhiyou': [('+25%','评分提升'),('5 维','评分维度'),('100%','合规通过'),('自动','评分→重写→验证')],
    'zhibu': [('30→2min','单篇发布'),('0 错误','格式准确'),('批量','多文章处理'),('JSON','CMS 就绪')],
    'zhichuan': [('待定','渠道数'),('自动','定时发布'),('A/B','变体测试'),('多平台','集成')],
    'zhixi': [('实时','E2E 数据'),('Input+Output','全漏斗'),('可执行','洞察发现'),('已验证','Input 有效性')],
    'zhishu': [('E2E','全流程自动'),('7 条','决策引擎'),('8h/周','节省人工'),('自动','行动计划')],
    's3': [('∞','弹性扩展'),('99.99%','持久性'),('8模块','数据互通'),('版本化','完整审计')],
}

for t in tools:
    tid = t['id']
    if t['status'] == 'prod':
        badge = '<span style="display:inline-block;padding:3px 10px;border-radius:12px;font-size:11px;background:rgba(76,175,80,.15);border:1px solid rgba(76,175,80,.3);color:#4caf50;margin-bottom:12px;">\u5df2\u4e0a\u7ebf</span>'
    else:
        badge = '<span style="display:inline-block;padding:3px 10px;border-radius:12px;font-size:11px;background:rgba(255,167,38,.15);border:1px solid rgba(255,167,38,.3);color:#ffa726;margin-bottom:12px;">\u5f00\u53d1\u4e2d</span>'
    caps_html = ''.join(f'<p style="margin:4px 0;color:#8892b0;font-size:12px;"><span style="color:#00bcd4;font-weight:700;">+</span> {c}</p>' for c in zh_caps[tid])
    impact_data = zh_impact.get(tid, t['impact'])
    impact_html = ''.join(
        f'<div style="background:#1a1d2e;border:1px solid #2a2f4a;border-radius:10px;padding:16px;"><div style="font-size:18px;font-weight:700;color:{t["color"]};">{v}</div><div style="font-size:10px;color:#7a82a0;text-transform:uppercase;">{l}</div></div>'
        for v, l in impact_data
    )
    if t['status'] == 'prod':
        cta = f'<span style="display:inline-block;padding:7px 16px;border-radius:6px;font-size:12px;font-weight:500;color:{t["color"]};background:rgba(255,255,255,.04);border:1px solid {t["color"]}40;">&#9654; \u901a\u8fc7\u5de6\u4fa7\u5bfc\u822a\u4f7f\u7528</span>'
    else:
        cta = '<span style="display:inline-block;padding:7px 16px;border-radius:6px;font-size:12px;font-weight:600;color:#5a6380;background:rgba(255,255,255,.03);border:1px solid #2a2f4a;">\u5373\u5c06\u4e0a\u7ebf</span>'
    sections_zh += f'''
<div id="{tid}" style="padding:30px 40px;border-top:1px solid #2a2f4a;">
<div style="display:grid;grid-template-columns:1.3fr 1fr;gap:20px;">
<div>
{badge}
<h2 style="font-size:28px;font-weight:800;color:{t['color']};margin:0 0 4px;">{zh_names[tid]}</h2>
<p style="font-size:13px;color:#8892b0;line-height:1.7;margin:10px 0 14px;">{zh_descs[tid]}</p>
{caps_html}
<div style="margin-top:16px;">{cta}</div>
<p style="margin-top:10px;font-size:11px;color:#5a6380;">\u8054\u7cfb <strong>@yujiashi</strong> \u83b7\u53d6\u8bbf\u95ee\u6743\u9650</p>
</div>
<div>
<p style="font-size:11px;color:#7a82a0;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">\u4e1a\u52a1\u5f71\u54cd</p>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">{impact_html}</div>
</div>
</div>
</div>'''

html_zh = f'''<div style="font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;background:#0f1117;color:#fff;padding:0;border-radius:12px;max-width:100%;margin:0 auto;">

<div style="text-align:center;padding:40px 20px 20px;">
<img src="data:image/png;base64,{logo_b64}" style="width:90px;height:90px;margin:0 auto 16px;display:block;border-radius:50%;" />
<h1 style="font-size:36px;font-weight:800;background:linear-gradient(135deg,#ff6b35,#e91e63,#9c27b0,#2196f3,#00bcd4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:0;">&#26234;&#31995;&#21015; Smart Suite</h1>
<p style="color:#8892b0;font-size:15px;margin-top:12px;max-width:600px;margin-left:auto;margin-right:auto;">\u4ece\u788e\u7247\u5316\u5185\u5bb9\u5de5\u4f5c\u6d41\uff0c\u5230 AI \u9a71\u52a8\u7684\u7aef\u5230\u7aef GEO \u5185\u5bb9\u667a\u80fd\u751f\u4ea7\u3001\u4f18\u5316\u4e0e\u6548\u679c\u8ffd\u8e2a\u3002</p>
</div>

<div style="display:flex;justify-content:center;gap:36px;margin:24px 0 30px;flex-wrap:wrap;">
<div style="text-align:center;"><div style="font-size:26px;font-weight:700;color:#00bcd4;">8</div><div style="font-size:11px;color:#7a82a0;">AI \u5de5\u5177</div></div>
<div style="text-align:center;"><div style="font-size:26px;font-weight:700;color:#00bcd4;">7+</div><div style="font-size:11px;color:#7a82a0;">AI \u68c0\u7d22\u5e73\u53f0</div></div>
<div style="text-align:center;"><div style="font-size:26px;font-weight:700;color:#00bcd4;">+65%</div><div style="font-size:11px;color:#7a82a0;">YTD \u6ce8\u518c\u5f00\u59cb YoY</div></div>
<div style="text-align:center;"><div style="font-size:26px;font-weight:700;color:#00bcd4;">+8,400 bps</div><div style="font-size:11px;color:#7a82a0;">vs SSR \u5927\u76d8\u9006\u8f6c</div></div>
</div>

<div style="margin:0 8px 16px;background:#1a1d2e;border-radius:12px;border:1px solid #2a2f4a;padding:32px 24px;">
<p style="font-size:12px;color:#5a6380;text-transform:uppercase;letter-spacing:1px;margin-bottom:20px;text-align:center;">\u7aef\u5230\u7aef\u95ed\u73af\u5de5\u4f5c\u6d41</p>
<div style="display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:nowrap;margin-bottom:20px;overflow-x:auto;">
<div style="background:#0f1117;border:1px solid #ffa726;border-radius:8px;padding:8px 14px;text-align:center;min-width:fit-content;"><div style="font-size:12px;color:#ffa726;font-weight:600;">\u667a\u5e93</div></div>
<div style="color:#8892b0;font-size:18px;font-weight:700;">&#10132;</div>
<div style="background:#0f1117;border:1px solid #ffcc02;border-radius:8px;padding:8px 14px;text-align:center;min-width:fit-content;"><div style="font-size:12px;color:#ffcc02;font-weight:600;">\u667a\u9020</div></div>
<div style="color:#8892b0;font-size:18px;font-weight:700;">&#10132;</div>
<div style="background:#0f1117;border:1px solid #e91e63;border-radius:8px;padding:8px 14px;text-align:center;min-width:fit-content;"><div style="font-size:12px;color:#e91e63;font-weight:600;">\u667a\u4f18</div></div>
<div style="color:#8892b0;font-size:18px;font-weight:700;">&#10132;</div>
<div style="background:#0f1117;border:1px solid #29b6f6;border-radius:8px;padding:8px 14px;text-align:center;min-width:fit-content;"><div style="font-size:12px;color:#29b6f6;font-weight:600;">\u667a\u5e03</div></div>
<div style="color:#8892b0;font-size:18px;font-weight:700;">&#10132;</div>
<div style="background:#0f1117;border:1px solid #26c6da;border-radius:8px;padding:8px 14px;text-align:center;min-width:fit-content;"><div style="font-size:12px;color:#26c6da;font-weight:600;">\u667a\u4f20</div></div>
<div style="color:#8892b0;font-size:18px;font-weight:700;">&#10132;</div>
<div style="background:#0f1117;border:1px solid #ab47bc;border-radius:8px;padding:8px 14px;text-align:center;min-width:fit-content;"><div style="font-size:12px;color:#ab47bc;font-weight:600;">\u667a\u6790</div></div>
<div style="color:#8892b0;font-size:18px;font-weight:700;">&#10132;</div>
<div style="background:#0f1117;border:1px solid #ff6b35;border-radius:8px;padding:8px 14px;text-align:center;min-width:fit-content;"><div style="font-size:12px;color:#ff6b35;font-weight:600;">\u667a\u4e2d\u67a2</div></div>
</div>
<div style="text-align:center;margin-top:12px;padding:10px;background:#0f1117;border-radius:8px;border:1px solid #2a2f4a;">
<p style="color:#00bcd4;font-size:12px;font-weight:600;margin:0;">&#8635; \u667a\u6790\u5c06\u6d1e\u5bdf\u53cd\u9988\u7ed9\u667a\u4e2d\u67a2 &#8594; \u667a\u4e2d\u67a2\u89e6\u53d1\u667a\u5e93/\u667a\u9020/\u667a\u4f18/\u667a\u5e03/\u667a\u4f20\u4f18\u5316\u63d0\u5347 performance \u5e76\u5f25\u8865 gaps</p>
</div>
</div>

{sections_zh}

<div style="padding:24px 40px;border-top:1px solid #2a2f4a;text-align:center;">
<p style="color:#7a82a0;font-size:11px;">\u667a\u7cfb\u5217 Smart Suite - AI \u9a71\u52a8\u7684 GEO \u5185\u5bb9\u667a\u80fd\u5e73\u53f0 | GEO Team | \u8054\u7cfb @yujiashi</p>
</div>

</div>'''

out_zh = Path(r'c:\Users\yujiashi\Desktop\SmartSuite_Phase1\ui\smart-suite-wiki-zh.html')
out_zh.write_text(html_zh, encoding='utf-8')
print(f"Generated ZH: {len(html_zh)} chars -> {out_zh}")
