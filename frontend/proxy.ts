import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { AUTH_COOKIE_NAME } from "@/lib/apiProxy";

const AUTH_ROUTES = new Set(["/login", "/register"]);

export function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  const hasToken = request.cookies.has(AUTH_COOKIE_NAME);

  if (!hasToken && !AUTH_ROUTES.has(pathname)) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname + search);
    return NextResponse.redirect(loginUrl);
  }

  if (hasToken && AUTH_ROUTES.has(pathname)) {
    return NextResponse.redirect(new URL("/trips", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/",
    "/trips/:path*",
    "/assistant/:path*",
    "/chat/:path*",
    "/profile/:path*",
    "/login",
    "/register",
  ],
};
