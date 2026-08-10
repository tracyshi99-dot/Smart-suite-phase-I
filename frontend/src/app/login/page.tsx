"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { useI18nStore } from "@/stores/i18n-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { ApiError } from "@/lib/types";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuthStore();
  const { setLocale } = useI18nStore();
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await login(username.trim());
      if (res.allowed) {
        // Set locale from region config
        const { regionConfig } = useAuthStore.getState();
        if (regionConfig?.ui_language) {
          setLocale(regionConfig.ui_language as "en" | "zh-CN" | "zh-TW" | "ko" | "vi");
        }
        router.replace("/overview");
      } else {
        setError("访问被拒绝 / Access Denied");
      }
    } catch (err) {
      const apiErr = err as ApiError;
      if (apiErr.isTimeout) {
        setError("连接超时 / Connection timed out");
      } else {
        setError("连接错误 / Connection error");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <GlassCard className="w-full max-w-md" padding="lg">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-[var(--accent)] mb-2">
            Smart Suite
          </h1>
          <p className="text-sm text-[var(--text-secondary)]">
            GEO Content Intelligence Platform
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="username"
              className="block text-sm text-[var(--text-secondary)] mb-1.5"
            >
              用户名 / Username
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              className="w-full bg-white/5 border border-[var(--border-glass)] rounded-lg px-4 py-2.5 text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)] transition-colors"
              autoFocus
              autoComplete="username"
            />
          </div>

          {error && (
            <div className="text-sm text-[var(--error)] bg-[var(--error)]/10 rounded-lg px-3 py-2" role="alert">
              {error}
            </div>
          )}

          <Button
            type="submit"
            className="w-full"
            size="lg"
            loading={loading}
            disabled={!username.trim()}
          >
            登录 / Login
          </Button>
        </form>
      </GlassCard>
    </div>
  );
}
