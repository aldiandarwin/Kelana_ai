import Image from "next/image";
import Link from "next/link";

export function AuthShell({
  eyebrow,
  title,
  description,
  children,
  footer,
}: {
  eyebrow: string;
  title: string;
  description: string;
  children: React.ReactNode;
  footer: React.ReactNode;
}) {
  return (
    <main className="grid min-h-screen bg-[#f5f7f2] text-slate-950 lg:grid-cols-[1.05fr_0.95fr]">
      <section className="relative hidden min-h-screen overflow-hidden lg:block">
        <Image
          src="/destination-hero.png"
          alt="Indonesian islands surrounded by turquoise water"
          fill
          priority
          sizes="55vw"
          className="object-cover"
        />
        <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(4,28,35,0.35),rgba(4,28,35,0.88))]" />
        <div className="relative flex min-h-screen flex-col justify-between p-12 text-white xl:p-16">
          <Link href="/login" className="flex w-fit items-center gap-3 text-xl font-semibold">
            <span className="grid size-11 place-items-center rounded-full bg-white/15 backdrop-blur">
              ✦
            </span>
            KelanaAI
          </Link>
          <div className="max-w-xl">
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-amber-300">
              Your private travel workspace
            </p>
            <h2 className="mt-5 text-5xl font-semibold leading-tight tracking-[-0.045em]">
              Your ideas, itineraries, and memories stay yours.
            </h2>
            <div className="mt-8 flex flex-wrap gap-3 text-sm text-white/75">
              {[
                "Secure JWT access",
                "Private trip history",
                "AI plans by Amazon Bedrock",
              ].map((item) => (
                <span key={item} className="rounded-full border border-white/20 bg-white/10 px-4 py-2 backdrop-blur">
                  {item}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="flex min-h-screen items-center justify-center px-5 py-10 sm:px-8 lg:px-12">
        <div className="w-full max-w-md">
          <Link href="/login" className="mb-10 flex items-center gap-3 text-lg font-semibold text-teal-950 lg:hidden">
            <span className="grid size-10 place-items-center rounded-full bg-teal-100 text-teal-800">✦</span>
            KelanaAI
          </Link>
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-teal-700">{eyebrow}</p>
          <h1 className="mt-3 text-4xl font-semibold tracking-[-0.04em] sm:text-5xl">{title}</h1>
          <p className="mt-4 text-base leading-7 text-slate-500">{description}</p>
          <div className="mt-8">{children}</div>
          <div className="mt-7 text-center text-sm text-slate-500">{footer}</div>
        </div>
      </section>
    </main>
  );
}
