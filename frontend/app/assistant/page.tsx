"use client";

import { FormEvent, useState } from "react";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import {
  askAssistant,
  getAssistantFailureMessage,
} from "@/services/assistantService";
import type { AssistantAnswer } from "@/types/assistant";

const inputClasses =
  "min-h-13 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 text-base font-medium text-slate-950 outline-none transition placeholder:text-slate-400 focus:border-teal-600 focus:bg-white focus:ring-4 focus:ring-teal-600/10";

const SAMPLE_QUESTIONS = [
  "How far is Khagrachari from Chattogram, and which rivers pass through it?",
  "What does the handbook say about Saint Martin's Island and Cheera-Dwip?",
  "Whose permission is needed before entering the Sundarbans through Karamjal?",
  "What is Kachikhali's other name and how long is the river journey from Khulna?",
];

export default function AssistantPage() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AssistantAnswer | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function ask(text: string) {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      setResult(await askAssistant({ question: text }));
    } catch (requestError) {
      setError(getAssistantFailureMessage(requestError));
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await ask(question);
  }

  async function handleSample(sample: string) {
    setQuestion(sample);
    await ask(sample);
  }

  return (
    <div className="flex min-h-screen flex-col bg-[#f5f7f2] text-slate-950">
      <SiteHeader />

      <main className="flex-1">
        <section className="overflow-hidden bg-[#083d42] text-white">
          <div className="mx-auto max-w-7xl px-5 py-14 sm:px-8 sm:py-18 lg:px-10">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-amber-300">
              Grounded in your travel documents
            </p>
            <h1 className="mt-3 text-4xl font-semibold tracking-[-0.04em] sm:text-5xl">
              Ask KelanaAI
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-white/70">
              Every answer here is retrieved from the KelanaAI knowledge base before it is
              written. When the documents do not cover your question, KelanaAI says so
              instead of guessing.
            </p>
          </div>
        </section>

        <section className="mx-auto max-w-4xl px-5 py-10 sm:px-8 sm:py-14 lg:px-10">
          <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
            <form onSubmit={handleSubmit} className="grid gap-5">
              <label className="grid gap-2 text-sm font-semibold text-slate-700">
                Your travel question
                <input
                  required
                  minLength={3}
                  maxLength={500}
                  type="text"
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="Can I bring medication into Japan?"
                  className={inputClasses}
                />
              </label>

              <button
                type="submit"
                disabled={loading}
                className="inline-flex min-h-13 items-center justify-center gap-3 rounded-full bg-teal-800 px-6 text-sm font-bold text-white shadow-lg shadow-teal-900/15 transition hover:bg-teal-700 disabled:cursor-wait disabled:opacity-65"
              >
                {loading ? "Searching your documents..." : "Ask KelanaAI"}
                {loading && (
                  <span className="size-5 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                )}
              </button>
            </form>

            <div className="mt-6 border-t border-slate-100 pt-5">
              <p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">
                Try one of these
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {SAMPLE_QUESTIONS.map((sample) => (
                  <button
                    key={sample}
                    type="button"
                    disabled={loading}
                    onClick={() => void handleSample(sample)}
                    className="rounded-full border border-slate-200 bg-white px-4 py-2 text-left text-xs font-semibold text-slate-600 transition hover:border-teal-700/30 hover:text-teal-800 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    {sample}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {loading && (
            <div
              aria-live="polite"
              className="mt-8 grid min-h-48 place-items-center rounded-[2rem] border border-slate-200 bg-white text-center shadow-sm"
            >
              <div>
                <span className="mx-auto block size-10 animate-spin rounded-full border-[3px] border-teal-800/20 border-t-teal-800" />
                <p className="mt-5 font-semibold text-teal-950">
                  Retrieving passages, then writing the answer
                </p>
              </div>
            </div>
          )}

          {!loading && error && (
            <div
              role="alert"
              className="mt-8 rounded-[2rem] border border-rose-200 bg-rose-50 p-8 text-center"
            >
              <h2 className="text-xl font-semibold text-rose-950">
                Unable to answer that question
              </h2>
              <p className="mt-3 text-sm text-rose-800">{error}</p>
            </div>
          )}

          {!loading && !error && result && (
            <article className="mt-8 rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-teal-700">
                  {result.grounded ? "Grounded answer" : "No matching document"}
                </p>
                <span className="rounded-full border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-500">
                  {result.mode}
                </span>
              </div>

              <h2 className="mt-3 text-2xl font-semibold tracking-[-0.03em]">
                {result.question}
              </h2>

              <div className="mt-5 grid gap-4 text-base leading-7 text-slate-700">
                {result.answer
                  .split("\n")
                  .map((line) => line.trim())
                  .filter(Boolean)
                  .map((line, index) => (
                    <p key={index}>{line}</p>
                  ))}
              </div>

              {result.sources.length > 0 ? (
                <div className="mt-7 rounded-2xl border border-slate-200 bg-slate-50 p-5">
                  <p className="text-xs font-bold uppercase tracking-[0.12em] text-slate-400">
                    Sources
                  </p>
                  <ul className="mt-3 grid gap-3">
                    {result.sources.map((source, index) => (
                      <li key={source.document + index}>
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="font-mono text-sm font-semibold text-teal-800">
                            {source.document}
                          </span>
                          {source.score !== null && (
                            <span className="rounded-full border border-slate-200 bg-white px-2.5 py-0.5 text-xs font-semibold text-slate-500">
                              match {source.score}
                            </span>
                          )}
                        </div>
                        <p className="mt-1 line-clamp-3 text-sm leading-6 text-slate-500">
                          {source.excerpt}
                        </p>
                      </li>
                    ))}
                  </ul>
                  <p className="mt-4 text-xs leading-5 text-slate-400">
                    Open the file in <span className="font-mono">knowledge/</span> to
                    verify the answer against the original document.
                  </p>
                </div>
              ) : (
                <p className="mt-7 rounded-2xl border border-dashed border-teal-700/25 bg-white px-5 py-6 text-sm leading-6 text-slate-500">
                  Nothing in the knowledge base scored high enough to answer this. Add a
                  document that covers it, run the ingestion script, and ask again.
                </p>
              )}
            </article>
          )}
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
