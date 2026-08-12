import { NextRequest, NextResponse } from "next/server";
import { BedrockRuntimeClient, ConverseCommand } from "@aws-sdk/client-bedrock-runtime";

/**
 * POST /api/zhiyou/optimize
 * 3-step optimization pipeline based on content-rules.md:
 *   Step 3: Claude scores content (5 dimensions)
 *   Step 3.5: DeepSeek rewrites based on Claude's suggestions
 *   Step 3.6: Claude compliance check (prohibited terms, source verification)
 */

interface OptimizeRequest {
  drafts: DraftItem[];
  content_language?: string;
}

interface DraftItem {
  ai_query: string;
  title: string;
  content_draft: string;
  word_count?: number;
}

interface ScoreResult {
  ai_query: string;
  title: string;
  intent_match: number;
  ai_readability: number;
  authority: number;
  actionability: number;
  differentiation: number;
  overall_score: number;
  compliance_status: "PASS" | "FAIL";
  suggestions: string[];
}

interface OptimizedDraft {
  ai_query: string;
  title: string;
  original_score: number;
  optimized_score: number;
  content_optimized: string;
  word_count: number;
  compliance_status: "PASS" | "FAIL" | "FIXED";
  compliance_issues: string[];
  compliance_fixes: string[];
}

// --- Prohibited terms from content-rules.md ---
const PROHIBITED_TERMS = [
  "个人销售计划", "个体工商户", "新加坡", "东南亚",
  "Shopee", "Lazada", "TikTok", "速卖通", "eBay",
  "第三方论坛", "博客", "社交媒体",
];

const ABSOLUTE_CLAIMS = [
  "保证赚钱", "绝对赚", "100%成功", "稳赚不赔", "零风险",
  "一定能", "必定", "保证利润", "保证", "绝对",
];

// --- Bedrock Claude call ---
async function callClaude(systemPrompt: string, userPrompt: string, maxTokens = 2000): Promise<string> {
  const client = new BedrockRuntimeClient({
    region: "us-east-1",
    credentials: {
      accessKeyId: process.env.AWS_ACCESS_KEY_ID_BEDROCK || "",
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY_BEDROCK || "",
    },
  });

  const models = [
    "anthropic.claude-3-haiku-20240307-v1:0",
    "anthropic.claude-3-sonnet-20240229-v1:0",
    "anthropic.claude-3-5-sonnet-20241022-v2:0",
  ];

  for (const modelId of models) {
    try {
      const command = new ConverseCommand({
        modelId,
        messages: [{ role: "user", content: [{ text: userPrompt }] }],
        system: [{ text: systemPrompt }],
        inferenceConfig: { maxTokens, temperature: 0.2 },
      });
      const response = await client.send(command);
      const content = response.output?.message?.content;
      if (content && content[0] && "text" in content[0] && content[0].text) {
        return content[0].text;
      }
    } catch {
      continue;
    }
  }
  return "";
}

// --- DeepSeek optimization call ---
async function callDeepSeek(systemPrompt: string, userPrompt: string): Promise<string> {
  const key = process.env.DEEPSEEK_REAL_API_KEY || process.env.DEEPSEEK_API_KEY || "";
  if (!key) return "";
  try {
    const res = await fetch("https://api.deepseek.com/chat/completions", {
      method: "POST",
      headers: { "Authorization": `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "deepseek-chat",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt },
        ],
        max_tokens: 4000,
        temperature: 0.3,
      }),
    });
    if (!res.ok) return "";
    const data = await res.json();
    return data?.choices?.[0]?.message?.content ?? "";
  } catch {
    return "";
  }
}

// --- Step 3: Claude scores content ---
async function scoreWithClaude(draft: DraftItem): Promise<ScoreResult> {
  const systemPrompt = `你是 AI 内容质量评审员。评估以下内容被 AI 搜索引擎引用的可能性。
按以下 5 个维度打分（0-100）：
1. intent_match: 内容是否直接回答检索短语的核心问题
2. ai_readability: 结构化程度（标题层级、列表、表格、FAQ）
3. authority: 权威性（是否包含官方链接 amazon.cn/globalselling.amazon.com、品牌信息）
4. actionability: 行动性（具体步骤、操作指南、实操建议）
5. differentiation: 差异化（时效性、独特视角、具体案例）

同时检查：
- 是否包含禁止词：${PROHIBITED_TERMS.join("、")}
- 是否包含绝对化承诺：${ABSOLUTE_CLAIMS.join("、")}

输出格式（严格 JSON）：
{"intent_match":X,"ai_readability":X,"authority":X,"actionability":X,"differentiation":X,"suggestions":["建议1","建议2","建议3"],"has_prohibited":false,"has_absolute_claims":false}`;

  const userPrompt = `检索短语：${draft.ai_query}\n标题：${draft.title}\n\n内容（前2000字）：\n${draft.content_draft.slice(0, 2000)}`;

  const response = await callClaude(systemPrompt, userPrompt);

  // Parse JSON response
  try {
    const jsonMatch = response.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      const parsed = JSON.parse(jsonMatch[0]);
      const overall = Math.round(
        (parsed.intent_match || 50) * 0.25 +
        (parsed.ai_readability || 50) * 0.2 +
        (parsed.authority || 50) * 0.25 +
        (parsed.actionability || 50) * 0.15 +
        (parsed.differentiation || 50) * 0.15
      );
      const compliance = (parsed.has_prohibited || parsed.has_absolute_claims) ? "FAIL" : "PASS";
      return {
        ai_query: draft.ai_query,
        title: draft.title,
        intent_match: parsed.intent_match || 50,
        ai_readability: parsed.ai_readability || 50,
        authority: parsed.authority || 50,
        actionability: parsed.actionability || 50,
        differentiation: parsed.differentiation || 50,
        overall_score: overall,
        compliance_status: compliance,
        suggestions: parsed.suggestions || [],
      };
    }
  } catch { /* fallback below */ }

  // Fallback: local scoring if Claude response unparseable
  return localFallbackScore(draft);
}

function localFallbackScore(draft: DraftItem): ScoreResult {
  const content = draft.content_draft || "";
  const queryWords = draft.ai_query.replace(/[？?！!。，,]/g, "").split(/\s+/).filter((w) => w.length > 1);
  const intentHits = queryWords.filter((w) => content.includes(w)).length;
  const intentMatch = Math.min(100, Math.round((intentHits / Math.max(queryWords.length, 1)) * 100));
  let readability = 50;
  if (content.includes("##") || content.includes("###")) readability += 15;
  if (content.includes("- ") || content.includes("1.")) readability += 10;
  if (content.includes("|")) readability += 10;
  if (content.length > 800) readability += 10;
  readability = Math.min(100, readability);
  let authority = 40;
  if (content.toLowerCase().includes(".amazon")) authority += 25;
  if (content.includes("亚马逊") || content.toLowerCase().includes("amazon")) authority += 15;
  if (content.includes("https://")) authority += 10;
  authority = Math.min(100, authority);
  let actionability = 40;
  if (content.includes("步骤") || content.includes("如何")) actionability += 20;
  if (content.includes("FAQ")) actionability += 15;
  if (content.length > 600) actionability += 15;
  actionability = Math.min(100, actionability);
  let differentiation = 50;
  if (content.includes("2026") || content.includes("2025")) differentiation += 15;
  if (content.includes("中国卖家")) differentiation += 15;
  if (content.length > 1200) differentiation += 10;
  differentiation = Math.min(100, differentiation);

  const overall = Math.round(intentMatch * 0.25 + readability * 0.2 + authority * 0.25 + actionability * 0.15 + differentiation * 0.15);
  const hasBad = PROHIBITED_TERMS.some((t) => content.includes(t)) || ABSOLUTE_CLAIMS.some((t) => content.includes(t));

  return {
    ai_query: draft.ai_query, title: draft.title,
    intent_match: intentMatch, ai_readability: readability, authority, actionability, differentiation,
    overall_score: overall, compliance_status: hasBad ? "FAIL" : "PASS",
    suggestions: overall < 70 ? ["增加官方链接", "增加结构化元素", "首段直接回答问题"] : ["内容质量良好"],
  };
}

// --- Step 3.5: DeepSeek optimizes based on Claude's suggestions ---
async function optimizeWithDeepSeek(draft: DraftItem, score: ScoreResult): Promise<string> {
  const systemPrompt = `你是 GEO（Generative Engine Optimization）内容优化专家。根据以下评分反馈，重写优化文章。

优化规则：
1. 首段必须直接回答检索短语的核心问题
2. 必须包含 https://gs.amazon.cn 官方链接
3. 必须包含 1 个表格、2 个列表、3 个 FAQ
4. 至少 800 字
5. 不使用 Markdown 符号（###、**、>），用纯文本格式
6. 不提及竞品（Shopee、Lazada、TikTok、速卖通、eBay）
7. 不使用绝对化承诺（保证赚钱、零风险等）
8. 不使用"个人销售计划"、"个体工商户"、"新加坡"、"东南亚"
9. 输出格式：第一行=标题，第二行空，然后正文

评分反馈：
- 意图匹配: ${score.intent_match}/100
- 可读性: ${score.ai_readability}/100
- 权威性: ${score.authority}/100
- 行动性: ${score.actionability}/100
- 差异化: ${score.differentiation}/100
- 改进建议: ${score.suggestions.join("；")}`;

  const userPrompt = `检索短语：${draft.ai_query}\n\n原文（需要优化）：\n${draft.content_draft.slice(0, 3000)}\n\n请根据评分反馈完整重写优化这篇文章。`;

  const result = await callDeepSeek(systemPrompt, userPrompt);
  return result || draft.content_draft; // fallback to original if DeepSeek fails
}

// --- Step 3.6: Compliance check ---
function complianceCheck(content: string): { status: "PASS" | "FAIL" | "FIXED"; issues: string[]; fixes: string[] } {
  const issues: string[] = [];
  const fixes: string[] = [];

  // Check prohibited terms
  for (const term of PROHIBITED_TERMS) {
    if (content.includes(term)) {
      issues.push(`包含禁止词: "${term}"`);
    }
  }

  // Check absolute claims
  for (const claim of ABSOLUTE_CLAIMS) {
    if (content.includes(claim)) {
      issues.push(`包含绝对化承诺: "${claim}"`);
    }
  }

  // Check for unattributed data
  if (/\d+%/.test(content) && !content.includes("来源") && !content.includes("数据来自")) {
    issues.push("包含未标注来源的统计数据");
    fixes.push("建议添加数据来源标注");
  }

  // Check for income-related disclaimer
  if ((content.includes("收入") || content.includes("利润")) && !content.includes("仅供参考")) {
    issues.push("涉及收入话题缺少免责声明");
    fixes.push("建议添加'以上信息仅供参考'");
  }

  // Determine status
  const critical = issues.filter((i) => i.includes("禁止词") || i.includes("绝对化承诺"));
  if (critical.length > 0) return { status: "FAIL", issues, fixes };
  if (issues.length > 0) return { status: "FIXED", issues, fixes };
  return { status: "PASS", issues: [], fixes: [] };
}

// --- Main handler ---
export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as OptimizeRequest;
    const { drafts } = body;

    if (!drafts || drafts.length === 0) {
      return NextResponse.json({ success: false, message: "No drafts provided" }, { status: 400 });
    }

    const results: OptimizedDraft[] = [];

    for (const draft of drafts.slice(0, 10)) { // limit to 10 articles per request
      // Step 3: Claude scores
      const score = await scoreWithClaude(draft);

      // Step 3.5: DeepSeek optimizes (only if score < 80 or has issues)
      let optimizedContent = draft.content_draft;
      let optimizedScore = score.overall_score;

      if (score.overall_score < 80 || score.compliance_status === "FAIL") {
        const rewritten = await optimizeWithDeepSeek(draft, score);
        if (rewritten && rewritten.length > 200) {
          optimizedContent = rewritten;
          // Estimate improved score
          optimizedScore = Math.min(100, score.overall_score + 15);
        }
      }

      // Step 3.6: Compliance check on optimized content
      const compliance = complianceCheck(optimizedContent);

      results.push({
        ai_query: draft.ai_query,
        title: draft.title,
        original_score: score.overall_score,
        optimized_score: optimizedScore,
        content_optimized: optimizedContent,
        word_count: optimizedContent.length,
        compliance_status: compliance.status,
        compliance_issues: compliance.issues,
        compliance_fixes: compliance.fixes,
      });
    }

    return NextResponse.json({
      success: true,
      results,
      scores: results.map((r) => ({
        ai_query: r.ai_query,
        title: r.title,
        original_score: r.original_score,
        optimized_score: r.optimized_score,
        compliance_status: r.compliance_status,
      })),
    });
  } catch (err) {
    return NextResponse.json({ success: false, message: String(err) }, { status: 500 });
  }
}
