"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { TripCard } from "@/components/TripCard";
import type { Trip } from "@/types/trip";

type SortMode = "latest" | "oldest" | "highest-budget";

const PAGE_SIZE = 10;

function tripTimestamp(trip: Trip): number {
  const timestamp = new Date(trip.created_at).getTime();
  return Number.isNaN(timestamp) ? trip.id : timestamp;
}

export function TripsDashboard({ initialTrips }: { initialTrips: Trip[] }) {
  const [query, setQuery] = useState("");
  const [sortMode, setSortMode] = useState<SortMode>("latest");
  const [page, setPage] = useState(1);

  const visibleTrips = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    const filtered = initialTrips.filter((trip) => {
      if (!normalizedQuery) return true;

      return [trip.destination, trip.travel_style ?? ""].some((value) =>
        value.toLowerCase().includes(normalizedQuery),
      );
    });

    return [...filtered].sort((a, b) => {
      if (sortMode === "highest-budget") return b.budget - a.budget;
      if (sortMode === "oldest") return tripTimestamp(a) - tripTimestamp(b);
      return tripTimestamp(b) - tripTimestamp(a);
    });
  }, [initialTrips, query, sortMode]);

  if (initialTrips.length === 0) {
    return (
      <div className="rounded-[2rem] border border-dashed border-teal-700/25 bg-white px-6 py-16 text-center shadow-sm">
        <span aria-hidden="true" className="text-4xl">
          ✈️
        </span>
        <h2 className="mt-5 text-2xl font-semibold text-slate-950">
          No trips found
        </h2>
        <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-slate-500">
          Create your first itinerary and it will be saved here for your next
          visit.
        </p>
        <Link
          href="/#planner"
          className="mt-7 inline-flex rounded-full bg-teal-800 px-6 py-3 text-sm font-bold text-white transition hover:bg-teal-700"
        >
          Generate a trip
        </Link>
      </div>
    );
  }

  const totalPages = Math.max(1, Math.ceil(visibleTrips.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const pageTrips = visibleTrips.slice(
    (safePage - 1) * PAGE_SIZE,
    safePage * PAGE_SIZE,
  );

  return (
    <>
      <div className="grid gap-4 rounded-3xl border border-slate-200/80 bg-white p-4 shadow-sm sm:grid-cols-[1fr_auto] sm:p-5">
        <label className="grid gap-2 text-sm font-semibold text-slate-700">
          Search trips
          <div className="relative">
            <span
              aria-hidden="true"
              className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400"
            >
              ⌕
            </span>
            <input
              type="search"
              value={query}
              onChange={(event) => {
                setQuery(event.target.value);
                setPage(1);
              }}
              placeholder="Destination or travel style"
              className="min-h-12 w-full rounded-xl border border-slate-200 bg-slate-50 pl-11 pr-4 text-base font-medium text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-teal-600 focus:bg-white focus:ring-4 focus:ring-teal-600/10"
            />
          </div>
        </label>

        <label className="grid gap-2 text-sm font-semibold text-slate-700">
          Sort by
          <select
            value={sortMode}
            onChange={(event) => {
              setSortMode(event.target.value as SortMode);
              setPage(1);
            }}
            className="min-h-12 rounded-xl border border-slate-200 bg-slate-50 px-4 text-base font-medium text-slate-950 outline-none transition focus:border-teal-600 focus:bg-white focus:ring-4 focus:ring-teal-600/10"
          >
            <option value="latest">Latest</option>
            <option value="oldest">Oldest</option>
            <option value="highest-budget">Highest budget</option>
          </select>
        </label>
      </div>

      <div className="mt-6 flex items-center justify-between gap-4 text-sm text-slate-500">
        <p>
          {visibleTrips.length} {visibleTrips.length === 1 ? "trip" : "trips"}
        </p>
        {query && (
          <button
            type="button"
            onClick={() => {
              setQuery("");
              setPage(1);
            }}
            className="font-bold text-teal-800 transition hover:text-teal-700"
          >
            Clear search
          </button>
        )}
      </div>

      {pageTrips.length > 0 ? (
        <div className="mt-5 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {pageTrips.map((trip) => (
            <TripCard key={trip.id} trip={trip} />
          ))}
        </div>
      ) : (
        <div className="mt-5 rounded-[2rem] border border-dashed border-slate-300 bg-white px-6 py-14 text-center">
          <h2 className="text-xl font-semibold text-slate-950">
            No matching trips
          </h2>
          <p className="mt-2 text-sm text-slate-500">
            Try a different destination or travel style.
          </p>
        </div>
      )}

      {totalPages > 1 && (
        <nav
          aria-label="Trip history pagination"
          className="mt-8 flex items-center justify-center gap-4"
        >
          <button
            type="button"
            disabled={safePage === 1}
            onClick={() => setPage((current) => Math.max(1, current - 1))}
            className="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-bold text-slate-700 transition hover:border-teal-700/30 hover:text-teal-800 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Previous
          </button>
          <span className="text-sm font-semibold text-slate-500">
            Page {safePage} of {totalPages}
          </span>
          <button
            type="button"
            disabled={safePage === totalPages}
            onClick={() =>
              setPage((current) => Math.min(totalPages, current + 1))
            }
            className="rounded-full border border-slate-200 bg-white px-5 py-2.5 text-sm font-bold text-slate-700 transition hover:border-teal-700/30 hover:text-teal-800 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Next
          </button>
        </nav>
      )}
    </>
  );
}
