"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { useAuth } from "@/components/AuthProvider";

export default function ProfilePage() {
  const router = useRouter();
  const { user, loading } = useAuth();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, router, user]);

  return (
    <div className="flex min-h-screen flex-col bg-[#f5f7f2] text-slate-950">
      <SiteHeader />
      <main className="flex-1">
        <section className="bg-[#083d42] text-white">
          <div className="mx-auto max-w-5xl px-5 py-14 sm:px-8 sm:py-18">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-amber-300">
              Your KelanaAI account
            </p>
            <h1 className="mt-3 text-4xl font-semibold tracking-[-0.04em] sm:text-5xl">
              Profile
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-white/70">
              This identity is read from your verified JWT. No user id is accepted from the page URL.
            </p>
          </div>
        </section>

        <section className="mx-auto max-w-5xl px-5 py-10 sm:px-8 sm:py-14">
          {loading || !user ? (
            <div className="animate-pulse rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm sm:p-10">
              <div className="size-20 rounded-3xl bg-slate-100" />
              <div className="mt-6 h-8 w-52 rounded bg-slate-100" />
              <div className="mt-3 h-5 w-64 rounded bg-slate-100" />
            </div>
          ) : (
            <div className="overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-sm">
              <div className="flex flex-col gap-6 border-b border-slate-100 p-7 sm:flex-row sm:items-center sm:p-10">
                <span className="grid size-20 shrink-0 place-items-center rounded-3xl bg-teal-100 text-3xl font-semibold text-teal-900">
                  {user.name.slice(0, 1).toUpperCase()}
                </span>
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.18em] text-teal-700">
                    Authenticated traveler
                  </p>
                  <h2 className="mt-2 text-3xl font-semibold tracking-[-0.035em]">
                    {user.name}
                  </h2>
                  <p className="mt-2 text-slate-500">{user.email}</p>
                </div>
              </div>

              <dl className="grid gap-px bg-slate-100 sm:grid-cols-2">
                <div className="bg-white p-7 sm:p-8">
                  <dt className="text-xs font-bold uppercase tracking-[0.16em] text-slate-400">
                    Total trips generated
                  </dt>
                  <dd className="mt-3 text-4xl font-semibold tracking-tight text-teal-900">
                    {user.total_trips}
                  </dd>
                </div>
                <div className="bg-white p-7 sm:p-8">
                  <dt className="text-xs font-bold uppercase tracking-[0.16em] text-slate-400">
                    Member since
                  </dt>
                  <dd className="mt-3 text-xl font-semibold text-slate-900">
                    {new Intl.DateTimeFormat("en", {
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                    }).format(new Date(user.created_at))}
                  </dd>
                </div>
              </dl>

              <div className="flex flex-col gap-3 p-7 sm:flex-row sm:p-10">
                <Link href="/#planner" className="inline-flex min-h-12 items-center justify-center rounded-full bg-teal-800 px-6 text-sm font-bold text-white transition hover:bg-teal-700">
                  Plan a new trip
                </Link>
                <Link href="/trips" className="inline-flex min-h-12 items-center justify-center rounded-full border border-slate-200 px-6 text-sm font-bold text-slate-700 transition hover:border-teal-700/30 hover:text-teal-800">
                  View my trips
                </Link>
              </div>
            </div>
          )}
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}
