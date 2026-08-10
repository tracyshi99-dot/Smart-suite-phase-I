"use client";

import { useState } from "react";
import { useI18nStore } from "@/stores/i18n-store";
import { useBatchStore } from "@/stores/batch-store";
import { useAuthStore } from "@/stores/auth-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { BatchSelector } from "@/components/ui/BatchSelector";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { apiPost } from "@/lib/api-client";
import { ZhiceRequest, ZhiceResult } from "@/lib/types";
import { ALL_PLATFORMS, LONG_OP_TIMEOUT_MS } from "@/lib/constants";

export default function ZhicePage() {
  const { t } = useI18nStore();
  const { activeBatch } = useBatchStore();
  const { user, regionConfig } = useAuthStore();

  const [topic, setTopic] = useState("");
  const [phraseCount, setPhraseCount] = useState(10);
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(
    regionConfig?.verification_platforms ?? ["deepseek", "chatgpt"]
  );
  const [testing, setTesting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<ZhiceResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState(1); // 1-5 workflow steps

  const togglePlatform = (p: string) => {
    setSelectedPlatforms((prev) =>
      prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]
    );
  };

  const handleRunTest = async () => {
    if (!topic.trim() || selectedPlatforms.length === 0) return;
    setTesting(true);
    setError(null);
    setProgress(30);

    try {
      const req: ZhiceRequest = {
        phrases: [topic.trim()], // In full version, generate multiple phrases
        platforms: selectedPlatforms,
        user: user ?? "",
      };
      const res = await apiPost<{ status: string; results?: ZhiceResult[] }>(
        "/api/zhice/verify",
        req,
        { timeout: LONG_OP_TIMEOUT_MS }
      );
      setProgress(100);
      setResults(res.results ?? []);
      setStep(2);
    } catch {
      setError("测试失败，请重试 / Test failed, please retry");
    } finally {
      setTesting(false);
    }
  };

  const coverageRate = results.length > 0
    ? (results.filter((r) => r.has_official_link).length / results.length) * 100
    : 0;
  const gaps = results.filter((r) => !r.has_official_link);

  return (
    <div className="space-y-6 max-w-[1400px]">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{t("zhice.title")}</h1>
        <BatchSelector />
      </div>

      {/* Workflow Stepper */}
      <div className="flex items-center gap-2">
        {["Execute", "Analysis", "Opportunities", "Status", "Dashboard"].map((label, i) => (
          <div key={i} className="flex items-center">
            <span
              className={`px-3 py-1 rounded-lg text-xs ${
                step === i + 1
                  ? "bg-[var(--accent)]/15 text-[var(--accent)] border border-[var(--accent)]/40"
                  : "bg-white/5 text-[var(--text-muted)]"
              }`}
            >
              {label}
            </span>
            {i < 4 && <span className="mx-1 text-[var(--border-glass)]">→</span>}
          </div>
        ))}
      </div>

      {/* Test Configuration */}
      {step === 1 && (
        <GlassCard>
          <div className="space-y-4">
            <div>
              <label className="block text-xs text-[var(--text-secondary)] mb-1">{t("zhice.topic")}</label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. 跨境电商注册流程"
                className="w-full bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)]"
              />
            </div>
            <div>
              <label className="block text-xs text-[var(--text-secondary)] mb-1">{t("zhice.platforms")}</label>
              <div className="flex flex-wrap gap-2">
                {ALL_PLATFORMS.map((p) => (
                  <button
                    key={p}
                    onClick={() => togglePlatform(p)}
                    className={`px-3 py-1 rounded-lg text-xs transition-all ${
                      selectedPlatforms.includes(p)
                        ? "bg-[var(--accent)]/20 text-[var(--accent)] border border-[var(--accent)]/40"
                        : "bg-white/5 text-[var(--text-muted)] border border-[var(--border-glass)] hover:border-[var(--accent)]/30"
                    }`}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div>
                <label className="block text-xs text-[var(--text-secondary)] mb-1">Phrases (3-30)</label>
                <input
                  type="number"
                  min={3}
                  max={30}
                  value={phraseCount}
                  onChange={(e) => setPhraseCount(Number(e.target.value))}
                  className="w-20 bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
                />
              </div>
              <Button onClick={handleRunTest} loading={testing} disabled={!topic.trim()}>
                {t("zhice.run")}
              </Button>
            </div>
            {testing && <ProgressBar percent={progress} label="Testing..." />}
            {error && <p className="text-sm text-[var(--error)]">{error}</p>}
          </div>
        </GlassCard>
      )}

      {/* Results */}
      {step >= 2 && results.length > 0 && (
        <>
          {/* Gap Analysis Summary */}
          <div className="grid grid-cols-3 gap-4">
            <GlassCard padding="sm" className="text-center">
              <p className="text-xs text-[var(--text-secondary)]">Total Tested</p>
              <p className="text-2xl font-bold">{results.length}</p>
            </GlassCard>
            <GlassCard padding="sm" className="text-center">
              <p className="text-xs text-[var(--text-secondary)]">Coverage Rate</p>
              <p className="text-2xl font-bold text-[var(--success)]">{coverageRate.toFixed(0)}%</p>
            </GlassCard>
            <GlassCard padding="sm" className="text-center">
              <p className="text-xs text-[var(--text-secondary)]">Gaps</p>
              <p className="text-2xl font-bold text-[var(--error)]">{gaps.length}</p>
            </GlassCard>
          </div>

          {/* Results Table */}
          <GlassCard padding="sm">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[var(--border-glass)]">
                    <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">Query</th>
                    <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">Platform</th>
                    <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">Official Link</th>
                    <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">Brand Mention</th>
                    <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">Preview</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((r, idx) => (
                    <tr key={idx} className="border-b border-[var(--border-glass)]/50 hover:bg-white/5">
                      <td className="px-2 py-2">{r.query}</td>
                      <td className="px-2 py-2 text-[var(--text-secondary)]">{r.platform}</td>
                      <td className="px-2 py-2">
                        <span className={r.has_official_link ? "text-[var(--success)]" : "text-[var(--error)]"}>
                          {r.has_official_link ? "✓" : "✗"}
                        </span>
                      </td>
                      <td className="px-2 py-2">
                        <span className={r.has_brand_mention ? "text-[var(--success)]" : "text-[var(--text-muted)]"}>
                          {r.has_brand_mention ? "✓" : "—"}
                        </span>
                      </td>
                      <td className="px-2 py-2 text-[var(--text-muted)] text-xs max-w-[200px] truncate">
                        {r.answer_preview}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </GlassCard>
        </>
      )}
    </div>
  );
}
