"use client";

import { useState, useEffect } from "react";
import { useI18nStore } from "@/stores/i18n-store";
import { useAuthStore } from "@/stores/auth-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid, BarChart, Bar } from "recharts";
import { GEO_MAU, SOURCE_ANALYSIS, INPUT_LINK_RATE, INPUT_SUMMARY, GEO_OUTPUT, PHRASE_CATEGORIES, SEMANTIC_COVERAGE } from "@/lib/zhixi-geo-data";

// ============ FULL DATA from geo_weekly_data.csv (WK1-WK29) ============
const ALL_WEEKLY = [
  {Week:"WK1",CN_GEO:15,WW_GEO:11,Total_GEO:26,WW_Direct:738,CN_Direct:0,Direct:738,Total:764,Total_PY:631},
  {Week:"WK2",CN_GEO:26,WW_GEO:24,Total_GEO:50,WW_Direct:1293,CN_Direct:0,Direct:1293,Total:1343,Total_PY:565},
  {Week:"WK3",CN_GEO:20,WW_GEO:20,Total_GEO:40,WW_Direct:1165,CN_Direct:0,Direct:1165,Total:1205,Total_PY:500},
  {Week:"WK4",CN_GEO:14,WW_GEO:20,Total_GEO:34,WW_Direct:1128,CN_Direct:0,Direct:1128,Total:1162,Total_PY:321},
  {Week:"WK5",CN_GEO:25,WW_GEO:15,Total_GEO:40,WW_Direct:1152,CN_Direct:0,Direct:1152,Total:1192,Total_PY:156},
  {Week:"WK6",CN_GEO:21,WW_GEO:15,Total_GEO:36,WW_Direct:904,CN_Direct:0,Direct:904,Total:940,Total_PY:481},
  {Week:"WK7",CN_GEO:7,WW_GEO:9,Total_GEO:16,WW_Direct:360,CN_Direct:0,Direct:360,Total:376,Total_PY:725},
  {Week:"WK8",CN_GEO:2,WW_GEO:7,Total_GEO:9,WW_Direct:202,CN_Direct:0,Direct:202,Total:211,Total_PY:963},
  {Week:"WK9",CN_GEO:35,WW_GEO:20,Total_GEO:55,WW_Direct:922,CN_Direct:0,Direct:922,Total:977,Total_PY:1070},
  {Week:"WK10",CN_GEO:36,WW_GEO:20,Total_GEO:56,WW_Direct:1399,CN_Direct:0,Direct:1399,Total:1455,Total_PY:1090},
  {Week:"WK11",CN_GEO:45,WW_GEO:13,Total_GEO:58,WW_Direct:1642,CN_Direct:0,Direct:1642,Total:1700,Total_PY:1037},
  {Week:"WK12",CN_GEO:36,WW_GEO:22,Total_GEO:58,WW_Direct:1752,CN_Direct:0,Direct:1752,Total:1810,Total_PY:997},
  {Week:"WK13",CN_GEO:33,WW_GEO:23,Total_GEO:56,WW_Direct:1806,CN_Direct:0,Direct:1806,Total:1862,Total_PY:870},
  {Week:"WK14",CN_GEO:35,WW_GEO:23,Total_GEO:58,WW_Direct:1634,CN_Direct:0,Direct:1634,Total:1692,Total_PY:753},
  {Week:"WK15",CN_GEO:45,WW_GEO:17,Total_GEO:62,WW_Direct:1581,CN_Direct:1082,Direct:2663,Total:2725,Total_PY:2672},
  {Week:"WK16",CN_GEO:40,WW_GEO:15,Total_GEO:55,WW_Direct:1750,CN_Direct:1327,Direct:3077,Total:3132,Total_PY:2970},
  {Week:"WK17",CN_GEO:32,WW_GEO:15,Total_GEO:47,WW_Direct:1738,CN_Direct:3128,Direct:4866,Total:4913,Total_PY:5549},
  {Week:"WK18",CN_GEO:33,WW_GEO:17,Total_GEO:50,WW_Direct:1330,CN_Direct:2120,Direct:3450,Total:3500,Total_PY:3692},
  {Week:"WK19",CN_GEO:33,WW_GEO:21,Total_GEO:54,WW_Direct:1453,CN_Direct:2072,Direct:3525,Total:3579,Total_PY:3964},
  {Week:"WK20",CN_GEO:41,WW_GEO:31,Total_GEO:72,WW_Direct:1914,CN_Direct:2242,Direct:4156,Total:4228,Total_PY:3822},
  {Week:"WK21",CN_GEO:44,WW_GEO:19,Total_GEO:63,WW_Direct:2054,CN_Direct:1929,Direct:3983,Total:4046,Total_PY:3872},
  {Week:"WK22",CN_GEO:38,WW_GEO:22,Total_GEO:60,WW_Direct:2143,CN_Direct:2271,Direct:4414,Total:4474,Total_PY:3349},
  {Week:"WK23",CN_GEO:25,WW_GEO:24,Total_GEO:49,WW_Direct:4060,CN_Direct:2904,Direct:6964,Total:7013,Total_PY:3446},
  {Week:"WK24",CN_GEO:41,WW_GEO:23,Total_GEO:64,WW_Direct:2252,CN_Direct:3140,Direct:5392,Total:5456,Total_PY:3436},
  {Week:"WK25",CN_GEO:31,WW_GEO:15,Total_GEO:46,WW_Direct:1579,CN_Direct:1538,Direct:3117,Total:3163,Total_PY:3718},
  {Week:"WK26",CN_GEO:38,WW_GEO:30,Total_GEO:68,WW_Direct:1619,CN_Direct:1938,Direct:3557,Total:3625,Total_PY:2156},
  {Week:"WK27",CN_GEO:41,WW_GEO:22,Total_GEO:63,WW_Direct:1537,CN_Direct:1874,Direct:3411,Total:3474,Total_PY:1929},
  {Week:"WK28",CN_GEO:41,WW_GEO:22,Total_GEO:63,WW_Direct:1219,CN_Direct:1637,Direct:2856,Total:2919,Total_PY:1795},
  {Week:"WK29",CN_GEO:41,WW_GEO:28,Total_GEO:69,WW_Direct:1400,CN_Direct:1272,Direct:2672,Total:2741,Total_PY:1935},
  {Week:"WK30",CN_GEO:38,WW_GEO:34,Total_GEO:72,WW_Direct:1499,CN_Direct:1016,Direct:2515,Total:2587,Total_PY:1845},
  {Week:"WK31",CN_GEO:51,WW_GEO:22,Total_GEO:73,WW_Direct:1725,CN_Direct:963,Direct:2688,Total:2761,Total_PY:1794},
  {Week:"WK32",CN_GEO:35,WW_GEO:20,Total_GEO:55,WW_Direct:1722,CN_Direct:960,Direct:2682,Total:2737,Total_PY:1723},
];

// Monthly data from geo_monthly_data.csv
const MONTHLY_DATA = [
  {Channel:"CN GEO",M1:89,M2:65,M3:165,Q1:319,M4:164,M5:163,M6:152,Q2:479,M7:189},
  {Channel:"WW GEO",M1:83,M2:51,M3:91,Q1:225,M4:70,M5:101,M6:97,Q2:268,M7:116},
  {Channel:"Total GEO",M1:172,M2:116,M3:256,Q1:544,M4:234,M5:264,M6:249,Q2:747,M7:305},
  {Channel:"Direct (WW+CN)",M1:9071,M2:3996,M3:11928,Q1:24995,M4:12592,M5:12626,M6:16885,Q2:42103,M7:12540},
  {Channel:"Total",M1:9243,M2:4112,M3:12184,Q1:25539,M4:12826,M5:12890,M6:17134,Q2:42850,M7:12845},
  {Channel:"SSR Total",M1:38062,M2:18084,M3:46314,Q1:102460,M4:47289,M5:48846,M6:51465,Q2:147600,M7:46123},
];

// Input Summary from geo_input_summary.csv
const INPUT_DATA = [
  {metric:"提示词#",Dec:152,M1:210,M2:297,M3:297,M4:397,M5:564,M6:646},
  {metric:"品牌词链接提及率",Dec:"18.1%",M1:"49.0%",M2:"53.5%",M3:"60.5%",M4:"53.7%",M5:"54.8%",M6:"56.9%"},
  {metric:"新建内容#",Dec:106,M1:98,M2:43,M3:118,M4:123,M5:135,M6:131},
  {metric:"旧内容优化#",Dec:67,M1:26,M2:12,M3:0,M4:1,M5:0,M6:0},
  {metric:"官网链接提及率",Dec:"18.1%",M1:"44.3%",M2:"35.3%",M3:"44.7%",M4:"37.7%",M5:"48.3%",M6:"51.6%"},
  {metric:"官网链接提及总量",Dec:220,M1:745,M2:839,M3:1063,M4:1197,M5:2498,M6:2666},
];

// Citation by platform (from brand_link_mentions_monthly.csv)
const CITATION_BY_PLATFORM = [
  {month:"M1",元宝:48.5,DeepSeek:50.8,豆包:61.6,ChatGPT:35.0},
  {month:"M2",元宝:52.5,DeepSeek:55.9,豆包:63.0,ChatGPT:42.4},
  {month:"M3",元宝:66.0,DeepSeek:62.6,豆包:69.4,ChatGPT:44.1},
  {month:"M4",元宝:61.2,DeepSeek:50.4,豆包:63.2,ChatGPT:39.8},
  {month:"M5",元宝:74.0,DeepSeek:66.5,豆包:48.6,ChatGPT:30.1,Kimi:59.1,千问:66.9,Gemini:46.9},
  {month:"M6",元宝:75.4,DeepSeek:66.7,豆包:56.9,ChatGPT:28.5,Kimi:53.4,千问:66.9,Gemini:44.8},
];

// YTD data (H1 = Jan-Jul 2026 vs 2025 H1)
const YTD_DATA = [
  {Channel:"CN GEO",Actual:798,PY:166,YoY:"+381%"},
  {Channel:"WW GEO",Actual:493,PY:267,YoY:"+85%"},
  {Channel:"Total GEO",Actual:1291,PY:433,YoY:"+198%"},
  {Channel:"Direct (WW+CN)",Actual:67098,PY:63582,YoY:"+6%"},
  {Channel:"Total (GEO+Direct)",Actual:68389,PY:64015,YoY:"+7%"},
  {Channel:"SSR Total (大盘)",Actual:250060,PY:302661,YoY:"-17%"},
];

function wow(c:number,p:number){if(!p)return"—";const r=((c-p)/p*100);return `${r>0?"+":""}${r.toFixed(1)}%`}

export default function ZhixiPage() {
  const { t, locale } = useI18nStore();
  const isZh = locale.startsWith("zh");
  const [tab, setTab] = useState<"output"|"monthly"|"input"|"citation"|"mau"|"sources"|"phrases">("output");
  const [showEarly, setShowEarly] = useState(false);
  const [phraseData, setPhraseData] = useState<{category:string;phrase:string;yuanbao:boolean;deepseek:boolean;doubao:boolean;chatgpt:boolean;kimi:boolean;qianwen:boolean;gemini:boolean}[]>([]);

  // Load phrase data from localStorage if previously uploaded
  useEffect(() => {
    try {
      const saved = localStorage.getItem("zhixi_phrase_data");
      if (saved) setPhraseData(JSON.parse(saved));
    } catch { /* ignore */ }
  }, []);

  // Handle Excel upload for phrase-level data
  const handlePhraseUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const XLSX = await import("xlsx");
      const buffer = await file.arrayBuffer();
      const wb = XLSX.read(buffer, { type: "array" });
      // Try to find the sheet with phrase data (sheet name containing "3.2" or "detail" or "CN+NA")
      let ws = null;
      for (const name of wb.SheetNames) {
        if (name.includes("3.2") || name.includes("detail") || name.includes("CN") || name.includes("Input")) {
          ws = wb.Sheets[name];
          break;
        }
      }
      if (!ws) ws = wb.Sheets[wb.SheetNames[0]]; // fallback to first sheet

      const rows = XLSX.utils.sheet_to_json(ws, { header: 1 }) as unknown[][];
      // Parse: look for rows with phrase data (category, phrase, link, then platform columns)
      const parsed: typeof phraseData = [];
      for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        if (!row || row.length < 5) continue;
        // Try to identify category (col 1-2) and phrase (col 2-3)
        const cat = String(row[1] || row[0] || "").trim();
        const phrase = String(row[2] || row[1] || "").trim();
        if (!phrase || phrase.length < 4) continue;
        // Look for 1/0 values in platform columns (typically cols 4+)
        // The Excel has many date columns; we take the last available month's data
        const vals = row.slice(3).map(v => v === 1 || v === "1" || v === true);
        // Map to platforms based on column position patterns
        // Simplified: if row has enough data, take last 7 values as platform flags
        const lastVals = vals.slice(-7);
        parsed.push({
          category: cat.length > 0 && cat.length < 20 ? cat : "其他",
          phrase,
          yuanbao: lastVals[0] || false,
          deepseek: lastVals[1] || false,
          doubao: lastVals[2] || false,
          chatgpt: lastVals[3] || false,
          kimi: lastVals[4] || false,
          qianwen: lastVals[5] || false,
          gemini: lastVals[6] || false,
        });
      }
      if (parsed.length > 0) {
        setPhraseData(parsed);
        localStorage.setItem("zhixi_phrase_data", JSON.stringify(parsed));
      } else {
        alert("未能解析到短语数据，请确认 Excel 格式正确");
      }
    } catch (err) {
      alert("解析失败: " + String(err));
    }
    e.target.value = "";
  };

  const latest = ALL_WEEKLY[ALL_WEEKLY.length - 1];
  const prev = ALL_WEEKLY[ALL_WEEKLY.length - 2];
  const recentWeeks = ALL_WEEKLY.slice(-10);
  const earlyWeeks = ALL_WEEKLY.slice(0, -10);

  // File upload
  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    alert(isZh ? `✅ 已上传: ${file.name}\n后续版本将自动解析并更新数据` : `✅ Uploaded: ${file.name}`);
    e.target.value = "";
  };

  return (
    <div className="space-y-5 max-w-[1400px]">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{t("zhixi.title")}</h1>
        <label className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-[var(--border-glass)] bg-white/5 cursor-pointer hover:border-[var(--accent)]/30 text-xs">
          📤 {isZh ? "上传数据" : "Upload Data"}
          <input type="file" accept=".csv,.xlsx,.xls" onChange={handleUpload} className="hidden" />
        </label>
      </div>

      {/* KPI Summary */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-2">
        <GlassCard padding="sm" className="text-center"><p className="text-[10px] text-[var(--text-muted)]">{latest.Week} Total</p><p className="text-lg font-bold text-[var(--accent)]">{latest.Total.toLocaleString()}</p><p className="text-[10px]">WoW {wow(latest.Total,prev.Total)}</p></GlassCard>
        <GlassCard padding="sm" className="text-center"><p className="text-[10px] text-[var(--text-muted)]">GEO Total</p><p className="text-lg font-bold text-blue-400">{latest.Total_GEO}</p><p className="text-[10px]">WoW {wow(latest.Total_GEO,prev.Total_GEO)}</p></GlassCard>
        <GlassCard padding="sm" className="text-center"><p className="text-[10px] text-[var(--text-muted)]">WW Direct</p><p className="text-lg font-bold text-purple-400">{latest.WW_Direct.toLocaleString()}</p></GlassCard>
        <GlassCard padding="sm" className="text-center"><p className="text-[10px] text-[var(--text-muted)]">YTD Total</p><p className="text-lg font-bold">68,389</p><p className="text-[10px] text-[var(--success)]">YoY +7%</p></GlassCard>
        <GlassCard padding="sm" className="text-center"><p className="text-[10px] text-[var(--text-muted)]">{isZh?"链接提及率":"Link Rate"}</p><p className="text-lg font-bold">51.6%</p><p className="text-[10px] text-[var(--success)]">M6</p></GlassCard>
        <GlassCard padding="sm" className="text-center"><p className="text-[10px] text-[var(--text-muted)]">{isZh?"内容总量":"Content"}</p><p className="text-lg font-bold">646</p><p className="text-[10px]">{isZh?"检索短语":"phrases"}</p></GlassCard>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-[var(--border-glass)] overflow-x-auto">
        {([["output","📊 Output"],["monthly","📅 Monthly"],["input","📝 Input"],["citation","🔍 Citation"],["mau","🌐 MAU"],["sources","📡 信源"],["phrases","🔎 短语详情"]] as [string,string][]).map(([k,l])=>(
          <button key={k} onClick={()=>setTab(k as typeof tab)} className={`px-3 py-2 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${tab===k?"border-[var(--accent)] text-[var(--accent)]":"border-transparent text-[var(--text-muted)]"}`}>{l}</button>
        ))}
      </div>

      {/* ===== TAB: OUTPUT ===== */}
      {tab === "output" && (<>
        {/* Trend Chart */}
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">Weekly Performance Trend</h2>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={ALL_WEEKLY.slice(-15)} margin={{top:5,right:10,left:0,bottom:5}}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="Week" tick={{fontSize:10,fill:"#8892b0"}} tickFormatter={(v:string)=>v.replace("WK","")} />
              <YAxis tick={{fontSize:10,fill:"#8892b0"}} />
              <Tooltip contentStyle={{background:"#1a1d2e",border:"1px solid #2a2f4a",borderRadius:8,fontSize:11}} />
              <Legend wrapperStyle={{fontSize:11}} />
              <Line type="monotone" dataKey="Total" stroke="#00bcd4" strokeWidth={2} dot={false} name="Total" />
              <Line type="monotone" dataKey="Total_PY" stroke="#5a6380" strokeWidth={1} strokeDasharray="4 4" dot={false} name="PY" />
              <Line type="monotone" dataKey="Direct" stroke="#ab47bc" strokeWidth={1.5} dot={false} name="Direct" />
              <Line type="monotone" dataKey="Total_GEO" stroke="#2196f3" strokeWidth={1.5} dot={false} name="GEO" />
            </LineChart>
          </ResponsiveContainer>
        </GlassCard>

        {/* Weekly Table (recent) */}
        <GlassCard padding="sm">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-sm font-medium text-[var(--text-secondary)]">Weekly Reg Starts</h2>
            <button onClick={()=>setShowEarly(!showEarly)} className="text-[10px] text-[var(--text-muted)] hover:text-[var(--accent)]">
              {showEarly ? "▲ 收起 WK1-19" : "▶ 展开 WK1-19"}
            </button>
          </div>
          {showEarly && (
            <div className="overflow-x-auto mb-3 border border-[var(--border-glass)] rounded p-1">
              <table className="w-full text-[10px]"><thead><tr className="border-b border-[var(--border-glass)]"><th className="px-1 py-0.5 text-left">Ch</th>{earlyWeeks.map(w=><th key={w.Week} className="px-1 py-0.5 text-center">{w.Week.replace("WK","")}</th>)}</tr></thead>
              <tbody>{([{n:"GEO",k:"Total_GEO" as const},{n:"Dir",k:"WW_Direct" as const},{n:"Tot",k:"Total" as const}]).map(c=>(
                <tr key={c.n} className="border-b border-[var(--border-glass)]/20"><td className="px-1 py-0.5">{c.n}</td>{earlyWeeks.map(w=><td key={w.Week} className="px-1 py-0.5 text-center font-mono">{w[c.k]||"—"}</td>)}</tr>
              ))}</tbody></table>
            </div>
          )}
          <div className="overflow-x-auto">
            <table className="w-full text-xs"><thead><tr className="border-b border-[var(--border-glass)]"><th className="px-2 py-1 text-left text-[var(--text-muted)]">Channel</th>{recentWeeks.map(w=><th key={w.Week} className="px-1 py-1 text-center text-[var(--text-muted)]">{w.Week.replace("WK","")}</th>)}<th className="px-2 py-1 text-center text-[var(--text-muted)]">WoW</th></tr></thead>
            <tbody>{([{n:"CN GEO",k:"CN_GEO" as const,c:"text-blue-400"},{n:"WW GEO",k:"WW_GEO" as const,c:"text-cyan-400"},{n:"GEO Total",k:"Total_GEO" as const,c:"text-blue-300 font-semibold"},{n:"Direct (WW+CN)",k:"Direct" as const,c:"text-purple-400"},{n:"Total",k:"Total" as const,c:"text-[var(--accent)] font-bold"}]).map(ch=>(
              <tr key={ch.n} className="border-b border-[var(--border-glass)]/30"><td className={`px-2 py-1 ${ch.c} whitespace-nowrap`}>{ch.n}</td>{recentWeeks.map(w=><td key={w.Week} className="px-1 py-1 text-center font-mono">{w[ch.k]>999?`${(w[ch.k]/1000).toFixed(1)}k`:w[ch.k]}</td>)}<td className="px-2 py-1 text-center font-mono">{wow(recentWeeks[recentWeeks.length-1][ch.k],recentWeeks[recentWeeks.length-2][ch.k])}</td></tr>
            ))}</tbody></table>
          </div>
        </GlassCard>
      </>)}

      {/* ===== TAB: MONTHLY ===== */}
      {tab === "monthly" && (<>
        {/* Monthly Trend Chart */}
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">Monthly Reg Start Trend</h2>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={[
              {month:"M1",Total_GEO:172,Direct:9071,Total:9243,SSR_Total:38062},
              {month:"M2",Total_GEO:116,Direct:3996,Total:4112,SSR_Total:18084},
              {month:"M3",Total_GEO:256,Direct:11928,Total:12184,SSR_Total:46314},
              {month:"M4",Total_GEO:234,Direct:12592,Total:12826,SSR_Total:47289},
              {month:"M5",Total_GEO:264,Direct:12626,Total:12890,SSR_Total:48846},
              {month:"M6",Total_GEO:249,Direct:16885,Total:17134,SSR_Total:51465},
              {month:"M7",Total_GEO:305,Direct:12540,Total:12845,SSR_Total:46123},
            ]} margin={{top:5,right:10,left:0,bottom:5}}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" tick={{fontSize:10,fill:"#8892b0"}} />
              <YAxis yAxisId="left" tick={{fontSize:10,fill:"#8892b0"}} />
              <YAxis yAxisId="right" orientation="right" tick={{fontSize:10,fill:"#8892b0"}} />
              <Tooltip contentStyle={{background:"#1a1d2e",border:"1px solid #2a2f4a",borderRadius:8,fontSize:11}} />
              <Legend wrapperStyle={{fontSize:11}} />
              <Line yAxisId="right" type="monotone" dataKey="SSR_Total" stroke="#5a6380" strokeWidth={1} strokeDasharray="4 4" dot={false} name="SSR Total (大盘)" />
              <Line yAxisId="left" type="monotone" dataKey="Total" stroke="#00bcd4" strokeWidth={2} dot={{r:3}} name="GEO+Direct Total" />
              <Line yAxisId="left" type="monotone" dataKey="Direct" stroke="#ab47bc" strokeWidth={1.5} dot={{r:2}} name="Direct" />
              <Line yAxisId="left" type="monotone" dataKey="Total_GEO" stroke="#2196f3" strokeWidth={1.5} dot={{r:2}} name="GEO" />
            </LineChart>
          </ResponsiveContainer>
        </GlassCard>

        {/* Monthly CL_RS% Trend Chart */}
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">Monthly CL_RS% (Clean Launch / Reg Start)</h2>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={[
              {month:"M1",GEO:7.0,Direct:17.8,GEO_Direct:17.6,SSR:21.0},
              {month:"M2",GEO:6.0,Direct:21.1,GEO_Direct:20.7,SSR:24.2},
              {month:"M3",GEO:10.2,Direct:23.5,GEO_Direct:23.2,SSR:26.0},
              {month:"M4",GEO:9.8,Direct:21.1,GEO_Direct:20.9,SSR:25.8},
              {month:"M5",GEO:12.1,Direct:24.3,GEO_Direct:24.1,SSR:28.0},
              {month:"M6",GEO:6.8,Direct:32.7,GEO_Direct:32.3,SSR:34.1},
              {month:"M7",GEO:3.6,Direct:23.3,GEO_Direct:22.9,SSR:23.4},
            ]} margin={{top:5,right:10,left:0,bottom:5}}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" tick={{fontSize:10,fill:"#8892b0"}} />
              <YAxis tick={{fontSize:10,fill:"#8892b0"}} domain={[0,40]} unit="%" />
              <Tooltip contentStyle={{background:"#1a1d2e",border:"1px solid #2a2f4a",borderRadius:8,fontSize:11}} formatter={(v)=>`${v}%`} />
              <Legend wrapperStyle={{fontSize:11}} />
              <Line type="monotone" dataKey="SSR" stroke="#5a6380" strokeWidth={1} strokeDasharray="4 4" dot={false} name="SSR Total CL_RS%" />
              <Line type="monotone" dataKey="GEO_Direct" stroke="#00bcd4" strokeWidth={2} dot={{r:3}} name="GEO+Direct CL_RS%" />
              <Line type="monotone" dataKey="Direct" stroke="#ab47bc" strokeWidth={1.5} dot={{r:2}} name="WW Direct CL_RS%" />
              <Line type="monotone" dataKey="GEO" stroke="#2196f3" strokeWidth={1.5} dot={{r:2}} name="GEO CL_RS%" />
            </LineChart>
          </ResponsiveContainer>
        </GlassCard>

        {/* Monthly Table */}
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">Monthly Data Table</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs"><thead><tr className="border-b border-[var(--border-glass)]"><th className="px-2 py-1 text-left text-[var(--text-muted)]">Channel</th><th className="px-2 py-1 text-center">M1</th><th className="px-2 py-1 text-center">M2</th><th className="px-2 py-1 text-center">M3</th><th className="px-2 py-1 text-center font-bold">Q1</th><th className="px-2 py-1 text-center">M4</th><th className="px-2 py-1 text-center">M5</th><th className="px-2 py-1 text-center">M6</th><th className="px-2 py-1 text-center font-bold">Q2</th><th className="px-2 py-1 text-center">M7</th></tr></thead>
            <tbody>{MONTHLY_DATA.map(r=>(<tr key={r.Channel} className={`border-b border-[var(--border-glass)]/30 ${r.Channel==="Total"||r.Channel==="SSR Total"?"font-bold":""}`}><td className="px-2 py-1">{r.Channel}</td><td className="px-2 py-1 text-center font-mono">{r.M1.toLocaleString()}</td><td className="px-2 py-1 text-center font-mono">{r.M2.toLocaleString()}</td><td className="px-2 py-1 text-center font-mono">{r.M3.toLocaleString()}</td><td className="px-2 py-1 text-center font-mono font-bold">{r.Q1.toLocaleString()}</td><td className="px-2 py-1 text-center font-mono">{r.M4.toLocaleString()}</td><td className="px-2 py-1 text-center font-mono">{r.M5.toLocaleString()}</td><td className="px-2 py-1 text-center font-mono">{r.M6.toLocaleString()}</td><td className="px-2 py-1 text-center font-mono font-bold">{r.Q2.toLocaleString()}</td><td className="px-2 py-1 text-center font-mono">{r.M7||"—"}</td></tr>))}</tbody></table>
          </div>
        </GlassCard>
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">YTD vs SSR Benchmark</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs"><thead><tr className="border-b border-[var(--border-glass)]"><th className="px-2 py-1 text-left">Channel</th><th className="px-2 py-1 text-center">YTD</th><th className="px-2 py-1 text-center">PY</th><th className="px-2 py-1 text-center">YoY</th><th className="px-2 py-1 text-center">vs 大盘</th></tr></thead>
            <tbody>{YTD_DATA.map(r=>{const pos=r.YoY.startsWith("+");return(<tr key={r.Channel} className="border-b border-[var(--border-glass)]/30"><td className="px-2 py-1">{r.Channel}</td><td className="px-2 py-1 text-center font-mono font-bold">{r.Actual.toLocaleString()}</td><td className="px-2 py-1 text-center font-mono text-[var(--text-muted)]">{r.PY.toLocaleString()}</td><td className={`px-2 py-1 text-center font-mono font-bold ${pos?"text-[var(--success)]":"text-[var(--error)]"}`}>{r.YoY}</td><td className="px-2 py-1 text-center text-[10px]">{r.Channel.includes("SSR")?"Benchmark":(pos?`跑赢 ${parseInt(r.YoY)+17}ppts`:"落后")}</td></tr>)})}</tbody></table>
          </div>
        </GlassCard>
      </>)}

      {/* ===== TAB: INPUT ===== */}
      {tab === "input" && (<>
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">{isZh?"Input Activities Summary（来自 geo_input_summary）":"Input Activities"}</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs"><thead><tr className="border-b border-[var(--border-glass)]"><th className="px-2 py-1 text-left text-[var(--text-muted)]">{isZh?"指标":"Metric"}</th><th className="px-2 py-1 text-center">Dec</th><th className="px-2 py-1 text-center">M1</th><th className="px-2 py-1 text-center">M2</th><th className="px-2 py-1 text-center">M3</th><th className="px-2 py-1 text-center">M4</th><th className="px-2 py-1 text-center">M5</th><th className="px-2 py-1 text-center">M6</th></tr></thead>
            <tbody>{INPUT_DATA.map((r,i)=>(<tr key={i} className="border-b border-[var(--border-glass)]/30"><td className="px-2 py-1 whitespace-nowrap">{r.metric}</td><td className="px-2 py-1 text-center font-mono">{r.Dec}</td><td className="px-2 py-1 text-center font-mono">{r.M1}</td><td className="px-2 py-1 text-center font-mono">{r.M2}</td><td className="px-2 py-1 text-center font-mono">{r.M3}</td><td className="px-2 py-1 text-center font-mono">{r.M4}</td><td className="px-2 py-1 text-center font-mono">{r.M5}</td><td className="px-2 py-1 text-center font-mono">{r.M6}</td></tr>))}</tbody></table>
          </div>
        </GlassCard>
        {/* Link Rate Trend Chart */}
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">{isZh?"官网链接提及率趋势":"Official Link Mention Rate Trend"}</h2>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={[{m:"Dec",rate:18.1},{m:"M1",rate:44.3},{m:"M2",rate:35.3},{m:"M3",rate:44.7},{m:"M4",rate:37.7},{m:"M5",rate:48.3},{m:"M6",rate:51.6}]} margin={{top:5,right:10,left:0,bottom:5}}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="m" tick={{fontSize:10,fill:"#8892b0"}} />
              <YAxis tick={{fontSize:10,fill:"#8892b0"}} domain={[0,70]} unit="%" />
              <Tooltip contentStyle={{background:"#1a1d2e",border:"1px solid #2a2f4a",borderRadius:8,fontSize:11}} />
              <Line type="monotone" dataKey="rate" stroke="#00bcd4" strokeWidth={2} name="Link Rate %" />
            </LineChart>
          </ResponsiveContainer>
        </GlassCard>
      </>)}

      {/* ===== TAB: CITATION ===== */}
      {tab === "citation" && (<>
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">{isZh?"官网链接提及率 by Platform（月度）":"Link Rate by Platform (Monthly)"}</h2>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={CITATION_BY_PLATFORM} margin={{top:5,right:10,left:0,bottom:5}}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" tick={{fontSize:10,fill:"#8892b0"}} />
              <YAxis tick={{fontSize:10,fill:"#8892b0"}} domain={[20,80]} unit="%" />
              <Tooltip contentStyle={{background:"#1a1d2e",border:"1px solid #2a2f4a",borderRadius:8,fontSize:11}} />
              <Legend wrapperStyle={{fontSize:10}} />
              <Line type="monotone" dataKey="元宝" stroke="#ff6b35" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="DeepSeek" stroke="#2196f3" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="豆包" stroke="#4caf50" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="ChatGPT" stroke="#9c27b0" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="千问" stroke="#00bcd4" strokeWidth={1.5} dot={false} />
              <Line type="monotone" dataKey="Kimi" stroke="#ffeb3b" strokeWidth={1.5} dot={false} />
              <Line type="monotone" dataKey="Gemini" stroke="#e91e63" strokeWidth={1.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </GlassCard>
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">{isZh?"检索短语验证详情":"Phrase Verification Detail"}</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs"><thead><tr className="border-b border-[var(--border-glass)]"><th className="px-2 py-1 text-left text-[var(--text-muted)]">Month</th><th className="px-2 py-1 text-center">元宝</th><th className="px-2 py-1 text-center">DeepSeek</th><th className="px-2 py-1 text-center">豆包</th><th className="px-2 py-1 text-center">ChatGPT</th><th className="px-2 py-1 text-center">Kimi</th><th className="px-2 py-1 text-center">千问</th><th className="px-2 py-1 text-center">Gemini</th></tr></thead>
            <tbody>{CITATION_BY_PLATFORM.map(r=>(<tr key={r.month} className="border-b border-[var(--border-glass)]/30"><td className="px-2 py-1 font-medium">{r.month}</td><td className="px-2 py-1 text-center font-mono">{r.元宝}%</td><td className="px-2 py-1 text-center font-mono">{r.DeepSeek}%</td><td className="px-2 py-1 text-center font-mono">{r.豆包}%</td><td className="px-2 py-1 text-center font-mono">{r.ChatGPT}%</td><td className="px-2 py-1 text-center font-mono">{r.Kimi||"—"}</td><td className="px-2 py-1 text-center font-mono">{r.千问||"—"}</td><td className="px-2 py-1 text-center font-mono">{r.Gemini||"—"}</td></tr>))}</tbody></table>
          </div>
        </GlassCard>
      </>)}

      {/* ===== TAB: GEO MAU ===== */}
      {tab === "mau" && (<>
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">AI Platform MAU — 国内 (万)</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs"><thead><tr className="border-b border-[var(--border-glass)]"><th className="px-2 py-1 text-left">Platform</th><th className="px-2 py-1 text-center">Jan</th><th className="px-2 py-1 text-center">Feb</th><th className="px-2 py-1 text-center">Mar</th><th className="px-2 py-1 text-center">Apr</th><th className="px-2 py-1 text-center">May</th><th className="px-2 py-1 text-center">Jun</th><th className="px-2 py-1 text-left text-[var(--text-muted)]">说明</th></tr></thead>
            <tbody>{GEO_MAU.CN.map(r=>(<tr key={r.platform} className="border-b border-[var(--border-glass)]/30"><td className="px-2 py-1 font-medium">{r.platform}</td><td className="px-2 py-1 text-center font-mono">{(r.Jan/10000).toFixed(1)}万</td><td className="px-2 py-1 text-center font-mono">{(r.Feb/10000).toFixed(1)}万</td><td className="px-2 py-1 text-center font-mono">{(r.Mar/10000).toFixed(1)}万</td><td className="px-2 py-1 text-center font-mono">{(r.Apr/10000).toFixed(1)}万</td><td className="px-2 py-1 text-center font-mono">{(r.May/10000).toFixed(1)}万</td><td className="px-2 py-1 text-center font-mono">{(r.Jun/10000).toFixed(1)}万</td><td className="px-2 py-1 text-[10px] text-[var(--text-muted)] max-w-[150px] truncate">{r.desc}</td></tr>))}</tbody></table>
          </div>
        </GlassCard>
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">AI Platform MAU — 海外</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs"><thead><tr className="border-b border-[var(--border-glass)]"><th className="px-2 py-1 text-left">Platform</th><th className="px-2 py-1 text-center">Apr</th><th className="px-2 py-1 text-center">May</th><th className="px-2 py-1 text-center">Jun</th><th className="px-2 py-1 text-left text-[var(--text-muted)]">说明</th></tr></thead>
            <tbody>{GEO_MAU.WW.map(r=>(<tr key={r.platform} className="border-b border-[var(--border-glass)]/30"><td className="px-2 py-1 font-medium">{r.platform}</td><td className="px-2 py-1 text-center font-mono">{r.Apr>0?(r.Apr/10000).toFixed(1)+"万":"—"}</td><td className="px-2 py-1 text-center font-mono">{r.May>0?(r.May/10000).toFixed(1)+"万":"—"}</td><td className="px-2 py-1 text-center font-mono">{r.Jun>0?(r.Jun/10000).toFixed(1)+"万":"—"}</td><td className="px-2 py-1 text-[10px] text-[var(--text-muted)]">{r.desc}</td></tr>))}</tbody></table>
          </div>
        </GlassCard>
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">GEO Output by Platform — Reg Start (FY26)</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs"><thead><tr className="border-b border-[var(--border-glass)]"><th className="px-2 py-1 text-left">Metric</th><th className="px-1 py-1 text-center">Jan</th><th className="px-1 py-1 text-center">Feb</th><th className="px-1 py-1 text-center">Mar</th><th className="px-1 py-1 text-center">Apr</th><th className="px-1 py-1 text-center">May</th><th className="px-1 py-1 text-center">Jun</th><th className="px-1 py-1 text-center">Jul</th><th className="px-1 py-1 text-center font-bold">YTD</th></tr></thead>
            <tbody>{GEO_OUTPUT.regStart.map(r=>(<tr key={r.metric} className={`border-b border-[var(--border-glass)]/30 ${!r.metric.startsWith(" ")?"font-semibold":""}`}><td className="px-2 py-1">{r.metric}</td><td className="px-1 py-1 text-center font-mono">{r.Jan}</td><td className="px-1 py-1 text-center font-mono">{r.Feb}</td><td className="px-1 py-1 text-center font-mono">{r.Mar}</td><td className="px-1 py-1 text-center font-mono">{r.Apr}</td><td className="px-1 py-1 text-center font-mono">{r.May}</td><td className="px-1 py-1 text-center font-mono">{r.Jun}</td><td className="px-1 py-1 text-center font-mono">{r.Jul}</td><td className="px-1 py-1 text-center font-mono font-bold">{r.YTD}</td></tr>))}</tbody></table>
          </div>
        </GlassCard>
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">Clean Launch (Monthly)</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs"><thead><tr className="border-b border-[var(--border-glass)]"><th className="px-2 py-1 text-left">Channel</th><th className="px-1 py-1 text-center">Jan</th><th className="px-1 py-1 text-center">Feb</th><th className="px-1 py-1 text-center">Mar</th><th className="px-1 py-1 text-center">Apr</th><th className="px-1 py-1 text-center">May</th><th className="px-1 py-1 text-center">Jun</th><th className="px-1 py-1 text-center">Jul</th><th className="px-1 py-1 text-center font-bold">YTD</th></tr></thead>
            <tbody>{GEO_OUTPUT.cleanLaunch.map(r=>(<tr key={r.metric} className={`border-b border-[var(--border-glass)]/30 ${!r.metric.startsWith(" ")?"font-semibold":""}`}><td className="px-2 py-1">{r.metric}</td><td className="px-1 py-1 text-center font-mono">{r.Jan.toLocaleString()}</td><td className="px-1 py-1 text-center font-mono">{r.Feb.toLocaleString()}</td><td className="px-1 py-1 text-center font-mono">{r.Mar.toLocaleString()}</td><td className="px-1 py-1 text-center font-mono">{r.Apr.toLocaleString()}</td><td className="px-1 py-1 text-center font-mono">{r.May.toLocaleString()}</td><td className="px-1 py-1 text-center font-mono">{r.Jun.toLocaleString()}</td><td className="px-1 py-1 text-center font-mono">{r.Jul.toLocaleString()}</td><td className="px-1 py-1 text-center font-mono font-bold">{r.YTD.toLocaleString()}</td></tr>))}</tbody></table>
          </div>
        </GlassCard>
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">Reg Start → Clean Launch 转化率 (CL_RS%)</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs"><thead><tr className="border-b border-[var(--border-glass)]"><th className="px-2 py-1 text-left">Channel</th><th className="px-1 py-1 text-center">Jan</th><th className="px-1 py-1 text-center">Feb</th><th className="px-1 py-1 text-center">Mar</th><th className="px-1 py-1 text-center">Apr</th><th className="px-1 py-1 text-center">May</th><th className="px-1 py-1 text-center">Jun</th><th className="px-1 py-1 text-center">Jul</th><th className="px-1 py-1 text-center font-bold">YTD</th></tr></thead>
            <tbody>{GEO_OUTPUT.conversion.map(r=>(<tr key={r.metric} className="border-b border-[var(--border-glass)]/30 font-semibold"><td className="px-2 py-1">{r.metric}</td><td className="px-1 py-1 text-center font-mono">{r.Jan}</td><td className="px-1 py-1 text-center font-mono">{r.Feb}</td><td className="px-1 py-1 text-center font-mono">{r.Mar}</td><td className="px-1 py-1 text-center font-mono">{r.Apr}</td><td className="px-1 py-1 text-center font-mono">{r.May}</td><td className="px-1 py-1 text-center font-mono">{r.Jun}</td><td className="px-1 py-1 text-center font-mono">{r.Jul}</td><td className="px-1 py-1 text-center font-mono font-bold">{r.YTD}</td></tr>))}</tbody></table>
          </div>
        </GlassCard>
      </>)}

      {/* ===== TAB: SOURCES ===== */}
      {tab === "sources" && (<>
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">信源分析 — 各平台 TOP5 引用来源（6月）</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {SOURCE_ANALYSIS.map(p=>(
              <div key={p.platform} className="border border-[var(--border-glass)] rounded-lg p-3">
                <p className="text-xs font-bold mb-2 text-[var(--accent)]">{p.platform}</p>
                {p.sources.map((s,i)=>(
                  <div key={i} className="flex items-center justify-between py-0.5">
                    <span className="text-[10px] text-[var(--text-primary)]">{s.name}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-[var(--text-muted)]">{s.url}</span>
                      <span className="text-[10px] font-mono font-bold text-[var(--accent)]">{s.pct}%</span>
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </GlassCard>
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">gs.amazon.cn 官网信源占比对比</h2>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={SOURCE_ANALYSIS.map(p=>({platform:p.platform,gs_pct:p.sources[0].pct}))} margin={{top:5,right:10,left:0,bottom:5}}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="platform" tick={{fontSize:10,fill:"#8892b0"}} />
              <YAxis tick={{fontSize:10,fill:"#8892b0"}} domain={[0,50]} unit="%" />
              <Tooltip contentStyle={{background:"#1a1d2e",border:"1px solid #2a2f4a",borderRadius:8,fontSize:11}} />
              <Bar dataKey="gs_pct" fill="#00bcd4" name="gs.amazon.cn %" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </GlassCard>
      </>)}

      {/* ===== TAB: PHRASES ===== */}
      {tab === "phrases" && (<>
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">检索短语逐条验证数据</h2>
          <p className="text-[10px] text-[var(--text-muted)] mb-3">上传 GEO-SEO Excel 文件（Sheet 3.2）自动解析每条检索短语在各平台的提及情况</p>
          <div className="flex items-center gap-3 mb-3">
            <label className="flex items-center gap-2 px-4 py-2 rounded-lg border border-[var(--accent)]/40 bg-[var(--accent)]/5 cursor-pointer hover:bg-[var(--accent)]/10 transition-colors">
              <span className="text-xs font-medium text-[var(--accent)]">📎 上传 Excel 解析短语数据</span>
              <input type="file" accept=".xlsx,.xls,.csv" onChange={handlePhraseUpload} className="hidden" />
            </label>
            {phraseData.length > 0 && <span className="text-xs text-[var(--success)]">✅ 已加载 {phraseData.length} 条</span>}
          </div>
          {phraseData.length > 0 ? (
            <div className="overflow-x-auto max-h-[500px] overflow-y-auto border border-[var(--border-glass)] rounded-lg">
              <table className="w-full text-[10px]">
                <thead className="sticky top-0 bg-[var(--bg-surface)] z-10">
                  <tr className="border-b border-[var(--border-glass)]">
                    <th className="px-2 py-1.5 text-left text-[var(--text-muted)] min-w-[40px]">#</th>
                    <th className="px-2 py-1.5 text-left text-[var(--text-muted)] min-w-[60px]">分类</th>
                    <th className="px-2 py-1.5 text-left text-[var(--text-muted)] min-w-[200px]">检索短语</th>
                    <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">元宝</th>
                    <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">DeepSeek</th>
                    <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">豆包</th>
                    <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">ChatGPT</th>
                    <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">Kimi</th>
                    <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">千问</th>
                    <th className="px-2 py-1.5 text-center text-[var(--text-muted)]">Gemini</th>
                  </tr>
                </thead>
                <tbody>
                  {phraseData.map((row, idx) => (
                    <tr key={idx} className="border-b border-[var(--border-glass)]/20 hover:bg-white/5">
                      <td className="px-2 py-1 text-[var(--text-muted)]">{idx + 1}</td>
                      <td className="px-2 py-1"><span className={`text-[9px] px-1 py-0.5 rounded ${row.category === "入口" ? "bg-blue-500/10 text-blue-400" : row.category === "入驻&注册" ? "bg-purple-500/10 text-purple-400" : row.category === "费用" ? "bg-yellow-500/10 text-yellow-400" : "bg-white/10 text-[var(--text-muted)]"}`}>{row.category}</span></td>
                      <td className="px-2 py-1 text-[var(--text-primary)] max-w-[250px] truncate">{row.phrase}</td>
                      <td className="px-2 py-1 text-center">{row.yuanbao ? "✅" : "❌"}</td>
                      <td className="px-2 py-1 text-center">{row.deepseek ? "✅" : "❌"}</td>
                      <td className="px-2 py-1 text-center">{row.doubao ? "✅" : "❌"}</td>
                      <td className="px-2 py-1 text-center">{row.chatgpt ? "✅" : "❌"}</td>
                      <td className="px-2 py-1 text-center">{row.kimi ? "✅" : "❌"}</td>
                      <td className="px-2 py-1 text-center">{row.qianwen ? "✅" : "❌"}</td>
                      <td className="px-2 py-1 text-center">{row.gemini ? "✅" : "❌"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-xs text-[var(--text-muted)]">
              <p>暂无逐条短语数据。请上传 GEO-SEO Excel 文件。</p>
              <p className="mt-1 text-[10px]">支持格式：Sheet 3.2 的 CN+NA 短语详情表</p>
            </div>
          )}
        </GlassCard>
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">检索短语提及数 by 类别 × 平台（6月汇总）</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs"><thead><tr className="border-b border-[var(--border-glass)]"><th className="px-2 py-1 text-left">分类</th><th className="px-1 py-1 text-center">总量</th><th className="px-1 py-1 text-center">元宝</th><th className="px-1 py-1 text-center">DeepSeek</th><th className="px-1 py-1 text-center">豆包</th><th className="px-1 py-1 text-center">ChatGPT</th><th className="px-1 py-1 text-center">Kimi</th><th className="px-1 py-1 text-center">千问</th></tr></thead>
            <tbody>{PHRASE_CATEGORIES.map(r=>(<tr key={r.category} className="border-b border-[var(--border-glass)]/30"><td className="px-2 py-1 font-medium">{r.category}</td><td className="px-1 py-1 text-center">{r.total}</td><td className="px-1 py-1 text-center font-mono">{r.jun_元宝}</td><td className="px-1 py-1 text-center font-mono">{r.jun_DeepSeek}</td><td className="px-1 py-1 text-center font-mono">{r.jun_豆包}</td><td className="px-1 py-1 text-center font-mono">{r.jun_ChatGPT}</td><td className="px-1 py-1 text-center font-mono">{r.jun_Kimi}</td><td className="px-1 py-1 text-center font-mono">{r.jun_千问}</td></tr>))}</tbody></table>
          </div>
        </GlassCard>
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">语义范围覆盖率（6月）</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs"><thead><tr className="border-b border-[var(--border-glass)]"><th className="px-2 py-1 text-left">语义分类</th><th className="px-1 py-1 text-center">Total</th><th className="px-1 py-1 text-center">元宝</th><th className="px-1 py-1 text-center">DeepSeek</th><th className="px-1 py-1 text-center">豆包</th><th className="px-1 py-1 text-center">ChatGPT</th><th className="px-1 py-1 text-center">Kimi</th><th className="px-1 py-1 text-center">千问</th></tr></thead>
            <tbody>{SEMANTIC_COVERAGE.map(r=>(<tr key={r.category} className="border-b border-[var(--border-glass)]/30"><td className="px-2 py-1">{r.category}</td><td className="px-1 py-1 text-center">{r.total}</td><td className="px-1 py-1 text-center font-mono">{r.rate_元宝}</td><td className="px-1 py-1 text-center font-mono">{r.rate_DeepSeek}</td><td className="px-1 py-1 text-center font-mono">{r.rate_豆包}</td><td className="px-1 py-1 text-center font-mono">{r.rate_ChatGPT}</td><td className="px-1 py-1 text-center font-mono">{r.rate_Kimi}</td><td className="px-1 py-1 text-center font-mono">{r.rate_千问}</td></tr>))}</tbody></table>
          </div>
        </GlassCard>
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">Input Summary — 月度汇总</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-xs"><thead><tr className="border-b border-[var(--border-glass)]">{INPUT_SUMMARY.headers.map(h=>(<th key={h} className="px-2 py-1 text-center">{h}</th>))}</tr></thead>
            <tbody>{INPUT_SUMMARY.rows.map((r,i)=>(<tr key={i} className="border-b border-[var(--border-glass)]/30">{r.map((c,j)=>(<td key={j} className={`px-2 py-1 text-center font-mono ${j===0?"text-left font-medium":""}`}>{c}</td>))}</tr>))}</tbody></table>
          </div>
        </GlassCard>
      </>)}

      {/* Attribution */}
      <GlassCard><details><summary className="text-sm font-medium text-[var(--text-secondary)] cursor-pointer">💡 {isZh?"归因 & Opportunities":"Attribution & Opportunities"}</summary><div className="mt-3 text-xs text-[var(--text-secondary)] space-y-1">
        <p>• CN GEO YTD +419% — GEO 策略持续有效，AI referrer 稳步增长</p>
        <p>• WW Direct YTD +60% vs SSR -17% — 跑赢大盘 77 ppts</p>
        <p>• 官网链接提及率从 18.1%→51.6%（Dec→M6），持续提升</p>
        <p>• 元宝最高 75.4%，ChatGPT 最低 28.5% — 国内平台效果优于海外</p>
        <p className="font-medium mt-2">🚀 Next Actions:</p>
        <p>• 扩大 EU/JP keyword 覆盖 | JP +113% YoY 增速最快</p>
        <p>• 提升 ChatGPT/Gemini 链接率（目前最低）</p>
        <p>• 建立 WK30+ 自动数据刷新机制</p>
      </div></details></GlassCard>
    </div>
  );
}
