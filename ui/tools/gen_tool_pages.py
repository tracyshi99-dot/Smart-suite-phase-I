"""Generate individual tool landing pages for Smart Suite."""
from pathlib import Path

OUT = Path(__file__).parent

TOOLS = [
    {
        "id": "zhiku",
        "name": "智库",
        "en_name": "Prompt Intelligencer",
        "color": "#ffa726",
        "icon": "📚",
        "steering": "tool-zhiku.md",
        "desc_en": "Connects to mainstream AI search platforms to capture real-time, high-precision search phrases and generate structured queries with high citation probability.",
        "desc_zh": "对接主流 AI 检索平台，获取实时性更强、相对精准的检索短语，生成高引用概率的结构化查询。",
        "prompts": [
            {"label": "Standard Run", "cmd": "执行智库 batch_004，market=ALL，keyword_limit=10"},
            {"label": "CN Market Only", "cmd": "执行智库 batch_004，market=CN，keyword_limit=15"},
            {"label": "NA Market Focus", "cmd": "执行智库 batch_004，market=NA，keyword_limit=10"},
        ],
        "input": "input/seo_sem_keywords.csv",
        "output": "output/{batch_id}/01_zhiku/zhiku_ai_queries.csv",
        "steps_en": ["Reads keywords from input CSV", "Generates AI-native search queries per keyword", "Scores and ranks queries by priority (1-5)", "Outputs selected high-value queries"],
        "steps_zh": ["从输入 CSV 读取关键词", "为每个关键词生成 AI 原生搜索查询", "按优先级 (1-5) 评分和排序", "输出已筛选的高价值查询"],
    },
    {
        "id": "zhizao",
        "name": "智造",
        "en_name": "Content Creator",
        "color": "#ffcc02",
        "icon": "✍️",
        "steering": "tool-zhizao.md",
        "desc_en": "Produces high-quality GEO-structured content at scale based on high-value search phrases, maximizing AI engine citation probability.",
        "desc_zh": "基于高价值检索短语批量生成高质量 GEO 结构化内容，最大化 AI 引擎引用概率。",
        "prompts": [
            {"label": "Standard Run", "cmd": "执行智造 batch_004，生成内容"},
            {"label": "Single Article", "cmd": "执行智造 batch_004，只生成第1篇"},
            {"label": "Resume from Part 3", "cmd": "执行智造 batch_004，从第3部分继续"},
        ],
        "input": "output/{batch_id}/01_zhiku/zhiku_ai_queries.csv",
        "output": "output/{batch_id}/02_zhizao/zhizao_draft_content.csv",
        "steps_en": ["Loads selected queries from 智库 output", "Retrieves knowledge from 3PKC KMS", "Generates GEO-structured article per query", "Outputs draft content with metadata"],
        "steps_zh": ["加载智库输出的已选查询", "从 3PKC KMS 知识库检索素材", "为每个查询生成 GEO 结构化文章", "输出带元数据的草稿内容"],
    },
    {
        "id": "zhiyou",
        "name": "智优",
        "en_name": "Content Optimizer",
        "color": "#e91e63",
        "icon": "⭐",
        "steering": "tool-zhiyou.md",
        "desc_en": "Scores content across 5 dimensions for AI citation probability, auto-rewrites weak sections, and ensures Amazon compliance.",
        "desc_zh": "通过 5 维度评分量化 AI 引用概率，自动重写薄弱环节，并确保通过亚马逊合规检查。",
        "prompts": [
            {"label": "Score Only", "cmd": "执行智优评分 batch_004"},
            {"label": "Score + Rewrite", "cmd": "执行智优执行 batch_004，基于评分建议重写"},
            {"label": "Compliance Check", "cmd": "执行合规审查 batch_004"},
        ],
        "input": "output/{batch_id}/02_zhizao/zhizao_draft_content.csv",
        "output": "output/{batch_id}/03_zhiyou/zhiyou_optimized_content.csv",
        "steps_en": ["Scores each article on 5 dimensions", "Identifies weak sections by score gap", "Auto-rewrites content to improve scores", "Runs Amazon compliance verification"],
        "steps_zh": ["对每篇文章进行 5 维度评分", "通过评分差距识别薄弱环节", "自动重写内容以提升评分", "执行亚马逊合规验证"],
    },
    {
        "id": "zhibu",
        "name": "智布&智传",
        "en_name": "Publisher & Distributor",
        "color": "#29b6f6",
        "icon": "☁️",
        "steering": "tool-zhibu.md",
        "desc_en": "Converts optimized content into LEGO CMS JSON format and enables one-click multi-channel distribution.",
        "desc_zh": "将优化后的内容转换为 LEGO CMS 标准 JSON 格式，支持一键多渠道分发。",
        "prompts": [
            {"label": "Generate JSON", "cmd": "执行智布 batch_004，生成JSON"},
            {"label": "Full Publish", "cmd": "执行智布 batch_004，生成JSON并发布"},
        ],
        "input": "output/{batch_id}/03_zhiyou/zhiyou_optimized_content.csv",
        "output": "output/{batch_id}/04_zhibu/zhibu_output.json",
        "steps_en": ["Loads optimized content from 智优", "Converts to LEGO CMS JSON structure", "Populates metadata fields automatically", "Ready for multi-channel publishing"],
        "steps_zh": ["加载智优输出的优化内容", "转换为 LEGO CMS JSON 结构", "自动填充元数据字段", "就绪多渠道发布"],
    },
    {
        "id": "zhixi",
        "name": "智析",
        "en_name": "Performance Analyzer",
        "color": "#ab47bc",
        "icon": "📊",
        "steering": "tool-zhixi.md",
        "desc_en": "Full-channel performance tracking and attribution analysis with automated Weekly/Monthly/YTD reporting against SSR benchmark.",
        "desc_zh": "全渠道效果追踪与归因分析，自动生成 Weekly/Monthly/YTD 多维报表，与 SSR 大盘对标。",
        "prompts": [
            {"label": "Weekly Report", "cmd": "生成智析报告 WK25"},
            {"label": "Monthly Summary", "cmd": "生成智析月度报告 M6"},
            {"label": "Update Data", "cmd": "更新智析数据"},
        ],
        "input": "Downloads/SSR_Funnel_Metrics_*.csv",
        "output": "output/metrics/zhixi_report_WK25.xlsx",
        "steps_en": ["Ingests SSR Funnel data from QuickSight export", "Computes GEO/Direct channel metrics with YoY", "Benchmarks against SSR total", "Generates Excel report + updates dashboard"],
        "steps_zh": ["导入 QuickSight 导出的 SSR Funnel 数据", "计算 GEO/Direct 各渠道指标及 YoY", "与 SSR 大盘对标", "生成 Excel 报表 + 更新 Dashboard"],
    },
    {
        "id": "s3",
        "name": "S3 Memory Keeper",
        "en_name": "Knowledge Storage",
        "color": "#42a5f5",
        "icon": "🗄️",
        "steering": "tool-s3.md",
        "desc_en": "AWS S3-based persistent storage layer providing unified data foundation for all Smart Suite modules with version control.",
        "desc_zh": "基于 AWS S3 的持久化知识存储层，为全模块提供统一数据底座，支持版本化存储。",
        "prompts": [
            {"label": "Sync to S3", "cmd": "同步 batch_004 数据到 S3"},
            {"label": "Download Latest", "cmd": "从 S3 下载最新 batch 数据"},
        ],
        "input": "output/{batch_id}/*",
        "output": "s3://smartsuite-data/{batch_id}/",
        "steps_en": ["Connects to AWS S3 bucket", "Syncs local batch data to cloud", "Maintains version history", "Enables cross-module data sharing"],
        "steps_zh": ["连接 AWS S3 存储桶", "同步本地批次数据到云端", "维护版本历史", "支持跨模块数据共享"],
    },
    {
        "id": "zhishu",
        "name": "智中枢",
        "en_name": "Workflow Orchestrator",
        "color": "linear-gradient(135deg, #ff6b35, #e91e63)",
        "icon": "🔄",
        "steering": "tool-zhishu.md",
        "desc_en": "Central orchestration hub connecting all modules into a complete E2E pipeline with 7-rule decision engine for automated weekly action plans.",
        "desc_zh": "全流程编排中心，串联所有模块为完整 E2E 流水线，内置 7 条决策规则引擎自动生成周度执行计划。",
        "prompts": [
            {"label": "Full Pipeline", "cmd": "全流程执行 batch_004，market=ALL，keyword_limit=10"},
            {"label": "Decision Plan", "cmd": "智中枢决策 WK25，生成周度计划"},
            {"label": "Gap Analysis", "cmd": "智中枢 Gap 分析，识别内容缺口"},
        ],
        "input": "All module outputs + SSR metrics",
        "output": "Weekly action plan + batch execution",
        "steps_en": ["Analyzes latest performance data", "Applies 7 decision rules", "Generates prioritized action plan", "Orchestrates full pipeline execution"],
        "steps_zh": ["分析最新效果数据", "应用 7 条决策规则", "生成优先级排序的行动计划", "编排全流程执行"],
    },
]

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} {en_name} – Smart Suite</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0a0a0f;color:#fff;min-height:100vh;padding:0}}
.top{{background:rgba(10,10,15,.92);border-bottom:1px solid #1e2030;padding:14px 40px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:10;backdrop-filter:blur(16px)}}
.top-left{{display:flex;align-items:center;gap:12px}}
.top-left a{{color:#8892b0;text-decoration:none;font-size:14px;display:flex;align-items:center;gap:6px;transition:color .2s}}
.top-left a:hover{{color:#fff}}
.top-logo{{width:36px;height:36px;border-radius:50%;background:conic-gradient(from 200deg,#ff6b35,#e91e63,#9c27b0,#2196f3,#00bcd4,#4caf50,#ffeb3b,#ff6b35);display:flex;align-items:center;justify-content:center}}
.top-logo span{{font-size:16px;font-weight:900;color:#fff;text-shadow:0 1px 3px rgba(0,0,0,.5)}}
.lang-btn{{padding:5px 12px;border-radius:5px;font-size:11px;font-weight:600;background:rgba(255,255,255,.06);border:1px solid #1e2030;color:#8892b0;cursor:pointer}}
.lang-btn:hover{{background:rgba(255,255,255,.1);color:#fff}}
.container{{max-width:900px;margin:0 auto;padding:40px}}
.icon-row{{font-size:48px;margin-bottom:16px}}
h1{{font-size:36px;font-weight:800;color:{color};margin-bottom:4px}}
.subtitle{{font-size:16px;color:#8892b0;margin-bottom:20px;font-style:italic}}
.desc{{font-size:15px;color:#8892b0;line-height:1.7;margin-bottom:32px;max-width:700px}}
.section-title{{font-size:13px;text-transform:uppercase;letter-spacing:1px;color:#5a6380;margin:32px 0 14px;border-bottom:1px solid #1e2030;padding-bottom:8px}}
.prompt-card{{background:#12131a;border:1px solid #1e2030;border-radius:10px;padding:16px 20px;margin-bottom:10px;display:flex;align-items:center;justify-content:space-between;transition:all .2s}}
.prompt-card:hover{{border-color:rgba(255,255,255,.1);background:#1a1b25}}
.prompt-label{{font-size:12px;color:#5a6380;margin-bottom:4px}}
.prompt-cmd{{font-size:14px;color:#e0e0e0;font-family:'Cascadia Code','Fira Code',monospace}}
.copy-btn{{padding:6px 14px;border-radius:6px;font-size:12px;font-weight:500;background:rgba(255,255,255,.06);border:1px solid #1e2030;color:#8892b0;cursor:pointer;transition:all .2s;white-space:nowrap}}
.copy-btn:hover{{background:rgba(255,255,255,.12);color:#fff}}
.io-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:8px}}
.io-card{{background:#12131a;border:1px solid #1e2030;border-radius:10px;padding:16px}}
.io-card h4{{font-size:11px;text-transform:uppercase;color:#5a6380;margin-bottom:8px;letter-spacing:.5px}}
.io-card p{{font-size:13px;color:#8892b0;font-family:monospace;word-break:break-all}}
.steps{{list-style:none;counter-reset:step}}
.steps li{{counter-increment:step;display:flex;align-items:flex-start;gap:12px;margin-bottom:12px;font-size:14px;color:#8892b0}}
.steps li::before{{content:counter(step);min-width:24px;height:24px;border-radius:50%;background:rgba(255,255,255,.06);border:1px solid #1e2030;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#5a6380;flex-shrink:0}}
.toast{{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:rgba(0,188,212,.9);color:#fff;padding:10px 22px;border-radius:8px;font-size:13px;opacity:0;transition:opacity .3s;pointer-events:none;z-index:99}}
.toast.show{{opacity:1}}
@media(max-width:768px){{.container{{padding:24px 16px}}.io-grid{{grid-template-columns:1fr}}h1{{font-size:28px}}}}
</style>
</head>
<body>
<div class="top">
  <div class="top-left">
    <a href="../smart-suite-showcase.html">← Back</a>
    <div class="top-logo"><span>智</span></div>
  </div>
  <button class="lang-btn" onclick="toggleLang()">中文</button>
</div>
<div class="container">
  <div class="icon-row">{icon}</div>
  <h1 id="toolName">{name} {en_name}</h1>
  <p class="subtitle" id="toolSub">{en_name}</p>
  <p class="desc" id="toolDesc">{desc_en}</p>

  <div class="section-title" data-en="USE IN KIRO" data-zh="在 KIRO 中使用">USE IN KIRO</div>
  <div class="prompt-card" style="border-color:rgba(0,188,212,.3);background:rgba(0,188,212,.05)">
    <div>
      <div class="prompt-label" style="color:#00bcd4">Reference this steering file in Kiro chat:</div>
      <div class="prompt-cmd" style="color:#00e5ff">#File .kiro/steering/{steering}</div>
    </div>
    <button class="copy-btn" onclick="copyCmd(this)">Copy</button>
  </div>
  <div class="prompt-card" style="border-color:rgba(171,71,188,.3);background:rgba(171,71,188,.05);margin-top:6px">
    <div>
      <div class="prompt-label" style="color:#ab47bc">Or open directly in Smart Suite Dashboard:</div>
      <div class="prompt-cmd"><a href="http://rem-5cg31524zw.ant.amazon.com:8501/?tool={id}" target="_blank" style="color:#ce93d8;text-decoration:none">http://rem-5cg31524zw.ant.amazon.com:8501/?tool={id}</a></div>
    </div>
    <button class="copy-btn" onclick="copyCmd(this)">Copy</button>
  </div>

  <div class="section-title" data-en="QUICK START PROMPTS" data-zh="快速启动指令">QUICK START PROMPTS</div>
  {prompts_html}

  <div class="section-title" data-en="INPUT / OUTPUT" data-zh="输入 / 输出">INPUT / OUTPUT</div>
  <div class="io-grid">
    <div class="io-card"><h4>Input</h4><p>{input}</p></div>
    <div class="io-card"><h4>Output</h4><p>{output}</p></div>
  </div>

  <div class="section-title" data-en="HOW IT WORKS" data-zh="工作流程">HOW IT WORKS</div>
  <ol class="steps" id="steps">
    {steps_html}
  </ol>
</div>
<div class="toast" id="toast"></div>
<script>
let lang='en';
const data = {{
  name_en: "{name} {en_name}",
  name_zh: "{name} {en_name}",
  sub_en: "{en_name}",
  sub_zh: "{desc_zh_short}",
  desc_en: "{desc_en}",
  desc_zh: "{desc_zh}",
  steps_en: {steps_en_json},
  steps_zh: {steps_zh_json}
}};
function toggleLang(){{
  lang = lang==='en'?'zh':'en';
  document.querySelector('.lang-btn').textContent = lang==='en'?'中文':'English';
  document.getElementById('toolDesc').textContent = data['desc_'+lang];
  document.getElementById('toolSub').textContent = data['sub_'+lang];
  document.querySelectorAll('.section-title').forEach(el=>{{el.textContent=el.dataset[lang]||el.textContent}});
  const steps = document.getElementById('steps');
  steps.innerHTML = data['steps_'+lang].map(s=>'<li>'+s+'</li>').join('');
  document.querySelectorAll('.copy-btn').forEach(b=>{{b.textContent=lang==='en'?'Copy':'复制'}});
}}
function copyCmd(el){{
  const cmd = el.closest('.prompt-card').querySelector('.prompt-cmd').textContent;
  navigator.clipboard.writeText(cmd).then(()=>showToast(lang==='en'?'Copied!':'已复制!')).catch(()=>{{
    const t=document.createElement('textarea');t.value=cmd;document.body.appendChild(t);t.select();document.execCommand('copy');document.body.removeChild(t);showToast(lang==='en'?'Copied!':'已复制!');
  }});
}}
function showToast(msg){{const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2000)}}
</script>
</body>
</html>"""

import json

for tool in TOOLS:
    prompts_html = ""
    for p in tool["prompts"]:
        prompts_html += f'''  <div class="prompt-card">
    <div><div class="prompt-label">{p["label"]}</div><div class="prompt-cmd">{p["cmd"]}</div></div>
    <button class="copy-btn" onclick="copyCmd(this)">Copy</button>
  </div>\n'''

    steps_en_html = "\n    ".join(f"<li>{s}</li>" for s in tool["steps_en"])
    color = tool["color"] if not tool["color"].startswith("linear") else "#ff6b35"

    html = TEMPLATE.format(
        id=tool["id"],
        name=tool["name"],
        en_name=tool["en_name"],
        color=color,
        icon=tool["icon"],
        desc_en=tool["desc_en"],
        desc_zh=tool["desc_zh"],
        desc_zh_short=tool["desc_zh"][:30] + "...",
        steering=tool["steering"],
        prompts_html=prompts_html,
        input=tool["input"],
        output=tool["output"],
        steps_html=steps_en_html,
        steps_en_json=json.dumps(tool["steps_en"]),
        steps_zh_json=json.dumps(tool["steps_zh"], ensure_ascii=False),
    )

    outfile = OUT / f"{tool['id']}.html"
    outfile.write_text(html, encoding="utf-8")
    print(f"  ✅ {outfile.name}")

print(f"\nDone! {len(TOOLS)} tool pages generated in {OUT}")
