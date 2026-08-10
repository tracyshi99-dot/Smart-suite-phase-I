"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { useI18nStore } from "@/stores/i18n-store";
import { GlassCard } from "@/components/ui/GlassCard";
import { Button } from "@/components/ui/Button";
import { ApiError } from "@/lib/types";

const ALLOWED_USERS = [
  "htp", "shencm", "chienlin", "emilwliu", "gurusuh", "hangntt", "nijuno", "zhjiayue", "gracezjy", "jessyhan",
  "fengceci", "effiezhu", "jltian", "qdhwzj", "siyundai", "tzuchunf", "yudiwan",
  "ykimche", "liangles", "rickylan", "sylviayj",
  "cshumin", "xinyill", "kexuache", "yirua", "huiml", "xdhuang", "aizhen",
  "eunsong", "joouns", "yountlim",
  "hanhdo", "ntkgiang", "ttthong", "ducnghia", "oanhhtk", "phunghd",
  "akiyww", "elynj", "zhengyea", "ruoxhuan", "zuezhang",
  "hengshaz", "qiuwenhl", "lingkzho", "bcoliang", "tyagao", "ngwxuyen",
  "linzhshi", "luntian", "kouxo", "mxyzhang", "mingcaz", "shiyingp", "shuanyu", "gutingt", "robinyxy", "porzh", "miazhe",
  "oyingcl", "yanganny", "sdjessie", "jochuang", "keweidu", "lubyshaw", "xiaoldin", "czhaamzn", "fanting", "viviying", "wenliwu", "gwenying", "xuhengl", "yuchy", "zzjn",
  "llnamzn", "panjf", "ketng", "zhangzq", "vyuqwang",
  "jinghuaf", "jundingl", "yangqiay", "xisjiang", "shihanya", "xlvhui", "uhlingfe",
  "yurachel", "bozhuang", "zhanpinn", "xiyang", "fangweii", "sangxiao", "evacui", "patekliu", "atangamz", "yduamzn",
  "shenhon", "wangnli", "gaoqinfe", "zennying", "liuyixua",
  "daisiwei", "lynnzl", "miazihui", "nicosun",
  "renahh", "mengyazm", "syanzhou", "eliangsh", "zhuzinin",
  "fenixau", "yanyx", "jiayizh", "jiayuch", "jiayunjy", "juliezl", "llzha", "meilig", "tianranh", "yihuaz", "caxiaoto",
  "quadaisy", "mbudhira",
];

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuthStore();
  const { setLocale } = useI18nStore();
  const [username, setUsername] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
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
            <input
              id="username"
              type="text"
              list="user-list"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter or select your login name"
              className="w-full border border-[var(--border-card)] rounded-lg px-4 py-2.5 text-[var(--text-primary)] bg-white focus:outline-none focus:border-[var(--accent)] transition-colors"
              autoFocus
              autoComplete="off"
            />
            <datalist id="user-list">
              {ALLOWED_USERS.map((u) => (
                <option key={u} value={u} />
              ))}
            </datalist>
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

        {/* Apply for access - always visible like Streamlit */}
        <div className="mt-6 pt-4 border-t border-[var(--border-card)]">
          <p className="text-sm text-[var(--text-secondary)] mb-3">
            {"\u6CA1\u6709\u6743\u9650\uFF1F"} / No access?
          </p>
          <label className="block text-sm font-medium text-[var(--text-primary)] mb-1.5">
            {"\u7533\u8BF7"} Login
          </label>
          <input
            type="text"
            value={applyName}
            onChange={(e) => setApplyName(e.target.value)}
            placeholder={"\u8F93\u5165\u60A8\u60F3\u7533\u8BF7\u7684\u767B\u5F55\u540D"}
            className="w-full border border-[var(--border-card)] rounded-lg px-4 py-2.5 text-sm text-[var(--text-primary)] bg-white focus:outline-none focus:border-[var(--accent)] mb-3"
          />
          {applySuccess ? (
            <p className="text-sm text-[var(--success)] text-center">
              {"\u2705"} {"\u7533\u8BF7\u5DF2\u63D0\u4EA4\uFF0C\u7B49\u5F85\u7BA1\u7406\u5458\u5BA1\u6838"}
            </p>
          ) : (
            <Button
              onClick={() => {
                if (applyName.trim()) setApplySuccess(true);
              }}
              disabled={!applyName.trim()}
              variant="secondary"
              className="w-full"
            >
              {"\u{1F4E8}"} {"\u7533\u8BF7\u6743\u9650"}
            </Button>
          )}
        </div>
      </GlassCard>
    </div>
  );
}
