"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useI18nStore } from "@/stores/i18n-store";
import { useBatchStore } from "@/stores/batch-store";
import { useAuthStore } from "@/stores/auth-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { BatchSelector } from "@/components/ui/BatchSelector";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { apiGet, apiPost } from "@/lib/api-client";
import { PhraseListResponse, ZhiceRequest, ZhiceResult } from "@/lib/types";
import { ALL_PLATFORMS, LONG_OP_TIMEOUT_MS } from "@/lib/constants";

export default function ZhicePage() {
  const router = useRouter();
  const { t, locale } = useI18nStore();
  const { activeBatch } = useBatchStore();
  const { user, regionConfig } = useAuthStore();
  const isZh = locale.startsWith("zh");

  // Source phrases from zhiku
  const [zhikuPhrases, setZhikuPhrases] = useState<string[]>([]);
  const [loadingPhrases, setLoadingPhrases] = useState(true);

  // Manual input
  const [manualPhrases, setManualPhrases] = useState("");
  const [inputMode, setInputMode] = useState<"zhiku" | "manual">("zhiku");

  // Platform selection
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(
    regionConfig?.verification_platforms ?? ["deepseek", "chatgpt"]
  );

  // Execution state
  const [testing, setTesting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<ZhiceResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Load selected phrases from zhiku
  useEffect(() => {
    async function loadSelected() {
      setLoadingPhrases(true);
      try {
        const res = await apiGet<PhraseListResponse>("/api/zhiku/phrases", {
          batch_id: activeBatch,
          user: user ?? "",
        });
        const selected = res.phrases
          .filter((p) => p.is_selected === "TRUE")
          .map((p) => p.ai_query);
        setZhikuPhrases(selected);
      } catch {
        setZhikuPhrases([]);
      } finally {
        setLoadingPhrases(false);
      }
    }
    loadSelected();
  }, [activeBatch, user]);

  const togglePlatform = (p: string) => {
    setSelectedPlatforms((prev) =>
      prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]
    );
  };

  const getPhrasesToTest = (): string[] => {
    if (inputMode === "zhiku") return zhikuPhrases;
    return manualPhrases.split("\n").map((l) => l.trim()).filter((l) => l.length > 3);
  };

  const handleRunTest = async () => {
    const phrases = getPhrasesToTest();
    if (phrases.length === 0 || selectedPlatforms.length === 0) return;
    setTesting(true);
    setError(null);
    setProgress(10);
    setResults([]);

    try {
      const req: ZhiceRequest = {
        phrases,
        platforms: selectedPlatforms,
        user: user ?? "",
      };
      setProgress(30);
      const res = await apiPost<{ status: string; results?: ZhiceResult[]; message?: string }>(
        "/api/zhice/verify",
        req,
        { timeout: LONG_OP_TIMEOUT_MS }
      );
      setProgress(100);
      setResults(res.results ?? []);
    } catch {
      setError(isZh ? "验证失败，请重试" : "Verification failed, please retry");
    } finally {
      setTesting(false);
    }
  };

  // Analysis
  const totalTested = results.length;
  const withLink = results.filter((r) => r.has_official_link).length;
  const withBrand = results.filter((r) => r.has_brand_mention).length;
  const coverageRate = totalTested > 0 ? (withLink / totalTested) * 100 : 0;
  const brandRate = totalTested > 0 ? (withBrand / totalTested) * 100 : 0;
  const gaps = results.filter((r) => !r.has_official_link && !r.has_brand_mention);
  const partialGaps = results.filter((r) => !r.has_official_link && r.has_brand_mention);

  return (
    <div className="space-y-6 max-w-[1400px]">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{t("zhice.title")}</h1>
        <BatchSelector />
      </div>

      {/* Source Selection */}
      <GlassCard>
        <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
          ① {isZh ? "待验证短语" : "Phrases to Verify"}
        </h2>
        <div className="flex gap-2 mb-3">
          <button
            onClick={() => setInputMode("zhiku")}
            className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${
              inputMode === "zhiku"
                ? "bg-[var(--accent)]/10 text-[var(--accent)] border-[var(--accent)]/30"
                : "text-[var(--text-secondary)] border-[var(--border-glass)] hover:bg-white/5"
            }`}
          >
            {isZh ? `从智库 (${zhikuPhrases.length} 条已选)` : `From Knowledge Base (${zhikuPhrases.length} selected)`}
          </button>
          <button
            onClick={() => setInputMode("manual")}
            className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${
              inputMode === "manual"
                ? "bg-[var(--accent)]/10 text-[var(--accent)] border-[var(--accent)]/30"
                : "text-[var(--text-secondary)] border-[var(--border-glass)] hover:bg-white/5"
            }`}
          >
            {isZh ? "手动输入" : "Manual Input"}
          </button>
        </div>

        {inputMode === "zhiku" && (
          <div>
            {loadingPhrases ? (
              <p className="text-xs text-[var(--text-muted)]">{t("common.loading")}</p>
            ) : zhikuPhrases.length === 0 ? (
              <p className="text-xs text-[var(--text-muted)]">
                {isZh ? "暂无选中短语，请先到智库选择" : "No selected phrases. Go to Knowledge Base first."}
              </p>
            ) : (
              <div className="max-h-40 overflow-y-auto bg-white/5 rounded-lg p-2 border border-[var(--border-glass)]">
                {zhikuPhrases.slice(0, 30).map((p, i) => (
                  <p key={i} className="text-xs text-[var(--text-primary)] py-0.5">{p}</p>
                ))}
                {zhikuPhrases.length > 30 && (
                  <p className="text-xs text-[var(--text-muted)]">...+{zhikuPhrases.length - 30} more</p>
                )}
              </div>
            )}
          </div>
        )}

        {inputMode === "manual" && (
          <textarea
            value={manualPhrases}
            onChange={(e) => setManualPhrases(e.target.value)}
            placeholder={isZh ? "每行一条检索短语..." : "One phrase per line..."}
            rows={5}
            className="w-full bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)] resize-y"
          />
        )}
      </GlassCard>

      {/* Platform Selection */}
      <GlassCard>
        <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
          ② {isZh ? "选择验证平台" : "Select Platforms"}
        </h2>
        <div className="flex flex-wrap gap-2">
          {ALL_PLATFORMS.map((p) => (
            <button
              key={p}
              onClick={() => togglePlatform(p)}
              className={`px-3 py-1.5 rounded-lg text-xs transition-all ${
                selectedPlatforms.includes(p)
                  ? "bg-[var(--accent)]/20 text-[var(--accent)] border border-[var(--accent)]/40"
                  : "bg-white/5 text-[var(--text-muted)] border border-[var(--border-glass)] hover:border-[var(--accent)]/30"
              }`}
            >
              {p}
            </button>
          ))}
        </div>
        <div className="mt-4 flex items-center gap-3">
          <Button
            onClick={handleRunTest}
            loading={testing}
            disabled={getPhrasesToTest().length === 0 || selectedPlatforms.length === 0}
          >
            {t("zhice.run")} ({getPhrasesToTest().length} × {selectedPlatforms.length})
          </Button>
          <span className="text-xs text-[var(--text-muted)]">
            = {getPhrasesToTest().length * selectedPlatforms.length} {isZh ? "次验证" : "verifications"}
          </span>
        </div>
        {testing && <ProgressBar percent={progress} label={isZh ? "验证中..." : "Verifying..."} className="mt-3" />}
        {error && <p className="text-sm text-[var(--error)] mt-2">{error}</p>}
      </GlassCard>

      {/* Results */}
      {results.length > 0 && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <GlassCard padding="sm" className="text-center">
              <p className="text-xs text-[var(--text-muted)]">{isZh ? "总测试数" : "Total"}</p>
              <p className="text-xl font-bold">{totalTested}</p>
            </GlassCard>
            <GlassCard padding="sm" className="text-center">
              <p className="text-xs text-[var(--text-muted)]">{isZh ? "官方链接" : "Has Link"}</p>
              <p className="text-xl font-bold text-[var(--success)]">{coverageRate.toFixed(0)}%</p>
            </GlassCard>
            <GlassCard padding="sm" className="text-center">
              <p className="text-xs text-[var(--text-muted)]">{isZh ? "品牌提及" : "Brand"}</p>
              <p className="text-xl font-bold text-[var(--accent)]">{brandRate.toFixed(0)}%</p>
            </GlassCard>
            <GlassCard padding="sm" className="text-center">
              <p className="text-xs text-[var(--text-muted)]">{isZh ? "完全缺口" : "Full Gap"}</p>
              <p className="text-xl font-bold text-[var(--error)]">{gaps.length}</p>
            </GlassCard>
            <GlassCard padding="sm" className="text-center">
              <p className="text-xs text-[var(--text-muted)]">{isZh ? "部分缺口" : "Partial"}</p>
              <p className="text-xl font-bold text-yellow-400">{partialGaps.length}</p>
            </GlassCard>
          </div>

          {/* Results Table */}
          <GlassCard padding="sm">
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">
              ③ {isZh ? "验证结果" : "Results"}
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[var(--border-glass)]">
                    <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">{isZh ? "检索短语" : "Query"}</th>
                    <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">{isZh ? "平台" : "Platform"}</th>
                    <th className="px-2 py-2 text-center text-xs text-[var(--text-secondary)]">{isZh ? "官方链接" : "Link"}</th>
                    <th className="px-2 py-2 text-center text-xs text-[var(--text-secondary)]">{isZh ? "品牌提及" : "Brand"}</th>
                    <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">{isZh ? "Gap" : "Gap"}</th>
                    <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">{isZh ? "预览" : "Preview"}</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((r, idx) => {
                    const gapStatus = !r.has_official_link && !r.has_brand_mention ? "full_gap"
                      : !r.has_official_link ? "partial_gap" : "covered";
                    return (
                      <tr key={idx} className="border-b border-[var(--border-glass)]/50 hover:bg-white/5">
                        <td className="px-2 py-2 max-w-[250px] truncate">{r.query}</td>
                        <td className="px-2 py-2 text-[var(--text-secondary)]">{r.platform}</td>
                        <td className="px-2 py-2 text-center">
                          <span className={r.has_official_link ? "text-[var(--success)]" : "text-[var(--error)]"}>
                            {r.has_official_link ? "✅" : "❌"}
                          </span>
                        </td>
                        <td className="px-2 py-2 text-center">
                          <span className={r.has_brand_mention ? "text-[var(--success)]" : "text-[var(--error)]"}>
                            {r.has_brand_mention ? "✅" : "❌"}
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
                        <td className="px-2 py-2 text-[var(--text-muted)] text-xs max-w-[180px] truncate">
                          {r.answer_preview || "—"}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </GlassCard>
        </>
      )}

      {/* CTA to next step */}
      <div className="flex justify-end pt-4">
        <button onClick={() => router.push("/zhizao")} className="px-4 py-2 rounded-lg text-sm font-medium bg-[var(--accent)] text-black hover:bg-[var(--accent-hover)] transition-colors">
          {isZh ? "下一步：生成内容 →" : "Next: Generate Content →"}
        </button>
      </div>
    </div>
  );
}
