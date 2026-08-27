import Link from "next/link";

import {
  formatBudget,
  formatTripDate,
  getCategoryBadgeClasses,
  getDestinationIcon,
  getTravelStyleBadgeClasses,
} from "@/lib/tripFormatting";
import type { Trip } from "@/types/trip";

export function TripCard({ trip }: { trip: Trip }) {
  const travelStyle = trip.travel_style?.trim() || "General";

  return (
    <Link
      href={"/trips/" + trip.id}
      aria-label={"View " + trip.destination + " itinerary"}
      className="group flex h-full flex-col rounded-3xl border border-slate-200/80 bg-white p-6 shadow-sm transition duration-200 hover:-translate-y-1 hover:border-teal-700/30 hover:shadow-xl hover:shadow-slate-900/8 focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-teal-700"
    >
      <div className="flex items-start justify-between gap-4">
        <span
          aria-hidden="true"
          className="grid size-12 shrink-0 place-items-center rounded-2xl bg-teal-50 text-2xl"
        >
          {getDestinationIcon(trip.destination)}
        </span>
        <span
          className={
            "rounded-full px-3 py-1 text-xs font-bold " +
            getCategoryBadgeClasses(trip.category)
          }
        >
          {trip.category}
        </span>
      </div>

      <div className="mt-6">
        <h2 className="text-2xl font-semibold tracking-[-0.03em] text-slate-950">
          {trip.destination}
        </h2>
        <p className="mt-2 text-sm text-slate-500">
          Saved {formatTripDate(trip.created_at)}
        </p>
      </div>

      <dl className="mt-6 grid grid-cols-2 gap-3 text-sm">
        <div className="rounded-2xl bg-slate-50 p-3">
          <dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">
            Duration
          </dt>
          <dd className="mt-1 font-semibold text-slate-800">{trip.days} days</dd>
        </div>
        <div className="rounded-2xl bg-slate-50 p-3">
          <dt className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">
            Budget
          </dt>
          <dd className="mt-1 font-semibold text-slate-800">
            {formatBudget(trip.budget)}
          </dd>
        </div>
      </dl>

      <div className="mt-5 flex flex-wrap gap-2">
        <span
          className={
            "rounded-full border px-3 py-1 text-xs font-semibold " +
            getTravelStyleBadgeClasses(travelStyle)
          }
        >
          {travelStyle}
        </span>
        <span className="rounded-full border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-500">
          {trip.ai_recommendation ? "AI itinerary ready" : "Plan pending"}
        </span>
      </div>

      <span className="mt-7 inline-flex items-center gap-2 text-sm font-bold text-teal-800">
        View itinerary
        <span
          aria-hidden="true"
          className="transition-transform duration-200 group-hover:translate-x-1"
        >
          →
        </span>
      </span>
    </Link>
  );
}
