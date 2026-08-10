"use client";

import Link from "next/link";
import { useI18nStore } from "@/stores/i18n-store";
import { useBatchStore } from "@/stores/batch-store";
import { usePipelineStore } from "@/stores/pipeline-store";
import { useEffect } from "react";
import { GlassCard } from "@/components/ui/GlassCard";
import { PipelineFlow } from "@/components/layout/PipelineFlow";
import { PIPELINE_MODULES } from "@/lib/constants";

export default function OverviewPage() {
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

  return (
    <div className="space-y-8 max-w-[1400px]">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-2xl border border-[var(--border-glass)] bg-gradient-to-br from-[var(--bg-secondary)] to-[#0d1a2e] p-8">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-4 left-8 w-32 h-32 bg-[var(--accent)]/20 rounded-full blur-3xl" />
          <div className="absolute bottom-4 right-12 w-24 h-24 bg-purple-500/15 rounded-full blur-3xl" />
        </div>
        <div className="relative z-10">
          <h1 className="text-2xl font-bold text-[var(--text-primary)] mb-2">
            {t("overview.title")}
          </h1>
          <p className="text-sm text-[var(--text-secondary)]">
            {t("overview.subtitle")}
          </p>
          <div className="mt-4 flex items-center gap-4 text-xs text-[var(--text-muted)]">
            <span className="px-2 py-1 rounded bg-[var(--accent)]/10 text-[var(--accent)] font-medium">
              {activeBatch}
            </span>
            <span>{PIPELINE_MODULES.length} {t("overview.goto")} modules</span>
          </div>
        </div>
      </div>

      {/* Pipeline Flow */}
      <GlassCard>
        <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
          {t("overview.pipeline_title")}
        </h2>
        <PipelineFlow steps={steps} />
      </GlassCard>

      {/* Module Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {PIPELINE_MODULES.map((mod) => (
          <Link key={mod.id} href={mod.path}>
            <GlassCard
              className="h-full hover:border-[var(--accent)]/40 transition-all duration-300 hover:-translate-y-1 cursor-pointer group"
              padding="md"
            >
              <div className="flex items-start gap-3">
                <span
                  className="text-2xl w-10 h-10 flex items-center justify-center rounded-lg"
                  style={{ background: `${mod.color}15` }}
                >
                  {mod.icon}
                </span>
                <div className="flex-1 min-w-0">
                  <h3
                    className="text-sm font-semibold group-hover:text-[var(--accent)] transition-colors"
                    style={{ color: mod.color }}
                  >
                    {t(`nav.${mod.id}`)}
                  </h3>
                  <p className="text-xs text-[var(--text-muted)] mt-1 line-clamp-2">
                    {t(mod.descKey)}
                  </p>
                </div>
              </div>
            </GlassCard>
          </Link>
        ))}
      </div>

      {/* Quick Start */}
      <GlassCard>
        <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-4">
          {t("overview.quick_start")}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link href="/zhiku" className="block">
            <div className="p-4 rounded-lg bg-[#ffa726]/5 border border-[#ffa726]/20 hover:border-[#ffa726]/50 transition-colors">
              <p className="text-xs font-medium text-[#ffa726] mb-1">Step 1</p>
              <p className="text-sm text-[var(--text-primary)]">
                {t("overview.zhiku_desc")}
              </p>
            </div>
          </Link>
          <Link href="/zhice" className="block">
            <div className="p-4 rounded-lg bg-[var(--accent)]/5 border border-[var(--accent)]/20 hover:border-[var(--accent)]/50 transition-colors">
              <p className="text-xs font-medium text-[var(--accent)] mb-1">Step 2</p>
              <p className="text-sm text-[var(--text-primary)]">
                {t("overview.zhice_desc")}
              </p>
            </div>
          </Link>
          <Link href="/zhizao" className="block">
            <div className="p-4 rounded-lg bg-[#ffcc02]/5 border border-[#ffcc02]/20 hover:border-[#ffcc02]/50 transition-colors">
              <p className="text-xs font-medium text-[#ffcc02] mb-1">Step 3</p>
              <p className="text-sm text-[var(--text-primary)]">
                {t("overview.zhizao_desc")}
              </p>
            </div>
          </Link>
        </div>
      </GlassCard>
    </div>
  );
}
