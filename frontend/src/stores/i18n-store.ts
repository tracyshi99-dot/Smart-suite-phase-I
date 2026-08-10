import { create } from "zustand";
import { persist } from "zustand/middleware";
import { SUPPORTED_LOCALES, SupportedLocale } from "@/lib/constants";

type StringsMap = Record<string, Record<string, string>>;

interface I18nState {
  locale: SupportedLocale;
  strings: StringsMap;
  loaded: boolean;
  setLocale: (locale: SupportedLocale) => void;
  t: (key: string) => string;
  loadStrings: () => Promise<void>;
}

export const useI18nStore = create<I18nState>()(
  persist(
    (set, get) => ({
      locale: "zh-CN",
      strings: {},
      loaded: false,

      setLocale: (locale: SupportedLocale) => {
        // Validate locale
        if (SUPPORTED_LOCALES.includes(locale)) {
          set({ locale });
        } else {
          console.warn(`[i18n] Invalid locale "${locale}", defaulting to "en"`);
          set({ locale: "en" });
        }
      },

      t: (key: string) => {
        const { strings, locale } = get();
        const entry = strings[key];
        if (!entry) return key; // Key not found, return raw key
        // Try current locale
        if (entry[locale]) return entry[locale];
        // Fallback to English
        if (entry["en"]) return entry["en"];
        // Return raw key
        return key;
      },

      loadStrings: async () => {
        try {
          const res = await fetch("/i18n/strings.json");
          if (res.ok) {
            const data = await res.json();
            set({ strings: data, loaded: true });
          }
        } catch {
          console.warn("[i18n] Failed to load strings.json");
        }
      },
    }),
    {
      name: "i18n-store",
      partialize: (state) => ({
        locale: state.locale,
      }),
    }
  )
);
