import { cookies } from "next/headers";

import {
  AUTH_COOKIE_NAME,
  BACKEND_API_URL,
  relayBackendResponse,
} from "@/lib/apiProxy";

type RouteContext = {
  params: Promise<{ path?: string[] }>;
};

async function forward(request: Request, context: RouteContext) {
  const token = (await cookies()).get(AUTH_COOKIE_NAME)?.value;
  if (!token) {
    return Response.json({ detail: "Authentication required" }, { status: 401 });
  }

  const { path = [] } = await context.params;
  const suffix = path.length
    ? "/" + path.map((segment) => encodeURIComponent(segment)).join("/")
    : "";
  const requestUrl = new URL(request.url);
  const headers = new Headers({ Authorization: "Bearer " + token });
  const contentType = request.headers.get("content-type");
  if (contentType) headers.set("Content-Type", contentType);

  const body = request.method === "GET" ? undefined : await request.text();
  const backendResponse = await fetch(
    BACKEND_API_URL + "/trips" + suffix + requestUrl.search,
    {
      method: request.method,
      headers,
      body: body || undefined,
      cache: "no-store",
    },
  );

  return relayBackendResponse(backendResponse);
}

export const GET = forward;
export const POST = forward;
export const PUT = forward;
export const DELETE = forward;
