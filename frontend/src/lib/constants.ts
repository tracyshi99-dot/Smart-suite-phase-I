export const PLATFORMS = {
  CN: ["deepseek", "doubao", "kimi", "yuanbao", "qianwen"],
  WW: ["chatgpt", "gemini", "perplexity", "grok"],
} as const;

export const ALL_PLATFORMS = [
  "deepseek",
  "doubao",
  "kimi",
  "yuanbao",
  "qianwen",
  "chatgpt",
  "gemini",
  "perplexity",
  "grok",
] as const;

export const TEMPLATES = [
  { id: "auto", label: "自动 / Auto" },
  { id: "registration", label: "注册 / Registration" },
  { id: "fees", label: "费用 / Fees" },
  { id: "logistics", label: "物流 / Logistics" },
  { id: "advertising", label: "广告 / Advertising" },
  { id: "listing", label: "Listing优化 / Listing" },
] as const;

export const NAV_ITEMS = [
  { id: "zhiku", path: "/zhiku", label: "智库", labelEn: "Knowledge" },
  { id: "zhice", path: "/zhice", label: "智测", labelEn: "Verify" },
  { id: "zhizao", path: "/zhizao", label: "智造", labelEn: "Generate" },
  { id: "zhiyou", path: "/zhiyou", label: "智优", labelEn: "Optimize" },
  { id: "zhibu", path: "/zhibu", label: "智布", labelEn: "Distribute" },
  { id: "zhixi", path: "/zhixi", label: "智析", labelEn: "Analytics" },
  { id: "zhongshu", path: "/zhongshu", label: "智中枢", labelEn: "Hub" },
] as const;

export const SUPPORTED_LOCALES = ["en", "zh-CN", "zh-TW", "ko", "vi"] as const;
export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];

export const LOCALE_LABELS: Record<SupportedLocale, string> = {
  en: "English",
  "zh-CN": "简体中文",
  "zh-TW": "繁體中文",
  ko: "한국어",
  vi: "Tiếng Việt",
};

export const SESSION_TIMEOUT_MS = 8 * 60 * 60 * 1000; // 8 hours
export const API_TIMEOUT_MS = 15000; // 15 seconds
export const LONG_OP_TIMEOUT_MS = 120000; // 120 seconds
export const POLL_INTERVAL_MS = 5000; // 5 seconds
export const MAX_RETRIES = 3;
