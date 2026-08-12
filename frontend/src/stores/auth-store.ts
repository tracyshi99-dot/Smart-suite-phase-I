import { create } from "zustand";
import { persist } from "zustand/middleware";
import { apiGet } from "@/lib/api-client";
import { AuthResponse, RegionConfig } from "@/lib/types";
import { SESSION_TIMEOUT_MS } from "@/lib/constants";

interface AuthState {
  user: string | null;
  region: string;
  subRegion: string;
  isAdmin: boolean;
  isAuthenticated: boolean;
  lastActivity: number;
  regionConfig: RegionConfig | null;
  login: (user: string) => Promise<AuthResponse>;
  logout: () => void;
  touch: () => void;
  isSessionExpired: () => boolean;
  loadRegionConfig: (region: string) => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      region: "CN",
      subRegion: "",
      isAdmin: false,
      isAuthenticated: false,
      lastActivity: Date.now(),
      regionConfig: null,

      login: async (user: string) => {
        try {
          const res = await apiGet<AuthResponse>("/api/auth/check", { user });
          if (res.allowed) {
            set({
              user: res.user,
              region: res.region ?? "CN",
              subRegion: res.sub_region ?? "",
              isAdmin: res.is_admin ?? false,
              isAuthenticated: true,
              lastActivity: Date.now(),
            });
            // Load region config after successful auth
            await get().loadRegionConfig(res.region ?? "CN");
          }
          return res;
        } catch {
          // Offline fallback: if API is unreachable, allow known users locally
          const OFFLINE_ALLOWED = [
            "yujiashi", "htp", "shencm", "chienlin", "emilwliu", "gurusuh", "hangntt",
            "nijuno", "zhjiayue", "gracezjy", "jessyhan", "fengceci", "effiezhu",
            "jltian", "qdhwzj", "siyundai", "tzuchunf", "yudiwan",
            "ykimche", "liangles", "rickylan", "sylviayj",
            "cshumin", "xinyill", "kexuache", "yirua", "huiml", "xdhuang", "aizhen",
          ];
          const normalizedUser = user.trim().toLowerCase();
          if (OFFLINE_ALLOWED.includes(normalizedUser)) {
            const offlineRes: AuthResponse = {
              allowed: true,
              user: normalizedUser,
              region: "CN",
              is_admin: normalizedUser === "yujiashi",
            };
            set({
              user: offlineRes.user,
              region: offlineRes.region ?? "CN",
              subRegion: "",
              isAdmin: offlineRes.is_admin ?? false,
              isAuthenticated: true,
              lastActivity: Date.now(),
            });
            await get().loadRegionConfig("CN");
            return offlineRes;
          }
          // Not in offline list, rethrow
          throw { status: 0, message: "Connection error", isTimeout: true, retriesExhausted: true };
        }
      },

      logout: () => {
        set({
          user: null,
          region: "CN",
          subRegion: "",
          isAdmin: false,
          isAuthenticated: false,
          lastActivity: 0,
          regionConfig: null,
        });
      },

      touch: () => {
        set({ lastActivity: Date.now() });
      },

      isSessionExpired: () => {
        const { lastActivity, isAuthenticated } = get();
        if (!isAuthenticated) return false;
        return Date.now() - lastActivity > SESSION_TIMEOUT_MS;
      },

      loadRegionConfig: async (region: string) => {
        try {
          // Try to fetch region config from a known path or API
          // For now, use hardcoded defaults based on region
          const configs: Record<string, Partial<RegionConfig>> = {
            CN: {
              region_code: "CN",
              display_name: "China",
              ui_language: "zh-CN",
              ai_platforms: {
                default_selected: ["deepseek", "doubao", "kimi", "yuanbao", "qianwen", "chatgpt", "gemini", "perplexity", "grok"],
                available: [],
              },
              default_seeds: ["跨境电商怎么做", "亚马逊开店流程", "FBA发货教程"],
              verification_platforms: ["deepseek", "doubao", "kimi", "chatgpt", "perplexity", "grok"],
              content_languages: [{ code: "zh-CN", name: "简体中文" }, { code: "en", name: "English" }],
            },
            NA: {
              region_code: "NA",
              display_name: "North America",
              ui_language: "en",
              ai_platforms: {
                default_selected: ["chatgpt", "gemini"],
                available: ["perplexity", "grok"],
              },
              default_seeds: ["how to sell on Amazon US", "Amazon FBA for beginners"],
              verification_platforms: ["chatgpt", "perplexity", "grok"],
              content_languages: [{ code: "en", name: "English" }],
            },
          };
          set({ regionConfig: (configs[region] ?? configs.CN) as RegionConfig });
        } catch {
          // Fallback to CN config
          console.warn("[auth-store] Failed to load region config, using defaults");
        }
      },
    }),
    {
      name: "auth-store",
      partialize: (state) => ({
        user: state.user,
        region: state.region,
        subRegion: state.subRegion,
        isAdmin: state.isAdmin,
        isAuthenticated: state.isAuthenticated,
        lastActivity: state.lastActivity,
      }),
    }
  )
);
