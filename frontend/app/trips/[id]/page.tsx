import Link from "next/link";
import { notFound } from "next/navigation";
import { connection } from "next/server";

import { ItineraryContent } from "@/components/ItineraryContent";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import {
  formatBudget,
  formatTripDate,
  getCategoryBadgeClasses,
  getDestinationIcon,
  getTravelStyleBadgeClasses,
} from "@/lib/tripFormatting";
import {
  getTrip,
  TripServiceError,
} from "@/services/tripService";
import type { Trip } from "@/types/trip";

export default async function TripDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  await connection();
  const { id } = await params;

  if (!/^\d+$/.test(id)) notFound();

  const tripId = Number(id);
  let trip: Trip;

  try {
    trip = await getTrip(tripId);
  } catch (error) {
    if (error instanceof TripServiceError && error.status === 404) notFound();
    throw error;
  }

  return (
    <div className="flex min-h-screen flex-col bg-[#f5f7f2] text-slate-950">
      <SiteHeader />

      <main className="flex-1">
        <section className="border-b border-slate-200 bg-white">
          <div className="mx-auto max-w-7xl px-5 py-10 sm:px-8 sm:py-14 lg:px-10">
            <Link
              href="/trips"
              className="inline-flex items-center gap-2 text-sm font-bold text-teal-800 transition hover:text-teal-700"
            >
              <span aria-hidden="true">←</span> Back to trip history
            </Link>

            <div className="mt-8 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
              <div className="flex items-start gap-4">
                <span
                  aria-hidden="true"
                  className="grid size-14 shrink-0 place-items-center rounded-2xl bg-teal-50 text-3xl"
                >
                  {getDestinationIcon(trip.destination)}
                </span>
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.2em] text-teal-700">
                    Saved itinerary
                  </p>
                  <h1 className="mt-2 text-4xl font-semibold tracking-[-0.04em] sm:text-5xl">
                    {trip.destination}
                  </h1>
                  <p className="mt-3 text-sm text-slate-500">
                    Created {formatTripDate(trip.created_at)}
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                <span
                  className={
                    "rounded-full px-4 py-2 text-xs font-bold " +
                    getCategoryBadgeClasses(trip.category)
                  }
                >
                  {trip.category}
                </span>
                <span
                  className={
                    "rounded-full border px-4 py-2 text-xs font-bold " +
                    getTravelStyleBadgeClasses(
                      trip.travel_style?.trim() || "General",
                    )
                  }
                >
                  {trip.travel_style?.trim() || "General"}
                </span>
              </div>
            </div>

            <dl className="mt-9 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {[
                ["Destination", trip.destination],
                ["Duration", trip.days + " days"],
                ["Total budget", formatBudget(trip.budget)],
                ["Daily budget", formatBudget(trip.daily_budget)],
              ].map(([label, value]) => (
                <div
                  key={label}
                  className="rounded-2xl border border-slate-200 bg-slate-50 p-4"
                >
                  <dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">
                    {label}
                  </dt>
                  <dd className="mt-1 font-semibold text-slate-900">{value}</dd>
                </div>
              ))}
            </dl>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-5 py-12 sm:px-8 sm:py-16 lg:px-10">
          <div className="mb-8">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-teal-700">
              AI recommendation
            </p>
            <h2 className="mt-2 text-3xl font-semibold tracking-[-0.035em]">
              Your day-by-day plan
            </h2>
          </div>

          {trip.ai_recommendation ? (
            <ItineraryContent recommendation={trip.ai_recommendation} />
          ) : (
            <div className="rounded-[2rem] border border-dashed border-amber-300 bg-amber-50 px-6 py-14 text-center">
              <h2 className="text-xl font-semibold text-amber-950">
                This trip has no AI itinerary yet
              </h2>
              <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-amber-900/70">
                Older saved trips may only contain budget details. Generate a
                new trip to save a complete recommendation.
              </p>
              <Link
                href="/#planner"
                className="mt-7 inline-flex rounded-full bg-amber-900 px-6 py-3 text-sm font-bold text-white transition hover:bg-amber-800"
              >
                Plan a new trip
              </Link>
            </div>
          )}
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
