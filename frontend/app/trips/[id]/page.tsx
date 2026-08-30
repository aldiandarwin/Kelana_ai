"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

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
  getRequestFailureMessage,
  getTrip,
  TripServiceError,
} from "@/services/tripService";
import type { Trip } from "@/types/trip";

export default function TripDetailPage() {
  const params = useParams<{ id: string }>();
  const [trip, setTrip] = useState<Trip | null>(null);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<number | undefined>();
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadTrip() {
      const id = params.id;
      if (!/^\d+$/.test(id)) {
        setStatus(404);
        setLoading(false);
        return;
      }

      try {
        setTrip(await getTrip(Number(id)));
      } catch (requestError) {
        if (requestError instanceof TripServiceError) {
          setStatus(requestError.status);
        }
        setError(getRequestFailureMessage(requestError));
      } finally {
        setLoading(false);
      }
    }
    void loadTrip();
  }, [params.id]);

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col bg-[#f5f7f2]">
        <SiteHeader />
        <main className="grid flex-1 place-items-center px-5 text-center">
          <div>
            <span className="mx-auto block size-11 animate-spin rounded-full border-[3px] border-teal-800/20 border-t-teal-800" />
            <p className="mt-5 font-semibold text-teal-950">Opening your itinerary</p>
          </div>
        </main>
        <SiteFooter />
      </div>
    );
  }

  if (!trip) {
    const forbidden = status === 403;
    return (
      <div className="flex min-h-screen flex-col bg-[#f5f7f2] text-slate-950">
        <SiteHeader />
        <main className="grid flex-1 place-items-center px-5 py-16 text-center">
          <div className="max-w-lg rounded-[2rem] border border-slate-200 bg-white p-8 shadow-sm sm:p-12">
            <span aria-hidden="true" className="text-4xl">{forbidden ? "🔒" : "🧭"}</span>
            <h1 className="mt-5 text-3xl font-semibold tracking-tight">
              {forbidden ? "This trip belongs to another traveler" : "Trip not found"}
            </h1>
            <p className="mt-3 text-sm leading-6 text-slate-500">
              {forbidden
                ? "KelanaAI protected this itinerary because its owner does not match your authenticated account."
                : error || "This itinerary may no longer exist."}
            </p>
            <Link href="/trips" className="mt-7 inline-flex rounded-full bg-teal-800 px-6 py-3 text-sm font-bold text-white hover:bg-teal-700">
              Back to my trips
            </Link>
          </div>
        </main>
        <SiteFooter />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-[#f5f7f2] text-slate-950">
      <SiteHeader />
      <main className="flex-1">
        <section className="border-b border-slate-200 bg-white">
          <div className="mx-auto max-w-7xl px-5 py-10 sm:px-8 sm:py-14 lg:px-10">
            <Link href="/trips" className="inline-flex items-center gap-2 text-sm font-bold text-teal-800 transition hover:text-teal-700">
              <span aria-hidden="true">←</span> Back to my trips
            </Link>

            <div className="mt-8 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
              <div className="flex items-start gap-4">
                <span aria-hidden="true" className="grid size-14 shrink-0 place-items-center rounded-2xl bg-teal-50 text-3xl">
                  {getDestinationIcon(trip.destination)}
                </span>
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.2em] text-teal-700">Your saved itinerary</p>
                  <h1 className="mt-2 text-4xl font-semibold tracking-[-0.04em] sm:text-5xl">{trip.destination}</h1>
                  <p className="mt-3 text-sm text-slate-500">Created {formatTripDate(trip.created_at)}</p>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                <span className={"rounded-full px-4 py-2 text-xs font-bold " + getCategoryBadgeClasses(trip.category)}>{trip.category}</span>
                <span className={"rounded-full border px-4 py-2 text-xs font-bold " + getTravelStyleBadgeClasses(trip.travel_style?.trim() || "General")}>
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
                <div key={label} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">{label}</dt>
                  <dd className="mt-1 font-semibold text-slate-900">{value}</dd>
                </div>
              ))}
            </dl>
          </div>
        </section>

        <section className="mx-auto max-w-7xl px-5 py-12 sm:px-8 sm:py-16 lg:px-10">
          <div className="mb-8">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-teal-700">AI recommendation</p>
            <h2 className="mt-2 text-3xl font-semibold tracking-[-0.035em]">Your day-by-day plan</h2>
          </div>

          {trip.ai_recommendation ? (
            <ItineraryContent recommendation={trip.ai_recommendation} />
          ) : (
            <div className="rounded-[2rem] border border-dashed border-amber-300 bg-amber-50 px-6 py-14 text-center">
              <h2 className="text-xl font-semibold text-amber-950">This trip has no AI itinerary yet</h2>
              <p className="mx-auto mt-3 max-w-lg text-sm leading-6 text-amber-900/70">
                Older saved trips may only contain budget details. Generate a new trip to save a complete recommendation.
              </p>
              <Link href="/#planner" className="mt-7 inline-flex rounded-full bg-amber-900 px-6 py-3 text-sm font-bold text-white hover:bg-amber-800">
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
