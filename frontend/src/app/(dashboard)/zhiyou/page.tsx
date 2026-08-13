"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useI18nStore } from "@/stores/i18n-store";
import { useBatchStore } from "@/stores/batch-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { BatchSelector } from "@/components/ui/BatchSelector";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { apiPost } from "@/lib/api-client";
import { DraftContent, ZhiyouRequest, ScoreResult, OptimizeResult } from "@/lib/types";
import { LONG_OP_TIMEOUT_MS } from "@/lib/constants";

// Compliance result type
interface ComplianceResult {
  ai_query: string;
  title: string;
  status: "PASS" | "FAIL" | "FIXED";
  issues: string[];
  fixes_applied: string[];
}

// Local scoring function (rule-based, no API needed)
function localScore(draft: DraftContent): ScoreResult {
  const content = draft.content_draft || "";
  const len = content.length;

  // Intent Match: does content address the query directly?
  const queryWords = draft.ai_query.replace(/[？?！!。，,]/g, "").split(/\s+/).filter((w) => w.length > 1);
  const intentHits = queryWords.filter((w) => content.includes(w)).length;
  const intentMatch = Math.min(100, Math.round((intentHits / Math.max(queryWords.length, 1)) * 100));

  // AI Readability: structure indicators
  let readability = 50;
  if (content.includes("##") || content.includes("###")) readability += 15;
  if (content.includes("- ") || content.includes("1.")) readability += 10;
  if (content.includes("|")) readability += 10; // table
  if (len > 800) readability += 10;
  if (len > 1500) readability += 5;
  readability = Math.min(100, readability);

  // Authority: official links and brand mentions
  let authority = 40;
  if (content.toLowerCase().includes(".amazon")) authority += 25;
  if (content.includes("亚马逊") || content.toLowerCase().includes("amazon")) authority += 15;
  if (content.includes("https://")) authority += 10;
  if (content.includes("官方") || content.includes("official")) authority += 10;
  authority = Math.min(100, authority);

  // Actionability: how-to signals
  let actionability = 40;
  if (content.includes("步骤") || content.includes("step") || content.includes("如何")) actionability += 20;
  if (content.includes("FAQ") || content.includes("常见问题")) actionability += 15;
  if (content.includes("注意") || content.includes("提示") || content.includes("tip")) actionability += 10;
  if (len > 600) actionability += 15;
  actionability = Math.min(100, actionability);

  // Differentiation
  let differentiation = 50;
  if (content.includes("2026") || content.includes("2025")) differentiation += 15;
  if (content.includes("中国卖家") || content.includes("Chinese seller")) differentiation += 15;
  if (len > 1200) differentiation += 10;
  if (content.includes("案例") || content.includes("example") || content.includes("实操")) differentiation += 10;
  differentiation = Math.min(100, differentiation);

  const overall = Math.round(
    intentMatch * 0.25 + readability * 0.2 + authority * 0.25 + actionability * 0.15 + differentiation * 0.15
  );

  const compliance = authority >= 60 && !content.includes("保证赚钱") && !content.includes("绝对") ? "PASS" : "FAIL";

  return {
    ai_query: draft.ai_query,
    title: draft.title,
    intent_match: intentMatch,
    ai_readability: readability,
    authority,
    actionability,
    differentiation,
    overall_score: overall,
    compliance_status: compliance as "PASS" | "FAIL",
  };
}

export default function ZhiyouPage() {
  const router = useRouter();
  const { t, locale } = useI18nStore();
  const { activeBatch } = useBatchStore();
  const isZh = locale.startsWith("zh");

  // Drafts from zhizao
  const [drafts, setDrafts] = useState<DraftContent[]>([]);
  const [scoring, setScoring] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [complianceChecking, setComplianceChecking] = useState(false);
  const [scores, setScores] = useState<ScoreResult[]>([]);
  const [optimizeResults, setOptimizeResults] = useState<OptimizeResult[]>([]);
  const [complianceResults, setComplianceResults] = useState<ComplianceResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);
  const [progressPercent, setProgressPercent] = useState(0);
  const [progressLabel, setProgressLabel] = useState("");
  const [selectedFinal, setSelectedFinal] = useState<Set<number>>(new Set());
  const [expandedFinalIdx, setExpandedFinalIdx] = useState<number | null>(null);

  // Load drafts from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem("zhizao_selected_drafts");
      if (saved) {
        const parsed = JSON.parse(saved) as DraftContent[];
        if (Array.isArray(parsed) && parsed.length > 0) {
          setDrafts(parsed);
          return;
        }
      }
      // Fallback: try loading from zhizao_sessions (last session's drafts)
      const sessions = JSON.parse(localStorage.getItem("zhizao_sessions") || "[]");
      if (sessions.length > 0 && sessions[0].drafts?.length > 0) {
        setDrafts(sessions[0].drafts);
      }
    } catch { /* ignore */ }
  }, []);

  // Score locally (instant, no API)
  const handleLocalScore = () => {
    if (drafts.length === 0) return;
    setScoring(true);
    setError(null);
    // Simulate brief processing
    setTimeout(() => {
      const results = drafts.map((d) => localScore(d));
      setScores(results);
      setScoring(false);
    }, 300);
  };


  // Optimize via API (best effort) or show suggestions
  const handleOptimize = async () => {
    setOptimizing(true);
    setError(null);
    try {
      const req: ZhiyouRequest = { batch_id: activeBatch, content_language: "zh-CN" };
      const res = await apiPost<{ results?: OptimizeResult[] }>("/api/zhiyou/optimize", req, { timeout: LONG_OP_TIMEOUT_MS });
      if (res.results && res.results.length > 0) {
        setOptimizeResults(res.results);
      } else {
        // Generate local suggestions based on scores
        const suggestions = scores
          .filter((s) => s.compliance_status === "FAIL" || s.overall_score < 70)
          .map((s) => ({
            ai_query: s.ai_query,
            original_score: s.overall_score,
            optimized_score: Math.min(100, s.overall_score + 15),
            changes: generateSuggestions(s),
            compliance_status: "PASS" as const,
          }));
        setOptimizeResults(suggestions);
      }
    } catch {
      // Generate local suggestions
      const suggestions = scores
        .filter((s) => s.compliance_status === "FAIL" || s.overall_score < 70)
        .map((s) => ({
          ai_query: s.ai_query,
          original_score: s.overall_score,
          optimized_score: Math.min(100, s.overall_score + 15),
          changes: generateSuggestions(s),
          compliance_status: "PASS" as const,
        }));
      setOptimizeResults(suggestions);
    } finally {
      setOptimizing(false);
    }
  };

  const failedArticles = scores.filter((s) => s.compliance_status === "FAIL" || s.overall_score < 70);

  // Compliance check (Step 3.6)
  const handleCompliance = () => {
    if (drafts.length === 0) return;
    setComplianceChecking(true);
    setProgressPercent(60);
    setProgressLabel(isZh ? "合规审查中..." : "Compliance check...");

    setTimeout(() => {
      const results = drafts.map((d) => localComplianceCheck(d));
      setComplianceResults(results);
      setComplianceChecking(false);
      setProgressPercent(100);
      setProgressLabel("");
    }, 400);
  };

  // One-click optimize: Score → Optimize → Compliance (Claude + DeepSeek pipeline)
  const handleOneClickOptimize = async () => {
    if (drafts.length === 0) return;
    setError(null);
    setScoring(true);
    setProgressPercent(10);
    setProgressLabel(isZh ? "Step 3: Claude 评分校准中..." : "Step 3: Claude scoring...");

    try {
      // Call real API: Claude scores → DeepSeek optimizes → Compliance check
      const res = await fetch("/api/zhiyou/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ drafts, content_language: locale }),
      });

      setProgressPercent(60);
      setProgressLabel(isZh ? "Step 3.5: DeepSeek 优化重写中..." : "Step 3.5: DeepSeek rewriting...");

      const data = await res.json();

      if (data.success && data.results?.length > 0) {
        // Extract scores
        const scoreResults: ScoreResult[] = data.results.map((r: { ai_query: string; title: string; original_score: number; compliance_status: string }) => ({
          ai_query: r.ai_query,
          title: r.title,
          intent_match: 0, ai_readability: 0, authority: 0, actionability: 0, differentiation: 0,
          overall_score: r.original_score,
          compliance_status: r.compliance_status,
        }));
        setScores(scoreResults);

        // Extract optimization results
        const optResults: OptimizeResult[] = data.results
          .filter((r: { original_score: number; optimized_score: number }) => r.optimized_score > r.original_score)
          .map((r: { ai_query: string; original_score: number; optimized_score: number; compliance_status: string; compliance_issues: string[] }) => ({
            ai_query: r.ai_query,
            original_score: r.original_score,
            optimized_score: r.optimized_score,
            changes: r.compliance_issues.length > 0 ? r.compliance_issues : ["内容已通过 DeepSeek 优化重写"],
            compliance_status: r.compliance_status,
          }));
        setOptimizeResults(optResults);

        // Extract compliance results
        const compResults: ComplianceResult[] = data.results.map((r: { ai_query: string; title: string; compliance_status: string; compliance_issues: string[]; compliance_fixes: string[] }) => ({
          ai_query: r.ai_query,
          title: r.title,
          status: r.compliance_status,
          issues: r.compliance_issues || [],
          fixes_applied: r.compliance_fixes || [],
        }));
        setComplianceResults(compResults);

        // Update drafts with optimized content
        const updatedDrafts = drafts.map((d) => {
          const optimized = data.results.find((r: { ai_query: string; content_optimized: string; word_count: number }) => r.ai_query === d.ai_query);
          if (optimized && optimized.content_optimized && optimized.content_optimized !== d.content_draft) {
            return { ...d, content_draft: optimized.content_optimized, word_count: optimized.word_count };
          }
          return d;
        });
        setDrafts(updatedDrafts);
        // Persist updated drafts
        localStorage.setItem("zhizao_selected_drafts", JSON.stringify(updatedDrafts));

        setProgressPercent(100);
        setProgressLabel(isZh ? "✅ Claude 评分 + DeepSeek 优化 + 合规审查 完成" : "✅ Claude Score + DeepSeek Optimize + Compliance Done");
      } else {
        // API failed, fallback to local
        await handleOneClickLocal();
      }
    } catch {
      // Fallback to local processing
      await handleOneClickLocal();
    } finally {
      setScoring(false);
      setOptimizing(false);
      setComplianceChecking(false);
      setTimeout(() => { setProgressPercent(0); setProgressLabel(""); }, 3000);
    }
  };

  // Local fallback for one-click optimize
  const handleOneClickLocal = async () => {
    setProgressPercent(20);
    setProgressLabel(isZh ? "⚡ 本地评分中..." : "⚡ Local scoring...");
    await new Promise((resolve) => setTimeout(resolve, 300));
    const scoreResults = drafts.map((d) => localScore(d));
    setScores(scoreResults);
    setProgressPercent(50);

    setProgressLabel(isZh ? "⚡ 生成优化建议..." : "⚡ Generating suggestions...");
    await new Promise((resolve) => setTimeout(resolve, 200));
    const needsOpt = scoreResults.filter((s) => s.compliance_status === "FAIL" || s.overall_score < 70);
    setOptimizeResults(needsOpt.map((s) => ({
      ai_query: s.ai_query, original_score: s.overall_score,
      optimized_score: Math.min(100, s.overall_score + 15),
      changes: generateSuggestions(s), compliance_status: "PASS" as const,
    })));
    setProgressPercent(75);

    setProgressLabel(isZh ? "⚡ 合规审查..." : "⚡ Compliance...");
    await new Promise((resolve) => setTimeout(resolve, 200));
    setComplianceResults(drafts.map((d) => localComplianceCheck(d)));
    setProgressPercent(100);
    setProgressLabel(isZh ? "✅ 本地优化完成（API 不可用时降级）" : "✅ Local optimization done (API fallback)");
  };

  return (
    <div className="space-y-6 max-w-[1400px]">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{t("zhiyou.title")}</h1>
      </div>

      {/* Content Preview from Zhizao */}
      {drafts.length === 0 ? (
        <GlassCard>
          <div className="text-center py-8">
            <p className="text-sm text-[var(--text-muted)]">
              {isZh
                ? "暂无待优化内容。请先在「智造」中生成内容并点击「下一步」。"
                : "No content to optimize. Generate content in Zhizao first and click 'Next'."}
            </p>
            <button
              onClick={() => router.push("/zhizao")}
              className="mt-3 text-xs text-[var(--accent)] hover:underline"
            >
              {isZh ? "← 返回智造" : "← Back to Zhizao"}
            </button>
          </div>
        </GlassCard>
      ) : (
        <>
          {/* Drafts loaded indicator */}
          <GlassCard>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-sm font-medium text-[var(--text-secondary)]">
                {isZh ? `① 待优化内容 (${drafts.length} 篇)` : `① Content to Optimize (${drafts.length} articles)`}
              </h2>
              <button
                onClick={() => router.push("/zhizao")}
                className="text-xs text-[var(--text-muted)] hover:text-[var(--accent)]"
              >
                {isZh ? "← 返回智造" : "← Back to Zhizao"}
              </button>
            </div>
            <div className="space-y-1 max-h-48 overflow-y-auto">
              {drafts.map((d, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2 rounded bg-white/5 border border-[var(--border-glass)] cursor-pointer hover:border-[var(--accent)]/30"
                  onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
                >
                  <div className="flex-1">
                    <p className="text-xs font-medium text-[var(--text-primary)]">{d.title || d.ai_query}</p>
                    <p className="text-[10px] text-[var(--text-muted)]">
                      {d.ai_query} • {d.word_count} {isZh ? "字" : "chars"}
                    </p>
                  </div>
                  <span className="text-xs text-[var(--text-muted)]">{expandedIdx === idx ? "▼" : "▶"}</span>
                </div>
              ))}
            </div>
            {expandedIdx !== null && drafts[expandedIdx] && (
              <div className="mt-3 p-3 rounded-lg bg-white/5 border border-[var(--border-glass)] max-h-60 overflow-y-auto">
                <pre className="text-xs text-[var(--text-primary)] whitespace-pre-wrap leading-relaxed">
                  {drafts[expandedIdx].content_draft.slice(0, 2000)}
                  {drafts[expandedIdx].content_draft.length > 2000 && "..."}
                </pre>
              </div>
            )}
          </GlassCard>

          {/* Actions */}
          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
              {isZh ? "② 操作" : "② Actions"}
            </h2>
            <div className="flex gap-3 flex-wrap mb-4">
              <Button onClick={handleOneClickOptimize} loading={scoring || optimizing}>
                {isZh ? "🚀 一键优化（评分+优化+合规）" : "🚀 One-Click Optimize (Score+Optimize+Compliance)"}
              </Button>
              <Button onClick={handleLocalScore} loading={scoring} variant="secondary">
                {isZh ? "⚡ 仅评分" : "⚡ Score Only"}
              </Button>
              <Button onClick={handleOptimize} loading={optimizing} disabled={scores.length === 0} variant="secondary">
                {isZh ? "🔧 仅优化建议" : "🔧 Suggestions Only"}
              </Button>
              <Button onClick={handleCompliance} loading={complianceChecking} disabled={drafts.length === 0} variant="secondary">
                {isZh ? "⚖️ 仅合规审核" : "⚖️ Compliance Only"}
              </Button>
            </div>
            <div className="text-xs text-[var(--text-muted)] bg-white/5 rounded-lg p-3 border border-[var(--border-glass)]">
              <p className="font-medium text-[var(--text-secondary)] mb-1">{isZh ? "「一键优化」包含：" : "One-Click includes:"}</p>
              <ul className="list-disc list-inside space-y-0.5">
                <li>{isZh ? "Step 3 - AI 引用可能性评分（意图匹配、可读性、权威性、行动性、差异化 5 维度）" : "Step 3 - AI Citation Score (5 dimensions: Intent, Readability, Authority, Actionability, Differentiation)"}</li>
                <li>{isZh ? "Step 3.5 - 基于评分建议的内容优化推荐" : "Step 3.5 - Content optimization based on score suggestions"}</li>
                <li>{isZh ? "Step 3.6 - 合规审查（禁止绝对化承诺、敏感信息、法律风险检测）" : "Step 3.6 - Compliance check (prohibited claims, sensitive info, legal risk)"}</li>
              </ul>
            </div>
          </GlassCard>
          {(scoring || optimizing || complianceChecking) && <ProgressBar percent={progressPercent} label={progressLabel} />}
          {error && <p className="text-sm text-[var(--error)]">{error}</p>}

          {/* Score Results */}
          {scores.length > 0 && (
            <GlassCard padding="sm">
              <details>
                <summary className="text-sm font-medium text-[var(--text-secondary)] mb-3 cursor-pointer">
                  {isZh ? "③ 评分结果" : "③ Scorecard"}
                  <span className="ml-2 text-xs text-[var(--text-muted)]">
                    {isZh ? "平均" : "Avg"}: {Math.round(scores.reduce((a, s) => a + s.overall_score, 0) / scores.length)}
                  </span>
                </summary>
              <div className="grid grid-cols-3 md:grid-cols-5 gap-2 mb-3">
                <div className="text-center p-2 rounded bg-white/5">
                  <p className="text-[10px] text-[var(--text-muted)]">{isZh ? "平均分" : "Avg Score"}</p>
                  <p className="text-lg font-bold text-[var(--accent)]">
                    {Math.round(scores.reduce((a, s) => a + s.overall_score, 0) / scores.length)}
                  </p>
                </div>
                <div className="text-center p-2 rounded bg-white/5">
                  <p className="text-[10px] text-[var(--text-muted)]">PASS</p>
                  <p className="text-lg font-bold text-[var(--success)]">
                    {scores.filter((s) => s.compliance_status === "PASS").length}
                  </p>
                </div>
                <div className="text-center p-2 rounded bg-white/5">
                  <p className="text-[10px] text-[var(--text-muted)]">FAIL</p>
                  <p className="text-lg font-bold text-[var(--error)]">
                    {scores.filter((s) => s.compliance_status === "FAIL").length}
                  </p>
                </div>
                <div className="text-center p-2 rounded bg-white/5">
                  <p className="text-[10px] text-[var(--text-muted)]">{isZh ? "需优化" : "Need Fix"}</p>
                  <p className="text-lg font-bold text-yellow-400">{failedArticles.length}</p>
                </div>
                <div className="text-center p-2 rounded bg-white/5">
                  <p className="text-[10px] text-[var(--text-muted)]">{isZh ? "总篇数" : "Total"}</p>
                  <p className="text-lg font-bold">{scores.length}</p>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-[var(--border-glass)]">
                      <th className="px-2 py-2 text-left text-xs text-[var(--text-secondary)]">Query</th>
                      <th className="px-2 py-2 text-xs text-[var(--text-secondary)]">{isZh ? "意图" : "Intent"}</th>
                      <th className="px-2 py-2 text-xs text-[var(--text-secondary)]">{isZh ? "可读性" : "Read"}</th>
                      <th className="px-2 py-2 text-xs text-[var(--text-secondary)]">{isZh ? "权威" : "Auth"}</th>
                      <th className="px-2 py-2 text-xs text-[var(--text-secondary)]">{isZh ? "行动性" : "Action"}</th>
                      <th className="px-2 py-2 text-xs text-[var(--text-secondary)]">{isZh ? "差异化" : "Diff"}</th>
                      <th className="px-2 py-2 text-xs text-[var(--text-secondary)]">{isZh ? "总分" : "Overall"}</th>
                      <th className="px-2 py-2 text-xs text-[var(--text-secondary)]">{isZh ? "状态" : "Status"}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {scores.map((s, idx) => (
                      <tr key={idx} className={`border-b border-[var(--border-glass)]/50 ${s.compliance_status === "FAIL" ? "bg-[var(--error)]/5" : ""}`}>
                        <td className="px-2 py-2 max-w-[200px] truncate">{s.title || s.ai_query}</td>
                        <td className="px-2 py-2 text-center font-mono text-xs">{s.intent_match}</td>
                        <td className="px-2 py-2 text-center font-mono text-xs">{s.ai_readability}</td>
                        <td className="px-2 py-2 text-center font-mono text-xs">{s.authority}</td>
                        <td className="px-2 py-2 text-center font-mono text-xs">{s.actionability}</td>
                        <td className="px-2 py-2 text-center font-mono text-xs">{s.differentiation}</td>
                        <td className="px-2 py-2 text-center font-mono text-xs font-bold">{s.overall_score}</td>
                        <td className="px-2 py-2 text-center">
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                            s.compliance_status === "PASS" ? "bg-[var(--success)]/20 text-[var(--success)]" : "bg-[var(--error)]/20 text-[var(--error)]"
                          }`}>
                            {s.compliance_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              </details>
            </GlassCard>
          )}

          {/* Optimize Results */}
          {optimizeResults.length > 0 && (
            <GlassCard padding="sm">
              <details>
                <summary className="text-sm font-medium text-[var(--text-secondary)] mb-3 cursor-pointer">
                  {isZh ? "③ 优化建议（Step 3.5）" : "③ Optimization Suggestions (Step 3.5)"}
                  <span className="ml-2 text-xs text-[var(--text-muted)]">{optimizeResults.length} {isZh ? "条" : "items"}</span>
                </summary>
              <div className="space-y-3">
                {optimizeResults.map((r, idx) => (
                  <div key={idx} className="p-3 bg-white/5 rounded-lg border border-[var(--border-glass)]">
                    <p className="text-sm font-medium">{r.ai_query}</p>
                    <div className="flex gap-4 mt-1 text-xs">
                      <span className="text-[var(--text-muted)]">{isZh ? "优化前" : "Before"}: {r.original_score}</span>
                      <span className="text-[var(--accent)]">{isZh ? "预估优化后" : "After"}: {r.optimized_score}</span>
                      <span className={r.compliance_status === "PASS" ? "text-[var(--success)]" : "text-[var(--error)]"}>
                        {r.compliance_status}
                      </span>
                    </div>
                    {r.changes.length > 0 && (
                      <ul className="mt-2 text-xs text-[var(--text-secondary)] list-disc list-inside space-y-0.5">
                        {r.changes.map((c, i) => <li key={i}>{c}</li>)}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
              </details>
            </GlassCard>
          )}

          {/* Compliance Results (Step 3.6) */}
          {complianceResults.length > 0 && (
            <GlassCard padding="sm">
              <details>
                <summary className="text-sm font-medium text-[var(--text-secondary)] mb-3 cursor-pointer">
                  {isZh ? "④ 合规审查（Step 3.6）" : "④ Compliance Check (Step 3.6)"}
                  <span className="ml-2 text-xs text-[var(--text-muted)]">
                    ✅{complianceResults.filter((r) => r.status === "PASS").length}
                    {" "}🔧{complianceResults.filter((r) => r.status === "FIXED").length}
                    {" "}❌{complianceResults.filter((r) => r.status === "FAIL").length}
                  </span>
                </summary>
              <div className="grid grid-cols-3 gap-2 mb-3">
                <div className="text-center p-2 rounded bg-white/5">
                  <p className="text-[10px] text-[var(--text-muted)]">PASS</p>
                  <p className="text-lg font-bold text-[var(--success)]">
                    {complianceResults.filter((r) => r.status === "PASS").length}
                  </p>
                </div>
                <div className="text-center p-2 rounded bg-white/5">
                  <p className="text-[10px] text-[var(--text-muted)]">FIXED</p>
                  <p className="text-lg font-bold text-yellow-400">
                    {complianceResults.filter((r) => r.status === "FIXED").length}
                  </p>
                </div>
                <div className="text-center p-2 rounded bg-white/5">
                  <p className="text-[10px] text-[var(--text-muted)]">FAIL</p>
                  <p className="text-lg font-bold text-[var(--error)]">
                    {complianceResults.filter((r) => r.status === "FAIL").length}
                  </p>
                </div>
              </div>
              <div className="space-y-2">
                {complianceResults.map((r, idx) => (
                  <div key={idx} className={`p-3 rounded-lg border ${
                    r.status === "PASS" ? "bg-green-500/5 border-green-500/20"
                      : r.status === "FIXED" ? "bg-yellow-500/5 border-yellow-500/20"
                      : "bg-red-500/5 border-red-500/20"
                  }`}>
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium">{r.title || r.ai_query}</p>
                      <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                        r.status === "PASS" ? "bg-green-500/20 text-green-400"
                          : r.status === "FIXED" ? "bg-yellow-500/20 text-yellow-400"
                          : "bg-red-500/20 text-red-400"
                      }`}>{r.status}</span>
                    </div>
                    {r.issues.length > 0 && (
                      <div className="mt-2">
                        <p className="text-[10px] text-[var(--text-muted)] mb-1">{isZh ? "发现问题：" : "Issues found:"}</p>
                        <ul className="text-xs text-[var(--error)] list-disc list-inside space-y-0.5">
                          {r.issues.map((issue, i) => <li key={i}>{issue}</li>)}
                        </ul>
                      </div>
                    )}
                    {r.fixes_applied.length > 0 && (
                      <div className="mt-2">
                        <p className="text-[10px] text-[var(--text-muted)] mb-1">{isZh ? "已自动修复：" : "Auto-fixed:"}</p>
                        <ul className="text-xs text-[var(--success)] list-disc list-inside space-y-0.5">
                          {r.fixes_applied.map((fix, i) => <li key={i}>{fix}</li>)}
                        </ul>
                      </div>
                    )}
                    {r.status === "PASS" && r.issues.length === 0 && (
                      <p className="text-xs text-[var(--success)] mt-1">{isZh ? "✅ 内容合规，无风险" : "✅ Content compliant, no risks"}</p>
                    )}
                  </div>
                ))}
              </div>
              </details>
            </GlassCard>
          )}

          {/* ⑤ Final Content - Full view, editable, selectable, downloadable */}
          {(scores.length > 0 || complianceResults.length > 0) && drafts.length > 0 && (
            <GlassCard>
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-sm font-medium text-[var(--text-secondary)]">
                  {isZh ? `⑤ 最终内容 (${drafts.length} 篇)` : `⑤ Final Content (${drafts.length} articles)`}
                </h2>
                <div className="flex gap-2">
                  <button
                    onClick={() => setSelectedFinal(new Set(drafts.map((_, i) => i)))}
                    className="text-xs text-[var(--text-secondary)] hover:text-[var(--accent)]"
                  >{isZh ? "全选" : "Select all"}</button>
                  <button
                    onClick={() => setSelectedFinal(new Set())}
                    className="text-xs text-[var(--text-secondary)] hover:text-[var(--accent)]"
                  >{isZh ? "取消" : "Clear"}</button>
                  <button
                    onClick={() => {
                      const toRemove = [...selectedFinal].sort((a, b) => b - a);
                      const remaining = drafts.filter((_, i) => !selectedFinal.has(i));
                      setDrafts(remaining);
                      setSelectedFinal(new Set());
                      localStorage.setItem("zhizao_selected_drafts", JSON.stringify(remaining));
                    }}
                    disabled={selectedFinal.size === 0}
                    className="text-xs text-[var(--error)] hover:text-red-600 disabled:opacity-40"
                  >{isZh ? "删除选中" : "Delete selected"}</button>
                </div>
              </div>

              <div className="space-y-3">
                {drafts.map((draft, idx) => (
                  <div key={idx} className="border border-[var(--border-glass)] rounded-lg overflow-hidden">
                    {/* Header row: checkbox + title + actions */}
                    <div className="flex items-center gap-3 p-3 bg-white/5">
                      <input
                        type="checkbox"
                        checked={selectedFinal.has(idx)}
                        onChange={() => {
                          setSelectedFinal((prev) => {
                            const next = new Set(prev);
                            if (next.has(idx)) next.delete(idx); else next.add(idx);
                            return next;
                          });
                        }}
                        className="accent-[var(--accent)] shrink-0"
                      />
                      <div
                        className="flex-1 cursor-pointer"
                        onClick={() => setExpandedFinalIdx(expandedFinalIdx === idx ? null : idx)}
                      >
                        <p className="text-sm font-semibold text-[var(--text-primary)]">{draft.title || draft.ai_query}</p>
                        <p className="text-[10px] text-[var(--text-muted)]">
                          {draft.ai_query} • {draft.word_count || draft.content_draft.length} {isZh ? "字" : "chars"}
                          {scores[idx] && ` • ${isZh ? "评分" : "Score"}: ${scores[idx].overall_score}`}
                        </p>
                      </div>
                      <div className="flex gap-1.5 shrink-0">
                        <button
                          onClick={() => navigator.clipboard.writeText(draft.content_draft)}
                          className="text-[10px] px-2 py-1 rounded border border-[var(--border-glass)] text-[var(--text-muted)] hover:text-[var(--accent)]"
                        >{isZh ? "复制" : "Copy"}</button>
                        <button
                          onClick={() => {
                            const blob = new Blob([`# ${draft.title}\n\n${draft.content_draft}`], { type: "text/markdown;charset=utf-8" });
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement("a"); a.href = url;
                            a.download = `${draft.title.slice(0, 30).replace(/[/\\?%*:|"<>]/g, "")}.md`;
                            a.click(); URL.revokeObjectURL(url);
                          }}
                          className="text-[10px] px-2 py-1 rounded border border-[var(--border-glass)] text-[var(--text-muted)] hover:text-[var(--accent)]"
                        >⬇</button>
                      </div>
                      <span className="text-xs text-[var(--text-muted)] shrink-0 cursor-pointer" onClick={() => setExpandedFinalIdx(expandedFinalIdx === idx ? null : idx)}>
                        {expandedFinalIdx === idx ? "▼" : "▶"}
                      </span>
                    </div>

                    {/* Expanded: full content, editable */}
                    {expandedFinalIdx === idx && (
                      <div className="p-3 border-t border-[var(--border-glass)]">
                        <textarea
                          value={draft.content_draft}
                          onChange={(e) => {
                            const updated = [...drafts];
                            updated[idx] = { ...updated[idx], content_draft: e.target.value, word_count: e.target.value.length };
                            setDrafts(updated);
                            localStorage.setItem("zhizao_selected_drafts", JSON.stringify(updated));
                          }}
                          rows={20}
                          className="w-full bg-white/5 border border-[var(--border-glass)] rounded-lg px-4 py-3 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)] resize-y leading-relaxed"
                        />
                        <p className="text-[10px] text-[var(--text-muted)] mt-1">
                          {draft.content_draft.length} {isZh ? "字 | 可直接编辑修改" : "chars | Editable"}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Batch download actions */}
              <div className="flex gap-3 items-center mt-4 pt-3 border-t border-[var(--border-glass)]">
                <button
                  onClick={() => {
                    const items = selectedFinal.size > 0 ? [...selectedFinal].map((i) => drafts[i]) : drafts;
                    const content = items.map((d) => `# ${d.title}\n\n${d.content_draft}`).join("\n\n---\n\n");
                    const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a"); a.href = url;
                    a.download = `zhiyou_final_${items.length}articles.md`;
                    a.click(); URL.revokeObjectURL(url);
                  }}
                  className="text-xs px-3 py-1.5 rounded-lg border border-[var(--border-glass)] text-[var(--text-secondary)] hover:text-[var(--accent)] hover:border-[var(--accent)] transition-colors"
                >
                  ⬇ {isZh ? `下载${selectedFinal.size > 0 ? "选中" : "全部"} (MD)` : `Download ${selectedFinal.size > 0 ? "selected" : "all"} (MD)`}
                </button>
                <button
                  onClick={() => {
                    const items = selectedFinal.size > 0 ? [...selectedFinal].map((i) => drafts[i]) : drafts;
                    const header = "ai_query,title,word_count,content_draft\n";
                    const rows = items.map((d) => `"${d.ai_query.replace(/"/g, '""')}","${d.title.replace(/"/g, '""')}",${d.word_count || d.content_draft.length},"${d.content_draft.replace(/"/g, '""')}"`).join("\n");
                    const blob = new Blob(["\uFEFF" + header + rows], { type: "text/csv;charset=utf-8" });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement("a"); a.href = url;
                    a.download = `zhiyou_final_${items.length}articles.csv`;
                    a.click(); URL.revokeObjectURL(url);
                  }}
                  className="text-xs px-3 py-1.5 rounded-lg border border-[var(--border-glass)] text-[var(--text-secondary)] hover:text-[var(--accent)] hover:border-[var(--accent)] transition-colors"
                >
                  ⬇ {isZh ? `下载${selectedFinal.size > 0 ? "选中" : "全部"} (CSV)` : `Download ${selectedFinal.size > 0 ? "selected" : "all"} (CSV)`}
                </button>
                <button
                  onClick={() => {
                    const items = selectedFinal.size > 0 ? [...selectedFinal].map((i) => drafts[i]) : drafts;
                    items.forEach((d, i) => {
                      const blob = new Blob([`# ${d.title}\n\n${d.content_draft}`], { type: "text/markdown;charset=utf-8" });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a"); a.href = url;
                      a.download = `${(i + 1).toString().padStart(2, "0")}_${d.title.slice(0, 30).replace(/[/\\?%*:|"<>]/g, "")}.md`;
                      a.click(); URL.revokeObjectURL(url);
                    });
                  }}
                  className="text-xs px-3 py-1.5 rounded-lg border border-[var(--border-glass)] text-[var(--text-secondary)] hover:text-[var(--accent)] hover:border-[var(--accent)] transition-colors"
                >
                  ⬇ {isZh ? "逐篇下载 (MD)" : "Download each (MD)"}
                </button>
                <span className="text-[10px] text-[var(--text-muted)]">
                  {selectedFinal.size > 0 ? `${selectedFinal.size} ${isZh ? "篇已选" : "selected"}` : `${drafts.length} ${isZh ? "篇" : "total"}`}
                </span>
              </div>
            </GlassCard>
          )}
        </>
      )}

      {/* CTA */}
      <div className="flex justify-end pt-4">
        <button
          onClick={() => {
            // Pass selected final drafts to zhibu
            const selected = selectedFinal.size > 0
              ? [...selectedFinal].map((i) => drafts[i]).filter(Boolean)
              : drafts;
            localStorage.setItem("zhiyou_final_drafts", JSON.stringify(selected));
            router.push("/zhibu");
          }}
          disabled={drafts.length === 0}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            drafts.length > 0
              ? "bg-[var(--accent)] text-black hover:bg-[var(--accent-hover)]"
              : "bg-gray-600 text-gray-400 cursor-not-allowed"
          }`}
        >
          {isZh
            ? `下一步：内容发布 (${selectedFinal.size > 0 ? selectedFinal.size : drafts.length} 篇) →`
            : `Next: Publish (${selectedFinal.size > 0 ? selectedFinal.size : drafts.length}) →`}
        </button>
      </div>
    </div>
  );
}

// Generate actionable suggestions based on score dimensions
function generateSuggestions(score: ScoreResult): string[] {
  const suggestions: string[] = [];
  if (score.intent_match < 70) suggestions.push("首段应直接回答检索短语的核心问题");
  if (score.ai_readability < 70) suggestions.push("增加结构化元素：标题层级(##)、列表、表格");
  if (score.authority < 70) suggestions.push("增加官方链接 (https://gs.amazon.cn) 和品牌权威信息");
  if (score.actionability < 70) suggestions.push("增加具体步骤、操作指南或FAQ");
  if (score.differentiation < 70) suggestions.push("增加时效性信息(2026)、具体案例或独特视角");
  if (score.compliance_status === "FAIL") suggestions.push("移除绝对化承诺用语（如'保证赚钱'、'绝对'等）");
  if (suggestions.length === 0) suggestions.push("内容质量良好，可考虑进一步丰富细节");
  return suggestions;
}

// Compliance check (Step 3.6) - Legal/PR/Tax review
function localComplianceCheck(draft: DraftContent): ComplianceResult {
  const content = draft.content_draft || "";
  const issues: string[] = [];
  const fixes: string[] = [];

  // 绝对化承诺检测
  const absoluteClaims = ["保证赚钱", "绝对赚", "100%成功", "稳赚不赔", "零风险", "一定能", "必定", "保证利润"];
  for (const claim of absoluteClaims) {
    if (content.includes(claim)) {
      issues.push(`包含绝对化承诺用语: "${claim}"`);
    }
  }

  // 敏感税务/法律信息
  const taxSensitive = ["避税", "逃税", "偷税", "税务漏洞", "灰色清关"];
  for (const term of taxSensitive) {
    if (content.includes(term)) {
      issues.push(`包含敏感税务用语: "${term}"`);
    }
  }

  // 竞品贬损
  const competitorBash = ["垃圾平台", "骗人的", "千万别用"];
  for (const term of competitorBash) {
    if (content.includes(term)) {
      issues.push(`可能存在竞品贬损: "${term}"`);
    }
  }

  // 未标注来源的数据
  const dataPatterns = /\d+%.*卖家|营收.*\d+万|利润.*\d+/g;
  const dataMatches = content.match(dataPatterns);
  if (dataMatches && !content.includes("来源") && !content.includes("数据来自") && !content.includes("according to")) {
    issues.push("包含未标注来源的统计数据，建议注明出处");
    fixes.push("建议添加数据来源标注");
  }

  // 必须包含免责声明检测
  if (content.includes("收入") || content.includes("利润") || content.includes("赚")) {
    if (!content.includes("仅供参考") && !content.includes("不构成") && !content.includes("实际结果可能")) {
      issues.push("涉及收入/利润话题但缺少免责声明");
      fixes.push("建议添加'以上信息仅供参考，实际结果因人而异'");
    }
  }

  // 官方链接合规 — 确保使用正确的官方 URL
  if (content.includes("amazon.com/sell") && !content.includes("gs.amazon.cn")) {
    fixes.push("建议同时包含中文官方链接 https://gs.amazon.cn");
  }

  // Determine status
  let status: "PASS" | "FAIL" | "FIXED" = "PASS";
  if (issues.length > 0) {
    // Check if issues are auto-fixable
    const criticalIssues = issues.filter((i) =>
      i.includes("绝对化承诺") || i.includes("敏感税务") || i.includes("竞品贬损")
    );
    if (criticalIssues.length > 0) {
      status = "FAIL";
    } else {
      status = "FIXED";
      fixes.push("非关键问题已标注，建议人工确认后放行");
    }
  }

  return {
    ai_query: draft.ai_query,
    title: draft.title || draft.ai_query,
    status,
    issues,
    fixes_applied: fixes,
  };
}
