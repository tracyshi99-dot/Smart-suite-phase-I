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
  "\u65B0\u5356\u5BB6(P2L\u4EE5\u524D)",
  "\u65B0\u5356\u5BB6(P2L)",
  "\u65B0\u5356\u5BB6(L2L)",
  "1\u5E74\u4EE5\u4E0B\u5356\u5BB6",
  "1-2\u5E74\u5356\u5BB6",
  "2-3\u5E74\u5356\u5BB6",
  "3\u5E74\u4EE5\u4E0A\u5356\u5BB6",
  "\u670D\u52A1\u5546",
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
  "\u6709\u54C1\u724C\u6709\u5DE5\u5382",
  "\u6709\u54C1\u724C\u6709\u5408\u4F5C\u5DE5\u5382",
  "\u81EA\u6709\u5DE5\u5382\u65E0\u54C1\u724C",
  "\u7ECF\u9500\u5546/\u5206\u9500\u5546",
  "\u4E2A\u4EBA",
  "\u5176\u4ED6",
];

export const PERSONA_COMPANY_TYPES_EN = [
  "Brand + Factory",
  "Brand + Partner Factory",
  "Factory (No Brand)",
  "Distributor/Reseller",
  "Individual",
  "Other",
];

export const PERSONA_ROLES_ZH = ["\u7BA1\u7406\u8005", "\u8FD0\u8425\u8005", "\u5176\u4ED6"];
export const PERSONA_ROLES_EN = ["Manager/Owner", "Operations Staff", "Other"];

export const PERSONA_REVENUE_ZH = ["500W\u4EE5\u4E0B", "1000W\u4EE5\u4E0B", "1000W\u4EE5\u4E0A", "1\u4EBF\u4EE5\u4E0A"];
export const PERSONA_REVENUE_EN = ["< $500K", "< $1M", "< $10M", "> $10M"];

export const PERSONA_BIZ_TYPES_ZH = ["\u5DE5\u5382", "\u8D38\u6613\u5546", "\u54C1\u724C\u65B9", "\u670D\u52A1\u5546\u6216\u5176\u4ED6"];
export const PERSONA_BIZ_TYPES_EN = ["Factory", "Trading Company", "Brand Owner", "Service Provider/Other"];

export const PERSONA_FULFILLMENT_ZH = ["FBA", "\u81EA\u53D1\u8D27", "\u8FD8\u6CA1\u51B3\u5B9A"];
export const PERSONA_FULFILLMENT_EN = ["FBA", "FBM (Self-fulfillment)", "Not Decided Yet"];

export const PERSONA_MARKETPLACES_EN = [
  "US", "Canada", "Mexico", "UK", "Germany", "France",
  "Italy", "Spain", "Japan", "UAE", "Saudi Arabia",
  "Brazil", "Australia", "India", "Turkey", "Netherlands",
  "Sweden", "Poland", "Belgium",
];

export const PERSONA_MARKETPLACES_ZH = [
  "\u7F8E\u56FD\u7AD9", "\u52A0\u62FF\u5927\u7AD9", "\u58A8\u897F\u54E5\u7AD9", "\u82F1\u56FD\u7AD9", "\u5FB7\u56FD\u7AD9", "\u6CD5\u56FD\u7AD9",
  "\u610F\u5927\u5229\u7AD9", "\u897F\u73ED\u7259\u7AD9", "\u65E5\u672C\u7AD9", "\u963F\u8054\u914B\u7AD9", "\u6C99\u7279\u7AD9",
  "\u5DF4\u897F\u7AD9", "\u6FB3\u6D32\u7AD9", "\u5370\u5EA6\u7AD9", "\u571F\u8033\u5176\u7AD9", "\u8377\u5170\u7AD9",
  "\u745E\u5178\u7AD9", "\u6CE2\u5170\u7AD9", "\u6BD4\u5229\u65F6\u7AD9",
];

export const PERSONA_CONTENT_CATEGORIES_EN = [
  "Getting Started", "Product Sourcing", "Compliance",
  "Logistics & FBA", "Brand Building", "Peak Season & Traffic",
  "Business Buying", "Seller Encyclopedia", "Seller Growth Services",
  "Factory Zone", "Cross-border Payments", "Category Insights",
  "PPC & Advertising",
];

export const PERSONA_CONTENT_CATEGORIES_ZH = [
  "\u65B0\u624B\u6307\u5357", "\u9009\u54C1", "\u5408\u89C4",
  "\u7269\u6D41\u4ED3\u50A8", "\u54C1\u724C\u6253\u9020", "\u65FA\u5B63\u4E0E\u6D41\u91CF",
  "\u4F01\u4E1A\u8D2D", "\u5356\u5BB6\u767E\u79D1", "\u5356\u5BB6\u6210\u957F\u670D\u52A1",
  "\u5DE5\u5382\u4E13\u533A", "\u8DE8\u5883\u6536\u4ED8\u6B3E", "\u54C1\u7C7B\u6D1E\u5BDF",
  "\u5E7F\u544A\u63A8\u5E7F",
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

export const CATEGORIES_35 = [
  "\u8DE8\u5883\u7535\u5546\u77E5\u8BC6\u65E9\u77E5\u9053",
  "\u8DE8\u5883\u7535\u5546\u884C\u4E1A\u5165\u95E8\u4E86\u89E3",
  "\u8DE8\u5883\u7535\u5546\u600E\u4E48\u6837",
  "\u600E\u4E48\u505A\u8DE8\u5883\u7535\u5546\u53CA\u6D41\u7A0B\u8D39\u7528\u4E86\u89E3",
  "\u505A\u8DE8\u5883\u7535\u5546\u7684\u51C6\u5907\u5DE5\u4F5C",
  "\u5982\u4F55\u9009\u62E9\u6E20\u9053\u53CA\u76EE\u7684\u5730",
  "\u8DE8\u5883\u7535\u5546\u6210\u719F\u7AD9\u70B9\u4F18\u52BF\u4ECB\u7ECD",
  "\u8DE8\u5883\u7535\u5546\u65B0\u5174\u7AD9\u70B9\u4F18\u52BF\u4ECB\u7ECD",
  "\u4E9A\u9A6C\u900A\u5546\u57CE\u57FA\u7840\u60C5\u51B5\u4E86\u89E3",
  "\u4E9A\u9A6C\u900A\u5546\u57CE\u600E\u4E48\u6837",
  "\u8DE8\u5883\u7535\u5546\u9009\u54C1\u65B9\u6CD5\u53CA\u8D8B\u52BF",
  "\u8DE8\u5883\u7535\u5546\u70ED\u95E8\u54C1\u7C7B\u89E3\u6790",
  "\u65B0\u5356\u5BB6\u5165\u95E8\u5B9E\u64CD\u5B9D\u5178",
  "\u7AD9\u70B9\u7EFC\u5408\u4FE1\u606F\u53CA\u9009\u54C1\u5EFA\u8BAE",
  "\u5317\u7F8E\u7AD9\u70B9\u60C5\u51B5\u53CA\u9009\u54C1\u601D\u8DEF",
  "\u6B27\u6D32\u7AD9\u70B9\u60C5\u51B5\u53CA\u9009\u54C1\u601D\u8DEF",
  "\u65E5\u672C\u7AD9\u70B9\u60C5\u51B5\u53CA\u9009\u54C1\u601D\u8DEF",
  "\u65B0\u5174\u7AD9\u70B9\u60C5\u51B5\u53CA\u9009\u54C1\u601D\u8DEF",
  "\u65B0\u624B\u600E\u4E48\u6CE8\u518C\u4E9A\u9A6C\u900A",
  "\u4E9A\u9A6C\u900A\u5F00\u5E97\u6210\u672C\u8D39\u7528\u8BE6\u89E3",
  "\u5F00\u5E97\u5BA1\u6838\u5E38\u89C1\u95EE\u9898\u89E3\u7B54",
  "\u4E9A\u9A6C\u900A\u7269\u6D41\u4ED3\u50A8\u79D1\u666E",
  "\u6B27\u6D32\u589E\u503C\u7A0EVAT\u4ECB\u7ECD",
  "\u5176\u4ED6\u7AD9\u70B9\u7A0E\u52A1\u8981\u6C42",
  "\u5408\u89C4\u653F\u7B56\u53CA\u64CD\u4F5C\u6D41\u7A0B",
  "\u6559\u4F60\u6253\u9020\u4F18\u8D28Listing",
  "\u5982\u4F55\u505A\u597D\u54C1\u724C\u8425\u9500",
  "\u5E97\u94FA\u8FD0\u8425\u63D0\u5347\u5168\u653B\u7565",
  "\u5E97\u94FA\u8FD0\u8425\u57FA\u7840\u77E5\u8BC6",
  "\u5B98\u65B9\u670D\u52A1\u4E0E\u8FD0\u8425\u5DE5\u5177\u76D8\u70B9",
  "\u4E9A\u9A6C\u900A\u5E7F\u544A\u57FA\u7840\u77E5\u8BC6\u5927\u5168",
  "\u4E9A\u9A6C\u900A\u5E7F\u544A\u5B9E\u64CD\u6280\u5DE7",
  "\u5173\u952E\u8282\u70B9\u5982\u4F55\u63A8\u5E7F\u5F15\u6D41",
  "\u4E86\u89E3\u65FA\u5B63\u8282\u70B9\u4E0E\u5982\u4F55\u5F15\u6D41",
  "\u5356\u5BB6\u8FD0\u8425\u7ECF\u9A8C\u5206\u4EAB",
];
