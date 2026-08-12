import { NextRequest, NextResponse } from "next/server";
import { BedrockRuntimeClient, ConverseCommand } from "@aws-sdk/client-bedrock-runtime";

/**
 * POST /api/zhizao/generate
 * 3-step content pipeline: Claude generate → Claude optimize → Qianwen polish
 * Runs on Vercel serverless (60s timeout on Hobby, 300s on Pro)
 */

interface GenerateRequest {
  batch_id: string;
  content_limit: number;
  content_language: string;
  template_id: string;
  phrases?: string[];
}

interface DraftContent {
  ai_query: string;
  title: string;
  word_count: number;
  content_draft: string;
}

// Bedrock Claude call
async function callClaude(systemPrompt: string, userPrompt: string, maxTokens = 3000): Promise<string> {
  const client = new BedrockRuntimeClient({
    region: "us-east-1",
    credentials: {
      accessKeyId: process.env.AWS_ACCESS_KEY_ID_BEDROCK || "",
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY_BEDROCK || "",
    },
  });

  // Try multiple model IDs (availability varies by account)
  const models = [
    "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "anthropic.claude-3-sonnet-20240229-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
  ];

  for (const modelId of models) {
    try {
      const command = new ConverseCommand({
        modelId,
        messages: [{ role: "user", content: [{ text: userPrompt }] }],
        system: [{ text: systemPrompt }],
        inferenceConfig: { maxTokens, temperature: 0.3 },
      });

      const response = await client.send(command);
      const content = response.output?.message?.content;
      if (content && content[0] && "text" in content[0] && content[0].text) {
        return content[0].text;
      }
    } catch (err) {
      // Try next model
      const errMsg = String(err);
      if (errMsg.includes("AccessDeniedException") || errMsg.includes("not authorized")) {
        continue; // Model not enabled, try next
      }
      // For other errors, also try next model
      continue;
    }
  }

  // All models failed
  return "";
}

// Qianwen polish
async function callQianwen(prompt: string): Promise<string> {
  const key = process.env.DASHSCOPE_API_KEY || "";
  if (!key) return prompt; // Skip polish if no key
  try {
    const res = await fetch("https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions", {
      method: "POST",
      headers: { "Authorization": `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "qwen-plus",
        messages: [{ role: "user", content: prompt }],
        max_tokens: 3000,
        temperature: 0.3,
      }),
    });
    if (!res.ok) return prompt;
    const data = await res.json();
    return data?.choices?.[0]?.message?.content ?? prompt;
  } catch {
    return prompt;
  }
}

async function generateOneArticle(phrase: string, language: string): Promise<DraftContent> {
  const isZh = language.startsWith("zh");

  // Step 1: Claude generates draft
  const genSystem = isZh
    ? `\u4F60\u662F\u8DE8\u5883\u7535\u5546\u5185\u5BB9\u4E13\u5BB6\u3002\u8F93\u51FA\u89C4\u5219\uFF1A\u7B2C\u4E00\u884C=\u6807\u9898\uFF0C\u7B2C\u4E8C\u884C\u7A7A\uFF0C\u7136\u540E\u6B63\u6587\u3002\u81F3\u5C11800\u5B57\uFF0C\u542B1\u4E2A\u8868\u683C\u30012\u4E2A\u5217\u8868\u30013\u4E2AFAQ\u3002\u690D\u5165https://gs.amazon.cn\u3002\u4E0D\u63D0\u53CA\u7ADE\u54C1\u3002`
    : "You are a cross-border e-commerce content expert. Output: first line=title, then blank line, then body. Min 800 words, include 1 table, 2 lists, 3 FAQ. Include https://sell.amazon.com. No competitor mentions.";

  let draft = "";
  try {
    draft = await callClaude(genSystem, isZh ? `\u8BF7\u4E3A\u68C0\u7D22\u77ED\u8BED\u300C${phrase}\u300D\u5199\u4E00\u7BC7GEO\u4F18\u5316\u6587\u7AE0\u3002\u9996\u6BB5\u76F4\u63A5\u56DE\u7B54\u95EE\u9898\u3002` : `Write a GEO-optimized article for: "${phrase}". First paragraph directly answers the query.`);
  } catch {
    return { ai_query: phrase, title: phrase, word_count: 0, content_draft: "Claude generation failed" };
  }

  if (!draft || draft.length < 100) {
    return { ai_query: phrase, title: phrase, word_count: 0, content_draft: draft || "Empty response" };
  }

  // Step 2: Claude optimizes (check accuracy, add structure)
  let optimized = draft;
  try {
    const optPrompt = isZh
      ? `\u8BF7\u4F18\u5316\u4EE5\u4E0B\u6587\u7AE0\uFF0C\u786E\u4FDD\uFF1A1)\u4FE1\u606F100%\u51C6\u786E 2)\u8868\u683C\u5B8C\u6574 3)FAQ\u5B9E\u7528 4)\u65E0\u654F\u611F\u8BCD\u3002\u76F4\u63A5\u8F93\u51FA\u4F18\u5316\u540E\u5168\u6587\uFF1A\n\n${draft}`
      : `Optimize this article. Ensure: 1) 100% factual accuracy 2) Complete tables 3) Useful FAQ 4) No sensitive words. Output the full optimized text:\n\n${draft}`;
    optimized = await callClaude(genSystem, optPrompt);
  } catch {
    optimized = draft; // Use draft if optimization fails
  }

  // Step 3: Qianwen polish (language fluency)
  let polished = optimized;
  try {
    const polishPrompt = isZh
      ? `\u8BF7\u6DA6\u8272\u4EE5\u4E0B\u6587\u7AE0\uFF0C\u63D0\u5347\u4E2D\u6587\u8868\u8FBE\u6D41\u7545\u5EA6\uFF0C\u4FDD\u6301\u539F\u610F\u548C\u7ED3\u6784\u4E0D\u53D8\uFF0C\u4E0D\u8981\u6DFB\u52A0\u65B0\u5185\u5BB9\u3002\u76F4\u63A5\u8F93\u51FA\u5168\u6587\uFF1A\n\n${optimized}`
      : `Polish this article for natural fluency. Keep meaning and structure unchanged, don't add new content. Output full text:\n\n${optimized}`;
    polished = await callQianwen(polishPrompt);
  } catch {
    polished = optimized;
  }

  // Extract title from first line
  const lines = polished.split("\n");
  const title = lines[0]?.replace(/^#+\s*/, "").trim() || phrase;
  const body = lines.slice(1).join("\n").trim();

  return {
    ai_query: phrase,
    title,
    word_count: body.length,
    content_draft: body || polished,
  };
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as GenerateRequest;
    const { content_limit = 1, content_language = "zh-CN", phrases = [] } = body;

    if (!phrases || phrases.length === 0) {
      return NextResponse.json({ success: false, drafts: [], message: "No phrases provided" }, { status: 400 });
    }

    // Generate one article at a time (called per-phrase from frontend)
    const limited = phrases.slice(0, content_limit);
    const drafts: DraftContent[] = [];

    for (const phrase of limited) {
      const draft = await generateOneArticle(phrase, content_language);
      drafts.push(draft);
    }

    return NextResponse.json({ success: true, drafts, count: drafts.length });
  } catch (err) {
    return NextResponse.json({ success: false, drafts: [], message: String(err) }, { status: 500 });
  }
}
