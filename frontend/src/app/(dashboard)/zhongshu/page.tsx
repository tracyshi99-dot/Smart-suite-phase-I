"use client";

import { useEffect, useState } from "react";
import { useI18nStore } from "@/stores/i18n-store";
import { useBatchStore } from "@/stores/batch-store";
import { usePipelineStore } from "@/stores/pipeline-store";
import { useAuthStore } from "@/stores/auth-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { BatchSelector } from "@/components/ui/BatchSelector";
import { PipelineFlow } from "@/components/layout/PipelineFlow";
import { Button } from "@/components/ui/Button";
import { apiGet } from "@/lib/api-client";
import { PhraseListResponse } from "@/lib/types";

export default function ZhongshuPage() {
  const { t, locale } = useI18nStore();
  const { activeBatch } = useBatchStore();
  const { status, fetchStatus } = usePipelineStore();
  const { isAdmin, user } = useAuthStore();
  const isZh = locale.startsWith("zh");

  const [activeTab, setActiveTab] = useState<"pipeline" | "decision" | "settings">("pipeline");
  const [batchStats, setBatchStats] = useState({ phrases: 0, selected: 0, articles: 0 });

  useEffect(() => {
    fetchStatus(activeBatch);
  }, [activeBatch, fetchStatus]);

  // Load batch stats
  useEffect(() => {
    async function loadStats() {
      try {
        const res = await apiGet<PhraseListResponse>("/api/zhiku/phrases", {
          batch_id: activeBatch,
          user: user ?? "",
        });
        const selected = res.phrases.filter((p) => p.is_selected === "TRUE").length;
        setBatchStats({ phrases: res.total, selected, articles: 0 });
      } catch {
        // ignore
      }
    }
    loadStats();
  }, [activeBatch, user]);

  const steps = status[activeBatch] ?? [
    { id: "01_zhiku", label: "智库", status: "pending" as const },
    { id: "02_zhizao", label: "智造", status: "pending" as const },
    { id: "03_zhiyou", label: "智优", status: "pending" as const },
    { id: "04_zhibu", label: "智布", status: "pending" as const },
  ];

  const completedSteps = steps.filter((s) => s.status === "complete").length;

  const tabs = [
    { id: "pipeline" as const, label: isZh ? "管线状态" : "Pipeline" },
    { id: "decision" as const, label: isZh ? "决策引擎" : "Decision Engine" },
    { id: "settings" as const, label: isZh ? "系统设置" : "Settings" },
  ];

  return (
    <div className="space-y-6 max-w-[1400px]">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{t("zhongshu.title")}</h1>
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

      {/* Pipeline Tab */}
      {activeTab === "pipeline" && (
        <>
          {/* Pipeline Flow */}
          <GlassCard>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-medium text-[var(--text-secondary)]">
                {isZh ? "管线进度" : "Pipeline Progress"}
              </h2>
              <span className="text-xs text-[var(--accent)]">{completedSteps}/4 steps</span>
            </div>
            <PipelineFlow steps={steps} />
          </GlassCard>

          {/* Batch Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {steps.map((step) => (
              <GlassCard key={step.id} padding="sm" glow={step.status === "active"}>
                <p className="text-xs text-[var(--text-secondary)]">{step.label}</p>
                <p className="text-lg font-bold mt-1">
                  {step.status === "complete" ? (
                    <span className="text-[var(--success)]">✓</span>
                  ) : step.status === "active" ? (
                    <span className="text-[var(--accent)]">●</span>
                  ) : (
                    <span className="text-[var(--text-muted)]">○</span>
                  )}
                </p>
                {step.fileCount !== undefined && (
                  <p className="text-xs text-[var(--text-muted)] mt-1">{step.fileCount} files</p>
                )}
              </GlassCard>
            ))}
          </div>

          {/* Batch Summary */}
          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
              {isZh ? "批次概览" : "Batch Summary"} — {activeBatch}
            </h2>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-xs text-[var(--text-muted)]">{isZh ? "总短语" : "Total Phrases"}</p>
                <p className="text-xl font-bold text-[var(--accent)]">{batchStats.phrases}</p>
              </div>
              <div>
                <p className="text-xs text-[var(--text-muted)]">{isZh ? "已选中" : "Selected"}</p>
                <p className="text-xl font-bold text-[var(--success)]">{batchStats.selected}</p>
              </div>
              <div>
                <p className="text-xs text-[var(--text-muted)]">{isZh ? "已生成内容" : "Articles"}</p>
                <p className="text-xl font-bold">{batchStats.articles}</p>
              </div>
            </div>
          </GlassCard>
        </>
      )}

      {/* Decision Engine Tab */}
      {activeTab === "decision" && (
        <>
          {/* 7 Decision Rules */}
          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-4">
              {isZh ? "7 条决策规则" : "7 Decision Rules"}
            </h2>
            <div className="space-y-3">
              {[
                { emoji: "🟢", name: isZh ? "Rule 1: 增长加速" : "Rule 1: Growth Acceleration", trigger: isZh ? "渠道 WoW > +30% 连续 2 周" : "Channel WoW > +30% for 2+ weeks", action: isZh ? "智库 +5 词，智造优先生产，智布加速发布" : "Zhiku +5 keywords, Zhizao priority, Zhibu accelerate" },
                { emoji: "🔴", name: isZh ? "Rule 2: 下降预警" : "Rule 2: Decline Alert", trigger: isZh ? "渠道 WoW < -20%" : "Channel WoW < -20%", action: isZh ? "暂停生产，智测重跑，智析归因分析" : "Pause production, re-run Zhice, attribution analysis" },
                { emoji: "🟡", name: isZh ? "Rule 3: 低量高增" : "Rule 3: Low Volume, High Growth", trigger: isZh ? "GEO weekly < 50 且 YoY > +50%" : "GEO weekly < 50 AND YoY > +50%", action: isZh ? "智库扩词 +10，智预推演，目标 4 周破 100" : "Expand +10 phrases, forecast, target 100 in 4 weeks" },
                { emoji: "🟢", name: isZh ? "Rule 4: 高增站点扩张" : "Rule 4: Site Expansion", trigger: isZh ? "站点 YoY > +100%" : "Site YoY > +100%", action: isZh ? "该站点关键词占比 30%+，集中资源" : "Allocate 30%+ keywords to that site" },
                { emoji: "🟡", name: isZh ? "Rule 5: 内容缺口" : "Rule 5: Content Gap", trigger: isZh ? "有流量但 2 周无新内容" : "Traffic exists but no content in 2 weeks", action: isZh ? "诊断瓶颈，重启全流程，48h 首发" : "Diagnose bottleneck, restart pipeline, 48h deadline" },
                { emoji: "🔴", name: isZh ? "Rule 6: 大盘对标" : "Rule 6: Benchmark", trigger: isZh ? "Our YoY < SSR YoY 连续 2 周" : "Our YoY < SSR YoY for 2+ weeks", action: isZh ? "BPS 分析，策略复盘，新方向建议" : "BPS analysis, strategy review, new direction" },
                { emoji: "🟡", name: isZh ? "Rule 7: 投入产出滞后" : "Rule 7: Input-Output Lag", trigger: isZh ? "发布 2-3 周后无 GEO/Direct 提升" : "No GEO/Direct lift 2-3 weeks after publish", action: isZh ? "智测验证→智优重写或调整发布平台" : "Zhice verify → Zhiyou rewrite or adjust platform" },
              ].map((rule) => (
                <div key={rule.name} className="flex items-start gap-3 p-3 rounded-lg bg-white/5 border border-[var(--border-glass)]/30">
                  <span className="text-lg">{rule.emoji}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-[var(--text-primary)]">{rule.name}</p>
                    <p className="text-xs text-[var(--text-muted)] mt-1"><span className="font-medium">{isZh ? "触发:" : "Trigger:"}</span> {rule.trigger}</p>
                    <p className="text-xs text-[var(--text-secondary)] mt-0.5"><span className="font-medium">{isZh ? "动作:" : "Action:"}</span> {rule.action}</p>
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>

          {/* Pipeline Flow Diagram */}
          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
              {isZh ? "全流程编排" : "Pipeline Orchestration"}
            </h2>
            <div className="text-xs font-mono text-[var(--text-secondary)] bg-black/20 rounded-lg p-4 overflow-x-auto whitespace-pre">
{`智中枢决策(WK计划)
    ↓
1. 智库 → 生成/扩展检索短语
    ↓
2. 智测 → 验证 AI 平台覆盖
    ↓
3. 智造 → 针对 Gap 生产内容
    ↓
4. 智优 → 评分 + 重写 + 合规
    ↓
5. 智布 → JSON 格式化 + 发布
    ↓
6. 智析 → 追踪效果 (2-3周)
    ↓
7. 智中枢 → 下一周决策 (闭环)

并行: 智预(预测) → 智库
      智传(分发) ← 智布`}
            </div>
          </GlassCard>

          {/* Execution Principles */}
          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
              {isZh ? "执行原则" : "Execution Principles"}
            </h2>
            <div className="space-y-2 text-xs text-[var(--text-secondary)]">
              <p>1. <span className="font-medium text-[var(--text-primary)]">{isZh ? "数据驱动" : "Data-driven"}</span> — {isZh ? "所有决策基于智析数据，不靠直觉" : "All decisions based on ZhiXi data"}</p>
              <p>2. <span className="font-medium text-[var(--text-primary)]">{isZh ? "闭环验证" : "Closed-loop"}</span> — {isZh ? "每个动作都有可衡量的结果指标" : "Every action has measurable outcomes"}</p>
              <p>3. <span className="font-medium text-[var(--text-primary)]">{isZh ? "优先级排序" : "Prioritized"}</span> — {isZh ? "CRITICAL > HIGH > MEDIUM > LOW" : "CRITICAL > HIGH > MEDIUM > LOW"}</p>
              <p>4. <span className="font-medium text-[var(--text-primary)]">{isZh ? "止损机制" : "Stop-loss"}</span> — {isZh ? "Rule 2 触发时立即暂停，不盲目投入" : "Pause immediately when Rule 2 triggers"}</p>
              <p>5. <span className="font-medium text-[var(--text-primary)]">{isZh ? "滞后容忍" : "Lag tolerance"}</span> — {isZh ? "内容→被引用通常滞后 2-3 周，Rule 7 不过早触发" : "Content→citation typically lags 2-3 weeks"}</p>
            </div>
          </GlassCard>

          {/* BPS Tracking */}
          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
              {isZh ? "BPS 大盘对标" : "BPS Benchmark Tracking"}
            </h2>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-xs text-[var(--text-muted)]">{isZh ? "我方 YTD YoY" : "Our YTD YoY"}</p>
                <p className="text-xl font-bold text-[var(--success)]">+55%</p>
              </div>
              <div>
                <p className="text-xs text-[var(--text-muted)]">{isZh ? "SSR 大盘 YoY" : "SSR Benchmark YoY"}</p>
                <p className="text-xl font-bold text-[var(--error)]">-23%</p>
              </div>
              <div>
                <p className="text-xs text-[var(--text-muted)]">BPS</p>
                <p className="text-xl font-bold text-[var(--accent)]">+7,800</p>
              </div>
            </div>
            <p className="text-xs text-[var(--text-muted)] mt-3 text-center">
              {isZh ? "公式: (Our YoY% - SSR YoY%) × 100 | 警戒线: 周度 BPS < 0 连续 2 周" : "Formula: (Our YoY% - SSR YoY%) × 100 | Alert: Weekly BPS < 0 for 2+ weeks"}
            </p>
          </GlassCard>
        </>
      )}

      {/* Settings Tab */}
      {activeTab === "settings" && (
        <>
          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-4">
              {isZh ? "区域配置" : "Region Configuration"}
            </h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-xs text-[var(--text-muted)]">{isZh ? "当前用户" : "Current User"}</p>
                <p className="text-[var(--text-primary)] font-medium">{user}</p>
              </div>
              <div>
                <p className="text-xs text-[var(--text-muted)]">{isZh ? "权限" : "Role"}</p>
                <p className="text-[var(--text-primary)] font-medium">
                  {isAdmin ? (isZh ? "管理员" : "Admin") : (isZh ? "用户" : "User")}
                </p>
              </div>
              <div>
                <p className="text-xs text-[var(--text-muted)]">{isZh ? "活跃批次" : "Active Batch"}</p>
                <p className="text-[var(--accent)] font-medium">{activeBatch}</p>
              </div>
              <div>
                <p className="text-xs text-[var(--text-muted)]">{isZh ? "界面语言" : "UI Language"}</p>
                <p className="text-[var(--text-primary)] font-medium">{locale}</p>
              </div>
            </div>
          </GlassCard>

          <GlassCard>
            <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-4">
              {isZh ? "系统信息" : "System Info"}
            </h2>
            <div className="space-y-2 text-xs text-[var(--text-muted)]">
              <p>• Frontend: Next.js 16.3 + React 19 + Zustand + Recharts</p>
              <p>• Backend: FastAPI + Mangum (Lambda)</p>
              <p>• API: {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}</p>
              <p>• Deploy: Vercel (Frontend) + AWS Lambda (API)</p>
            </div>
          </GlassCard>

          {isAdmin && (
            <GlassCard>
              <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-4">
                {isZh ? "管理员操作" : "Admin Actions"}
              </h2>
              <div className="space-y-3">
                <Button onClick={() => window.open("https://smartsuite-geo.vercel.app", "_blank")}>
                  {isZh ? "打开 Vercel 面板" : "Open Vercel Dashboard"}
                </Button>
                <p className="text-xs text-[var(--text-muted)]">
                  {isZh
                    ? "用户管理、批次管理等高级功能请使用 Streamlit 版本或直接编辑 users.json"
                    : "User management and advanced features available in Streamlit or via users.json"
                  }
                </p>
              </div>
            </GlassCard>
          )}
        </>
      )}
    </div>
  );
}
