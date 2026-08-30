"use client";

import { useEffect, useState } from "react";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { TripsDashboard } from "@/components/TripsDashboard";
import { getRequestFailureMessage, getTrips } from "@/services/tripService";
import type { Trip } from "@/types/trip";

export default function TripsPage() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadTrips() {
      try {
        setTrips(await getTrips());
      } catch (requestError) {
        setError(getRequestFailureMessage(requestError));
      } finally {
        setLoading(false);
      }
    }
    void loadTrips();
  }, []);

  return (
    <div className="flex min-h-screen flex-col bg-[#f5f7f2] text-slate-950">
      <SiteHeader />

      <main className="flex-1">
        <section className="overflow-hidden bg-[#083d42] text-white">
          <div className="mx-auto max-w-7xl px-5 py-14 sm:px-8 sm:py-18 lg:px-10">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-amber-300">
              Your private travel archive
            </p>
            <div className="mt-3 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <h1 className="text-4xl font-semibold tracking-[-0.04em] sm:text-5xl">
                  My trip history
                </h1>
                <p className="mt-4 max-w-2xl text-base leading-7 text-white/70">
                  Every itinerary below is filtered by your authenticated account. Other travelers cannot see this list.
                </p>
              </div>
              {!loading && !error && (
                <span className="w-fit rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-semibold text-white/80">
                  {trips.length} saved {trips.length === 1 ? "trip" : "trips"}
                </span>
              )}
            </div>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-5 py-10 sm:px-8 sm:py-14 lg:px-10">
          {loading && (
            <div aria-live="polite" className="grid min-h-72 place-items-center rounded-[2rem] border border-slate-200 bg-white text-center shadow-sm">
              <div>
                <span className="mx-auto block size-10 animate-spin rounded-full border-[3px] border-teal-800/20 border-t-teal-800" />
                <p className="mt-5 font-semibold text-teal-950">Loading your private trips</p>
              </div>
            </div>
          )}
          {!loading && error && (
            <div role="alert" className="rounded-[2rem] border border-rose-200 bg-rose-50 p-8 text-center">
              <h2 className="text-xl font-semibold text-rose-950">Unable to load your trips</h2>
              <p className="mt-3 text-sm text-rose-800">{error}</p>
            </div>
          )}
          {!loading && !error && <TripsDashboard initialTrips={trips} />}
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
