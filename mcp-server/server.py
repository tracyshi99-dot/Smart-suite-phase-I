"""
SmartSuite MCP Server - Exposes all ZhiXi workflow steps as MCP tools.
Run with: uvx --from mcp mcp run server.py
"""
import json
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP

BASE_PATH = Path(__file__).parent.parent
STEERING_PATH = BASE_PATH / ".kiro" / "steering"
OUTPUT_PATH = BASE_PATH / "output"

mcp = FastMCP("SmartSuite")


def load_steering(filename: str) -> str:
    """Load a steering file."""
    try:
        return (STEERING_PATH / filename).read_text(encoding="utf-8")
    except Exception as e:
        return f"Error loading {filename}: {e}"


def extract_section(markdown: str, section_name: str) -> str:
    """Extract a section from steering markdown."""
    lines = markdown.split("\n")
    capturing = False
    result = []
    depth = 0

    for line in lines:
        if section_name in line:
            capturing = True
            depth = len(line) - len(line.lstrip("#"))
            result.append(line)
            continue
        if capturing:
            if line.startswith("#") and len(result) > 5:
                header_depth = len(line) - len(line.lstrip("#"))
                if header_depth <= depth:
                    break
            result.append(line)

    return "\n".join(result) if result else f'Section "{section_name}" not found.'


@mcp.tool()
def zhiku(batch_id: str, market: str = "ALL", keyword_limit: int = 10) -> str:
    """智库 (Step 1) - AI Query Generation. Generates AI-native search queries from SEO/SEM keywords."""
    steering = load_steering("smart-suite-phase1.md")
    instructions = extract_section(steering, "Step 1: 智库")
    return (
        f"## 智库 (Step 1) - Parameters:\n"
        f"- batch_id: {batch_id}\n- market: {market}\n- keyword_limit: {keyword_limit}\n\n"
        f"## Instructions:\n{instructions}\n\n"
        f"## Paths:\n"
        f"- Input: {BASE_PATH / 'input' / 'seo_sem_keywords.csv'}\n"
        f"- Output: {OUTPUT_PATH / batch_id / '01_zhiku' / 'zhiku_ai_queries.csv'}"
    )


@mcp.tool()
def zhizao(batch_id: str, content_limit: int = 5) -> str:
    """智造 (Step 2) - Content Generation. Generates draft content following SEO+GEO standards."""
    steering = load_steering("smart-suite-phase1.md")
    instructions = extract_section(steering, "Step 2: 智造")
    return (
        f"## 智造 (Step 2) - Parameters:\n"
        f"- batch_id: {batch_id}\n- content_limit: {content_limit}\n\n"
        f"## Instructions:\n{instructions}\n\n"
        f"## Paths:\n"
        f"- Input: {OUTPUT_PATH / batch_id / '01_zhiku' / 'zhiku_ai_queries.csv'} (is_selected=TRUE)\n"
        f"- Output: {OUTPUT_PATH / batch_id / '02_zhizao' / 'zhizao_draft_content.csv'}"
    )


@mcp.tool()
def zhiyou_score(batch_id: str) -> str:
    """智优评分 (Step 3) - AI Citation Likelihood Scoring. Evaluates content across 5 dimensions."""
    steering = load_steering("smart-suite-phase1.md")
    instructions = extract_section(steering, "Step 3: 智优评分")
    return (
        f"## 智优评分 (Step 3) - Parameters:\n- batch_id: {batch_id}\n\n"
        f"## Instructions:\n{instructions}\n\n"
        f"## Paths:\n"
        f"- Input: {OUTPUT_PATH / batch_id / '02_zhizao' / 'zhizao_draft_content.csv'}\n"
        f"- Output: {OUTPUT_PATH / batch_id / '03_zhiyou' / 'zhiyou_scorecard.csv'}"
    )


@mcp.tool()
def zhiyou_execute(batch_id: str) -> str:
    """智优执行 (Step 3.5) - Content Rewrite based on scorecard suggestions."""
    steering = load_steering("smart-suite-phase1.md")
    instructions = extract_section(steering, "Step 3.5: 智优执行")
    return (
        f"## 智优执行 (Step 3.5) - Parameters:\n- batch_id: {batch_id}\n\n"
        f"## Instructions:\n{instructions}\n\n"
        f"## Paths:\n"
        f"- Input: draft + scorecard from {OUTPUT_PATH / batch_id / '03_zhiyou'}\n"
        f"- Output: {OUTPUT_PATH / batch_id / '03_zhiyou' / 'zhiyou_optimized_content.csv'}"
    )


@mcp.tool()
def zhiyou_compliance(batch_id: str) -> str:
    """合规审查 (Step 3.6) - Legal Compliance Check with auto-fix."""
    steering = load_steering("smart-suite-phase1.md")
    instructions = extract_section(steering, "Step 3.6: 合规审查")
    return (
        f"## 合规审查 (Step 3.6) - Parameters:\n- batch_id: {batch_id}\n\n"
        f"## Instructions:\n{instructions}\n\n"
        f"## Paths:\n"
        f"- Input: {OUTPUT_PATH / batch_id / '03_zhiyou' / 'zhiyou_optimized_content.csv'}\n"
        f"- Output: {OUTPUT_PATH / batch_id / '03_zhiyou' / 'zhiyou_compliance_checked.csv'}"
    )


@mcp.tool()
def zhibu(batch_id: str) -> str:
    """智布 (Step 4) - JSON Formatting for publishing."""
    steering = load_steering("smart-suite-phase1.md")
    instructions = extract_section(steering, "Step 4: 智布")
    return (
        f"## 智布 (Step 4) - Parameters:\n- batch_id: {batch_id}\n\n"
        f"## Instructions:\n{instructions}\n\n"
        f"## Paths:\n"
        f"- Input: compliance-checked content\n"
        f"- Output: {OUTPUT_PATH / batch_id / '04_zhibu' / 'zhibu_output.json'}"
    )


@mcp.tool()
def zhixi(week: str, csv_path: str = "") -> str:
    """智析 (Step 6) - Performance Analysis Excel Report. Generates full ZhiXi report with Weekly/Monthly/Traffic/T2R%/SSR benchmark."""
    steering = load_steering("zhixi-report.md")
    script_path = OUTPUT_PATH / "metrics" / "gen_zhixi_v6.ps1"
    return (
        f"## 智析 (Step 6) - Parameters:\n- week: {week}\n- csv_path: {csv_path or 'latest'}\n\n"
        f"## Full Specification:\n{steering}\n\n"
        f"## Action Required:\n"
        f"1. Extract data from CSV\n"
        f"2. Update data arrays in: {script_path}\n"
        f"3. Run script to generate: {OUTPUT_PATH / 'metrics' / f'zhixi_report_{week}.xlsx'}"
    )


@mcp.tool()
def zhongshu(week: str) -> str:
    """智中枢 (Decision Engine) - Weekly Planning based on ZhiXi report and 7 decision rules."""
    steering = load_steering("smart-suite-phase1.md")
    instructions = extract_section(steering, "智中枢")
    return (
        f"## 智中枢 Decision Engine - Plan for {week}:\n\n"
        f"## Instructions:\n{instructions}\n\n"
        f"## Action Required:\n"
        f"1. Read latest zhixi report from: {OUTPUT_PATH / 'metrics'}\n"
        f"2. Apply 7 decision rules\n"
        f"3. Generate weekly action plan"
    )


@mcp.tool()
def batch_report(batch_id: str) -> str:
    """批次报告 (Step 5) - Batch Summary Report with statistics across all pipeline steps."""
    steering = load_steering("smart-suite-phase1.md")
    instructions = extract_section(steering, "Step 5: Batch Summary")
    return (
        f"## Batch Summary Report (Step 5) - Parameters:\n- batch_id: {batch_id}\n\n"
        f"## Instructions:\n{instructions}\n\n"
        f"## Paths:\n"
        f"- Read all outputs from: {OUTPUT_PATH / batch_id}\n"
        f"- Write to: {OUTPUT_PATH / 'Batch_Summary_Report' / f'{batch_id}_summary.csv'}"
    )


@mcp.tool()
def full_pipeline(batch_id: str, market: str = "ALL", keyword_limit: int = 10) -> str:
    """全流程执行 - Run Steps 1-5 sequentially. Returns execution order and paths."""
    return (
        f"## 全流程执行 - Full Pipeline:\n"
        f"- batch_id: {batch_id}\n- market: {market}\n- keyword_limit: {keyword_limit}\n\n"
        f"## Execution Order:\n"
        f"1. zhiku → {OUTPUT_PATH / batch_id / '01_zhiku'}\n"
        f"2. zhizao → {OUTPUT_PATH / batch_id / '02_zhizao'}\n"
        f"3. zhiyou_score → {OUTPUT_PATH / batch_id / '03_zhiyou' / 'scorecard'}\n"
        f"4. zhiyou_execute → {OUTPUT_PATH / batch_id / '03_zhiyou' / 'optimized'}\n"
        f"5. zhiyou_compliance → {OUTPUT_PATH / batch_id / '03_zhiyou' / 'compliance'}\n"
        f"6. zhibu → {OUTPUT_PATH / batch_id / '04_zhibu'}\n"
        f"7. batch_report → summary\n\n"
        f"Execute each step sequentially. Pause for review after each."
    )


@mcp.tool()
def get_steering(file: str) -> str:
    """获取规则 - Read a steering file to understand rules for any step."""
    return load_steering(file)


@mcp.tool()
def zhice(
    persona_name: str,
    persona_background: str,
    persona_goal: str,
    platforms: str = "chatgpt,perplexity,google_sge",
    language: str = "mixed",
    rounds: int = 5
) -> str:
    """智测 - AI Search Journey Simulation. 模拟真实用户在不同AI检索平台的多轮递进式搜索旅程。独立模块，与内容流水线并行。

    Args:
        persona_name: 模拟人物名称（如"深圳3C卖家张先生"）
        persona_background: 人物背景描述
        persona_goal: 人物的搜索目标/想解决的问题
        platforms: 要模拟的AI平台。快捷: all/ww/cn。或逗号分隔: chatgpt,gemini,perplexity,deepseek,doubao,kimi,yuanbao,qianwen
        language: 搜索语言偏好 zh-CN|en-US|mixed
        rounds: 模拟搜索轮次数（至少5轮）
    """
    steering = load_steering("zhice-simulation.md")
    # Expand shortcut platform names
    platform_map = {
        "all": "chatgpt,gemini,perplexity,deepseek,doubao,kimi,yuanbao,qianwen",
        "ww": "chatgpt,gemini,perplexity",
        "cn": "deepseek,doubao,kimi,yuanbao,qianwen",
    }
    resolved_platforms = platform_map.get(platforms.strip().lower(), platforms)
    platform_list = [p.strip() for p in resolved_platforms.split(",")]

    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    persona_id = persona_name.replace(" ", "_")[:20]

    output_dir = OUTPUT_PATH / "zhice"

    return (
        f"## 智测 - AI Search Journey Simulation\n\n"
        f"### 人物画像\n"
        f"- 名称: {persona_name}\n"
        f"- 背景: {persona_background}\n"
        f"- 目标: {persona_goal}\n"
        f"- 语言: {language}\n\n"
        f"### 模拟配置\n"
        f"- 平台: {', '.join(platform_list)}\n"
        f"- 轮次: {rounds}\n"
        f"- 时间戳: {timestamp}\n\n"
        f"### 执行指令\n{steering}\n\n"
        f"### 执行步骤\n"
        f"1. 根据人物画像，推导出 Round 1 的初始搜索问题\n"
        f"2. 为每个选定平台生成差异化的检索短语\n"
        f"3. 使用 web_search 实际执行搜索，记录结果和来源\n"
        f"4. 分析结果，推导出下一轮的深入问题（递进逻辑）\n"
        f"5. 重复 {rounds} 轮\n"
        f"6. 生成检测报告（覆盖率、竞争分析、优化建议）\n\n"
        f"### 输出路径\n"
        f"- 旅程数据: {output_dir / f'journey_{persona_id}_{timestamp}.json'}\n"
        f"- 检测报告: {output_dir / f'zhice_report_{persona_id}_{timestamp}.csv'}\n"
        f"- 汇总报告: {output_dir / f'zhice_summary_{timestamp}.md'}"
    )


@mcp.tool()
def zhice_platforms() -> str:
    """智测平台列表 - 列出所有支持的AI检索平台及其特点，分WW和CN两区。"""
    return (
        "## 支持的 AI 检索平台\n\n"
        "### WW（海外平台）\n"
        "| 代号 | 名称 | 特点 | 搜索风格 |\n"
        "|------|------|------|----------|\n"
        "| chatgpt | ChatGPT (OpenAI) | 对话式，上下文连续 | 口语化提问，多轮对话 |\n"
        "| gemini | Gemini (Google) | Google生态，搜索增强 | 自然语言+结构化 |\n"
        "| perplexity | Perplexity AI | 搜索增强，带来源 | 精确问题，期望引用 |\n\n"
        "### CN（国内平台）\n"
        "| 代号 | 名称 | 特点 | 搜索风格 |\n"
        "|------|------|------|----------|\n"
        "| deepseek | DeepSeek | 技术导向，reasoning强 | 技术性问题 |\n"
        "| doubao | 豆包 (字节跳动) | 中文场景，抖音生态 | 纯中文口语化 |\n"
        "| kimi | Kimi (月之暗面) | 长文本处理 | 中文深度问题 |\n"
        "| yuanbao | 元宝 (腾讯) | 微信生态 | 搜索+对话混合 |\n"
        "| qianwen | 通义千问 (阿里) | 电商场景强 | 阿里生态相关 |\n\n"
        "### 快捷选项\n"
        "- `all` = 全部8个平台\n"
        "- `ww` = chatgpt,gemini,perplexity\n"
        "- `cn` = deepseek,doubao,kimi,yuanbao,qianwen\n\n"
        "使用方式: platforms='ww' 或 platforms='chatgpt,deepseek,kimi'"
    )


if __name__ == "__main__":
    mcp.run()
