"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { AuthShell } from "@/components/AuthShell";
import { getAuthFailureMessage, register } from "@/services/authService";

const inputClasses =
  "min-h-13 w-full rounded-xl border border-slate-200 bg-white px-4 text-base font-medium text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-teal-600 focus:ring-4 focus:ring-teal-600/10";

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      await register({ name, email, password });
      router.push(
        "/login?registered=1&email=" + encodeURIComponent(email.trim().toLowerCase()),
      );
    } catch (requestError) {
      setError(getAuthFailureMessage(requestError));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell
      eyebrow="Create your private workspace"
      title="Start planning as you."
      description="Your account keeps every itinerary tied to one owner, so other travelers cannot view or change it."
      footer={
        <>
          Already have an account?{" "}
          <Link href="/login" className="font-bold text-teal-800 hover:text-teal-700">
            Sign in
          </Link>
        </>
      }
    >
      {error && (
        <div role="alert" className="mb-5 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-800">
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit} className="grid gap-4">
        <label className="grid gap-2 text-sm font-semibold text-slate-700">
          Full name
          <input
            required
            minLength={2}
            maxLength={100}
            autoComplete="name"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Alice Traveler"
            className={inputClasses}
          />
        </label>
        <label className="grid gap-2 text-sm font-semibold text-slate-700">
          Email address
          <input
            required
            maxLength={255}
            autoComplete="email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@example.com"
            className={inputClasses}
          />
        </label>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="grid gap-2 text-sm font-semibold text-slate-700">
            Password
            <input
              required
              minLength={8}
              maxLength={72}
              autoComplete="new-password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="8+ characters"
              className={inputClasses}
            />
          </label>
          <label className="grid gap-2 text-sm font-semibold text-slate-700">
            Confirm password
            <input
              required
              minLength={8}
              maxLength={72}
              autoComplete="new-password"
              type="password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              placeholder="Repeat password"
              className={inputClasses}
            />
          </label>
        </div>
        <p className="text-xs leading-5 text-slate-500">
          Use at least 8 characters. Your password is hashed before it is stored.
        </p>
        <button
          type="submit"
          disabled={loading}
          className="mt-2 inline-flex min-h-13 items-center justify-center gap-3 rounded-full bg-teal-800 px-6 text-sm font-bold text-white shadow-lg shadow-teal-900/15 transition hover:bg-teal-700 disabled:cursor-wait disabled:opacity-65"
        >
          {loading ? "Creating your account..." : "Create my account"}
          {loading && <span className="size-5 animate-spin rounded-full border-2 border-white/30 border-t-white" />}
        </button>
      </form>
    </AuthShell>
  );
}
