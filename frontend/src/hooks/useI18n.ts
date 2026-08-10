"use client";

import { useI18nStore } from "@/stores/i18n-store";

/**
 * Convenience hook for translation.
 * Usage: const { t, locale, setLocale } = useI18n();
 */
export function useI18n() {
  const { t, locale, setLocale, loadStrings, loaded } = useI18nStore();
  return { t, locale, setLocale, loadStrings, loaded };
}
