/**
 * GEO/SEO Analytics Data — from uploaded Excel
 * Source: -GEOSEO- (1).xlsx
 */

// Sheet 1: AI Platform Visits — 月访问量 (万), split by Total / Mobile(APP) / PC(Website)
// Source: 右侧列 "2026年AI平台数据统计（月访问量 维度）"
export const GEO_MAU = {
  CN: [
    { platform: "DeepSeek", Jan: 29800, Feb: 40657, Mar: 35550, Apr: 62548, May: 0, Jun: 62288, desc: "国产算力，低成本API，20-35岁男性为主" },
    { platform: "  Mobile", Jan: 0, Feb: 13257, Mar: 0, Apr: 13898, May: 0, Jun: 13908, desc: "" },
    { platform: "  PC", Jan: 29800, Feb: 27400, Mar: 35550, Apr: 48650, May: 0, Jun: 48380, desc: "" },
    { platform: "豆包", Jan: 11200, Feb: 41268, Mar: 9890, Apr: 49893, May: 0, Jun: 47718, desc: "字节旗下，高互动娱乐学习，APP为主" },
    { platform: "  Mobile", Jan: 0, Feb: 31531, Mar: 0, Apr: 33604, May: 0, Jun: 32431, desc: "" },
    { platform: "  PC", Jan: 11200, Feb: 9737, Mar: 9890, Apr: 16289, May: 0, Jun: 15287, desc: "" },
    { platform: "元宝", Jan: 1943, Feb: 12457, Mar: 1559, Apr: 12886, May: 0, Jun: 11602, desc: "腾讯AI助手，微信生态，公众号优先" },
    { platform: "  Mobile", Jan: 0, Feb: 10945, Mar: 0, Apr: 11113, May: 0, Jun: 10392, desc: "" },
    { platform: "  PC", Jan: 1943, Feb: 1512, Mar: 1559, Apr: 1773, May: 0, Jun: 1210, desc: "" },
    { platform: "Kimi", Jan: 3346, Feb: 6978, Mar: 4568, Apr: 6902, May: 0, Jun: 6285, desc: "长文本处理，PC网页端，22-40岁高学历" },
    { platform: "  Mobile", Jan: 0, Feb: 2473, Mar: 0, Apr: 2533, May: 0, Jun: 2269, desc: "" },
    { platform: "  PC", Jan: 3346, Feb: 4505, Mar: 4568, Apr: 4369, May: 0, Jun: 4016, desc: "" },
    { platform: "文小言", Jan: 369, Feb: 1173, Mar: 255, Apr: 1001, May: 0, Jun: 890, desc: "百度AI，高时效性，政策更新" },
    { platform: "  Mobile", Jan: 0, Feb: 925, Mar: 0, Apr: 770, May: 0, Jun: 657, desc: "" },
    { platform: "  PC", Jan: 369, Feb: 248, Mar: 255, Apr: 231, May: 0, Jun: 233, desc: "" },
    { platform: "千问", Jan: 3381, Feb: 23349, Mar: 3305, Apr: 25607, May: 0, Jun: 47041, desc: "阿里开源，技术文档，FAQ结构化" },
    { platform: "  Mobile", Jan: 0, Feb: 20269, Mar: 0, Apr: 3572, May: 0, Jun: 2511, desc: "" },
    { platform: "  PC", Jan: 3381, Feb: 3080, Mar: 3305, Apr: 22035, May: 0, Jun: 44530, desc: "" },
  ],
  WW: [
    { platform: "ChatGPT", Jan: 572400, Feb: 535200, Mar: 535300, Apr: 569000, May: 0, Jun: 655549, desc: "全球最大AI，高质量结构化内容" },
    { platform: "  Mobile", Jan: 0, Feb: 0, Mar: 0, Apr: 0, May: 0, Jun: 99549, desc: "" },
    { platform: "  PC", Jan: 0, Feb: 0, Mar: 0, Apr: 569000, May: 0, Jun: 556000, desc: "" },
    { platform: "Gemini", Jan: 206900, Feb: 211000, Mar: 218000, Apr: 285000, May: 0, Jun: 311274, desc: "Google生态，多模态，Android深度集成" },
    { platform: "  Mobile", Jan: 0, Feb: 0, Mar: 0, Apr: 0, May: 0, Jun: 16274, desc: "" },
    { platform: "  PC", Jan: 0, Feb: 0, Mar: 0, Apr: 285000, May: 0, Jun: 295000, desc: "" },
    { platform: "Grok", Jan: 31400, Feb: 29800, Mar: 31000, Apr: 29037, May: 0, Jun: 28866, desc: "X/Twitter旗下，实时热搜解读" },
    { platform: "  Mobile", Jan: 0, Feb: 0, Mar: 0, Apr: 0, May: 0, Jun: 6788, desc: "" },
    { platform: "  PC", Jan: 0, Feb: 0, Mar: 0, Apr: 29037, May: 0, Jun: 22078, desc: "" },
  ],
};

// Sheet 2: 信源分析 — 各平台信源占比 (6月)
export const SOURCE_ANALYSIS = [
  { platform: "豆包", sources: [
    { name: "亚马逊全球开店", url: "gs.amazon.cn", pct: 33.45 },
    { name: "抖音", url: "douyin.com", pct: 22.13 },
    { name: "Amazon Seller Central", url: "sell.amazon.com", pct: 6.05 },
    { name: "雨果跨境", url: "cifnews.com", pct: 3.38 },
    { name: "今日头条", url: "toutiao.com", pct: 3.02 },
  ]},
  { platform: "元宝", sources: [
    { name: "亚马逊全球开店", url: "gs.amazon.cn", pct: 34.10 },
    { name: "大数跨境", url: "10100.com", pct: 14.42 },
    { name: "Amazon Seller Central", url: "sell.amazon.com", pct: 10.74 },
    { name: "腾讯网", url: "qq.com", pct: 5.32 },
    { name: "AMZ123", url: "amz123.com", pct: 2.57 },
  ]},
  { platform: "DeepSeek", sources: [
    { name: "亚马逊全球开店", url: "gs.amazon.cn", pct: 42.18 },
    { name: "CoGoLinks", url: "cogolinks.com", pct: 9.72 },
    { name: "跨境魔方", url: "upkuajing.com", pct: 4.39 },
    { name: "连连国际", url: "lianlianpay.com", pct: 2.97 },
    { name: "iPayLinks", url: "ipaylinks.com", pct: 1.93 },
  ]},
  { platform: "千问", sources: [
    { name: "亚马逊全球开店", url: "gs.amazon.cn", pct: 44.98 },
    { name: "雨果跨境", url: "cifnews.com", pct: 4.64 },
    { name: "php中文网", url: "php.cn", pct: 4.09 },
    { name: "Seller Central", url: "sellercentral.amazon.com", pct: 3.19 },
    { name: "百运网", url: "by56.com", pct: 2.87 },
  ]},
  { platform: "Kimi", sources: [
    { name: "亚马逊全球开店", url: "gs.amazon.cn", pct: 44.20 },
    { name: "雨果跨境", url: "cifnews.com", pct: 4.94 },
    { name: "跨境笔记", url: "kuajingnote.com", pct: 4.54 },
    { name: "腾讯", url: "qq.com", pct: 4.04 },
    { name: "AMZ123", url: "amz123.com", pct: 2.52 },
  ]},
  { platform: "ChatGPT", sources: [
    { name: "亚马逊全球开店", url: "gs.amazon.cn", pct: 39.20 },
    { name: "Sell on Amazon", url: "sell.amazon.com", pct: 9.20 },
    { name: "财讯网", url: "caixun.cn", pct: 6.19 },
    { name: "出海网", url: "chwang.com", pct: 6.19 },
    { name: "亚马逊中国", url: "amazon.cn", pct: 6.19 },
  ]},
];

// Sheet 3.1: GEO Input Table — 品牌词链接提及率 by platform by month
export const INPUT_LINK_RATE = [
  { month: "Jan", 元宝: 48.48, DeepSeek: 50.84, 豆包: 61.62, ChatGPT: 35.02, Kimi: 0, 千问: 0, Gemini: 0 },
  { month: "Feb", 元宝: 52.53, DeepSeek: 55.89, 豆包: 62.96, ChatGPT: 42.42, Kimi: 0, 千问: 0, Gemini: 0 },
  { month: "Mar", 元宝: 65.99, DeepSeek: 62.63, 豆包: 69.36, ChatGPT: 44.11, Kimi: 0, 千问: 0, Gemini: 0 },
  { month: "Apr", 元宝: 61.21, DeepSeek: 50.38, 豆包: 63.22, ChatGPT: 39.80, Kimi: 0, 千问: 0, Gemini: 0 },
  { month: "May", 元宝: 73.98, DeepSeek: 66.45, 豆包: 48.60, ChatGPT: 30.11, Kimi: 59.14, 千问: 66.88, Gemini: 46.88 },
  { month: "Jun", 元宝: 75.36, DeepSeek: 66.74, 豆包: 56.88, ChatGPT: 28.54, Kimi: 53.39, 千问: 66.94, Gemini: 44.76 },
];

// Sheet 3.1: Input Summary
export const INPUT_SUMMARY = {
  headers: ["指标", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "YTD"],
  rows: [
    ["提示词#", "297", "297", "297", "397", "564", "646", "646"],
    ["品牌词链接提及", "582", "635", "719", "852", "1,019", "1,108", "—"],
    ["品牌词链接提及率", "49.0%", "53.5%", "60.5%", "53.7%", "54.8%", "56.9%", "—"],
    ["行业提示词", "—", "—", "—", "—", "98", "159", "159"],
    ["行业词提及率", "—", "—", "—", "—", "7.4%", "37.2%", "—"],
    ["新建内容#", "98", "43", "118", "123", "135", "131", "648"],
    ["旧内容优化#", "26", "12", "0", "1", "0", "0", "39"],
    ["官网链接提及率", "44.3%", "35.3%", "44.7%", "37.7%", "48.3%", "51.6%", "—"],
    ["官网链接提及总量", "745", "839", "1,063", "1,197", "2,498", "2,666", "—"],
  ],
};

// Sheet 4: GEO Output — Traffic & RegStart by Platform
export const GEO_OUTPUT = {
  traffic: [
    { metric: "GEO Traffic Total", Jan: 3446, Feb: 2146, Mar: 5326, Apr: 5290, May: 5831, Jun: 4756, Jul: 2825, YTD: 29620 },
    { metric: "CN Website", Jan: 2229, Feb: 1552, Mar: 3890, Apr: 3909, May: 4146, Jun: 3269, Jul: 1968, YTD: 20963 },
    { metric: "  豆包", Jan: 1764, Feb: 1292, Mar: 3407, Apr: 3387, May: 3501, Jun: 2759, Jul: 1651, YTD: 17761 },
    { metric: "  ChatGPT", Jan: 150, Feb: 89, Mar: 119, Apr: 105, May: 245, Jun: 222, Jul: 162, YTD: 1092 },
    { metric: "  元宝", Jan: 119, Feb: 31, Mar: 64, Apr: 135, May: 111, Jun: 81, Jul: 27, YTD: 568 },
    { metric: "  千问", Jan: 75, Feb: 63, Mar: 186, Apr: 124, May: 132, Jun: 116, Jul: 60, YTD: 756 },
    { metric: "  Gemini", Jan: 118, Feb: 75, Mar: 113, Apr: 158, May: 154, Jun: 90, Jul: 63, YTD: 771 },
    { metric: "CN2NA Website", Jan: 1217, Feb: 594, Mar: 1436, Apr: 1381, May: 1685, Jun: 1487, Jul: 857, YTD: 8657 },
  ],
  regStart: [
    { metric: "GEO Reg.Start Total", Jan: 172, Feb: 116, Mar: 256, Apr: 234, May: 264, Jun: 249, Jul: 305, YTD: 1596 },
    { metric: "CN Website", Jan: 89, Feb: 65, Mar: 165, Apr: 164, May: 163, Jun: 152, Jul: 189, YTD: 987 },
    { metric: "  豆包", Jan: 73, Feb: 51, Mar: 147, Apr: 149, May: 128, Jun: 123, Jul: 56, YTD: 727 },
    { metric: "  ChatGPT", Jan: 5, Feb: 6, Mar: 7, Apr: 6, May: 14, Jun: 23, Jul: 9, YTD: 70 },
    { metric: "  Gemini", Jan: 10, Feb: 2, Mar: 9, Apr: 10, May: 10, Jun: 9, Jul: 3, YTD: 53 },
    { metric: "CN2NA Website", Jan: 76, Feb: 43, Mar: 81, Apr: 65, May: 93, Jun: 89, Jul: 99, YTD: 546 },
  ],
  cleanLaunch: [
    { metric: "Total GEO", Jan: 12, Feb: 7, Mar: 26, Apr: 23, May: 32, Jun: 17, Jul: 11, YTD: 128 },
    { metric: "  CN GEO", Jan: 9, Feb: 6, Mar: 18, Apr: 21, May: 23, Jun: 11, Jul: 5, YTD: 93 },
    { metric: "  WW GEO", Jan: 3, Feb: 1, Mar: 8, Apr: 2, May: 9, Jun: 6, Jul: 6, YTD: 35 },
    { metric: "WW Direct", Jan: 829, Feb: 431, Mar: 1546, Apr: 1467, May: 1879, Jun: 3245, Jul: 1413, YTD: 10810 },
    { metric: "GEO+Direct Total", Jan: 841, Feb: 438, Mar: 1572, Apr: 1490, May: 1911, Jun: 3262, Jul: 1424, YTD: 10938 },
    { metric: "SSR Total (大盘)", Jan: 7988, Feb: 4373, Mar: 12032, Apr: 12209, May: 13694, Jun: 17558, Jul: 10785, YTD: 78639 },
  ],
  conversion: [
    { metric: "Total GEO CL_RS%", Jan: "7.0%", Feb: "6.0%", Mar: "10.2%", Apr: "9.8%", May: "12.1%", Jun: "6.8%", Jul: "3.6%", YTD: "9.9%" },
    { metric: "WW Direct CL_RS%", Jan: "17.8%", Feb: "21.1%", Mar: "23.5%", Apr: "21.1%", May: "24.3%", Jun: "32.7%", Jul: "23.3%", YTD: "24.6%" },
    { metric: "GEO+Direct CL_RS%", Jan: "17.6%", Feb: "20.7%", Mar: "23.2%", Apr: "20.9%", May: "24.1%", Jun: "32.3%", Jul: "22.9%", YTD: "24.3%" },
    { metric: "SSR Total CL_RS%", Jan: "21.0%", Feb: "24.2%", Mar: "26.0%", Apr: "25.8%", May: "28.0%", Jun: "34.1%", Jul: "23.4%", YTD: "27.1%" },
  ],
};

// Sheet 3.2: Phrase-level verification summary (aggregated by category)
export const PHRASE_CATEGORIES = [
  { category: "入口", total: 112, jun_元宝: 100, jun_DeepSeek: 94, jun_豆包: 70, jun_ChatGPT: 32, jun_Kimi: 60, jun_千问: 68 },
  { category: "入驻&注册", total: 185, jun_元宝: 141, jun_DeepSeek: 128, jun_豆包: 110, jun_ChatGPT: 43, jun_Kimi: 121, jun_千问: 133 },
  { category: "其他", total: 161, jun_元宝: 91, jun_DeepSeek: 75, jun_豆包: 86, jun_ChatGPT: 61, jun_Kimi: 59, jun_千问: 84 },
  { category: "费用", total: 12, jun_元宝: 8, jun_DeepSeek: 3, jun_豆包: 5, jun_ChatGPT: 0, jun_Kimi: 6, jun_千问: 4 },
  { category: "政策", total: 15, jun_元宝: 4, jun_DeepSeek: 2, jun_豆包: 5, jun_ChatGPT: 1, jun_Kimi: 8, jun_千问: 3 },
  { category: "新手", total: 46, jun_元宝: 39, jun_DeepSeek: 41, jun_豆包: 43, jun_ChatGPT: 39, jun_Kimi: 36, jun_千问: 37 },
  { category: "品类", total: 20, jun_元宝: 20, jun_DeepSeek: 20, jun_豆包: 0, jun_ChatGPT: 0, jun_Kimi: 7, jun_千问: 0 },
  { category: "物流", total: 7, jun_元宝: 2, jun_DeepSeek: 2, jun_豆包: 3, jun_ChatGPT: 2, jun_Kimi: 3, jun_千问: 2 },
  { category: "行业", total: 38, jun_元宝: 22, jun_DeepSeek: 26, jun_豆包: 26, jun_ChatGPT: 26, jun_Kimi: 24, jun_千问: 23 },
  { category: "站点", total: 3, jun_元宝: 0, jun_DeepSeek: 1, jun_豆包: 0, jun_ChatGPT: 0, jun_Kimi: 0, jun_千问: 0 },
];

// Sheet 6: 语义范围 × 平台提及率 (6月)
export const SEMANTIC_COVERAGE = [
  { category: "开店入驻流程", total: 161, rate_元宝: "69.6%", rate_DeepSeek: "62.7%", rate_豆包: "45.3%", rate_ChatGPT: "26.1%", rate_Kimi: "68.3%", rate_千问: "66.5%" },
  { category: "官网与站点入口", total: 105, rate_元宝: "69.5%", rate_DeepSeek: "71.4%", rate_豆包: "55.2%", rate_ChatGPT: "30.5%", rate_Kimi: "24.8%", rate_千问: "71.4%" },
  { category: "平台综合信息", total: 51, rate_元宝: "88.2%", rate_DeepSeek: "74.5%", rate_豆包: "86.3%", rate_ChatGPT: "62.8%", rate_Kimi: "49.0%", rate_千问: "78.4%" },
  { category: "卖家后台与登录", total: 45, rate_元宝: "62.2%", rate_DeepSeek: "55.6%", rate_豆包: "64.4%", rate_ChatGPT: "31.1%", rate_Kimi: "22.2%", rate_千问: "53.3%" },
  { category: "入驻条件与材料", total: 62, rate_元宝: "38.7%", rate_DeepSeek: "33.9%", rate_豆包: "29.0%", rate_ChatGPT: "4.8%", rate_Kimi: "33.9%", rate_千问: "33.9%" },
  { category: "账号注册", total: 29, rate_元宝: "44.8%", rate_DeepSeek: "44.8%", rate_豆包: "41.4%", rate_ChatGPT: "13.8%", rate_Kimi: "37.9%", rate_千问: "44.8%" },
  { category: "新手入门", total: 34, rate_元宝: "79.4%", rate_DeepSeek: "82.4%", rate_豆包: "88.2%", rate_ChatGPT: "73.5%", rate_Kimi: "70.6%", rate_千问: "76.5%" },
  { category: "费用与成本", total: 40, rate_元宝: "35.0%", rate_DeepSeek: "25.0%", rate_豆包: "30.0%", rate_ChatGPT: "25.0%", rate_Kimi: "32.5%", rate_千问: "27.5%" },
  { category: "市场与行业趋势", total: 36, rate_元宝: "61.1%", rate_DeepSeek: "72.2%", rate_豆包: "72.2%", rate_ChatGPT: "72.2%", rate_Kimi: "66.7%", rate_千问: "63.9%" },
  { category: "选品与品类", total: 17, rate_元宝: "88.2%", rate_DeepSeek: "88.2%", rate_豆包: "11.8%", rate_ChatGPT: "5.9%", rate_Kimi: "41.2%", rate_千问: "11.8%" },
];
