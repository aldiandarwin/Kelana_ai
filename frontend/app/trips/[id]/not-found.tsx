import Link from "next/link";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export default function TripNotFound() {
  return (
    <div className="flex min-h-screen flex-col bg-[#f5f7f2]">
      <SiteHeader />
      <main className="grid flex-1 place-items-center px-5 py-16 text-center">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-teal-700">
            Trip not found
          </p>
          <h1 className="mt-3 text-4xl font-semibold tracking-[-0.04em] text-slate-950">
            This itinerary does not exist
          </h1>
          <p className="mx-auto mt-4 max-w-lg text-sm leading-6 text-slate-500">
            The trip may have been removed, or the link may be incorrect.
          </p>
          <Link
            href="/trips"
            className="mt-7 inline-flex rounded-full bg-teal-800 px-6 py-3 text-sm font-bold text-white transition hover:bg-teal-700"
          >
            Back to trip history
          </Link>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
