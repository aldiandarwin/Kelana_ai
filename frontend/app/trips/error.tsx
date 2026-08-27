"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export default function TripsError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const router = useRouter();

  return (
    <div className="flex min-h-screen flex-col bg-[#f5f7f2]">
      <SiteHeader />
      <main className="grid flex-1 place-items-center px-5 py-16">
        <div
          role="alert"
          className="w-full max-w-2xl rounded-[2rem] border border-rose-200 bg-rose-50 p-8 text-center sm:p-12"
        >
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-rose-700">
            We hit some turbulence
          </p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-rose-950">
            Trip history is unavailable
          </h1>
          <p className="mx-auto mt-4 max-w-lg text-sm leading-6 text-rose-900/70">
            KelanaAI could not reach the travel service. Make sure FastAPI and
            PostgreSQL are running, then try again.
          </p>
          <div className="mt-7 flex flex-col justify-center gap-3 sm:flex-row">
            <button
              type="button"
              onClick={() => {
                router.refresh();
                reset();
              }}
              className="rounded-full bg-rose-900 px-6 py-3 text-sm font-bold text-white transition hover:bg-rose-800"
            >
              Try again
            </button>
            <Link
              href="/"
              className="rounded-full border border-rose-300 px-6 py-3 text-sm font-bold text-rose-900 transition hover:bg-rose-100"
            >
              Back home
            </Link>
          </div>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
