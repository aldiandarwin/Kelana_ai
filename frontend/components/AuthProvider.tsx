"use client";

import { usePathname, useRouter } from "next/navigation";
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import {
  AuthServiceError,
  getCurrentUser,
  logout as logoutRequest,
} from "@/services/authService";
import type { User } from "@/types/auth";

type AuthContextValue = {
  user: User | null;
  loading: boolean;
  refreshUser: () => Promise<User | null>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
      return currentUser;
    } catch (error) {
      if (error instanceof AuthServiceError && error.status === 401) {
        setUser(null);
        return null;
      }
      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let active = true;
    getCurrentUser()
      .then((currentUser) => {
        if (active) setUser(currentUser);
      })
      .catch((error) => {
        if (!active) return;
        setUser(null);
        if (
          error instanceof AuthServiceError &&
          error.status === 401 &&
          pathname !== "/login" &&
          pathname !== "/register"
        ) {
          router.replace("/login");
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    function handleUnauthorized() {
      setUser(null);
      router.replace("/login");
      router.refresh();
    }

    window.addEventListener("kelana:unauthorized", handleUnauthorized);
    return () => {
      active = false;
      window.removeEventListener("kelana:unauthorized", handleUnauthorized);
    };
  }, [pathname, router]);

  const logout = useCallback(async () => {
    try {
      await logoutRequest();
    } finally {
      setUser(null);
      router.replace("/login");
      router.refresh();
    }
  }, [router]);

  const value = useMemo(
    () => ({ user, loading, refreshUser, logout }),
    [user, loading, refreshUser, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
