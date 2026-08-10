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
  { id: "overview", path: "/overview", label: "总览", labelEn: "Overview" },
  { id: "zhiku", path: "/zhiku", label: "智库", labelEn: "Knowledge" },
  { id: "zhice", path: "/zhice", label: "智测", labelEn: "Verify" },
  { id: "zhizao", path: "/zhizao", label: "智造", labelEn: "Generate" },
  { id: "zhiyou", path: "/zhiyou", label: "智优", labelEn: "Optimize" },
  { id: "zhibu", path: "/zhibu", label: "智布", labelEn: "Distribute" },
  { id: "zhixi", path: "/zhixi", label: "智析", labelEn: "Analytics" },
  { id: "zhongshu", path: "/zhongshu", label: "智中枢", labelEn: "Hub" },
  { id: "request", path: "/request", label: "需求提交", labelEn: "Request" },
] as const;

export const PIPELINE_MODULES = [
  {
    id: "zhiku",
    icon: "📚",
    color: "#ffa726",
    path: "/zhiku",
    descKey: "overview.zhiku_desc",
  },
  {
    id: "zhice",
    icon: "🔍",
    color: "#00d4aa",
    path: "/zhice",
    descKey: "overview.zhice_desc",
  },
  {
    id: "zhizao",
    icon: "✍️",
    color: "#ffcc02",
    path: "/zhizao",
    descKey: "overview.zhizao_desc",
  },
  {
    id: "zhiyou",
    icon: "✨",
    color: "#e91e63",
    path: "/zhiyou",
    descKey: "overview.zhiyou_desc",
  },
  {
    id: "zhibu",
    icon: "📤",
    color: "#29b6f6",
    path: "/zhibu",
    descKey: "overview.zhibu_desc",
  },
  {
    id: "zhixi",
    icon: "📊",
    color: "#ab47bc",
    path: "/zhixi",
    descKey: "overview.zhixi_desc",
  },
  {
    id: "zhongshu",
    icon: "🎛️",
    color: "#ff6b35",
    path: "/zhongshu",
    descKey: "overview.zhongshu_desc",
  },
] as const;

export const PERSONA_IDENTITIES_ZH = [
  "新卖家（未注册）",
  "新卖家（已注册）",
  "新卖家（已上线）",
  "< 1年卖家",
  "1-2年卖家",
  "2-3年卖家",
  "3年以上卖家",
  "服务商",
];

export const PERSONA_IDENTITIES_EN = [
  "New Seller (Pre-registration)",
  "New Seller (Registered)",
  "New Seller (Launched)",
  "< 1 Year Seller",
  "1-2 Year Seller",
  "2-3 Year Seller",
  "3+ Year Seller",
  "Service Provider",
];

export const PERSONA_COMPANY_TYPES_ZH = [
  "品牌+自有工厂",
  "品牌+代工工厂",
  "工厂（无品牌）",
  "经销商/贸易商",
  "个人",
  "其他",
];

export const PERSONA_COMPANY_TYPES_EN = [
  "Brand + Factory",
  "Brand + Partner Factory",
  "Factory (No Brand)",
  "Distributor/Reseller",
  "Individual",
  "Other",
];

export const PERSONA_MARKETPLACES_EN = [
  "US", "Canada", "Mexico", "UK", "Germany", "France",
  "Italy", "Spain", "Japan", "UAE", "Saudi Arabia",
  "Brazil", "Australia", "India",
];

export const PERSONA_MARKETPLACES_ZH = [
  "美国站", "加拿大站", "墨西哥站", "英国站", "德国站", "法国站",
  "意大利站", "西班牙站", "日本站", "阿联酋站", "沙特站",
  "巴西站", "澳洲站", "印度站",
];

export const PERSONA_CONTENT_CATEGORIES_EN = [
  "Getting Started", "Product Sourcing", "Compliance",
  "Logistics & FBA", "Brand Building", "Peak Season & Traffic",
  "Business Buying", "Seller Encyclopedia", "Seller Growth Services",
  "Factory Zone", "Cross-border Payments", "Category Insights",
  "PPC & Advertising",
];

export const PERSONA_CONTENT_CATEGORIES_ZH = [
  "新手指南", "选品方法", "合规政策",
  "物流与FBA", "品牌建设", "旺季引流",
  "企业购", "百科", "卖家成长服务",
  "工厂专区", "跨境支付", "品类分析",
  "PPC与广告",
];

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
