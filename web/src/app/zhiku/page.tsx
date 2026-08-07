"use client";

import { useState } from "react";
import { Search, Sparkles, Upload, CheckCircle2, ArrowRight } from "lucide-react";

export default function ZhikuPage() {
  const [seedWord, setSeedWord] = useState("");
  const [count, setCount] = useState(15);
  const [phrases, setPhrases] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedCount, setSelectedCount] = useState(0);

  const handleExpand = async () => {
    if (!seedWord.trim()) return;
    setLoading(true);
    try {
      const res = await fetch("/api/zhiku/expand", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ seed_word: seedWord, count, language: "zh-CN" }),
      });
      const data = await res.json();
      if (data.success) {
        // Reload phrases
        loadPhrases();
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const loadPhrases = async () => {
    try {
      const res = await fetch("/api/zhiku/phrases?batch_id=batch_001");
      const data = await res.json();
      setPhrases(data.phrases || []);
      setSelectedCount(data.phrases?.filter((p: any) => p.is_selected === "TRUE").length || 0);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="p-8 max-w-6xl">
      {/* Page Header */}
      <div className="mb-8">
        <div className="tag-orange mb-3">检索短语发现</div>
        <h1 className="text-2xl font-bold text-text-primary mb-2">
          智库 — AI 检索短语裂变
        </h1>
        <p className="text-text-secondary text-sm">
          输入核心词根，AI 自动裂变为用户在 ChatGPT/DeepSeek/豆包等搜索引擎中真实输入的检索短语
        </p>
      </div>

      {/* Pipeline Progress */}
      <div className="flex items-center gap-2 mb-8 p-4 bg-gray-50 rounded-card">
        <StepDot active label="智库" />
        <ArrowRight size={14} className="text-gray-300" />
        <StepDot label="智测" />
        <ArrowRight size={14} className="text-gray-300" />
        <StepDot label="智造" />
        <ArrowRight size={14} className="text-gray-300" />
        <StepDot label="智优" />
        <ArrowRight size={14} className="text-gray-300" />
        <StepDot label="智布" />
      </div>

      {/* Main Content: Two columns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Input */}
        <div className="lg:col-span-1">
          <div className="card p-6 space-y-5">
            <h2 className="font-semibold text-base flex items-center gap-2">
              <Sparkles size={18} className="text-amazon-orange" />
              核心词裂变
            </h2>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1.5">
                词根
              </label>
              <input
                type="text"
                value={seedWord}
                onChange={(e) => setSeedWord(e.target.value)}
                placeholder="例如：亚马逊FBA、跨境电商选品"
                className="w-full px-4 py-2.5 border border-border-light rounded-button text-sm focus:outline-none focus:ring-2 focus:ring-amazon-orange/20 focus:border-amazon-orange transition-all"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-1.5">
                裂变数量: {count}
              </label>
              <input
                type="range"
                min={5}
                max={30}
                value={count}
                onChange={(e) => setCount(Number(e.target.value))}
                className="w-full accent-amazon-orange"
              />
              <div className="flex justify-between text-xs text-text-muted mt-1">
                <span>5</span>
                <span>30</span>
              </div>
            </div>

            <button
              onClick={handleExpand}
              disabled={loading || !seedWord.trim()}
              className="btn-primary w-full justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="animate-pulse">裂变中...</span>
              ) : (
                <>
                  <Sparkles size={16} />
                  开始裂变
                </>
              )}
            </button>
          </div>

          {/* Quick Stats */}
          <div className="card p-5 mt-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-text-muted text-xs">总短语数</p>
                <p className="text-xl font-bold text-text-primary">{phrases.length}</p>
              </div>
              <div>
                <p className="text-text-muted text-xs">已选中</p>
                <p className="text-xl font-bold text-amazon-orange">{selectedCount}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Phrase List */}
        <div className="lg:col-span-2">
          <div className="card">
            {/* Header */}
            <div className="px-6 py-4 border-b border-border-light flex items-center justify-between">
              <h2 className="font-semibold text-sm">当前检索短语库</h2>
              <div className="flex gap-2">
                <button className="btn-secondary text-xs py-1.5 px-3">
                  全选
                </button>
                <button className="btn-secondary text-xs py-1.5 px-3">
                  💾 保存
                </button>
              </div>
            </div>

            {/* Phrase Table */}
            <div className="divide-y divide-border-light max-h-[600px] overflow-y-auto">
              {phrases.length === 0 ? (
                <div className="p-12 text-center">
                  <Search size={48} className="mx-auto text-gray-200 mb-4" />
                  <p className="text-text-secondary text-sm">还没有检索短语</p>
                  <p className="text-text-muted text-xs mt-1">输入词根点击"开始裂变"生成</p>
                </div>
              ) : (
                phrases.map((phrase, idx) => (
                  <PhraseRow key={idx} phrase={phrase} index={idx} />
                ))
              )}
            </div>
          </div>

          {/* CTA */}
          {selectedCount > 0 && (
            <div className="mt-4 p-4 bg-amazon-orange/5 border border-amazon-orange/20 rounded-card flex items-center justify-between">
              <p className="text-sm font-medium">
                已选中 <span className="text-amazon-orange font-bold">{selectedCount}</span> 条短语
              </p>
              <button className="btn-primary">
                下一步：智测验证
                <ArrowRight size={16} />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function StepDot({ active, label }: { active?: boolean; label: string }) {
  return (
    <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium ${
      active ? "bg-amazon-orange text-white" : "bg-gray-100 text-text-muted"
    }`}>
      {active && <CheckCircle2 size={12} />}
      {label}
    </div>
  );
}

function PhraseRow({ phrase, index }: { phrase: any; index: number }) {
  const isSelected = phrase.is_selected === "TRUE";
  return (
    <div className={`px-6 py-3 flex items-center gap-4 hover:bg-gray-50 transition-colors ${
      isSelected ? "bg-amazon-orange/5" : ""
    }`}>
      <input
        type="checkbox"
        checked={isSelected}
        className="w-4 h-4 accent-amazon-orange rounded"
        readOnly
      />
      <div className="flex-1 min-w-0">
        <p className="text-sm text-text-primary truncate">{phrase.ai_query}</p>
      </div>
      <span className="tag-blue text-xs">{phrase.source || "seed"}</span>
      <span className="text-xs text-text-muted w-8 text-center">
        {phrase.accuracy_score || "—"}
      </span>
    </div>
  );
}
