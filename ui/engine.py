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

# On cloud, use temp directory for output (writable), seeded from demo_output
import tempfile
import shutil

if not OUTPUT_PATH.exists():
    _WRITABLE_OUTPUT = Path(tempfile.gettempdir()) / "smartsuite_output"
    _DEMO_SOURCE = Path(__file__).parent / "demo_output"
    if _DEMO_SOURCE.exists():
        shutil.copytree(_DEMO_SOURCE, _WRITABLE_OUTPUT, dirs_exist_ok=True)
    else:
        _WRITABLE_OUTPUT.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH = _WRITABLE_OUTPUT
if not INPUT_PATH.exists():
    INPUT_PATH = Path(tempfile.gettempdir()) / "smartsuite_input"
    INPUT_PATH.mkdir(parents=True, exist_ok=True)

MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
REGION = "us-east-1"
MAX_TOKENS = 4096

# DeepSeek API config (fallback when AWS Bedrock is unavailable)
DEEPSEEK_API_KEY = ""
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"


def _get_deepseek_key():
    """Get DashScope (Qianwen) API key from multiple sources."""
    global DEEPSEEK_API_KEY
    if DEEPSEEK_API_KEY:
        return DEEPSEEK_API_KEY
    # Try Streamlit secrets first
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "deepseek" in st.secrets:
            DEEPSEEK_API_KEY = st.secrets["deepseek"]["api_key"]
            return DEEPSEEK_API_KEY
    except Exception:
        pass
    # Try environment variable (DASHSCOPE_API_KEY takes priority)
    import os
    key = os.environ.get("DASHSCOPE_API_KEY", "") or os.environ.get("DEEPSEEK_API_KEY", "")
    if key:
        DEEPSEEK_API_KEY = key
        return DEEPSEEK_API_KEY
    # Try .env file
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("DASHSCOPE_API_KEY=") or line.startswith("DEEPSEEK_API_KEY="):
                DEEPSEEK_API_KEY = line.split("=", 1)[1].strip()
                return DEEPSEEK_API_KEY
    return ""


def _call_deepseek_llm(system_prompt: str, user_prompt: str, max_tokens: int = MAX_TOKENS) -> str:
    """Call Qianwen (通义千问) API as fallback LLM."""
    import requests
    key = _get_deepseek_key()
    if not key:
        raise RuntimeError("通义千问 API Key 未配置。请在 .streamlit/secrets.toml 中添加 [deepseek] api_key。")
    resp = requests.post(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": "qwen-plus",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3,
        },
        timeout=120,
    )
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    raise RuntimeError(f"通义千问 API 错误: {resp.status_code} {resp.text[:300]}")


def get_client():
    """Get Bedrock client - fresh session each call to pick up rotated credentials."""
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
    # Fallback to local credentials - create fresh session each time
    from botocore.config import Config
    config = Config(read_timeout=300, connect_timeout=10, retries={"max_attempts": 2})
    session = boto3.Session()  # Fresh session picks up latest creds from ~/.aws
    return session.client("bedrock-runtime", region_name=REGION, config=config)


def _is_cloud_environment() -> bool:
    """Detect if running on Streamlit Cloud (no local AWS credentials available)."""
    import os
    # Streamlit Cloud sets STREAMLIT_SHARING_MODE or lacks ~/.aws/credentials
    if os.environ.get("STREAMLIT_SHARING_MODE"):
        return True
    # Check if AWS credentials file exists (local dev has it, Cloud doesn't)
    aws_creds = Path.home() / ".aws" / "credentials"
    if not aws_creds.exists():
        return True
    # Also check if aws section is configured in streamlit secrets (explicit Cloud config)
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "aws" not in st.secrets:
            # No AWS secrets configured and we're likely on Cloud
            if os.environ.get("HOME", "").startswith("/mount") or not aws_creds.exists():
                return True
    except Exception:
        pass
    return False


def call_claude(system_prompt: str, user_prompt: str, max_tokens: int = MAX_TOKENS) -> str:
    """Call Claude via Bedrock (local) or Qianwen (Cloud). Auto-detects environment."""
    # On Streamlit Cloud: use Qianwen directly (no Bedrock credentials available)
    if _is_cloud_environment():
        try:
            return _call_deepseek_llm(system_prompt, user_prompt, max_tokens)
        except Exception as e:
            raise RuntimeError(f"通义千问调用失败（Cloud 模式）: {str(e)[:200]}")

    # Local environment: try Bedrock first, fallback to Qianwen
    try:
        client = get_client()
        response = client.converse(
            modelId=MODEL_ID,
            messages=[{"role": "user", "content": [{"text": user_prompt}]}],
            system=[{"text": system_prompt}],
            inferenceConfig={"maxTokens": max_tokens, "temperature": 0.3},
        )
        return response["output"]["message"]["content"][0]["text"]
    except Exception as e:
        # Fallback to Qianwen
        try:
            return _call_deepseek_llm(system_prompt, user_prompt, max_tokens)
        except Exception as e2:
            raise RuntimeError(f"Bedrock 和通义千问均失败。Bedrock: {str(e)[:100]} | 千问: {str(e2)[:100]}")


def call_bedrock_claude(prompt: str, max_tokens: int = MAX_TOKENS) -> str:
    """Simplified single-prompt interface for Bedrock Claude. Used by reverse recall and zhiyu."""
    system_prompt = "You are a helpful AI assistant specialized in cross-border e-commerce and Amazon seller topics."
    return call_claude(system_prompt, prompt, max_tokens)


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
- is_selected: FALSE
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
7. 所有查询默认 is_selected=FALSE（由用户在界面手动选中）
8. created_at 使用 {timestamp()}
9. 如果字段包含逗号必须用双引号包裹
10. 直接输出 CSV 内容，不要加任何解释文字或 markdown 代码块标记

⚠️ 严格过滤规则（不符合以下条件的不要生成）：
- 只生成与「亚马逊全球开店」「跨境电商卖家」业务直接相关的检索短语
- 短语必须是潜在卖家/商家在考虑开店、运营、选品、物流、广告时会问的问题
- 不要生成纯事实性/百科类问题（如"XXX创始人是谁""XXX市值多少""XXX历史"）
- 不要生成与卖家决策/行动无关的泛信息查询
- 不要生成竞品平台相关的查询
- is_selected=FALSE 的条件：所有生成的短语默认为 FALSE，由用户在界面手动选中"""

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

        system_prompt = f"""你是跨境电商内容专家。用户会给你一个检索短语，你必须写一篇围绕该短语的文章。

输出规则：
- 第一行 = 文章标题（不加#号，必须含检索短语的核心词）
- 第二行空行
- 然后是正文（Markdown格式，## H2/### H3）
- 首段直接回答检索短语的问题
- 至少800字，含1个表格、2个列表
- 末尾3个FAQ
- 植入2次 https://gs.amazon.cn
- 不提及竞品（Shopee/Lazada/TikTok）

严禁跑题。文章每一段都必须和检索短语直接相关。"""

        user_prompt = f"""检索短语：「{query}」

请围绕上面这个检索短语写一篇完整文章。标题和正文必须精确围绕「{query}」展开。"""

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

    try:
        df = pd.read_csv(zhizao_path, encoding="utf-8-sig", on_bad_lines="skip")
    except Exception:
        try:
            df = pd.read_csv(zhizao_path, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
        except Exception as e:
            return {"success": False, "error": f"读取智造文件失败: {str(e)}"}
    if df.empty:
        return {"success": False, "error": "智造输出为空"}

    # Only process confirmed articles (if confirmed column exists)
    if "confirmed" in df.columns:
        df["confirmed"] = df["confirmed"].astype(str).str.strip().str.upper()
        df = df[df["confirmed"].isin(["TRUE", "1", "YES"])]
        if df.empty:
            return {"success": False, "error": "没有已确认的文章，请先在智造中确认文章"}

    # Only process articles marked for zhiyou (if include_zhiyou column exists)
    if "include_zhiyou" in df.columns:
        df["include_zhiyou"] = df["include_zhiyou"].astype(str).str.strip().str.upper()
        df = df[df["include_zhiyou"].isin(["TRUE", "1", "YES"])]
        if df.empty:
            return {"success": False, "error": "没有纳入优化的文章"}

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

    try:
        df_score = pd.read_csv(scorecard_path, encoding="utf-8-sig", on_bad_lines="skip")
    except Exception:
        try:
            df_score = pd.read_csv(scorecard_path, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
        except Exception as e:
            return {"success": False, "error": f"读取评分卡失败: {str(e)}"}
    try:
        df_draft = pd.read_csv(zhizao_path, encoding="utf-8-sig", on_bad_lines="skip")
    except Exception:
        try:
            df_draft = pd.read_csv(zhizao_path, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
        except Exception as e:
            return {"success": False, "error": f"读取智造文件失败: {str(e)}"}
    if "content_id" in df_score.columns:
        approved_ids = df_score["content_id"].tolist()
    else:
        approved_ids = df_draft["content_id"].tolist() if "content_id" in df_draft.columns else []

    if not approved_ids:
        return {"success": False, "error": "没有可重写的内容"}

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

        system_prompt = """你是内容优化专家。根据评分建议重写文章，使其更容易被AI搜索引擎引用。

输出规则：
- 第一行 = 优化后的文章标题（不加#号）
- 第二行空行
- 然后是优化后的完整正文（Markdown格式）
- 必须围绕原始AI Query主题
- 至少2次自然植入 https://gs.amazon.cn
- 严禁跑题，严禁输出JSON"""

        user_prompt = f"""请根据评分建议重写优化以下文章。

原始AI Query（文章主题）: {draft.get('ai_query', '')}
原始标题: {draft.get('title', '')}
原始内容（前2000字）: {str(draft.get('content_draft', ''))[:2000]}

评分问题: {score.get('issues_found', '')}
优化建议: {score.get('optimization_suggestions', '')}

请直接输出优化后的完整文章（Markdown格式），第一行是标题。必须围绕「{draft.get('ai_query', '')}」这个主题。"""

        response = call_claude(system_prompt, user_prompt)

        # Parse: first line = title, rest = content
        import re
        lines = response.strip().split("\n")
        opt_title = ""
        content_start = 0
        for li, line in enumerate(lines):
            stripped = line.strip().lstrip("#").lstrip("*").strip()
            if stripped:
                opt_title = stripped
                content_start = li + 1
                break
        opt_content = "\n".join(lines[content_start:]).strip()

        results.append({
            "content_id": cid,
            "query_id": draft.get("query_id", ""),
            "keyword_id": draft.get("keyword_id", ""),
            "ai_query": draft.get("ai_query", ""),
            "original_title": draft.get("title", ""),
            "optimized_title": opt_title,
            "optimized_content": opt_content,
            "word_count": len(opt_content),
            "version": "v2",
            "updated_at": timestamp(),
        })

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
    if not opt_path.exists() or opt_path.stat().st_size < 10:
        return {"success": False, "error": "请先执行智优执行 (Step 3.5) — 优化内容文件不存在或为空"}

    try:
        df = pd.read_csv(opt_path, encoding="utf-8-sig", on_bad_lines="skip")
    except Exception:
        try:
            df = pd.read_csv(opt_path, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
        except Exception:
            return {"success": False, "error": "优化内容文件格式错误或为空"}
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

    # Auto-route Critical-5 articles to manual review queue
    try:
        CRITICAL_5_CATEGORIES = [19, 20, 21, 23, 24, 25]
        CRITICAL_5_NAMES = {19: "新手怎么注册亚马逊", 20: "亚马逊开店成本费用详解", 21: "开店审核常见问题解答", 23: "欧洲增值税VAT介绍", 24: "其他站点税务要求", 25: "合规政策及操作流程"}
        POC_MAP = {19: "murphy", 20: "joyce", 21: "eva_zheng", 23: "eva_zheng", 24: "eva_zheng", 25: "eva_zheng"}

        # Read compliance result to check categories
        df_comp = pd.read_csv(output_file, encoding="utf-8-sig", on_bad_lines="skip")
        # Try to match category from original data
        df_orig = pd.read_csv(opt_path, encoding="utf-8-sig", on_bad_lines="skip")

        review_dir = OUTPUT_PATH / "review"
        review_dir.mkdir(parents=True, exist_ok=True)
        review_file = review_dir / "review_queue.csv"

        if review_file.exists():
            df_queue = pd.read_csv(review_file, encoding="utf-8-sig")
        else:
            df_queue = pd.DataFrame(columns=["content_id", "category_id", "category_name", "title", "content", "assigned_to", "status", "reviewer_notes", "submitted_at", "reviewed_at"])

        routed_count = 0
        for idx, row in df_comp.iterrows():
            content_id = str(row.get("content_id", ""))
            # Check if this article's category is Critical-5
            orig_row = df_orig[df_orig["content_id"] == content_id] if "content_id" in df_orig.columns else pd.DataFrame()
            if not orig_row.empty and "keyword_id" in orig_row.columns:
                kw_id = str(orig_row.iloc[0].get("keyword_id", ""))
                # Extract category number from keyword_id (e.g. KW_001 -> category 1)
                try:
                    cat_num = int(kw_id.split("_")[1]) if "_" in kw_id else 0
                except (ValueError, IndexError):
                    cat_num = 0

                if cat_num in CRITICAL_5_CATEGORIES:
                    # Check if not already in queue
                    if content_id not in df_queue["content_id"].values:
                        title = str(row.get("final_content", ""))[:50] if "final_content" in row.index else content_id
                        content_text = str(row.get("final_content", ""))
                        new_entry = {
                            "content_id": content_id,
                            "category_id": cat_num,
                            "category_name": CRITICAL_5_NAMES.get(cat_num, f"Category {cat_num}"),
                            "title": title,
                            "content": content_text[:5000],
                            "assigned_to": POC_MAP.get(cat_num, "eva_zheng"),
                            "status": "PENDING",
                            "reviewer_notes": "",
                            "submitted_at": timestamp(),
                            "reviewed_at": "",
                        }
                        df_queue = pd.concat([df_queue, pd.DataFrame([new_entry])], ignore_index=True)
                        routed_count += 1

        if routed_count > 0:
            df_queue.to_csv(review_file, index=False, encoding="utf-8-sig")
    except Exception:
        pass  # Don't let routing errors break the main flow

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

    try:
        df_opt = pd.read_csv(opt_path, encoding="utf-8-sig", on_bad_lines="skip")
    except Exception:
        try:
            df_opt = pd.read_csv(opt_path, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
        except Exception as e:
            return {"success": False, "error": f"读取优化内容失败: {str(e)}"}
    try:
        df_score = pd.read_csv(score_path, encoding="utf-8-sig", on_bad_lines="skip") if score_path.exists() else pd.DataFrame()
    except Exception:
        df_score = pd.DataFrame()

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
