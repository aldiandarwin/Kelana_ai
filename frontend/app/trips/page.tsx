import type { Metadata } from "next";
import { connection } from "next/server";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { TripsDashboard } from "@/components/TripsDashboard";
import { getTrips } from "@/services/tripService";

export const metadata: Metadata = {
  title: "My Trips | KelanaAI",
  description: "Browse and revisit every itinerary saved in KelanaAI.",
};

export default async function TripsPage() {
  await connection();
  const trips = await getTrips();

  return (
    <div className="flex min-h-screen flex-col bg-[#f5f7f2] text-slate-950">
      <SiteHeader />

      <main className="flex-1">
        <section className="overflow-hidden bg-[#083d42] text-white">
          <div className="mx-auto max-w-7xl px-5 py-14 sm:px-8 sm:py-18 lg:px-10">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-amber-300">
              Your travel archive
            </p>
            <div className="mt-3 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <h1 className="text-4xl font-semibold tracking-[-0.04em] sm:text-5xl">
                  Trip history
                </h1>
                <p className="mt-4 max-w-2xl text-base leading-7 text-white/70">
                  Revisit saved plans without generating another AI response.
                  Every itinerary below comes directly from PostgreSQL.
                </p>
              </div>
              <span className="w-fit rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-white/80">
                {trips.length} saved {trips.length === 1 ? "trip" : "trips"}
              </span>
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-5 py-10 sm:px-8 sm:py-14 lg:px-10">
          <TripsDashboard initialTrips={trips} />
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
