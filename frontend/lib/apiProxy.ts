import { NextResponse } from "next/server";

export const AUTH_COOKIE_NAME = "kelana_access_token";

export const BACKEND_API_URL = (
  process.env.API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000/api/v1"
).replace(/\/+$/, "");

export function authCookieOptions(maxAge?: number) {
  return {
    httpOnly: true,
    sameSite: "lax" as const,
    secure: process.env.NODE_ENV === "production",
    path: "/",
    ...(maxAge ? { maxAge } : {}),
  };
}

export async function relayBackendResponse(
  backendResponse: Response,
  clearAuthCookie = false,
): Promise<NextResponse> {
  const response = new NextResponse(await backendResponse.arrayBuffer(), {
    status: backendResponse.status,
    headers: {
      "Content-Type":
        backendResponse.headers.get("content-type") ?? "application/json",
    },
  });

  if (clearAuthCookie || backendResponse.status === 401) {
    response.cookies.set(AUTH_COOKIE_NAME, "", {
      ...authCookieOptions(),
      maxAge: 0,
    });
  }

  return response;
}
