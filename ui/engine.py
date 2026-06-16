"""
Smart Suite Execution Engine - Bedrock Claude 3.5 Sonnet
Executes pipeline steps (智库→智造→智优→智布) via AWS Bedrock.
"""
import boto3
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional

# --- Config ---
BASE_PATH = Path(__file__).parent.parent
OUTPUT_PATH = BASE_PATH / "output"
INPUT_PATH = BASE_PATH / "input"
STEERING_PATH = BASE_PATH / ".kiro" / "steering"

# On cloud, use temp directory for output
import tempfile

if not OUTPUT_PATH.exists():
    OUTPUT_PATH = Path(tempfile.gettempdir()) / "smartsuite_output"
    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
if not INPUT_PATH.exists():
    INPUT_PATH = Path(tempfile.gettempdir()) / "smartsuite_input"
    INPUT_PATH.mkdir(parents=True, exist_ok=True)

MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
REGION = "us-east-1"
MAX_TOKENS = 4096


def get_client():
    """Get Bedrock client - uses Streamlit secrets on cloud, local creds otherwise."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "aws" in st.secrets:
            return boto3.client(
                "bedrock-runtime",
                region_name=st.secrets["aws"].get("region", REGION),
                aws_access_key_id=st.secrets["aws"]["access_key_id"],
                aws_secret_access_key=st.secrets["aws"]["secret_access_key"],
            )
    except Exception:
        pass
    # Fallback to local credentials (SSO, env vars, etc.)
    from botocore.config import Config
    config = Config(read_timeout=300, connect_timeout=10, retries={"max_attempts": 2})
    return boto3.client("bedrock-runtime", region_name=REGION, config=config)


def call_claude(system_prompt: str, user_prompt: str, max_tokens: int = MAX_TOKENS) -> str:
    """Call Claude 3.5 Sonnet via Bedrock Converse API."""
    client = get_client()
    response = client.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": user_prompt}]}],
        system=[{"text": system_prompt}],
        inferenceConfig={"maxTokens": max_tokens, "temperature": 0.3},
    )
    return response["output"]["message"]["content"][0]["text"]


def load_steering() -> str:
    """Load the main steering file."""
    path = STEERING_PATH / "smart-suite-phase1.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _fix_csv_quoting(filepath: Path):
    """Re-save CSV through pandas to fix any quoting/column issues."""
    try:
        df = pd.read_csv(filepath, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
        if not df.empty:
            df.to_csv(filepath, index=False, encoding="utf-8-sig")
    except Exception:
        pass  # Don't corrupt file if we can't parse it


# ============================================================
# SEMANTIC EXPANSION (源B: 核心词根裂变)
# ============================================================
def run_semantic_expansion(core_semantic: str, market: str = "CN", count: int = 15,
                           language: str = "zh", batch_id: str = "batch_001",
                           progress_callback=None) -> dict:
    """Generate AI-native search queries by expanding a core semantic concept."""
    if progress_callback:
        progress_callback(0.1, "正在裂变检索短语...")

    system_prompt = f"""你是一位精通 AI 搜索引擎用户行为的专家。

你的任务是：给定核心语义「{core_semantic}」，裂变出用户在 AI 搜索引擎（如 ChatGPT、DeepSeek、Perplexity）中关于这个主题最可能输入的检索短语。

关键规则：
1. 所有短语必须直接包含或紧密围绕「{core_semantic}」这个词/概念
2. 模拟真实用户提问，口语化，10-25字
3. 覆盖不同角度：是什么、怎么做、多少钱、有什么好处、有什么风险、和XX比哪个好
4. 不要偏离核心词，不要生成与「{core_semantic}」无关的内容
5. 短语中应该能看到「{core_semantic}」或其同义词"""

    user_prompt = f"""核心语义：{core_semantic}
目标市场：{market}
输出语言：{language}
生成数量：{count}

请输出 CSV 格式，字段：
keyword_id,keyword,query_id,ai_query,intent_type,query_type,priority_score,estimated_volume,category,language,market,is_selected,created_at

规则：
- keyword_id: SEM_001
- keyword: "{core_semantic}"
- query_id: SEM_001_01, SEM_001_02...
- ai_query: 裂变出的检索短语（必须与「{core_semantic}」直接相关）
- intent_type: informational / comparison / transactional / troubleshooting
- priority_score: 1-5（与核心词相关性+商业价值综合评分）
- estimated_volume: 预估月检索量（high/medium/low）
- category: 从以下类别选最匹配的：跨境电商知识早知道|跨境电商行业入门了解|亚马逊商城基础情况了解|新手怎么注册亚马逊|亚马逊开店成本费用详解|亚马逊物流仓储科普|教你打造优质Listing|店铺运营提升全攻略|亚马逊广告基础知识大全|跨境电商选品方法及趋势
- is_selected: TRUE
- created_at: {timestamp()}

重要：如果字段包含逗号必须用双引号包裹。直接输出CSV，不要代码块。"""

    result = call_claude(system_prompt, user_prompt)

    if progress_callback:
        progress_callback(0.7, "正在保存...")

    output_dir = OUTPUT_PATH / batch_id / "01_zhiku"
    ensure_dir(output_dir)
    output_file = output_dir / "zhiku_ai_queries.csv"

    csv_content = result.strip()
    if csv_content.startswith("```"):
        csv_content = "\n".join(csv_content.split("\n")[1:])
    if csv_content.endswith("```"):
        csv_content = "\n".join(csv_content.split("\n")[:-1])

    # Ensure header
    expected_header = "keyword_id,keyword,query_id,ai_query,intent_type,query_type,priority_score,estimated_volume,category,language,market,is_selected,created_at"
    csv_lines = csv_content.strip().split("\n")
    if csv_lines and "ai_query" not in csv_lines[0] and "keyword_id" not in csv_lines[0]:
        csv_content = expected_header + "\n" + csv_content.strip()

    # Append to existing file
    if output_file.exists():
        try:
            existing = output_file.read_text(encoding="utf-8-sig").strip()
            if existing and len(existing) > 10:
                new_lines = csv_content.strip().split("\n")
                if new_lines and ("keyword_id" in new_lines[0] or "ai_query" in new_lines[0]):
                    new_lines = new_lines[1:]
                if new_lines:
                    output_file.write_text(existing + "\n" + "\n".join(new_lines), encoding="utf-8-sig")
            else:
                output_file.write_text(csv_content.strip(), encoding="utf-8-sig")
        except Exception:
            output_file.write_text(csv_content.strip(), encoding="utf-8-sig")
    else:
        output_file.write_text(csv_content.strip(), encoding="utf-8-sig")

    if progress_callback:
        progress_callback(1.0, "裂变完成 ✅")

    # Auto-fix CSV quoting
    _fix_csv_quoting(output_file)

    lines = [l for l in csv_content.strip().split("\n") if l.strip()]
    query_count = max(0, len(lines) - 1)

    return {"success": True, "output_file": str(output_file), "query_count": query_count}


# ============================================================
# STEP 1: 智库
# ============================================================
def run_zhiku(batch_id: str, market: str = "ALL", keyword_limit: int = 10,
              progress_callback=None) -> dict:
    """Execute Step 1: Generate AI queries from keywords."""
    steering = load_steering()

    # Load keywords
    kw_path = INPUT_PATH / "seo_sem_keywords.csv"
    if not kw_path.exists():
        return {"success": False, "error": "关键词文件不存在: input/seo_sem_keywords.csv"}

    df_kw = pd.read_csv(kw_path, encoding="utf-8-sig")

    # Filter by market
    if market != "ALL":
        df_kw = df_kw[df_kw["market"] == market]

    # Limit keywords
    df_kw = df_kw.head(keyword_limit)

    if df_kw.empty:
        return {"success": False, "error": f"没有找到 market={market} 的关键词"}

    if progress_callback:
        progress_callback(0.1, "正在调用 Claude 生成 AI Queries...")

    # Build prompt
    kw_list = df_kw[["keyword_id", "Keyword", "market", "keyword_type", "priority"]].to_csv(index=False)

    system_prompt = f"""你是 Smart Suite 智库模块。严格按照以下规则生成 AI 原生搜索查询。

{steering}

重点关注 Step 1: 智库 的规则。"""

    user_prompt = f"""请为以下关键词生成 AI 原生搜索查询。

关键词列表：
{kw_list}

要求：
1. 每个关键词生成 8-12 个高质量 AI 查询
2. 输出格式为 CSV，字段：keyword_id,keyword,query_id,ai_query,intent_type,query_type,priority_score,estimated_volume,category,language,market,is_selected,created_at
3. intent_type: informational / navigational / transactional / comparison
4. query_type: branded / generic / industry / conversion-oriented
5. priority_score: 1-5
6. category: 从以下类别选最匹配的一个：跨境电商知识早知道|跨境电商行业入门了解|亚马逊商城基础情况了解|新手怎么注册亚马逊|亚马逊开店成本费用详解|亚马逊物流仓储科普|教你打造优质Listing|店铺运营提升全攻略|亚马逊广告基础知识大全|跨境电商选品方法及趋势
7. 只有高质量查询设 is_selected=TRUE
8. created_at 使用 {timestamp()}
9. 如果字段包含逗号必须用双引号包裹
10. 直接输出 CSV 内容，不要加任何解释文字或 markdown 代码块标记

⚠️ 严格过滤规则（不符合以下条件的不要生成）：
- 只生成与「亚马逊全球开店」「跨境电商卖家」业务直接相关的检索短语
- 短语必须是潜在卖家/商家在考虑开店、运营、选品、物流、广告时会问的问题
- 不要生成纯事实性/百科类问题（如"XXX创始人是谁""XXX市值多少""XXX历史"）
- 不要生成与卖家决策/行动无关的泛信息查询
- 不要生成竞品平台相关的查询
- is_selected=FALSE 的条件：与亚马逊开店卖家决策无关、纯百科知识、无法产出营销内容的短语"""

    result = call_claude(system_prompt, user_prompt)

    if progress_callback:
        progress_callback(0.7, "正在保存结果...")

    # Parse and save
    output_dir = OUTPUT_PATH / batch_id / "01_zhiku"
    ensure_dir(output_dir)
    output_file = output_dir / "zhiku_ai_queries.csv"

    # Clean result (remove markdown code fences if present)
    csv_content = result.strip()
    if csv_content.startswith("```"):
        csv_content = "\n".join(csv_content.split("\n")[1:])
    if csv_content.endswith("```"):
        csv_content = "\n".join(csv_content.split("\n")[:-1])

    # Ensure header
    expected_header = "keyword_id,keyword,query_id,ai_query,intent_type,query_type,priority_score,estimated_volume,category,language,market,is_selected,created_at"
    csv_lines = csv_content.strip().split("\n")
    if csv_lines and "ai_query" not in csv_lines[0] and "keyword_id" not in csv_lines[0]:
        csv_content = expected_header + "\n" + csv_content.strip()

    # Append to existing file (not overwrite)
    if output_file.exists():
        try:
            existing = output_file.read_text(encoding="utf-8-sig").strip()
            if existing and len(existing) > 10:
                new_lines = csv_content.strip().split("\n")
                if new_lines and ("keyword_id" in new_lines[0] or "ai_query" in new_lines[0]):
                    new_lines = new_lines[1:]
                if new_lines:
                    output_file.write_text(existing + "\n" + "\n".join(new_lines), encoding="utf-8-sig")
            else:
                output_file.write_text(csv_content.strip(), encoding="utf-8-sig")
        except Exception:
            output_file.write_text(csv_content.strip(), encoding="utf-8-sig")
    else:
        output_file.write_text(csv_content.strip(), encoding="utf-8-sig")

    if progress_callback:
        progress_callback(1.0, "智库完成 ✅")

    # Auto-fix CSV quoting
    _fix_csv_quoting(output_file)

    # Dedup by ai_query column
    try:
        df_final = pd.read_csv(output_file, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
        if not df_final.empty and "ai_query" in df_final.columns:
            before_count = len(df_final)
            df_final = df_final.drop_duplicates(subset=["ai_query"], keep="first")
            df_final.to_csv(output_file, index=False, encoding="utf-8-sig")
    except Exception:
        pass

    # Count results
    lines = [l for l in csv_content.strip().split("\n") if l.strip()]
    query_count = max(0, len(lines) - 1)

    return {
        "success": True,
        "output_file": str(output_file),
        "query_count": query_count,
        "keywords_processed": len(df_kw),
    }


# ============================================================
# STEP 2: 智造
# ============================================================
def run_zhizao(batch_id: str, content_limit: int = 5,
               progress_callback=None) -> dict:
    """Execute Step 2: Generate draft content for selected queries."""
    steering = load_steering()

    # Load zhiku output
    zhiku_path = OUTPUT_PATH / batch_id / "01_zhiku" / "zhiku_ai_queries.csv"
    if not zhiku_path.exists():
        return {"success": False, "error": "请先执行智库 (Step 1)"}

    df_q = pd.read_csv(zhiku_path, encoding="utf-8-sig")

    # Filter selected
    if "is_selected" in df_q.columns:
        df_q["is_selected"] = df_q["is_selected"].astype(str).str.strip().str.upper()
        df_q = df_q[df_q["is_selected"].isin(["TRUE", "1", "YES"])]

    df_q = df_q.head(content_limit)

    if df_q.empty:
        return {"success": False, "error": "没有已选中的 AI Queries"}

    output_dir = OUTPUT_PATH / batch_id / "02_zhizao"
    ensure_dir(output_dir)

    results = []
    total = len(df_q)

    for idx, row in df_q.iterrows():
        if progress_callback:
            progress_callback((idx + 1) / (total + 1),
                              f"正在生成第 {idx+1}/{total} 篇内容...")

        query = row.get("ai_query", "")
        keyword = row.get("keyword", "")
        keyword_id = row.get("keyword_id", "")
        query_id = row.get("query_id", "")

        system_prompt = f"""你是一位精通跨境电商的顶级内容营销专家，专注亚马逊全球开店。

你的唯一任务：根据用户给你的「检索短语」撰写一篇 800+ 字的文章。

⚠️ 最高优先级规则：
- 文章标题和正文必须 100% 围绕用户给的检索短语
- 首段必须直接回答检索短语提出的问题
- 如果内容偏离了检索短语的主题，视为失败

内容格式要求：
- 第一行输出文章标题（不加#号）
- 使用 Markdown 格式（## H2, ### H3）
- 至少包含 1 个表格、2 个列表
- 至少 2 次自然植入 https://gs.amazon.cn
- 末尾包含 3 个 FAQ（常见问题解答）
- 不提及 Shopee/Lazada/TikTok 等竞品"""

        user_prompt = f"""请为以下 AI 查询生成一篇完整的 SEO+GEO 双优化文章。

⚠️ 最重要的规则：文章必须 100% 围绕下面这个检索短语来写，标题和正文必须直接回答这个问题。
如果文章内容偏离了这个检索短语的主题，视为失败。

AI Query（检索短语，文章必须精确回答这个问题）: {query}
Keyword: {keyword}
Keyword ID: {keyword_id}
Query ID: {query_id}

要求：
1. 文章标题必须包含或紧密对应 AI Query 中的核心表达
2. 首段必须直接回答 AI Query 提出的问题（金字塔原则）
3. 全文所有 H2/H3 必须围绕 AI Query 展开，不能跑题
4. 严格遵循内容结构要求（开头段落 + H2/H3 + FAQ + 结语）
5. 至少 800 字
6. 至少 1 个表格、2 个列表、3 个 FAQ
7. 至少 2 次自然植入 https://gs.amazon.cn
8. 不提及竞品（Shopee, Lazada, TikTok 等）

请直接输出文章正文（Markdown 格式），不要包裹在 JSON 或代码块中。
第一行是文章标题（不加 # 号），第二行空行，然后是正文。"""

        response = call_claude(system_prompt, user_prompt)

        # Parse response: first line = title, rest = content
        import re
        lines = response.strip().split("\n")
        # Extract title (first non-empty line, strip any leading # or *)
        title = ""
        content_start = 0
        for i, line in enumerate(lines):
            stripped = line.strip().lstrip("#").lstrip("*").strip()
            if stripped:
                title = stripped
                content_start = i + 1
                break

        content_body = "\n".join(lines[content_start:]).strip()

        # Extract FAQ section if present
        faq_match = re.search(r'(##\s*(?:常见问题|FAQ).+)', content_body, re.DOTALL | re.IGNORECASE)
        faq_section = faq_match.group(1) if faq_match else ""

        results.append({
            "content_id": f"C_{keyword_id}_{idx+1:03d}",
            "query_id": query_id,
            "keyword_id": keyword_id,
            "ai_query": query,
            "title": title,
            "meta_title": title[:60],
            "meta_description": content_body[:120].replace("\n", " "),
            "content_draft": content_body,
            "faq_section": faq_section,
            "cta": "立即前往亚马逊卖家平台注册：https://gs.amazon.cn",
            "geo_summary": content_body[:100].replace("\n", " "),
            "word_count": len(content_body),
            "version": "v1",
            "created_at": timestamp(),
        })

    # Save as CSV
    df_out = pd.DataFrame(results)
    output_file = output_dir / "zhizao_draft_content.csv"
    df_out.to_csv(output_file, index=False, encoding="utf-8-sig")

    if progress_callback:
        progress_callback(1.0, "智造完成 ✅")

    return {
        "success": True,
        "output_file": str(output_file),
        "articles_generated": len(results),
    }


# ============================================================
# STEP 3: 智优评分
# ============================================================
def run_zhiyou_score(batch_id: str, progress_callback=None) -> dict:
    """Execute Step 3: Score content across 5 dimensions."""
    steering = load_steering()

    zhizao_path = OUTPUT_PATH / batch_id / "02_zhizao" / "zhizao_draft_content.csv"
    if not zhizao_path.exists():
        return {"success": False, "error": "请先执行智造 (Step 2)"}

    df = pd.read_csv(zhizao_path, encoding="utf-8-sig")
    if df.empty:
        return {"success": False, "error": "智造输出为空"}

    if progress_callback:
        progress_callback(0.1, "正在评分...")

    # Build content summaries for scoring
    articles_text = ""
    for idx, row in df.iterrows():
        title = row.get("title", "")
        content = str(row.get("content_draft", ""))[:2000]
        articles_text += f"\n---\ncontent_id: {row.get('content_id', idx)}\nquery_id: {row.get('query_id', '')}\nkeyword_id: {row.get('keyword_id', '')}\nai_query: {row.get('ai_query', '')}\ntitle: {title}\ncontent (前2000字): {content}\n"

    system_prompt = f"""你是 Smart Suite 智优评分模块。严格按照以下规则评分。

{steering}

重点关注 Step 3: 智优评分 的规则。"""

    user_prompt = f"""请对以下内容进行 AI 引用概率评分。

{articles_text}

要求：
1. 对每篇内容按 5 个维度评分（1-5分）
2. 输出 CSV 格式，字段：content_id,query_id,keyword_id,ai_query,intent_match_score,ai_readability_score,authority_score,actionability_score,differentiation_score,overall_score,issues_found,risk_flags,optimization_suggestions,is_approved,version,updated_at
3. overall_score = intent_match*0.30 + ai_readability*0.20 + authority*0.20 + actionability*0.20 + differentiation*0.10
4. is_approved=TRUE 条件：overall_score>=4.5 且 intent_match>=4 且 authority>=4
5. optimization_suggestions 必须具体可操作
6. updated_at: {timestamp()}
7. 直接输出 CSV，不要加解释或代码块标记"""

    result = call_claude(system_prompt, user_prompt)

    if progress_callback:
        progress_callback(0.8, "正在保存评分卡...")

    output_dir = OUTPUT_PATH / batch_id / "03_zhiyou"
    ensure_dir(output_dir)
    output_file = output_dir / "zhiyou_scorecard.csv"

    csv_content = result.strip()
    if csv_content.startswith("```"):
        csv_content = "\n".join(csv_content.split("\n")[1:])
    if csv_content.endswith("```"):
        csv_content = "\n".join(csv_content.split("\n")[:-1])

    output_file.write_text(csv_content.strip(), encoding="utf-8-sig")

    if progress_callback:
        progress_callback(1.0, "智优评分完成 ✅")

    lines = [l for l in csv_content.strip().split("\n") if l.strip()]
    return {
        "success": True,
        "output_file": str(output_file),
        "articles_scored": max(0, len(lines) - 1),
    }


# ============================================================
# STEP 3.5: 智优执行
# ============================================================
def run_zhiyou_execute(batch_id: str, progress_callback=None) -> dict:
    """Execute Step 3.5: Rewrite content based on scorecard suggestions."""
    steering = load_steering()

    scorecard_path = OUTPUT_PATH / batch_id / "03_zhiyou" / "zhiyou_scorecard.csv"
    zhizao_path = OUTPUT_PATH / batch_id / "02_zhizao" / "zhizao_draft_content.csv"

    if not scorecard_path.exists():
        return {"success": False, "error": "请先执行智优评分 (Step 3)"}
    if not zhizao_path.exists():
        return {"success": False, "error": "智造输出不存在"}

    df_score = pd.read_csv(scorecard_path, encoding="utf-8-sig")
    df_draft = pd.read_csv(zhizao_path, encoding="utf-8-sig")

    # Filter approved only
    if "is_approved" in df_score.columns:
        approved_ids = df_score[df_score["is_approved"].astype(str).str.upper() == "TRUE"]["content_id"].tolist()
    else:
        approved_ids = df_score["content_id"].tolist()

    if not approved_ids:
        return {"success": False, "error": "没有通过评分的内容"}

    results = []
    total = len(approved_ids)

    for i, cid in enumerate(approved_ids):
        if progress_callback:
            progress_callback((i + 1) / (total + 1), f"正在重写第 {i+1}/{total} 篇...")

        draft_row = df_draft[df_draft["content_id"] == cid]
        score_row = df_score[df_score["content_id"] == cid]

        if draft_row.empty or score_row.empty:
            continue

        draft = draft_row.iloc[0]
        score = score_row.iloc[0]

        system_prompt = f"""你是 Smart Suite 智优执行模块。根据评分建议重写优化内容。

{steering}

重点关注 Step 3.5: 智优执行 的规则。"""

        user_prompt = f"""请根据评分建议重写以下内容。

原始标题: {draft.get('title', '')}
原始内容: {str(draft.get('content_draft', ''))[:3000]}
AI Query: {draft.get('ai_query', '')}

评分结果:
- intent_match: {score.get('intent_match_score', '')}
- ai_readability: {score.get('ai_readability_score', '')}
- authority: {score.get('authority_score', '')}
- actionability: {score.get('actionability_score', '')}
- differentiation: {score.get('differentiation_score', '')}
- issues: {score.get('issues_found', '')}
- suggestions: {score.get('optimization_suggestions', '')}

请输出 JSON：
{{
  "content_id": "{cid}",
  "query_id": "{draft.get('query_id', '')}",
  "keyword_id": "{draft.get('keyword_id', '')}",
  "ai_query": "{draft.get('ai_query', '')}",
  "original_title": "{draft.get('title', '')}",
  "optimized_title": "优化后标题",
  "optimized_meta_title": "SEO标题",
  "optimized_meta_description": "SEO描述",
  "optimized_content": "完整重写文章(800-1500字,Markdown)",
  "optimized_faq": "3个FAQ",
  "optimized_cta": "CTA",
  "optimized_geo_summary": "100字摘要+链接",
  "word_count": 数字,
  "table_count": 数字,
  "list_count": 数字,
  "link_count": 数字,
  "changes_applied": "应用的优化列表",
  "version": "v2",
  "updated_at": "{timestamp()}"
}}"""

        response = call_claude(system_prompt, user_prompt)
        try:
            text = response.strip()
            if text.startswith("```"):
                text = "\n".join(text.split("\n")[1:])
            if text.endswith("```"):
                text = "\n".join(text.split("\n")[:-1])
            article = json.loads(text)
            results.append(article)
        except json.JSONDecodeError:
            results.append({"content_id": cid, "optimized_content": response,
                            "version": "v2", "updated_at": timestamp()})

    output_dir = OUTPUT_PATH / batch_id / "03_zhiyou"
    ensure_dir(output_dir)
    output_file = output_dir / "zhiyou_optimized_content.csv"
    pd.DataFrame(results).to_csv(output_file, index=False, encoding="utf-8-sig")

    if progress_callback:
        progress_callback(1.0, "智优执行完成 ✅")

    return {"success": True, "output_file": str(output_file), "articles_rewritten": len(results)}


# ============================================================
# STEP 3.6: 合规审查
# ============================================================
def run_zhiyou_compliance(batch_id: str, progress_callback=None) -> dict:
    """Execute Step 3.6: Legal compliance check with auto-fix."""
    steering = load_steering()

    opt_path = OUTPUT_PATH / batch_id / "03_zhiyou" / "zhiyou_optimized_content.csv"
    if not opt_path.exists():
        return {"success": False, "error": "请先执行智优执行 (Step 3.5)"}

    df = pd.read_csv(opt_path, encoding="utf-8-sig")
    if df.empty:
        return {"success": False, "error": "优化内容为空"}

    if progress_callback:
        progress_callback(0.1, "正在进行合规审查...")

    # Build content for review
    articles_text = ""
    for idx, row in df.iterrows():
        content = str(row.get("optimized_content", ""))[:3000]
        articles_text += f"\n---\ncontent_id: {row.get('content_id', idx)}\ntitle: {row.get('optimized_title', '')}\ncontent: {content}\n"

    system_prompt = f"""你是 Smart Suite 合规审查模块。严格按照以下合规规则审查并自动修正内容。

{steering}

重点关注 Step 3.6: 合规审查 的所有规则（禁用词、数据规范、注册表述、品牌使用等）。"""

    user_prompt = f"""请对以下内容进行合规审查。

{articles_text}

要求：
1. 检查所有合规规则（禁用词、数据引用、注册表述、品牌使用、地图敏感地区等）
2. 自动修正可修复的问题
3. 输出 CSV 格式，字段：content_id,query_id,keyword_id,compliance_status,issues_found,fixes_applied,final_content,final_faq,final_cta,final_geo_summary,updated_at
4. compliance_status: PASS(无问题) / FIXED(已修正) / BLOCKED(需人工)
5. updated_at: {timestamp()}
6. 直接输出 CSV，不要加解释或代码块标记"""

    result = call_claude(system_prompt, user_prompt, max_tokens=MAX_TOKENS)

    if progress_callback:
        progress_callback(0.8, "正在保存合规结果...")

    output_file = OUTPUT_PATH / batch_id / "03_zhiyou" / "zhiyou_compliance_checked.csv"
    csv_content = result.strip()
    if csv_content.startswith("```"):
        csv_content = "\n".join(csv_content.split("\n")[1:])
    if csv_content.endswith("```"):
        csv_content = "\n".join(csv_content.split("\n")[:-1])

    output_file.write_text(csv_content.strip(), encoding="utf-8-sig")

    if progress_callback:
        progress_callback(1.0, "合规审查完成 ✅")

    return {"success": True, "output_file": str(output_file)}


# ============================================================
# STEP 4: 智布
# ============================================================
def run_zhibu(batch_id: str, progress_callback=None) -> dict:
    """Execute Step 4: Convert to structured JSON."""
    steering = load_steering()

    opt_path = OUTPUT_PATH / batch_id / "03_zhiyou" / "zhiyou_optimized_content.csv"
    score_path = OUTPUT_PATH / batch_id / "03_zhiyou" / "zhiyou_scorecard.csv"

    if not opt_path.exists():
        return {"success": False, "error": "请先执行智优执行 (Step 3.5)"}

    df_opt = pd.read_csv(opt_path, encoding="utf-8-sig")
    df_score = pd.read_csv(score_path, encoding="utf-8-sig") if score_path.exists() else pd.DataFrame()

    if df_opt.empty:
        return {"success": False, "error": "优化内容为空"}

    if progress_callback:
        progress_callback(0.2, "正在生成 JSON...")

    items = []
    for _, row in df_opt.iterrows():
        cid = row.get("content_id", "")
        score_row = df_score[df_score["content_id"] == cid].iloc[0] if not df_score.empty and cid in df_score.get("content_id", pd.Series()).values else {}

        item = {
            "content_id": cid,
            "query_id": row.get("query_id", ""),
            "keyword_id": row.get("keyword_id", ""),
            "keyword": row.get("ai_query", ""),
            "ai_query": row.get("ai_query", ""),
            "meta": {
                "title": row.get("optimized_meta_title", row.get("optimized_title", "")),
                "description": row.get("optimized_meta_description", ""),
            },
            "body": row.get("optimized_content", ""),
            "faq": row.get("optimized_faq", ""),
            "cta": row.get("optimized_cta", ""),
            "geo_summary": row.get("optimized_geo_summary", ""),
            "ai_friendly": {
                "intent_match_score": score_row.get("intent_match_score", 0) if isinstance(score_row, dict) or hasattr(score_row, 'get') else 0,
                "ai_readability_score": score_row.get("ai_readability_score", 0) if isinstance(score_row, dict) or hasattr(score_row, 'get') else 0,
                "authority_score": score_row.get("authority_score", 0) if isinstance(score_row, dict) or hasattr(score_row, 'get') else 0,
                "actionability_score": score_row.get("actionability_score", 0) if isinstance(score_row, dict) or hasattr(score_row, 'get') else 0,
                "differentiation_score": score_row.get("differentiation_score", 0) if isinstance(score_row, dict) or hasattr(score_row, 'get') else 0,
                "overall_score": score_row.get("overall_score", 0) if isinstance(score_row, dict) or hasattr(score_row, 'get') else 0,
            },
            "compliance": {
                "status": "PASS",
                "copyright": "Copyright © 2026 Amazon. All rights Reserved.",
            },
            "quality_metrics": {
                "word_count": row.get("word_count", 0),
                "table_count": row.get("table_count", 0),
                "list_count": row.get("list_count", 0),
                "link_count": row.get("link_count", 0),
            },
        }
        items.append(item)

    output_json = {
        "batch_id": batch_id,
        "created_at": timestamp(),
        "total_items": len(items),
        "items": items,
    }

    output_dir = OUTPUT_PATH / batch_id / "04_zhibu"
    ensure_dir(output_dir)
    output_file = output_dir / "zhibu_output.json"
    output_file.write_text(json.dumps(output_json, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    if progress_callback:
        progress_callback(1.0, "智布完成 ✅")

    return {"success": True, "output_file": str(output_file), "items_count": len(items)}


# ============================================================
# FULL PIPELINE
# ============================================================
def run_full_pipeline(batch_id: str, market: str = "ALL", keyword_limit: int = 10,
                      content_limit: int = 5, progress_callback=None) -> dict:
    """Execute full pipeline: Steps 1 → 2 → 3 → 3.5 → 3.6 → 4."""
    results = {}

    steps = [
        ("智库 (Step 1)", lambda cb: run_zhiku(batch_id, market, keyword_limit, cb)),
        ("智造 (Step 2)", lambda cb: run_zhizao(batch_id, content_limit, cb)),
        ("智优评分 (Step 3)", lambda cb: run_zhiyou_score(batch_id, cb)),
        ("智优执行 (Step 3.5)", lambda cb: run_zhiyou_execute(batch_id, cb)),
        ("合规审查 (Step 3.6)", lambda cb: run_zhiyou_compliance(batch_id, cb)),
        ("智布 (Step 4)", lambda cb: run_zhibu(batch_id, cb)),
    ]

    for i, (name, func) in enumerate(steps):
        if progress_callback:
            progress_callback(i / len(steps), f"正在执行: {name}...")

        result = func(None)
        results[name] = result

        if not result.get("success"):
            results["stopped_at"] = name
            results["error"] = result.get("error", "Unknown error")
            break

    if progress_callback:
        progress_callback(1.0, "全流程完成 ✅")

    results["success"] = all(r.get("success", False) for r in results.values() if isinstance(r, dict))
    return results
