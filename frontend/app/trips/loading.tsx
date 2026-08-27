import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export default function TripsLoading() {
  return (
    <div className="flex min-h-screen flex-col bg-[#f5f7f2]">
      <SiteHeader />
      <main className="flex-1">
        <div className="h-64 animate-pulse bg-[#083d42]" />
        <div className="mx-auto grid max-w-7xl gap-5 px-5 py-10 sm:px-8 md:grid-cols-2 lg:px-10 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <div
              key={index}
              className="h-80 animate-pulse rounded-3xl border border-slate-200 bg-white"
            />
          ))}
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
