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

MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
REGION = "us-east-1"
MAX_TOKENS = 4096

# DeepSeek API config (fallback when AWS Bedrock is unavailable)
DEEPSEEK_API_KEY = ""
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"


def _get_deepseek_key():
    """Get DashScope (Qianwen) API key from multiple sources. No caching — always reads fresh."""
    global DEEPSEEK_API_KEY
    # If already set by main thread (for parallel workers), use it
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
        return key
    # Try .env file
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("DASHSCOPE_API_KEY=") or line.startswith("DEEPSEEK_API_KEY="):
                DEEPSEEK_API_KEY = line.split("=", 1)[1].strip()
                return DEEPSEEK_API_KEY
    return ""


def _call_deepseek_llm(system_prompt: str, user_prompt: str, max_tokens: int = MAX_TOKENS) -> str:
    """Call Qianwen (通义千问) API as fallback LLM. Uses qwen-plus."""
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


def _call_qianwen_max(system_prompt: str, user_prompt: str, max_tokens: int = MAX_TOKENS) -> str:
    """Call Qianwen-Max (通义千问旗舰版) for higher quality optimization tasks."""
    import requests
    key = _get_deepseek_key()
    if not key:
        raise RuntimeError("通义千问 API Key 未配置。")
    resp = requests.post(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": "qwen-max",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3,
        },
        timeout=180,
    )
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    raise RuntimeError(f"通义千问-Max API 错误: {resp.status_code} {resp.text[:300]}")


def call_zhiyou_model(system_prompt: str, user_prompt: str, max_tokens: int = MAX_TOKENS) -> str:
    """Dedicated model call for 智优 scoring and compliance.
    Three-stage architecture:
    - 智造: Claude (production) — structured content generation
    - 智优 score/compliance: Claude (strict rule execution) — THIS FUNCTION
    - 智优 rewrite final polish: call_zhiyou_polish() — Qwen for natural Chinese
    Priority: Claude (Bedrock) → Qianwen-Max (fallback)."""
    try:
        return call_claude(system_prompt, user_prompt, max_tokens)
    except Exception:
        # Fallback to Qwen-Max if Bedrock unavailable
        try:
            return _call_qianwen_max(system_prompt, user_prompt, max_tokens)
        except Exception:
            return _call_deepseek_llm(system_prompt, user_prompt, max_tokens)


def call_zhiyou_polish(system_prompt: str, user_prompt: str, max_tokens: int = MAX_TOKENS) -> str:
    """Final Chinese naturalness polish for 智优 rewrite output.
    Uses Qwen-Max for native Chinese fluency after Claude handles structure/compliance.
    Priority: Qianwen-Max → Qianwen-Plus (fallback)."""
    try:
        return _call_qianwen_max(system_prompt, user_prompt, max_tokens)
    except Exception:
        return _call_deepseek_llm(system_prompt, user_prompt, max_tokens)


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
    if os.environ.get("STREAMLIT_SHARING_MODE"):
        return True
    aws_creds = Path.home() / ".aws" / "credentials"
    if not aws_creds.exists():
        return True
    return False


def call_claude(system_prompt: str, user_prompt: str, max_tokens: int = MAX_TOKENS) -> str:
    """Call Claude via Bedrock first, fallback to Qianwen. Works on both local and Cloud."""
    # Always try Bedrock first (Cloud has AWS creds in secrets)
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

你的任务是：给定核心语义「{core_semantic}」，裂变出用户在 AI 搜索引擎（如 ChatGPT、DeepSeek、Perplexity、豆包、Kimi）中关于这个主题最可能输入的检索短语。

关键规则：
1. 所有短语必须直接包含或紧密围绕「{core_semantic}」这个词/概念
2. 模拟真实用户在 AI 平台上的提问习惯：
   - 完整的自然语句，像对话一样提问（不是搜索引擎的碎片关键词）
   - 每条短语 15-40 字，形成完整问句
   - 包含具体场景、条件或限定词（如"2026年"、"新手"、"中国卖家"、"小企业"、"工厂转型"）
   - 常见句式：怎么做/需要什么/有哪些/多少钱/步骤是什么/和XX比哪个好/有什么风险
3. 覆盖不同角度：是什么、怎么做、费用成本、优劣势、风险、对比、流程步骤、常见问题
4. 不要偏离核心词，不要生成与「{core_semantic}」无关的内容
5. 短语中应该能看到「{core_semantic}」或其同义词/变体

示例（假设核心语义为"亚马逊开店"）：
- 2026年中国卖家怎么在亚马逊开店？需要什么材料和条件？
- 亚马逊开店的完整流程是什么？从注册到上架需要多久？
- 个人没有公司可以在亚马逊开店吗？有什么限制？
- 亚马逊开店的费用大概需要多少？月租和佣金怎么算？
- 新手在亚马逊开店应该选北美站还是欧洲站？哪个更容易出单？"""

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

⚠️ 检索短语格式规则（最重要！）：
- 每条 ai_query 必须是 15-40 字的完整自然问句
- 模拟用户在 AI 搜索平台（ChatGPT、DeepSeek、豆包、Kimi）上真实对话的提问方式
- 必须是问句形式，包含疑问词（怎么/如何/什么/哪些/多少/为什么/能不能/是否/有没有）
- 包含具体场景或限定条件（如"2026年"、"新手"、"中国卖家"、"工厂转型"、"没经验"）
- 禁止输出碎片关键词或短词组（如"亚马逊开店"、"FBA费用"这种太短的不行）
- 正确示例：
  - "2026年中国卖家在亚马逊开店需要准备哪些材料和条件？" (25字) ✅
  - "新手第一次做亚马逊FBA发货流程是什么？有哪些注意事项？" (26字) ✅
  - "没有外贸经验的工厂老板想做跨境电商应该怎么入手？" (23字) ✅
- 错误示例：
  - "亚马逊开店" (5字) ❌ 太短
  - "FBA费用" (4字) ❌ 不是问句
  - "跨境电商选品" (6字) ❌ 碎片关键词

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
# STEP 2: 智造 - Content Brief Generation
# ============================================================
def generate_content_brief(query: str, current_ai_answer: str = "", knowledge: str = "") -> dict:
    """Generate a content brief before full article generation.
    Returns structured brief that guides article creation."""
    brief_prompt = f"""为以下 AI 检索短语生成一份内容生产简报（Content Brief）。

检索短语：「{query}」

{'当前 AI 回答摘要：' + current_ai_answer[:300] if current_ai_answer else ''}
{'可引用的官方数据：' + knowledge[:500] if knowledge else ''}

请输出 JSON 格式的 Content Brief：
{{
  "target_query": "检索短语",
  "search_intent": "用户搜索意图分析（为什么问这个问题）",
  "target_audience": "目标受众（谁会搜这个）",
  "content_angle": "内容切入角度（怎么比现有回答更好）",
  "must_cover_points": ["必须覆盖的要点1", "要点2", "要点3", "要点4", "要点5"],
  "differentiation": "与现有 AI 回答的差异化方向",
  "recommended_structure": ["开篇直答", "第二段建议", "第三段建议", "FAQ"],
  "data_to_cite": ["需要引用的数据点1", "数据点2"],
  "target_word_count": 1000,
  "seo_keywords": ["核心关键词1", "关键词2", "关键词3"]
}}

只输出 JSON，不要其他文字。"""

    try:
        result = call_claude("你是内容策略专家。输出纯 JSON。", brief_prompt, max_tokens=800)
        # Parse JSON
        import re
        text = result.strip()
        if text.startswith("```"):
            text = "\n".join(text.split("\n")[1:])
        if text.endswith("```"):
            text = "\n".join(text.split("\n")[:-1])
        m = re.search(r'\{[\s\S]*\}', text)
        if m:
            import json
            return json.loads(m.group())
    except Exception:
        pass

    return {"target_query": query, "must_cover_points": [], "recommended_structure": []}


# ============================================================
# STEP 2: 智造
# ============================================================
def run_zhizao(batch_id: str, content_limit: int = 5,
               progress_callback=None, template_id: str = "auto",
               reuse_template: dict = None, content_language: str = "zh-CN") -> dict:
    """Execute Step 2: Generate draft content for selected queries.
    template_id: 'auto' (detect from query), 'none' (from scratch),
                 'registration', 'fees', 'logistics', 'advertising', 'listing'
    reuse_template: dict with 'content' key — previously saved article to adapt
    content_language: 'zh-CN' (simplified), 'zh-TW' (traditional), 'en', 'ko', 'vi'
    """
    steering = load_steering()

    # Load topic-specific knowledge bases
    _REGISTRATION_KEYWORDS = ["注册", "入驻", "开店", "准备资料", "条件", "资质", "审核", "register", "registration", "sign up"]
    _reg_knowledge = ""
    _reg_skill = ""
    _reg_kb_path = INPUT_PATH / "knowledge" / "registration_knowledge_base.md"
    _reg_skill_path = INPUT_PATH / "knowledge" / "registration_writing_skill.md"
    if _reg_kb_path.exists():
        _reg_knowledge = _reg_kb_path.read_text(encoding="utf-8")
    if _reg_skill_path.exists():
        _reg_skill = _reg_skill_path.read_text(encoding="utf-8")

    # Load zhiku output
    zhiku_path = OUTPUT_PATH / batch_id / "01_zhiku" / "zhiku_ai_queries.csv"
    if not zhiku_path.exists():
        return {"success": False, "error": "请先执行智库 (Step 1)"}

    df_q = pd.read_csv(zhiku_path, encoding="utf-8-sig")

    # Filter selected
    if "is_selected" in df_q.columns:
        df_q["is_selected"] = df_q["is_selected"].astype(str).str.strip().str.upper()
        df_q_selected = df_q[df_q["is_selected"].isin(["TRUE", "1", "YES"])]
    else:
        df_q_selected = df_q

    selected_count = len(df_q_selected)

    # Skip already-generated queries (so subsequent runs produce NEW articles)
    output_dir = OUTPUT_PATH / batch_id / "02_zhizao"
    existing_output_file = output_dir / "zhizao_draft_content.csv"
    if existing_output_file.exists() and existing_output_file.stat().st_size > 0:
        try:
            df_existing = pd.read_csv(existing_output_file, encoding="utf-8-sig", on_bad_lines="skip")
            if not df_existing.empty and "ai_query" in df_existing.columns and "ai_query" in df_q_selected.columns:
                already_done = set(df_existing["ai_query"].dropna().astype(str).str.strip())
                df_q_selected = df_q_selected[~df_q_selected["ai_query"].astype(str).str.strip().isin(already_done)]
        except Exception:
            pass

    df_q = df_q_selected.head(content_limit)

    if df_q.empty:
        if selected_count == 0:
            return {"success": False, "error": "没有已选中的 AI Queries。请先回到【智库】页面，在短语列表中勾选要生成内容的短语（选中列 = ✅），然后再回来执行智造。"}
        else:
            return {"success": False, "error": f"已选中的 {selected_count} 条短语都已经生成过文章了。如需重新生成，请先在智造页面清空历史记录，或在智库中选中新的短语。"}

    output_dir = OUTPUT_PATH / batch_id / "02_zhizao"
    ensure_dir(output_dir)

    # Content templates — pre-defined structures for common topics
    TEMPLATES = {
        "registration": """## 文章结构模板（注册流程类）
请严格按照以下结构填充内容：

1. **开篇直答**（100字）：直接回答"如何注册"
2. **注册前准备**（150字）：需要的材料清单（表格形式）
3. **注册步骤详解**（300字）：分步骤说明（编号列表）
4. **常见审核问题**（150字）：审核失败原因+解决方案
5. **注册后下一步**（100字）：注册成功后的行动指引
6. **FAQ**（3个问答）
7. **CTA**：引导访问 https://gs.amazon.cn

必须包含：1个材料清单表格 + 1个步骤编号列表 + 1个费用对比列表""",

        "fees": """## 文章结构模板（费用成本类）
请严格按照以下结构填充内容：

1. **开篇直答**（80字）：一句话总结费用范围
2. **费用总览表**（200字）：所有费用项的表格（费用类型/金额/频率/说明）
3. **各项费用详解**（300字）：逐项解释每笔费用
4. **费用计算示例**（150字）：用具体数字举例月度/年度总费用
5. **省钱技巧**（100字）：降低费用的方法（列表形式）
6. **FAQ**（3个问答）
7. **CTA**：引导访问 https://gs.amazon.cn

必须包含：1个费用总览表格 + 1个计算示例列表 + 1个省钱技巧列表""",

        "logistics": """## 文章结构模板（物流仓储类）
请严格按照以下结构填充内容：

1. **开篇直答**（80字）：FBA vs FBM 核心区别
2. **物流方案对比表**（200字）：FBA/FBM/第三方的优劣势表格
3. **FBA 详细流程**（250字）：从发货到入仓的步骤
4. **费用结构**（150字）：仓储费+配送费的计算方式
5. **常见问题与解决**（100字）：丢件/延迟/退货处理
6. **FAQ**（3个问答）
7. **CTA**：引导访问 https://gs.amazon.cn

必须包含：1个方案对比表格 + 1个流程步骤列表 + 1个费用结构列表""",

        "advertising": """## 文章结构模板（广告推广类）
请严格按照以下结构填充内容：

1. **开篇直答**（80字）：广告类型概述和预期效果
2. **广告类型对比表**（200字）：SP/SB/SD 三种广告的对比表格
3. **新手广告策略**（250字）：从0到1的广告启动步骤
4. **预算分配建议**（150字）：不同阶段的预算分配方案
5. **优化技巧**（100字）：提升 ACOS 的实操建议（列表形式）
6. **FAQ**（3个问答）
7. **CTA**：引导访问 https://gs.amazon.cn

必须包含：1个广告类型对比表格 + 1个策略步骤列表 + 1个优化技巧列表""",

        "listing": """## 文章结构模板（Listing优化类）
请严格按照以下结构填充内容：

1. **开篇直答**（80字）：优质Listing的核心要素
2. **Listing要素评分表**（200字）：各要素重要性+评分标准的表格
3. **标题优化公式**（150字）：标题结构公式+好坏示例
4. **图片与A+内容**（200字）：图片要求+A+内容制作要点
5. **关键词策略**（100字）：前台/后台关键词布局
6. **FAQ**（3个问答）
7. **CTA**：引导访问 https://gs.amazon.cn

必须包含：1个要素评分表格 + 1个标题公式列表 + 1个关键词布局列表""",
    }

    results = []
    total = len(df_q)

    # --- Helper function for single article generation (enables parallelism) ---
    def _generate_single_article(idx_row_tuple):
        idx, row = idx_row_tuple
        query = str(row.get("ai_query", "")).strip()
        if not query or query == "nan":
            return None
        keyword = str(row.get("keyword", ""))
        keyword_id = str(row.get("keyword_id", ""))
        query_id = str(row.get("query_id", ""))

        # --- Step A: Pre-research — get current AI answer ---
        current_answer_summary = ""
        try:
            research_prompt = f"用100字简要回答这个问题：{query}"
            current_answer = _call_deepseek_llm(
                "你是AI搜索引擎。简洁回答用户问题。",
                research_prompt, max_tokens=200
            )
            current_answer_summary = current_answer[:500]
        except Exception:
            current_answer_summary = ""

        # --- Step D: Load relevant knowledge base ---
        knowledge_context = ""
        knowledge_dir = BASE_PATH / "input" / "knowledge"
        if knowledge_dir.exists():
            query_lower = query.lower()
            category = row.get("category", "")

            if category:
                for kb_file in knowledge_dir.glob("cat_*.md"):
                    if category in kb_file.name:
                        knowledge_context = kb_file.read_text(encoding="utf-8")[:1500]
                        break

            if not knowledge_context:
                keyword_to_cat = {
                    "注册": "cat_19", "开店": "cat_19", "开户": "cat_19",
                    "费用": "cat_20", "成本": "cat_20", "多少钱": "cat_20", "佣金": "cat_20",
                    "审核": "cat_21", "二审": "cat_21",
                    "物流": "cat_22", "仓储": "cat_22", "fba": "cat_22", "发货": "cat_22",
                    "vat": "cat_23", "增值税": "cat_23",
                    "税务": "cat_24", "税": "cat_24",
                    "合规": "cat_25", "政策": "cat_25",
                    "listing": "cat_26", "标题": "cat_26", "图片": "cat_26",
                    "品牌": "cat_27", "brand": "cat_27",
                    "运营": "cat_28", "店铺": "cat_28",
                    "广告": "cat_31", "ppc": "cat_31", "推广": "cat_31",
                    "选品": "cat_11", "品类": "cat_12",
                    "北美": "cat_15", "美国": "cat_15",
                    "欧洲": "cat_16", "英国": "cat_16", "德国": "cat_16",
                    "日本": "cat_17",
                    "旺季": "cat_34", "prime day": "cat_34", "黑五": "cat_34",
                }
                for kw, cat_prefix in keyword_to_cat.items():
                    if kw in query_lower:
                        for kb_file in knowledge_dir.glob(f"{cat_prefix}_*.md"):
                            knowledge_context = kb_file.read_text(encoding="utf-8")[:1500]
                            break
                        break

        knowledge_section = ""
        if knowledge_context:
            knowledge_section = f"\n【官方数据参考】请在文章中引用以下真实数据（标注数据来源）：\n{knowledge_context}\n"

        # --- Load user-uploaded materials (from batch/materials/) ---
        materials_dir = OUTPUT_PATH / batch_id / "materials"
        materials_context = ""
        if materials_dir.exists():
            query_lower_m = query.lower()
            for mat_file in materials_dir.iterdir():
                if not mat_file.is_file():
                    continue
                # Check if material filename relates to query keywords
                fname_lower = mat_file.stem.lower()
                query_words = [w for w in query_lower_m.replace("？", "").replace("?", "").split() if len(w) > 1]
                # Match if any query word appears in filename, or just load all materials (< 3 files)
                match = any(w in fname_lower for w in query_words) or len(list(materials_dir.glob("*"))) <= 3
                if match:
                    try:
                        if mat_file.suffix in [".txt", ".md", ".csv"]:
                            mat_text = mat_file.read_text(encoding="utf-8")[:2000]
                        elif mat_file.suffix == ".docx":
                            try:
                                from docx import Document as DocxDocument
                                doc = DocxDocument(str(mat_file))
                                mat_text = "\n".join([p.text for p in doc.paragraphs[:50]])[:2000]
                            except ImportError:
                                mat_text = ""
                        else:
                            mat_text = ""
                        if mat_text:
                            materials_context += f"\n--- 素材: {mat_file.name} ---\n{mat_text}\n"
                    except Exception:
                        pass
                if len(materials_context) > 4000:
                    break  # Don't exceed context limit

        if materials_context:
            knowledge_section += f"\n【用户上传素材（请从中提取相关信息写入文章）】\n{materials_context[:4000]}\n"

        # --- Language detection: pure English query → English article, else Chinese ---
        import re as _re
        _has_chinese = bool(_re.search(r'[\u4e00-\u9fff]', query))
        _is_pure_english = not _has_chinese and bool(_re.search(r'[a-zA-Z]', query))
        article_language = "English" if _is_pure_english else "Chinese"

        # Determine output language variant based on content_language param
        _lang_instruction = ""
        if content_language == "zh-TW":
            _lang_instruction = "\n\n【語言要求】整篇文章必須使用繁體中文（正體中文）撰寫，包括標題、正文、FAQ。不得使用簡體中文。使用台灣地區的慣用表達和用詞習慣。\n"
            article_language = "Chinese"  # Force Chinese mode even if query has some English
        elif content_language == "ko":
            _lang_instruction = "\n\n【언어 요구사항】전체 기사를 한국어로 작성해야 합니다. 제목, 본문, FAQ 모두 한국어로 작성하세요.\n"
            article_language = "Chinese"  # Use Chinese-style template structure
        elif content_language == "vi":
            _lang_instruction = "\n\n【Yêu cầu ngôn ngữ】Toàn bộ bài viết phải được viết bằng tiếng Việt, bao gồm tiêu đề, nội dung và FAQ.\n"
            article_language = "Chinese"  # Use Chinese-style template structure
        elif content_language == "en":
            article_language = "English"

        if article_language == "English":
            system_prompt = f"""You are a cross-border e-commerce content expert. Write a comprehensive article about the given search query.

{'[Competitive Analysis] Current AI answer summary:' + chr(10) + current_answer_summary + chr(10) + 'Your article must be more complete, authoritative, and actionable than the above.' + chr(10) if current_answer_summary else ''}{knowledge_section}
Output rules:
- First line = Article title (no # symbol, must contain core keywords from the query)
- Second line blank
- Then body text (Markdown format, ## H2/### H3)
- First paragraph: directly answer the search query
- Minimum 800 words, include 1 table, 2 lists
- End with 3 FAQ items
- Naturally include https://sell.amazon.com at least 2 times
- Do NOT mention competitors (Shopee/Lazada/TikTok)

Stay strictly on topic. Every paragraph must relate directly to the search query.

DATA & CITATION RULES (violating any = content rejected):
1. ❌ NEVER fabricate reports/data: Do NOT use "according to Amazon's 20XX report" or "statistics show" unless the report is explicitly provided in the [Official Data Reference] section above
2. ❌ NEVER invent percentages: Do NOT claim "increases by XX%" or "reduces XX%" without a verifiable source
3. ❌ NEVER use absolute superlatives: Do NOT say "the largest", "the best", "the most" — even with "one of" you need data to back it up
4. ✅ When describing fees/commissions, only cite publicly available Seller Central rates, and note "actual fees may vary per Seller Central"
5. ✅ When giving examples, use hypothetical framing: "For example, if a product is priced at $25..." NOT "According to reports, average costs are..."
6. ❌ NEVER name specific third-party brands: Do NOT write Apple/Nike/Samsung — use "a well-known electronics brand" etc.
7. ❌ NEVER interpret tax/legal regulations: Only quote official text + add "please consult a professional tax advisor"

PROHIBITED WORDS AND PHRASES (must NEVER appear in your output):
- Misleading/exaggerated terms: guaranteed profit, easy money, zero risk, 100% stable orders, monopolize market, strongest strategy, crush competitors
- Inducing violations: flash kill only, loss sale, bundled, penetrate, PK
- Contact/redirect terms: scan QR code, WeChat, QQ, contact info, leave contact
- Sensitive behavior terms: crack, block, guarantee, scam, sure profit, must explode, passive income
- Do NOT use superlatives like "best ever", "absolute", "ultimate", "number one"
- Do NOT make income or profit guarantees"""
        else:
            system_prompt = f"""你是跨境电商内容专家。用户会给你一个检索短语，你必须写一篇围绕该短语的文章。

{'【竞品分析】以下是AI搜索引擎对该问题的当前回答摘要：' + chr(10) + current_answer_summary + chr(10) + '你的文章必须比上面的回答更完整、更权威、更有操作指导性。补充它没有的表格、步骤、数据。' + chr(10) if current_answer_summary else ''}{knowledge_section}
输出规则：
- 第一行 = 文章标题（不加#号，必须含检索短语的核心词）
- 第二行空行
- 然后是正文（Markdown格式，## H2/### H3）
- 首段直接回答检索短语的问题
- 至少800字，含1个表格、2个列表
- 末尾3个FAQ
- 植入2次 https://gs.amazon.cn
- 不提及竞品（Shopee/Lazada/TikTok）

严禁跑题。文章每一段都必须和检索短语直接相关。

【数据与引用铁律 — 违反任何一条视为不合格】
1. ❌ 绝对禁止编造报告/数据：不得使用"根据亚马逊XX年XX报告"、"据XX统计"等表述，除非该报告在【官方数据参考】中明确提供
2. ❌ 禁止捏造百分比：不得使用"提升XX%"、"降低XX%"、"避开XX%的坑"等具体百分比，除非有明确数据来源
3. ❌ 禁止使用绝对化用语：不得说"全球最大"、"流量最大"、"力度最大"、"最XX的"，即使加了"之一"也需有数据支撑
4. ✅ 如需描述费率/佣金，只能引用 Seller Central 公开可查的标准费率，并标注"以卖家平台实际显示为准"
5. ✅ 如需举例说明，使用假设性表述："假设一件售价$25的商品…"而非"根据报告，平均费用为…"
6. ❌ 禁止提及具体第三方品牌名：不得直接写 Apple/Nike/Samsung 等品牌名，用"某知名电子品牌"等泛称代替
7. ❌ 禁止对税务/法规做解读：税务信息只能引用官方原文+注明"请咨询专业税务顾问"

【敏感词禁用清单（2026年，以下词汇绝对不能出现在文章中）】
一、常见敏感词（禁止使用）：疫情、平台、销售、品牌、行业、线上电商生意、海外电商、搜索、消费者、全球、优质、真正、中心、精准、全方位、领先、正品、专利、税务、独立、推荐
注意："平台"应替换为"网站"或"站点"。例外：「亚马逊卖家平台」「亚马逊全球物流团队订舱平台」作为固定翻译名可保留。
二、诱导违规词：仅限、秒杀、亏本、彻底、捆绑、PK、渗透
三、违规引流导流词：扫码、微信、QQ、联系方式
四、违规操作/敏感行为词：破解、屏蔽、担保、诈骗、稳赚、必爆、躺赚、稳出单
五、禁止句式（及类似表达）：绝对能做爆海外市场、做跨境轻松稳赚大钱、加微信/QQ领取出海干货、留联系方式对接海外货源、垄断海外多国电商市场、全网最强跨境运营玩法、100%稳定出单无风险、极致打法横扫海外同行

注意：以上词汇即使在正面语境中也不得使用。请用中性客观的表述替代。
另外：禁止使用"市场/细分市场"，应替换为"站点/国家/地区/行业"。{_lang_instruction}"""

        # Template detection and instruction
        template_instruction = ""
        actual_template = template_id
        if template_id == "auto":
            query_lower = query.lower()
            if any(kw in query_lower for kw in ["注册", "开店", "开户", "register", "sign up", "create account", "申请", "审核", "đăng ký", "등록"]):
                actual_template = "registration"
            elif any(kw in query_lower for kw in ["费用", "成本", "多少钱", "价格", "收费", "佣金", "cost", "fee", "price", "how much", "chi phí", "비용"]):
                actual_template = "fees"
            elif any(kw in query_lower for kw in ["物流", "仓储", "fba", "fbm", "发货", "配送", "运费", "shipping", "fulfillment", "warehouse", "vận chuyển", "물류", "배송"]):
                actual_template = "logistics"
            elif any(kw in query_lower for kw in ["广告", "推广", "ppc", "cpc", "acos", "sponsor", "advertis", "营销", "引流", "quảng cáo", "광고"]):
                actual_template = "advertising"
            elif any(kw in query_lower for kw in ["listing", "标题", "图片", "关键词", "a+", "详情页", "五点", "bullet", "seo", "优化listing", "tối ưu", "리스팅"]):
                actual_template = "listing"
            else:
                actual_template = "none"

        if actual_template != "none" and actual_template in TEMPLATES:
            if article_language == "English":
                template_instruction = f"\n\nUse a structured article format with: Direct Answer → Details/Steps → Comparison Table → FAQ → CTA (https://sell.amazon.com)\n\nEnsure at least 1 table, 2 lists, and 3 FAQ items."
            else:
                template_instruction = f"\n\n{TEMPLATES[actual_template]}\n\n请严格按照上述模板结构生成内容，每个部分都必须有内容。"

        # Inject registration-specific knowledge base and writing rules
        if actual_template == "registration" and (_reg_knowledge or _reg_skill):
            reg_rules = ""
            if _reg_skill:
                reg_rules += f"\n\n【注册类写作规范（必须严格遵守，遵守可免走人工审核）】\n{_reg_skill[:3000]}\n"
            if _reg_knowledge:
                reg_rules += f"\n\n【注册类官方知识库（只能使用以下信息，不得编造）】\n{_reg_knowledge[:4000]}\n"
            template_instruction += reg_rules

        user_prompt = f"""检索短语：「{query}」
{template_instruction}
请围绕上面这个检索短语写一篇完整文章。标题和正文必须精确围绕「{query}」展开。""" if article_language != "English" else f"""Search phrase: "{query}"
{template_instruction}
Write a complete article focused precisely on the above search phrase. Title and body must directly address "{query}"."""

        # If reuse_template is provided, use adaptation mode
        if reuse_template and reuse_template.get("content"):
            base_content = reuse_template["content"][:3000]
            base_query = reuse_template.get("source_query", "")
            if article_language == "English":
                user_prompt = f"""Search phrase: "{query}"

Below is an existing high-quality reference article (original phrase: "{base_query}"):
---
{base_content}
---

Adapt this reference article for the new search phrase "{query}":
1. Keep the overall structure and format
2. Rewrite all content to focus on "{query}"
3. Replace irrelevant details, add information relevant to the new phrase
4. Ensure the title contains core keywords from "{query}"
5. Keep tables, lists, FAQ structure
6. Keep the link https://sell.amazon.com

Output: First line = new title (no #), then blank line, then full body."""
            else:
                user_prompt = f"""检索短语：「{query}」

以下是一篇已有的优质参考文章（原短语：「{base_query}」）：
---
{base_content}
---

请基于上面的参考文章，针对新检索短语「{query}」进行改写调整：
1. 保留文章的整体结构和格式
2. 将所有内容重新围绕「{query}」展开
3. 替换不相关的细节，补充与新短语相关的信息
4. 确保标题包含「{query}」的核心词
5. 保留表格、列表、FAQ的结构
6. 确保链接 https://gs.amazon.cn 保留

输出：第一行=新标题（不加#），然后空行，然后是完整正文。"""

        response = call_claude(system_prompt, user_prompt)

        # Parse response
        import re
        lines = response.strip().split("\n")
        title = ""
        content_start = 0
        for i, line in enumerate(lines):
            stripped = line.strip().lstrip("#").lstrip("*").strip()
            if stripped:
                title = stripped
                content_start = i + 1
                break

        content_body = "\n".join(lines[content_start:]).strip()
        faq_match = re.search(r'(##\s*(?:常见问题|FAQ).+)', content_body, re.DOTALL | re.IGNORECASE)
        faq_section = faq_match.group(1) if faq_match else ""

        return {
            "content_id": f"C_{keyword_id}_{abs(hash(query)) % 100000:05d}",
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
            "confirmed": "True",
            "include_zhiyou": "True",
        }

    # --- Execute in parallel (5 concurrent workers) ---
    from concurrent.futures import ThreadPoolExecutor, as_completed

    MAX_WORKERS = 5  # 5 parallel API calls for faster generation
    items = list(df_q.iterrows())

    # Pre-fetch API key in main thread (st.secrets not accessible from worker threads)
    _prefetched_key = _get_deepseek_key()
    if _prefetched_key:
        global DEEPSEEK_API_KEY
        DEEPSEEK_API_KEY = _prefetched_key

    if progress_callback:
        progress_callback(0.05, f"正在并行生成 {total} 篇内容（{MAX_WORKERS} 并发）...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_generate_single_article, item): item[0] for item in items}
        completed = 0
        errors = []
        for future in as_completed(futures):
            try:
                result = future.result()
                if result is not None:
                    results.append(result)
            except Exception as e:
                errors.append(str(e)[:100])
            completed += 1
            if progress_callback:
                progress_callback(completed / total, f"已完成 {completed}/{total} 篇...")

    # Sort results by content_id to maintain order
    results.sort(key=lambda x: x.get("content_id", ""))

    # If no results but had errors, report them
    if not results and errors:
        return {"success": True, "output_file": "", "articles_generated": 0,
                "error_details": "; ".join(errors[:3])}

    # Save as CSV
    df_out = pd.DataFrame(results)
    output_file = output_dir / "zhizao_draft_content.csv"

    # Append to existing file (don't overwrite previous batches)
    if output_file.exists() and output_file.stat().st_size > 0:
        try:
            existing = pd.read_csv(output_file, encoding="utf-8-sig", on_bad_lines="skip")
            combined = pd.concat([existing, df_out], ignore_index=True)
            if "ai_query" in combined.columns:
                combined = combined.drop_duplicates(subset=["ai_query"], keep="last")
            combined.to_csv(output_file, index=False, encoding="utf-8-sig")
        except pd.errors.EmptyDataError:
            df_out.to_csv(output_file, index=False, encoding="utf-8-sig")
    else:
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

def _normalize_zhizao_df(df: "pd.DataFrame") -> "pd.DataFrame":
    """Normalize zhizao output DataFrame to ensure consistent columns for zhiyou.
    Handles common format variations from AI-generated CSV output."""
    # Standard column mapping: possible AI output names → expected names
    col_aliases = {
        "content": "content_draft",
        "draft": "content_draft",
        "article": "content_draft",
        "body": "content_draft",
        "text": "content_draft",
        "article_title": "title",
        "headline": "title",
        "query": "ai_query",
        "search_query": "ai_query",
        "id": "content_id",
    }
    for old_name, new_name in col_aliases.items():
        if old_name in df.columns and new_name not in df.columns:
            df = df.rename(columns={old_name: new_name})

    # Ensure required columns exist with defaults
    required_defaults = {
        "content_id": lambda df: [f"C_AUTO_{i+1:03d}" for i in range(len(df))],
        "query_id": "",
        "keyword_id": "",
        "ai_query": "",
        "title": "",
        "content_draft": "",
        "confirmed": "TRUE",
        "include_zhiyou": "TRUE",
    }
    for col, default in required_defaults.items():
        if col not in df.columns:
            df[col] = default(df) if callable(default) else default

    # Normalize boolean columns
    for bool_col in ["confirmed", "include_zhiyou"]:
        if bool_col in df.columns:
            df[bool_col] = df[bool_col].astype(str).str.strip().str.upper()
            df[bool_col] = df[bool_col].apply(
                lambda x: "TRUE" if x in ["TRUE", "1", "YES", "T"] else "FALSE"
            )

    return df


def _normalize_scorecard_df(df: "pd.DataFrame") -> "pd.DataFrame":
    """Normalize scorecard DataFrame: ensure score columns are numeric."""
    score_cols = [c for c in df.columns if c.endswith("_score")]
    for col in score_cols:
        # Handle values like "4.3/5", "4.3分", or plain "4.3"
        df[col] = (
            df[col].astype(str)
            .str.replace(r"[/／].*", "", regex=True)  # Remove "/5" suffix
            .str.replace(r"[分点]", "", regex=True)   # Remove Chinese suffixes
            .str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Ensure is_approved column exists and is normalized
    if "is_approved" in df.columns:
        df["is_approved"] = df["is_approved"].astype(str).str.strip().str.upper()
    else:
        # Calculate from overall_score if missing
        if "overall_score" in df.columns:
            df["is_approved"] = df["overall_score"].apply(
                lambda x: "TRUE" if pd.notna(x) and x >= 4.0 else "FALSE"
            )
        else:
            df["is_approved"] = "TRUE"

    return df


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

    # Normalize zhizao output to standard format
    df = _normalize_zhizao_df(df)

    # Only process confirmed articles
    df = df[df["confirmed"].isin(["TRUE", "1", "YES"])]
    if df.empty:
        return {"success": False, "error": "没有已确认的文章，请先在智造中确认文章"}

    # Only process articles marked for zhiyou
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

    result = call_zhiyou_model(system_prompt, user_prompt)

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

    # Post-process: normalize scorecard to ensure numeric scores
    try:
        df_sc = pd.read_csv(output_file, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
        df_sc = _normalize_scorecard_df(df_sc)
        df_sc.to_csv(output_file, index=False, encoding="utf-8-sig")
    except Exception:
        pass  # If normalization fails, keep raw output

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
def run_zhiyou_execute(batch_id: str, progress_callback=None, content_language: str = "zh-CN") -> dict:
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

    # Normalize both DataFrames
    df_score = _normalize_scorecard_df(df_score)
    df_draft = _normalize_zhizao_df(df_draft)

    # Get content IDs to rewrite (all scored articles, not just "approved")
    if "content_id" in df_score.columns and not df_score["content_id"].dropna().empty:
        approved_ids = df_score["content_id"].dropna().tolist()
    elif "content_id" in df_draft.columns and not df_draft["content_id"].dropna().empty:
        approved_ids = df_draft["content_id"].dropna().tolist()
    else:
        # Fallback: generate IDs and use all drafts
        approved_ids = [f"C_AUTO_{i+1:03d}" for i in range(len(df_draft))]
        df_draft["content_id"] = approved_ids

    if not approved_ids:
        return {"success": False, "error": "没有可重写的内容"}

    results = []
    total = len(approved_ids)

    def _rewrite_single(i_cid_tuple):
        i, cid = i_cid_tuple
        draft_row = df_draft[df_draft["content_id"] == cid]
        score_row = df_score[df_score["content_id"] == cid] if "content_id" in df_score.columns else pd.DataFrame()

        # If no match by content_id, try matching by index
        if draft_row.empty and i < len(df_draft):
            draft_row = df_draft.iloc[[i]]
        if score_row.empty and i < len(df_score):
            score_row = df_score.iloc[[i]]

        if draft_row.empty:
            return None

        draft = draft_row.iloc[0]
        score = score_row.iloc[0] if not score_row.empty else pd.Series({"issues_found": "", "optimization_suggestions": "请优化内容结构、增加权威性和可操作性"})

        # Check if this article is registration-related
        _query_lower = str(draft.get('ai_query', '')).lower()
        _is_reg = any(kw in _query_lower for kw in ["注册", "入驻", "开店", "准备资料", "条件", "资质", "审核", "register", "registration"])
        _reg_extra = ""
        if _is_reg:
            _reg_kb_path = Path(__file__).parent.parent / "input" / "knowledge" / "registration_knowledge_base.md"
            _reg_sk_path = Path(__file__).parent.parent / "input" / "knowledge" / "registration_writing_skill.md"
            if _reg_sk_path.exists():
                _reg_extra += f"\n\n【注册类写作规范（必须遵守，遵守可免走人工审核）】\n{_reg_sk_path.read_text(encoding='utf-8')[:2500]}\n"
            if _reg_kb_path.exists():
                _reg_extra += f"\n\n【注册类知识库（只能使用以下事实）】\n{_reg_kb_path.read_text(encoding='utf-8')[:3000]}\n"

        # Build language instruction for zhiyou
        _zhiyou_lang_instruction = ""
        if content_language == "zh-TW":
            _zhiyou_lang_instruction = "\n\n【語言要求】優化後的文章必須使用繁體中文（正體中文），包括標題、正文、FAQ。不得輸出簡體中文。使用台灣地區慣用表達。\n"
        elif content_language == "ko":
            _zhiyou_lang_instruction = "\n\n【언어 요구사항】최적화된 기사는 한국어로 작성되어야 합니다.\n"
        elif content_language == "vi":
            _zhiyou_lang_instruction = "\n\n【Yêu cầu ngôn ngữ】Bài viết tối ưu phải được viết bằng tiếng Việt.\n"

        system_prompt = f"""你是内容优化专家。根据评分建议重写文章，使其更容易被AI搜索引擎引用。

输出规则：
- 第一行 = 优化后的文章标题（不加#号）
- 第二行空行
- 然后是优化后的完整正文（Markdown格式）
- 必须围绕原始AI Query主题
- 至少2次自然植入 https://gs.amazon.cn
- 【重要】必须保留并优化 FAQ 板块（## 常见问题 / FAQ），至少3个问答对，用 Q: A: 或 ### 问题 格式
- FAQ 是 AI 引擎最容易抓取引用的结构化内容，绝对不能删除
- 严禁跑题，严禁输出JSON

【敏感词禁用清单（2026年，以下词汇绝对不能出现在优化后的文章中）】
一、常见敏感词（禁止使用）：疫情、平台（可用"站点/网站"代替，"亚马逊卖家平台"除外）、销售、品牌、行业、线上电商生意、海外电商、搜索、消费者、全球、优质、真正、中心、精准、全方位、领先、正品、专利、税务、独立、推荐
二、诱导违规词：仅限、秒杀、亏本、彻底、捆绑、PK、渗透
三、违规引流导流词：扫码、微信、QQ、联系方式
四、违规操作/敏感行为词：破解、屏蔽、担保、诈骗、稳赚、必爆、躺赚、稳出单
五、禁止句式：绝对能做爆海外市场、做跨境轻松稳赚大钱、加微信/QQ领取出海干货、留联系方式对接海外货源、垄断海外多国电商市场、全网最强跨境运营玩法、100%稳定出单无风险、极致打法横扫海外同行
六、绝对化用语（禁止使用）：最好、最佳、最便宜、最贵、最快、最强、最优、第一、顶级、唯一、No.1
  - 替代方式：用"往往是较为…之一"/"可能是…"/"相对较…"代替
七、品牌合规禁用词：
  - "生态/生态系统/生态圈" → 替换为"服务体系/产业服务集群"
  - "合作伙伴" → 替换为"第三方服务提供商"
  - "市场/细分市场" → 替换为"站点/国家/地区"
  - "最佳实践" → 替换为"实践分享/推荐做法"
八、保证性陈述（禁止使用）：一定能、必定、保证增长、确保销量、转化率会提升/降低XX%
  - 替代方式：用"可能"/"约"/"通常"/"往往"等限定词

【数据与免责声明规范】
- 引用任何具体数据（如百分比、费率）必须标注来源（如"根据亚马逊官方2026年费率表"）
- 假设性/估算数据必须加脚注："以上数据为估算示例，实际费用因产品和具体情况而异，仅供参考。"
- 费率/费用对比表底部必须添加免责说明
- 描述服务特性时不能夸大（如FBA退货不是所有类目免费，需添加"多数类目"等限定）

【注册表述规范】
- 注册必须表述为"通过亚马逊卖家平台注册"，不能用"全球开店注册"
- 服务提供方为"亚马逊/亚马逊XX站"，不能是"全球开店"

注意：如果原文中含有上述敏感词，优化时必须用中性客观的表述替代。
{_reg_extra}{_zhiyou_lang_instruction}"""

        user_prompt = f"""请根据评分建议重写优化以下文章。

原始AI Query（文章主题）: {draft.get('ai_query', '')}
原始标题: {draft.get('title', '')}
原始内容（前2000字）: {str(draft.get('content_draft', ''))[:2000]}

评分问题: {score.get('issues_found', '')}
优化建议: {score.get('optimization_suggestions', '')}

请直接输出优化后的完整文章（Markdown格式），第一行是标题。必须围绕「{draft.get('ai_query', '')}」这个主题。
⚠️ 文章末尾必须保留 FAQ 板块（至少3个问答），这是 AI 引擎抓取的关键结构。"""

        response = call_zhiyou_model(system_prompt, user_prompt)

        # --- Stage 3: Chinese naturalness polish via Qwen ---
        try:
            _polish_lang_note = ""
            if content_language == "zh-TW":
                _polish_lang_note = "\n8. 【重要】全文必須使用繁體中文（正體中文），不得有任何簡體中文字。使用台灣慣用表達。\n"
            elif content_language == "ko":
                _polish_lang_note = "\n8. 전체 기사는 한국어로 유지해야 합니다.\n"
            elif content_language == "vi":
                _polish_lang_note = "\n8. Toàn bộ bài viết phải được giữ bằng tiếng Việt.\n"

            polish_prompt = f"""你是一位资深中文编辑。请对以下文章做最终润色，只优化中文表达的自然度和流畅性。

规则：
1. 不改变文章结构（H1/H2/H3/FAQ/表格/列表全部保留）
2. 不改变事实内容和数据
3. 不删除任何链接（https://gs.amazon.cn 等）
4. 不添加新信息
5. 只修改不自然、生硬、翻译腔的表达，让文章读起来更像母语人士写的
6. 保持专业、客观中立的语气
7. 输出完整文章，格式不变{_polish_lang_note}

文章：
{response}"""
            _polish_sys = "你是中文内容润色专家。只优化表达自然度，不改变结构、事实和链接。"
            if content_language == "zh-TW":
                _polish_sys = "你是繁體中文內容潤色專家。確保全文使用繁體中文（正體中文），使用台灣慣用表達。只優化表達自然度，不改變結構、事實和連結。"
            response = call_zhiyou_polish(
                _polish_sys,
                polish_prompt, max_tokens=MAX_TOKENS
            )
        except Exception:
            pass  # If polish fails, use Claude's output directly

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

        return {
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
            "confirmed": "True",
            "needs_poc_review": "False",
            "poc_approved": "True",
        }

    # --- Execute in parallel (3 concurrent workers) ---
    from concurrent.futures import ThreadPoolExecutor, as_completed

    MAX_WORKERS = 3
    items = list(enumerate(approved_ids))

    if progress_callback:
        progress_callback(0.05, f"正在并行重写 {total} 篇内容（{MAX_WORKERS} 并发）...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_rewrite_single, item): item for item in items}
        completed = 0
        for future in as_completed(futures):
            try:
                result = future.result()
                if result is not None:
                    results.append(result)
            except Exception:
                pass
            completed += 1
            if progress_callback:
                progress_callback(completed / total, f"已完成 {completed}/{total} 篇重写...")

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
    zhizao_fallback_path = OUTPUT_PATH / batch_id / "02_zhizao" / "zhizao_draft_content.csv"

    # Try optimized content first, fall back to zhizao draft
    source_path = None
    content_col = "optimized_content"
    title_col = "optimized_title"

    if opt_path.exists() and opt_path.stat().st_size > 10:
        source_path = opt_path
    elif zhizao_fallback_path.exists() and zhizao_fallback_path.stat().st_size > 10:
        # Fallback: use zhizao draft directly for compliance check
        source_path = zhizao_fallback_path
        content_col = "content_draft"
        title_col = "title"
    else:
        return {"success": False, "error": "请先执行智优执行 (Step 3.5) 或智造 (Step 2) — 没有可审查的内容"}

    try:
        df = pd.read_csv(source_path, encoding="utf-8-sig", on_bad_lines="skip")
    except Exception:
        try:
            df = pd.read_csv(source_path, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
        except Exception:
            return {"success": False, "error": "内容文件格式错误或为空"}
    if df.empty:
        return {"success": False, "error": "内容为空"}

    # Normalize column names for consistent access
    if content_col not in df.columns:
        # Try common alternatives
        for alt in ["optimized_content", "content_draft", "content", "body", "text"]:
            if alt in df.columns:
                content_col = alt
                break
    if title_col not in df.columns:
        for alt in ["optimized_title", "title", "headline"]:
            if alt in df.columns:
                title_col = alt
                break

    if progress_callback:
        progress_callback(0.1, "正在进行合规审查...")

    # Build content for review
    articles_text = ""
    for idx, row in df.iterrows():
        content = str(row.get(content_col, ""))[:3000]
        title = str(row.get(title_col, ""))
        articles_text += f"\n---\ncontent_id: {row.get('content_id', idx)}\ntitle: {title}\ncontent: {content}\n"

    system_prompt = f"""你是 Smart Suite 合规审查模块。严格按照以下合规规则审查并自动修正内容。

{steering}

重点关注 Step 3.6: 合规审查 的所有规则（禁用词、数据规范、注册表述、品牌使用等）。

【最高优先级：虚假数据/报告检测 — 发现即 FIXED】
❗ AI 生成的内容极易编造不存在的报告和数据。请重点排查以下模式并自动修正：
1. "根据亚马逊XX年XX报告/白皮书/数据" — 除非引用的是 Seller Central 公开费率页面，否则该报告大概率不存在 → 删除整句或改为"根据亚马逊卖家平台公开信息"
2. "据统计/研究表明/报告指出 + 具体数字%" — 无法验证的统计数据 → 删除具体数字，改为定性描述（如"显著提升"）
3. "平均占售价的XX%至XX%" — 除非是已知的标准佣金费率（如8%-15%），否则视为编造 → 改为"具体费率因品类而异，详见卖家平台费率页面"
4. "超过X万个/X千个卖家/账号因XXX被关闭/封号" — 内部执法数据不可对外引用 → 删除整句或改为"违规卖家可能面临账号限制"
5. "根据XX机构XX年数据，罚款平均为X万美元" — 改为"可能面临相关法规的处罚"
6. "避开/解决/降低XX%的常见问题/风险/坑" — 无根据的百分比 → 删除百分比，改为"有效避免多数常见问题"
7. "全球最大/流量最大/力度最大/增速最快" — 绝对化表述 → 改为"领先的/较大的/主要的"
8. 具体第三方品牌名(Apple/Nike/Samsung等)在举例语境 → 改为"某知名XX品牌"

每检测到一条，在 fixes_applied 中标注修正了什么。

【敏感词禁用清单（2026年）— 以下词汇在内容中出现即视为不合规，必须替换】
一、常见敏感词（禁止使用）：疫情、平台（可用"站点/网站"代替，"亚马逊卖家平台"除外）、销售、品牌、行业、线上电商生意、海外电商、搜索、消费者、全球、优质、真正、中心、精准、全方位、领先、正品、专利、税务、独立、推荐
二、诱导违规词：仅限、秒杀、亏本、彻底、捆绑、PK、渗透
三、违规引流导流词：扫码、微信、QQ、联系方式
四、违规操作/敏感行为词：破解、屏蔽、担保、诈骗、稳赚、必爆、躺赚、稳出单
五、禁止句式：绝对能做爆海外市场、做跨境轻松稳赚大钱、加微信/QQ领取出海干货、留联系方式对接海外货源、垄断海外多国电商市场、全网最强跨境运营玩法、100%稳定出单无风险、极致打法横扫海外同行
六、绝对化用语（禁止）：最好、最佳、最便宜、最贵、最快、最强、最优、第一、顶级、唯一
  - 替换方式：用"往往是较为…之一"/"可能是…"/"相对较…"代替
七、品牌合规禁用词：
  - "生态/生态系统/生态圈" → 替换为"服务体系/产业服务集群"
  - "合作伙伴" → 替换为"第三方服务提供商"
  - "市场/细分市场" → 替换为"站点/国家/地区"
  - "最佳实践" → 替换为"实践分享/推荐做法"
八、保证性陈述（禁止）：一定能、必定、保证增长、确保销量、转化率会提升/降低XX%
  - 替换方式：用"可能"/"约"/"通常"/"往往"等限定词
九、数据与免责声明：
  - 引用数据必须标注来源
  - 假设性/估算数据必须加脚注"以上为示例，实际费用因情况而异"
  - 服务描述不能夸大（如FBA退货并非所有类目免费，需加"多数类目"限定）

审查要求：若发现上述敏感词，compliance_status 标记为 FIXED，在 fixes_applied 中说明替换了哪些词，在 final_content 中输出替换后的内容。"""

    user_prompt = f"""请对以下内容进行合规审查。

{articles_text}

要求：
1. 检查所有合规规则（禁用词、数据引用、注册表述、品牌使用、地图敏感地区等）
2. 自动修正可修复的问题
3. 输出 CSV 格式，字段：content_id,query_id,keyword_id,compliance_status,issues_found,fixes_applied,final_content,final_faq,final_cta,final_geo_summary,updated_at
4. compliance_status: PASS(无问题) / FIXED(已修正) / BLOCKED(需人工)
5. updated_at: {timestamp()}
6. 直接输出 CSV，不要加解释或代码块标记"""

    result = call_zhiyou_model(system_prompt, user_prompt, max_tokens=MAX_TOKENS)

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
# STEP 3.7: Pre-Legal Self-Check（送审前自审核）
# ============================================================
def run_pre_legal_check(batch_id: str, progress_callback=None) -> dict:
    """Execute Step 3.7: Pre-Legal Self-Check v2 before sending to Legal/PR/Tax review.
    
    v2 improvements:
    - Context-aware checking (regex + surrounding context validation)
    - Whitelist exemptions for common false positives
    - Severity-based filtering by content criticality level
    - Deduplication (same-category issues reported only once per article)
    - Max 5 actionable findings per article to reduce noise
    
    Scans all articles in the batch against 4-layer compliance rules:
    Layer 1: SOP判定 (is Legal/PR/Tax review required?)
    Layer 2: Legal Questionnaire 8项检查
    Layer 3: Playbook合规规则 (General+Legal+PR+Tax)
    Layer 4: RoA隐私合规 (VN/KR/TW)
    
    Output: per-article PASS/WARNING/BLOCKED + detailed findings (max 5)
    BLOCKED articles are filtered out from downstream 智布/送审 flow.
    """
    import re

    # --- Load source content ---
    compliance_path = OUTPUT_PATH / batch_id / "03_zhiyou" / "zhiyou_compliance_checked.csv"
    opt_path = OUTPUT_PATH / batch_id / "03_zhiyou" / "zhiyou_optimized_content.csv"
    zhizao_path = OUTPUT_PATH / batch_id / "02_zhizao" / "zhizao_draft_content.csv"

    source_path = None
    content_col = "final_content"
    if compliance_path.exists() and compliance_path.stat().st_size > 10:
        source_path = compliance_path
    elif opt_path.exists() and opt_path.stat().st_size > 10:
        source_path = opt_path
        content_col = "optimized_content"
    elif zhizao_path.exists() and zhizao_path.stat().st_size > 10:
        source_path = zhizao_path
        content_col = "content_draft"
    else:
        return {"success": False, "error": "请先执行合规审查 (Step 3.6) — 没有可审查的内容"}

    try:
        df = pd.read_csv(source_path, encoding="utf-8-sig", on_bad_lines="skip")
    except Exception:
        try:
            df = pd.read_csv(source_path, encoding="utf-8-sig", on_bad_lines="skip", engine="python")
        except Exception:
            return {"success": False, "error": "内容文件格式错误或为空"}
    if df.empty:
        return {"success": False, "error": "内容为空"}

    # Resolve content column
    if content_col not in df.columns:
        for alt in ["final_content", "optimized_content", "content_draft", "content", "body"]:
            if alt in df.columns:
                content_col = alt
                break

    if progress_callback:
        progress_callback(0.1, "正在执行 Pre-Legal Self-Check v2...")

    # === CONTEXT-AWARE WHITELIST PATTERNS ===
    # These patterns, when found near a match, indicate the match is a false positive
    DISCLAIMER_PATTERNS = [
        r'仅供参考', r'以实际.*为准', r'具体.*请.*咨询', r'数据来源',
        r'以上.*示例', r'实际.*因.*而异', r'请以.*官方.*为准',
        r'不构成.*建议', r'不代表.*立场', r'详见.*官网',
    ]

    OFFICIAL_FEE_PATTERNS = [
        # Common Amazon official fee references that should NOT trigger data-no-source
        r'39\.99\s*美元', r'月租费', r'专业销售计划', r'个人销售计划',
        r'佣金.*8.*15', r'销售佣金', r'FBA.*配送费', r'仓储费',
        r'sellercentral', r'seller\s*central', r'官方.*费率',
    ]

    PLATFORM_WHITELIST_CONTEXT = [
        # Contexts where "平台" is acceptable
        r'卖家平台', r'广告平台', r'物流平台', r'搜索平台', r'AI.*平台',
        r'第三方平台', r'不是.*平台', r'并非.*平台', r'作为.*平台',
        r'(?:ChatGPT|Perplexity|Gemini|DeepSeek|Kimi).*平台',
        r'平台.*(?:对比|比较|选择)',  # comparing platforms is educational context
    ]

    THIRD_PARTY_GENERIC_PATTERNS = [
        # Generic references to 3rd parties that are NOT endorsements
        r'第三方.*工具', r'第三方.*服务', r'如.*等', r'本文不推荐',
        r'具体.*工具', r'相关.*服务商',
    ]

    def _get_context(content: str, match_start: int, match_end: int, window: int = 80) -> str:
        """Get surrounding context around a regex match."""
        ctx_start = max(0, match_start - window)
        ctx_end = min(len(content), match_end + window)
        return content[ctx_start:ctx_end]

    def _has_disclaimer_nearby(content: str, match_start: int, paragraph_window: int = 300) -> bool:
        """Check if there's a disclaimer within the same paragraph or nearby."""
        ctx = content[max(0, match_start - 50):min(len(content), match_start + paragraph_window)]
        return any(re.search(p, ctx) for p in DISCLAIMER_PATTERNS)

    def _is_official_fee_context(content: str, match_start: int) -> bool:
        """Check if the matched data is in the context of official Amazon fees."""
        ctx = _get_context(content, match_start, match_start + 50, window=150)
        return any(re.search(p, ctx, re.IGNORECASE) for p in OFFICIAL_FEE_PATTERNS)

    def _is_platform_whitelisted(content: str, match_start: int, match_end: int) -> bool:
        """Check if 'platform' usage is in an acceptable context."""
        ctx = _get_context(content, match_start, match_end, window=30)
        return any(re.search(p, ctx) for p in PLATFORM_WHITELIST_CONTEXT)

    def _is_third_party_generic(content: str, match_start: int) -> bool:
        """Check if 3rd-party mention is generic (not endorsement)."""
        ctx = _get_context(content, match_start, match_start + 50, window=100)
        return any(re.search(p, ctx) for p in THIRD_PARTY_GENERIC_PATTERNS)

    def _has_qualifier(content: str, match_start: int) -> bool:
        """Check if an absolute/superlative term already has a qualifier (之一/可能/相对)."""
        ctx = _get_context(content, match_start, match_start + 20, window=20)
        return any(q in ctx for q in ['之一', '可能', '相对', '通常', '往往', '较为'])

    # === RULE-BASED CHECKS with CONTEXT VALIDATION (Layer 2-3-4) ===
    CHECKS = {
        # Layer 2: Legal Questionnaire
        "L2_external_data": {
            "name": "外部数据引用无出处",
            "patterns": [r'数据显示', r'据.*统计', r'研究表明', r'报告指出',
                         r'根据.*\d{4}年.*(?:报告|白皮书|数据|调查)',
                         r'根据.*(?:绩效报告|物流费用报告|合规报告|执法数据)',
                         r'据.*(?:机构|委员会|协会).*数据'],
            "level": "BLOCKED",
            "priority": "P0",
            "desc": "引用可能不存在的报告/数据（AI hallucination高风险）",
            "context_check": "disclaimer",  # Only trigger if no disclaimer nearby
            "min_criticality": 3,
        },
        "L2_fabricated_percentage": {
            "name": "无根据百分比声明",
            "patterns": [r'(?:避开|解决|降低|避免)\s*\d+%\s*(?:的|常见|风险|问题|坑)',
                         r'(?:提升|增长|提高|增加)\s*(?:了\s*)?\d+%(?!.*(?:来源|数据|参考|Seller Central))',
                         r'平均(?:占|为|达到?).*\d+%\s*(?:至|到|-)\s*\d+%'],
            "level": "WARNING",
            "priority": "P1",
            "desc": "使用了无法验证的百分比数据，需标注来源或改为定性描述",
            "context_check": "disclaimer_or_official",
            "min_criticality": 3,
        },
        "L2_percentage_no_source": {
            "name": "增长/降低数据缺来源",
            "patterns": [r'(?:同比|环比|年均).*(?:增长|下降|提升|降低)\s*\d+%'],
            "level": "WARNING",
            "priority": "P1",
            "desc": "引用具体增长/降低百分比但未标注数据来源",
            "context_check": "disclaimer_or_official",
            "min_criticality": 4,
        },
        "L2_internal_data": {
            "name": "内部Amazon数据",
            "patterns": [r'\bMAU\b', r'\bGMS\b', r'\bGMV\b', r'活跃用户.*\d', r'卖家数量.*\d'],
            "level": "BLOCKED",
            "priority": "P0",
            "desc": "包含可能为内部未公开数据的指标",
            "context_check": None,
            "min_criticality": 3,
        },
        "L2_personal_info": {
            "name": "个人信息收集",
            "patterns": [r'收集.*个人信息', r'填写.*(?:注册|报名).*表', r'留下.*(?:手机号|邮箱|联系方式)'],
            "level": "WARNING",
            "priority": "P1",
            "desc": "涉及个人信息收集，需确认已获得同意",
            "context_check": None,
            "min_criticality": 3,
        },
        # Layer 3A: General Guidelines
        "A2_internal_info": {
            "name": "内部信息泄露",
            "patterns": [r'汇报线', r'org\s*chart', r'组织架构', r'办公室地址', r'部门结构'],
            "level": "BLOCKED",
            "priority": "P0",
            "desc": "禁止对外透露内部组织信息",
            "context_check": None,
            "min_criticality": 3,
        },
        "A3_guarantee": {
            "name": "保证性陈述",
            "patterns": [r'一定能(?:赚|成功|做到)', r'必定(?:能|会)', r'保证.*(?:增长|盈利|赚)',
                         r'确保.*(?:销量|收入|成功)', r'100%.*(?:赚|成功|盈利)',
                         r'肯定能(?:赚|成功)'],
            "level": "BLOCKED",
            "priority": "P0",
            "desc": "禁止使用保证性陈述（应改为客观性陈述）",
            "context_check": None,
            "min_criticality": 3,
        },
        "A4_prohibited_absolute": {
            "name": "绝对化用语",
            "patterns": [r'(?:全球|全网|业内)最(?:大|好|强|快|优)',
                         r'第一品牌', r'No\.\s*1\b', r'唯一的选择',
                         r'没有比.*更好',
                         r'流量最(?:大|高|多)',
                         r'(?:打击|执行|监管)力度(?:全球|业内)?最(?:大|强)',
                         r'(?:增速|增长|发展)最(?:快|猛)'],
            "level": "WARNING",
            "priority": "P1",
            "desc": "绝对化用语需删除或改为'领先的/主要的/较大的'",
            "context_check": "qualifier",  # Exempt if already has qualifier
            "min_criticality": 3,
        },
        "A4_prohibited_ecosystem": {
            "name": "生态/生态系统敏感词",
            "patterns": [r'亚马逊.*生态', r'(?:电商|跨境).*生态系统', r'(?:电商|跨境).*生态圈'],
            "level": "WARNING",
            "priority": "P2",
            "desc": "应替换为'服务体系/产业服务集群'",
            "context_check": None,
            "min_criticality": 4,
        },
        "A4_prohibited_platform": {
            "name": "平台敏感词（品牌语境）",
            "patterns": [r'亚马逊平台', r'电商平台(?!.*对比|.*选择)'],
            "level": "WARNING",
            "priority": "P2",
            "desc": "正式描述中不应使用'亚马逊平台'，应使用'亚马逊'/'亚马逊站点'",
            "context_check": "platform_whitelist",
            "min_criticality": 5,  # Only check in Critical=5 content
        },
        "A6_service_provider": {
            "name": "服务商背书",
            "patterns": [r'官方认可', r'指定服务商', r'官方推荐', r'(?:强烈|特别)推荐.*(?:服务商|工具)'],
            "level": "BLOCKED",
            "priority": "P0",
            "desc": "禁止为服务商背书或给予官方名号",
            "context_check": "third_party_generic",  # Exempt if generic mention
            "min_criticality": 3,
        },
        "A6_specific_brand_recommend": {
            "name": "具体第三方品牌推荐",
            "patterns": [r'(?:推荐|建议).*(?:Jungle\s*Scout|Helium\s*10|Payoneer|连连|WorldFirst|PingPong)',
                         r'(?:使用|选择)(?:Jungle\s*Scout|Helium\s*10)'],
            "level": "WARNING",
            "priority": "P1",
            "desc": "提及具体第三方品牌名可能构成推荐，建议用泛称替代",
            "context_check": "third_party_generic",
            "min_criticality": 4,
        },
        "A6_brand_in_example": {
            "name": "举例中提及知名品牌",
            "patterns": [r'(?:如|例如|比如).*(?:Apple|Nike|Samsung|Adidas|Sony|Louis\s*Vuitton|Gucci)',
                         r'(?:Apple|Nike|Samsung|Adidas).*(?:品牌词|商标|侵权)',
                         r'避免.*(?:使用|包含).*(?:Apple|Nike|Samsung)'],
            "level": "WARNING",
            "priority": "P2",
            "desc": "举例中直接提及第三方品牌名，建议改为'某知名XX品牌'",
            "context_check": None,
            "min_criticality": 4,
        },
        # Layer 3C: PR Specific
        "C1_sensitive_region": {
            "name": "敏感地区表述",
            "patterns": [r'(?<!中国)台湾(?!.*中国台湾)', r'(?<!中国)(?<!中国特别行政区)香港(?!.*中国)',
                         r'(?<!中国)(?<!中国特别行政区)澳门(?!.*中国)'],
            "level": "BLOCKED",
            "priority": "P0",
            "desc": "台湾/香港/澳门前需加'中国'前缀",
            "context_check": None,
            "min_criticality": 3,
        },
        "C2_competitor_compare": {
            "name": "竞品对比",
            "patterns": [r'(?:对比|比较|优于|好于|强于).*(?:Shopee|Lazada|TikTok|速卖通|eBay)',
                         r'(?:Shopee|Lazada|TikTok|速卖通|eBay).*(?:不如|更好|劣势|差)'],
            "level": "BLOCKED",
            "priority": "P0",
            "desc": "禁止与友商进行直接比较",
            "context_check": None,
            "min_criticality": 3,
        },
        # Layer 3D: Tax Specific
        "D1_tax_terms": {
            "name": "税务禁用词",
            "patterns": [r'(?:我们|全球开店).*招商', r'seller\s*recruiting',
                         r'(?:税务|税收).*筹划', r'协议定价'],
            "level": "BLOCKED",
            "priority": "P0",
            "desc": "禁止使用'招商/税务筹划'等税务敏感词",
            "context_check": None,
            "min_criticality": 3,
        },
        "D2_registration_expr": {
            "name": "卖家注册引导不合规",
            "patterns": [r'(?:前往|访问|打开).*全球开店.*注册', r'扫码.*注册',
                         r'我们(?:将|会|来).*审核', r'我们的.*(?:审核|要求|标准)'],
            "level": "BLOCKED",
            "priority": "P0",
            "desc": "注册必须引导至'亚马逊卖家平台(Seller Central)'",
            "context_check": None,
            "min_criticality": 4,
        },
        "D4_tax_interpretation": {
            "name": "税务政策解读",
            "patterns": [r'根据.*(?:税务|税收).*文件.*(?:可以|能够|应当)享受',
                         r'(?:税务|税收).*(?:建议|方案|解决方案|规划)',
                         r'(?:帮助|协助).*(?:避税|节税|减税)'],
            "level": "BLOCKED",
            "priority": "P0",
            "desc": "禁止对税务政策做出解读，需加'请咨询专业税务顾问'",
            "context_check": None,
            "min_criticality": 3,
        },
        "D4_tax_statement_no_disclaimer": {
            "name": "税务信息缺免责声明",
            "patterns": [r'(?:销售税|增值税|VAT|GST|关税).*(?:需要|必须|应当|要求)'],
            "level": "WARNING",
            "priority": "P1",
            "desc": "税务相关描述需加免责声明'以上信息仅供参考，请咨询税务顾问'",
            "context_check": "disclaimer",
            "min_criticality": 4,
        },
        "D5_free_service": {
            "name": "免费服务/赠品",
            "patterns": [r'(?:亚马逊|我们).*免费(?:提供|赠送|发放)', r'免费礼物', r'免费赠品'],
            "level": "WARNING",
            "priority": "P1",
            "desc": "亚马逊中国实体提供免费服务/赠品需税务部批准",
            "context_check": None,
            "min_criticality": 4,
        },
        # Layer 3E: Data & Disclaimer
        "E2_fee_table_no_disclaimer": {
            "name": "费用表缺免责声明",
            "patterns": [r'(?:费率|费用|成本|价格).*(?:表|一览|汇总|明细)'],
            "level": "WARNING",
            "priority": "P2",
            "desc": "费用表/明细需添加'以上数据仅供参考，实际费用以官方为准'",
            "context_check": "disclaimer",
            "min_criticality": 4,
        },
    }

    # === Determine article criticality from category ===
    def _get_criticality(row) -> int:
        """Infer content criticality from keyword_id or category."""
        CRITICAL_5 = {19, 20, 21, 23, 24, 25}
        CRITICAL_4 = {4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 22, 26, 27, 29, 30, 32}
        CRITICAL_3 = {2, 3, 31, 33, 34, 35}
        try:
            kw_id = str(row.get("keyword_id", row.get("category_id", "")))
            cat_num = int(kw_id.split("_")[1]) if "_" in kw_id else int(kw_id) if kw_id.isdigit() else 0
        except (ValueError, IndexError):
            cat_num = 0
        if cat_num in CRITICAL_5:
            return 5
        elif cat_num in CRITICAL_4:
            return 4
        elif cat_num in CRITICAL_3:
            return 3
        return 4  # Default to standard

    # === Execute checks per article ===
    results = []
    total = len(df)

    for idx, row in df.iterrows():
        if progress_callback:
            progress_callback(0.1 + 0.7 * (idx / total), f"正在检查第 {idx+1}/{total} 篇...")

        content_id = str(row.get("content_id", f"C__{idx:05d}"))
        content = str(row.get(content_col, ""))
        title = str(row.get("optimized_title", row.get("title", row.get("final_content", ""))))[:100]
        criticality = _get_criticality(row)

        article_checks = []
        article_status = "PASS"
        seen_categories = set()  # For deduplication

        for check_id, check_def in CHECKS.items():
            # Skip checks below this article's criticality threshold
            if criticality < check_def.get("min_criticality", 3):
                continue

            triggered = False
            matched_text = ""
            match_start = 0

            for pattern in check_def["patterns"]:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    triggered = True
                    matched_text = match.group(0)
                    match_start = match.start()
                    break

            if not triggered:
                continue

            # === CONTEXT VALIDATION (v2 core improvement) ===
            context_type = check_def.get("context_check")

            if context_type == "disclaimer":
                # Exempt if disclaimer is nearby
                if _has_disclaimer_nearby(content, match_start):
                    continue

            elif context_type == "disclaimer_or_official":
                # Exempt if disclaimer nearby OR it's referencing official Amazon fees
                if _has_disclaimer_nearby(content, match_start) or _is_official_fee_context(content, match_start):
                    continue

            elif context_type == "platform_whitelist":
                # Exempt if platform usage is in acceptable context
                if _is_platform_whitelisted(content, match_start, match_start + len(matched_text)):
                    continue

            elif context_type == "third_party_generic":
                # Exempt if the 3rd-party mention is generic/educational
                if _is_third_party_generic(content, match_start):
                    continue

            elif context_type == "qualifier":
                # Exempt if already qualified with 之一/可能/相对
                if _has_qualifier(content, match_start):
                    continue

            # Deduplication: only keep one finding per check category prefix
            category_prefix = check_id.split("_")[0]  # e.g. "A4", "D1", "L2"
            if category_prefix in seen_categories:
                continue
            seen_categories.add(category_prefix)

            check_status = check_def["level"]
            article_checks.append({
                "check_id": check_id,
                "name": check_def["name"],
                "status": check_status,
                "priority": check_def.get("priority", "P2"),
                "findings": f"检测到: '{matched_text}' — {check_def['desc']}",
                "auto_fixable": check_status == "WARNING",
            })
            # Escalate article status
            if check_status == "BLOCKED":
                article_status = "BLOCKED"
            elif check_status == "WARNING" and article_status != "BLOCKED":
                article_status = "WARNING"

        # Sort findings by priority and limit to top 5
        priority_order = {"P0": 0, "P1": 1, "P2": 2}
        article_checks.sort(key=lambda x: priority_order.get(x.get("priority", "P2"), 9))
        article_checks = article_checks[:5]  # Max 5 findings per article

        # Re-evaluate article_status based on kept findings only
        if article_checks:
            if any(c["status"] == "BLOCKED" for c in article_checks):
                article_status = "BLOCKED"
            else:
                article_status = "WARNING"
        else:
            article_status = "PASS"

        # Determine review requirements (Layer 1)
        content_lower = content.lower()
        legal_required = any(kw in content_lower for kw in ["vp演讲", "director发言", "新服务发布", "新项目发布", "gdpr", "vat法规", "payment法规"])
        pr_required = False  # Would need channel info which we don't have per-article
        tax_required = True  # All new content

        results.append({
            "content_id": content_id,
            "title": title[:80],
            "overall_status": article_status,
            "criticality": criticality,
            "legal_review_required": legal_required,
            "pr_review_required": pr_required,
            "tax_review_required": tax_required,
            "checks_total": len(CHECKS),
            "checks_passed": len(CHECKS) - len(article_checks),
            "checks_warning": sum(1 for c in article_checks if c["status"] == "WARNING"),
            "checks_blocked": sum(1 for c in article_checks if c["status"] == "BLOCKED"),
            "findings": article_checks,
        })

    # === Save results ===
    if progress_callback:
        progress_callback(0.85, "正在保存自审结果...")

    output_dir = OUTPUT_PATH / batch_id / "03_zhiyou"
    ensure_dir(output_dir)

    # Save detailed JSON report
    report = {
        "batch_id": batch_id,
        "checked_at": timestamp(),
        "total_articles": total,
        "summary": {
            "pass": sum(1 for r in results if r["overall_status"] == "PASS"),
            "warning": sum(1 for r in results if r["overall_status"] == "WARNING"),
            "blocked": sum(1 for r in results if r["overall_status"] == "BLOCKED"),
        },
        "articles": results,
    }

    report_file = output_dir / "pre_legal_check_report.json"
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    # Save CSV summary for quick reference
    summary_rows = []
    for r in results:
        findings_str = "; ".join([f"[{c['status']}] {c['name']}: {c['findings']}" for c in r["findings"]]) if r["findings"] else "无问题"
        summary_rows.append({
            "content_id": r["content_id"],
            "title": r["title"],
            "overall_status": r["overall_status"],
            "pass": r["checks_passed"],
            "warning": r["checks_warning"],
            "blocked": r["checks_blocked"],
            "legal_required": r["legal_review_required"],
            "findings": findings_str,
        })

    df_summary = pd.DataFrame(summary_rows)
    summary_file = output_dir / "pre_legal_check_summary.csv"
    df_summary.to_csv(summary_file, index=False, encoding="utf-8-sig")

    if progress_callback:
        progress_callback(1.0, f"Pre-Legal Self-Check 完成 ✅ | PASS:{report['summary']['pass']} WARNING:{report['summary']['warning']} BLOCKED:{report['summary']['blocked']}")

    return {
        "success": True,
        "output_file": str(report_file),
        "summary_file": str(summary_file),
        "summary": report["summary"],
        "blocked_ids": [r["content_id"] for r in results if r["overall_status"] == "BLOCKED"],
    }


# ============================================================
# STEP 4: 智布
# ============================================================
def run_zhibu(batch_id: str, progress_callback=None) -> dict:
    """Execute Step 4: Convert to structured JSON (Lego-compatible format)."""
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

    import re

    def _extract_structure(content: str, title: str) -> dict:
        """Extract h1 and h2 headers from markdown content."""
        h2s = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
        if not h2s:
            # Try numbered sections as h2
            h2s = re.findall(r'^\*\*(\d+[\.\、].+?)\*\*', content, re.MULTILINE)
        return {"h1": title, "h2": h2s[:8]}  # max 8 h2s

    def _extract_faq(content: str) -> list:
        """Extract FAQ from markdown content into structured [{question, answer}] format."""
        faqs = []
        # Pattern 1: ### question / answer
        faq_section = re.search(r'(?:##\s*(?:常见问题|FAQ|Frequently Asked Questions).+?)(?=\n##\s|\Z)', content, re.DOTALL | re.IGNORECASE)
        if faq_section:
            faq_text = faq_section.group(0)
            # Find Q&A pairs
            qa_pairs = re.findall(r'(?:###|\*\*Q[:\d]*[.、]?\*\*|Q[:：]\s*)\s*(.+?)\n+(?:\*\*A[:\d]*[.、]?\*\*|A[:：]\s*)?(.+?)(?=\n(?:###|\*\*Q|Q[:：]|\Z))', faq_text, re.DOTALL)
            for q, a in qa_pairs:
                q = q.strip().rstrip('?？').strip() + '?'
                a = a.strip()
                if q and a and len(a) > 5:
                    faqs.append({"question": q, "answer": a[:300]})
        # Pattern 2: numbered questions
        if not faqs:
            qa_pairs = re.findall(r'\d+[.、]\s*\*{0,2}(.+?)\*{0,2}\s*[\n:：]+\s*(.+?)(?=\n\d+[.、]|\Z)', content, re.DOTALL)
            for q, a in qa_pairs[-5:]:  # Take last 5 (likely FAQ section at end)
                q = q.strip()
                a = a.strip()
                if '?' in q or '？' in q or '吗' in q or '什么' in q:
                    faqs.append({"question": q, "answer": a[:300]})
        return faqs[:5]  # max 5 FAQs

    def _extract_keywords(ai_query: str, content: str) -> list:
        """Extract SEO keywords from query and content."""
        keywords = [ai_query]
        # Add query variations
        words = ai_query.replace('？', '').replace('?', '').split()
        if len(words) > 3:
            keywords.append(' '.join(words[:4]))
        return keywords[:5]

    def _safe_score(val):
        """Safely convert a score value to number, handling NaN/None/strings."""
        try:
            if val is None:
                return 0
            f = float(val)
            import math
            if math.isnan(f):
                return 0
            return round(f, 1)
        except (ValueError, TypeError):
            return 0

    items = []
    for _, row in df_opt.iterrows():
        # Sanitize pandas NaN values at read time
        def _safe_str(val, default=""):
            s = str(val) if val is not None else default
            return default if s.lower() in ("nan", "none", "null") else s

        cid = _safe_str(row.get("content_id", ""))
        # Fix invalid content_id
        if not cid or not cid.startswith("C_") or len(cid) < 5:
            cid = f"C_{abs(hash(str(row.get('ai_query', '')) + str(row.get('title', '')))) % 100000:05d}"

        title = _safe_str(row.get("optimized_title", row.get("title", "")))
        content = _safe_str(row.get("optimized_content", row.get("content_draft", "")))
        ai_query = _safe_str(row.get("ai_query", ""))
        category = _safe_str(row.get("category", ""))

        # Extract scores from scorecard if available
        _score_row = {}
        if not df_score.empty and "content_id" in df_score.columns:
            _match = df_score[df_score["content_id"] == cid]
            if not _match.empty:
                _score_row = _match.iloc[0].to_dict()

        # Extract structure from content
        structure = _extract_structure(content, title)
        faqs = _extract_faq(content)
        keywords = _extract_keywords(ai_query, content)

        # Build item in full nested format (matches batch_003 structure)
        item = {
            "content_id": cid,
            "query_id": _safe_str(row.get("query_id", "")),
            "keyword_id": _safe_str(row.get("keyword_id", "")),
            "keyword": ai_query,
            "ai_query": ai_query,
            "meta": {
                "title": title,
                "description": _safe_str(row.get("meta_description", "")),
            },
            "body": content,
            "category": category,
            "faq": faqs if faqs else "",
            "cta": _safe_str(row.get("cta", "")),
            "geo_summary": _safe_str(row.get("geo_summary", "")),
            "ai_friendly": {
                "intent_match_score": _safe_str(_score_row.get("intent_match_score", _safe_str(row.get("intent_match_score", "")))),
                "ai_readability_score": _safe_str(_score_row.get("ai_readability_score", _safe_str(row.get("ai_readability_score", "")))),
                "authority_score": _safe_str(_score_row.get("authority_score", _safe_str(row.get("authority_score", "")))),
                "actionability_score": _safe_str(_score_row.get("actionability_score", _safe_str(row.get("actionability_score", "")))),
                "differentiation_score": _safe_str(_score_row.get("differentiation_score", _safe_str(row.get("differentiation_score", "")))),
                "overall_score": _safe_score(_score_row.get("overall_score", row.get("overall_score", 0))),
            },
            "compliance": {
                "status": _safe_str(row.get("compliance_status", _safe_str(row.get("compliance_result", "")))),
                "copyright": f"Copyright © {datetime.now().year} Amazon. All rights Reserved.",
            },
            "quality_metrics": {
                "word_count": len(content),
                "table_count": content.count("|---|"),
                "list_count": len(re.findall(r'^\s*[-*•]\s', content, re.MULTILINE)),
                "link_count": len(re.findall(r'https?://', content)),
            },
            "structure": structure,
            "keywords": keywords,
            "created_from": f"{batch_id}/{cid}",
            "created_at": timestamp(),
        }
        items.append(item)

    # Save each item as individual JSON file
    output_dir = OUTPUT_PATH / batch_id / "04_zhibu"
    ensure_dir(output_dir)

    for item in items:
        # Filename = query or title (sanitized)
        fname = (item.get("ai_query") or item.get("meta", {}).get("title", ""))[:60]
        fname = fname.replace("/", "").replace("\\", "").replace(":", "").replace("?", "？").replace("*", "").replace('"', "").replace("<", "").replace(">", "").replace("|", "").strip()
        if not fname:
            fname = f"article_{abs(hash(item.get('content_id', ''))) % 100000}"
        item_file = output_dir / f"{fname}.json"
        item_file.write_text(json.dumps(item, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    # Save combined file for the UI display
    output_json = {
        "batch_id": batch_id,
        "created_at": timestamp(),
        "total_items": len(items),
        "source_keywords": list(set(i["ai_query"] for i in items if i.get("ai_query"))),
        "items": items,
    }
    combined_file = output_dir / "zhibu_output.json"
    combined_file.write_text(json.dumps(output_json, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    # Generate LEGO Sell Design format for each article
    try:
        from lego_converter import convert_article_to_lego_page
        lego_dir = output_dir / "lego_sell_design"
        lego_dir.mkdir(parents=True, exist_ok=True)
        for item in items:
            lego_page = convert_article_to_lego_page(
                title=item.get("meta", {}).get("title", ""),
                content=item.get("body", ""),
                source_query=item.get("ai_query", ""),
                batch_id=batch_id
            )
            fname = (item.get("ai_query") or item.get("meta", {}).get("title", ""))[:60]
            fname = fname.replace("/", "").replace("\\", "").replace(":", "").replace("*", "").replace('"', "").replace("<", "").replace(">", "").replace("|", "").strip()
            if not fname:
                fname = f"article_{abs(hash(item.get('content_id', ''))) % 100000}"
            lego_file = lego_dir / f"{fname}.json"
            lego_file.write_text(json.dumps(lego_page, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    except Exception:
        pass

    if progress_callback:
        progress_callback(1.0, "智布完成 ✅")

    return {"success": True, "output_file": str(combined_file), "items_count": len(items)}


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
        ("送审前自审 (Step 3.7)", lambda cb: run_pre_legal_check(batch_id, cb)),
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
