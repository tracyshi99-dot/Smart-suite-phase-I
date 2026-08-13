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

// --- History types ---
interface ZhiceHistoryEntry {
  id: string;
  date: string;
  topic: string;
  phrases: string[];
  platforms: string[];
  results: ZhiceResult[];
  archived?: boolean; // true = user deleted → moved to history
}

const ZHICE_SESSIONS_KEY = "zhice_sessions";
const ZHICE_HISTORY_KEY = "zhice_history";

function loadSessions(): ZhiceHistoryEntry[] {
  try {
    return JSON.parse(localStorage.getItem(ZHICE_SESSIONS_KEY) || "[]");
  } catch { return []; }
}
function saveSessions(data: ZhiceHistoryEntry[]) {
  localStorage.setItem(ZHICE_SESSIONS_KEY, JSON.stringify(data));
}
function loadHistory(): ZhiceHistoryEntry[] {
  try {
    return JSON.parse(localStorage.getItem(ZHICE_HISTORY_KEY) || "[]");
  } catch { return []; }
}
function saveHistory(data: ZhiceHistoryEntry[]) {
  localStorage.setItem(ZHICE_HISTORY_KEY, JSON.stringify(data));
}

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

  // Platform selection
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(
    regionConfig?.verification_platforms ?? ["deepseek", "chatgpt"]
  );

  // Execution state
  const [testing, setTesting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<ZhiceResult[]>([]);
  const [selectedIndices, setSelectedIndices] = useState<Set<number>>(new Set());
  const [error, setError] = useState<string | null>(null);

  // History & sessions
  const [sessions, setSessions] = useState<ZhiceHistoryEntry[]>([]);
  const [history, setHistory] = useState<ZhiceHistoryEntry[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  // Load persisted sessions + history on mount
  useEffect(() => {
    setSessions(loadSessions());
    setHistory(loadHistory());
  }, []);

  // Auto-restore last session results if no new test has been run
  useEffect(() => {
    if (results.length === 0 && sessions.length > 0) {
      const last = sessions[0];
      setResults(last.results);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessions]);

  // Auto-select gaps when results change
  useEffect(() => {
    if (results.length > 0) {
      const gapIndices = new Set<number>();
      results.forEach((r, i) => {
        if (!r.has_official_link) gapIndices.add(i);
      });
      setSelectedIndices(gapIndices);
    }
  }, [results]);

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

  // Unified phrase pool (from all sources)
  const [phrasePool, setPhrasePool] = useState<{ text: string; source: string; selected: boolean }[]>([]);

  // Semantic dedup: normalize phrase to core keywords for comparison
  function normalizePhrase(text: string): string {
    return text
      .toLowerCase()
      .replace(/[？?！!。，,、：:；;（）()【】\[\]""''\"\']/g, "")
      .replace(/\s+/g, "")
      // Remove common filler words that don't change intent
      .replace(/(怎么样|怎样|如何|怎么|什么|哪些|哪个|吗|呢|啊|吧|的|了|是|在|有|和|与|或|到|从|为|对|把|被|让|给)/g, "")
      .trim();
  }

  // Check if two phrases are semantically duplicate (same core + intent)
  function isDuplicate(newText: string, existingTexts: string[]): string | null {
    const normNew = normalizePhrase(newText);
    if (normNew.length < 2) return null;
    for (const existing of existingTexts) {
      const normExisting = normalizePhrase(existing);
      // Exact match after normalization
      if (normNew === normExisting) return existing;
      // One contains the other (core meaning identical)
      if (normNew.length > 3 && normExisting.length > 3) {
        if (normNew.includes(normExisting) || normExisting.includes(normNew)) {
          // Only flag if overlap is >70% of the shorter one
          const shorter = Math.min(normNew.length, normExisting.length);
          const longer = Math.max(normNew.length, normExisting.length);
          if (shorter / longer > 0.7) return existing;
        }
      }
    }
    return null;
  }

  // Sync zhiku phrases into pool
  useEffect(() => {
    if (zhikuPhrases.length > 0) {
      setPhrasePool((prev) => {
        const existingTexts = prev.map((p) => p.text);
        const newItems: { text: string; source: string; selected: boolean }[] = [];
        for (const p of zhikuPhrases) {
          const dup = isDuplicate(p, existingTexts);
          if (!dup) {
            newItems.push({ text: p, source: "智库", selected: true });
            existingTexts.push(p);
          }
        }
        return [...prev, ...newItems];
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [zhikuPhrases]);

  // Handle file upload (Excel/CSV/TXT)
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      let items: string[] = [];
      const ext = file.name.split(".").pop()?.toLowerCase();

      if (ext === "xlsx" || ext === "xls") {
        const XLSX = await import("xlsx");
        const buffer = await file.arrayBuffer();
        const wb = XLSX.read(buffer, { type: "array" });
        const ws = wb.Sheets[wb.SheetNames[0]];
        const rows = XLSX.utils.sheet_to_json(ws, { header: 1 }) as unknown[][];
        // Skip header if it looks like one
        const startIdx = rows.length > 0 && typeof rows[0]?.[0] === "string" &&
          ((rows[0][0] as string).includes("query") || (rows[0][0] as string).includes("短语") || (rows[0][0] as string).includes("检索")) ? 1 : 0;
        items = rows.slice(startIdx)
          .map((row) => String(row[0] ?? "").trim())
          .filter((s) => s.length > 3);
      } else {
        // CSV / TXT / MD
        const text = await file.text();
        items = text.split("\n")
          .map((l) => l.split(",")[0]?.trim().replace(/^["']|["']$/g, ""))
          .filter((s) => s.length > 3);
      }

      if (items.length > 0) {
        setPhrasePool((prev) => {
          const existingTexts = prev.map((p) => p.text);
          const newItems: { text: string; source: string; selected: boolean }[] = [];
          let dedupCount = 0;
          for (const p of items) {
            const dup = isDuplicate(p, existingTexts);
            if (!dup) {
              newItems.push({ text: p, source: `上传:${file.name}`, selected: true });
              existingTexts.push(p);
            } else {
              dedupCount++;
            }
          }
          if (dedupCount > 0) {
            setError(`${dedupCount} ${isZh ? "条重复短语已自动去重" : "duplicates removed"}`);
            setTimeout(() => setError(null), 3000);
          }
          return [...prev, ...newItems];
        });
      }
    } catch { /* ignore */ }
    e.target.value = "";
  };

  // Add manual phrases to pool
  const handleAddManualToPool = () => {
    const lines = manualPhrases.split("\n").map((l) => l.trim()).filter((l) => l.length > 3);
    if (lines.length === 0) return;
    setPhrasePool((prev) => {
      const existingTexts = prev.map((p) => p.text);
      const newItems: { text: string; source: string; selected: boolean }[] = [];
      let dedupCount = 0;
      for (const p of lines) {
        const dup = isDuplicate(p, existingTexts);
        if (!dup) {
          newItems.push({ text: p, source: "手动", selected: true });
          existingTexts.push(p);
        } else {
          dedupCount++;
        }
      }
      if (dedupCount > 0) {
        setError(`${dedupCount} ${isZh ? "条与已有短语意图重复，已跳过" : "duplicates skipped (same intent)"}`);
        setTimeout(() => setError(null), 3000);
      }
      return [...prev, ...newItems];
    });
    setManualPhrases("");
  };

  // Get selected phrases from pool for testing
  const getPhrasesToTest = (): string[] => {
    return phrasePool.filter((p) => p.selected).map((p) => p.text);
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
        // Auto-select all gaps (full_gap + partial_gap) by default
        const gapIndices = new Set<number>();
        data.results.forEach((r, i) => {
          if (!r.has_official_link) gapIndices.add(i);
        });
        setSelectedIndices(gapIndices);

        // Persist to sessions
        const entry: ZhiceHistoryEntry = {
          id: `zhice_${Date.now()}`,
          date: new Date().toLocaleString(),
          topic: phrases.slice(0, 3).join(", ").slice(0, 50),
          phrases,
          platforms: selectedPlatforms,
          results: data.results,
        };
        const updated = [entry, ...sessions].slice(0, 20); // keep last 20
        setSessions(updated);
        saveSessions(updated);
      } else {
        setError(isZh ? `API \u672A\u8FD4\u56DE\u7ED3\u679C: ${data.message || "unknown"}` : `API returned no results: ${data.message || "unknown"}`);
      }
    } catch {
      setError(isZh ? "验证失败，请重试" : "Verification failed, please retry");
    } finally {
      setTesting(false);
    }
  };

  // Delete a session → move to history
  const handleDeleteSession = (id: string) => {
    const target = sessions.find((s) => s.id === id);
    if (!target) return;
    const updatedSessions = sessions.filter((s) => s.id !== id);
    setSessions(updatedSessions);
    saveSessions(updatedSessions);
    const updatedHistory = [{ ...target, archived: true }, ...history].slice(0, 50);
    setHistory(updatedHistory);
    saveHistory(updatedHistory);
    // If we were viewing this session's results, clear them
    if (results === target.results || (results.length > 0 && results[0]?.query === target.results[0]?.query)) {
      setResults([]);
      setSelectedIndices(new Set());
    }
  };

  // Restore from history → put back in sessions and load results
  const handleRestoreFromHistory = (id: string) => {
    const target = history.find((h) => h.id === id);
    if (!target) return;
    const updatedHistory = history.filter((h) => h.id !== id);
    setHistory(updatedHistory);
    saveHistory(updatedHistory);
    const restored = { ...target, archived: false };
    const updatedSessions = [restored, ...sessions].slice(0, 20);
    setSessions(updatedSessions);
    saveSessions(updatedSessions);
    setResults(restored.results);
  };

  // Reuse phrases from a history entry (load into pool for re-testing)
  const handleReusePhrasesFromHistory = (entry: ZhiceHistoryEntry) => {
    setPhrasePool((prev) => {
      const existing = new Set(prev.map((p) => p.text));
      const newItems = entry.phrases
        .filter((p) => !existing.has(p))
        .map((p) => ({ text: p, source: "历史复用", selected: true }));
      return [...prev, ...newItems];
    });
    setSelectedPlatforms(entry.platforms);
    setShowHistory(false);
  };

  // Permanently delete from history
  const handlePermanentDelete = (id: string) => {
    const updatedHistory = history.filter((h) => h.id !== id);
    setHistory(updatedHistory);
    saveHistory(updatedHistory);
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

        {/* Input sources row */}
        <div className="flex flex-wrap gap-3 mb-4">
          {/* 智库 */}
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg border border-[var(--border-glass)] bg-white/5">
            <span className="text-xs text-[var(--text-secondary)]">{isZh ? "智库" : "Zhiku"}:</span>
            <span className="text-xs font-medium text-[var(--accent)]">{zhikuPhrases.length} {isZh ? "条" : ""}</span>
            {loadingPhrases && <span className="text-[10px] text-[var(--text-muted)]">...</span>}
          </div>

          {/* 手动输入 */}
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={manualPhrases}
              onChange={(e) => setManualPhrases(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); handleAddManualToPool(); } }}
              placeholder={isZh ? "输入短语，按 Enter 添加（多条用换行分隔）" : "Type phrase, press Enter to add"}
              className="w-64 bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-2 text-xs text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)]"
            />
            <button
              onClick={handleAddManualToPool}
              disabled={!manualPhrases.trim()}
              className="text-xs px-3 py-2 rounded-lg border border-[var(--border-glass)] text-[var(--accent)] hover:bg-[var(--accent)]/10 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              + {isZh ? "添加" : "Add"}
            </button>
          </div>

          {/* 文件上传 */}
          <label className="flex items-center gap-2 px-3 py-2 rounded-lg border border-[var(--border-glass)] bg-white/5 cursor-pointer hover:border-[var(--accent)]/30 transition-colors">
            <span className="text-xs text-[var(--text-secondary)]">📎 {isZh ? "上传文件" : "Upload"}</span>
            <span className="text-[10px] text-[var(--text-muted)]">(Excel/CSV/TXT)</span>
            <input
              type="file"
              accept=".csv,.txt,.xlsx,.xls,.md"
              onChange={handleFileUpload}
              className="hidden"
            />
          </label>
        </div>

        {/* Unified phrase table */}
        {phrasePool.length > 0 ? (
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-[var(--text-muted)]">
                {phrasePool.filter((p) => p.selected).length}/{phrasePool.length} {isZh ? "条已选中" : "selected"}
              </span>
              <div className="flex gap-2">
                <button onClick={() => setPhrasePool((prev) => prev.map((p) => ({ ...p, selected: true })))} className="text-[10px] text-[var(--text-secondary)] hover:text-[var(--accent)]">{isZh ? "全选" : "All"}</button>
                <button onClick={() => setPhrasePool((prev) => prev.map((p) => ({ ...p, selected: false })))} className="text-[10px] text-[var(--text-secondary)] hover:text-[var(--accent)]">{isZh ? "全不选" : "None"}</button>
                <button onClick={() => setPhrasePool([])} className="text-[10px] text-[var(--error)] hover:text-red-600">{isZh ? "清空" : "Clear"}</button>
              </div>
            </div>
            <div className="max-h-56 overflow-y-auto border border-[var(--border-glass)] rounded-lg">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-[var(--bg-surface)]">
                  <tr className="border-b border-[var(--border-glass)]">
                    <th className="w-8 px-2 py-1.5 text-center text-[10px] text-[var(--text-muted)]">✓</th>
                    <th className="px-2 py-1.5 text-left text-[10px] text-[var(--text-muted)]">#</th>
                    <th className="px-2 py-1.5 text-left text-[10px] text-[var(--text-muted)]">{isZh ? "检索短语" : "Phrase"}</th>
                    <th className="px-2 py-1.5 text-left text-[10px] text-[var(--text-muted)]">{isZh ? "来源" : "Source"}</th>
                    <th className="w-8 px-2 py-1.5"></th>
                  </tr>
                </thead>
                <tbody>
                  {phrasePool.map((p, idx) => (
                    <tr key={idx} className="border-b border-[var(--border-glass)]/30 hover:bg-white/5">
                      <td className="px-2 py-1 text-center">
                        <input
                          type="checkbox"
                          checked={p.selected}
                          onChange={() => {
                            setPhrasePool((prev) => {
                              const updated = [...prev];
                              updated[idx] = { ...updated[idx], selected: !updated[idx].selected };
                              return updated;
                            });
                          }}
                          className="accent-[var(--accent)]"
                        />
                      </td>
                      <td className="px-2 py-1 text-[10px] text-[var(--text-muted)]">{idx + 1}</td>
                      <td className="px-2 py-1 text-xs text-[var(--text-primary)]">{p.text}</td>
                      <td className="px-2 py-1">
                        <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                          p.source === "智库" ? "bg-blue-500/10 text-blue-400"
                            : p.source === "手动" ? "bg-purple-500/10 text-purple-400"
                            : "bg-green-500/10 text-green-400"
                        }`}>{p.source}</span>
                      </td>
                      <td className="px-2 py-1 text-center">
                        <button
                          onClick={() => setPhrasePool((prev) => prev.filter((_, i) => i !== idx))}
                          className="text-[10px] text-[var(--text-muted)] hover:text-[var(--error)]"
                        >✕</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <p className="text-xs text-[var(--text-muted)] py-4 text-center">
            {isZh ? "暂无短语。通过智库传入、手动输入或上传文件添加待测短语。" : "No phrases yet. Add via Knowledge Base, manual input, or file upload."}
          </p>
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
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-sm font-medium text-[var(--text-secondary)]">
                ③ {isZh ? "验证结果" : "Results"}
              </h2>
              <div className="flex items-center gap-3">
                <span className="text-xs text-[var(--text-muted)]">
                  {selectedIndices.size} {isZh ? "\u6761\u5DF2\u9009" : "selected"}
                </span>
                <button
                  onClick={() => {
                    const gapIndices = new Set<number>();
                    results.forEach((r, i) => { if (!r.has_official_link) gapIndices.add(i); });
                    setSelectedIndices(gapIndices);
                  }}
                  className="text-xs text-[var(--accent)] hover:underline"
                >
                  {isZh ? "\u9009\u4E2D\u6240\u6709\u7F3A\u53E3" : "Select all gaps"}
                </button>
                <button onClick={() => setSelectedIndices(new Set(results.map((_, i) => i)))} className="text-xs text-[var(--text-secondary)] hover:text-[var(--accent)]">
                  {isZh ? "\u5168\u9009" : "Select all"}
                </button>
                <button onClick={() => setSelectedIndices(new Set())} className="text-xs text-[var(--text-secondary)] hover:text-[var(--accent)]">
                  {isZh ? "\u53D6\u6D88" : "Clear"}
                </button>
              </div>
            </div>
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
                          <th className="px-2 py-2 text-center w-8">{"\u2713"}</th>
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
                        {platformResults.map((r) => {
                          const globalIdx = results.indexOf(r);
                          const gapStatus = !r.has_official_link && !r.has_brand_mention ? "full_gap"
                            : !r.has_official_link ? "partial_gap" : "covered";
                          const sentimentLabel = r.sentiment === "positive" ? (isZh ? "\u79EF\u6781" : "Positive")
                            : r.sentiment === "negative" ? (isZh ? "\u6D88\u6781" : "Negative")
                            : (isZh ? "\u4E2D\u6027" : "Neutral");
                          const sentimentColor = r.sentiment === "positive" ? "text-green-400"
                            : r.sentiment === "negative" ? "text-red-400" : "text-gray-400";
                          return (
                            <tr key={globalIdx} className="border-b border-[var(--border-glass)]/50 hover:bg-white/5">
                              <td className="px-2 py-2 text-center">
                                <input
                                  type="checkbox"
                                  checked={selectedIndices.has(globalIdx)}
                                  onChange={() => {
                                    setSelectedIndices((prev) => {
                                      const next = new Set(prev);
                                      if (next.has(globalIdx)) next.delete(globalIdx);
                                      else next.add(globalIdx);
                                      return next;
                                    });
                                  }}
                                  className="accent-[var(--accent)]"
                                />
                              </td>
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

      {/* Sessions & History Panel */}
      <GlassCard>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-medium text-[var(--text-secondary)]">
            {isZh ? "📋 测试记录" : "📋 Test Sessions"}
          </h2>
          <div className="flex gap-2">
            <button
              onClick={() => setShowHistory(false)}
              className={`text-xs px-2 py-1 rounded ${!showHistory ? "bg-[var(--accent)]/10 text-[var(--accent)]" : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"}`}
            >
              {isZh ? `当前 (${sessions.length})` : `Current (${sessions.length})`}
            </button>
            <button
              onClick={() => setShowHistory(true)}
              className={`text-xs px-2 py-1 rounded ${showHistory ? "bg-[var(--accent)]/10 text-[var(--accent)]" : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"}`}
            >
              {isZh ? `历史记录 (${history.length})` : `History (${history.length})`}
            </button>
          </div>
        </div>

        {!showHistory ? (
          /* Current Sessions */
          sessions.length === 0 ? (
            <p className="text-xs text-[var(--text-muted)]">{isZh ? "暂无测试记录，运行测试后自动保存" : "No sessions yet. Results are saved automatically."}</p>
          ) : (
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {sessions.map((s) => (
                <div key={s.id} className="flex items-center justify-between p-2 rounded-lg bg-white/5 border border-[var(--border-glass)] hover:border-[var(--accent)]/30 transition-colors">
                  <div
                    className="flex-1 cursor-pointer"
                    onClick={() => { setResults(s.results); setSelectedIndices(new Set()); }}
                  >
                    <p className="text-xs font-medium text-[var(--text-primary)]">{s.topic}</p>
                    <p className="text-[10px] text-[var(--text-muted)]">
                      {s.date} • {s.phrases.length} {isZh ? "短语" : "phrases"} × {s.platforms.join(", ")} • {s.results.length} {isZh ? "结果" : "results"}
                    </p>
                  </div>
                  <div className="flex gap-1 shrink-0 ml-2">
                    <button
                      onClick={() => { setResults(s.results); setSelectedIndices(new Set()); }}
                      className="text-[10px] px-2 py-1 rounded border border-[var(--border-glass)] text-[var(--accent)] hover:bg-[var(--accent)]/10"
                      title={isZh ? "查看结果" : "View results"}
                    >
                      {isZh ? "查看" : "View"}
                    </button>
                    <button
                      onClick={() => handleReusePhrasesFromHistory(s)}
                      className="text-[10px] px-2 py-1 rounded border border-[var(--border-glass)] text-[var(--text-secondary)] hover:text-[var(--accent)]"
                      title={isZh ? "复用短语重新测试" : "Reuse phrases for new test"}
                    >
                      {isZh ? "复用" : "Reuse"}
                    </button>
                    <button
                      onClick={() => handleDeleteSession(s.id)}
                      className="text-[10px] px-2 py-1 rounded border border-[var(--border-glass)] text-[var(--error)] hover:bg-red-500/10"
                      title={isZh ? "删除到历史" : "Delete to history"}
                    >
                      {isZh ? "删除" : "Del"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )
        ) : (
          /* History (archived / deleted sessions) */
          history.length === 0 ? (
            <p className="text-xs text-[var(--text-muted)]">{isZh ? "暂无历史记录" : "No history records"}</p>
          ) : (
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {history.map((h) => (
                <div key={h.id} className="flex items-center justify-between p-2 rounded-lg bg-white/5 border border-[var(--border-glass)] opacity-80 hover:opacity-100 transition-opacity">
                  <div className="flex-1">
                    <p className="text-xs font-medium text-[var(--text-primary)]">{h.topic}</p>
                    <p className="text-[10px] text-[var(--text-muted)]">
                      {h.date} • {h.phrases.length} {isZh ? "短语" : "phrases"} • {h.results.length} {isZh ? "结果" : "results"}
                    </p>
                  </div>
                  <div className="flex gap-1 shrink-0 ml-2">
                    <button
                      onClick={() => handleRestoreFromHistory(h.id)}
                      className="text-[10px] px-2 py-1 rounded border border-[var(--border-glass)] text-[var(--success)] hover:bg-green-500/10"
                      title={isZh ? "恢复到当前" : "Restore"}
                    >
                      {isZh ? "恢复" : "Restore"}
                    </button>
                    <button
                      onClick={() => handleReusePhrasesFromHistory(h)}
                      className="text-[10px] px-2 py-1 rounded border border-[var(--border-glass)] text-[var(--text-secondary)] hover:text-[var(--accent)]"
                      title={isZh ? "复用短语重新测试" : "Reuse phrases"}
                    >
                      {isZh ? "复用" : "Reuse"}
                    </button>
                    <button
                      onClick={() => handlePermanentDelete(h.id)}
                      className="text-[10px] px-2 py-1 rounded border border-[var(--border-glass)] text-[var(--error)] hover:bg-red-500/10"
                      title={isZh ? "永久删除" : "Permanently delete"}
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )
        )}
      </GlassCard>

      {/* CTA to next step */}
      <div className="flex items-center justify-end gap-3 pt-4">
        {selectedIndices.size > 0 && (() => {
          const selectedQueries = [...selectedIndices].map((i) => results[i]?.query).filter(Boolean);
          const uniquePhrases = [...new Set(selectedQueries)];
          return (
            <span className="text-xs text-[var(--success)]">
              {"\u2705"} {selectedIndices.size} {isZh ? "\u884C\u5DF2\u9009\uFF0C\u5BF9\u5E94" : "rows selected ="} {uniquePhrases.length} {isZh ? "\u7BC7\u5185\u5BB9" : "articles"}
            </span>
          );
        })()}
        <button
          onClick={() => {
            // Pass unique selected queries to zhizao via localStorage
            const selectedQueries = [...selectedIndices].map((i) => results[i]?.query).filter(Boolean);
            const unique = [...new Set(selectedQueries)];
            localStorage.setItem("zhice_selected_queries", JSON.stringify(unique));
            router.push("/zhizao");
          }}
          disabled={selectedIndices.size === 0}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            selectedIndices.size > 0
              ? "bg-[var(--accent)] text-black hover:bg-[var(--accent-hover)]"
              : "bg-gray-600 text-gray-400 cursor-not-allowed"
          }`}
        >
          {isZh
            ? `\u4E0B\u4E00\u6B65\uFF1A\u751F\u6210\u5185\u5BB9 (${new Set([...selectedIndices].map((i) => results[i]?.query).filter(Boolean)).size} \u7BC7) \u2192`
            : `Next: Generate Content (${new Set([...selectedIndices].map((i) => results[i]?.query).filter(Boolean)).size} articles) \u2192`
          }
        </button>
      </div>
    </div>
  );
}
