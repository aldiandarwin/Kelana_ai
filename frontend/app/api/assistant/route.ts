import { cookies } from "next/headers";

import {
  AUTH_COOKIE_NAME,
  BACKEND_API_URL,
  relayBackendResponse,
} from "@/lib/apiProxy";

export async function POST(request: Request) {
  const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value;
  if (!token) {
    return Response.json({ detail: "Authentication required" }, { status: 401 });
  }

  const headers = new Headers({ Authorization: "Bearer " + token });
  const contentType = request.headers.get("content-type");
  if (contentType) headers.set("Content-Type", contentType);

  const backendResponse = await fetch(BACKEND_API_URL + "/assistant", {
    method: "POST",
    headers,
    body: await request.text(),
    cache: "no-store",
  });
  return relayBackendResponse(backendResponse);
}
