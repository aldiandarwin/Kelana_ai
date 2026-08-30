import { NextResponse } from "next/server";

import {
  AUTH_COOKIE_NAME,
  BACKEND_API_URL,
  authCookieOptions,
  relayBackendResponse,
} from "@/lib/apiProxy";

type LoginResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
};

export async function POST(request: Request) {
  const backendResponse = await fetch(BACKEND_API_URL + "/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: await request.text(),
    cache: "no-store",
  });

  if (!backendResponse.ok) return relayBackendResponse(backendResponse);

  const payload = (await backendResponse.json()) as LoginResponse;
  const response = NextResponse.json({ authenticated: true });
  response.cookies.set(
    AUTH_COOKIE_NAME,
    payload.access_token,
    authCookieOptions(payload.expires_in),
  );
  return response;
}
