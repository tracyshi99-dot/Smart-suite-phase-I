"use client";

import { useState, useEffect } from "react";
import { useI18nStore } from "@/stores/i18n-store";
import { useBatchStore } from "@/stores/batch-store";
import { useAuthStore } from "@/stores/auth-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { BatchSelector } from "@/components/ui/BatchSelector";
import { apiGet } from "@/lib/api-client";
import { MetricsResponse, PhraseListResponse } from "@/lib/types";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend,
} from "recharts";

export default function ZhixiPage() {
  const { t, locale } = useI18nStore();
  const { activeBatch } = useBatchStore();
  const { user } = useAuthStore();
  const isZh = locale.startsWith("zh");

  const [monthlyData, setMonthlyData] = useState<Record<string, unknown>[]>([]);
  const [citations, setCitations] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  // User's own stats
  const [totalPhrases, setTotalPhrases] = useState(0);
  const [selectedPhrases, setSelectedPhrases] = useState(0);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const [monthly, cite, phrases] = await Promise.all([
          apiGet<MetricsResponse>("/api/zhixi/monthly"),
          apiGet<MetricsResponse>("/api/zhixi/citations"),
          apiGet<PhraseListResponse>("/api/zhiku/phrases", {
            batch_id: activeBatch,
            user: user ?? "",
          }),
        ]);
        setMonthlyData(monthly.data);
        setCitations(cite.data);
        setTotalPhrases(phrases.total);
        setSelectedPhrases(
          phrases.phrases.filter((p) => p.is_selected === "TRUE").length
        );
      } catch {
        // Keep existing
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [activeBatch, user]);

  // Compute citation metrics from results
  const totalCitations = citations.length;
  const withBrand = citations.filter(
    (r) => String(r.has_brand_mention ?? r.brand_mention ?? "").toUpperCase() === "TRUE"
  ).length;
  const withLink = citations.filter(
    (r) => String(r.has_official_link ?? r.official_link ?? "").toUpperCase() === "TRUE"
  ).length;
  const brandRate = totalCitations > 0 ? Math.round((withBrand / totalCitations) * 100) : 0;
  const linkRate = totalCitations > 0 ? Math.round((withLink / totalCitations) * 100) : 0;

  return (
    <div className="space-y-6 max-w-[1400px]">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{t("zhixi.title")}</h1>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
        <GlassCard padding="sm" className="text-center">
          <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-wide">{isZh ? "总短语" : "Phrases"}</p>
          <p className="text-lg font-bold text-[var(--accent)]">{totalPhrases}</p>
        </GlassCard>
        <GlassCard padding="sm" className="text-center">
          <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-wide">{isZh ? "已选中" : "Selected"}</p>
          <p className="text-lg font-bold text-[var(--success)]">{selectedPhrases}</p>
        </GlassCard>
        <GlassCard padding="sm" className="text-center">
          <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-wide">{isZh ? "验证数" : "Tested"}</p>
          <p className="text-lg font-bold">{totalCitations}</p>
        </GlassCard>
        <GlassCard padding="sm" className="text-center">
          <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-wide">{isZh ? "品牌提及率" : "Brand Rate"}</p>
          <p className="text-lg font-bold text-[var(--accent)]">{brandRate}%</p>
        </GlassCard>
        <GlassCard padding="sm" className="text-center">
          <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-wide">{isZh ? "链接率" : "Link Rate"}</p>
          <p className="text-lg font-bold text-[var(--success)]">{linkRate}%</p>
        </GlassCard>
        <GlassCard padding="sm" className="text-center">
          <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-wide">{isZh ? "缺口率" : "Gap Rate"}</p>
          <p className="text-lg font-bold text-[var(--error)]">{totalCitations > 0 ? 100 - linkRate : 0}%</p>
        </GlassCard>
      </div>

      {/* Trend Chart */}
      <GlassCard>
        <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
          {isZh ? "月度趋势" : "Monthly Trend"}
        </h2>
        {loading ? (
          <div className="h-64 flex items-center justify-center text-[var(--text-muted)]">
            {t("common.loading")}
          </div>
        ) : monthlyData.length === 0 ? (
          <div className="h-64 flex items-center justify-center text-[var(--text-muted)]">
            {t("common.empty")}
          </div>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={monthlyData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis
                  dataKey="month"
                  stroke="#7b8ab8"
                  fontSize={11}
                  tickLine={false}
                />
                <YAxis stroke="#7b8ab8" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    background: "rgba(10,14,26,0.95)",
                    border: "1px solid rgba(255,255,255,0.1)",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
                <Legend wrapperStyle={{ fontSize: "11px" }} />
                <Line type="monotone" dataKey="cn_geo" name="CN GEO" stroke="#ffa726" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="ww_geo" name="WW GEO" stroke="#00d4aa" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="ww_direct" name="WW Direct" stroke="#29b6f6" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </GlassCard>

      {/* Citation Performance Table */}
      <GlassCard>
        <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
          {isZh ? "AI 引用验证结果" : "Citation Performance"}
        </h2>
        {citations.length === 0 ? (
          <div className="py-8 text-center text-[var(--text-muted)]">
            {isZh ? "暂无验证数据，请先到智测运行验证" : "No verification data yet. Run verification in the Verify tab."}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border-glass)]">
                  <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">{isZh ? "检索短语" : "Query"}</th>
                  <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">{isZh ? "平台" : "Platform"}</th>
                  <th className="px-2 py-2 text-center text-xs text-[var(--text-secondary)]">{isZh ? "品牌提及" : "Brand"}</th>
                  <th className="px-2 py-2 text-center text-xs text-[var(--text-secondary)]">{isZh ? "官方链接" : "Link"}</th>
                  <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">{isZh ? "Gap 状态" : "Gap Status"}</th>
                </tr>
              </thead>
              <tbody>
                {citations.slice(0, 50).map((row, idx) => {
                  const brand = String(row.has_brand_mention ?? row.brand_mention ?? "").toUpperCase() === "TRUE";
                  const link = String(row.has_official_link ?? row.official_link ?? "").toUpperCase() === "TRUE";
                  const gapStatus = !link && !brand ? "full_gap" : !link ? "partial_gap" : "covered";
                  return (
                    <tr key={idx} className="border-b border-[var(--border-glass)]/50 hover:bg-white/5">
                      <td className="px-2 py-2 max-w-[250px] truncate">
                        {String(row.ai_query ?? row.phrase ?? row.query ?? "")}
                      </td>
                      <td className="px-2 py-2 text-[var(--text-secondary)]">
                        {String(row.platform ?? "")}
                      </td>
                      <td className="px-2 py-2 text-center">
                        <span className={brand ? "text-[var(--success)]" : "text-[var(--error)]"}>
                          {brand ? "✅" : "❌"}
                        </span>
                      </td>
                      <td className="px-2 py-2 text-center">
                        <span className={link ? "text-[var(--success)]" : "text-[var(--error)]"}>
                          {link ? "✅" : "❌"}
                        </span>
                      </td>
                      <td className="px-2 py-2">
                        <span className={`text-xs px-1.5 py-0.5 rounded ${
                          gapStatus === "full_gap" ? "bg-red-500/10 text-red-400"
                            : gapStatus === "partial_gap" ? "bg-yellow-500/10 text-yellow-400"
                            : "bg-green-500/10 text-green-400"
                        }`}>
                          {gapStatus === "full_gap" ? (isZh ? "完全缺口" : "Full Gap")
                            : gapStatus === "partial_gap" ? (isZh ? "部分缺口" : "Partial")
                            : (isZh ? "已覆盖" : "Covered")}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {citations.length > 50 && (
              <p className="text-xs text-[var(--text-muted)] mt-2 text-center">
                {isZh ? `显示前 50 条，共 ${citations.length} 条` : `Showing 50 of ${citations.length}`}
              </p>
            )}
          </div>
        )}
      </GlassCard>

      {/* Insights */}
      {totalCitations > 0 && (
        <GlassCard>
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">💡 Insights</h2>
          <ul className="text-xs text-[var(--text-primary)] space-y-1.5">
            <li>• {isZh ? "品牌提及率" : "Brand Mention Rate"}: <strong>{brandRate}%</strong> ({withBrand}/{totalCitations})</li>
            <li>• {isZh ? "官方链接率" : "Official Link Rate"}: <strong>{linkRate}%</strong> ({withLink}/{totalCitations})</li>
            <li>• {isZh ? "完全缺口（无品牌+无链接）" : "Full Gap (no brand + no link)"}: <strong>{citations.filter(r => String(r.has_brand_mention ?? "").toUpperCase() !== "TRUE" && String(r.has_official_link ?? "").toUpperCase() !== "TRUE").length}</strong> — {isZh ? "优先生产内容" : "Priority for content production"}</li>
            <li>• {isZh ? "部分缺口（有品牌无链接）" : "Partial Gap (brand, no link)"}: <strong>{citations.filter(r => String(r.has_brand_mention ?? "").toUpperCase() === "TRUE" && String(r.has_official_link ?? "").toUpperCase() !== "TRUE").length}</strong> — {isZh ? "优化现有内容" : "Optimize existing content"}</li>
          </ul>
        </GlassCard>
      )}
    </div>
  );
}
