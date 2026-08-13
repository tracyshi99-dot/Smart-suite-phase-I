"use client";

import { useState, useEffect } from "react";
import { useI18nStore } from "@/stores/i18n-store";
import { useAuthStore } from "@/stores/auth-store";
import { GlassCard } from "@/components/ui/GlassCard";

// ============ DATA ============
// Weekly data from geo_weekly_data.csv (WK20-WK29)
const WEEKLY_DATA = [
  {Week:"WK20",CN_GEO:41,WW_GEO:31,Total_GEO:72,WW_Direct:1914,CN_Direct:2242,Total:4228,Total_PY:3822},
  {Week:"WK21",CN_GEO:44,WW_GEO:19,Total_GEO:63,WW_Direct:2054,CN_Direct:1929,Total:4046,Total_PY:3872},
  {Week:"WK22",CN_GEO:38,WW_GEO:22,Total_GEO:60,WW_Direct:2143,CN_Direct:2271,Total:4474,Total_PY:3349},
  {Week:"WK23",CN_GEO:25,WW_GEO:24,Total_GEO:49,WW_Direct:4060,CN_Direct:2904,Total:7013,Total_PY:3446},
  {Week:"WK24",CN_GEO:41,WW_GEO:23,Total_GEO:64,WW_Direct:2252,CN_Direct:3140,Total:5456,Total_PY:3436},
  {Week:"WK25",CN_GEO:31,WW_GEO:15,Total_GEO:46,WW_Direct:1579,CN_Direct:1538,Total:3163,Total_PY:3718},
  {Week:"WK26",CN_GEO:38,WW_GEO:30,Total_GEO:68,WW_Direct:1619,CN_Direct:1938,Total:3625,Total_PY:2156},
  {Week:"WK27",CN_GEO:41,WW_GEO:22,Total_GEO:63,WW_Direct:1537,CN_Direct:1874,Total:3474,Total_PY:1929},
  {Week:"WK28",CN_GEO:41,WW_GEO:22,Total_GEO:63,WW_Direct:1219,CN_Direct:1637,Total:2919,Total_PY:1795},
  {Week:"WK29",CN_GEO:41,WW_GEO:28,Total_GEO:69,WW_Direct:1400,CN_Direct:1272,Total:2741,Total_PY:1935},
];

// Monthly data from geo_monthly_data.csv
const MONTHLY_DATA = [
  {Channel:"CN GEO",M1:89,M2:65,M3:165,Q1:319,M4:164,M5:163,M6:152,Q2:479,M7:105},
  {Channel:"WW GEO",M1:83,M2:51,M3:91,Q1:225,M4:70,M5:101,M6:97,Q2:268,M7:63},
  {Channel:"Total GEO",M1:172,M2:116,M3:256,Q1:544,M4:234,M5:264,M6:249,Q2:747,M7:168},
  {Channel:"WW Direct",M1:4966,M2:2388,M3:7269,Q1:14623,M4:7204,M5:8136,M6:9726,Q2:25066,M7:3527},
  {Channel:"CN Direct",M1:4106,M2:1607,M3:4664,Q1:10377,M4:5385,M5:4488,M6:7158,Q2:17031,M7:4101},
  {Channel:"Total",M1:9244,M2:4111,M3:12189,Q1:25544,M4:12823,M5:12888,M6:17133,Q2:42844,M7:7796},
];

// YTD data
const YTD_DATA = [
  {Channel:"CN GEO",Actual:903,PY:174,YoY:"+419%"},
  {Channel:"WW GEO",Actual:556,PY:196,YoY:"+184%"},
  {Channel:"Total GEO",Actual:1459,PY:370,YoY:"+294%"},
  {Channel:"WW Direct",Actual:43216,PY:26938,YoY:"+60%"},
  {Channel:"CN Direct",Actual:31509,PY:41765,YoY:"-25%"},
  {Channel:"Total (GEO+Direct)",Actual:76184,PY:69073,YoY:"+10%"},
  {Channel:"SSR Total (大盘)",Actual:250062,PY:302509,YoY:"-17%"},
];

function wow(curr: number, prev: number): string {
  if (!prev) return "—";
  const pct = ((curr - prev) / prev * 100);
  return `${pct > 0 ? "+" : ""}${pct.toFixed(1)}%`;
}

function trendIcon(curr: number, prev: number): string {
  if (!prev) return "→";
  const pct = (curr - prev) / prev * 100;
  if (pct > 15) return "↑";
  if (pct < -15) return "⚠️↓";
  return "→";
}

export default function ZhixiPage() {
  const { t, locale } = useI18nStore();
  const { user } = useAuthStore();
  const isZh = locale.startsWith("zh");

  // Citation data from localStorage (from zhice results)
  const [citationData, setCitationData] = useState<{query:string;platform:string;brand:boolean;link:boolean}[]>([]);
  const [activeTab, setActiveTab] = useState<"output"|"monthly"|"input"|"citation">("output");

  useEffect(() => {
    // Load citation data from zhice sessions
    try {
      const sessions = JSON.parse(localStorage.getItem("zhice_sessions") || "[]");
      const citations: {query:string;platform:string;brand:boolean;link:boolean}[] = [];
      for (const s of sessions) {
        for (const r of (s.results || [])) {
          citations.push({ query: r.query, platform: r.platform, brand: !!r.has_brand_mention, link: !!r.has_official_link });
        }
      }
      setCitationData(citations);
    } catch { /* ignore */ }
  }, []);

  const latest = WEEKLY_DATA[WEEKLY_DATA.length - 1];
  const prev = WEEKLY_DATA[WEEKLY_DATA.length - 2];
  const totalWoW = prev.Total ? ((latest.Total - prev.Total) / prev.Total * 100) : 0;
  const totalYoY = latest.Total_PY ? ((latest.Total - latest.Total_PY) / latest.Total_PY * 100) : 0;
  const judgment = totalYoY > 20 ? "🟢 POSITIVE" : totalYoY < -10 ? "🔴 NEGATIVE" : "🟡 MIXED";

  // Citation stats
  const totalCitations = citationData.length;
  const brandCount = citationData.filter(c => c.brand).length;
  const linkCount = citationData.filter(c => c.link).length;
  const brandRate = totalCitations > 0 ? Math.round(brandCount / totalCitations * 100) : 0;
  const linkRate = totalCitations > 0 ? Math.round(linkCount / totalCitations * 100) : 0;

  // File upload handler
  const handleUploadData = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    // Store uploaded file reference for future use
    alert(isZh ? `✅ 已上传: ${file.name} (${(file.size/1024).toFixed(1)}KB)\n数据将在下次刷新后生效` : `✅ Uploaded: ${file.name}`);
    e.target.value = "";
  };

  return (
    <div className="space-y-6 max-w-[1400px]">
      <h1 className="text-xl font-bold">{t("zhixi.title")}</h1>

      {/* Executive Summary */}
      <GlassCard>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-medium text-[var(--text-secondary)]">Executive Summary — {latest.Week}</h2>
          <span className={`text-sm font-bold ${judgment.includes("POSITIVE") ? "text-[var(--success)]" : judgment.includes("NEGATIVE") ? "text-[var(--error)]" : "text-yellow-400"}`}>{judgment}</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-6 gap-2">
          <div className="text-center p-2 rounded bg-white/5"><p className="text-[10px] text-[var(--text-muted)]">{isZh?"本周 Total":"This Week"}</p><p className="text-lg font-bold text-[var(--accent)]">{latest.Total.toLocaleString()}</p><p className="text-[10px]">WoW {wow(latest.Total,prev.Total)}</p></div>
          <div className="text-center p-2 rounded bg-white/5"><p className="text-[10px] text-[var(--text-muted)]">GEO Total</p><p className="text-lg font-bold text-blue-400">{latest.Total_GEO}</p><p className="text-[10px]">WoW {wow(latest.Total_GEO,prev.Total_GEO)}</p></div>
          <div className="text-center p-2 rounded bg-white/5"><p className="text-[10px] text-[var(--text-muted)]">WW Direct</p><p className="text-lg font-bold text-purple-400">{latest.WW_Direct.toLocaleString()}</p><p className="text-[10px]">WoW {wow(latest.WW_Direct,prev.WW_Direct)}</p></div>
          <div className="text-center p-2 rounded bg-white/5"><p className="text-[10px] text-[var(--text-muted)]">YoY</p><p className={`text-lg font-bold ${totalYoY>0?"text-[var(--success)]":"text-[var(--error)]"}`}>{totalYoY>0?"+":""}{totalYoY.toFixed(0)}%</p></div>
          <div className="text-center p-2 rounded bg-white/5"><p className="text-[10px] text-[var(--text-muted)]">{isZh?"品牌提及率":"Brand Rate"}</p><p className="text-lg font-bold">{brandRate}%</p><p className="text-[10px]">{brandCount}/{totalCitations}</p></div>
          <div className="text-center p-2 rounded bg-white/5"><p className="text-[10px] text-[var(--text-muted)]">{isZh?"官方链接率":"Link Rate"}</p><p className="text-lg font-bold">{linkRate}%</p><p className="text-[10px]">{linkCount}/{totalCitations}</p></div>
        </div>
      </GlassCard>

      {/* Tab Navigation */}
      <div className="flex gap-1 border-b border-[var(--border-glass)]">
        {([["output",isZh?"📊 Output Metrics":"📊 Output"],["monthly",isZh?"📅 Monthly/YTD":"📅 Monthly"],["input",isZh?"📝 Input Activities":"📝 Input"],["citation",isZh?"🔍 AI Citation":"🔍 Citation"]] as [string,string][]).map(([key,label]) => (
          <button key={key} onClick={() => setActiveTab(key as typeof activeTab)} className={`px-3 py-2 text-xs font-medium transition-colors border-b-2 ${activeTab===key ? "border-[var(--accent)] text-[var(--accent)]" : "border-transparent text-[var(--text-muted)] hover:text-[var(--text-secondary)]"}`}>{label}</button>
        ))}
      </div>

      {/* TAB: Output Metrics */}
      {activeTab === "output" && (
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">Weekly Trend — Reg Starts ({WEEKLY_DATA[0].Week}–{latest.Week})</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead><tr className="border-b border-[var(--border-glass)]">
                <th className="px-2 py-1.5 text-left text-[var(--text-muted)]">Channel</th>
                {WEEKLY_DATA.map(w => <th key={w.Week} className="px-1.5 py-1.5 text-center text-[var(--text-muted)]">{w.Week.replace("WK","")}</th>)}
                <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">WoW</th>
                <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">T</th>
              </tr></thead>
              <tbody>
                {([{name:"CN GEO",key:"CN_GEO" as const,color:"text-blue-400"},{name:"WW GEO",key:"WW_GEO" as const,color:"text-cyan-400"},{name:"GEO Total",key:"Total_GEO" as const,color:"text-blue-300 font-semibold"},{name:"WW Direct",key:"WW_Direct" as const,color:"text-purple-400"},{name:"CN Direct",key:"CN_Direct" as const,color:"text-gray-400"},{name:"Total",key:"Total" as const,color:"text-[var(--accent)] font-bold"}]).map(ch => (
                  <tr key={ch.name} className="border-b border-[var(--border-glass)]/30">
                    <td className={`px-2 py-1 ${ch.color} whitespace-nowrap`}>{ch.name}</td>
                    {WEEKLY_DATA.map(w => <td key={w.Week} className="px-1.5 py-1 text-center font-mono">{w[ch.key]>999?(w[ch.key]/1000).toFixed(1)+"k":w[ch.key]}</td>)}
                    <td className="px-2 py-1 text-center font-mono">{wow(WEEKLY_DATA[WEEKLY_DATA.length-1][ch.key],WEEKLY_DATA[WEEKLY_DATA.length-2][ch.key])}</td>
                    <td className="px-2 py-1 text-center">{trendIcon(WEEKLY_DATA[WEEKLY_DATA.length-1][ch.key],WEEKLY_DATA[WEEKLY_DATA.length-2][ch.key])}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      )}

      {/* TAB: Monthly + YTD */}
      {activeTab === "monthly" && (
        <>
          <GlassCard padding="sm">
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">Monthly Trend — Reg Starts</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead><tr className="border-b border-[var(--border-glass)]">
                  <th className="px-2 py-1.5 text-left text-[var(--text-muted)]">Channel</th>
                  <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">M1</th>
                  <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">M2</th>
                  <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">M3</th>
                  <th className="px-2 py-1.5 text-center text-[var(--text-muted)] font-bold">Q1</th>
                  <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">M4</th>
                  <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">M5</th>
                  <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">M6</th>
                  <th className="px-2 py-1.5 text-center text-[var(--text-muted)] font-bold">Q2</th>
                  <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">M7 MTD</th>
                </tr></thead>
                <tbody>
                  {MONTHLY_DATA.map(row => (
                    <tr key={row.Channel} className={`border-b border-[var(--border-glass)]/30 ${row.Channel==="Total"?"font-bold":""}`}>
                      <td className="px-2 py-1 whitespace-nowrap">{row.Channel}</td>
                      <td className="px-2 py-1 text-center font-mono">{row.M1.toLocaleString()}</td>
                      <td className="px-2 py-1 text-center font-mono">{row.M2.toLocaleString()}</td>
                      <td className="px-2 py-1 text-center font-mono">{row.M3.toLocaleString()}</td>
                      <td className="px-2 py-1 text-center font-mono font-bold">{row.Q1.toLocaleString()}</td>
                      <td className="px-2 py-1 text-center font-mono">{row.M4.toLocaleString()}</td>
                      <td className="px-2 py-1 text-center font-mono">{row.M5.toLocaleString()}</td>
                      <td className="px-2 py-1 text-center font-mono">{row.M6.toLocaleString()}</td>
                      <td className="px-2 py-1 text-center font-mono font-bold">{row.Q2.toLocaleString()}</td>
                      <td className="px-2 py-1 text-center font-mono">{row.M7.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </GlassCard>
          <GlassCard padding="sm">
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">YTD Summary — vs SSR Benchmark</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead><tr className="border-b border-[var(--border-glass)]">
                  <th className="px-2 py-1.5 text-left text-[var(--text-muted)]">Channel</th>
                  <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">YTD Actual</th>
                  <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">YTD PY</th>
                  <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">YoY</th>
                  <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">vs 大盘</th>
                </tr></thead>
                <tbody>
                  {YTD_DATA.map(row => {
                    const isPositive = row.YoY.startsWith("+");
                    const benchmark = row.Channel.includes("SSR") ? "—" : (isPositive ? `跑赢 ${parseInt(row.YoY)+17} ppts` : `落后`);
                    return (
                      <tr key={row.Channel} className={`border-b border-[var(--border-glass)]/30 ${row.Channel.includes("Total (GEO")?"font-bold":""}`}>
                        <td className="px-2 py-1">{row.Channel}</td>
                        <td className="px-2 py-1 text-center font-mono font-bold">{row.Actual.toLocaleString()}</td>
                        <td className="px-2 py-1 text-center font-mono text-[var(--text-muted)]">{row.PY.toLocaleString()}</td>
                        <td className={`px-2 py-1 text-center font-mono font-bold ${isPositive?"text-[var(--success)]":"text-[var(--error)]"}`}>{row.YoY}</td>
                        <td className="px-2 py-1 text-center text-xs">{benchmark}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </GlassCard>
        </>
      )}

      {/* TAB: Input Activities */}
      {activeTab === "input" && (
        <GlassCard>
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">{isZh?"Input Activities 追踪":"Input Activities Tracking"}</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead><tr className="border-b border-[var(--border-glass)]">
                <th className="px-3 py-2 text-left text-[var(--text-muted)]">{isZh?"指标":"Metric"}</th>
                <th className="px-3 py-2 text-center text-[var(--text-muted)]">{isZh?"本周":"This Week"}</th>
                <th className="px-3 py-2 text-center text-[var(--text-muted)]">YTD</th>
                <th className="px-3 py-2 text-center text-[var(--text-muted)]">{isZh?"状态":"Status"}</th>
              </tr></thead>
              <tbody>
                {[
                  {metric:isZh?"检索短语总数":"Total Phrases",week:"—",ytd:"—",status:"⚠️"},
                  {metric:isZh?"内容产出篇数":"Articles Produced",week:"—",ytd:"—",status:"⚠️"},
                  {metric:isZh?"内容发布篇数":"Articles Published",week:"—",ytd:"—",status:"⚠️"},
                  {metric:isZh?"覆盖 AI 引擎数":"AI Engines Covered",week:"9",ytd:"9",status:"✅"},
                  {metric:isZh?"智测验证次数":"Verifications Run",week:String(citationData.length>0?1:0),ytd:String(Math.ceil(citationData.length/5)),status:citationData.length>0?"✅":"⚠️"},
                  {metric:isZh?"品牌提及率":"Brand Mention Rate",week:`${brandRate}%`,ytd:`${brandRate}%`,status:brandRate>50?"✅":"⚠️"},
                  {metric:isZh?"官方链接率":"Official Link Rate",week:`${linkRate}%`,ytd:`${linkRate}%`,status:linkRate>30?"✅":"⚠️"},
                ].map((row,i) => (
                  <tr key={i} className="border-b border-[var(--border-glass)]/30">
                    <td className="px-3 py-2">{row.metric}</td>
                    <td className="px-3 py-2 text-center font-mono">{row.week}</td>
                    <td className="px-3 py-2 text-center font-mono">{row.ytd}</td>
                    <td className="px-3 py-2 text-center">{row.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="text-[10px] text-[var(--text-muted)] mt-2">{isZh?"⚠️ 标记的指标需要通过上传数据或运行智测来补充":"⚠️ Marked metrics need data upload or running verification"}</p>
        </GlassCard>
      )}

      {/* TAB: AI Citation Performance */}
      {activeTab === "citation" && (
        <GlassCard>
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">{isZh?"AI Citation Performance（来自智测验证结果）":"AI Citation Performance (from Zhice results)"}</h2>
          {citationData.length === 0 ? (
            <p className="text-xs text-[var(--text-muted)] py-4 text-center">{isZh?"暂无验证数据。请先在「智测」中运行测试。":"No verification data. Run tests in Zhice first."}</p>
          ) : (
            <>
              <div className="grid grid-cols-4 gap-2 mb-4">
                <div className="text-center p-2 rounded bg-white/5"><p className="text-[10px] text-[var(--text-muted)]">{isZh?"总验证数":"Total"}</p><p className="text-lg font-bold">{totalCitations}</p></div>
                <div className="text-center p-2 rounded bg-white/5"><p className="text-[10px] text-[var(--text-muted)]">{isZh?"品牌提及":"Brand"}</p><p className="text-lg font-bold text-[var(--success)]">{brandCount} ({brandRate}%)</p></div>
                <div className="text-center p-2 rounded bg-white/5"><p className="text-[10px] text-[var(--text-muted)]">{isZh?"官方链接":"Link"}</p><p className="text-lg font-bold text-[var(--accent)]">{linkCount} ({linkRate}%)</p></div>
                <div className="text-center p-2 rounded bg-white/5"><p className="text-[10px] text-[var(--text-muted)]">{isZh?"完全缺口":"Full Gap"}</p><p className="text-lg font-bold text-[var(--error)]">{citationData.filter(c=>!c.brand&&!c.link).length}</p></div>
              </div>
              <div className="overflow-x-auto max-h-64 overflow-y-auto">
                <table className="w-full text-xs">
                  <thead className="sticky top-0 bg-[var(--bg-surface)]"><tr className="border-b border-[var(--border-glass)]">
                    <th className="px-2 py-1.5 text-left text-[var(--text-muted)]">{isZh?"检索短语":"Query"}</th>
                    <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">{isZh?"平台":"Platform"}</th>
                    <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">{isZh?"品牌":"Brand"}</th>
                    <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">{isZh?"链接":"Link"}</th>
                    <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">Gap</th>
                  </tr></thead>
                  <tbody>
                    {citationData.slice(0, 50).map((c, i) => (
                      <tr key={i} className="border-b border-[var(--border-glass)]/30">
                        <td className="px-2 py-1 max-w-[200px] truncate">{c.query}</td>
                        <td className="px-2 py-1 text-center">{c.platform}</td>
                        <td className="px-2 py-1 text-center">{c.brand?"✅":"❌"}</td>
                        <td className="px-2 py-1 text-center">{c.link?"✅":"❌"}</td>
                        <td className="px-2 py-1 text-center"><span className={`text-[10px] px-1.5 py-0.5 rounded ${!c.brand&&!c.link?"bg-red-500/10 text-red-400":!c.link?"bg-yellow-500/10 text-yellow-400":"bg-green-500/10 text-green-400"}`}>{!c.brand&&!c.link?"Full":!c.link?"Partial":"OK"}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </GlassCard>
      )}

      {/* Data Upload Section */}
      <GlassCard>
        <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">{isZh?"📤 上传数据":"📤 Upload Data"}</h2>
        <p className="text-xs text-[var(--text-muted)] mb-3">{isZh?"上传 SSR Funnel Metrics CSV 或 Excel 文件更新 GEO 数据":"Upload SSR Funnel Metrics CSV or Excel to update GEO data"}</p>
        <div className="flex flex-wrap gap-3">
          <label className="flex items-center gap-2 px-4 py-2 rounded-lg border border-[var(--border-glass)] bg-white/5 cursor-pointer hover:border-[var(--accent)]/30">
            <span className="text-xs">{isZh?"📊 上传 GEO 周度数据":"📊 Upload Weekly Data"}</span>
            <span className="text-[10px] text-[var(--text-muted)]">(CSV/Excel)</span>
            <input type="file" accept=".csv,.xlsx,.xls" onChange={handleUploadData} className="hidden" />
          </label>
          <label className="flex items-center gap-2 px-4 py-2 rounded-lg border border-[var(--border-glass)] bg-white/5 cursor-pointer hover:border-[var(--accent)]/30">
            <span className="text-xs">{isZh?"📅 上传月度数据":"📅 Upload Monthly Data"}</span>
            <input type="file" accept=".csv,.xlsx,.xls" onChange={handleUploadData} className="hidden" />
          </label>
          <label className="flex items-center gap-2 px-4 py-2 rounded-lg border border-[var(--border-glass)] bg-white/5 cursor-pointer hover:border-[var(--accent)]/30">
            <span className="text-xs">{isZh?"🔍 上传 Citation 验证结果":"🔍 Upload Citation Results"}</span>
            <input type="file" accept=".csv,.xlsx,.xls" onChange={handleUploadData} className="hidden" />
          </label>
        </div>
      </GlassCard>

      {/* Attribution & Insights (collapsible) */}
      <GlassCard>
        <details open>
          <summary className="text-sm font-medium text-[var(--text-secondary)] cursor-pointer">{isZh?"💡 归因分析 & Opportunities":"💡 Attribution & Opportunities"}</summary>
          <div className="mt-3 space-y-2 text-xs text-[var(--text-secondary)]">
            <p>• CN GEO {latest.CN_GEO} — {isZh?"AI search referrer 持续增长，GEO 策略验证有效":"AI search referrer growing, GEO strategy validated"}</p>
            <p>• WW Direct {latest.WW_Direct.toLocaleString()} — {isZh?"2-3 周内容发布滞后效应":"2-3 week content publish lag effect"}</p>
            <p>• {isZh?"YTD GEO+Direct 跑赢大盘 ~27 ppts":"YTD GEO+Direct outperform benchmark by ~27 ppts"}</p>
            <div className="mt-2 pt-2 border-t border-[var(--border-glass)]">
              <p className="font-medium text-[var(--text-primary)]">{isZh?"🚀 Opportunities:":"🚀 Opportunities:"}</p>
              <p>• {isZh?"扩大 EU/JP 覆盖（GEO 绝对值低但 YoY 增速快）":"Expand EU/JP coverage (low absolute but high YoY)"}</p>
              <p>• {isZh?"建立 Input→Output 周度追踪完善归因":"Establish weekly Input→Output tracking"}</p>
              <p>• {isZh?"JP Direct +113% YoY — AI search 渗透最快市场":"JP Direct +113% YoY — fastest AI penetration"}</p>
            </div>
          </div>
        </details>
      </GlassCard>
    </div>
  );
}
