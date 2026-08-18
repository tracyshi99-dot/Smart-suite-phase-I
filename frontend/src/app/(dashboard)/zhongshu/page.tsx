"use client";

import { useEffect, useState } from "react";
import { useI18nStore } from "@/stores/i18n-store";
import { useBatchStore } from "@/stores/batch-store";
import { usePipelineStore } from "@/stores/pipeline-store";
import { useAuthStore } from "@/stores/auth-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { PipelineFlow } from "@/components/layout/PipelineFlow";
import { Button } from "@/components/ui/Button";
import { DecisionEngine } from "@/components/zhongshu/DecisionEngine";

export default function ZhongshuPage() {
  const { t, locale } = useI18nStore();
  const { activeBatch } = useBatchStore();
  const { status, fetchStatus } = usePipelineStore();
  const { isAdmin, user } = useAuthStore();
  const isZh = locale.startsWith("zh");

  const [activeTab, setActiveTab] = useState<"pipeline" | "decision" | "settings">("decision");

  useEffect(() => {
    fetchStatus(activeBatch);
  }, [activeBatch, fetchStatus]);

  const steps = status[activeBatch] ?? [
    { id: "01_zhiku", label: "智库", status: "pending" as const },
    { id: "02_zhizao", label: "智造", status: "pending" as const },
    { id: "03_zhiyou", label: "智优", status: "pending" as const },
    { id: "04_zhibu", label: "智布", status: "pending" as const },
  ];

  const completedSteps = steps.filter((s) => s.status === "complete").length;

  const tabs = [
    { id: "pipeline" as const, label: isZh ? "管线状态" : "Pipeline" },
    { id: "decision" as const, label: isZh ? "决策引擎" : "Decision Engine" },
    { id: "settings" as const, label: isZh ? "系统设置" : "Settings" },
  ];

  return (
    <div className="space-y-6 max-w-[1400px]">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{t("zhongshu.title")}</h1>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-[var(--border-glass)]">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
              activeTab === tab.id
                ? "bg-[var(--accent)]/10 text-[var(--accent)] border border-[var(--accent)]/30 border-b-transparent"
                : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/5"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Pipeline Tab */}
      {activeTab === "pipeline" && (
        <>
          <GlassCard>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-medium text-[var(--text-secondary)]">{isZh ? "管线进度" : "Pipeline Progress"}</h2>
              <span className="text-xs text-[var(--accent)]">{completedSteps}/4 steps</span>
            </div>
            <PipelineFlow steps={steps} />
          </GlassCard>

          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">{isZh ? "GEO Input 总览 (YTD Jun)" : "GEO Input Summary (YTD Jun)"}</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div><p className="text-xs text-[var(--text-muted)]">{isZh ? "提示词总数" : "Total Phrases"}</p><p className="text-xl font-bold text-[var(--accent)]">646</p><p className="text-[10px] text-[var(--text-muted)]">{isZh ? "品牌487 + 行业159" : "Brand 487 + Industry 159"}</p></div>
              <div><p className="text-xs text-[var(--text-muted)]">{isZh ? "品牌提及数" : "Brand Mentions"}</p><p className="text-xl font-bold text-[var(--success)]">1,948</p><p className="text-[10px] text-[var(--text-muted)]">{isZh ? "7平台×487词" : "7 platforms × 487"}</p></div>
              <div><p className="text-xs text-[var(--text-muted)]">{isZh ? "链接提及数" : "Link Mentions"}</p><p className="text-xl font-bold text-[var(--warning)]">1,108</p><p className="text-[10px] text-[var(--text-muted)]">{isZh ? "提及率 56.88%" : "Rate 56.88%"}</p></div>
              <div><p className="text-xs text-[var(--text-muted)]">{isZh ? "新建内容" : "New Content"}</p><p className="text-xl font-bold">648</p><p className="text-[10px] text-[var(--text-muted)]">YTD</p></div>
            </div>
          </GlassCard>

          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">{isZh ? "月度 Input 进度" : "Monthly Input Progress"}</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-xs"><thead><tr className="border-b border-[var(--border-glass)]"><th className="px-2 py-1 text-left">{isZh ? "指标" : "Metric"}</th><th className="px-2 py-1 text-center">Jan</th><th className="px-2 py-1 text-center">Feb</th><th className="px-2 py-1 text-center">Mar</th><th className="px-2 py-1 text-center">Apr</th><th className="px-2 py-1 text-center">May</th><th className="px-2 py-1 text-center">Jun</th></tr></thead>
              <tbody>
                {([
                  [isZh ? "提示词#" : "Phrases#", 297, 297, 297, 397, 564, 646],
                  [isZh ? "品牌提及#" : "Brand#", 1188, 1188, 1188, 1588, 1860, 1948],
                  [isZh ? "链接提及#" : "Links#", 582, 635, 719, 852, 1019, 1108],
                  [isZh ? "链接率" : "Rate", "49.0%", "53.5%", "60.5%", "53.7%", "54.8%", "56.9%"],
                  [isZh ? "新建内容#" : "Content#", 98, 43, 118, 123, 135, 131],
                ] as (string | number)[][]).map((row) => (
                  <tr key={String(row[0])} className="border-b border-[var(--border-glass)]/30"><td className="px-2 py-1 font-medium">{row[0]}</td>{row.slice(1).map((v, i) => <td key={i} className="px-2 py-1 text-center font-mono">{v}</td>)}</tr>
                ))}
              </tbody></table>
            </div>
          </GlassCard>

          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">{isZh ? "各平台链接提及率 (Jun)" : "Platform Link Rate (Jun)"}</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[{n:"元宝",r:"75.4%",c:367},{n:"DeepSeek",r:"66.7%",c:325},{n:"千问",r:"66.9%",c:326},{n:"豆包",r:"56.9%",c:277},{n:"Kimi",r:"53.4%",c:260},{n:"Gemini",r:"44.8%",c:218},{n:"ChatGPT",r:"28.5%",c:139}].map(p=>(
                <div key={p.n} className="p-2 rounded-lg bg-white/5 border border-[var(--border-glass)]/30 text-center"><p className="text-xs font-medium">{p.n}</p><p className="text-sm font-bold text-[var(--accent)] mt-1">{p.r}</p><p className="text-[10px] text-[var(--text-muted)]">{p.c} links</p></div>
              ))}
            </div>
          </GlassCard>

          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">{isZh ? "行业词进展 (May→Jun)" : "Industry Keywords (May→Jun)"}</h2>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div><p className="text-xs text-[var(--text-muted)]">{isZh ? "行业提示词" : "Industry Phrases"}</p><p className="text-xl font-bold text-[var(--accent)]">159</p><p className="text-[10px] text-[var(--text-muted)]">98 → 159</p></div>
              <div><p className="text-xs text-[var(--text-muted)]">{isZh ? "行业词提及" : "Mentions"}</p><p className="text-xl font-bold text-[var(--success)]">414</p><p className="text-[10px] text-[var(--text-muted)]">51 → 414</p></div>
              <div><p className="text-xs text-[var(--text-muted)]">{isZh ? "提及率" : "Rate"}</p><p className="text-xl font-bold text-[var(--warning)]">37.2%</p><p className="text-[10px] text-[var(--text-muted)]">7.4% → 37.2%</p></div>
            </div>
          </GlassCard>
        </>
      )}

      {/* Decision Engine Tab */}
      {activeTab === "decision" && <DecisionEngine isZh={isZh} />}

      {/* Settings Tab */}
      {activeTab === "settings" && (
        <>
          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-4">{isZh ? "区域配置" : "Region Configuration"}</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div><p className="text-xs text-[var(--text-muted)]">{isZh ? "当前用户" : "User"}</p><p className="font-medium">{user}</p></div>
              <div><p className="text-xs text-[var(--text-muted)]">{isZh ? "权限" : "Role"}</p><p className="font-medium">{isAdmin ? "Admin" : "User"}</p></div>
              <div><p className="text-xs text-[var(--text-muted)]">{isZh ? "活跃批次" : "Batch"}</p><p className="text-[var(--accent)] font-medium">{activeBatch}</p></div>
              <div><p className="text-xs text-[var(--text-muted)]">{isZh ? "语言" : "Language"}</p><p className="font-medium">{locale}</p></div>
            </div>
          </GlassCard>
          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-4">{isZh ? "系统信息" : "System Info"}</h2>
            <div className="space-y-2 text-xs text-[var(--text-muted)]">
              <p>• Frontend: Next.js 16.3 + React 19 + Zustand</p>
              <p>• Backend: FastAPI + Mangum (Lambda)</p>
              <p>• API: {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}</p>
              <p>• Deploy: Vercel (FE) + AWS Lambda (API)</p>
            </div>
          </GlassCard>
        </>
      )}
    </div>
  );
}
