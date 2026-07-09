"""
智测 Engine - AI Search Journey Simulation
Simulates user search journeys across multiple AI platforms.
Uses Claude to generate platform-specific queries and analyze search results.
"""
import json
import os
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable

try:
    from engine import call_claude, ensure_dir, OUTPUT_PATH
except ImportError:
    try:
        from ui.engine import call_claude, ensure_dir, OUTPUT_PATH
    except ImportError:
        # Inline fallback if engine can't be imported
        import boto3
        from botocore.config import Config

        OUTPUT_PATH = Path(__file__).parent.parent / "output"
        if not OUTPUT_PATH.exists():
            import tempfile
            OUTPUT_PATH = Path(tempfile.gettempdir()) / "smartsuite_output"
            OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

        def ensure_dir(path: Path):
            path.mkdir(parents=True, exist_ok=True)

        def call_claude(system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
            config = Config(read_timeout=300, connect_timeout=10, retries={"max_attempts": 2})
            session = boto3.Session(region_name="us-east-1")
            client = session.client("bedrock-runtime", config=config)
            response = client.converse(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                messages=[{"role": "user", "content": [{"text": user_prompt}]}],
                system=[{"text": system_prompt}],
                inferenceConfig={"maxTokens": max_tokens, "temperature": 0.3},
            )
            return response["output"]["message"]["content"][0]["text"]

ZHICE_OUTPUT = OUTPUT_PATH / "zhice"


PLATFORM_INFO = {
    "chatgpt": {"name": "ChatGPT", "region": "WW", "style": "中文口语化提问，对话式，多轮连续，偏综合回答"},
    "gemini": {"name": "Gemini", "region": "WW", "style": "中文自然语言，搜索增强，结构化问题"},
    "perplexity": {"name": "Perplexity", "region": "WW", "style": "中文精确问题，期望带来源引用，学术感"},
    "deepseek": {"name": "DeepSeek", "region": "CN", "style": "中文技术性问题，逻辑推理型"},
    "doubao": {"name": "豆包", "region": "CN", "style": "纯中文口语化，简短直接，日常用语"},
    "kimi": {"name": "Kimi", "region": "CN", "style": "中文深度问题，要求详细分析，长文本"},
    "yuanbao": {"name": "元宝", "region": "CN", "style": "中文搜索+对话混合，微信生态用语"},
    "qianwen": {"name": "千问", "region": "CN", "style": "中文问题，电商场景偏好，阿里生态"},
}


def generate_round_queries(
    persona: dict,
    platforms: list,
    round_num: int,
    previous_rounds: list = None,
    custom_direction: str = "",
) -> dict:
    """Generate platform-specific search queries for a given round.

    Returns dict: {platform: suggested_query}
    """
    platform_desc = "\n".join([
        f"- {p}: {PLATFORM_INFO[p]['name']} ({PLATFORM_INFO[p]['region']}) - 风格: {PLATFORM_INFO[p]['style']}"
        for p in platforms
    ])

    prev_context = ""
    if previous_rounds:
        for rd in previous_rounds[-2:]:  # Last 2 rounds for context
            prev_context += f"\nRound {rd['round_num']}:\n"
            for p, q in rd.get("queries", {}).items():
                prev_context += f"  {p}: {q}\n"
            if rd.get("key_findings"):
                prev_context += f"  关键发现: {rd['key_findings']}\n"

    direction_text = f"\n用户指定方向: {custom_direction}" if custom_direction else ""

    system_prompt = """你是一位精通用户搜索行为的专家。你的任务是模拟一个中国跨境电商卖家在不同AI检索平台上的搜索旅程。

关键规则：
1. 所有平台的检索短语统一使用中文
2. 检索短语必须简短自然，像正常人打字提问（一般10-25个字，最多不超过30字）
3. 不要写长句，不要写"请详细介绍...包括...以及..."这种罗列式问题
4. 模拟真实用户随手一问的感觉，口语化
5. 每个平台的问题可以不同，但都是基于上一轮获得的某个具体信息点深入追问
6. 递进逻辑：看到一个信息点 → 好奇/疑惑 → 追问一个短问题

好的示例：
- "FBA费用怎么算"
- "亚马逊注册需要什么资料"
- "新手选品怎么选比较安全"
- "北美站和欧洲站哪个好做"

坏的示例（太长太复杂）：
- "作为一个中国卖家，我想了解在亚马逊美国站注册卖家账户的完整流程"
- "请详细介绍FBA的费用结构，包括仓储费、配送费等各项费用的计算方式" """

    user_prompt = f"""人物: {persona.get('name', '')} - {persona.get('background', '')}
目标: {persona.get('goal', '')}

当前第 {round_num} 轮。
{f"上几轮记录:{prev_context}" if prev_context else "第一轮，从最基础的问题开始。"}
{direction_text}

为以下平台生成检索短语（每条10-25字，像随手打字提问）:
{platform_desc}

输出JSON（不要代码块）:
{{
  "round_mindset": "用户此刻想什么(10字内)",
  "queries": {{"平台代号": "简短问题"}},
  "next_round_hint": "下一步可能问什么(10字内)"
}}"""

    result = call_claude(system_prompt, user_prompt, max_tokens=1024)

    # Parse JSON
    text = result.strip()
    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:])
    if text.endswith("```"):
        text = "\n".join(text.split("\n")[:-1])

    try:
        data = json.loads(text)
        return data
    except json.JSONDecodeError:
        # Try to extract JSON from mixed text
        import re
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return data
            except json.JSONDecodeError:
                pass
        # Fallback
        return {
            "round_mindset": "AI 返回格式异常，请手动编辑检索短语",
            "round_trigger": "",
            "queries": {p: f"请为 {PLATFORM_INFO[p]['name']} 输入检索短语" for p in platforms},
            "next_round_hint": "",
            "_raw_response": text[:500],
        }


def _load_env():
    """Load .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

_load_env()


def _call_openai(query: str) -> dict:
    """Call OpenAI ChatGPT API with web search enabled for real-time results."""
    import requests
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        return {"full_answer": "OpenAI API Key 未配置", "key_points": [], "sources": []}

    # Try with web_search tool first (for real-time search results)
    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": query}],
                "tools": [{"type": "web_search"}],
                "max_tokens": 2048,
                "temperature": 0.7,
            },
            timeout=90,
        )
        if resp.status_code == 200:
            data = resp.json()
            answer = data["choices"][0]["message"]["content"]
            # Extract sources from annotations if available
            sources = []
            annotations = data["choices"][0]["message"].get("annotations", [])
            for ann in annotations:
                if ann.get("type") == "url_citation":
                    sources.append(ann.get("url", ""))
            return {"full_answer": answer, "key_points": [], "sources": sources, "_real": True, "_web_search": True}
    except Exception:
        pass

    # Fallback: without web_search
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": query}],
            "max_tokens": 1024,
            "temperature": 0.7,
        },
        timeout=60,
    )
    if resp.status_code == 200:
        answer = resp.json()["choices"][0]["message"]["content"]
        return {"full_answer": answer, "key_points": [], "sources": [], "_real": True, "_web_search": False}
    return {"full_answer": f"OpenAI API 错误: {resp.status_code} {resp.text[:200]}", "key_points": [], "sources": []}


def _call_gemini(query: str) -> dict:
    """Call Google Gemini API."""
    import requests
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        return {"full_answer": "Gemini API Key 未配置", "key_points": [], "sources": []}
    resp = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}",
        headers={"Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": query}]}]},
        timeout=60,
    )
    if resp.status_code == 200:
        data = resp.json()
        try:
            answer = data["candidates"][0]["content"]["parts"][0]["text"]
            return {"full_answer": answer, "key_points": [], "sources": [], "_real": True}
        except (KeyError, IndexError):
            return {"full_answer": f"Gemini 响应格式异常: {str(data)[:200]}", "key_points": [], "sources": []}
    return {"full_answer": f"Gemini API 错误: {resp.status_code} {resp.text[:200]}", "key_points": [], "sources": []}


def _call_deepseek(query: str) -> dict:
    """Call DeepSeek API (OpenAI-compatible)."""
    import requests
    key = os.environ.get("DEEPSEEK_API_KEY", "")
    # Also try .env file
    if not key:
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("DEEPSEEK_API_KEY="):
                    key = line.split("=", 1)[1].strip()
                    break
    if not key:
        return {"full_answer": "DeepSeek API Key 未配置", "key_points": [], "sources": []}
    resp = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": query}],
            "max_tokens": 1024,
            "temperature": 0.7,
        },
        timeout=60,
    )
    if resp.status_code == 200:
        answer = resp.json()["choices"][0]["message"]["content"]
        return {"full_answer": answer, "key_points": [], "sources": [], "_real": True}
    return {"full_answer": f"DeepSeek API 错误: {resp.status_code} {resp.text[:200]}", "key_points": [], "sources": []}


def _call_qianwen(query: str) -> dict:
    """Call Alibaba Qianwen (通义千问) via DashScope API."""
    import requests
    key = os.environ.get("DASHSCOPE_API_KEY", "")
    # Also try Streamlit secrets and .env file
    if not key:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "deepseek" in st.secrets:
                key = st.secrets["deepseek"]["api_key"]
        except Exception:
            pass
    if not key:
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("DASHSCOPE_API_KEY="):
                    key = line.split("=", 1)[1].strip()
                    break
    if not key:
        return {"full_answer": "千问 API Key 未配置", "key_points": [], "sources": []}
    resp = requests.post(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": "qwen-plus",
            "messages": [{"role": "user", "content": query}],
            "max_tokens": 1024,
            "temperature": 0.7,
        },
        timeout=60,
    )
    if resp.status_code == 200:
        answer = resp.json()["choices"][0]["message"]["content"]
        return {"full_answer": answer, "key_points": [], "sources": [], "_real": True}
    return {"full_answer": f"千问 API 错误: {resp.status_code} {resp.text[:200]}", "key_points": [], "sources": []}


def _call_kimi(query: str) -> dict:
    """Call Moonshot Kimi API (OpenAI-compatible)."""
    import requests
    key = os.environ.get("MOONSHOT_API_KEY", "")
    if not key:
        return {"full_answer": "Kimi API Key 未配置", "key_points": [], "sources": []}
    resp = requests.post(
        "https://api.moonshot.cn/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": "moonshot-v1-8k",
            "messages": [{"role": "user", "content": query}],
            "max_tokens": 1024,
            "temperature": 0.7,
        },
        timeout=60,
    )
    if resp.status_code == 200:
        answer = resp.json()["choices"][0]["message"]["content"]
        return {"full_answer": answer, "key_points": [], "sources": [], "_real": True}
    return {"full_answer": f"Kimi API 错误: {resp.status_code} {resp.text[:200]}", "key_points": [], "sources": []}


def _call_doubao(query: str) -> dict:
    """Call 豆包 (ByteDance Volcengine) API."""
    import requests
    key = os.environ.get("DOUBAO_API_KEY", "")
    if not key:
        return {"full_answer": "豆包 API Key 未配置", "key_points": [], "sources": []}
    resp = requests.post(
        "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": "doubao-1-5-pro-32k-250115",
            "messages": [{"role": "user", "content": query}],
            "max_tokens": 1024,
            "temperature": 0.7,
        },
        timeout=60,
    )
    if resp.status_code == 200:
        answer = resp.json()["choices"][0]["message"]["content"]
        return {"full_answer": answer, "key_points": [], "sources": [], "_real": True}
    return {"full_answer": f"豆包 API 错误: {resp.status_code} {resp.text[:200]}", "key_points": [], "sources": []}


# Map platform codes to their real API call functions
REAL_API_MAP = {
    "chatgpt": _call_openai,
    "gemini": _call_gemini,
    "deepseek": _call_deepseek,
    "qianwen": _call_qianwen,
    "kimi": _call_kimi,
    "doubao": _call_doubao,
}


def simulate_search_results(
    queries: dict,
    persona: dict,
    round_num: int,
    progress_callback: Optional[Callable] = None,
) -> dict:
    """Call real APIs for supported platforms, simulate the rest with Claude."""
    import os
    all_results = {}
    platforms_list = list(queries.keys())
    total = len(platforms_list)

    real_platforms = []
    simulated_platforms = []
    for p in platforms_list:
        if p in REAL_API_MAP:
            real_platforms.append(p)
        else:
            simulated_platforms.append(p)

    # --- Call real APIs ---
    for idx, p in enumerate(real_platforms):
        if progress_callback:
            pct = (idx + 1) / (total + 1)
            progress_callback(pct, f"🔴 真实API调用: {PLATFORM_INFO.get(p, {}).get('name', p)}...")
        try:
            result = REAL_API_MAP[p](queries[p])
            all_results[p] = result
        except Exception as e:
            all_results[p] = {"full_answer": f"调用失败: {e}", "key_points": [], "sources": []}

    # --- Simulate remaining platforms with Claude (batch of 2) ---
    if simulated_platforms:
        batch_size = 2
        for batch_idx in range(0, len(simulated_platforms), batch_size):
            batch = simulated_platforms[batch_idx:batch_idx + batch_size]
            if progress_callback:
                pct = (len(real_platforms) + batch_idx + 1) / (total + 1)
                names = ", ".join([PLATFORM_INFO.get(p, {}).get("name", p) for p in batch])
                progress_callback(pct, f"🟡 模拟: {names}...")

            platform_lines = "\n".join([
                f"- {PLATFORM_INFO.get(p, {}).get('name', p)}(代号{p}): \"{queries[p]}\""
                for p in batch
            ])

            system_prompt = "你是AI搜索引擎模拟专家。直接输出纯JSON，不要代码块，不要解释文字。"
            user_prompt = f"""模拟以下AI平台对问题的完整回答:
{platform_lines}

输出JSON(用平台代号小写作key):
{{
  "{batch[0]}": {{
    "full_answer": "完整回答(150-250字)",
    "key_points": ["要点1","要点2","要点3"],
    "sources": [{{"title":"标题","domain":"域名","url":"https://链接","is_our_content":false}}]
  }}{(',' + chr(10) + '  "' + batch[1] + '": {{同上格式}}') if len(batch) > 1 else ''}
}}"""

            try:
                result_text = call_claude(system_prompt, user_prompt, max_tokens=4096)
                text = result_text.strip()
                if text.startswith("```"):
                    text = "\n".join(text.split("\n")[1:])
                if text.endswith("```"):
                    text = "\n".join(text.split("\n")[:-1])

                import re
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    m = re.search(r'\{[\s\S]*\}', text)
                    data = json.loads(m.group()) if m else {}

                for k, v in data.items():
                    key_lower = k.lower()
                    for p in batch:
                        if p == key_lower or PLATFORM_INFO.get(p, {}).get("name", "").lower() == key_lower:
                            v["_simulated"] = True
                            all_results[p] = v
                            break
            except Exception as e:
                for p in batch:
                    all_results[p] = {"full_answer": f"模拟失败: {e}", "key_points": [], "sources": [], "_simulated": True}

    # Fill missing
    for p in platforms_list:
        if p not in all_results:
            all_results[p] = {"full_answer": "未获取到结果", "key_points": [], "sources": []}

    our_found = any(
        any(s.get("is_our_content") for s in r.get("sources", []))
        for r in all_results.values()
    )

    if progress_callback:
        progress_callback(1.0, "✅ 完成")

    return {
        "results": all_results,
        "key_findings": f"真实API: {len(real_platforms)}个, 模拟: {len(simulated_platforms)}个",
        "our_content_found": our_found,
        "coverage_note": "已发现我们内容" if our_found else "未发现我们内容",
    }


def generate_report(journey_data: dict) -> dict:
    """Generate a comprehensive analysis report from the complete journey data.

    Returns dict with report sections.
    """
    system_prompt = """你是一位 GEO（Generative Engine Optimization）策略分析专家。
基于用户的 AI 搜索旅程数据，生成一份全面的检测报告，包含覆盖率分析、竞争分析和优化建议。"""

    journey_summary = json.dumps(journey_data, ensure_ascii=False, indent=2)[:6000]

    user_prompt = f"""请基于以下搜索旅程数据生成检测报告。

{journey_summary}

请输出 JSON（不要代码块标记）:
{{
  "overview": {{
    "total_rounds": 数字,
    "total_queries": 数字,
    "platforms_tested": ["平台列表"],
    "our_content_found_rounds": 数字,
    "overall_coverage_rate": "百分比"
  }},
  "coverage_analysis": {{
    "by_platform": {{"平台": "覆盖情况描述"}},
    "uncovered_nodes": ["未覆盖的关键节点"],
    "strong_nodes": ["覆盖良好的节点"]
  }},
  "competitor_analysis": {{
    "frequent_sources": [{{"domain": "域名", "frequency": 数字, "content_type": "内容类型"}}],
    "competitor_strengths": ["竞品优势"]
  }},
  "recommendations": {{
    "new_keywords": ["建议新增的检索短语"],
    "content_gaps": ["内容缺口"],
    "optimization_priorities": ["优化优先级"]
  }},
  "summary": "3-5句话总结"
}}"""

    result = call_claude(system_prompt, user_prompt, max_tokens=2048)

    text = result.strip()
    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:])
    if text.endswith("```"):
        text = "\n".join(text.split("\n")[:-1])

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"summary": "报告生成失败", "raw": result}


def save_journey(journey_data: dict, persona_name: str) -> Path:
    """Save journey data to output/zhice/ directory."""
    ensure_dir(ZHICE_OUTPUT)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = persona_name.replace(" ", "_")[:20]
    filepath = ZHICE_OUTPUT / f"zhice_journey_{safe_name}_{timestamp}.json"
    filepath.write_text(json.dumps(journey_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return filepath


def save_report(report_data: dict, persona_name: str) -> Path:
    """Save report to output/zhice/ directory."""
    ensure_dir(ZHICE_OUTPUT)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = persona_name.replace(" ", "_")[:20]
    filepath = ZHICE_OUTPUT / f"zhice_report_{safe_name}_{timestamp}.json"
    filepath.write_text(json.dumps(report_data, ensure_ascii=False, indent=2), encoding="utf-8")
    return filepath


def generate_excel_report(journey_data: dict, persona_name: str) -> Path:
    """Generate Excel report with one sheet per query.

    Each sheet contains:
    - Query (the search phrase)
    - Platform responses (key points per platform)
    - Source links per platform

    Returns path to the generated .xlsx file.
    """
    from io import BytesIO

    ensure_dir(ZHICE_OUTPUT)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = persona_name.replace(" ", "_")[:20]
    filepath = ZHICE_OUTPUT / f"zhice_report_{safe_name}_{timestamp}.xlsx"

    # Collect all unique queries across rounds
    # Structure: sheet per round, rows per platform
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:

        # --- Overview Sheet ---
        overview_rows = []
        overview_rows.append({
            "项目": "人物名称",
            "内容": journey_data.get("persona", {}).get("name", "")
        })
        overview_rows.append({
            "项目": "人物背景",
            "内容": journey_data.get("persona", {}).get("background", "")
        })
        overview_rows.append({
            "项目": "搜索目标",
            "内容": journey_data.get("persona", {}).get("goal", "")
        })
        overview_rows.append({
            "项目": "测试平台",
            "内容": ", ".join(journey_data.get("platforms", []))
        })
        overview_rows.append({
            "项目": "总轮次",
            "内容": str(len(journey_data.get("rounds", [])))
        })
        overview_rows.append({
            "项目": "生成时间",
            "内容": journey_data.get("generated_at", "")
        })

        df_overview = pd.DataFrame(overview_rows)
        df_overview.to_excel(writer, sheet_name="概览", index=False)

        # --- One sheet per round ---
        rounds = journey_data.get("rounds", [])
        for rd in rounds:
            round_num = rd.get("round_num", 0)
            queries = rd.get("queries", {})
            results = rd.get("results", {})
            sheet_name = f"Round{round_num}"[:31]  # Excel sheet name max 31 chars

            rows = []
            for platform, query in queries.items():
                platform_name = PLATFORM_INFO.get(platform, {}).get("name", platform)
                platform_result = results.get(platform, {})
                key_points = platform_result.get("key_points", [])
                sources = platform_result.get("sources", [])
                full_answer = platform_result.get("full_answer", "")

                # Main row with answer
                answer_text = full_answer if full_answer else ("\n".join(key_points) if key_points else "无结果")
                key_points_text = "\n".join([f"• {kp}" for kp in key_points]) if key_points else ""
                source_links = "\n".join([
                    f"{s.get('title', '')} | {s.get('domain', '')} | {s.get('url', '')} | {'✅我们' if s.get('is_our_content') else '竞品'} | {s.get('relevance', '')}"
                    for s in sources
                ]) if sources else "无来源"

                rows.append({
                    "平台": platform_name,
                    "检索短语": query,
                    "AI完整回答": answer_text,
                    "关键要点": key_points_text,
                    "信息来源": source_links,
                    "来源数量": len(sources),
                    "是否包含我们内容": "是" if any(s.get("is_our_content") for s in sources) else "否",
                })

            df_round = pd.DataFrame(rows)
            df_round.to_excel(writer, sheet_name=sheet_name, index=False)

        # --- Sources Summary Sheet ---
        all_sources = []
        for rd in rounds:
            results = rd.get("results", {})
            for platform, result in results.items():
                for src in result.get("sources", []):
                    all_sources.append({
                        "轮次": rd.get("round_num", 0),
                        "平台": PLATFORM_INFO.get(platform, {}).get("name", platform),
                        "来源标题": src.get("title", ""),
                        "域名": src.get("domain", ""),
                        "URL": src.get("url", ""),
                        "是否我们内容": "是" if src.get("is_our_content") else "否",
                    })

        if all_sources:
            df_sources = pd.DataFrame(all_sources)
            df_sources.to_excel(writer, sheet_name="来源汇总", index=False)

        # --- Coverage Sheet ---
        coverage_rows = []
        for rd in rounds:
            results = rd.get("results", {})
            our_found = False
            for platform, result in results.items():
                if any(s.get("is_our_content") for s in result.get("sources", [])):
                    our_found = True
                    break
            coverage_rows.append({
                "轮次": rd.get("round_num", 0),
                "关键发现": rd.get("key_findings", ""),
                "我们内容覆盖": "✅" if our_found else "❌",
                "覆盖情况": rd.get("coverage_note", ""),
            })

        df_coverage = pd.DataFrame(coverage_rows)
        df_coverage.to_excel(writer, sheet_name="覆盖率", index=False)

    return filepath


def analyze_cited_content(journey_data: dict) -> dict:
    """Analyze content that was cited by AI engines across the journey.

    Extracts:
    - Structural patterns of cited content
    - Why these sources got cited (authority signals, format, etc.)
    - Actionable lessons for 智造/智优 to produce similar content

    Returns a learning report dict that can be fed to zhizao/zhiyou.
    """
    # Collect all cited sources
    all_sources = []
    for rd in journey_data.get("rounds", []):
        for platform, result in rd.get("results", {}).items():
            for src in result.get("sources", []):
                all_sources.append({
                    "round": rd.get("round_num"),
                    "platform": platform,
                    "title": src.get("title", ""),
                    "domain": src.get("domain", ""),
                    "url": src.get("url", ""),
                    "is_our_content": src.get("is_our_content", False),
                })

    if not all_sources:
        return {"success": False, "error": "没有找到被引用的内容"}

    sources_text = json.dumps(all_sources, ensure_ascii=False, indent=2)[:4000]

    system_prompt = """你是一位 GEO（Generative Engine Optimization）内容策略专家。

你的任务是：分析 AI 搜索引擎引用的竞品内容，提取它们被引用的结构特征和成功模式，
然后输出一份"学习报告"，供内容生产团队（智造/智优）参考，帮助他们产出更容易被 AI 引擎抓取和引用的内容。

重点分析维度：
1. 内容结构（标题格式、段落长度、H2/H3使用、列表/表格密度）
2. 权威信号（数据引用、专家身份、时间新鲜度、品牌背书）
3. 信息密度（每段是否有明确结论、是否有直接回答用户问题的"摘要段"）
4. 可引用性（是否有独立可摘取的facts/数据/结论，方便AI引擎引用）
5. SEO+GEO 双优化特征（关键词密度、FAQ结构、Schema标记线索）"""

    user_prompt = f"""以下是在多轮AI搜索旅程中被各平台引用的内容来源：

{sources_text}

用户画像：{json.dumps(journey_data.get('persona', {}), ensure_ascii=False)}

请分析这些被引用内容的成功模式，输出 JSON（不要代码块标记）：
{{
  "cited_content_patterns": {{
    "structural_patterns": [
      "被引用内容的结构特征1",
      "被引用内容的结构特征2"
    ],
    "authority_signals": [
      "权威信号1",
      "权威信号2"
    ],
    "citability_factors": [
      "可引用性因素1",
      "可引用性因素2"
    ]
  }},
  "competitor_strengths": [
    {{"domain": "竞品域名", "strength": "优势描述", "lesson": "我们可以学什么"}}
  ],
  "recommendations_for_zhizao": {{
    "title_format": "标题应该怎么写",
    "content_structure": "内容结构建议",
    "opening_paragraph": "首段怎么写才容易被引用",
    "data_usage": "数据和事实怎么呈现",
    "faq_strategy": "FAQ怎么设计",
    "summary_block": "摘要段怎么写"
  }},
  "recommendations_for_zhiyou": {{
    "scoring_adjustments": "评分标准应该调整什么",
    "rewrite_focus": "优化重写时重点关注什么",
    "geo_signals_to_add": "需要增加的GEO信号"
  }},
  "sample_structure": "一篇理想文章的结构模板（用Markdown展示）",
  "summary": "3句话总结核心学习"
}}"""

    result = call_claude(system_prompt, user_prompt, max_tokens=2048)

    text = result.strip()
    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:])
    if text.endswith("```"):
        text = "\n".join(text.split("\n")[:-1])

    try:
        report = json.loads(text)
    except json.JSONDecodeError:
        import re
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                report = json.loads(json_match.group())
            except json.JSONDecodeError:
                report = {"summary": "分析失败", "raw": text[:1000]}
        else:
            report = {"summary": "分析失败", "raw": text[:1000]}

    # Save the learning report
    ensure_dir(ZHICE_OUTPUT)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = journey_data.get("persona", {}).get("name", "unknown").replace(" ", "_")[:20]
    report_path = ZHICE_OUTPUT / f"zhice_learning_{safe_name}_{timestamp}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    report["_saved_path"] = str(report_path)
    report["success"] = True
    return report


def run_zhice_journey(persona_name: str, persona_goal: str, platforms: list, rounds: int = 5) -> dict:
    """Run a complete zhice journey simulation from the UI.
    
    Args:
        persona_name: User persona name
        persona_goal: What the user wants to achieve
        platforms: List of platform codes (e.g. ['qianwen', 'chatgpt'])
        rounds: Number of search rounds to simulate
    
    Returns:
        dict with 'success', 'summary', 'results', etc.
    """
    _load_env()
    
    results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate search queries based on the persona goal
    try:
        queries = generate_round_queries(
            persona_goal=persona_goal,
            platforms=platforms,
            round_num=1,
            previous_results=None,
        )
    except Exception:
        # Fallback: use the goal directly as a query
        queries = {p: persona_goal for p in platforms}
    
    # Run searches across platforms
    for round_num in range(1, rounds + 1):
        round_results = {"round_num": round_num, "queries": queries, "results": {}}
        
        for platform in platforms:
            query = queries.get(platform, persona_goal)
            api_func = REAL_API_MAP.get(platform)
            
            if api_func:
                try:
                    r = api_func(query)
                    answer = r.get("full_answer", "")
                    has_gs = "gs.amazon" in answer.lower() or "globalselling" in answer.lower()
                    has_brand = "全球开店" in answer or "Global Selling" in answer
                    
                    round_results["results"][platform] = {
                        "query": query,
                        "answer_length": len(answer),
                        "has_official_link": has_gs,
                        "has_brand_mention": has_brand,
                        "answer_preview": answer[:300],
                        "sources": r.get("sources", []),
                    }
                except Exception as e:
                    round_results["results"][platform] = {"error": str(e)}
            else:
                round_results["results"][platform] = {"error": f"No API for {platform}"}
        
        results.append(round_results)
        
        # Generate next round queries based on results (simplified)
        if round_num < rounds:
            queries = {p: f"{persona_goal} (follow-up {round_num+1})" for p in platforms}
    
    # Save results
    output = {
        "persona_name": persona_name,
        "persona_goal": persona_goal,
        "platforms": platforms,
        "rounds": rounds,
        "timestamp": timestamp,
        "results": results,
    }
    
    # Summary
    total_queries = sum(len(r["results"]) for r in results)
    with_link = sum(
        1 for r in results 
        for p_result in r["results"].values() 
        if p_result.get("has_official_link")
    )
    with_brand = sum(
        1 for r in results 
        for p_result in r["results"].values() 
        if p_result.get("has_brand_mention")
    )
    
    output["summary"] = {
        "total_queries": total_queries,
        "with_official_link": with_link,
        "with_brand_mention": with_brand,
        "coverage_rate": f"{with_link*100//total_queries if total_queries else 0}%",
        "platforms_tested": platforms,
    }
    
    # Save to file
    ZHICE_OUTPUT.mkdir(parents=True, exist_ok=True)
    safe_name = persona_name.replace(" ", "_")[:20]
    out_file = ZHICE_OUTPUT / f"journey_{safe_name}_{timestamp}.json"
    out_file.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    
    output["success"] = True
    output["_saved_path"] = str(out_file)
    return output
