"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";

/**
 * Hook that checks auth state and redirects to login if not authenticated.
 * Returns auth state for conditional rendering.
 */
export function useAuth() {
  const router = useRouter();
  const { isAuthenticated, isSessionExpired, logout, user, region, isAdmin, touch } =
    useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }
    if (isSessionExpired()) {
      logout();
      router.replace("/login");
    }
  }, [isAuthenticated, isSessionExpired, logout, router]);

  return {
    isAuthenticated,
    user,
    region,
    isAdmin,
    touch,
    logout,
  };
}
