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
import { ZhizaoRequest, DraftContent } from "@/lib/types";
import { TEMPLATES, LONG_OP_TIMEOUT_MS } from "@/lib/constants";
import { truncateText } from "@/lib/utils";

export default function ZhizaoPage() {
  const { t } = useI18nStore();
  const { activeBatch } = useBatchStore();
  const { regionConfig } = useAuthStore();

  const [contentLimit, setContentLimit] = useState(5);
  const [language, setLanguage] = useState(regionConfig?.content_languages?.[0]?.code ?? "zh-CN");
  const [template, setTemplate] = useState("auto");
  const [generating, setGenerating] = useState(false);
  const [drafts, setDrafts] = useState<DraftContent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);
    try {
      const req: ZhizaoRequest = {
        batch_id: activeBatch,
        content_limit: contentLimit,
        content_language: language,
        template_id: template,
      };
      const res = await apiPost<{ drafts?: DraftContent[]; success?: boolean }>(
        "/api/zhizao/generate",
        req,
        { timeout: LONG_OP_TIMEOUT_MS }
      );
      setDrafts(res.drafts ?? []);
    } catch {
      setError("生成失败，请重试 / Generation failed");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6 max-w-[1400px]">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{t("zhizao.title")}</h1>
        <BatchSelector />
      </div>

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
              {(regionConfig?.content_languages ?? [{ code: "zh-CN", name: "中文" }]).map((l) => (
                <option key={l.code} value={l.code} className="bg-[var(--bg-secondary)]">{l.name}</option>
              ))}
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
        {generating && <ProgressBar percent={45} label="生成中 / Generating..." className="mt-3" />}
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
                <span className="text-[var(--text-muted)]">{expandedIdx === idx ? "▼" : "▶"}</span>
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
    </div>
  );
}
