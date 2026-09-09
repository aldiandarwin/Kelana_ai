import Link from "next/link";

function PlaneIcon() {
  return (
    <svg
      aria-hidden="true"
      className="size-5"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth="1.8"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M6 15.75 4.5 18l1.5.75 3-1.5 3 3v1.5l1.5.75 1.5-3-1.5-4.5 3.75-3.75c1.5-1.5 2.25-3.75 1.5-4.5s-3 0-4.5 1.5L10.5 12 6 10.5l-3 1.5.75 1.5h1.5l3 3-1.5 3Z"
      />
    </svg>
  );
}

export function SiteFooter() {
  return (
    <footer className="border-t border-white/10 bg-[#072e33] text-white">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 px-5 py-9 sm:flex-row sm:items-center sm:justify-between sm:px-8 lg:px-10">
        <div>
          <div className="flex items-center gap-2 font-semibold">
            <PlaneIcon /> KelanaAI
          </div>
          <p className="mt-2 text-sm text-white/55">
            © 2026 KelanaAI. Built for MAIN AI Native Software Engineer Bootcamp.
          </p>
        </div>
        <div className="flex flex-wrap gap-x-6 gap-y-3 text-sm font-medium text-white/65">
          <Link className="transition hover:text-white" href="/about">About KelanaAI</Link>
          <Link className="transition hover:text-white" href="/">
            Home
          </Link>
          <Link className="transition hover:text-white" href="/#planner">
            Plan a trip
          </Link>
          <Link className="transition hover:text-white" href="/assistant">
            Assistant
          </Link>
          <Link className="transition hover:text-white" href="/chat">
            Chat
          </Link>
          <Link className="transition hover:text-white" href="/trips">
            My trips
          </Link>
          <Link className="transition hover:text-white" href="/profile">
            Profile
          </Link>
          <Link className="transition hover:text-white" href="/#how-it-works">
            How it works
          </Link>
        </div>
      </div>
    </footer>
  );
}
