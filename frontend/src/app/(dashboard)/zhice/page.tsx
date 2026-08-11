"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
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
  const searchParams = useSearchParams();
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
        // Method 1: Check URL search params (passed via Next.js router)
        const fromUrl = searchParams.get("phrases");
        if (fromUrl) {
          try {
            const parsed = JSON.parse(decodeURIComponent(fromUrl)) as string[];
            if (Array.isArray(parsed) && parsed.length > 0) {
              setZhikuPhrases(parsed);
              setLoadingPhrases(false);
              return;
            }
          } catch { /* ignore parse error, try next method */ }
        }

        // Method 2: Check localStorage (set by zhiku page)
        const cached = localStorage.getItem("zhiku_selected_phrases");
        if (cached) {
          try {
            const parsed = JSON.parse(cached) as string[];
            if (Array.isArray(parsed) && parsed.length > 0) {
              setZhikuPhrases(parsed);
              setLoadingPhrases(false);
              return;
            }
          } catch { /* ignore parse error */ }
        }

        // Method 3: Fallback to API
        const res = await apiGet<PhraseListResponse>("/api/zhiku/phrases", {
          batch_id: activeBatch,
          user: user ?? "",
        });
        const selected = res.phrases
          .filter((p) => p.is_selected === "TRUE" || p.is_selected === true || p.is_selected === "true")
          .map((p) => p.ai_query);
        setZhikuPhrases(selected);
      } catch {
        setZhikuPhrases([]);
      } finally {
        setLoadingPhrases(false);
      }
    }
    loadSelected();
  }, [activeBatch, user, searchParams]);

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
      // Use Next.js API route (runs on Vercel serverless, no Lambda needed)
      const res = await fetch("/api/zhice/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
      });
      const data = await res.json() as { status: string; results?: ZhiceResult[]; message?: string };
      setProgress(100);
      if (data.results && data.results.length > 0) {
        setResults(data.results);
      } else {
        setError(isZh ? `API \u672A\u8FD4\u56DE\u7ED3\u679C: ${data.message || "unknown"}` : `API returned no results: ${data.message || "unknown"}`);
      }
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

          {/* Results Table - Grouped by Platform */}
          <GlassCard padding="sm">
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">
              ③ {isZh ? "验证结果" : "Results"}
            </h2>
            {selectedPlatforms.map((platform) => {
              const platformResults = results.filter((r) => r.platform === platform);
              if (platformResults.length === 0) return null;
              const platformLink = platformResults.filter((r) => r.has_official_link).length;
              const platformBrand = platformResults.filter((r) => r.has_brand_mention).length;
              return (
                <div key={platform} className="mb-6">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-sm font-semibold text-[var(--accent)]">{platform}</span>
                    <span className="text-xs text-[var(--text-muted)]">
                      {isZh ? "\u5B98\u65B9\u94FE\u63A5" : "Link"}: {platformLink}/{platformResults.length} |
                      {isZh ? " \u54C1\u724C\u63D0\u53CA" : " Brand"}: {platformBrand}/{platformResults.length}
                    </span>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-[var(--border-glass)]">
                          <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">{isZh ? "\u68C0\u7D22\u77ED\u8BED" : "Query"}</th>
                          <th className="px-2 py-2 text-center text-xs text-[var(--text-secondary)]">{isZh ? "\u5B98\u65B9\u94FE\u63A5" : "Link"}</th>
                          <th className="px-2 py-2 text-center text-xs text-[var(--text-secondary)]">{isZh ? "\u54C1\u724C\u63D0\u53CA" : "Brand"}</th>
                          <th className="px-2 py-2 text-center text-xs text-[var(--text-secondary)]">{isZh ? "\u60C5\u611F" : "Sentiment"}</th>
                          <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">{isZh ? "\u7ADE\u54C1" : "Competitors"}</th>
                          <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">Gap</th>
                          <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">{isZh ? "\u9884\u89C8" : "Preview"}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {platformResults.map((r, idx) => {
                          const gapStatus = !r.has_official_link && !r.has_brand_mention ? "full_gap"
                            : !r.has_official_link ? "partial_gap" : "covered";
                          const sentimentLabel = r.sentiment === "positive" ? (isZh ? "\u79EF\u6781" : "Positive")
                            : r.sentiment === "negative" ? (isZh ? "\u6D88\u6781" : "Negative")
                            : (isZh ? "\u4E2D\u6027" : "Neutral");
                          const sentimentColor = r.sentiment === "positive" ? "text-green-400"
                            : r.sentiment === "negative" ? "text-red-400" : "text-gray-400";
                          return (
                            <tr key={idx} className="border-b border-[var(--border-glass)]/50 hover:bg-white/5">
                              <td className="px-2 py-2 max-w-[220px] truncate">{r.query}</td>
                              <td className="px-2 py-2 text-center">
                                <span className={r.has_official_link ? "text-[var(--success)]" : "text-[var(--error)]"}>
                                  {r.has_official_link ? "\u2705" : "\u274C"}
                                </span>
                              </td>
                              <td className="px-2 py-2 text-center">
                                <span className={r.has_brand_mention ? "text-[var(--success)]" : "text-[var(--error)]"}>
                                  {r.has_brand_mention ? "\u2705" : "\u274C"}
                                </span>
                              </td>
                              <td className={`px-2 py-2 text-center text-xs ${sentimentColor}`}>{sentimentLabel}</td>
                              <td className="px-2 py-2 text-xs text-yellow-400 max-w-[120px] truncate">{r.competitors || "\u2014"}</td>
                              <td className="px-2 py-2">
                                <span className={`text-xs px-1.5 py-0.5 rounded ${
                                  gapStatus === "full_gap" ? "bg-red-500/10 text-red-400"
                                    : gapStatus === "partial_gap" ? "bg-yellow-500/10 text-yellow-400"
                                    : "bg-green-500/10 text-green-400"
                                }`}>
                                  {gapStatus === "full_gap" ? (isZh ? "\u5B8C\u5168\u7F3A\u53E3" : "Full Gap")
                                    : gapStatus === "partial_gap" ? (isZh ? "\u90E8\u5206\u7F3A\u53E3" : "Partial")
                                    : (isZh ? "\u5DF2\u8986\u76D6" : "Covered")}
                                </span>
                              </td>
                              <td className="px-2 py-2 text-[var(--text-muted)] text-xs max-w-[160px] truncate">
                                {r.answer_preview || "\u2014"}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              );
            })}
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
