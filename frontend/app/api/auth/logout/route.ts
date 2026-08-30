import { NextResponse } from "next/server";

import { AUTH_COOKIE_NAME, authCookieOptions } from "@/lib/apiProxy";

export async function POST() {
  const response = NextResponse.json({ authenticated: false });
  response.cookies.set(AUTH_COOKIE_NAME, "", {
    ...authCookieOptions(),
    maxAge: 0,
  });
  return response;
}
