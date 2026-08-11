"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { useI18nStore } from "@/stores/i18n-store";
import { Sidebar } from "@/components/layout/Sidebar";
import { ChatPanel } from "@/components/layout/ChatPanel";
import { LanguageSwitcher } from "@/components/layout/LanguageSwitcher";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { isAuthenticated, isSessionExpired, logout, touch } = useAuthStore();
  const { loadStrings, loaded } = useI18nStore();

  // Load i18n strings on mount
  useEffect(() => {
    if (!loaded) {
      loadStrings();
    }
  }, [loaded, loadStrings]);

  // Check auth - delay to allow hydration from localStorage
  useEffect(() => {
    // Give zustand persist time to hydrate from localStorage
    const timer = setTimeout(() => {
      if (!isAuthenticated) {
        router.replace("/login");
        return;
      }
      if (isSessionExpired()) {
        logout();
        router.replace("/login");
      }
    }, 100);
    return () => clearTimeout(timer);
  }, [isAuthenticated, isSessionExpired, logout, router]);

  // Track user activity for session timeout
  useEffect(() => {
    const handleActivity = () => touch();
    window.addEventListener("click", handleActivity);
    window.addEventListener("keydown", handleActivity);
    return () => {
      window.removeEventListener("click", handleActivity);
      window.removeEventListener("keydown", handleActivity);
    };
  }, [touch]);

  if (!isAuthenticated) {
    return null; // Will redirect
  }

  return (
    <div className="flex min-h-screen bg-[var(--bg-surface)]">
      <Sidebar />
      <main className="flex-1 ml-[var(--sidebar-collapsed)] lg:ml-[var(--sidebar-width)] p-6 transition-all duration-200 relative">
        {/* Global language switcher - top right */}
        <div className="absolute top-4 right-4 z-30">
          <LanguageSwitcher />
        </div>
        {children}
      </main>
      <ChatPanel />
    </div>
  );
}
