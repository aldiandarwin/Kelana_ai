import type { Metadata } from "next";
import Link from "next/link";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = {
  title: "About KelanaAI | Thoughtful Travel Planning",
  description: "AI itineraries, document-grounded travel answers, and private conversation history.",
};

const features = [
  { number: "01", title: "Start with a real plan", body: "Turn your destination, travel style, trip length, and budget into a day-by-day itinerary. Save it to your own dashboard." },
  { number: "02", title: "Ask with a source", body: "Use the Knowledge Assistant for travel questions grounded in our reference documents, including Bangladesh guides. Follow the cited sources to check the answer." },
  { number: "03", title: "Pick up where you left off", body: "Open Chat for a conversation that carries context across messages. Your history is saved to your account so you can return and continue planning." },
];

export default function AboutPage() {
  return (
    <div className="flex min-h-screen flex-col bg-[#f5f7f2] text-slate-950">
      <SiteHeader />
      <main className="flex-1">
        <section className="bg-[#083d42] text-white">
          <div className="mx-auto max-w-5xl px-5 py-16 sm:px-8 sm:py-24">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-amber-300">Meet your travel-planning companion</p>
            <h1 className="mt-4 max-w-3xl text-4xl font-semibold tracking-[-0.04em] sm:text-6xl">Less time piecing it together.<br />More room to explore.</h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-white/75">KelanaAI brings your itinerary, travel references, and planning conversations into one place. Built by Aldian Darwin Putra during the MAIN AI Native Software Engineer Bootcamp.</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/" className="rounded-full bg-amber-300 px-6 py-3 font-semibold text-teal-950 hover:bg-amber-200">Plan your next trip</Link>
              <a href="#how-it-works" className="rounded-full border border-white/30 px-6 py-3 font-semibold hover:bg-white/10">How it works</a>
            </div>
          </div>
        </section>
        <section id="how-it-works" className="mx-auto max-w-5xl px-5 py-14 sm:px-8">
          <h2 className="text-3xl font-semibold tracking-tight">Three ways to plan with confidence</h2>
          <div className="mt-8 grid gap-5 md:grid-cols-3">
            {features.map((feature) => (
              <article key={feature.number} className="rounded-3xl border border-slate-200 bg-white p-7">
                <span className="text-sm font-bold tracking-widest text-teal-700">{feature.number}</span>
                <h3 className="mt-5 text-xl font-semibold">{feature.title}</h3>
                <p className="mt-3 text-sm leading-7 text-slate-600">{feature.body}</p>
              </article>
            ))}
          </div>
        </section>
        <section className="mx-auto grid max-w-5xl gap-6 px-5 pb-16 sm:px-8 md:grid-cols-2">
          <div className="rounded-3xl bg-teal-50 p-8">
            <h2 className="text-2xl font-semibold text-teal-950">Built around the journey</h2>
            <p className="mt-4 text-sm leading-7 text-slate-700">Next.js serves the interface, FastAPI handles validation and account access, PostgreSQL stores trips and conversations, and Amazon Bedrock generates AI responses. The Knowledge Assistant retrieves document excerpts before answering; Chat reconstructs your conversation history for each response.</p>
            <a className="mt-5 inline-block font-semibold text-teal-800 underline underline-offset-4" href="https://github.com/aldiandarwin/Kelana_ai" target="_blank" rel="noreferrer">Explore the project on GitHub</a>
          </div>
          <div className="rounded-3xl border border-amber-200 bg-amber-50 p-8">
            <h2 className="text-2xl font-semibold text-amber-950">A helpful guide, not a guarantee</h2>
            <p className="mt-4 text-sm leading-7 text-slate-700">AI can make mistakes, and reference documents can become outdated. Confirm current travel rules, prices, opening hours, and safety advice with official sources before booking.</p>
            <p className="mt-4 text-sm leading-7 text-slate-700">Trips and conversations are saved to your account. Planning inputs and selected conversation history are sent to Amazon Bedrock to generate responses. Avoid sharing passport numbers, payment details, or other sensitive information.</p>
          </div>
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}
