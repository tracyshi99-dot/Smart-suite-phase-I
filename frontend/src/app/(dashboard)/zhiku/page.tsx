"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useI18nStore } from "@/stores/i18n-store";
import { useBatchStore } from "@/stores/batch-store";
import { useAuthStore } from "@/stores/auth-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { BatchSelector } from "@/components/ui/BatchSelector";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { apiGet, apiPost } from "@/lib/api-client";
import {
  PhraseData,
  PhraseListResponse,
  SeedExpansionRequest,
  PersonaExpansionRequest,
  UploadPhrasesRequest,
} from "@/lib/types";
import { LONG_OP_TIMEOUT_MS, CATEGORIES_35 } from "@/lib/constants";
import {
  PERSONA_IDENTITIES_ZH,
  PERSONA_IDENTITIES_EN,
  PERSONA_COMPANY_TYPES_ZH,
  PERSONA_COMPANY_TYPES_EN,
  PERSONA_ROLES_ZH,
  PERSONA_ROLES_EN,
  PERSONA_REVENUE_ZH,
  PERSONA_REVENUE_EN,
  PERSONA_BIZ_TYPES_ZH,
  PERSONA_BIZ_TYPES_EN,
  PERSONA_FULFILLMENT_ZH,
  PERSONA_FULFILLMENT_EN,
  PERSONA_MARKETPLACES_ZH,
  PERSONA_MARKETPLACES_EN,
  PERSONA_CONTENT_CATEGORIES_ZH,
  PERSONA_CONTENT_CATEGORIES_EN,
} from "@/lib/constants";
import { truncateText } from "@/lib/utils";

type TabId = "seed" | "persona" | "upload";

// Client-side scoring - Query Intelligence Framework (8-dimension lite)
function scorePhrase(q: string): number {
  let s = 3.0;
  // Length: 15-30 chars is sweet spot
  if (q.length >= 15 && q.length <= 30) s += 0.5;
  else if (q.length > 30) s += 0.3;
  // Intent clarity: question words
  if (/[\u600E\u5982\u591A\u54EA\u4E3A\u4EC0\u80FD]|how|what|why|which|can/i.test(q)) s += 0.5;
  // Business relevance: brand/product keywords
  if (/\u4E9A\u9A6C\u900A|amazon|fba|\u6CE8\u518C|\u5F00\u5E97|\u9009\u54C1|\u7269\u6D41|\u5E7F\u544A|listing/i.test(q)) s += 0.5;
  // Naturalness: question particles
  if (/[\u5417\u5462\u554A\u5427\uFF1F?]/.test(q)) s += 0.3;
  // Context specificity: scenario words (新手/2026/中国卖家/美国站/欧洲站)
  if (/\u65B0\u624B|\u5C0F\u767D|2026|2025|\u4E2D\u56FD\u5356\u5BB6|\u7F8E\u56FD\u7AD9|\u6B27\u6D32\u7AD9|\u65E5\u672C\u7AD9|beginner|chinese seller/i.test(q)) s += 0.3;
  // Decision/comparison value: vs/对比/推荐/应该
  if (/vs|\u8FD8\u662F|\u533A\u522B|\u5BF9\u6BD4|\u54EA\u4E2A\u597D|\u5E94\u8BE5|\u503C\u5F97|\u9002\u5408|\u63A8\u8350|\u6700\u597D|compare|recommend|should/i.test(q)) s += 0.3;
  return Math.min(5.0, Math.round(s * 10) / 10);
}

// Helper: check if is_selected is truthy (handles "TRUE", true, "true", 1)
function isSelected(val: unknown): boolean {
  if (val === true || val === "TRUE" || val === "true" || val === "1" || val === 1) return true;
  return false;
}

export default function ZhikuPage() {
  const { t, locale } = useI18nStore();
  const { activeBatch } = useBatchStore();
  const { user, regionConfig } = useAuthStore();
  const router = useRouter();
  const isZh = locale.startsWith("zh");

  // Tab state
  const [activeTab, setActiveTab] = useState<TabId>("seed");

  // Seed expansion state
  const [seed, setSeed] = useState("");
  const [count, setCount] = useState(15);
  const [language, setLanguage] = useState<string>(locale || "zh-CN");
  const [expanding, setExpanding] = useState(false);
  const [expandError, setExpandError] = useState<string | null>(null);

  // Persona expansion state
  const [identity, setIdentity] = useState("");
  const [companyType, setCompanyType] = useState("");
  const [role, setRole] = useState("");
  const [revenue, setRevenue] = useState("");
  const [bizType, setBizType] = useState("");
  const [fulfillment, setFulfillment] = useState("");
  const [marketplaces, setMarketplaces] = useState<string[]>([]);
  const [contentFocus, setContentFocus] = useState<string[]>([]);
  const [personaCount, setPersonaCount] = useState(5);
  const [personaExpanding, setPersonaExpanding] = useState(false);
  const [personaError, setPersonaError] = useState<string | null>(null);

  // Upload state
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadType, setUploadType] = useState<"phrases" | "keywords">("phrases");
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);

  // Phrase table state
  const [phrases, setPhrases] = useState<PhraseData[]>([]);
  const [loading, setLoading] = useState(false);
  const [sortKey, setSortKey] = useState<keyof PhraseData>("priority_score");
  const [sortAsc, setSortAsc] = useState(false);
  const [filterCategory, setFilterCategory] = useState("");
  const [filterIntent, setFilterIntent] = useState("");
  const [filterMinScore, setFilterMinScore] = useState(0);
  const [searchText, setSearchText] = useState("");

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
      // Split into batches of 5 to fit within API Gateway 30s timeout
      const batchSize = 5;
      const batches = Math.ceil(count / batchSize);
      const allPhrases: string[] = [];

      for (let i = 0; i < batches; i++) {
        const thisCount = Math.min(batchSize, count - allPhrases.length);
        const req: SeedExpansionRequest = {
          seed_word: seed.trim(),
          count: thisCount,
          language,
          market: regionConfig?.region_code ?? "CN",
          batch_id: activeBatch,
        };
        const res = await apiPost<{ success?: boolean; count?: number; phrases?: string[] }>(
          "/api/zhiku/expand", req, { timeout: LONG_OP_TIMEOUT_MS }
        );
        if (res.phrases && res.phrases.length > 0) {
          allPhrases.push(...res.phrases);
        }
      }

      if (allPhrases.length > 0) {
        const newPhrases: PhraseData[] = allPhrases.map((q) => ({
          ai_query: q,
          source: `seed_${seed.trim()}`,
          is_selected: "FALSE",
          priority_score: scorePhrase(q),
          intent_type: "",
          estimated_volume: 0,
          category: "",
          created_at: new Date().toISOString(),
        }));
        setPhrases((prev) => {
          const existing = new Set(prev.map((p) => p.ai_query));
          const unique = newPhrases.filter((p) => !existing.has(p.ai_query));
          return [...prev, ...unique];
        });
      } else {
        await loadPhrases();
      }
    } catch {
      setExpandError(isZh ? "\u88C2\u53D8\u5931\u8D25\uFF0C\u8BF7\u91CD\u8BD5" : "Expansion failed, please retry");
    } finally {
      setExpanding(false);
    }
  };

  // Persona expansion - split batches like seed expand
  const handlePersonaExpand = async () => {
    if (!identity) return;
    setPersonaExpanding(true);
    setPersonaError(null);
    try {
      const batchSize = 5;
      const batches = Math.ceil(personaCount / batchSize);
      const allPhrases: string[] = [];

      for (let i = 0; i < batches; i++) {
        const thisCount = Math.min(batchSize, personaCount - allPhrases.length);
        const req: PersonaExpansionRequest = {
          identity,
          company_type: companyType,
          marketplace: marketplaces,
          content_focus: contentFocus,
          count: thisCount,
          language,
          batch_id: activeBatch,
        };
        const res = await apiPost<{ success?: boolean; phrases?: string[] }>(
          "/api/zhiku/expand-persona", req, { timeout: LONG_OP_TIMEOUT_MS }
        );
        if (res.phrases && res.phrases.length > 0) {
          allPhrases.push(...res.phrases);
        }
      }

      if (allPhrases.length > 0) {
        const newPhrases: PhraseData[] = allPhrases.map((q) => ({
          ai_query: q,
          source: `persona_${identity}`,
          is_selected: "FALSE",
          priority_score: scorePhrase(q),
          intent_type: "",
          estimated_volume: 0,
          category: contentFocus[0] ?? "",
          created_at: new Date().toISOString(),
        }));
        setPhrases((prev) => {
          const existing = new Set(prev.map((p) => p.ai_query));
          const unique = newPhrases.filter((p) => !existing.has(p.ai_query));
          return [...prev, ...unique];
        });
      } else {
        await loadPhrases();
      }
    } catch {
      setPersonaError(isZh ? "\u753B\u50CF\u63A8\u6F14\u5931\u8D25\uFF0C\u8BF7\u91CD\u8BD5" : "Persona expansion failed, retry");
    } finally {
      setPersonaExpanding(false);
    }
  };

  // Upload handler
  const handleUpload = async () => {
    if (!uploadFile) return;
    setUploading(true);
    setUploadError(null);
    setUploadSuccess(null);
    try {
      const text = await uploadFile.text();
      const lines = text.split("\n").map((l) => l.trim()).filter((l) => l.length > 0);
      // Try to detect header row
      const hasHeader = lines[0]?.toLowerCase().includes("query") ||
        lines[0]?.toLowerCase().includes("keyword") ||
        lines[0]?.includes("\u68C0\u7D22") || lines[0]?.includes("\u5173\u952E");
      const dataLines = hasHeader ? lines.slice(1) : lines;
      // Extract first column (CSV)
      const phrases = dataLines
        .map((l) => l.split(",")[0]?.trim().replace(/^["']|["']$/g, ""))
        .filter((p) => p.length > 3);

      if (phrases.length === 0) {
        setUploadError(isZh ? "\u672A\u68C0\u6D4B\u5230\u6709\u6548\u77ED\u8BED" : "No valid phrases detected");
        return;
      }

      const req: UploadPhrasesRequest = {
        phrases,
        source: uploadType === "keywords" ? "seo_sem_upload" : "manual_upload",
        batch_id: activeBatch,
      };
      await apiPost("/api/zhiku/upload", req, { timeout: LONG_OP_TIMEOUT_MS });
      await loadPhrases();
      setUploadSuccess(
        isZh ? `\u2705 \u5BFC\u5165 ${phrases.length} \u6761` : `\u2705 Imported ${phrases.length} phrases`
      );
      setUploadFile(null);
    } catch {
      setUploadError(isZh ? "\u4E0A\u4F20\u5931\u8D25\uFF0C\u8BF7\u91CD\u8BD5" : "Upload failed, please retry");
    } finally {
      setUploading(false);
    }
  };

  // Toggle selection
  const handleToggleSelect = async (idx: number) => {
    const phrase = filteredPhrases[idx];
    const originalIdx = phrases.indexOf(phrase);
    const newSelected = !isSelected(phrase.is_selected);
    setPhrases((prev) => {
      const updated = [...prev];
      updated[originalIdx] = { ...updated[originalIdx], is_selected: newSelected ? "TRUE" : "FALSE" };
      return updated;
    });
    try {
      await apiPost("/api/zhiku/select", { batch_id: activeBatch, indices: [originalIdx], selected: newSelected });
    } catch {
      setPhrases((prev) => {
        const reverted = [...prev];
        reverted[originalIdx] = { ...reverted[originalIdx], is_selected: newSelected ? "FALSE" : "TRUE" };
        return reverted;
      });
    }
  };

  // Bulk select/deselect
  const handleBulkSelect = async (selectAll: boolean) => {
    const newValue = selectAll ? "TRUE" : "FALSE";
    const prevPhrases = [...phrases];
    setPhrases((prev) => prev.map((p) => ({ ...p, is_selected: newValue })));
    try {
      await apiPost("/api/zhiku/select", {
        batch_id: activeBatch,
        indices: phrases.map((_, i) => i),
        selected: selectAll,
      });
    } catch {
      setPhrases(prevPhrases);
    }
  };

  // Archive selected items
  const handleArchiveSelected = async () => {
    const selectedIndices = phrases
      .map((p, i) => (isSelected(p.is_selected) ? i : -1))
      .filter((i) => i >= 0);
    if (selectedIndices.length === 0) return;
    try {
      await apiPost("/api/archive", {
        batch_id: activeBatch,
        step: "01_zhiku",
        filename: "zhiku_ai_queries.csv",
        indices: selectedIndices,
      });
      setPhrases((prev) => prev.filter((p) => !isSelected(p.is_selected)));
    } catch {
      // ignore
    }
  };

  // Archive all items
  const handleArchiveAll = async () => {
    if (phrases.length === 0) return;
    if (!confirm(isZh ? "\u786E\u5B9A\u6E05\u9664\u6240\u6709\u77ED\u8BED\uFF1F\uFF08\u5C06\u4FDD\u5B58\u5230\u5386\u53F2\u8BB0\u5F55\uFF09" : "Clear all phrases? (will be saved to history)")) return;
    try {
      await apiPost("/api/archive", {
        batch_id: activeBatch,
        step: "01_zhiku",
        filename: "zhiku_ai_queries.csv",
        indices: [],
      });
      setPhrases([]);
    } catch {
      // ignore
    }
  };

  // Sort & filter
  const handleSort = (key: keyof PhraseData) => {
    if (sortKey === key) setSortAsc(!sortAsc);
    else { setSortKey(key); setSortAsc(true); }
  };

  const categories = CATEGORIES_35;
  const intentTypes = [...new Set(phrases.map((p) => p.intent_type).filter(Boolean))];
  const selectedCount = phrases.filter((p) => isSelected(p.is_selected)).length;

  const filteredPhrases = phrases
    .filter((p) => !filterCategory || p.category === filterCategory)
    .filter((p) => !filterIntent || p.intent_type === filterIntent)
    .filter((p) => p.priority_score >= filterMinScore)
    .filter((p) => !searchText || p.ai_query.toLowerCase().includes(searchText.toLowerCase()))
    .sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (typeof aVal === "number" && typeof bVal === "number")
        return sortAsc ? aVal - bVal : bVal - aVal;
      return sortAsc ? String(aVal).localeCompare(String(bVal)) : String(bVal).localeCompare(String(aVal));
    });

  // Persona option lists
  const identities = isZh ? PERSONA_IDENTITIES_ZH : PERSONA_IDENTITIES_EN;
  const companyTypes = isZh ? PERSONA_COMPANY_TYPES_ZH : PERSONA_COMPANY_TYPES_EN;
  const roles = isZh ? PERSONA_ROLES_ZH : PERSONA_ROLES_EN;
  const revenues = isZh ? PERSONA_REVENUE_ZH : PERSONA_REVENUE_EN;
  const bizTypes = isZh ? PERSONA_BIZ_TYPES_ZH : PERSONA_BIZ_TYPES_EN;
  const fulfillments = isZh ? PERSONA_FULFILLMENT_ZH : PERSONA_FULFILLMENT_EN;
  const marketplaceOptions = isZh ? PERSONA_MARKETPLACES_ZH : PERSONA_MARKETPLACES_EN;
  const contentOptions = isZh ? PERSONA_CONTENT_CATEGORIES_ZH : PERSONA_CONTENT_CATEGORIES_EN;

  const tabs: { id: TabId; label: string }[] = [
    { id: "seed", label: t("zhiku.tab_seed") },
    { id: "persona", label: t("zhiku.tab_persona") },
    { id: "upload", label: t("zhiku.tab_upload") },
  ];

  return (
    <div className="space-y-6 max-w-[1400px]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{t("zhiku.title")}</h1>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-[var(--border-glass)]">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
              activeTab === tab.id
                ? "bg-[var(--accent)]/10 text-[var(--accent)] border border-[var(--accent)]/30 border-b-transparent"
                : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/5"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab: Seed Expansion */}
      {activeTab === "seed" && (
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
                onKeyDown={(e) => e.key === "Enter" && handleExpand()}
                placeholder={regionConfig?.default_seeds?.[0] ?? "\u8DE8\u5883\u7535\u5546\u600E\u4E48\u505A"}
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
                {locale === "en" ? (
                  <option value="en" className="bg-[var(--bg-secondary)]">English</option>
                ) : (
                  <>
                    <option value={locale} className="bg-[var(--bg-secondary)]">
                      {locale === "zh-CN" ? "\u4E2D\u6587" : locale === "zh-TW" ? "\u7E41\u9AD4\u4E2D\u6587" : locale === "ko" ? "\uD55C\uAD6D\uC5B4" : locale === "vi" ? "Ti\u1EBFng Vi\u1EC7t" : locale}
                    </option>
                    <option value={`${locale}+en`} className="bg-[var(--bg-secondary)]">
                      {locale === "zh-CN" ? "\u4E2D\u6587+English" : locale === "zh-TW" ? "\u7E41\u9AD4\u4E2D\u6587+English" : locale === "ko" ? "\uD55C\uAD6D\uC5B4+English" : locale === "vi" ? "Ti\u1EBFng Vi\u1EC7t+English" : `${locale}+English`}
                    </option>
                  </>
                )}
              </select>
            </div>
            <Button onClick={handleExpand} loading={expanding} disabled={!seed.trim()}>
              {t("zhiku.expand")}
            </Button>
          </div>
          {expanding && <ProgressBar percent={50} label={isZh ? "\u88C2\u53D8\u4E2D..." : "Expanding..."} className="mt-3" />}
          {expandError && <p className="text-sm text-[var(--error)] mt-2">{expandError}</p>}
        </GlassCard>
      )}

      {/* Tab: Persona Expansion */}
      {activeTab === "persona" && (
        <GlassCard>
          <p className="text-xs text-[var(--text-secondary)] mb-4">{t("zhiku.persona_desc")}</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs text-[var(--text-secondary)] mb-1">{t("zhiku.identity")}</label>
              <select
                value={identity}
                onChange={(e) => setIdentity(e.target.value)}
                className="w-full bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
              >
                <option value="" className="bg-[var(--bg-surface)]">--</option>
                {identities.map((i) => (
                  <option key={i} value={i} className="bg-[var(--bg-surface)]">{i}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-[var(--text-secondary)] mb-1">{t("zhiku.company_type")}</label>
              <select
                value={companyType}
                onChange={(e) => setCompanyType(e.target.value)}
                className="w-full bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
              >
                <option value="" className="bg-[var(--bg-surface)]">--</option>
                {companyTypes.map((c) => (
                  <option key={c} value={c} className="bg-[var(--bg-surface)]">{c}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-[var(--text-secondary)] mb-1">{isZh ? "\u804C\u4F4D" : "Role"}</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
              >
                <option value="" className="bg-[var(--bg-surface)]">--</option>
                {roles.map((r) => (
                  <option key={r} value={r} className="bg-[var(--bg-surface)]">{r}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-[var(--text-secondary)] mb-1">{isZh ? "\u5E74\u9500\u552E\u989D" : "Annual Revenue"}</label>
              <select
                value={revenue}
                onChange={(e) => setRevenue(e.target.value)}
                className="w-full bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
              >
                <option value="" className="bg-[var(--bg-surface)]">--</option>
                {revenues.map((r) => (
                  <option key={r} value={r} className="bg-[var(--bg-surface)]">{r}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-[var(--text-secondary)] mb-1">{isZh ? "\u516C\u53F8\u7C7B\u578B" : "Business Model"}</label>
              <select
                value={bizType}
                onChange={(e) => setBizType(e.target.value)}
                className="w-full bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
              >
                <option value="" className="bg-[var(--bg-surface)]">--</option>
                {bizTypes.map((b) => (
                  <option key={b} value={b} className="bg-[var(--bg-surface)]">{b}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs text-[var(--text-secondary)] mb-1">{isZh ? "\u53D1\u8D27\u65B9\u5F0F" : "Fulfillment"}</label>
              <select
                value={fulfillment}
                onChange={(e) => setFulfillment(e.target.value)}
                className="w-full bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
              >
                <option value="" className="bg-[var(--bg-surface)]">--</option>
                {fulfillments.map((f) => (
                  <option key={f} value={f} className="bg-[var(--bg-surface)]">{f}</option>
                ))}
              </select>
            </div>
            <div className="md:col-span-3">
              <label className="block text-xs text-[var(--text-secondary)] mb-1">{t("zhiku.marketplace")}</label>
              <div className="flex flex-wrap gap-1.5 max-h-28 overflow-y-auto p-2 bg-white/5 border border-[var(--border-glass)] rounded-lg">
                {marketplaceOptions.map((m) => (
                  <label key={m} className="flex items-center gap-1 text-xs text-[var(--text-secondary)] cursor-pointer">
                    <input
                      type="checkbox"
                      checked={marketplaces.includes(m)}
                      onChange={(e) => setMarketplaces(e.target.checked ? [...marketplaces, m] : marketplaces.filter((x) => x !== m))}
                      className="accent-[var(--accent)] w-3 h-3"
                    />
                    {m}
                  </label>
                ))}
              </div>
            </div>
            <div className="md:col-span-3">
              <label className="block text-xs text-[var(--text-secondary)] mb-1">{t("zhiku.content_focus")}</label>
              <div className="flex flex-wrap gap-1.5 max-h-28 overflow-y-auto p-2 bg-white/5 border border-[var(--border-glass)] rounded-lg">
                {contentOptions.map((c) => (
                  <label key={c} className="flex items-center gap-1 text-xs text-[var(--text-secondary)] cursor-pointer">
                    <input
                      type="checkbox"
                      checked={contentFocus.includes(c)}
                      onChange={(e) => setContentFocus(e.target.checked ? [...contentFocus, c] : contentFocus.filter((x) => x !== c))}
                      className="accent-[var(--accent)] w-3 h-3"
                    />
                    {c}
                  </label>
                ))}
              </div>
            </div>
          </div>
          <div className="flex items-end gap-3 mt-4">
            <div className="w-24">
              <label className="block text-xs text-[var(--text-secondary)] mb-1">{t("zhiku.count")}</label>
              <input
                type="number"
                min={5}
                max={30}
                value={personaCount}
                onChange={(e) => setPersonaCount(Number(e.target.value))}
                className="w-full bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
              />
            </div>
            <Button onClick={handlePersonaExpand} loading={personaExpanding} disabled={!identity}>
              {t("zhiku.generate_persona")}
            </Button>
          </div>
          {personaExpanding && <ProgressBar percent={50} label={isZh ? "\u63A8\u6F14\u4E2D..." : "Generating..."} className="mt-3" />}
          {personaError && <p className="text-sm text-[var(--error)] mt-2">{personaError}</p>}
        </GlassCard>
      )}

      {/* Tab: Upload */}
      {activeTab === "upload" && (
        <GlassCard>
          <p className="text-xs text-[var(--text-secondary)] mb-4">{t("zhiku.upload_desc")}</p>
          <div className="flex gap-3 mb-4">
            <button
              onClick={() => setUploadType("phrases")}
              className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${
                uploadType === "phrases"
                  ? "bg-[var(--accent)]/10 text-[var(--accent)] border-[var(--accent)]/30"
                  : "text-[var(--text-secondary)] border-[var(--border-glass)] hover:bg-white/5"
              }`}
            >
              {isZh ? "\u68C0\u7D22\u77ED\u8BED" : "Search Phrases"}
            </button>
            <button
              onClick={() => setUploadType("keywords")}
              className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${
                uploadType === "keywords"
                  ? "bg-[var(--accent)]/10 text-[var(--accent)] border-[var(--accent)]/30"
                  : "text-[var(--text-secondary)] border-[var(--border-glass)] hover:bg-white/5"
              }`}
            >
              {isZh ? "SEO/SEM \u5173\u952E\u8BCD" : "SEO/SEM Keywords"}
            </button>
          </div>
          <p className="text-xs text-[var(--text-muted)] mb-3">
            {uploadType === "phrases"
              ? (isZh ? "CSV \u9700\u5305\u542B ai_query \u5217\uFF08\u6216\u7B2C\u4E00\u5217\u4E3A\u77ED\u8BED\uFF09" : "CSV must have ai_query column (or first column as phrases)")
              : (isZh ? "CSV \u9700\u5305\u542B keyword \u5217\uFF0C\u5C06\u88AB\u6269\u5C55\u4E3A\u68C0\u7D22\u77ED\u8BED" : "CSV should have keyword column, will be expanded to search phrases")
            }
          </p>
          <div className="flex items-center gap-3">
            <label className="flex-1">
              <input
                type="file"
                accept=".csv,.xlsx"
                onChange={(e) => setUploadFile(e.target.files?.[0] ?? null)}
                className="block w-full text-xs text-[var(--text-secondary)] file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border file:border-[var(--border-glass)] file:text-xs file:font-medium file:bg-white/5 file:text-[var(--text-primary)] hover:file:bg-white/10 file:cursor-pointer"
              />
            </label>
            <Button onClick={handleUpload} loading={uploading} disabled={!uploadFile}>
              {t("zhiku.upload_btn")}
            </Button>
          </div>
          {uploadError && <p className="text-sm text-[var(--error)] mt-2">{uploadError}</p>}
          {uploadSuccess && <p className="text-sm text-[var(--success)] mt-2">{uploadSuccess}</p>}
        </GlassCard>
      )}

      {/* Metrics */}
      <div className="flex gap-4">
        <GlassCard padding="sm" className="flex-1">
          <p className="text-xs text-[var(--text-muted)]">{t("zhiku.total")}</p>
          <p className="text-lg font-bold text-[var(--accent)]">{phrases.length}</p>
        </GlassCard>
        <GlassCard padding="sm" className="flex-1">
          <p className="text-xs text-[var(--text-muted)]">{t("zhiku.selected")}</p>
          <p className="text-lg font-bold text-[var(--success)]">{selectedCount}</p>
        </GlassCard>
      </div>

      {/* Filters & Actions */}
      <div className="flex flex-wrap gap-3 items-center">
        <input
          type="text"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          placeholder={isZh ? "\u641C\u7D22\u77ED\u8BED..." : "Search phrases..."}
          className="bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-1.5 text-xs text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)] w-48"
        />
        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          className="bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-1.5 text-xs text-[var(--text-secondary)] focus:outline-none focus:border-[var(--accent)]"
        >
          <option value="">{isZh ? "\u6240\u6709\u5206\u7C7B" : "All Categories"}</option>
          {categories.map((c) => (
            <option key={c} value={c} className="bg-[var(--bg-secondary)]">{c}</option>
          ))}
        </select>
        <select
          value={filterIntent}
          onChange={(e) => setFilterIntent(e.target.value)}
          className="bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-1.5 text-xs text-[var(--text-secondary)] focus:outline-none focus:border-[var(--accent)]"
        >
          <option value="">{isZh ? "\u6240\u6709\u610F\u56FE" : "All Intent Types"}</option>
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
        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={() => handleBulkSelect(true)}
            className="text-xs text-[var(--text-secondary)] hover:text-[var(--accent)] transition-colors"
          >
            {"\u2611\uFE0F"} {t("zhiku.select_all")}
          </button>
          <button
            onClick={() => handleBulkSelect(false)}
            className="text-xs text-[var(--text-secondary)] hover:text-[var(--accent)] transition-colors"
          >
            {"\u2610"} {t("zhiku.deselect_all")}
          </button>
          <button
            onClick={handleArchiveSelected}
            className="text-xs text-[var(--error)] hover:text-red-600 transition-colors"
          >
            {"\uD83D\uDDD1\uFE0F"} {isZh ? "\u6E05\u9664\u9009\u4E2D" : "Clear Selected"}
          </button>
          <button
            onClick={handleArchiveAll}
            className="text-xs text-[var(--error)] hover:text-red-600 transition-colors"
          >
            {"\uD83D\uDDD1\uFE0F"} {isZh ? "\u6E05\u9664\u5168\u90E8" : "Clear All"}
          </button>
          <span className="text-xs text-[var(--text-muted)]">
            {filteredPhrases.length} / {phrases.length}
          </span>
        </div>
      </div>

      {/* Phrase Table */}
      <GlassCard padding="sm">
        {loading ? (
          <div className="text-center py-8 text-[var(--text-secondary)]">{t("common.loading")}</div>
        ) : filteredPhrases.length === 0 ? (
          <div className="text-center py-8 text-[var(--text-secondary)]">{t("zhiku.empty")}</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border-glass)]">
                  <th className="px-2 py-2 text-left w-8">{"\u2713"}</th>
                  {(["ai_query", "source", "intent_type", "priority_score", "category"] as const).map((col) => (
                    <th
                      key={col}
                      className="px-2 py-2 text-left cursor-pointer hover:text-[var(--accent)] transition-colors text-xs text-[var(--text-secondary)]"
                      onClick={() => handleSort(col)}
                    >
                      {col === "ai_query" ? (isZh ? "\u68C0\u7D22\u77ED\u8BED" : "Query")
                        : col === "source" ? (isZh ? "\u6765\u6E90" : "Source")
                        : col === "intent_type" ? (isZh ? "\u610F\u56FE" : "Intent")
                        : col === "priority_score" ? (isZh ? "\u8BC4\u5206" : "Score")
                        : col === "category" ? (isZh ? "\u5206\u7C7B" : "Category") : col}
                      {sortKey === col && (sortAsc ? " \u2191" : " \u2193")}
                    </th>
                  ))}
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
                        checked={isSelected(phrase.is_selected)}
                        onChange={() => handleToggleSelect(idx)}
                        className="accent-[var(--accent)]"
                        aria-label={`Select ${phrase.ai_query}`}
                      />
                    </td>
                    <td className="px-2 py-2 text-[var(--text-primary)] max-w-[300px]">
                      {truncateText(phrase.ai_query, 60)}
                    </td>
                    <td className="px-2 py-2 text-[var(--text-muted)] text-xs">
                      {phrase.source ?? "\u2014"}
                    </td>
                    <td className="px-2 py-2 text-[var(--text-secondary)]">{phrase.intent_type}</td>
                    <td className="px-2 py-2 text-[var(--accent)] font-mono">{phrase.priority_score}</td>
                    <td className="px-2 py-2 text-[var(--text-muted)]">{phrase.category}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>

      {/* CTA to next step */}
      <div className="flex items-center justify-end gap-3">
        {selectedCount > 0 && (
          <span className="text-xs text-[var(--success)]">
            {"\u2705"} {selectedCount} {isZh ? "\u6761\u5DF2\u9009\u4E2D\uFF08\u81EA\u52A8\u4FDD\u5B58\uFF09" : "selected (auto-saved)"}
          </span>
        )}
        <Button onClick={() => {
          // Save selected phrases for zhice page via localStorage
          const selectedPhrases = phrases.filter((p) => isSelected(p.is_selected)).map((p) => p.ai_query);
          localStorage.setItem("zhiku_selected_phrases", JSON.stringify(selectedPhrases));
          // Also pass via URL query params as backup
          const encoded = encodeURIComponent(JSON.stringify(selectedPhrases));
          router.push(`/zhice?phrases=${encoded}`);
        }}>
          {t("zhiku.next_step")}
        </Button>
      </div>

      {/* History / Archive Section */}
      <GlassCard>
        <details>
          <summary className="cursor-pointer text-sm font-medium text-[var(--text-secondary)] select-none">
            {"\uD83D\uDCC1"} {isZh ? "\u5386\u53F2\u8BB0\u5F55\uFF08\u5DF2\u5F52\u6863\uFF09" : "History (Archived)"}
          </summary>
          <HistoryPanel batchId={activeBatch} isZh={isZh} onRestore={loadPhrases} />
        </details>
      </GlassCard>
    </div>
  );
}

function HistoryPanel({ batchId, isZh, onRestore }: { batchId: string; isZh: boolean; onRestore: () => void }) {
  const [archived, setArchived] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(false);
  const [restoring, setRestoring] = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const res = await apiGet<{ items: Record<string, unknown>[]; total: number }>("/api/archive", {
          batch_id: batchId,
          step: "01_zhiku",
        });
        setArchived(res.items);
      } catch {
        setArchived([]);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [batchId]);

  const handleRestore = async (query: string) => {
    setRestoring(true);
    try {
      await apiPost("/api/restore", {
        batch_id: batchId,
        step: "01_zhiku",
        filename: "zhiku_ai_queries.csv",
        queries: [query],
      });
      setArchived((prev) => prev.filter((item) => item.ai_query !== query));
      onRestore();
    } catch {
      // ignore
    } finally {
      setRestoring(false);
    }
  };

  const handleRestoreAll = async () => {
    if (archived.length === 0) return;
    setRestoring(true);
    try {
      const allQueries = archived.map((item) => String(item.ai_query ?? "")).filter(Boolean);
      await apiPost("/api/restore", {
        batch_id: batchId,
        step: "01_zhiku",
        filename: "zhiku_ai_queries.csv",
        queries: allQueries,
      });
      setArchived([]);
      onRestore();
    } catch {
      // ignore
    } finally {
      setRestoring(false);
    }
  };

  if (loading) return <p className="text-xs text-[var(--text-muted)] py-2">{isZh ? "\u52A0\u8F7D\u4E2D..." : "Loading..."}</p>;
  if (archived.length === 0) return <p className="text-xs text-[var(--text-muted)] py-2">{isZh ? "\u6682\u65E0\u5386\u53F2\u8BB0\u5F55" : "No history yet"}</p>;

  return (
    <div className="mt-3 space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs text-[var(--text-muted)]">{archived.length} {isZh ? "\u6761\u5DF2\u5F52\u6863" : "archived items"}</span>
        <button
          onClick={handleRestoreAll}
          disabled={restoring}
          className="text-xs text-[var(--accent)] hover:underline disabled:opacity-50"
        >
          {"\uD83D\uDD04"} {isZh ? "\u5168\u90E8\u6062\u590D" : "Restore All"}
        </button>
      </div>
      <div className="max-h-48 overflow-y-auto border border-[var(--border-card)] rounded-lg">
        <table className="w-full text-xs">
          <tbody>
            {archived.slice(0, 30).map((item, idx) => (
              <tr key={idx} className="border-b border-[var(--border-card)]/50 hover:bg-[var(--bg-surface)]">
                <td className="px-2 py-1.5 max-w-[300px] truncate">{String(item.ai_query ?? "")}</td>
                <td className="px-2 py-1.5 text-[var(--text-muted)]">{String(item._archived_at ?? "")}</td>
                <td className="px-1 py-1.5">
                  <button
                    onClick={() => handleRestore(String(item.ai_query ?? ""))}
                    disabled={restoring}
                    className="text-[var(--accent)] hover:underline disabled:opacity-50"
                  >
                    {isZh ? "\u6062\u590D" : "Restore"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
