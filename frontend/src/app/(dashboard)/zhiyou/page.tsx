"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useI18nStore } from "@/stores/i18n-store";
import { useBatchStore } from "@/stores/batch-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { BatchSelector } from "@/components/ui/BatchSelector";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { apiPost } from "@/lib/api-client";
import { ZhiyouRequest, ScoreResult, OptimizeResult } from "@/lib/types";
import { LONG_OP_TIMEOUT_MS } from "@/lib/constants";

export default function ZhiyouPage() {
  const router = useRouter();
  const { t } = useI18nStore();
  const { activeBatch } = useBatchStore();

  const [scoring, setScoring] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [scores, setScores] = useState<ScoreResult[]>([]);
  const [optimizeResults, setOptimizeResults] = useState<OptimizeResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleScore = async () => {
    setScoring(true);
    setError(null);
    try {
      const req: ZhiyouRequest = { batch_id: activeBatch, content_language: "zh-CN" };
      const res = await apiPost<{ scores?: ScoreResult[] }>("/api/zhiyou/score", req, { timeout: LONG_OP_TIMEOUT_MS });
      setScores(res.scores ?? []);
    } catch {
      setError("评分失败 / Scoring failed");
    } finally {
      setScoring(false);
    }
  };

  const handleOptimize = async () => {
    setOptimizing(true);
    setError(null);
    try {
      const req: ZhiyouRequest = { batch_id: activeBatch, content_language: "zh-CN" };
      const res = await apiPost<{ results?: OptimizeResult[] }>("/api/zhiyou/optimize", req, { timeout: LONG_OP_TIMEOUT_MS });
      setOptimizeResults(res.results ?? []);
    } catch {
      setError("优化失败 / Optimization failed");
    } finally {
      setOptimizing(false);
    }
  };

  const failedArticles = scores.filter((s) => s.compliance_status === "FAIL");

  return (
    <div className="space-y-6 max-w-[1400px]">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{t("zhiyou.title")}</h1>
        <BatchSelector />
      </div>

      {/* Actions */}
      <div className="flex gap-3">
        <Button onClick={handleScore} loading={scoring}>{t("zhiyou.score")}</Button>
        <Button onClick={handleOptimize} loading={optimizing} disabled={failedArticles.length === 0} variant="secondary">
          {t("zhiyou.optimize")}
        </Button>
      </div>
      {(scoring || optimizing) && <ProgressBar percent={50} label="Processing..." />}
      {error && <p className="text-sm text-[var(--error)]">{error}</p>}

      {/* Score Results */}
      {scores.length > 0 && (
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">Scorecard</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border-glass)]">
                  <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">Query</th>
                  <th className="px-2 py-2 text-xs text-[var(--text-secondary)]">Intent</th>
                  <th className="px-2 py-2 text-xs text-[var(--text-secondary)]">Readability</th>
                  <th className="px-2 py-2 text-xs text-[var(--text-secondary)]">Authority</th>
                  <th className="px-2 py-2 text-xs text-[var(--text-secondary)]">Action</th>
                  <th className="px-2 py-2 text-xs text-[var(--text-secondary)]">Diff</th>
                  <th className="px-2 py-2 text-xs text-[var(--text-secondary)]">Overall</th>
                  <th className="px-2 py-2 text-xs text-[var(--text-secondary)]">Status</th>
                </tr>
              </thead>
              <tbody>
                {scores.map((s, idx) => (
                  <tr key={idx} className={`border-b border-[var(--border-glass)]/50 ${s.compliance_status === "FAIL" ? "bg-[var(--error)]/5" : ""}`}>
                    <td className="px-2 py-2 max-w-[200px] truncate">{s.ai_query}</td>
                    <td className="px-2 py-2 text-center font-mono">{s.intent_match}</td>
                    <td className="px-2 py-2 text-center font-mono">{s.ai_readability}</td>
                    <td className="px-2 py-2 text-center font-mono">{s.authority}</td>
                    <td className="px-2 py-2 text-center font-mono">{s.actionability}</td>
                    <td className="px-2 py-2 text-center font-mono">{s.differentiation}</td>
                    <td className="px-2 py-2 text-center font-mono font-bold">{s.overall_score}</td>
                    <td className="px-2 py-2 text-center">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        s.compliance_status === "PASS" ? "bg-[var(--success)]/20 text-[var(--success)]" : "bg-[var(--error)]/20 text-[var(--error)]"
                      }`}>
                        {s.compliance_status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      )}

      {/* Optimize Results */}
      {optimizeResults.length > 0 && (
        <GlassCard padding="sm">
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">Optimization Results</h2>
          <div className="space-y-3">
            {optimizeResults.map((r, idx) => (
              <div key={idx} className="p-3 bg-white/5 rounded-lg">
                <p className="text-sm font-medium">{r.ai_query}</p>
                <div className="flex gap-4 mt-1 text-xs">
                  <span className="text-[var(--text-muted)]">Before: {r.original_score}</span>
                  <span className="text-[var(--accent)]">After: {r.optimized_score}</span>
                  <span className={r.compliance_status === "PASS" ? "text-[var(--success)]" : "text-[var(--error)]"}>
                    {r.compliance_status}
                  </span>
                </div>
                {r.changes.length > 0 && (
                  <ul className="mt-2 text-xs text-[var(--text-secondary)] list-disc list-inside">
                    {r.changes.map((c, i) => <li key={i}>{c}</li>)}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </GlassCard>
      )}

      {/* CTA */}
      <div className="flex justify-end pt-4">
        <button onClick={() => router.push("/zhibu")} className="px-4 py-2 rounded-lg text-sm font-medium bg-[var(--accent)] text-black hover:bg-[var(--accent-hover)] transition-colors">
          下一步：内容发布 →
        </button>
      </div>
    </div>
  );
}
