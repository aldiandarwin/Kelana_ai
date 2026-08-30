"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { useAuth } from "@/components/AuthProvider";
import { getAuthFailureMessage, login } from "@/services/authService";

const inputClasses =
  "min-h-13 w-full rounded-xl border border-slate-200 bg-white px-4 text-base font-medium text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-teal-600 focus:ring-4 focus:ring-teal-600/10";

export function LoginForm({
  initialEmail,
  registered,
  nextPath,
}: {
  initialEmail: string;
  registered: boolean;
  nextPath: string;
}) {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [email, setEmail] = useState(initialEmail);
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      await login({ email, password });
      await refreshUser();
      router.replace(nextPath);
      router.refresh();
    } catch (requestError) {
      setError(getAuthFailureMessage(requestError));
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      {registered && (
        <div role="status" className="mb-5 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-800">
          Account created. Sign in with your new credentials.
        </div>
      )}
      {error && (
        <div role="alert" className="mb-5 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-800">
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit} className="grid gap-5">
        <label className="grid gap-2 text-sm font-semibold text-slate-700">
          Email address
          <input
            required
            autoComplete="email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@example.com"
            className={inputClasses}
          />
        </label>
        <label className="grid gap-2 text-sm font-semibold text-slate-700">
          Password
          <input
            required
            autoComplete="current-password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="Enter your password"
            className={inputClasses}
          />
        </label>
        <button
          type="submit"
          disabled={loading}
          className="mt-2 inline-flex min-h-13 items-center justify-center gap-3 rounded-full bg-teal-800 px-6 text-sm font-bold text-white shadow-lg shadow-teal-900/15 transition hover:bg-teal-700 disabled:cursor-wait disabled:opacity-65"
        >
          {loading ? "Signing you in..." : "Sign in securely"}
          {loading && <span className="size-5 animate-spin rounded-full border-2 border-white/30 border-t-white" />}
        </button>
      </form>
    </>
  );
}
