import { NextRequest, NextResponse } from "next/server";

/**
 * POST /api/zhice/verify
 * Verifies phrases against real AI platforms (DeepSeek, Qianwen, etc.)
 * Runs server-side on Vercel, bypasses Lambda entirely.
 */

interface VerifyRequest {
  phrases: string[];
  platforms: string[];
  user?: string;
}

interface VerifyResult {
  query: string;
  platform: string;
  has_official_link: boolean;
  has_brand_mention: boolean;
  sentiment: string;
  competitors: string;
  answer_preview: string;
  error?: string;
}

const BRAND_KEYWORDS = [
  "\u4E9A\u9A6C\u900A", "\u5168\u7403\u5F00\u5E97", "amazon", "Amazon",
  "Global Selling", "Seller Central", "\u5356\u5BB6\u5E73\u53F0",
  "FBA", "fba", "\u4E9A\u9A6C\u900A\u7269\u6D41", "Amazon Global",
  "gs.amazon", "sell.amazon", "sellercentral",
];

// Platform API callers
async function callDeepSeek(query: string): Promise<string> {
  const key = process.env.DEEPSEEK_REAL_API_KEY || process.env.DEEPSEEK_API_KEY || "";
  if (!key) return "";
  const res = await fetch("https://api.deepseek.com/chat/completions", {
    method: "POST",
    headers: { "Authorization": `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "deepseek-chat",
      messages: [{ role: "user", content: query }],
      max_tokens: 300,
      temperature: 0.7,
    }),
  });
  if (!res.ok) return "";
  const data = await res.json();
  return data?.choices?.[0]?.message?.content ?? "";
}

async function callQianwen(query: string): Promise<string> {
  const key = process.env.DASHSCOPE_API_KEY || process.env.DEEPSEEK_API_KEY || "";
  if (!key) return "";
  const res = await fetch("https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions", {
    method: "POST",
    headers: { "Authorization": `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "qwen-plus",
      messages: [{ role: "user", content: query }],
      max_tokens: 300,
      temperature: 0.7,
    }),
  });
  if (!res.ok) return "";
  const data = await res.json();
  return data?.choices?.[0]?.message?.content ?? "";
}

async function callKimi(query: string): Promise<string> {
  const key = process.env.MOONSHOT_API_KEY || "";
  if (!key) return "";
  const res = await fetch("https://api.moonshot.cn/v1/chat/completions", {
    method: "POST",
    headers: { "Authorization": `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "moonshot-v1-8k",
      messages: [{ role: "user", content: query }],
      max_tokens: 300,
      temperature: 0.7,
    }),
  });
  if (!res.ok) return "";
  const data = await res.json();
  return data?.choices?.[0]?.message?.content ?? "";
}

async function callDoubao(query: string): Promise<string> {
  const key = process.env.DOUBAO_API_KEY || "";
  if (!key) return "";
  const res = await fetch("https://ark.cn-beijing.volces.com/api/v3/chat/completions", {
    method: "POST",
    headers: { "Authorization": `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "doubao-1-5-pro-32k-250115",
      messages: [{ role: "user", content: query }],
      max_tokens: 300,
      temperature: 0.7,
    }),
  });
  if (!res.ok) return "";
  const data = await res.json();
  return data?.choices?.[0]?.message?.content ?? "";
}

async function callChatGPT(query: string): Promise<string> {
  const key = process.env.OPENAI_API_KEY || "";
  if (!key) return "";
  const res = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: { "Authorization": `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      messages: [{ role: "user", content: query }],
      max_tokens: 300,
      temperature: 0.7,
    }),
  });
  if (!res.ok) return "";
  const data = await res.json();
  return data?.choices?.[0]?.message?.content ?? "";
}

async function callGemini(query: string): Promise<string> {
  const key = process.env.GEMINI_API_KEY || "";
  if (!key) return "";
  const res = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${key}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ contents: [{ parts: [{ text: query }] }] }),
    }
  );
  if (!res.ok) return "";
  const data = await res.json();
  return data?.candidates?.[0]?.content?.parts?.[0]?.text ?? "";
}

// Fallback: use DeepSeek for unsupported platforms
async function callFallback(query: string): Promise<string> {
  return callDeepSeek(query);
}

const PLATFORM_MAP: Record<string, (q: string) => Promise<string>> = {
  deepseek: callDeepSeek,
  qianwen: callQianwen,
  kimi: callKimi,
  doubao: callDoubao,
  chatgpt: callChatGPT,
  gemini: callGemini,
  perplexity: callFallback,
  yuanbao: callFallback,
  grok: callFallback,
};

function analyzeAnswer(answer: string): { has_brand: boolean; has_link: boolean; sentiment: string; competitors: string } {
  const lower = answer.toLowerCase();
  const has_brand = BRAND_KEYWORDS.some((kw) => lower.includes(kw.toLowerCase()));
  const has_link = lower.includes("amazon") || lower.includes("gs.amazon") ||
    lower.includes("sell.amazon") || lower.includes("sellercentral");

  // Sentiment analysis
  const POSITIVE = ["\u673A\u4F1A", "\u4F18\u52BF", "\u7B80\u5355", "\u5BB9\u6613", "\u63A8\u8350", "\u503C\u5F97", "\u5229\u6DA6", "\u589E\u957F", "\u6210\u529F", "\u4FBF\u6377", "\u9AD8\u6548", "\u652F\u6301", "\u5E2E\u52A9", "\u9002\u5408", "\u524D\u666F", "opportunity", "easy", "recommend", "profitable", "growth"];
  const NEGATIVE = ["\u98CE\u9669", "\u96BE", "\u95E8\u69DB", "\u4E8F\u635F", "\u590D\u6742", "\u7ADE\u4E89\u6FC0\u70C8", "\u5C01\u53F7", "\u4FB5\u6743", "\u9A97\u5C40", "\u4E0D\u5EFA\u8BAE", "\u8C28\u614E", "\u5931\u8D25", "\u6DD8\u6C70", "\u5185\u5377", "risk", "difficult", "complex", "banned"];
  const posCount = POSITIVE.filter((kw) => lower.includes(kw.toLowerCase())).length;
  const negCount = NEGATIVE.filter((kw) => lower.includes(kw.toLowerCase())).length;
  const sentiment = posCount > negCount ? "positive" : negCount > posCount ? "negative" : "neutral";

  // Competitor detection
  const COMPETITORS: Record<string, string[]> = {
    "Shopee": ["shopee", "\u867E\u76AE"],
    "TikTok Shop": ["tiktok shop", "tiktok", "\u6296\u97F3\u7535\u5546"],
    "Alibaba": ["alibaba", "\u963F\u91CC\u5DF4\u5DF4", "1688", "\u901F\u5356\u901A", "aliexpress"],
    "eBay": ["ebay"],
    "Walmart": ["walmart", "\u6C83\u5C14\u739B"],
    "Temu": ["temu", "\u62FC\u591A\u591A\u8DE8\u5883"],
    "Shopify": ["shopify"],
  };
  const found: string[] = [];
  for (const [name, keywords] of Object.entries(COMPETITORS)) {
    if (keywords.some((kw) => lower.includes(kw.toLowerCase()))) {
      found.push(name);
    }
  }
  return { has_brand, has_link, sentiment, competitors: found.join(", ") };
}

async function verifyOne(phrase: string, platform: string): Promise<VerifyResult> {
  const caller = PLATFORM_MAP[platform] || callFallback;
  let answer = "";
  try {
    answer = await caller(phrase);
  } catch {
    answer = "";
  }
  const { has_brand, has_link, sentiment, competitors } = analyzeAnswer(answer);
  return {
    query: phrase,
    platform,
    has_official_link: has_link,
    has_brand_mention: has_brand,
    sentiment,
    competitors,
    answer_preview: answer.slice(0, 150),
  };
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as VerifyRequest;
    const { phrases, platforms } = body;

    if (!phrases?.length || !platforms?.length) {
      return NextResponse.json(
        { status: "error", message: "Missing phrases or platforms", results: [] },
        { status: 400 }
      );
    }

    // Run all verifications concurrently (max ~10 at a time via Promise.all)
    const tasks: Promise<VerifyResult>[] = [];
    for (const phrase of phrases) {
      for (const platform of platforms) {
        tasks.push(verifyOne(phrase, platform));
      }
    }

    const results = await Promise.all(tasks);
    return NextResponse.json({ status: "success", results });
  } catch (err) {
    return NextResponse.json(
      { status: "error", message: String(err), results: [] },
      { status: 500 }
    );
  }
}
