"use client";

import Link from "next/link";
import { useI18nStore } from "@/stores/i18n-store";

interface ModuleData {
  id: string;
  path: string;
  icon: string;
  color: string;
  tag: string;
  name: { en: string; zh: string };
  sub: { en: string; zh: string };
  desc: { en: string; zh: string };
  caps: { en: string[]; zh: string[] };
  impact: { v: string; en: string; zh: string }[];
}

const MODULES: ModuleData[] = [
  {
    id: "zhiku", path: "/zhiku", icon: "\u{1F4DA}",
    color: "#ffa726", tag: "Production",
    name: { en: "Prompt Intelligencer", zh: "\u667A\u5E93 Prompt Intelligencer" },
    sub: { en: "AI Search Phrase Discovery", zh: "AI \u68C0\u7D22\u77ED\u8BED\u53D1\u73B0" },
    desc: {
      en: "Connects to 7 AI search platforms to capture real-time high-precision search phrases with intent classification and priority scoring.",
      zh: "\u5BF9\u63A5 7 \u5927\u4E3B\u6D41 AI \u68C0\u7D22\u5E73\u53F0\uFF0C\u83B7\u53D6\u5B9E\u65F6\u6027\u5F3A\u7684\u68C0\u7D22\u77ED\u8BED\uFF0C\u652F\u6301\u610F\u56FE\u5206\u7C7B\u4E0E\u4F18\u5148\u7EA7\u8BC4\u5206\u3002",
    },
    caps: {
      en: ["7 AI platforms connected", "Multi-intent query generation", "Priority scoring (1-5)", "Persona-based expansion"],
      zh: ["\u5BF9\u63A5 7 \u5927 AI \u5E73\u53F0", "\u591A\u610F\u56FE\u67E5\u8BE2\u751F\u6210", "\u4F18\u5148\u7EA7\u8BC4\u5206 (1-5)", "\u753B\u50CF\u63A8\u6F14\u88C2\u53D8"],
    },
    impact: [
      { v: "7", en: "AI Platforms", zh: "AI \u5E73\u53F0" },
      { v: "Real-time", en: "Phrase Freshness", zh: "\u77ED\u8BED\u65F6\u6548\u6027" },
      { v: "3-5x", en: "Variants/Topic", zh: "\u6BCF\u4E3B\u9898\u53D8\u4F53" },
      { v: "35", en: "Categories", zh: "\u8BDD\u9898\u7C7B\u522B" },
    ],
  },
  {
    id: "zhice", path: "/zhice", icon: "\u{1F50D}",
    color: "#00bfa5", tag: "Production",
    name: { en: "AI Search Tester", zh: "\u667A\u6D4B AI Search Tester" },
    sub: { en: "AI Search Coverage Verification", zh: "AI \u641C\u7D22\u8986\u76D6\u9A8C\u8BC1" },
    desc: {
      en: "Verifies phrase coverage across 7 AI search platforms, discovers content gaps, and guides precision content production.",
      zh: "\u5728 7 \u5927 AI \u641C\u7D22\u5E73\u53F0\u4E0A\u9A8C\u8BC1\u77ED\u8BED\u8986\u76D6\u60C5\u51B5\uFF0C\u53D1\u73B0\u5185\u5BB9\u7F3A\u53E3\uFF0C\u6307\u5BFC\u7CBE\u51C6\u5185\u5BB9\u751F\u4EA7\u3002",
    },
    caps: {
      en: ["7-platform full coverage verification", "Brand mention + official link dual detection", "Gap auto-classification (full_gap / partial_gap / covered)", "AI auto-execution + manual upload support"],
      zh: ["7 \u5E73\u53F0\u5168\u8986\u76D6\u9A8C\u8BC1", "\u54C1\u724C\u63D0\u53CA + \u5B98\u65B9\u94FE\u63A5\u53CC\u91CD\u68C0\u6D4B", "Gap \u81EA\u52A8\u5206\u7C7B\uFF08\u5B8C\u5168\u7F3A\u53E3/\u90E8\u5206\u7F3A\u53E3/\u5DF2\u8986\u76D6\uFF09", "AI \u81EA\u52A8\u6267\u884C + \u624B\u52A8\u4E0A\u4F20\u652F\u6301"],
    },
    impact: [
      { v: "7", en: "AI Platforms", zh: "AI \u5E73\u53F0" },
      { v: "Real-time", en: "Gap Detection", zh: "\u5B9E\u65F6 Gap \u68C0\u6D4B" },
      { v: "3 types", en: "Gap Classification", zh: "Gap \u5206\u7C7B" },
      { v: "\u2192", en: "Guides Content", zh: "\u6307\u5BFC\u5185\u5BB9\u751F\u4EA7" },
    ],
  },
  {
    id: "zhizao", path: "/zhizao", icon: "\u270D\uFE0F",
    color: "#ffcc02", tag: "Production",
    name: { en: "Content Creator", zh: "\u667A\u9020 Content Creator" },
    sub: { en: "AI-Optimized Content Generation", zh: "AI \u4F18\u5316\u5185\u5BB9\u751F\u6210" },
    desc: {
      en: "Produces GEO-structured content at scale. Direct answers, tables, FAQ format maximize AI citation probability.",
      zh: "\u57FA\u4E8E\u9AD8\u4EF7\u503C\u77ED\u8BED\u6279\u91CF\u751F\u6210 GEO \u7ED3\u6784\u5316\u5185\u5BB9\uFF0C\u6700\u5927\u5316 AI \u5F15\u7528\u6982\u7387\u3002",
    },
    caps: {
      en: ["GEO-first structured output", "Knowledge-base grounded writing", "3hrs to 10min per article", "100+ articles/month capacity"],
      zh: ["GEO \u4F18\u5148\u7ED3\u6784\u5316\u8F93\u51FA", "\u77E5\u8BC6\u5E93\u9A71\u52A8\u5199\u4F5C", "\u5355\u7BC7 3h\u219210min", "\u6708\u4EA7 100+ \u7BC7"],
    },
    impact: [
      { v: "3h\u219210min", en: "Per Article", zh: "\u5355\u7BC7\u65F6\u95F4" },
      { v: "800-3000", en: "Words/Article", zh: "\u6BCF\u7BC7\u5B57\u6570" },
      { v: "100%", en: "GEO Compliance", zh: "GEO \u5408\u89C4" },
      { v: "100+/mo", en: "Output Capacity", zh: "\u6708\u4EA7\u80FD" },
    ],
  },
  {
    id: "zhiyou", path: "/zhiyou", icon: "\u{1F527}",
    color: "#e91e63", tag: "Production",
    name: { en: "Content Optimizer", zh: "\u667A\u4F18 Content Optimizer" },
    sub: { en: "AI Citation Scoring & Optimization", zh: "AI \u5F15\u7528\u8BC4\u5206\u4E0E\u4F18\u5316" },
    desc: {
      en: "5-dimension scoring, auto-rewrite based on gaps, Amazon compliance verification in one pipeline.",
      zh: "5 \u7EF4\u5EA6\u8BC4\u5206\u3001\u57FA\u4E8E\u5DEE\u8DDD\u81EA\u52A8\u91CD\u5199\u3001\u4E9A\u9A6C\u900A\u5408\u89C4\u9A8C\u8BC1\u3002",
    },
    caps: {
      en: ["5-dimension AI citation scoring", "Auto-rewrite on FAIL", "Amazon compliance auto-fix", "Before/after tracking"],
      zh: ["5 \u7EF4\u5EA6 AI \u5F15\u7528\u8BC4\u5206", "\u4E0D\u5408\u683C\u81EA\u52A8\u91CD\u5199", "\u4E9A\u9A6C\u900A\u5408\u89C4\u81EA\u52A8\u4FEE\u590D", "\u524D\u540E\u5BF9\u6BD4\u8FFD\u8E2A"],
    },
    impact: [
      { v: "+25%", en: "Score Uplift", zh: "\u8BC4\u5206\u63D0\u5347" },
      { v: "5 dim", en: "Scoring", zh: "\u8BC4\u5206\u7EF4\u5EA6" },
      { v: "100%", en: "Compliance", zh: "\u5408\u89C4\u7387" },
      { v: "Auto", en: "Score\u2192Fix", zh: "\u8BC4\u5206\u2192\u4FEE\u590D" },
    ],
  },
  {
    id: "zhibu", path: "/zhibu", icon: "\u{1F4E6}",
    color: "#29b6f6", tag: "Production",
    name: { en: "Content Publisher", zh: "\u667A\u5E03 Content Publisher" },
    sub: { en: "Structured JSON Output for CMS", zh: "CMS \u7ED3\u6784\u5316 JSON \u8F93\u51FA" },
    desc: {
      en: "Converts optimized content into LEGO CMS standard JSON, ready for multi-channel publishing.",
      zh: "\u5C06\u4F18\u5316\u5185\u5BB9\u8F6C\u6362\u4E3A LEGO CMS \u6807\u51C6 JSON\uFF0C\u53EF\u76F4\u63A5\u5BF9\u63A5\u53D1\u5E03\u5E73\u53F0\u3002",
    },
    caps: {
      en: ["LEGO CMS JSON format", "Auto metadata population", "Batch processing", "Version tracking"],
      zh: ["LEGO CMS JSON \u683C\u5F0F", "\u5143\u6570\u636E\u81EA\u52A8\u586B\u5145", "\u6279\u91CF\u5904\u7406", "\u7248\u672C\u8FFD\u8E2A"],
    },
    impact: [
      { v: "30\u21922min", en: "Per Article", zh: "\u5355\u7BC7\u65F6\u95F4" },
      { v: "0 errors", en: "Accuracy", zh: "\u51C6\u786E\u7387" },
      { v: "Batch", en: "Processing", zh: "\u6279\u91CF\u5904\u7406" },
      { v: "JSON", en: "CMS-Ready", zh: "CMS \u5C31\u7EEA" },
    ],
  },
  {
    id: "zhichuan", path: "/zhongshu", icon: "\u{1F4E1}",
    color: "#26c6da", tag: "Dev",
    name: { en: "Content Distributor", zh: "\u667A\u4F20 Content Distributor" },
    sub: { en: "Multi-Channel Automated Distribution", zh: "\u591A\u6E20\u9053\u81EA\u52A8\u5206\u53D1" },
    desc: {
      en: "Automates multi-channel content distribution across official website, blog, knowledge center, and third-party platforms.",
      zh: "\u81EA\u52A8\u5316\u591A\u6E20\u9053\u5185\u5BB9\u5206\u53D1\uFF0C\u8986\u76D6\u5B98\u7F51\u3001\u535A\u5BA2\u3001\u77E5\u8BC6\u4E2D\u5FC3\u53CA\u7B2C\u4E09\u65B9\u5E73\u53F0\u3002",
    },
    caps: {
      en: ["One-click multi-channel distribution", "Scheduled publishing with timezone", "A/B content variant management", "Cross-platform workflow automation"],
      zh: ["\u591A\u6E20\u9053\u4E00\u952E\u5206\u53D1", "\u652F\u6301\u65F6\u533A\u7684\u5B9A\u65F6\u53D1\u5E03", "A/B \u5185\u5BB9\u53D8\u4F53\u7BA1\u7406", "\u8DE8\u5E73\u53F0\u53D1\u5E03\u5DE5\u4F5C\u6D41"],
    },
    impact: [
      { v: "Multi", en: "Channels", zh: "\u6E20\u9053\u6570" },
      { v: "Auto", en: "Scheduling", zh: "\u5B9A\u65F6\u53D1\u5E03" },
      { v: "A/B", en: "Variant Testing", zh: "\u53D8\u4F53\u6D4B\u8BD5" },
      { v: "E2E", en: "Integration", zh: "\u5E73\u53F0\u96C6\u6210" },
    ],
  },
  {
    id: "zhixi", path: "/zhixi", icon: "\u{1F4CA}",
    color: "#ab47bc", tag: "Production",
    name: { en: "Performance Analyzer", zh: "\u667A\u6790 Performance Analyzer" },
    sub: { en: "Full-Channel Attribution & Reporting", zh: "\u5168\u6E20\u9053\u5F52\u56E0\u4E0E\u62A5\u8868" },
    desc: {
      en: "Tracks GEO performance with automated reporting, benchmarks against SSR total, quantifies content contribution.",
      zh: "\u5168\u6E20\u9053\u6548\u679C\u8FFD\u8E2A\u4E0E\u5F52\u56E0\u5206\u6790\uFF0C\u81EA\u52A8\u751F\u6210\u62A5\u8868\uFF0C\u4E0E SSR \u5927\u76D8\u5BF9\u6807\u3002",
    },
    caps: {
      en: ["Weekly/Monthly/YTD reports", "AI citation tracking", "Gap identification", "Actionable insights"],
      zh: ["\u5468/\u6708/\u5E74\u5EA6\u62A5\u8868", "AI \u5F15\u7528\u8FFD\u8E2A", "Gap \u8BC6\u522B", "\u53EF\u6267\u884C\u6D1E\u5BDF"],
    },
    impact: [
      { v: "Real-time", en: "Data", zh: "\u6570\u636E" },
      { v: "Input+Output", en: "Full Funnel", zh: "\u5168\u6F0F\u6597" },
      { v: "Actionable", en: "Insights", zh: "\u6D1E\u5BDF" },
      { v: "Validated", en: "Effectiveness", zh: "\u6709\u6548\u6027" },
    ],
  },
  {
    id: "zhongshu", path: "/zhongshu", icon: "\u{1F3AF}",
    color: "#ff6b35", tag: "Dev",
    name: { en: "Workflow Orchestrator", zh: "\u667A\u4E2D\u67A2 Workflow Orchestrator" },
    sub: { en: "End-to-End Pipeline Intelligence", zh: "\u7AEF\u5230\u7AEF\u6D41\u6C34\u7EBF\u667A\u80FD" },
    desc: {
      en: "Central orchestration hub with 7-rule decision engine, auto-generating weekly action plans.",
      zh: "\u5168\u6D41\u7A0B\u7F16\u6392\u4E2D\u5FC3\uFF0C\u5185\u7F6E 7 \u6761\u51B3\u7B56\u89C4\u5219\u5F15\u64CE\uFF0C\u81EA\u52A8\u751F\u6210\u5468\u5EA6\u6267\u884C\u8BA1\u5212\u3002",
    },
    caps: {
      en: ["E2E pipeline orchestration", "7-rule decision engine", "Auto weekly plans", "8hrs/wk saved"],
      zh: ["\u7AEF\u5230\u7AEF\u6D41\u6C34\u7EBF\u7F16\u6392", "7 \u6761\u51B3\u7B56\u89C4\u5219", "\u5468\u5EA6\u81EA\u52A8\u8BA1\u5212", "\u6BCF\u5468\u8282\u7701 8h"],
    },
    impact: [
      { v: "E2E", en: "Automation", zh: "\u81EA\u52A8\u5316" },
      { v: "7 rules", en: "Decision Engine", zh: "\u51B3\u7B56\u5F15\u64CE" },
      { v: "8hrs/wk", en: "Time Saved", zh: "\u8282\u7701\u65F6\u95F4" },
      { v: "Auto", en: "Weekly Plans", zh: "\u5468\u5EA6\u8BA1\u5212" },
    ],
  },
  {
    id: "s3", path: "/zhongshu", icon: "\u{2601}\uFE0F",
    color: "#42a5f5", tag: "Dev",
    name: { en: "S3 Memory Keeper", zh: "S3 Memory Keeper" },
    sub: { en: "Persistent Knowledge Storage Layer", zh: "\u6301\u4E45\u5316\u77E5\u8BC6\u5B58\u50A8\u5C42" },
    desc: {
      en: "AWS S3-based persistent storage serving as the unified data foundation for all Smart Suite modules with version control.",
      zh: "\u57FA\u4E8E AWS S3 \u7684\u6301\u4E45\u5316\u5B58\u50A8\u5C42\uFF0C\u4E3A\u5168\u6A21\u5757\u63D0\u4F9B\u7EDF\u4E00\u6570\u636E\u5E95\u5EA7\uFF0C\u652F\u6301\u7248\u672C\u63A7\u5236\u3002",
    },
    caps: {
      en: ["Unified storage for all modules", "Version-controlled repository", "Cross-module data sync", "Batch archival & retrieval"],
      zh: ["\u5168\u6A21\u5757\u6570\u636E\u7EDF\u4E00\u5B58\u50A8", "\u7248\u672C\u5316\u5185\u5BB9\u4ED3\u5E93", "\u8DE8\u6A21\u5757\u6570\u636E\u540C\u6B65", "\u6279\u6B21\u5F52\u6863\u4E0E\u68C0\u7D22"],
    },
    impact: [
      { v: "\u221E", en: "Scalable", zh: "\u5F39\u6027\u6269\u5C55" },
      { v: "99.99%", en: "Durability", zh: "\u6301\u4E45\u6027" },
      { v: "9 modules", en: "Connected", zh: "\u6A21\u5757\u4E92\u901A" },
      { v: "Versioned", en: "Audit Trail", zh: "\u5BA1\u8BA1\u8FFD\u8E2A" },
    ],
  },
];

const STATS = [
  { value: "9", label: { en: "AI Tools", zh: "AI \u5DE5\u5177" } },
  { value: "7+", label: { en: "AI Search Platforms", zh: "AI \u68C0\u7D22\u5E73\u53F0" } },
  { value: "+65%", label: { en: "YTD YoY Growth", zh: "YTD \u589E\u957F YoY" } },
  { value: "+8,400 bps", label: { en: "vs SSR Benchmark", zh: "Reg Start vs SSR \u5927\u76D8\u9006\u8F6C" } },
];

export default function OverviewPage() {
  const { locale } = useI18nStore();
  const isZh = locale.startsWith("zh");
  const t = (obj: { en: string; zh: string }) => (isZh ? obj.zh : obj.en);
  const tArr = (obj: { en: string[]; zh: string[] }) => (isZh ? obj.zh : obj.en);

  return (
    <div className="space-y-10 max-w-[1100px] pb-16">
      {/* Hero */}
      <section className="text-center py-10">
        {/* Logo - AI/Tech feel with animated effects */}
        <div className="relative inline-block mb-6" style={{ width: "120px", height: "120px" }}>
          {/* Particle dots orbiting */}
          <div className="absolute inset-0 animate-spin" style={{ animationDuration: "20s" }}>
            <div className="absolute w-1.5 h-1.5 rounded-full bg-cyan-400 top-0 left-1/2 -ml-0.5" style={{ boxShadow: "0 0 6px rgba(0,188,212,0.8)" }} />
            <div className="absolute w-1 h-1 rounded-full bg-purple-400 bottom-2 right-2" style={{ boxShadow: "0 0 4px rgba(171,71,188,0.6)" }} />
          </div>
          {/* Outer glow ring */}
          <div
            className="absolute rounded-full animate-pulse"
            style={{
              width: "110px", height: "110px",
              top: "50%", left: "50%",
              marginTop: "-55px", marginLeft: "-55px",
              background: "radial-gradient(circle, rgba(0,188,212,0.08) 0%, transparent 70%)",
            }}
          />
          {/* Spinning outer ring - cyan */}
          <div
            className="absolute rounded-full animate-spin"
            style={{
              width: "100px", height: "100px",
              top: "50%", left: "50%",
              marginTop: "-50px", marginLeft: "-50px",
              border: "1.5px solid transparent",
              borderTopColor: "rgba(0,188,212,0.6)",
              borderRightColor: "rgba(0,188,212,0.2)",
              animationDuration: "6s",
            }}
          />
          {/* Counter-spinning inner ring - purple */}
          <div
            className="absolute rounded-full animate-spin"
            style={{
              width: "108px", height: "108px",
              top: "50%", left: "50%",
              marginTop: "-54px", marginLeft: "-54px",
              border: "1px solid transparent",
              borderBottomColor: "rgba(171,71,188,0.4)",
              borderLeftColor: "rgba(171,71,188,0.15)",
              animationDuration: "10s",
              animationDirection: "reverse",
            }}
          />
          {/* Logo image only - no text overlay */}
          <div
            className="absolute rounded-full z-10 overflow-hidden"
            style={{
              width: "80px", height: "80px",
              top: "50%", left: "50%",
              marginTop: "-40px", marginLeft: "-40px",
              boxShadow: "0 0 24px rgba(0,188,212,0.15), 0 0 48px rgba(171,71,188,0.08)",
            }}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src="/logo.png"
              alt="Smart Suite"
              className="w-full h-full"
            />
          </div>
          {/* Scan line effect */}
          <div
            className="absolute z-20 rounded-full overflow-hidden pointer-events-none"
            style={{
              width: "80px", height: "80px",
              top: "50%", left: "50%",
              marginTop: "-40px", marginLeft: "-40px",
            }}
          >
            <div
              className="absolute w-full h-[2px] left-0 animate-pulse"
              style={{
                top: "50%",
                background: "linear-gradient(90deg, transparent, rgba(0,188,212,0.4), transparent)",
                animationDuration: "3s",
              }}
            />
          </div>
        </div>
        {/* Title */}
        <h1
          className="text-3xl font-extrabold mb-2"
          style={{
            background: "linear-gradient(135deg, #ff6b35, #e91e63, #9c27b0, #2196f3, #00bcd4)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
          }}
        >
          {"\u667A\u7CFB\u5217"} Smart Suite
        </h1>
        <p className="text-sm font-medium text-[var(--accent)] tracking-wide mb-3">
          AI-Native GEO Marketing Operating Model
        </p>
        <p className="text-sm text-[var(--text-secondary)] max-w-2xl mx-auto leading-relaxed">
          Smart Suite unifies GEO insights, content, governance, and measurement into one intelligent operating model—enabling marketing to continuously learn, optimize, and scale.
        </p>
        <div className="flex justify-center gap-10 mt-8">
          {STATS.map((s, i) => (
            <div key={i} className="text-center">
              <div className="text-2xl font-bold text-[var(--accent)]">{s.value}</div>
              <div className="text-xs text-[var(--text-muted)] mt-1">{t(s.label)}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Module Sections */}
      {MODULES.map((mod) => (
        <section
          key={mod.id}
          className="bg-white border border-[var(--border-card)] rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow"
        >
          <div className="grid grid-cols-1 md:grid-cols-[1.2fr_1fr] gap-8">
            <div>
              <div
                className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium border mb-3"
                style={{
                  borderColor: mod.tag === "Dev" ? "#ffa726" : "#067d62",
                  color: mod.tag === "Dev" ? "#ffa726" : "#067d62",
                  background: mod.tag === "Dev" ? "#ffa72610" : "#067d6210",
                }}
              >
                <span className="w-1.5 h-1.5 rounded-full" style={{ background: mod.tag === "Dev" ? "#ffa726" : "#067d62" }} />
                {mod.tag === "Dev" ? (isZh ? "\u5F00\u53D1\u4E2D" : "In Development") : "Production"}
              </div>
              <h2 className="text-xl font-bold mb-1" style={{ color: mod.color }}>
                {t(mod.name)}
              </h2>
              <p className="text-sm italic text-[var(--text-muted)] mb-3">{t(mod.sub)}</p>
              <p className="text-sm text-[var(--text-secondary)] leading-relaxed mb-4">{t(mod.desc)}</p>
              <Link
                href={mod.path}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-[var(--text-primary)] bg-[var(--bg-surface)] border border-[var(--border-card)] hover:border-[var(--accent)] hover:text-[var(--accent)] transition-colors"
              >
                {"\u{1F680}"} {isZh ? "\u542F\u52A8\u5DE5\u5177" : "Launch Tool"}
              </Link>
              <div className="mt-5">
                <h4 className="text-[10px] uppercase tracking-widest text-[var(--text-muted)] font-semibold mb-2">
                  {isZh ? "\u6838\u5FC3\u80FD\u529B" : "CORE CAPABILITIES"}
                </h4>
                {tArr(mod.caps).map((cap, i) => (
                  <div key={i} className="flex items-start gap-2 text-sm text-[var(--text-secondary)] mb-1.5">
                    <span className="text-[var(--accent)] font-bold shrink-0">+</span>
                    {cap}
                  </div>
                ))}
              </div>
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-widest text-[var(--text-muted)] font-semibold mb-3">
                BUSINESS IMPACT
              </p>
              <div className="grid grid-cols-2 gap-3">
                {mod.impact.map((item, i) => (
                  <div key={i} className="rounded-xl border border-[var(--border-card)] p-4 bg-[var(--bg-surface)]">
                    <div className="text-lg font-bold" style={{ color: mod.color }}>{item.v}</div>
                    <div className="text-xs text-[var(--text-muted)] mt-1">{t(item)}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>
      ))}

      <footer className="text-center text-xs text-[var(--text-muted)] py-6 border-t border-[var(--border-card)]">
        Smart Suite &ndash; AI-Powered GEO Content Intelligence Platform &middot; Built by GEO Team &middot; Phase I
      </footer>
    </div>
  );
}
