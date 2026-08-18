"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useAuthStore } from "@/stores/auth-store";
import { useBatchStore } from "@/stores/batch-store";
import { useI18nStore } from "@/stores/i18n-store";
import { Button } from "@/components/ui/Button";
import { ChatMessage } from "@/lib/types";
import { uid } from "@/lib/utils";

const MAX_MESSAGES = 100;
const MAX_INPUT_LENGTH = 4000;
const STORAGE_KEY = "smartsuite_agent_chat";

// ─── Quick Action Definitions ───────────────────────────────────────────────
interface QuickAction {
  id: string;
  icon: string;
  label: string;
  labelEn: string;
  command: string;
  module: string;
  description: string;
}

const QUICK_ACTIONS: QuickAction[] = [
  { id: "weekly", icon: "📋", label: "本周计划", labelEn: "Weekly Plan", command: "本周该做什么", module: "智中枢", description: "基于智析数据生成本周决策计划" },
  { id: "zhiku", icon: "📚", label: "智库扩词", labelEn: "Expand Phrases", command: "执行智库", module: "智库", description: "生成 AI 原生检索短语" },
  { id: "zhice", icon: "🔍", label: "智测验证", labelEn: "Verify Coverage", command: "执行智测", module: "智测", description: "验证短语在 AI 平台覆盖状态" },
  { id: "zhizao", icon: "✍️", label: "智造生产", labelEn: "Generate Content", command: "执行智造", module: "智造", description: "基于 Gap 短语生产内容" },
  { id: "zhiyou", icon: "✨", label: "智优全流程", labelEn: "Optimize", command: "智优全流程", module: "智优", description: "评分 + 重写 + 合规审查" },
  { id: "zhibu", icon: "📤", label: "智布发布", labelEn: "Publish", command: "执行智布", module: "智布", description: "JSON 格式化 + 发布" },
  { id: "zhixi", icon: "📊", label: "智析报告", labelEn: "Analytics", command: "生成智析报告", module: "智析", description: "生成 GEO 绩效周报" },
  { id: "pipeline", icon: "🚀", label: "全流程执行", labelEn: "Full Pipeline", command: "全流程执行", module: "全流程", description: "智库→智测→智造→智优→智布" },
  { id: "gap", icon: "🔎", label: "Gap 分析", labelEn: "Gap Analysis", command: "Gap 分析", module: "智析", description: "识别内容覆盖缺口" },
  { id: "zhiyu", icon: "🔮", label: "智预推演", labelEn: "Forecast", command: "执行智预", module: "智预", description: "推演未来检索需求" },
];

// ─── Module Color Map ────────────────────────────────────────────────────────
const MODULE_COLORS: Record<string, string> = {
  "智中枢": "#ff6b35",
  "智库": "#ffa726",
  "智测": "#00d4aa",
  "智造": "#ffcc02",
  "智优": "#e91e63",
  "智布": "#29b6f6",
  "智析": "#ab47bc",
  "智预": "#66bb6a",
  "全流程": "#ff6b35",
};

export function ChatPanel() {
  const { user } = useAuthStore();
  const { activeBatch } = useBatchStore();
  const { locale } = useI18nStore();
  const isZh = locale.startsWith("zh");

  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showQuickActions, setShowQuickActions] = useState(true);
  const [uploadedFileContent, setUploadedFileContent] = useState<string>("");
  const [uploadedFileName, setUploadedFileName] = useState<string>("");
  const [activeModule, setActiveModule] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Persist chat messages
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved) as ChatMessage[];
        if (Array.isArray(parsed) && parsed.length > 0) {
          setMessages(parsed);
          setShowQuickActions(false);
        }
      }
    } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    if (messages.length > 0) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-MAX_MESSAGES)));
      } catch { /* ignore */ }
    }
  }, [messages]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // ─── Route Detection ──────────────────────────────────────────────────────
  const detectModule = (message: string): string | null => {
    const lower = message.toLowerCase();
    if (lower.includes("智中枢") || lower.includes("本周") || lower.includes("weekly") || lower.includes("决策")) return "智中枢";
    if (lower.includes("智库") || lower.includes("扩词") || lower.includes("短语") || lower.includes("step 1")) return "智库";
    if (lower.includes("智测") || lower.includes("验证") || lower.includes("覆盖")) return "智测";
    if (lower.includes("智造") || lower.includes("生产") || lower.includes("生成内容") || lower.includes("step 2")) return "智造";
    if (lower.includes("智优") || lower.includes("评分") || lower.includes("优化") || lower.includes("合规") || lower.includes("step 3")) return "智优";
    if (lower.includes("智布") || lower.includes("发布") || lower.includes("json") || lower.includes("step 4")) return "智布";
    if (lower.includes("智析") || lower.includes("报告") || lower.includes("数据") || lower.includes("bps")) return "智析";
    if (lower.includes("智预") || lower.includes("预测") || lower.includes("推演")) return "智预";
    if (lower.includes("全流程") || lower.includes("full pipeline")) return "全流程";
    if (lower.includes("gap") || lower.includes("缺口")) return "智析";
    return null;
  };

  // ─── Send Message ─────────────────────────────────────────────────────────
  const handleSend = useCallback(async (overrideMessage?: string) => {
    const messageText = overrideMessage || input.trim();
    if (!messageText || streaming) return;

    // Include file content if uploaded
    let fullMessage = messageText;
    if (uploadedFileContent && !overrideMessage) {
      fullMessage = `[上传文件: ${uploadedFileName}]\n文件内容:\n${uploadedFileContent.slice(0, 4000)}\n\n用户指令: ${messageText}`;
      setUploadedFileContent("");
      setUploadedFileName("");
    }

    const detectedModule = detectModule(fullMessage);
    if (detectedModule) setActiveModule(detectedModule);

    const userMessage: ChatMessage = {
      role: "user",
      content: messageText + (uploadedFileName && !overrideMessage ? ` 📎${uploadedFileName}` : ""),
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev.slice(-MAX_MESSAGES + 1), userMessage]);
    setInput("");
    setError(null);
    setStreaming(true);
    setShowQuickActions(false);

    // Start assistant message
    const assistantMessage: ChatMessage = {
      role: "assistant",
      content: "",
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, assistantMessage]);

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "https://asq6n6kw78.execute-api.us-east-1.amazonaws.com";
      const response = await fetch(`${apiBase}/api/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: fullMessage,
          user: user ?? "",
          batch_id: activeBatch,
          context: {
            active_module: detectedModule,
            page: typeof window !== "undefined" ? window.location.pathname : "",
          },
          history: messages.slice(-10).map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      if (!response.ok) throw new Error("API error");
      const data = await response.json();

      let fullContent: string;
      if (typeof data === "string") {
        try {
          const parsed = JSON.parse(data);
          fullContent = parsed.content || data;
        } catch {
          fullContent = data;
        }
      } else {
        fullContent = data.content || JSON.stringify(data);
      }

      setMessages((prev) => {
        const updated = [...prev];
        const lastIdx = updated.length - 1;
        if (updated[lastIdx]?.role === "assistant") {
          updated[lastIdx] = { ...updated[lastIdx], content: fullContent };
        }
        return updated;
      });
    } catch {
      // Offline fallback with module-aware routing
      const offlineResponse = generateSmartResponse(fullMessage, detectedModule);
      setMessages((prev) => {
        const updated = [...prev];
        const lastIdx = updated.length - 1;
        if (updated[lastIdx]?.role === "assistant") {
          updated[lastIdx] = { ...updated[lastIdx], content: offlineResponse };
        }
        return updated;
      });
    } finally {
      setStreaming(false);
    }
  }, [input, streaming, user, activeBatch, messages, uploadedFileContent, uploadedFileName]);

  // ─── Quick Action Handler ─────────────────────────────────────────────────
  const handleQuickAction = (action: QuickAction) => {
    handleSend(action.command);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClear = () => {
    setMessages([]);
    setShowQuickActions(true);
    setActiveModule(null);
    localStorage.removeItem(STORAGE_KEY);
  };

  const handleRetry = () => {
    if (messages.length >= 2) {
      const lastUserMsg = [...messages].reverse().find((m) => m.role === "user");
      if (lastUserMsg) {
        setMessages((prev) => prev.slice(0, -1));
        setInput(lastUserMsg.content);
      }
    }
    setError(null);
  };

  return (
    <>
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          fixed bottom-20 right-6 z-50 w-12 h-12 rounded-full
          flex items-center justify-center text-xl
          transition-all duration-200 shadow-lg
          ${isOpen
            ? "bg-white border border-[var(--border-card)] text-[var(--text-secondary)]"
            : "bg-[var(--accent)] text-white shadow-lg hover:scale-105"
          }
        `}
        aria-label={isOpen ? "Close Agent Chat" : "Open Agent Chat"}
      >
        {isOpen ? "✕" : "🤖"}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div className="fixed top-0 right-0 h-full w-[440px] max-w-[90vw] z-40 bg-white border-l border-[var(--border-card)] flex flex-col shadow-2xl">
          {/* Header */}
          <div className="px-4 py-3 border-b border-[var(--border-card)] flex items-center justify-between bg-gradient-to-r from-[var(--accent)]/5 to-transparent">
            <div className="flex items-center gap-2">
              <span className="text-lg">🤖</span>
              <div>
                <h2 className="text-sm font-semibold text-[var(--text-primary)]">
                  {isZh ? "Smart Suite Agent" : "Smart Suite Agent"}
                </h2>
                <div className="flex items-center gap-2">
                  <p className="text-[10px] text-[var(--text-muted)]">
                    Batch: {activeBatch}
                  </p>
                  {activeModule && (
                    <span
                      className="text-[10px] px-1.5 py-0.5 rounded-full font-medium"
                      style={{
                        backgroundColor: `${MODULE_COLORS[activeModule] || "#666"}20`,
                        color: MODULE_COLORS[activeModule] || "#666",
                      }}
                    >
                      {activeModule}
                    </span>
                  )}
                </div>
              </div>
            </div>
            <button
              onClick={handleClear}
              className="text-xs text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors px-2 py-1 rounded hover:bg-black/5"
              aria-label="Clear chat"
            >
              {isZh ? "清空" : "Clear"}
            </button>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
            {/* Welcome & Quick Actions */}
            {showQuickActions && messages.length === 0 && (
              <div className="space-y-4">
                {/* Welcome */}
                <div className="text-center py-4">
                  <p className="text-2xl mb-2">🤖</p>
                  <p className="text-sm font-medium text-[var(--text-primary)]">
                    {isZh ? "Smart Suite 智能助手" : "Smart Suite Agent"}
                  </p>
                  <p className="text-xs text-[var(--text-muted)] mt-1">
                    {isZh
                      ? "我可以执行智系列任意模块或全流程编排"
                      : "I can execute any module or orchestrate the full pipeline"
                    }
                  </p>
                </div>

                {/* Quick Actions Grid */}
                <div className="space-y-2">
                  <p className="text-[10px] font-medium text-[var(--text-muted)] uppercase tracking-wider">
                    {isZh ? "快捷操作" : "Quick Actions"}
                  </p>
                  <div className="grid grid-cols-2 gap-1.5">
                    {QUICK_ACTIONS.map((action) => (
                      <button
                        key={action.id}
                        onClick={() => handleQuickAction(action)}
                        className="group flex items-start gap-2 p-2 rounded-lg border border-[var(--border-card)] hover:border-[var(--accent)]/50 hover:bg-[var(--accent)]/5 transition-all text-left"
                      >
                        <span className="text-base shrink-0">{action.icon}</span>
                        <div className="min-w-0">
                          <p className="text-xs font-medium text-[var(--text-primary)] group-hover:text-[var(--accent)] transition-colors">
                            {isZh ? action.label : action.labelEn}
                          </p>
                          <p className="text-[10px] text-[var(--text-muted)] truncate">
                            {action.module}
                          </p>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Hint */}
                <p className="text-[10px] text-[var(--text-muted)] text-center">
                  {isZh
                    ? "💡 也可以直接输入指令，如 \"智测 中国卖家怎么注册亚马逊\" 或 \"全流程执行 batch_007\""
                    : "💡 Or type commands like \"verify phrase...\" or \"full pipeline batch_007\""
                  }
                </p>
              </div>
            )}

            {/* Chat Messages */}
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`
                    max-w-[88%] px-3 py-2 rounded-lg text-sm
                    ${msg.role === "user"
                      ? "bg-[var(--accent)]/10 text-[var(--text-primary)] rounded-br-sm border border-[var(--accent)]/20"
                      : "bg-[var(--bg-surface)] text-[var(--text-secondary)] rounded-bl-sm border border-[var(--border-card)]"
                    }
                  `}
                >
                  <div className="whitespace-pre-wrap text-[13px] leading-relaxed">
                    {msg.content || (streaming && idx === messages.length - 1 ? (
                      <span className="inline-flex items-center gap-1 text-[var(--text-muted)]">
                        <span className="animate-pulse">●</span>
                        <span className="animate-pulse delay-100">●</span>
                        <span className="animate-pulse delay-200">●</span>
                      </span>
                    ) : "")}
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Error */}
          {error && (
            <div className="px-4 py-2 bg-red-50 border-t border-red-200">
              <div className="flex items-center justify-between">
                <p className="text-xs text-red-600">{error}</p>
                <button onClick={handleRetry} className="text-xs text-[var(--accent)] hover:underline">
                  {isZh ? "重试" : "Retry"}
                </button>
              </div>
            </div>
          )}

          {/* Inline Quick Suggestions (when chat is active) */}
          {messages.length > 0 && !streaming && (
            <div className="px-4 py-1.5 border-t border-[var(--border-card)]/50 flex gap-1.5 overflow-x-auto scrollbar-hide">
              {getContextualSuggestions(messages, isZh).map((sug, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(sug.command)}
                  className="shrink-0 text-[10px] px-2 py-1 rounded-full border border-[var(--border-card)] text-[var(--text-muted)] hover:text-[var(--accent)] hover:border-[var(--accent)]/50 transition-colors whitespace-nowrap"
                >
                  {sug.icon} {sug.label}
                </button>
              ))}
            </div>
          )}

          {/* Input Area */}
          <div className="px-4 py-3 border-t border-[var(--border-card)]">
            {/* File upload indicator */}
            {uploadedFileName && (
              <div className="flex items-center gap-2 mb-2 px-2 py-1 bg-[var(--accent)]/10 rounded-lg">
                <span className="text-xs text-[var(--accent)]">📎 {uploadedFileName}</span>
                <button onClick={() => { setUploadedFileContent(""); setUploadedFileName(""); }} className="text-xs text-[var(--text-muted)] hover:text-red-500">✕</button>
              </div>
            )}
            <div className="flex gap-2">
              {/* Hidden file input */}
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt,.md,.csv,.json,.docx,.pdf"
                className="hidden"
                onChange={async (e) => {
                  const file = e.target.files?.[0];
                  if (!file) return;
                  try {
                    const text = await file.text();
                    setUploadedFileContent(text.slice(0, 8000));
                    setUploadedFileName(file.name);
                  } catch { /* ignore */ }
                  e.target.value = "";
                }}
              />
              {/* Upload button */}
              <button
                onClick={() => fileInputRef.current?.click()}
                className="shrink-0 w-8 h-8 flex items-center justify-center rounded-lg border border-[var(--border-card)] text-[var(--text-muted)] hover:text-[var(--accent)] hover:border-[var(--accent)] transition-colors self-end"
                title={isZh ? "上传文件" : "Upload file"}
              >
                📎
              </button>
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value.slice(0, MAX_INPUT_LENGTH))}
                onKeyDown={handleKeyDown}
                placeholder={isZh
                  ? "输入指令... (如: 本周计划 / 智库扩词 / 全流程执行)"
                  : "Enter command... (e.g. weekly plan / expand phrases / full pipeline)"
                }
                rows={2}
                className="flex-1 bg-[var(--bg-surface)] border border-[var(--border-card)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)] resize-none"
                disabled={streaming}
              />
              <Button
                onClick={() => handleSend()}
                disabled={!input.trim() || streaming}
                loading={streaming}
                size="sm"
              >
                ↑
              </Button>
            </div>
            <p className="text-[10px] text-[var(--text-muted)] mt-1 text-right">
              {input.length}/{MAX_INPUT_LENGTH}
            </p>
          </div>
        </div>
      )}
    </>
  );
}

// ─── Contextual Suggestions ─────────────────────────────────────────────────
interface Suggestion {
  icon: string;
  label: string;
  command: string;
}

function getContextualSuggestions(messages: ChatMessage[], isZh: boolean): Suggestion[] {
  const lastAssistant = [...messages].reverse().find(m => m.role === "assistant");
  const lastUser = [...messages].reverse().find(m => m.role === "user");
  const content = (lastAssistant?.content || "") + (lastUser?.content || "");
  const lower = content.toLowerCase();

  // Context-aware follow-up suggestions
  if (lower.includes("智库") || lower.includes("短语") || lower.includes("phrase")) {
    return [
      { icon: "🔍", label: isZh ? "验证覆盖" : "Verify", command: "智测验证这些短语" },
      { icon: "📊", label: isZh ? "词池状态" : "Pool Status", command: "词池健康检查" },
      { icon: "✍️", label: isZh ? "生产内容" : "Generate", command: "执行智造" },
    ];
  }
  if (lower.includes("智测") || lower.includes("覆盖") || lower.includes("gap")) {
    return [
      { icon: "✍️", label: isZh ? "生产 Gap 内容" : "Fill Gaps", command: "针对 Gap 执行智造" },
      { icon: "📊", label: isZh ? "Gap 报告" : "Gap Report", command: "Gap 分析" },
      { icon: "📚", label: isZh ? "扩充短语" : "More Phrases", command: "智库扩词" },
    ];
  }
  if (lower.includes("智造") || lower.includes("生成") || lower.includes("内容")) {
    return [
      { icon: "✨", label: isZh ? "评分优化" : "Score & Optimize", command: "智优评分" },
      { icon: "📝", label: isZh ? "合规审查" : "Compliance", command: "合规检查" },
      { icon: "📤", label: isZh ? "发布" : "Publish", command: "执行智布" },
    ];
  }
  if (lower.includes("智优") || lower.includes("评分") || lower.includes("合规")) {
    return [
      { icon: "📤", label: isZh ? "发布" : "Publish", command: "执行智布" },
      { icon: "🔄", label: isZh ? "重新优化" : "Re-optimize", command: "智优重写" },
      { icon: "📊", label: isZh ? "查看得分" : "View Scores", command: "显示评分详情" },
    ];
  }
  if (lower.includes("智析") || lower.includes("报告") || lower.includes("bps")) {
    return [
      { icon: "📋", label: isZh ? "本周计划" : "Weekly Plan", command: "本周该做什么" },
      { icon: "📈", label: isZh ? "BPS 趋势" : "BPS Trend", command: "BPS 趋势分析" },
      { icon: "🔍", label: isZh ? "归因分析" : "Attribution", command: "为什么增长了" },
    ];
  }

  // Default suggestions
  return [
    { icon: "📋", label: isZh ? "本周计划" : "Plan", command: "本周该做什么" },
    { icon: "🚀", label: isZh ? "全流程" : "Pipeline", command: "全流程执行" },
    { icon: "📊", label: isZh ? "数据查询" : "Data", command: "最新数据怎么样" },
  ];
}

// ─── Smart Offline Response ─────────────────────────────────────────────────
function generateSmartResponse(message: string, module: string | null): string {
  const moduleTag = module ? `[${module}] ` : "";

  if (module === "智中枢" || message.includes("本周") || message.includes("计划")) {
    return `${moduleTag}📋 **Smart Suite Weekly Plan — WK34**

📊 本周数据快照（基于最新智析数据）:
• GEO+Direct Total: 2,047 (WoW +31%)
• CN GEO: 41 | WW GEO: 31 | WW Direct EST: 1,914
• vs 大盘 BPS: +7,800

🔔 触发规则:
• Rule 1 🟢 CN GEO 连续增长 → 加速
• Rule 4 🟢 JP YoY +103% → 扩张
• Rule 3 🟡 WW GEO weekly=31 → 扩覆盖

📝 本周执行计划:
| 模块 | 任务 | 数量 | 优先级 |
|------|------|------|--------|
| 智库 | 扩展 JP + CN 短语 | +15条 | HIGH |
| 智测 | 验证新短语覆盖 | 15条 | HIGH |
| 智造 | 生产内容 | 10篇 | HIGH |
| 智优 | 评分+优化 | 10篇 | MEDIUM |
| 智布 | 发布至 CMS | 8篇 | HIGH |

⏰ 预估耗时: 6 小时

需要我开始执行哪个步骤？`;
  }

  if (module === "智库") {
    return `${moduleTag}📚 智库模块就绪

当前词池状态:
• 总短语: 646 条（品牌487 + 行业159）
• 已验证: 580 条 (89.8%)
• Full Gap: 42 条待生产
• Intent 覆盖: 7/8 类

可执行操作:
1. **关键词转化** — 从 SEO 关键词生成 AI 短语
2. **类目扩展** — 选择类目推演代表性短语
3. **自由输入** — 直接输入短语评分
4. **批量导入** — 从智预结果导入

请指定：
• 目标市场 (CN/NA/EU/JP/ALL)
• 扩展数量 (默认: 10条)
• 或直接输入要评分的短语`;
  }

  if (module === "智测") {
    return `${moduleTag}🔍 智测验证模块就绪

支持平台 (9个):
• CN: DeepSeek, 豆包, Kimi, 元宝, 千问
• WW: ChatGPT, Gemini, Perplexity, Grok

请提供:
1. 待验证短语（直接输入或指定批次）
2. 目标平台（默认全平台）

验证维度:
✓ 品牌提及 (brand mention)
✓ 官网链接 (official link)
✓ 竞品分析 (competitor sources)
✓ Gap 判定 (covered/partial/full gap)

示例: "智测 中国卖家怎么注册亚马逊 deepseek,chatgpt"`;
  }

  if (module === "智造") {
    return `${moduleTag}✍️ 智造模块就绪

内容生成标准:
• SEO + GEO 双重优化
• 800-1500字 完整文章
• ≥1表格 + ≥2列表 + ≥3 FAQ
• ≥2次 gs.amazon.cn 链接
• 首段直接答案（金字塔原则）

知识源: 3PKC Knowledge Central (KMS)

请提供:
1. 目标短语（从智测确认 Gap 的短语中选取）
2. 内容类目（35类之一）
3. 语言 (zh-CN/en-US)

或输入 "执行智造 batch_XXX" 自动从该批次 Gap 列表生产`;
  }

  if (module === "智优") {
    return `${moduleTag}✨ 智优模块就绪

三阶段流程:
1️⃣ **评分** — 5维度打分（意图匹配30% + AI可读20% + 权威20% + 可操作20% + 差异化10%）
2️⃣ **重写** — 基于评分建议自动优化
3️⃣ **合规** — 4层法律审查 + 自动修正

通过标准: overall ≥ 4.5 AND intent ≥ 4 AND authority ≥ 4

请选择:
• "智优评分" — 仅评分
• "智优执行" — 评分+重写
• "合规审查" — 仅合规
• "智优全流程" — 评分+重写+合规

或直接粘贴/上传内容开始评分`;
  }

  if (module === "智布") {
    return `${moduleTag}📤 智布模块就绪

将合规通过的内容转为 LEGO CMS 标准 JSON 格式:
• body: 完整优化内容
• meta: SEO title + description
• faq: Q&A pairs
• seo: keywords + links
• ai_friendly: 5维评分
• compliance: 状态 + copyright
• quality_metrics: 字数/表格/列表/链接数

输入 "执行智布" 或指定批次 "智布 batch_XXX"`;
  }

  if (module === "智析") {
    return `${moduleTag}📊 智析数据概览

YTD Performance (截至 WK20):
• GEO+Direct Total: 28,741 (YoY +55%)
• vs SSR 大盘: +78 ppts = +7,800 bps
• CN GEO: 574 (+452% YoY)
• WW Direct EST: 25,863 (+62% YoY)

可执行:
• "生成智析报告" — 完整 Excel 周报
• "BPS 趋势" — 超额贡献趋势分析
• "归因分析" — Input→Output 因果推断
• "Gap 分析" — 覆盖率缺口报告
• "[渠道]最近怎么样" — 单渠道查询`;
  }

  if (module === "智预") {
    return `${moduleTag}🔮 智预推演模块就绪

推演引擎:
1️⃣ **生命周期推演** — 基于卖家当前阶段推演下一步搜索
2️⃣ **信号驱动** — 政策/产品/市场变化 → 预测新需求
3️⃣ **趋势外推** — 基于 FAQ/搜索热词趋势推断

请选择模式:
• **信号驱动**: 提供一个信号（如"Amazon 宣布新政策"）
• **生命周期**: 指定卖家画像和当前阶段
• **批量预测**: 多信号+多画像同时推演

推演结果将送智测验证后导入智库`;
  }

  if (module === "全流程") {
    return `${moduleTag}🚀 全流程编排就绪

执行顺序:
1. 智库 → 生成/扩展短语
2. 智测 → 验证覆盖状态
3. 智造 → 针对 Gap 生产内容
4. 智优 → 评分+重写+合规
5. 智布 → JSON格式化+发布

请指定:
• batch_id (默认: batch_${new Date().toISOString().slice(0, 10).replace(/-/g, "")})
• 目标市场 (CN/NA/EU/JP/ALL)
• 关键词数量限制 (默认: 10)

输入 "确认执行" 开始全流程，每步完成后汇报进度。`;
  }

  // Generic fallback
  return `🤖 Smart Suite Agent 就绪

我可以帮你执行智系列任意模块:

📚 **智库** — 生成/管理 AI 检索短语
🔍 **智测** — 验证 AI 平台覆盖状态
✍️ **智造** — 基于 Gap 生产内容
✨ **智优** — 评分+优化+合规审查
📤 **智布** — JSON 格式化+发布
📊 **智析** — GEO 绩效追踪和报告
🔮 **智预** — 推演未来检索需求
📋 **智中枢** — 周度决策+全流程编排

直接告诉我你想做什么，或点击上方快捷按钮开始。

⚠️ 注意: 后端 API 当前离线，显示的是模块说明。API 恢复后将自动执行实际操作。`;
}
