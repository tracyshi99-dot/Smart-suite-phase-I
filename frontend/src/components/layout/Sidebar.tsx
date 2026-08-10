"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { useI18nStore } from "@/stores/i18n-store";
import { NAV_ITEMS, LOCALE_LABELS, SUPPORTED_LOCALES, SupportedLocale } from "@/lib/constants";

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();
  const { locale, setLocale, t } = useI18nStore();

  return (
    <aside className="fixed left-0 top-0 h-full w-[var(--sidebar-width)] bg-[var(--bg-secondary)]/80 backdrop-blur-md border-r border-[var(--border-glass)] flex flex-col z-40 lg:w-[var(--sidebar-width)] md:w-[var(--sidebar-collapsed)] transition-all duration-200">
      {/* Logo / Title */}
      <div className="p-4 border-b border-[var(--border-glass)]">
        <h1 className="text-lg font-bold text-[var(--accent)] md:text-center lg:text-left">
          <span className="lg:inline md:hidden">Smart Suite</span>
          <span className="lg:hidden md:inline">SS</span>
        </h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 overflow-y-auto" aria-label="Main navigation">
        <ul className="space-y-1 px-2">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.path;
            return (
              <li key={item.id}>
                <Link
                  href={item.path}
                  className={`
                    flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all
                    ${
                      isActive
                        ? "bg-[var(--accent)]/10 text-[var(--accent)] border border-[var(--accent)]/30"
                        : "text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/5"
                    }
                  `}
                  aria-current={isActive ? "page" : undefined}
                >
                  <span className="w-6 h-6 flex items-center justify-center text-base">
                    {getNavIcon(item.id)}
                  </span>
                  <span className="lg:inline md:hidden">
                    {t(`nav.${item.id}`)}
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Bottom section */}
      <div className="p-3 border-t border-[var(--border-glass)] space-y-2">
        {/* Language switcher */}
        <select
          value={locale}
          onChange={(e) => setLocale(e.target.value as SupportedLocale)}
          className="w-full bg-white/5 border border-[var(--border-glass)] rounded-lg px-2 py-1.5 text-xs text-[var(--text-secondary)] focus:outline-none focus:border-[var(--accent)]"
          aria-label={t("lang.switch")}
        >
          {SUPPORTED_LOCALES.map((loc) => (
            <option key={loc} value={loc} className="bg-[var(--bg-secondary)]">
              {LOCALE_LABELS[loc]}
            </option>
          ))}
        </select>

        {/* User + Logout */}
        <div className="flex items-center justify-between">
          <span className="text-xs text-[var(--text-muted)] truncate lg:inline md:hidden">
            {user}
          </span>
          <button
            onClick={logout}
            className="text-xs text-[var(--text-secondary)] hover:text-[var(--error)] transition-colors"
            aria-label={t("auth.logout")}
          >
            {t("auth.logout")}
          </button>
        </div>
      </div>
    </aside>
  );
}

function getNavIcon(id: string): string {
  const icons: Record<string, string> = {
    overview: "🏠",
    zhiku: "📚",
    zhice: "🔍",
    zhizao: "⚡",
    zhiyou: "✨",
    zhibu: "📤",
    zhixi: "📊",
    zhongshu: "🎛️",
    request: "🔄",
  };
  return icons[id] ?? "•";
}
