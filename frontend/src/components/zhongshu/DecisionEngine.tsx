"use client";

import { useState } from "react";
import { GlassCard } from "@/components/ui/GlassCard";

interface Task {
  id: string;
  module: string;
  description: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  rule: string;
  enabled: boolean;
  status: "pending" | "running" | "done" | "skipped";
  result?: string;
}

// Auto-generated tasks based on current ZhiXi data (Jun WK25)
const INITIAL_TASKS: Task[] = [
  { id: "t1", module: "智库", description: "新增入口/注册类高意图短语 ×50（7月重点）", priority: "HIGH", rule: "Rule 1", enabled: true, status: "pending" },
  { id: "t2", module: "智库", description: "扩展行业词 ×30（当前159→目标190）", priority: "HIGH", rule: "Rule 4", enabled: true, status: "pending" },
  { id: "t3", module: "智造", description: "生产入口注册类内容 ×10 篇", priority: "HIGH", rule: "Rule 1", enabled: true, status: "pending" },
  { id: "t4", module: "智造", description: "生产行业词内容 ×8 篇（提及率37.2%→目标45%）", priority: "HIGH", rule: "Rule 7", enabled: true, status: "pending" },
  { id: "t5", module: "智优", description: "审核全部18篇新内容（三段式优化）", priority: "MEDIUM", rule: "—", enabled: true, status: "pending" },
  { id: "t6", module: "智布", description: "发布已通过内容至 LEGO CMS", priority: "HIGH", rule: "—", enabled: true, status: "pending" },
  { id: "t7", module: "智测", description: "验证入口注册类新短语覆盖率", priority: "MEDIUM", rule: "Rule 5", enabled: true, status: "pending" },
  { id: "t8", module: "智测", description: "ChatGPT 链接提及率专项排查（当前28.5%，最低）", priority: "HIGH", rule: "Rule 7", enabled: true, status: "pending" },
  { id: "t9", module: "智析", description: "更新 Jul WK 数据，追踪品牌链接率恢复", priority: "LOW", rule: "—", enabled: true, status: "pending" },
  { id: "t10", module: "智预", description: "推演 Q3 旺季（Prime Day）相关检索需求", priority: "MEDIUM", rule: "Rule 4", enabled: false, status: "pending" },
];

export function DecisionEngine({ isZh }: { isZh: boolean }) {
  const [tasks, setTasks] = useState<Task[]>(INITIAL_TASKS);
  const [runningAll, setRunningAll] = useState(false);

  const toggleTask = (id: string) => {
    setTasks(prev => prev.map(t => t.id === id ? { ...t, enabled: !t.enabled } : t));
  };

  const runTask = async (id: string) => {
    setTasks(prev => prev.map(t => t.id === id ? { ...t, status: "running" } : t));
    // Simulate execution
    await new Promise(r => setTimeout(r, 1500 + Math.random() * 1000));
    setTasks(prev => prev.map(t => t.id === id ? { ...t, status: "done", result: isZh ? "✓ 已完成" : "✓ Done" } : t));
  };

  const runAll = async () => {
    setRunningAll(true);
    const enabledTasks = tasks.filter(t => t.enabled && t.status === "pending");
    for (const task of enabledTasks) {
      await runTask(task.id);
    }
    setRunningAll(false);
  };

  const resetAll = () => {
    setTasks(INITIAL_TASKS);
  };

  const enabledCount = tasks.filter(t => t.enabled).length;
  const doneCount = tasks.filter(t => t.status === "done").length;

  const priorityColor = (p: string) => p === "HIGH" ? "text-red-400" : p === "MEDIUM" ? "text-yellow-400" : "text-gray-400";
  const statusIcon = (s: string) => s === "done" ? "✅" : s === "running" ? "⏳" : s === "skipped" ? "⏭️" : "○";

  return (
    <>
      {/* Triggered Rules Summary */}
      <GlassCard>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-medium text-[var(--text-secondary)]">
            {isZh ? "📊 当前触发的规则（基于 Jun 智析数据）" : "📊 Triggered Rules (based on Jun ZhiXi data)"}
          </h2>
          <span className="text-xs px-2 py-0.5 rounded bg-[var(--accent)]/10 text-[var(--accent)]">WK30</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {[
            { emoji: "🟢", rule: "Rule 1", reason: isZh ? "CN GEO WoW +24%→+35% 连续增长" : "CN GEO WoW +24%→+35% consecutive growth", status: isZh ? "触发 → 加速" : "Triggered → Accelerate" },
            { emoji: "🟢", rule: "Rule 4", reason: isZh ? "JP Direct YoY +103%, CN GEO YoY +452%" : "JP Direct YoY +103%, CN GEO YoY +452%", status: isZh ? "触发 → 扩张" : "Triggered → Expand" },
            { emoji: "🟡", rule: "Rule 3", reason: isZh ? "WW GEO weekly=31, YoY +94%" : "WW GEO weekly=31, YoY +94%", status: isZh ? "触发 → 扩覆盖" : "Triggered → Expand coverage" },
            { emoji: "🟡", rule: "Rule 7", reason: isZh ? "ChatGPT 链接率28.5%（最低），行业词提及率仅37.2%" : "ChatGPT link rate 28.5% (lowest), industry rate 37.2%", status: isZh ? "触发 → 排查" : "Triggered → Investigate" },
          ].map((r) => (
            <div key={r.rule} className="flex items-center gap-2 p-2 rounded bg-white/5 border border-[var(--border-glass)]/20">
              <span>{r.emoji}</span>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium">{r.rule}: <span className="text-[var(--text-muted)]">{r.reason}</span></p>
                <p className="text-[10px] text-[var(--accent)]">{r.status}</p>
              </div>
            </div>
          ))}
          <div className="flex items-center gap-2 p-2 rounded bg-white/5 border border-green-500/20">
            <span>✅</span>
            <div className="flex-1">
              <p className="text-xs font-medium text-green-400">Rule 6: BPS +7,800 — {isZh ? "大幅跑赢大盘，无需触发" : "Well above benchmark, not triggered"}</p>
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Task List - Selectable & Executable */}
      <GlassCard>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-medium text-[var(--text-secondary)]">
            {isZh ? "📋 执行任务清单" : "📋 Execution Task List"} ({doneCount}/{enabledCount})
          </h2>
          <div className="flex gap-2">
            <button onClick={resetAll} className="px-2 py-1 text-xs rounded border border-[var(--border-glass)] text-[var(--text-muted)] hover:text-[var(--text-primary)]">
              {isZh ? "重置" : "Reset"}
            </button>
            <button onClick={runAll} disabled={runningAll} className="px-3 py-1 text-xs rounded bg-[var(--accent)] text-white font-medium disabled:opacity-50">
              {runningAll ? (isZh ? "执行中..." : "Running...") : (isZh ? "▶ 一键执行全部" : "▶ Run All")}
            </button>
          </div>
        </div>
        <div className="space-y-2">
          {tasks.map((task) => (
            <div key={task.id} className={`flex items-center gap-3 p-3 rounded-lg border transition-all ${task.status === "done" ? "bg-green-500/5 border-green-500/20" : task.status === "running" ? "bg-[var(--accent)]/5 border-[var(--accent)]/30 animate-pulse" : "bg-white/5 border-[var(--border-glass)]/30"}`}>
              <input type="checkbox" checked={task.enabled} onChange={() => toggleTask(task.id)} className="w-4 h-4 rounded accent-[var(--accent)]" disabled={task.status !== "pending"} />
              <span className="text-sm">{statusIcon(task.status)}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-xs px-1.5 py-0.5 rounded bg-[var(--accent)]/10 text-[var(--accent)] font-medium">{task.module}</span>
                  <span className={`text-[10px] font-medium ${priorityColor(task.priority)}`}>{task.priority}</span>
                  <span className="text-[10px] text-[var(--text-muted)]">{task.rule}</span>
                </div>
                <p className="text-xs text-[var(--text-primary)] mt-1">{task.description}</p>
                {task.result && <p className="text-[10px] text-green-400 mt-0.5">{task.result}</p>}
              </div>
              {task.enabled && task.status === "pending" && (
                <button onClick={() => runTask(task.id)} className="px-2 py-1 text-[10px] rounded border border-[var(--accent)]/30 text-[var(--accent)] hover:bg-[var(--accent)]/10">
                  {isZh ? "执行" : "Run"}
                </button>
              )}
            </div>
          ))}
        </div>
      </GlassCard>

      {/* 1-2 Week Plan */}
      <GlassCard>
        <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
          {isZh ? "📅 未来 1-2 周计划（基于智析 Jun 数据）" : "📅 1-2 Week Plan (based on ZhiXi Jun data)"}
        </h2>
        <div className="space-y-4">
          {/* Week 1 */}
          <div>
            <p className="text-xs font-bold text-[var(--accent)] mb-2">{isZh ? "▸ 第 1 周 (WK30-31)" : "▸ Week 1 (WK30-31)"}</p>
            <div className="space-y-1.5 pl-3 border-l-2 border-[var(--accent)]/30">
              <p className="text-xs">🎯 {isZh ? "重点: 入口/注册类内容集中发布（7月已新增50提示词）" : "Focus: Publish portal/registration content (50 new phrases added in Jul)"}</p>
              <p className="text-xs">📝 {isZh ? "智造: 10篇入口注册类 + 8篇行业词内容" : "Zhizao: 10 portal/reg articles + 8 industry articles"}</p>
              <p className="text-xs">🔍 {isZh ? "智测: ChatGPT 提及率专项优化（当前28.5% → 目标35%）" : "Zhice: ChatGPT rate optimization (28.5% → target 35%)"}</p>
              <p className="text-xs">📊 {isZh ? "KPI: 品牌链接率 > 58%, 行业链接率 > 40%" : "KPI: Brand link rate > 58%, Industry rate > 40%"}</p>
            </div>
          </div>
          {/* Week 2 */}
          <div>
            <p className="text-xs font-bold text-[var(--text-secondary)] mb-2">{isZh ? "▸ 第 2 周 (WK31-32)" : "▸ Week 2 (WK31-32)"}</p>
            <div className="space-y-1.5 pl-3 border-l-2 border-[var(--border-glass)]/30">
              <p className="text-xs">🎯 {isZh ? "重点: 注册类内容 RAG 指令测试定型 + 行业词内容追加" : "Focus: Registration RAG instruction finalization + more industry content"}</p>
              <p className="text-xs">📝 {isZh ? "智造: 注册类深度文章 ×5（RAG 模式）+ 行业词 ×10" : "Zhizao: 5 registration deep articles (RAG) + 10 industry"}</p>
              <p className="text-xs">🔍 {isZh ? "智测: 全平台覆盖验证（含 Kimi/千问/Gemini 新增平台）" : "Zhice: Full platform coverage test (incl. Kimi/Qianwen/Gemini)"}</p>
              <p className="text-xs">📊 {isZh ? "KPI: 总短语 → 700+, 行业词提及率 > 45%" : "KPI: Total phrases → 700+, Industry rate > 45%"}</p>
            </div>
          </div>
          {/* Key Insight */}
          <div className="p-3 rounded-lg bg-yellow-500/5 border border-yellow-500/20">
            <p className="text-xs font-medium text-yellow-400 mb-1">💡 {isZh ? "核心洞察" : "Key Insight"}</p>
            <p className="text-xs text-[var(--text-secondary)]">
              {isZh
                ? "7月行动逻辑: 5-6月集中优化行业词导致高意图词（入口/注册）产出减少 → Doubao 流量提及增但有效点击减 → 回调词池结构，强化入口/注册类高转化词"
                : "Jul logic: May-Jun industry keyword expansion reduced high-intent phrase output → Doubao mentions up but clicks down → Rebalance toward portal/registration high-conversion phrases"
              }
            </p>
          </div>
        </div>
      </GlassCard>

      {/* BPS Summary */}
      <GlassCard>
        <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
          {isZh ? "📈 BPS 大盘对标" : "📈 BPS Benchmark"}
        </h2>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-xs text-[var(--text-muted)]">{isZh ? "我方 YTD YoY" : "Our YTD YoY"}</p>
            <p className="text-xl font-bold text-[var(--success)]">+55%</p>
          </div>
          <div>
            <p className="text-xs text-[var(--text-muted)]">{isZh ? "SSR 大盘 YoY" : "SSR Benchmark"}</p>
            <p className="text-xl font-bold text-red-400">-23%</p>
          </div>
          <div>
            <p className="text-xs text-[var(--text-muted)]">BPS</p>
            <p className="text-xl font-bold text-[var(--accent)]">+7,800</p>
          </div>
        </div>
        <p className="text-[10px] text-[var(--text-muted)] mt-2 text-center">
          {isZh ? "跑赢大盘 78 ppts | 最保守口径（扣 CN Direct+SEO）仍跑赢 13 ppts" : "Outperforming benchmark by 78 ppts | Conservative estimate still +13 ppts"}
        </p>
      </GlassCard>
    </>
  );
}
