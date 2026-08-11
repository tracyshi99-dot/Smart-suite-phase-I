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
  const [language, setLanguage] = useState("zh-CN");
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
          priority_score: 3.0,
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
          priority_score: 3.5,
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
        lines[0]?.includes("检索") || lines[0]?.includes("关键");
      const dataLines = hasHeader ? lines.slice(1) : lines;
      // Extract first column (CSV)
      const phrases = dataLines
        .map((l) => l.split(",")[0]?.trim().replace(/^["']|["']$/g, ""))
        .filter((p) => p.length > 3);

      if (phrases.length === 0) {
        setUploadError(isZh ? "未检测到有效短语" : "No valid phrases detected");
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
        isZh ? `✅ 导入 ${phrases.length} 条` : `✅ Imported ${phrases.length} phrases`
      );
      setUploadFile(null);
    } catch {
      setUploadError(isZh ? "上传失败，请重试" : "Upload failed, please retry");
    } finally {
      setUploading(false);
    }
  };

  // Toggle selection
  const handleToggleSelect = async (idx: number) => {
    const phrase = filteredPhrases[idx];
    const originalIdx = phrases.indexOf(phrase);
    const newSelected = phrase.is_selected !== "TRUE";
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
      .map((p, i) => (p.is_selected === "TRUE" ? i : -1))
      .filter((i) => i >= 0);
    if (selectedIndices.length === 0) return;
    try {
      await apiPost("/api/archive", {
        batch_id: activeBatch,
        step: "01_zhiku",
        filename: "zhiku_ai_queries.csv",
        indices: selectedIndices,
      });
      setPhrases((prev) => prev.filter((p) => p.is_selected !== "TRUE"));
    } catch {
      // ignore
    }
  };

  // Archive all items
  const handleArchiveAll = async () => {
    if (phrases.length === 0) return;
    if (!confirm(isZh ? "确定清除全部短语？（将保存到历史记录）" : "Clear all phrases? (will be saved to history)")) return;
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
  const selectedCount = phrases.filter((p) => p.is_selected === "TRUE").length;

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
                {(regionConfig?.content_languages ?? [{ code: "zh-CN", name: "中文" }, { code: "en", name: "English" }]).map((l) => (
                  <option key={l.code} value={l.code} className="bg-[var(--bg-secondary)]">{l.name}</option>
                ))}
              </select>
            </div>
            <Button onClick={handleExpand} loading={expanding} disabled={!seed.trim()}>
              {t("zhiku.expand")}
            </Button>
          </div>
          {expanding && <ProgressBar percent={50} label={isZh ? "裂变中..." : "Expanding..."} className="mt-3" />}
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
              {isZh ? "检索短语" : "Search Phrases"}
            </button>
            <button
              onClick={() => setUploadType("keywords")}
              className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${
                uploadType === "keywords"
                  ? "bg-[var(--accent)]/10 text-[var(--accent)] border-[var(--accent)]/30"
                  : "text-[var(--text-secondary)] border-[var(--border-glass)] hover:bg-white/5"
              }`}
            >
              {isZh ? "SEO/SEM 关键词" : "SEO/SEM Keywords"}
            </button>
          </div>
          <p className="text-xs text-[var(--text-muted)] mb-3">
            {uploadType === "phrases"
              ? (isZh ? "CSV 必须包含 ai_query 列（或第一列为短语）" : "CSV must have ai_query column (or first column as phrases)")
              : (isZh ? "CSV 应包含 keyword 列，上传后将自动裂变为检索短语" : "CSV should have keyword column, will be expanded to search phrases")
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
          placeholder={isZh ? "搜索短语..." : "Search phrases..."}
          className="bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-1.5 text-xs text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)] w-48"
        />
        <select
          value={filterCategory}
          onChange={(e) => setFilterCategory(e.target.value)}
          className="bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-1.5 text-xs text-[var(--text-secondary)] focus:outline-none focus:border-[var(--accent)]"
        >
          <option value="">{isZh ? "所有分类" : "All Categories"}</option>
          {categories.map((c) => (
            <option key={c} value={c} className="bg-[var(--bg-secondary)]">{c}</option>
          ))}
        </select>
        <select
          value={filterIntent}
          onChange={(e) => setFilterIntent(e.target.value)}
          className="bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-1.5 text-xs text-[var(--text-secondary)] focus:outline-none focus:border-[var(--accent)]"
        >
          <option value="">{isZh ? "所有意图" : "All Intent Types"}</option>
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
            ☑️ {t("zhiku.select_all")}
          </button>
          <button
            onClick={() => handleBulkSelect(false)}
            className="text-xs text-[var(--text-secondary)] hover:text-[var(--accent)] transition-colors"
          >
            ☐ {t("zhiku.deselect_all")}
          </button>
          <button
            onClick={handleArchiveSelected}
            className="text-xs text-[var(--error)] hover:text-red-600 transition-colors"
          >
            🗑️ {isZh ? "清除选中" : "Clear Selected"}
          </button>
          <button
            onClick={handleArchiveAll}
            className="text-xs text-[var(--error)] hover:text-red-600 transition-colors"
          >
            🗑️ {isZh ? "清除全部" : "Clear All"}
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
                  <th className="px-2 py-2 text-left w-8">✓</th>
                  {(["ai_query", "source", "intent_type", "priority_score", "category"] as const).map((col) => (
                    <th
                      key={col}
                      className="px-2 py-2 text-left cursor-pointer hover:text-[var(--accent)] transition-colors text-xs text-[var(--text-secondary)]"
                      onClick={() => handleSort(col)}
                    >
                      {col === "ai_query" ? (isZh ? "检索短语" : "Query")
                        : col === "source" ? (isZh ? "来源" : "Source")
                        : col === "intent_type" ? (isZh ? "意图" : "Intent")
                        : col === "priority_score" ? (isZh ? "评分" : "Score")
                        : col === "category" ? (isZh ? "分类" : "Category") : col}
                      {sortKey === col && (sortAsc ? " ↑" : " ↓")}
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
                        checked={phrase.is_selected === "TRUE"}
                        onChange={() => handleToggleSelect(idx)}
                        className="accent-[var(--accent)]"
                        aria-label={`Select ${phrase.ai_query}`}
                      />
                    </td>
                    <td className="px-2 py-2 text-[var(--text-primary)] max-w-[300px]">
                      {truncateText(phrase.ai_query, 60)}
                    </td>
                    <td className="px-2 py-2 text-[var(--text-muted)] text-xs">
                      {phrase.source ?? "—"}
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
      {/* CTA to next step */}
      <div className="flex justify-end">
        <Button onClick={() => router.push("/zhice")}>
          {t("zhiku.next_step")}
        </Button>
      </div>

      {/* History / Archive Section */}
      <GlassCard>
        <details>
          <summary className="cursor-pointer text-sm font-medium text-[var(--text-secondary)] select-none">
            📂 {isZh ? "历史记录（已归档）" : "History (Archived)"}
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

  if (loading) return <p className="text-xs text-[var(--text-muted)] py-2">{isZh ? "加载中..." : "Loading..."}</p>;
  if (archived.length === 0) return <p className="text-xs text-[var(--text-muted)] py-2">{isZh ? "暂无历史记录" : "No history yet"}</p>;

  return (
    <div className="mt-3 space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs text-[var(--text-muted)]">{archived.length} {isZh ? "条已归档" : "archived items"}</span>
        <button
          onClick={handleRestoreAll}
          disabled={restoring}
          className="text-xs text-[var(--accent)] hover:underline disabled:opacity-50"
        >
          🔄 {isZh ? "全部恢复" : "Restore All"}
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
                    {isZh ? "恢复" : "Restore"}
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
