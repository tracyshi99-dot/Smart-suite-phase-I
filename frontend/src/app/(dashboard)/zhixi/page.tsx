"use client";

import { useState, useEffect } from "react";
import { useI18nStore } from "@/stores/i18n-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { MetricCard } from "@/components/ui/MetricCard";
import { apiGet } from "@/lib/api-client";
import { MetricsResponse } from "@/lib/types";

export default function ZhixiPage() {
  const { t } = useI18nStore();
  const [monthlyData, setMonthlyData] = useState<Record<string, unknown>[]>([]);
  const [citations, setCitations] = useState<Record<string, unknown>[]>([]);
  const [summary, setSummary] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [monthly, cite, sum] = await Promise.all([
          apiGet<MetricsResponse>("/api/zhixi/monthly"),
          apiGet<MetricsResponse>("/api/zhixi/citations"),
          apiGet<{ data: Record<string, unknown>[] }>("/api/zhixi/summary"),
        ]);
        setMonthlyData(monthly.data);
        setCitations(cite.data);
        setSummary(sum.data);
      } catch {
        // Keep existing data on error
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <div className="space-y-6 max-w-[1400px]">
      <h1 className="text-xl font-bold">{t("zhixi.title")}</h1>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="CN GEO YTD" value="574" change={452} changeLabel="YoY" trend="up" />
        <MetricCard label="WW GEO YTD" value="364" change={94} changeLabel="YoY" trend="up" />
        <MetricCard label="WW Direct EST" value="25,863" change={62} changeLabel="YoY" trend="up" />
        <MetricCard label="GEO+Direct Total" value="28,741" change={55} changeLabel="YoY" trend="up" />
      </div>

      {/* Trend Chart placeholder */}
      <GlassCard>
        <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">Weekly Trend - Reg Start</h2>
        {loading ? (
          <div className="h-48 flex items-center justify-center text-[var(--text-muted)]">
            {t("common.loading")}
          </div>
        ) : monthlyData.length === 0 ? (
          <div className="h-48 flex items-center justify-center text-[var(--text-muted)]">
            {t("common.empty")}
          </div>
        ) : (
          <div className="h-48 flex items-center justify-center text-[var(--text-muted)]">
            📊 Chart will render here (Recharts integration pending)
            <br />
            Data points: {monthlyData.length}
          </div>
        )}
      </GlassCard>

      {/* Citations Table */}
      <GlassCard>
        <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">Citation Tracking</h2>
        {citations.length === 0 ? (
          <div className="py-6 text-center text-[var(--text-muted)]">{t("common.empty")}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border-glass)]">
                  <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">Phrase</th>
                  <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">Platform</th>
                  <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">Status</th>
                  <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">Date</th>
                </tr>
              </thead>
              <tbody>
                {citations.slice(0, 20).map((row, idx) => (
                  <tr key={idx} className="border-b border-[var(--border-glass)]/50 hover:bg-white/5">
                    <td className="px-2 py-2">{String(row.phrase ?? row.ai_query ?? "")}</td>
                    <td className="px-2 py-2 text-[var(--text-secondary)]">{String(row.platform ?? "")}</td>
                    <td className="px-2 py-2">{String(row.citation_status ?? row.status ?? "")}</td>
                    <td className="px-2 py-2 text-[var(--text-muted)]">{String(row.verification_date ?? row.date ?? "")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>

      {/* Input Summary */}
      {summary.length > 0 && (
        <GlassCard>
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">GEO Input Summary</h2>
          <pre className="text-xs text-[var(--text-muted)] overflow-auto">
            {JSON.stringify(summary, null, 2)}
          </pre>
        </GlassCard>
      )}
    </div>
  );
}
