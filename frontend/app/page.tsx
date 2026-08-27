"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { ItineraryContent } from "@/components/ItineraryContent";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import {
  createTrip,
  generateTripRecommendation,
  getRequestFailureMessage,
} from "@/services/tripService";
import type { Trip } from "@/types/trip";

function ArrowIcon() {
  return (
    <svg
      aria-hidden="true"
      className="size-5 transition-transform duration-200 group-hover:translate-x-1"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth="2"
    >
      <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14m-6-6 6 6-6 6" />
    </svg>
  );
}

export default function Home() {
  const router = useRouter();
  const [destination, setDestination] = useState("Labuan Bajo");
  const [days, setDays] = useState("5");
  const [budget, setBudget] = useState("2000");
  const [travelStyle, setTravelStyle] = useState("Family");
  const [trip, setTrip] = useState<Trip | null>(null);
  const [recommendation, setRecommendation] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function generateRecommendation(tripId: number) {
    const result = await generateTripRecommendation(tripId);
    setRecommendation(result.recommendation);
    router.push("/trips");
  }

  async function createTripAndGenerate() {
    setLoading(true);
    setError("");
    setRecommendation("");
    setTrip(null);

    try {
      const createdTrip = await createTrip({
        destination,
        days: Number(days),
        budget: Number(budget),
        travel_style: travelStyle,
      });
      setTrip(createdTrip);
      await generateRecommendation(createdTrip.id);
    } catch (requestError) {
      setError(getRequestFailureMessage(requestError));
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await createTripAndGenerate();
  }

  async function handleRetry() {
    setLoading(true);
    setError("");

    try {
      if (trip) {
        await generateRecommendation(trip.id);
      } else {
        await createTripAndGenerate();
      }
    } catch (requestError) {
      setError(getRequestFailureMessage(requestError));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#f5f7f2] text-slate-950">
      <SiteHeader overlay />

      <main id="top">
        <section className="relative isolate min-h-[660px] overflow-hidden sm:min-h-[720px]">
          <Image
            src="/destination-hero.png"
            alt="Tropical Indonesian islands surrounded by turquoise water at sunrise"
            fill
            priority
            sizes="100vw"
            className="object-cover object-center"
          />
          <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(4,28,35,0.86)_0%,rgba(4,28,35,0.58)_48%,rgba(4,28,35,0.16)_100%)]" />
          <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(4,20,25,0.32)_0%,transparent_35%,rgba(4,20,25,0.5)_100%)]" />

          <div className="relative mx-auto flex min-h-[660px] max-w-7xl items-center px-5 pb-36 pt-32 sm:min-h-[720px] sm:px-8 sm:pb-44 lg:px-10">
            <div className="max-w-3xl text-white">
              <span className="inline-flex items-center gap-2 rounded-full border border-white/25 bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] backdrop-blur-md sm:text-sm">
                <span className="size-2 rounded-full bg-amber-300" />
                Your AI travel planner
              </span>
              <h1 className="mt-6 max-w-3xl text-5xl font-semibold leading-[0.98] tracking-[-0.045em] sm:text-6xl lg:text-7xl">
                Go further. Plan smarter.
              </h1>
              <p className="mt-6 max-w-xl text-base leading-7 text-white/80 sm:text-lg sm:leading-8">
                Turn one travel idea into a thoughtful day-by-day itinerary,
                shaped around your budget and the way you love to explore.
              </p>
              <div className="mt-8 flex flex-wrap gap-x-6 gap-y-3 text-sm text-white/80">
                <span className="flex items-center gap-2">
                  <span className="text-amber-300">✦</span> Tailored by Amazon Bedrock
                </span>
                <span className="flex items-center gap-2">
                  <span className="text-amber-300">✦</span> Ready in moments
                </span>
              </div>
            </div>
          </div>
        </section>

        <section
          id="planner"
          className="relative z-10 mx-auto -mt-24 max-w-7xl scroll-mt-6 px-5 sm:-mt-28 sm:px-8 lg:px-10"
        >
          <div className="overflow-hidden rounded-[2rem] border border-white/70 bg-white shadow-[0_32px_80px_-32px_rgba(15,23,42,0.38)]">
            <div className="border-b border-slate-100 px-6 py-6 sm:px-8">
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-teal-700">
                Start your journey
              </p>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950 sm:text-3xl">
                Where would you like to go?
              </h2>
            </div>

            <form onSubmit={handleSubmit} className="p-6 sm:p-8">
              <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
                <label className="grid gap-2 text-sm font-semibold text-slate-700">
                  Destination
                  <input
                    required
                    name="destination"
                    value={destination}
                    onChange={(event) => setDestination(event.target.value)}
                    className="min-h-13 rounded-xl border border-slate-200 bg-slate-50 px-4 text-base font-medium text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-teal-600 focus:bg-white focus:ring-4 focus:ring-teal-600/10"
                    placeholder="e.g. Labuan Bajo"
                  />
                </label>

                <label className="grid gap-2 text-sm font-semibold text-slate-700">
                  Days
                  <input
                    required
                    min="1"
                    name="days"
                    type="number"
                    value={days}
                    onChange={(event) => setDays(event.target.value)}
                    className="min-h-13 rounded-xl border border-slate-200 bg-slate-50 px-4 text-base font-medium text-slate-950 outline-none transition focus:border-teal-600 focus:bg-white focus:ring-4 focus:ring-teal-600/10"
                  />
                </label>

                <label className="grid gap-2 text-sm font-semibold text-slate-700">
                  Total budget (USD)
                  <input
                    required
                    min="1"
                    name="budget"
                    type="number"
                    value={budget}
                    onChange={(event) => setBudget(event.target.value)}
                    className="min-h-13 rounded-xl border border-slate-200 bg-slate-50 px-4 text-base font-medium text-slate-950 outline-none transition focus:border-teal-600 focus:bg-white focus:ring-4 focus:ring-teal-600/10"
                  />
                </label>

                <label className="grid gap-2 text-sm font-semibold text-slate-700">
                  Travel style
                  <select
                    name="travel_style"
                    value={travelStyle}
                    onChange={(event) => setTravelStyle(event.target.value)}
                    className="min-h-13 rounded-xl border border-slate-200 bg-slate-50 px-4 text-base font-medium text-slate-950 outline-none transition focus:border-teal-600 focus:bg-white focus:ring-4 focus:ring-teal-600/10"
                  >
                    <option>Family</option>
                    <option>Solo</option>
                    <option>Couple</option>
                  </select>
                </label>
              </div>

              <div className="mt-7 flex flex-col gap-4 border-t border-slate-100 pt-6 sm:flex-row sm:items-center sm:justify-between">
                <p className="max-w-xl text-sm leading-6 text-slate-500">
                  Your destination, trip length, budget, and travel style stay
                  at the center of every plan.
                </p>
                <button
                  type="submit"
                  disabled={loading}
                  className="group inline-flex min-h-13 shrink-0 items-center justify-center gap-3 rounded-full bg-teal-800 px-6 text-sm font-bold text-white shadow-lg shadow-teal-900/15 transition hover:bg-teal-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700 disabled:cursor-wait disabled:opacity-70"
                >
                  {loading ? "Designing your trip..." : "Generate my itinerary"}
                  {loading ? (
                    <span className="size-5 animate-spin rounded-full border-2 border-white/35 border-t-white" />
                  ) : (
                    <ArrowIcon />
                  )}
                </button>
              </div>
            </form>
          </div>
        </section>

        <section
          id="how-it-works"
          className="mx-auto max-w-7xl scroll-mt-8 px-5 py-20 sm:px-8 sm:py-24 lg:px-10"
        >
          {loading && (
            <div
              aria-live="polite"
              className="grid min-h-72 place-items-center rounded-[2rem] border border-teal-900/10 bg-[#e7f0eb] px-6 text-center"
            >
              <div>
                <span className="mx-auto block size-11 animate-spin rounded-full border-[3px] border-teal-800/20 border-t-teal-800" />
                <p className="mt-5 text-lg font-semibold text-teal-950">
                  KelanaAI is planning your trip
                </p>
                <p className="mt-2 text-sm text-teal-900/65">
                  Building a {days}-day itinerary for {destination}.
                </p>
              </div>
            </div>
          )}

          {!loading && error && (
            <div
              role="alert"
              className="rounded-[2rem] border border-rose-200 bg-rose-50 p-7 sm:flex sm:items-center sm:justify-between sm:gap-8 sm:p-10"
            >
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-rose-700">
                  We hit some turbulence
                </p>
                <h2 className="mt-2 text-2xl font-semibold tracking-tight text-rose-950">
                  Unable to generate your itinerary
                </h2>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-rose-900/70">
                  {error}
                </p>
              </div>
              <button
                type="button"
                onClick={handleRetry}
                className="mt-6 inline-flex min-h-12 items-center justify-center rounded-full bg-rose-900 px-6 text-sm font-bold text-white transition hover:bg-rose-800 sm:mt-0"
              >
                Try again
              </button>
            </div>
          )}

          {!loading && recommendation && trip && (
            <div aria-live="polite">
              <div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.2em] text-teal-700">
                    Your AI itinerary
                  </p>
                  <h2 className="mt-2 text-3xl font-semibold tracking-[-0.035em] text-slate-950 sm:text-4xl">
                    {trip.destination}, thoughtfully planned
                  </h2>
                </div>
                <div className="flex flex-wrap gap-2 text-xs font-semibold text-slate-600">
                  <span className="rounded-full border border-slate-200 bg-white px-4 py-2">
                    {trip.days} days
                  </span>
                  <span className="rounded-full border border-slate-200 bg-white px-4 py-2">
                    USD {trip.budget.toLocaleString()}
                  </span>
                  <span className="rounded-full border border-slate-200 bg-white px-4 py-2">
                    {trip.category} budget
                  </span>
                </div>
              </div>

              <div className="mt-9">
                <ItineraryContent recommendation={recommendation} />
              </div>
            </div>
          )}

          {!loading && !error && !recommendation && (
            <div className="grid gap-8 lg:grid-cols-[0.85fr_1.15fr] lg:items-center">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-teal-700">
                  Simple by design
                </p>
                <h2 className="mt-3 text-3xl font-semibold tracking-[-0.035em] text-slate-950 sm:text-4xl">
                  From one idea to a trip you can picture.
                </h2>
                <p className="mt-5 max-w-lg text-base leading-7 text-slate-600">
                  Tell us where you want to go, how long you have, your budget,
                  and travel style. KelanaAI turns those details into a
                  practical day-by-day itinerary.
                </p>
              </div>
              <ol className="grid gap-4 sm:grid-cols-3">
                {[
                  ["01", "Share your idea", "Choose a destination, duration, budget, and style."],
                  ["02", "AI shapes the plan", "KelanaAI turns your preferences into a practical route."],
                  ["03", "Explore your itinerary", "Review daily activities, food ideas, transport, and tips."],
                ].map(([number, title, copy]) => (
                  <li
                    key={number}
                    className="rounded-3xl border border-slate-200/80 bg-white p-6 shadow-sm"
                  >
                    <span className="text-sm font-bold text-teal-700">{number}</span>
                    <h3 className="mt-4 font-semibold text-slate-950">{title}</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-500">{copy}</p>
                  </li>
                ))}
              </ol>
            </div>
          )}
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
