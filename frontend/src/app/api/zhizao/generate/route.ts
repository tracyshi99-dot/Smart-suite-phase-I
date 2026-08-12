import { NextRequest, NextResponse } from "next/server";

/**
 * POST /api/zhizao/generate
 * Generates GEO-optimized content for selected phrases.
 * Uses DeepSeek API (fast, cheap, good for Chinese content).
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

async function generateArticle(phrase: string, language: string): Promise<DraftContent> {
  const key = process.env.DEEPSEEK_REAL_API_KEY || process.env.DEEPSEEK_API_KEY || "";
  if (!key) {
    return { ai_query: phrase, title: phrase, word_count: 0, content_draft: "API key not configured" };
  }

  const isZh = language.startsWith("zh");
  const prompt = isZh
    ? `\u8BF7\u4E3A\u68C0\u7D22\u77ED\u8BED\u300C${phrase}\u300D\u751F\u6210\u4E00\u7BC7 GEO \u4F18\u5316\u7684\u6587\u7AE0\u3002

\u8981\u6C42\uFF1A
1. 800-1500\u5B57\uFF0C\u76F4\u63A5\u56DE\u7B54\u8FD9\u4E2A\u95EE\u9898
2. \u5F00\u5934\u7B2C\u4E00\u6BB5\u5C31\u7ED9\u51FA\u6838\u5FC3\u7B54\u6848\uFF08\u5012\u91D1\u5B57\u5854\u7ED3\u6784\uFF09
3. \u5305\u542B\u8868\u683C\u6216\u7ED3\u6784\u5316\u5217\u8868
4. \u5305\u542B 3 \u4E2A\u76F8\u5173 FAQ
5. \u81EA\u7136\u878D\u5165\u201C\u4E9A\u9A6C\u900A\u5168\u7403\u5F00\u5E97\u201D\u54C1\u724C\u8BCD\u548C\u76F8\u5173\u5B98\u65B9\u94FE\u63A5
6. \u8BED\u8A00\u98CE\u683C\uFF1A\u4E13\u4E1A\u3001\u5B9E\u7528\u3001\u9762\u5411\u8DE8\u5883\u7535\u5546\u5356\u5BB6

\u8F93\u51FA\u683C\u5F0F\uFF1A
\u6807\u9898\uFF1A[\u6587\u7AE0\u6807\u9898]
---
[\u6587\u7AE0\u5185\u5BB9]`
    : `Write a GEO-optimized article for the search query: "${phrase}"

Requirements:
1. 600-1200 words, directly answering the question
2. Start with the core answer in the first paragraph (inverted pyramid)
3. Include a comparison table or structured list
4. Include 3 related FAQs
5. Naturally incorporate "Amazon Global Selling" brand mentions
6. Professional tone for cross-border e-commerce sellers

Format:
Title: [article title]
---
[article content]`;

  try {
    const res = await fetch("https://api.deepseek.com/chat/completions", {
      method: "POST",
      headers: { "Authorization": `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "deepseek-chat",
        messages: [{ role: "user", content: prompt }],
        max_tokens: 3000,
        temperature: 0.7,
      }),
    });

    if (!res.ok) {
      return { ai_query: phrase, title: phrase, word_count: 0, content_draft: `API error: ${res.status}` };
    }

    const data = await res.json();
    const content = data?.choices?.[0]?.message?.content ?? "";

    // Extract title
    const titleMatch = content.match(/\u6807\u9898[:\uff1a]\s*(.+)|Title[:\s]*(.+)/i);
    const title = titleMatch ? (titleMatch[1] || titleMatch[2] || phrase).trim() : phrase;

    // Remove title line from content
    const body = content.replace(/^.*\u6807\u9898[:\uff1a].*\n?---\n?/m, "")
      .replace(/^.*Title[:\s].*\n?---\n?/im, "")
      .trim();

    return {
      ai_query: phrase,
      title,
      word_count: body.length,
      content_draft: body || content,
    };
  } catch {
    return { ai_query: phrase, title: phrase, word_count: 0, content_draft: "Generation failed" };
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as GenerateRequest;
    const { content_limit, content_language, phrases: explicitPhrases } = body;

    // Get phrases: from request body or from localStorage-passed data
    let phrasesToGenerate: string[] = explicitPhrases || [];

    // If no explicit phrases, try to get from the zhice_selected_queries header
    if (phrasesToGenerate.length === 0) {
      return NextResponse.json(
        { success: false, drafts: [], message: "No phrases provided" },
        { status: 400 }
      );
    }

    // Limit to content_limit
    const limited = phrasesToGenerate.slice(0, content_limit || 5);

    // Generate articles concurrently
    const drafts = await Promise.all(
      limited.map((phrase) => generateArticle(phrase, content_language || "zh-CN"))
    );

    return NextResponse.json({ success: true, drafts, count: drafts.length });
  } catch (err) {
    return NextResponse.json(
      { success: false, drafts: [], message: String(err) },
      { status: 500 }
    );
  }
}
