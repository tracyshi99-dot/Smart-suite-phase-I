"use client";

import { useI18nStore } from "@/stores/i18n-store";
import { SUPPORTED_LOCALES, LOCALE_LABELS, SupportedLocale } from "@/lib/constants";

export function LanguageSwitcher() {
  const { locale, setLocale } = useI18nStore();

  return (
    <select
      value={locale}
      onChange={(e) => setLocale(e.target.value as SupportedLocale)}
      className="border border-[var(--border-card)] rounded-lg px-3 py-1.5 text-xs text-[var(--text-secondary)] bg-white focus:outline-none focus:border-[var(--accent)] cursor-pointer"
      aria-label="Language"
    >
      {SUPPORTED_LOCALES.map((loc) => (
        <option key={loc} value={loc}>
          {LOCALE_LABELS[loc]}
        </option>
      ))}
    </select>
  );
}
