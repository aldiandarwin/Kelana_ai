"use client";

import Link from "next/link";

export default function AppError({ retry }: { error: Error & { digest?: string }; retry: () => void }) {
  return (
    <main className="grid min-h-screen place-items-center bg-[#f5f7f2] px-5 py-16">
      <div role="alert" className="w-full max-w-2xl rounded-[2rem] border border-rose-200 bg-white p-8 text-center sm:p-12">
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-rose-700">KelanaAI · An unexpected detour</p>
        <h1 className="mt-4 text-3xl font-semibold text-slate-950">We couldn&apos;t load this page</h1>
        <p className="mt-5 leading-7 text-slate-600">Something went wrong while preparing your page. Wait a moment and try again. If you just submitted a request, check your trip or chat history before submitting it again.</p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <button onClick={() => retry()} className="rounded-full bg-teal-800 px-6 py-3 font-semibold text-white hover:bg-teal-700">Try again</button>
          <Link href="/about" className="rounded-full border border-slate-200 px-6 py-3 font-semibold text-slate-700">About KelanaAI</Link>
        </div>
      </div>
    </main>
  );
}
