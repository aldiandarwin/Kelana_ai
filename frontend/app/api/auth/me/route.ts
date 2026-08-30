import { cookies } from "next/headers";

import {
  AUTH_COOKIE_NAME,
  BACKEND_API_URL,
  relayBackendResponse,
} from "@/lib/apiProxy";

export async function GET() {
  const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value;
  if (!token) {
    return Response.json({ detail: "Authentication required" }, { status: 401 });
  }

  const backendResponse = await fetch(BACKEND_API_URL + "/auth/me", {
    headers: { Authorization: "Bearer " + token },
    cache: "no-store",
  });
  return relayBackendResponse(backendResponse);
}
