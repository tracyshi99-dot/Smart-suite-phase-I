"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useAuthStore } from "@/stores/auth-store";
import { useBatchStore } from "@/stores/batch-store";
import { useI18nStore } from "@/stores/i18n-store";
import { Button } from "@/components/ui/Button";
import { ChatMessage } from "@/lib/types";
import { apiStream } from "@/lib/api-client";
import { uid } from "@/lib/utils";

const MAX_MESSAGES = 100; // 50 pairs
const MAX_INPUT_LENGTH = 2000;

export function ChatPanel() {
  const { user } = useAuthStore();
  const { activeBatch } = useBatchStore();
  const { t } = useI18nStore();

  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = useCallback(async () => {
    if (!input.trim() || streaming) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: input.trim(),
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev.slice(-MAX_MESSAGES + 1), userMessage]);
    setInput("");
    setError(null);
    setStreaming(true);

    // Start assistant message
    const assistantId = uid();
    const assistantMessage: ChatMessage = {
      role: "assistant",
      content: "",
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, assistantMessage]);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "https://asq6n6kw78.execute-api.us-east-1.amazonaws.com"}/api/chat/stream`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: userMessage.content,
            user: user ?? "",
            batch_id: activeBatch,
            history: messages.slice(-10).map((m) => ({
              role: m.role,
              content: m.content,
            })),
          }),
        }
      );

      if (!response.ok) throw new Error("API error");
      const data = await response.json();
      // Handle both direct object and string-encoded JSON
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
      setError("连接中断，请重试 / Connection interrupted");
      // Keep the partial message if any
    } finally {
      setStreaming(false);
    }
  }, [input, streaming, user, activeBatch, messages]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleRetry = () => {
    if (messages.length >= 2) {
      // Remove last assistant message and resend
      const lastUserMsg = [...messages].reverse().find((m) => m.role === "user");
      if (lastUserMsg) {
        setMessages((prev) => prev.slice(0, -1)); // Remove failed assistant msg
        setInput(lastUserMsg.content);
      }
    }
    setError(null);
  };

  return (
    <>
      {/* Toggle Button - moved up to not block input */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          fixed bottom-20 right-6 z-50 w-12 h-12 rounded-full
          flex items-center justify-center text-xl
          transition-all duration-200 shadow-lg
          ${isOpen
            ? "bg-white border border-[var(--border-card)] text-[var(--text-secondary)]"
            : "bg-[var(--accent)] text-white shadow-lg"
          }
        `}
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        {isOpen ? "✕" : "💬"}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div className="fixed top-0 right-0 h-full w-[400px] max-w-[90vw] z-40 bg-white border-l border-[var(--border-card)] flex flex-col shadow-2xl">
          {/* Header */}
          <div className="px-4 py-3 border-b border-[var(--border-card)] flex items-center justify-between">
            <div>
              <h2 className="text-sm font-medium text-[var(--text-primary)]">Agent Chat</h2>
              <p className="text-xs text-[var(--text-muted)]">
                Batch: {activeBatch}
              </p>
            </div>
            <button
              onClick={() => setMessages([])}
              className="text-xs text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors"
              aria-label="Clear chat"
            >
              Clear
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3">
            {messages.length === 0 && (
              <div className="text-center py-12 text-[var(--text-muted)] text-sm">
                <p>👋 Ask me anything about Smart Suite</p>
                <p className="mt-2 text-xs">
                  I can expand phrases, run tests, generate content, and more.
                </p>
              </div>
            )}
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`
                    max-w-[85%] px-3 py-2 rounded-lg text-sm whitespace-pre-wrap
                    ${msg.role === "user"
                      ? "bg-[var(--accent)]/15 text-[var(--text-primary)] rounded-br-sm"
                      : "bg-[var(--bg-surface)] text-[var(--text-secondary)] rounded-bl-sm border border-[var(--border-card)]"
                    }
                  `}
                >
                  {msg.content || (streaming && idx === messages.length - 1 ? "..." : "")}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Error */}
          {error && (
            <div className="px-4 py-2 bg-[var(--error)]/10 border-t border-[var(--error)]/20">
              <div className="flex items-center justify-between">
                <p className="text-xs text-[var(--error)]">{error}</p>
                <button
                  onClick={handleRetry}
                  className="text-xs text-[var(--accent)] hover:underline"
                >
                  {t("common.retry")}
                </button>
              </div>
            </div>
          )}

          {/* Input */}
          <div className="px-4 py-3 border-t border-[var(--border-card)]">
            <div className="flex gap-2">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value.slice(0, MAX_INPUT_LENGTH))}
                onKeyDown={handleKeyDown}
                placeholder="Type a message... (Enter to send)"
                rows={2}
                className="flex-1 bg-[var(--bg-surface)] border border-[var(--border-card)] rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)] resize-none"
                disabled={streaming}
              />
              <Button
                onClick={handleSend}
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
