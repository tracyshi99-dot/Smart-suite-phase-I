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
import { apiPost } from "@/lib/api-client";
import { ZhizaoRequest, DraftContent } from "@/lib/types";
import { TEMPLATES, LONG_OP_TIMEOUT_MS } from "@/lib/constants";
import { truncateText } from "@/lib/utils";

export default function ZhizaoPage() {
  const router = useRouter();
  const { t, locale } = useI18nStore();
  const { activeBatch } = useBatchStore();
  const { regionConfig } = useAuthStore();
  const isZh = locale.startsWith("zh");

  // Phrases from zhice
  const [phrases, setPhrases] = useState<string[]>([]);
  const [contentLimit, setContentLimit] = useState(5);
  const [language, setLanguage] = useState(locale || "zh-CN");
  const [template, setTemplate] = useState("auto");
  const [generating, setGenerating] = useState(false);
  const [drafts, setDrafts] = useState<DraftContent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  // Load phrases from zhice (localStorage)
  useEffect(() => {
    try {
      const saved = localStorage.getItem("zhice_selected_queries");
      if (saved) {
        const parsed = JSON.parse(saved) as string[];
        if (Array.isArray(parsed) && parsed.length > 0) {
          setPhrases(parsed);
          setContentLimit(parsed.length);
        }
      }
    } catch { /* ignore */ }
  }, []);

  const handleGenerate = async () => {
    if (phrases.length === 0) {
      setError(isZh ? "\u6CA1\u6709\u5F85\u751F\u6210\u77ED\u8BED" : "No phrases to generate");
      return;
    }
    setGenerating(true);
    setError(null);
    try {
      // Step 1: Upload phrases to S3 as selected (so Lambda can find them)
      const API_BASE = "https://asq6n6kw78.execute-api.us-east-1.amazonaws.com";
      await fetch(`${API_BASE}/api/zhiku/upload`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phrases: phrases,
          source: "zhice_verified",
          batch_id: activeBatch,
        }),
      });

      // Step 2: Call Lambda generate (uses Claude→Claude→Qianwen pipeline)
      const res = await fetch(`${API_BASE}/api/zhizao/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          batch_id: activeBatch,
          content_limit: contentLimit,
          content_language: language,
          template_id: template,
        }),
      });
      const data = await res.json() as { drafts?: DraftContent[]; success?: boolean; error?: string; message?: string };
      if (data.drafts && data.drafts.length > 0) {
        setDrafts(data.drafts);
      } else {
        setError(isZh ? `\u751F\u6210\u5931\u8D25: ${data.error || data.message || "timeout"}` : `Generation failed: ${data.error || data.message || "timeout"}`);
      }
    } catch {
      setError(isZh ? "\u751F\u6210\u5931\u8D25\uFF0C\u8BF7\u91CD\u8BD5" : "Generation failed, please retry");
    } finally {
      setGenerating(false);
    }
  };

  // Handle file upload (existing content / reference materials)
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      let items: string[] = [];
      const ext = file.name.split(".").pop()?.toLowerCase();

      if (ext === "xlsx" || ext === "xls") {
        // Parse Excel
        const XLSX = await import("xlsx");
        const buffer = await file.arrayBuffer();
        const wb = XLSX.read(buffer, { type: "array" });
        const ws = wb.Sheets[wb.SheetNames[0]];
        const rows = XLSX.utils.sheet_to_json<Record<string, unknown>>(ws, { header: 1 }) as unknown[][];
        // Take first column, skip header if it looks like one
        const startIdx = rows.length > 0 && typeof rows[0]?.[0] === "string" &&
          (rows[0][0] as string).toLowerCase().includes("query") || (rows[0]?.[0] as string)?.includes("\u68C0\u7D22") ? 1 : 0;
        items = rows.slice(startIdx)
          .map((row) => String(row[0] ?? "").trim())
          .filter((s) => s.length > 3);
      } else {
        // CSV / TXT / MD
        const text = await file.text();
        const lines = text.split("\n").map((l) => l.trim()).filter((l) => l.length > 5);
        items = lines.map((l) => l.split(",")[0]?.trim().replace(/^["']|["']$/g, "")).filter(Boolean);
      }

      if (items.length > 0) {
        setPhrases((prev) => [...new Set([...prev, ...items])]);
        setContentLimit((prev) => Math.max(prev, items.length));
      }
    } catch { /* ignore */ }
    e.target.value = "";
  };

  return (
    <div className="space-y-6 max-w-[1400px]">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{t("zhizao.title")}</h1>
        <BatchSelector />
      </div>

      {/* Source Phrases from Zhice */}
      {phrases.length > 0 && (
        <GlassCard>
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-sm font-medium text-[var(--text-secondary)]">
              {isZh ? `\u2460 \u5F85\u751F\u6210\u77ED\u8BED (${phrases.length} \u7BC7)` : `\u2460 Phrases to Generate (${phrases.length} articles)`}
            </h2>
            <button
              onClick={() => { setPhrases([]); localStorage.removeItem("zhice_selected_queries"); }}
              className="text-xs text-[var(--text-muted)] hover:text-[var(--error)]"
            >
              {isZh ? "\u6E05\u9664" : "Clear"}
            </button>
          </div>
          <div className="max-h-40 overflow-y-auto bg-white/5 rounded-lg p-2 border border-[var(--border-glass)]">
            {phrases.map((p, i) => (
              <div key={i} className="flex items-center justify-between py-0.5">
                <span className="text-xs text-[var(--text-primary)]">{i + 1}. {p}</span>
                <button
                  onClick={() => setPhrases((prev) => prev.filter((_, idx) => idx !== i))}
                  className="text-xs text-[var(--text-muted)] hover:text-[var(--error)] ml-2"
                >
                  {"\u2715"}
                </button>
              </div>
            ))}
          </div>
        </GlassCard>
      )}

      {/* Upload / Add Phrases */}
      <GlassCard>
        <div className="flex items-center gap-4 flex-wrap">
          <label className="text-xs text-[var(--text-secondary)]">
            {isZh ? "\u4E0A\u4F20\u7D20\u6750/\u5DF2\u6709\u5185\u5BB9" : "Upload materials/existing content"}:
          </label>
          <input
            type="file"
            accept=".csv,.txt,.md,.xlsx,.xls"
            onChange={handleUpload}
            className="text-xs text-[var(--text-secondary)] file:mr-2 file:py-1.5 file:px-3 file:rounded-lg file:border file:border-[var(--border-glass)] file:text-xs file:bg-white/5 file:text-[var(--text-primary)] hover:file:bg-white/10 file:cursor-pointer"
          />
          <span className="text-[10px] text-[var(--text-muted)]">
            {isZh ? "CSV/TXT/MD/Excel\uFF0C\u6BCF\u884C\u4E00\u6761\u77ED\u8BED\u6216\u5185\u5BB9" : "CSV/TXT/MD/Excel, one phrase or content per line"}
          </span>
        </div>
      </GlassCard>

      {/* Generate Form */}
      <GlassCard>
        <div className="flex flex-wrap gap-4 items-end">
          <div>
            <label className="block text-xs text-[var(--text-secondary)] mb-1">Limit</label>
            <input
              type="number"
              min={1}
              max={30}
              value={contentLimit}
              onChange={(e) => setContentLimit(Number(e.target.value))}
              className="w-20 bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
            />
          </div>
          <div>
            <label className="block text-xs text-[var(--text-secondary)] mb-1">Language</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
            >
              <option value="zh-CN" className="bg-[var(--bg-secondary)]">{"\u7B80\u4F53\u4E2D\u6587"}</option>
              <option value="en" className="bg-[var(--bg-secondary)]">English</option>
              <option value="zh-TW" className="bg-[var(--bg-secondary)]">{"\u7E41\u9AD4\u4E2D\u6587"}</option>
              <option value="ko" className="bg-[var(--bg-secondary)]">{"\uD55C\uAD6D\uC5B4"}</option>
              <option value="vi" className="bg-[var(--bg-secondary)]">Ti\u1EBFng Vi\u1EC7t</option>
              <option value="ja" className="bg-[var(--bg-secondary)]">{"\u65E5\u672C\u8A9E"}</option>
              <option value="de" className="bg-[var(--bg-secondary)]">Deutsch</option>
              <option value="fr" className="bg-[var(--bg-secondary)]">Fran\u00E7ais</option>
              <option value="es" className="bg-[var(--bg-secondary)]">Espa\u00F1ol</option>
              <option value="ar" className="bg-[var(--bg-secondary)]">{"\u0627\u0644\u0639\u0631\u0628\u064A\u0629"}</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-[var(--text-secondary)] mb-1">Template</label>
            <select
              value={template}
              onChange={(e) => setTemplate(e.target.value)}
              className="bg-white/5 border border-[var(--border-glass)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]"
            >
              {TEMPLATES.map((tmpl) => (
                <option key={tmpl.id} value={tmpl.id} className="bg-[var(--bg-secondary)]">{tmpl.label}</option>
              ))}
            </select>
          </div>
          <Button onClick={handleGenerate} loading={generating}>
            {t("zhizao.generate")}
          </Button>
        </div>
        {generating && <ProgressBar percent={45} label={isZh ? "\u751F\u6210\u4E2D..." : "Generating..."} className="mt-3" />}
        {error && <p className="text-sm text-[var(--error)] mt-2">{error}</p>}
      </GlassCard>

      {/* Drafts List */}
      {drafts.length > 0 && (
        <div className="space-y-2">
          {drafts.map((draft, idx) => (
            <GlassCard key={idx} padding="sm">
              <div
                className="flex items-center justify-between cursor-pointer"
                onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
              >
                <div className="flex-1">
                  <p className="text-sm font-medium">{draft.title || draft.ai_query}</p>
                  <p className="text-xs text-[var(--text-muted)]">
                    {draft.ai_query} • {draft.word_count} words
                  </p>
                </div>
                <span className="text-[var(--text-muted)]">{expandedIdx === idx ? "\u25BC" : "\u25B6"}</span>
              </div>
              {expandedIdx === idx && (
                <div className="mt-3 pt-3 border-t border-[var(--border-glass)]">
                  <p className="text-sm text-[var(--text-secondary)] whitespace-pre-wrap">
                    {truncateText(draft.content_draft, 500)}
                  </p>
                </div>
              )}
            </GlassCard>
          ))}
        </div>
      )}

      {/* CTA */}
      <div className="flex justify-end pt-4">
        <button onClick={() => router.push("/zhiyou")} className="px-4 py-2 rounded-lg text-sm font-medium bg-[var(--accent)] text-black hover:bg-[var(--accent-hover)] transition-colors">
          {isZh ? "\u4E0B\u4E00\u6B65\uFF1A\u5185\u5BB9\u4F18\u5316 \u2192" : "Next: Optimize \u2192"}
        </button>
      </div>
    </div>
  );
}
