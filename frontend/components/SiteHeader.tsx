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

export function SiteHeader({ overlay = false }: { overlay?: boolean }) {
  const linkColor = overlay
    ? "text-white/85 hover:text-white"
    : "text-slate-600 hover:text-teal-800";

  return (
    <header
      className={
        overlay
          ? "absolute inset-x-0 top-0 z-20"
          : "sticky inset-x-0 top-0 z-30 border-b border-slate-200/80 bg-white/90 backdrop-blur-xl"
      }
    >
      <nav
        aria-label="Primary navigation"
        className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-8 lg:px-10"
      >
        <Link
          href="/"
          className={
            "flex items-center gap-2 " +
            (overlay ? "text-white" : "text-teal-950")
          }
        >
          <span
            className={
              "grid size-10 place-items-center rounded-full " +
              (overlay ? "bg-white/15 backdrop-blur-md" : "bg-teal-100")
            }
          >
            <PlaneIcon />
          </span>
          <span className="text-lg font-semibold tracking-tight">KelanaAI</span>
        </Link>

        <div className="flex items-center gap-4 text-sm font-semibold sm:gap-7">
          <Link
            className={"hidden transition sm:inline " + linkColor}
            href="/"
          >
            Home
          </Link>
          <Link
            className={"hidden transition md:inline " + linkColor}
            href="/#planner"
          >
            Plan a trip
          </Link>
          <Link
            href="/trips"
            className={
              "rounded-full px-4 py-2.5 transition " +
              (overlay
                ? "border border-white/30 bg-white/10 text-white hover:bg-white/20"
                : "bg-teal-800 text-white hover:bg-teal-700")
            }
          >
            My trips
          </Link>
        </div>
      </nav>
    </header>
  );
}
