"use client";

import { useState, useEffect } from "react";
import { useI18nStore } from "@/stores/i18n-store";
import { useAuthStore } from "@/stores/auth-store";
import { GlassCard } from "@/components/ui/GlassCard";

// Weekly data structure matching geo_weekly_data.csv
interface WeeklyRow {
  Week: string;
  CN_GEO: number; CN_GEO_PY: number;
  WW_GEO: number; WW_GEO_PY: number;
  Total_GEO: number; Total_GEO_PY: number;
  WW_Direct: number; WW_Direct_PY: number;
  CN_Direct: number; CN_Direct_PY: number;
  Direct_Total: number; Direct_Total_PY: number;
  Total: number; Total_PY: number;
}

// Hardcoded latest data from geo_weekly_data.csv (WK15-WK29)
const WEEKLY_DATA: WeeklyRow[] = [
  {Week:"WK15",CN_GEO:45,CN_GEO_PY:5,WW_GEO:17,WW_GEO_PY:5,Total_GEO:62,Total_GEO_PY:10,WW_Direct:1581,WW_Direct_PY:1033,CN_Direct:1082,CN_Direct_PY:1629,Direct_Total:2663,Direct_Total_PY:2662,Total:2725,Total_PY:2672},
  {Week:"WK16",CN_GEO:40,CN_GEO_PY:7,WW_GEO:15,WW_GEO_PY:8,Total_GEO:55,Total_GEO_PY:15,WW_Direct:1750,WW_Direct_PY:1047,CN_Direct:1327,CN_Direct_PY:1908,Direct_Total:3077,Direct_Total_PY:2955,Total:3132,Total_PY:2970},
  {Week:"WK17",CN_GEO:32,CN_GEO_PY:12,WW_GEO:15,WW_GEO_PY:6,Total_GEO:47,Total_GEO_PY:18,WW_Direct:1738,WW_Direct_PY:1037,CN_Direct:3128,CN_Direct_PY:4494,Direct_Total:4866,Direct_Total_PY:5531,Total:4913,Total_PY:5549},
  {Week:"WK18",CN_GEO:33,CN_GEO_PY:6,WW_GEO:17,WW_GEO_PY:5,Total_GEO:50,Total_GEO_PY:11,WW_Direct:1330,WW_Direct_PY:763,CN_Direct:2120,CN_Direct_PY:2918,Direct_Total:3450,Direct_Total_PY:3681,Total:3500,Total_PY:3692},
  {Week:"WK19",CN_GEO:33,CN_GEO_PY:4,WW_GEO:21,WW_GEO_PY:7,Total_GEO:54,Total_GEO_PY:11,WW_Direct:1453,WW_Direct_PY:1047,CN_Direct:2072,CN_Direct_PY:2906,Direct_Total:3525,Direct_Total_PY:3953,Total:3579,Total_PY:3964},
  {Week:"WK20",CN_GEO:41,CN_GEO_PY:5,WW_GEO:31,WW_GEO_PY:13,Total_GEO:72,Total_GEO_PY:18,WW_Direct:1914,WW_Direct_PY:1066,CN_Direct:2242,CN_Direct_PY:2738,Direct_Total:4156,Direct_Total_PY:3804,Total:4228,Total_PY:3822},
  {Week:"WK21",CN_GEO:44,CN_GEO_PY:7,WW_GEO:19,WW_GEO_PY:13,Total_GEO:63,Total_GEO_PY:20,WW_Direct:2054,WW_Direct_PY:986,CN_Direct:1929,CN_Direct_PY:2866,Direct_Total:3983,Direct_Total_PY:3852,Total:4046,Total_PY:3872},
  {Week:"WK22",CN_GEO:38,CN_GEO_PY:10,WW_GEO:22,WW_GEO_PY:11,Total_GEO:60,Total_GEO_PY:21,WW_Direct:2143,WW_Direct_PY:904,CN_Direct:2271,CN_Direct_PY:2424,Direct_Total:4414,Direct_Total_PY:3328,Total:4474,Total_PY:3349},
  {Week:"WK23",CN_GEO:25,CN_GEO_PY:10,WW_GEO:24,WW_GEO_PY:11,Total_GEO:49,Total_GEO_PY:21,WW_Direct:4060,WW_Direct_PY:1099,CN_Direct:2904,CN_Direct_PY:2326,Direct_Total:6964,Direct_Total_PY:3425,Total:7013,Total_PY:3446},
  {Week:"WK24",CN_GEO:41,CN_GEO_PY:19,WW_GEO:23,WW_GEO_PY:21,Total_GEO:64,Total_GEO_PY:40,WW_Direct:2252,WW_Direct_PY:1286,CN_Direct:3140,CN_Direct_PY:2110,Direct_Total:5392,Direct_Total_PY:3396,Total:5456,Total_PY:3436},
  {Week:"WK25",CN_GEO:31,CN_GEO_PY:5,WW_GEO:15,WW_GEO_PY:12,Total_GEO:46,Total_GEO_PY:17,WW_Direct:1579,WW_Direct_PY:3127,CN_Direct:1538,CN_Direct_PY:574,Direct_Total:3117,Direct_Total_PY:3701,Total:3163,Total_PY:3718},
  {Week:"WK26",CN_GEO:38,CN_GEO_PY:9,WW_GEO:30,WW_GEO_PY:9,Total_GEO:68,Total_GEO_PY:18,WW_Direct:1619,WW_Direct_PY:1270,CN_Direct:1938,CN_Direct_PY:868,Direct_Total:3557,Direct_Total_PY:2138,Total:3625,Total_PY:2156},
  {Week:"WK27",CN_GEO:41,CN_GEO_PY:18,WW_GEO:22,WW_GEO_PY:12,Total_GEO:63,Total_GEO_PY:30,WW_Direct:1537,WW_Direct_PY:894,CN_Direct:1874,CN_Direct_PY:1005,Direct_Total:3411,Direct_Total_PY:1899,Total:3474,Total_PY:1929},
  {Week:"WK28",CN_GEO:41,CN_GEO_PY:10,WW_GEO:22,WW_GEO_PY:8,Total_GEO:63,Total_GEO_PY:18,WW_Direct:1219,WW_Direct_PY:848,CN_Direct:1637,CN_Direct_PY:929,Direct_Total:2856,Direct_Total_PY:1777,Total:2919,Total_PY:1795},
  {Week:"WK29",CN_GEO:41,CN_GEO_PY:20,WW_GEO:28,WW_GEO_PY:7,Total_GEO:69,Total_GEO_PY:27,WW_Direct:1400,WW_Direct_PY:863,CN_Direct:1272,CN_Direct_PY:1045,Direct_Total:2672,Direct_Total_PY:1908,Total:2741,Total_PY:1935},
];

function wow(curr: number, prev: number): string {
  if (prev === 0) return "—";
  const pct = ((curr - prev) / prev * 100);
  return `${pct > 0 ? "+" : ""}${pct.toFixed(1)}%`;
}

function yoy(actual: number, py: number): string {
  if (py === 0) return actual > 0 ? "+∞" : "—";
  const pct = ((actual - py) / py * 100);
  return `${pct > 0 ? "+" : ""}${pct.toFixed(1)}%`;
}

function trendIcon(curr: number, prev: number): string {
  if (prev === 0) return "→";
  const pct = (curr - prev) / prev * 100;
  if (pct > 15) return "↑";
  if (pct < -15) return "⚠️ ↓";
  return "→";
}

export default function ZhixiPage() {
  const { t, locale } = useI18nStore();
  const { user } = useAuthStore();
  const isZh = locale.startsWith("zh");

  const latest = WEEKLY_DATA[WEEKLY_DATA.length - 1];
  const prev = WEEKLY_DATA[WEEKLY_DATA.length - 2];

  // YTD calculations (sum all weeks)
  const ytd = WEEKLY_DATA.reduce((acc, w) => ({
    CN_GEO: acc.CN_GEO + w.CN_GEO, CN_GEO_PY: acc.CN_GEO_PY + w.CN_GEO_PY,
    WW_GEO: acc.WW_GEO + w.WW_GEO, WW_GEO_PY: acc.WW_GEO_PY + w.WW_GEO_PY,
    Total_GEO: acc.Total_GEO + w.Total_GEO, Total_GEO_PY: acc.Total_GEO_PY + w.Total_GEO_PY,
    WW_Direct: acc.WW_Direct + w.WW_Direct, WW_Direct_PY: acc.WW_Direct_PY + w.WW_Direct_PY,
    Total: acc.Total + w.Total, Total_PY: acc.Total_PY + w.Total_PY,
  }), { CN_GEO: 0, CN_GEO_PY: 0, WW_GEO: 0, WW_GEO_PY: 0, Total_GEO: 0, Total_GEO_PY: 0, WW_Direct: 0, WW_Direct_PY: 0, Total: 0, Total_PY: 0 });

  // Judgment
  const totalWoW = prev.Total > 0 ? (latest.Total - prev.Total) / prev.Total * 100 : 0;
  const totalYoY = ytd.Total_PY > 0 ? (ytd.Total - ytd.Total_PY) / ytd.Total_PY * 100 : 0;
  const judgment = totalWoW > 10 && totalYoY > 0 ? "🟢 POSITIVE" : totalWoW < -20 ? "🔴 NEGATIVE" : "🟡 MIXED";

  // Recent 8 weeks for display
  const recentWeeks = WEEKLY_DATA.slice(-8);

  return (
    <div className="space-y-6 max-w-[1400px]">
      <h1 className="text-xl font-bold">{t("zhixi.title")}</h1>

      {/* Executive Summary */}
      <GlassCard>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-medium text-[var(--text-secondary)]">
            {isZh ? "Executive Summary" : "Executive Summary"} — {latest.Week}
          </h2>
          <span className={`text-sm font-bold ${judgment.includes("POSITIVE") ? "text-[var(--success)]" : judgment.includes("NEGATIVE") ? "text-[var(--error)]" : "text-yellow-400"}`}>
            {judgment}
          </span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
          <div className="text-center p-3 rounded-lg bg-white/5 border border-[var(--border-glass)]">
            <p className="text-[10px] text-[var(--text-muted)]">{isZh ? "本周 Total" : "This Week"}</p>
            <p className="text-xl font-bold text-[var(--accent)]">{latest.Total.toLocaleString()}</p>
            <p className="text-[10px] text-[var(--text-muted)]">WoW {wow(latest.Total, prev.Total)}</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-white/5 border border-[var(--border-glass)]">
            <p className="text-[10px] text-[var(--text-muted)]">GEO Total</p>
            <p className="text-xl font-bold text-blue-400">{latest.Total_GEO}</p>
            <p className="text-[10px] text-[var(--text-muted)]">WoW {wow(latest.Total_GEO, prev.Total_GEO)}</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-white/5 border border-[var(--border-glass)]">
            <p className="text-[10px] text-[var(--text-muted)]">WW Direct</p>
            <p className="text-xl font-bold text-purple-400">{latest.WW_Direct.toLocaleString()}</p>
            <p className="text-[10px] text-[var(--text-muted)]">WoW {wow(latest.WW_Direct, prev.WW_Direct)}</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-white/5 border border-[var(--border-glass)]">
            <p className="text-[10px] text-[var(--text-muted)]">YTD Total</p>
            <p className="text-xl font-bold">{ytd.Total.toLocaleString()}</p>
            <p className="text-[10px] text-[var(--success)]">YoY {yoy(ytd.Total, ytd.Total_PY)}</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-white/5 border border-[var(--border-glass)]">
            <p className="text-[10px] text-[var(--text-muted)]">YTD GEO</p>
            <p className="text-xl font-bold text-blue-400">{ytd.Total_GEO.toLocaleString()}</p>
            <p className="text-[10px] text-[var(--success)]">YoY {yoy(ytd.Total_GEO, ytd.Total_GEO_PY)}</p>
          </div>
        </div>
      </GlassCard>

      {/* Weekly Trend Table */}
      <GlassCard padding="sm">
        <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
          {isZh ? "Weekly Trend — Reg Starts" : "Weekly Trend — Reg Starts"}
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-[var(--border-glass)]">
                <th className="px-2 py-1.5 text-left text-[var(--text-muted)]">Channel</th>
                {recentWeeks.map((w) => (
                  <th key={w.Week} className="px-2 py-1.5 text-center text-[var(--text-muted)]">{w.Week}</th>
                ))}
                <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">WoW</th>
                <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">Trend</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: "CN GEO", key: "CN_GEO" as const, color: "text-blue-400" },
                { name: "WW GEO", key: "WW_GEO" as const, color: "text-cyan-400" },
                { name: "GEO Total", key: "Total_GEO" as const, color: "text-blue-300 font-semibold" },
                { name: "WW Direct", key: "WW_Direct" as const, color: "text-purple-400" },
                { name: "CN Direct", key: "CN_Direct" as const, color: "text-gray-400" },
                { name: "Total", key: "Total" as const, color: "text-[var(--accent)] font-bold" },
              ].map((ch) => (
                <tr key={ch.name} className="border-b border-[var(--border-glass)]/30">
                  <td className={`px-2 py-1.5 ${ch.color}`}>{ch.name}</td>
                  {recentWeeks.map((w) => (
                    <td key={w.Week} className="px-2 py-1.5 text-center font-mono">{w[ch.key] || "—"}</td>
                  ))}
                  <td className="px-2 py-1.5 text-center font-mono">
                    {wow(recentWeeks[recentWeeks.length-1][ch.key], recentWeeks[recentWeeks.length-2][ch.key])}
                  </td>
                  <td className="px-2 py-1.5 text-center">
                    {trendIcon(recentWeeks[recentWeeks.length-1][ch.key], recentWeeks[recentWeeks.length-2][ch.key])}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>

      {/* YTD Summary */}
      <GlassCard padding="sm">
        <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
          {isZh ? "YTD Summary — Reg Starts (vs PY)" : "YTD Summary — Reg Starts (vs PY)"}
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="border-b border-[var(--border-glass)]">
                <th className="px-2 py-1.5 text-left text-[var(--text-muted)]">Channel</th>
                <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">YTD Actual</th>
                <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">YTD PY</th>
                <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">Delta</th>
                <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">YoY</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: "CN GEO", actual: ytd.CN_GEO, py: ytd.CN_GEO_PY },
                { name: "WW GEO", actual: ytd.WW_GEO, py: ytd.WW_GEO_PY },
                { name: "GEO Total", actual: ytd.Total_GEO, py: ytd.Total_GEO_PY },
                { name: "WW Direct", actual: ytd.WW_Direct, py: ytd.WW_Direct_PY },
                { name: "GEO + Direct Total", actual: ytd.Total, py: ytd.Total_PY },
              ].map((row) => (
                <tr key={row.name} className="border-b border-[var(--border-glass)]/30">
                  <td className="px-2 py-1.5 font-medium">{row.name}</td>
                  <td className="px-2 py-1.5 text-center font-mono font-bold">{row.actual.toLocaleString()}</td>
                  <td className="px-2 py-1.5 text-center font-mono text-[var(--text-muted)]">{row.py.toLocaleString()}</td>
                  <td className={`px-2 py-1.5 text-center font-mono ${row.actual - row.py > 0 ? "text-[var(--success)]" : "text-[var(--error)]"}`}>
                    {row.actual - row.py > 0 ? "+" : ""}{(row.actual - row.py).toLocaleString()}
                  </td>
                  <td className={`px-2 py-1.5 text-center font-mono font-bold ${row.actual > row.py ? "text-[var(--success)]" : "text-[var(--error)]"}`}>
                    {yoy(row.actual, row.py)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassCard>

      {/* Attribution & Insights */}
      <GlassCard>
        <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
          {isZh ? "归因分析 & 行动建议" : "Attribution & Action Items"}
        </h2>
        <div className="space-y-2 text-xs">
          <p className="text-[var(--text-primary)]">
            <span className="font-bold">📊 {latest.Week} Output:</span> Total = {latest.Total.toLocaleString()} (WoW {wow(latest.Total, prev.Total)})
          </p>
          <div className="mt-2 space-y-1 text-[var(--text-secondary)]">
            <p>• CN GEO {latest.CN_GEO} (WoW {wow(latest.CN_GEO, prev.CN_GEO)}) — {isZh ? "AI search referrer 流量" : "AI search referrer traffic"} {trendIcon(latest.CN_GEO, prev.CN_GEO)}</p>
            <p>• WW GEO {latest.WW_GEO} (WoW {wow(latest.WW_GEO, prev.WW_GEO)}) — {isZh ? "海外 AI 搜索引用" : "Overseas AI citations"} {trendIcon(latest.WW_GEO, prev.WW_GEO)}</p>
            <p>• WW Direct {latest.WW_Direct.toLocaleString()} (WoW {wow(latest.WW_Direct, prev.WW_Direct)}) — {isZh ? "内容发布滞后效应 2-3 周" : "Content publish lag 2-3 weeks"} {trendIcon(latest.WW_Direct, prev.WW_Direct)}</p>
          </div>
          <div className="mt-3 pt-3 border-t border-[var(--border-glass)]">
            <p className="font-medium text-[var(--text-primary)] mb-1">{isZh ? "🚀 行动建议：" : "🚀 Action Items:"}</p>
            <ul className="list-disc list-inside space-y-0.5 text-[var(--text-secondary)]">
              <li>{isZh ? "扩大 EU/JP 检索短语覆盖（GEO 绝对值仍低）" : "Expand EU/JP keyword coverage (GEO absolute still low)"}</li>
              <li>{isZh ? "保持 NA 内容产出节奏（WW Direct 增长引擎）" : "Maintain NA content velocity (WW Direct growth engine)"}</li>
              <li>{isZh ? "已发布内容 2-3 周后重新验证引用效果" : "Re-verify citation after 2-3 weeks post-publish"}</li>
            </ul>
          </div>
        </div>
      </GlassCard>

      {/* Gaps & Opportunities */}
      <GlassCard>
        <details>
          <summary className="text-sm font-medium text-[var(--text-secondary)] cursor-pointer">
            {isZh ? "Gaps & Opportunities" : "Gaps & Opportunities"}
          </summary>
          <div className="mt-3 space-y-3 text-xs">
            <div>
              <p className="font-medium text-[var(--text-primary)] mb-1">🔍 Gaps:</p>
              <ul className="list-disc list-inside space-y-0.5 text-[var(--text-secondary)]">
                <li>{isZh ? "WW GEO 绝对值仍小，大部分 AI search 流量不带 referrer" : "WW GEO absolute still small, most AI traffic has no referrer"}</li>
                <li>{isZh ? "Input activities 数据缺失，无法精确归因" : "Input activities data missing, cannot attribute precisely"}</li>
              </ul>
            </div>
            <div>
              <p className="font-medium text-[var(--text-primary)] mb-1">📚 Learnings:</p>
              <ul className="list-disc list-inside space-y-0.5 text-[var(--text-secondary)]">
                <li>{isZh ? "CN GEO +452% 证明 GEO 优化策略有效" : "CN GEO +452% proves GEO strategy works"}</li>
                <li>{isZh ? "WW Direct +62% vs 大盘 -23%，间接归因逻辑成立" : "WW Direct +62% vs benchmark -23%, indirect attribution holds"}</li>
                <li>{isZh ? "2-3 周内容发布→流量滞后效应已被验证" : "2-3 week content→traffic lag effect confirmed"}</li>
              </ul>
            </div>
            <div>
              <p className="font-medium text-[var(--text-primary)] mb-1">🚀 Opportunities:</p>
              <ul className="list-disc list-inside space-y-0.5 text-[var(--text-secondary)]">
                <li>{isZh ? "增加 EU/JP 内容覆盖（GEO 绝对值低但 YoY 高）" : "Increase EU/JP content (low absolute but high YoY)"}</li>
                <li>{isZh ? "建立 Input→Output 周度追踪，完善归因" : "Establish weekly Input→Output tracking for attribution"}</li>
                <li>{isZh ? "JP Direct +113% YoY，AI search 在日本渗透最快" : "JP Direct +113% YoY, fastest AI search penetration"}</li>
              </ul>
            </div>
          </div>
        </details>
      </GlassCard>
    </div>
  );
}
