import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col bg-[#f5f7f2]">
      <SiteHeader />
      <main className="grid flex-1 place-items-center px-5 py-16">
        <div className="w-full max-w-2xl rounded-[2rem] border border-teal-100 bg-white p-8 text-center sm:p-12">
          <p className="text-sm font-bold uppercase tracking-[0.2em] text-teal-700">404 · A little off the map</p>
          <h1 className="mt-4 text-4xl font-semibold tracking-tight text-teal-950">This stop doesn&apos;t exist</h1>
          <p className="mx-auto mt-5 max-w-md leading-7 text-slate-600">The page may have moved, or the link may be incomplete. Let&apos;s get you back to planning your next adventure.</p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Link href="/" className="rounded-full bg-teal-800 px-6 py-3 font-semibold text-white hover:bg-teal-700">Back to planning</Link>
            <Link href="/about" className="rounded-full border border-teal-200 px-6 py-3 font-semibold text-teal-900 hover:bg-teal-50">About KelanaAI</Link>
          </div>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
