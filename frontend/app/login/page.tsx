import Link from "next/link";

import { AuthShell } from "@/components/AuthShell";
import { LoginForm } from "@/components/LoginForm";

type LoginSearchParams = Promise<{
  registered?: string;
  email?: string;
  next?: string;
}>;

export default async function LoginPage({
  searchParams,
}: {
  searchParams: LoginSearchParams;
}) {
  const query = await searchParams;
  const requestedPath = query.next;
  const nextPath =
    requestedPath?.startsWith("/") && !requestedPath.startsWith("//")
      ? requestedPath
      : "/trips";

  return (
    <AuthShell
      eyebrow="Welcome back"
      title="Continue your journey."
      description="Sign in to generate new itineraries and revisit only the trips that belong to you."
      footer={
        <>
          New to KelanaAI?{" "}
          <Link href="/register" className="font-bold text-teal-800 hover:text-teal-700">
            Create an account
          </Link>
        </>
      }
    >
      <LoginForm
        initialEmail={query.email ?? ""}
        registered={query.registered === "1"}
        nextPath={nextPath}
      />
    </AuthShell>
  );
}
