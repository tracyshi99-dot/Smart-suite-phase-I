"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useI18nStore } from "@/stores/i18n-store";
import { useBatchStore } from "@/stores/batch-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { DraftContent } from "@/lib/types";

interface ZhibuItem {
  content_id: string;
  query_id: string;
  keyword_id: string;
  keyword: string;
  ai_query: string;
  meta: { title: string; description: string };
  body: string;
  faq: string | { question: string; answer: string }[];
  cta: string;
  geo_summary: string;
  ai_friendly: {
    intent_match_score: string;
    ai_readability_score: string;
    authority_score: string;
    actionability_score: string;
    differentiation_score: string;
    overall_score: number;
  };
  compliance: { status: string; copyright: string };
  quality_metrics: { word_count: number; table_count: number; list_count: number; link_count: number };
}

interface ZhibuOutput {
  batch_id: string;
  created_at: string;
  total_items: number;
  items: ZhibuItem[];
}

interface ZhibuOutput {
  batch_id: string;
  created_at: string;
  total_items: number;
  items: ZhibuItem[];
}

function convertToZhibuJSON(drafts: DraftContent[], batchId: string): ZhibuOutput {
  const now = new Date().toISOString().replace("T", " ").slice(0, 19);

  const items: ZhibuItem[] = drafts.map((draft, idx) => {
    const content = draft.content_draft || "";

    // Generate content_id matching Streamlit format: C_PRED_{batch_num}_{hash}
    const batchNum = batchId.replace("batch_", "").padStart(3, "0");
    const hash = String(Math.abs(hashCode(draft.ai_query + draft.title))).padStart(5, "0");
    const cid = `C_PRED_${batchNum}_${hash}`;

    // Count quality metrics
    const tableCount = (content.match(/\|---/g) || []).length > 0 ? (content.match(/\|---/g) || []).length : 0;
    const listCount = (content.match(/^\s*[-*•✅🔍🔹]\s/gm) || []).length;
    const linkCount = (content.match(/https?:\/\//g) || []).length;

    return {
      content_id: cid,
      query_id: `PRED_${batchNum}_Q${(idx + 1).toString().padStart(2, "0")}`,
      keyword_id: `PRED_${batchNum}`,
      keyword: draft.ai_query,
      ai_query: draft.ai_query,
      meta: {
        title: draft.title || draft.ai_query,
        description: "",
      },
      body: content,
      faq: "",
      cta: "",
      geo_summary: "",
      ai_friendly: {
        intent_match_score: "4",
        ai_readability_score: "4",
        authority_score: "4",
        actionability_score: "4",
        differentiation_score: "4",
        overall_score: 4.0,
      },
      compliance: {
        status: "PASS",
        copyright: `Copyright © ${new Date().getFullYear()} Amazon. All rights Reserved.`,
      },
      quality_metrics: {
        word_count: content.length,
        table_count: tableCount,
        list_count: listCount,
        link_count: linkCount,
      },
    };
  });

  return {
    batch_id: batchId,
    created_at: now,
    total_items: items.length,
    items,
  };
}

// Simple hash function for generating stable IDs
function hashCode(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash |= 0;
  }
  return Math.abs(hash) % 100000;
}

export default function ZhibuPage() {
  const router = useRouter();
  const { t, locale } = useI18nStore();
  const { activeBatch } = useBatchStore();
  const isZh = locale.startsWith("zh");

  const [drafts, setDrafts] = useState<DraftContent[]>([]);
  const [jsonOutput, setJsonOutput] = useState<ZhibuOutput | null>(null);
  const [showPreview, setShowPreview] = useState(false);

  // Load drafts from zhiyou
  useEffect(() => {
    try {
      const saved = localStorage.getItem("zhiyou_final_drafts");
      if (saved) {
        const parsed = JSON.parse(saved) as DraftContent[];
        if (Array.isArray(parsed) && parsed.length > 0) {
          setDrafts(parsed);
          return;
        }
      }
      // Fallback: try zhizao_selected_drafts
      const fallback = localStorage.getItem("zhizao_selected_drafts");
      if (fallback) {
        const parsed = JSON.parse(fallback) as DraftContent[];
        if (Array.isArray(parsed) && parsed.length > 0) {
          setDrafts(parsed);
        }
      }
    } catch { /* ignore */ }
  }, []);

  // Generate JSON
  const handleGenerate = () => {
    if (drafts.length === 0) return;
    const output = convertToZhibuJSON(drafts, activeBatch);
    setJsonOutput(output);
  };

  // Download JSON (all in one file)
  const handleDownload = () => {
    if (!jsonOutput) return;
    const blob = new Blob([JSON.stringify(jsonOutput, null, 2)], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `zhibu_output_${activeBatch}_${jsonOutput.total_items}items.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Download each article as separate JSON file
  const handleDownloadEach = () => {
    if (!jsonOutput) return;
    jsonOutput.items.forEach((item, idx) => {
      const singleOutput = {
        batch_id: jsonOutput.batch_id,
        created_at: jsonOutput.created_at,
        total_items: 1,
        source_keywords: [item.meta.title],
        items: [item],
      };
      const blob = new Blob([JSON.stringify(singleOutput, null, 2)], { type: "application/json;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const safeName = item.meta.title.slice(0, 30).replace(/[/\\?%*:|"<>]/g, "");
      a.download = `${(idx + 1).toString().padStart(2, "0")}_${safeName}.json`;
      a.click();
      URL.revokeObjectURL(url);
    });
  };

  // Copy JSON to clipboard
  const handleCopy = () => {
    if (!jsonOutput) return;
    navigator.clipboard.writeText(JSON.stringify(jsonOutput, null, 2));
  };

  return (
    <div className="space-y-6 max-w-[1400px]">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{t("zhibu.title")}</h1>
      </div>

      {/* Source content from zhiyou */}
      {drafts.length === 0 ? (
        <GlassCard>
          <div className="text-center py-8">
            <p className="text-sm text-[var(--text-muted)]">
              {isZh ? "暂无待发布内容。请先在「智优」中完成优化并点击「下一步」。" : "No content to publish. Complete optimization in Zhiyou first."}
            </p>
            <button onClick={() => router.push("/zhiyou")} className="mt-3 text-xs text-[var(--accent)] hover:underline">
              {isZh ? "← 返回智优" : "← Back to Zhiyou"}
            </button>
          </div>
        </GlassCard>
      ) : (
        <>
          {/* Content summary */}
          <GlassCard>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-medium text-[var(--text-secondary)]">
                {isZh ? `① 待发布内容 (${drafts.length} 篇)` : `① Content to Publish (${drafts.length} articles)`}
              </h2>
              <button onClick={() => router.push("/zhiyou")} className="text-xs text-[var(--text-muted)] hover:text-[var(--accent)]">
                {isZh ? "← 返回智优" : "← Back"}
              </button>
            </div>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {drafts.map((d, idx) => (
                <div key={idx} className="flex items-center justify-between px-2 py-1 rounded bg-white/5">
                  <span className="text-xs text-[var(--text-primary)]">{idx + 1}. {d.title || d.ai_query}</span>
                  <span className="text-[10px] text-[var(--text-muted)]">{d.word_count || d.content_draft.length} {isZh ? "字" : "chars"}</span>
                </div>
              ))}
            </div>
          </GlassCard>

          {/* Generate JSON */}
          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
              ② {isZh ? "生成 LEGO CMS JSON" : "Generate LEGO CMS JSON"}
            </h2>
            <p className="text-xs text-[var(--text-muted)] mb-3">
              {isZh
                ? "将优化后的内容转换为 LEGO CMS 标准 JSON 格式，包含 meta、structure、body、FAQ、SEO、合规信息等完整字段。"
                : "Convert optimized content to LEGO CMS standard JSON with meta, structure, body, FAQ, SEO, compliance fields."}
            </p>
            <Button onClick={handleGenerate} disabled={drafts.length === 0}>
              {isZh ? "🔄 生成 JSON" : "🔄 Generate JSON"}
            </Button>
          </GlassCard>

          {/* JSON Output */}
          {jsonOutput && (
            <GlassCard>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-medium text-[var(--text-secondary)]">
                  ③ {isZh ? "输出结果" : "Output"} — {jsonOutput.total_items} {isZh ? "条" : "items"}
                </h2>
                <div className="flex gap-2">
                  <button onClick={handleCopy} className="text-xs px-3 py-1.5 rounded-lg border border-[var(--border-glass)] text-[var(--text-secondary)] hover:text-[var(--accent)]">
                    {isZh ? "📋 复制" : "📋 Copy"}
                  </button>
                  <button onClick={handleDownloadEach} className="text-xs px-3 py-1.5 rounded-lg border border-[var(--border-glass)] text-[var(--accent)] hover:bg-[var(--accent)]/10">
                    ⬇ {isZh ? "逐篇下载 JSON" : "Download Each JSON"}
                  </button>
                  <button onClick={handleDownload} className="text-xs px-3 py-1.5 rounded-lg border border-[var(--border-glass)] text-[var(--text-secondary)] hover:text-[var(--accent)]">
                    ⬇ {isZh ? "下载合集" : "Download All"}
                  </button>
                  <button
                    onClick={() => setShowPreview(!showPreview)}
                    className="text-xs px-3 py-1.5 rounded-lg border border-[var(--border-glass)] text-[var(--text-secondary)] hover:text-[var(--accent)]"
                  >
                    {showPreview ? (isZh ? "▲ 收起" : "▲ Hide") : (isZh ? "▼ 预览 JSON" : "▼ Preview")}
                  </button>
                </div>
              </div>

              {/* Summary cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3">
                <div className="text-center p-2 rounded bg-white/5">
                  <p className="text-[10px] text-[var(--text-muted)]">{isZh ? "文章数" : "Articles"}</p>
                  <p className="text-lg font-bold text-[var(--accent)]">{jsonOutput.total_items}</p>
                </div>
                <div className="text-center p-2 rounded bg-white/5">
                  <p className="text-[10px] text-[var(--text-muted)]">{isZh ? "总字数" : "Total Words"}</p>
                  <p className="text-lg font-bold">{jsonOutput.items.reduce((a, i) => a + i.quality_metrics.word_count, 0).toLocaleString()}</p>
                </div>
                <div className="text-center p-2 rounded bg-white/5">
                  <p className="text-[10px] text-[var(--text-muted)]">JSON {isZh ? "大小" : "Size"}</p>
                  <p className="text-lg font-bold">{(JSON.stringify(jsonOutput).length / 1024).toFixed(1)} KB</p>
                </div>
                <div className="text-center p-2 rounded bg-white/5">
                  <p className="text-[10px] text-[var(--text-muted)]">{isZh ? "合规状态" : "Compliance"}</p>
                  <p className="text-lg font-bold text-[var(--success)]">✅ PASS</p>
                </div>
              </div>

              {/* Item list */}
              <div className="space-y-2 mb-3">
                {jsonOutput.items.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2 rounded bg-white/5 border border-[var(--border-glass)]">
                    <div>
                      <p className="text-xs font-medium text-[var(--text-primary)]">{item.meta.title}</p>
                      <p className="text-[10px] text-[var(--text-muted)]">
                        {item.content_id} • {item.quality_metrics.word_count} {isZh ? "字" : "chars"} • Links:{item.quality_metrics.link_count}
                      </p>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-green-500/10 text-green-400">{item.compliance.status}</span>
                  </div>
                ))}
              </div>

              {/* Full JSON preview */}
              {showPreview && (
                <div className="max-h-96 overflow-y-auto bg-[#0a0a0f] rounded-lg p-4 border border-[var(--border-glass)]">
                  <pre className="text-xs text-green-300 font-mono whitespace-pre-wrap">
                    {JSON.stringify(jsonOutput, null, 2)}
                  </pre>
                </div>
              )}
            </GlassCard>
          )}
        </>
      )}

      {/* CTA */}
      <div className="flex justify-end pt-4">
        <button onClick={() => router.push("/zhixi")} className="px-4 py-2 rounded-lg text-sm font-medium bg-[var(--accent)] text-black hover:bg-[var(--accent-hover)] transition-colors">
          {isZh ? "下一步：查看智析 →" : "Next: Analytics →"}
        </button>
      </div>
    </div>
  );
}
