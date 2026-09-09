export default function Loading() {
  return (
    <main aria-busy="true" className="grid min-h-[70vh] place-items-center bg-[#f5f7f2] px-5 py-16">
      <div role="status" aria-live="polite" className="text-center">
        <div aria-hidden="true" className="mx-auto size-12 animate-spin rounded-full border-4 border-teal-100 border-t-teal-700 motion-reduce:animate-none" />
        <h1 className="mt-6 text-2xl font-semibold text-teal-950">Getting your next stop ready</h1>
        <p className="mt-3 text-sm text-slate-600">Loading KelanaAI. Thanks for your patience.</p>
      </div>
    </main>
  );
}
