"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { useI18nStore } from "@/stores/i18n-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { ApiError } from "@/lib/types";

const ALLOWED_USERS = [
  "fanting", "czhaamzn", "yuchy", "porzh", "linzhshi",
  "fenixau", "tianranh", "qiudanie", "quadaisy", "budhiraja",
  "mbudhira", "xinyill", "xdhuang", "gracezjy", "htp",
  "jinghuaf", "mxyzhang", "emilwliu", "qdhwzj", "panjf",
  "rickylan", "yountlim", "phunghd", "oanhhtk",
];

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuthStore();
  const { setLocale } = useI18nStore();
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showApply, setShowApply] = useState(false);
  const [applyName, setApplyName] = useState("");
  const [applySuccess, setApplySuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username) return;

    setLoading(true);
    setError(null);

    try {
      const res = await login(username);
      if (res.allowed) {
        const { regionConfig } = useAuthStore.getState();
        if (regionConfig?.ui_language) {
          setLocale(regionConfig.ui_language as "en" | "zh-CN" | "zh-TW" | "ko" | "vi");
        }
        router.replace("/overview");
      } else {
        setError("Access Denied / \u8BBF\u95EE\u88AB\u62D2\u7EDD");
      }
    } catch (err) {
      const apiErr = err as ApiError;
      if (apiErr.isTimeout) {
        setError("Connection timed out / \u8FDE\u63A5\u8D85\u65F6");
      } else {
        setError("Connection error / \u8FDE\u63A5\u9519\u8BEF");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[var(--bg-surface)]">
      <GlassCard className="w-full max-w-md" padding="lg">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-[var(--accent)] mb-2">
            Smart Suite
          </h1>
          <p className="text-sm text-[var(--text-secondary)]">
            AI-native marketing platform
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="username"
              className="block text-sm text-[var(--text-secondary)] mb-1.5"
            >
              Login Name
            </label>
            <select
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border border-[var(--border-card)] rounded-lg px-4 py-2.5 text-[var(--text-primary)] bg-white focus:outline-none focus:border-[var(--accent)] transition-colors"
            >
              <option value="">-- Select your login name --</option>
              {ALLOWED_USERS.map((u) => (
                <option key={u} value={u}>{u}</option>
              ))}
            </select>
          </div>

          {error && (
            <div className="text-sm text-[var(--error)] bg-red-50 rounded-lg px-3 py-2" role="alert">
              {error}
            </div>
          )}

          <Button
            type="submit"
            className="w-full"
            size="lg"
            loading={loading}
            disabled={!username}
          >
            Login
          </Button>
        </form>

        {/* Apply for access */}
        <div className="mt-6 pt-4 border-t border-[var(--border-card)]">
          {!showApply ? (
            <button
              onClick={() => setShowApply(true)}
              className="w-full text-sm text-[var(--text-muted)] hover:text-[var(--accent)] transition-colors"
            >
              No access? Apply here / \u6CA1\u6709\u8D26\u53F7\uFF1F\u7533\u8BF7\u6743\u9650
            </button>
          ) : applySuccess ? (
            <p className="text-sm text-[var(--success)] text-center">
              {"\u2705"} Application submitted. Admin will review. / \u7533\u8BF7\u5DF2\u63D0\u4EA4\uFF0C\u7B49\u5F85\u7BA1\u7406\u5458\u5BA1\u6838\u3002
            </p>
          ) : (
            <div className="space-y-3">
              <p className="text-xs text-[var(--text-muted)]">
                Enter your desired login name / \u8F93\u5165\u60F3\u7533\u8BF7\u7684\u767B\u5F55\u540D
              </p>
              <input
                type="text"
                value={applyName}
                onChange={(e) => setApplyName(e.target.value)}
                placeholder="your-login-name"
                className="w-full border border-[var(--border-card)] rounded-lg px-4 py-2 text-sm text-[var(--text-primary)] bg-white focus:outline-none focus:border-[var(--accent)]"
              />
              <Button
                onClick={() => {
                  if (applyName.trim()) setApplySuccess(true);
                }}
                disabled={!applyName.trim()}
                variant="secondary"
                className="w-full"
              >
                {"\u{1F4E8}"} Apply for Access / \u7533\u8BF7\u6743\u9650
              </Button>
            </div>
          )}
        </div>
      </GlassCard>
    </div>
  );
}
