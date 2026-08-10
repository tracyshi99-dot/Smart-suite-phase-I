"use client";

import { useState, useEffect, useCallback } from "react";
import { useI18nStore } from "@/stores/i18n-store";
import { useBatchStore } from "@/stores/batch-store";
import { useAuthStore } from "@/stores/auth-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { BatchSelector } from "@/components/ui/BatchSelector";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { apiGet, apiPost } from "@/lib/api-client";
import { PhraseData, PhraseListResponse, SeedExpansionRequest } from "@/lib/types";
import { LONG_OP_TIMEOUT_MS } from "@/lib/constants";
import { truncateText } from "@/lib/utils";

export default function ZhikuPage() {
  const { t } = useI18nStore();
  const { activeBatch } = useBatchStore();
  const { user, regionConfig } = useAuthStore();

  // Seed expansion state
  const [seed, setSeed] = useState("");
  const [count, setCount] = useState(15);
  const [language, setLanguage] = useState("zh-CN");
  const [market, setMarket] = useState("CN");
  const [expanding, setExpanding] = useState(false);
  const [expandError, setExpandError] = useState<string | null>(null);

  // Phrase table state
  const [phrases, setPhrases] = useState<PhraseData[]>([]);
  const [loading, setLoading] = useState(false);
  const [sortKey, setSortKey] = useState<keyof PhraseData>("priority_score");
  const [sortAsc, setSortAsc] = useState(false);
  const [filterCategory, setFilterCategory] = useState("");
  const [filterIntent, setFilterIntent] = useState("");
  const [filterMinScore, setFilterMinScore] = useState(0);

  // Load phrases on mount / batch change
  useEffect(() => {
    let cancelled = false;
    async function fetchPhrases() {
      setLoading(true);
      try {
        const res = await apiGet<PhraseListResponse>("/api/zhiku/phrases", {
          batch_id: activeBatch,
          user: user ?? "",
        });
        if (!cancelled) setPhrases(res.phrases);
      } catch {
        // Keep existing phrases on error
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetchPhrases();
    return () => { cancelled = true; };
  }, [activeBatch, user]);

  // Reload helper for use after expand
  const loadPhrases = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiGet<PhraseListResponse>("/api/zhiku/phrases", {
        batch_id: activeBatch,
        user: user ?? "",
      });
      setPhrases(res.phrases);
    } catch {
      // Keep existing
    } finally {
      setLoading(false);
    }
  }, [activeBatch, user]);

  // Expand seed
  const handleExpand = async () => {
    if (!seed.trim()) return;
    setExpanding(true);
    setExpandError(null);
    try {
      const req: SeedExpansionRequest = {
        seed_word: seed.trim(),
        count,
        language,
        market,
        batch_id: activeBatch,
      };
      await apiPost("/api/zhiku/expand", req, { timeout: LONG_OP_TIMEOUT_MS });
      // Reload phrases after expansion
      await loadPhrases();
    } catch {
      setExpandError("裂变失败，请重试 / Expansion failed, please retry");
    } finally {
      setExpanding(false);
    }
  };

  // Toggle selection
  const handleToggleSelect = async (idx: number) => {
    const phrase = filteredPhrases[idx];
    const originalIdx = phrases.indexOf(phrase);
    const newSelected = phrase.is_selected !== "TRUE";

    // Optimistic update
    setPhrases((prev) => {
      const updated = [...prev];
      updated[originalIdx] = {
        ...updated[originalIdx],
        is_selected: newSelected ? "TRUE" : "FALSE",
      };
      return updated;
    });

    try {
      await apiPost("/api/zhiku/select", {
        batch_id: activeBatch,
        indices: [originalIdx],
        selected: newSelected,
      });
    } catch {
      // Revert on failure
      setPhrases((prev) => {
        const reverted = [...prev];
        reverted[originalIdx] = {
          ...reverted[originalIdx],
          is_selected: newSelected ? "FALSE" : "TRUE",
        };
        return reverted;
      });
    }
  };

  // Sort & filter
  const handleSort = (key: keyof PhraseData) => {
    if (sortKey === key) {
      setSortAsc(!sortAsc);
    } else {
      setSortKey(key);
      setSortAsc(true);
    }
  };

  const categories = [...new Set(phrases.map((p) => p.category).filter(Boolean))];
  const intentTypes = [...new Set(phrases.map((p) => p.intent_type).filter(Boolean))];

  const filteredPhrases = phrases
    .filter((p) => !filterCategory || p.category === filterCategory)
    .filter((p) => !filterIntent || p.intent_type === filterIntent)
    .filter((p) => p.priority_score >= filterMinScore)
    .sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (typeof aVal === "number" && typeof bVal === "number") {
        return sortAsc ? aVal - bVal : bVal - aVal;
      }
      return sortAsc
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal));
    });

  return (
    <div className="space-y-6 max-w-[1400px]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{t("zhiku.title")}</h1>
        <BatchSelector />
      </div>

      {/* Seed Expansion */}
      <GlassCard>
        <div className="flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs text-[var(--text-secondary)] mb-1">
              {t("zhiku.seed")}
            </label>
            <input
              type="text"
              value={seed}
              onChange={(e) => setSeed(e.target.value)}
              placeholder={regionConfig?.default_seeds?.[0] ?? "跨境电商怎么做"}
              className="w-full bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)]"
            />
          </div>
          <div className="w-20">
            <label className="block text-xs text-[var(--text-secondary)] mb-1">
              {t("zhiku.count")}
            </label>
            <input
              type="number"
              min={1}
              max={50}
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
              className="w-full bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
            />
          </div>
          <div className="w-28">
            <label className="block text-xs text-[var(--text-secondary)] mb-1">Language</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full bg-white/5 border border-[var(--border-glass)] rounded-lg px-2 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
            >
              {(regionConfig?.content_languages ?? [{ code: "zh-CN", name: "中文" }]).map((l) => (
                <option key={l.code} value={l.code} className="bg-[var(--bg-secondary)]">
                  {l.name}
                </option>
              ))}
            </select>
          </div>
          <Button onClick={handleExpand} loading={expanding} disabled={!seed.trim()}>
            {t("zhiku.expand")}
          </Button>
        </div>
        {expanding && <ProgressBar percent={50} label="裂变中..." className="mt-3" />}
        {expandError && (
          <p className="text-sm text-[var(--error)] mt-2">{expandError}</p>
        )}
      </GlassCard>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 items-center">
        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          className="bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-1.5 text-xs text-[var(--text-secondary)] focus:outline-none focus:border-[var(--accent)]"
        >
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c} value={c} className="bg-[var(--bg-secondary)]">{c}</option>
          ))}
        </select>
        <select
          value={filterIntent}
          onChange={(e) => setFilterIntent(e.target.value)}
          className="bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-1.5 text-xs text-[var(--text-secondary)] focus:outline-none focus:border-[var(--accent)]"
        >
          <option value="">All Intent Types</option>
          {intentTypes.map((i) => (
            <option key={i} value={i} className="bg-[var(--bg-secondary)]">{i}</option>
          ))}
        </select>
        <div className="flex items-center gap-1">
          <span className="text-xs text-[var(--text-muted)]">Min Score:</span>
          <input
            type="number"
            min={0}
            max={10}
            step={0.5}
            value={filterMinScore}
            onChange={(e) => setFilterMinScore(Number(e.target.value))}
            className="w-16 bg-white/5 border border-[var(--border-glass)] rounded px-2 py-1 text-xs text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
          />
        </div>
        <span className="text-xs text-[var(--text-muted)] ml-auto">
          {filteredPhrases.length} / {phrases.length} phrases
        </span>
      </div>

      {/* Phrase Table */}
      <GlassCard padding="sm">
        {loading ? (
          <div className="text-center py-8 text-[var(--text-secondary)]">
            {t("common.loading")}
          </div>
        ) : filteredPhrases.length === 0 ? (
          <div className="text-center py-8 text-[var(--text-secondary)]">
            {t("zhiku.empty")}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border-glass)]">
                  <th className="px-2 py-2 text-left w-8">✓</th>
                  {(["ai_query", "intent_type", "priority_score", "estimated_volume", "category"] as const).map(
                    (col) => (
                      <th
                        key={col}
                        className="px-2 py-2 text-left cursor-pointer hover:text-[var(--accent)] transition-colors text-xs text-[var(--text-secondary)]"
                        onClick={() => handleSort(col)}
                      >
                        {col}
                        {sortKey === col && (sortAsc ? " ↑" : " ↓")}
                      </th>
                    )
                  )}
                </tr>
              </thead>
              <tbody>
                {filteredPhrases.map((phrase, idx) => (
                  <tr
                    key={idx}
                    className="border-b border-[var(--border-glass)]/50 hover:bg-white/5 transition-colors"
                  >
                    <td className="px-2 py-2">
                      <input
                        type="checkbox"
                        checked={phrase.is_selected === "TRUE"}
                        onChange={() => handleToggleSelect(idx)}
                        className="accent-[var(--accent)]"
                        aria-label={`Select ${phrase.ai_query}`}
                      />
                    </td>
                    <td className="px-2 py-2 text-[var(--text-primary)] max-w-[300px]">
                      {truncateText(phrase.ai_query, 60)}
                    </td>
                    <td className="px-2 py-2 text-[var(--text-secondary)]">{phrase.intent_type}</td>
                    <td className="px-2 py-2 text-[var(--accent)] font-mono">{phrase.priority_score}</td>
                    <td className="px-2 py-2 text-[var(--text-secondary)] font-mono">{phrase.estimated_volume}</td>
                    <td className="px-2 py-2 text-[var(--text-muted)]">{phrase.category}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>
    </div>
  );
}
