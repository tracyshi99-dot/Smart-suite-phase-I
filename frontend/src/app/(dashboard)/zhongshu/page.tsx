"use client";

import { useEffect } from "react";
import { useI18nStore } from "@/stores/i18n-store";
import { useBatchStore } from "@/stores/batch-store";
import { usePipelineStore } from "@/stores/pipeline-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { BatchSelector } from "@/components/ui/BatchSelector";
import { PipelineFlow } from "@/components/layout/PipelineFlow";

export default function ZhongshuPage() {
  const { t } = useI18nStore();
  const { activeBatch } = useBatchStore();
  const { status, fetchStatus } = usePipelineStore();

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

  return (
    <div className="space-y-6 max-w-[1400px]">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{t("zhongshu.title")}</h1>
        <BatchSelector />
      </div>

      {/* Pipeline Flow */}
      <GlassCard>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-medium text-[var(--text-secondary)]">Pipeline Progress</h2>
          <span className="text-xs text-[var(--accent)]">{completedSteps}/4 steps</span>
        </div>
        <PipelineFlow steps={steps} />
      </GlassCard>

      {/* Batch Overview */}
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
    </div>
  );
}
