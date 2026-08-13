"use client";

import { useEffect, useState } from "react";
import { useI18nStore } from "@/stores/i18n-store";
import { useBatchStore } from "@/stores/batch-store";
import { usePipelineStore } from "@/stores/pipeline-store";
import { useAuthStore } from "@/stores/auth-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { BatchSelector } from "@/components/ui/BatchSelector";
import { PipelineFlow } from "@/components/layout/PipelineFlow";
import { Button } from "@/components/ui/Button";
import { apiGet } from "@/lib/api-client";
import { PhraseListResponse } from "@/lib/types";

export default function ZhongshuPage() {
  const { t, locale } = useI18nStore();
  const { activeBatch } = useBatchStore();
  const { status, fetchStatus } = usePipelineStore();
  const { isAdmin, user } = useAuthStore();
  const isZh = locale.startsWith("zh");

  const [activeTab, setActiveTab] = useState<"pipeline" | "settings">("pipeline");
  const [batchStats, setBatchStats] = useState({ phrases: 0, selected: 0, articles: 0 });

  useEffect(() => {
    fetchStatus(activeBatch);
  }, [activeBatch, fetchStatus]);

  // Load batch stats
  useEffect(() => {
    async function loadStats() {
      try {
        const res = await apiGet<PhraseListResponse>("/api/zhiku/phrases", {
          batch_id: activeBatch,
          user: user ?? "",
        });
        const selected = res.phrases.filter((p) => p.is_selected === "TRUE").length;
        setBatchStats({ phrases: res.total, selected, articles: 0 });
      } catch {
        // ignore
      }
    }
    loadStats();
  }, [activeBatch, user]);

  const steps = status[activeBatch] ?? [
    { id: "01_zhiku", label: "智库", status: "pending" as const },
    { id: "02_zhizao", label: "智造", status: "pending" as const },
    { id: "03_zhiyou", label: "智优", status: "pending" as const },
    { id: "04_zhibu", label: "智布", status: "pending" as const },
  ];

  const completedSteps = steps.filter((s) => s.status === "complete").length;

  const tabs = [
    { id: "pipeline" as const, label: isZh ? "管线状态" : "Pipeline" },
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
          {/* Pipeline Flow */}
          <GlassCard>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-medium text-[var(--text-secondary)]">
                {isZh ? "管线进度" : "Pipeline Progress"}
              </h2>
              <span className="text-xs text-[var(--accent)]">{completedSteps}/4 steps</span>
            </div>
            <PipelineFlow steps={steps} />
          </GlassCard>

          {/* Batch Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {steps.map((step) => (
              <GlassCard key={step.id} padding="sm" glow={step.status === "active"}>
                <p className="text-xs text-[var(--text-secondary)]">{step.label}</p>
                <p className="text-lg font-bold mt-1">
                  {step.status === "complete" ? (
                    <span className="text-[var(--success)]">✓</span>
                  ) : step.status === "active" ? (
                    <span className="text-[var(--accent)]">●</span>
                  ) : (
                    <span className="text-[var(--text-muted)]">○</span>
                  )}
                </p>
                {step.fileCount !== undefined && (
                  <p className="text-xs text-[var(--text-muted)] mt-1">{step.fileCount} files</p>
                )}
              </GlassCard>
            ))}
          </div>

          {/* Batch Summary */}
          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
              {isZh ? "批次概览" : "Batch Summary"} — {activeBatch}
            </h2>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-xs text-[var(--text-muted)]">{isZh ? "总短语" : "Total Phrases"}</p>
                <p className="text-xl font-bold text-[var(--accent)]">{batchStats.phrases}</p>
              </div>
              <div>
                <p className="text-xs text-[var(--text-muted)]">{isZh ? "已选中" : "Selected"}</p>
                <p className="text-xl font-bold text-[var(--success)]">{batchStats.selected}</p>
              </div>
              <div>
                <p className="text-xs text-[var(--text-muted)]">{isZh ? "已生成内容" : "Articles"}</p>
                <p className="text-xl font-bold">{batchStats.articles}</p>
              </div>
            </div>
          </GlassCard>
        </>
      )}

      {/* Settings Tab */}
      {activeTab === "settings" && (
        <>
          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-4">
              {isZh ? "区域配置" : "Region Configuration"}
            </h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-xs text-[var(--text-muted)]">{isZh ? "当前用户" : "Current User"}</p>
                <p className="text-[var(--text-primary)] font-medium">{user}</p>
              </div>
              <div>
                <p className="text-xs text-[var(--text-muted)]">{isZh ? "权限" : "Role"}</p>
                <p className="text-[var(--text-primary)] font-medium">
                  {isAdmin ? (isZh ? "管理员" : "Admin") : (isZh ? "用户" : "User")}
                </p>
              </div>
              <div>
                <p className="text-xs text-[var(--text-muted)]">{isZh ? "活跃批次" : "Active Batch"}</p>
                <p className="text-[var(--accent)] font-medium">{activeBatch}</p>
              </div>
              <div>
                <p className="text-xs text-[var(--text-muted)]">{isZh ? "界面语言" : "UI Language"}</p>
                <p className="text-[var(--text-primary)] font-medium">{locale}</p>
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-4">
              {isZh ? "系统信息" : "System Info"}
            </h2>
            <div className="space-y-2 text-xs text-[var(--text-muted)]">
              <p>• Frontend: Next.js 16.3 + React 19 + Zustand + Recharts</p>
              <p>• Backend: FastAPI + Mangum (Lambda)</p>
              <p>• API: {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}</p>
              <p>• Deploy: Vercel (Frontend) + AWS Lambda (API)</p>
            </div>
          </GlassCard>

          {isAdmin && (
            <GlassCard>
              <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-4">
                {isZh ? "管理员操作" : "Admin Actions"}
              </h2>
              <div className="space-y-3">
                <Button onClick={() => window.open("https://smartsuite-geo.vercel.app", "_blank")}>
                  {isZh ? "打开 Vercel 面板" : "Open Vercel Dashboard"}
                </Button>
                <p className="text-xs text-[var(--text-muted)]">
                  {isZh
                    ? "用户管理、批次管理等高级功能请使用 Streamlit 版本或直接编辑 users.json"
                    : "User management and advanced features available in Streamlit or via users.json"
                  }
                </p>
              </div>
            </GlassCard>
          )}
        </>
      )}
    </div>
  );
}
