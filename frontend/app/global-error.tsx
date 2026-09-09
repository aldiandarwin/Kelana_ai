"use client";

import "./globals.css";

export default function GlobalError({ retry }: { error: Error & { digest?: string }; retry: () => void }) {
  return (
    <html lang="en">
      <head><title>KelanaAI | Temporarily unavailable</title></head>
      <body>
        <main className="grid min-h-screen place-items-center bg-[#f5f7f2] px-5 py-16">
          <div role="alert" className="w-full max-w-xl rounded-3xl border border-rose-200 bg-white p-10 text-center">
            <p className="text-sm font-semibold text-teal-800">KelanaAI</p>
            <h1 className="mt-4 text-3xl font-semibold text-slate-950">We hit an unexpected detour</h1>
            <p className="mt-5 leading-7 text-slate-600">The application is temporarily unavailable. Please try again in a moment. Check your saved history before repeating a request.</p>
            <button onClick={() => retry()} className="mt-7 rounded-full bg-teal-800 px-6 py-3 font-semibold text-white hover:bg-teal-700">Try again</button>
          </div>
        </main>
      </body>
    </html>
  );
}
