"use client";

import { useState, useEffect } from "react";
import { useI18nStore } from "@/stores/i18n-store";
import { useAuthStore } from "@/stores/auth-store";
import { GlassCard } from "@/components/ui/GlassCard";

interface RequestSummary {
  tests: number;
  queries: number;
  opportunities: number;
  articles: number;
}

export default function RequestPage() {
  const { locale } = useI18nStore();
  const { user, isAdmin } = useAuthStore();
  const isZh = locale.startsWith("zh");

  const [summary, setSummary] = useState<RequestSummary>({
    tests: 0, queries: 0, opportunities: 0, articles: 0,
  });

  useEffect(() => {
    // In production this would call /api/requests/summary
    // For now show placeholder data
    setSummary({ tests: 3, queries: 45, opportunities: 12, articles: 8 });
  }, [user]);

  return (
    <div className="space-y-6 max-w-[1400px]">
      <h1 className="text-xl font-bold">
        {isZh ? "🔄 需求提交" : "🔄 Request Submission"}
      </h1>
      <p className="text-sm text-[var(--text-secondary)]">
        {isZh
          ? "测试 → 发现机会 → 内容生产 → 发布"
          : "Test → Discover Opportunities → Content Production → Publish"}
      </p>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <GlassCard padding="sm" className="text-center">
          <p className="text-xs text-[var(--text-muted)]">{isZh ? "测试次数" : "Tests"}</p>
          <p className="text-xl font-bold text-[var(--accent)]">{summary.tests}</p>
        </GlassCard>
        <GlassCard padding="sm" className="text-center">
          <p className="text-xs text-[var(--text-muted)]">{isZh ? "短语数" : "Queries"}</p>
          <p className="text-xl font-bold">{summary.queries}</p>
        </GlassCard>
        <GlassCard padding="sm" className="text-center">
          <p className="text-xs text-[var(--text-muted)]">{isZh ? "机会点" : "Opportunities"}</p>
          <p className="text-xl font-bold text-yellow-400">{summary.opportunities}</p>
        </GlassCard>
        <GlassCard padding="sm" className="text-center">
          <p className="text-xs text-[var(--text-muted)]">{isZh ? "已生成文章" : "Articles"}</p>
          <p className="text-xl font-bold text-[var(--success)]">{summary.articles}</p>
        </GlassCard>
      </div>

      {/* Quick Actions */}
      <GlassCard>
        <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-3">
          {isZh ? "工作流程" : "Workflow"}
        </h2>
        <div className="space-y-3 text-sm text-[var(--text-primary)]">
          <div className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-[var(--border-glass)]">
            <span className="text-lg">1️⃣</span>
            <div>
              <p className="font-medium">{isZh ? "在智库中选中检索短语" : "Select phrases in Knowledge Base"}</p>
              <p className="text-xs text-[var(--text-muted)]">{isZh ? "种子裂变 / 画像推演 / 手动上传" : "Seed expansion / Persona / Upload"}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-[var(--border-glass)]">
            <span className="text-lg">2️⃣</span>
            <div>
              <p className="font-medium">{isZh ? "在智测中验证 Gap" : "Verify gaps in Testing"}</p>
              <p className="text-xs text-[var(--text-muted)]">{isZh ? "多平台 AI 搜索验证" : "Multi-platform AI search verification"}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-[var(--border-glass)]">
            <span className="text-lg">3️⃣</span>
            <div>
              <p className="font-medium">{isZh ? "在智造中生成内容" : "Generate content in Production"}</p>
              <p className="text-xs text-[var(--text-muted)]">{isZh ? "GEO 优化的内容草稿" : "GEO-optimized content drafts"}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-lg bg-white/5 border border-[var(--border-glass)]">
            <span className="text-lg">4️⃣</span>
            <div>
              <p className="font-medium">{isZh ? "在智优中评分优化" : "Score and optimize"}</p>
              <p className="text-xs text-[var(--text-muted)]">{isZh ? "5 维度评分 + 自动优化" : "5-dimension scoring + auto-optimize"}</p>
            </div>
          </div>
        </div>
      </GlassCard>

      {isAdmin && (
        <GlassCard>
          <h2 className="text-sm font-medium text-[var(--text-secondary)] mb-2">
            {isZh ? "管理员视图" : "Admin View"}
          </h2>
          <p className="text-xs text-[var(--text-muted)]">
            {isZh
              ? "批量审批和发布功能将在后续版本中添加。目前请使用 Streamlit 版本进行审批操作。"
              : "Batch approval and publishing features coming soon. Use Streamlit version for now."}
          </p>
        </GlassCard>
      )}
    </div>
  );
}
