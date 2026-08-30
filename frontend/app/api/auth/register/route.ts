import { BACKEND_API_URL, relayBackendResponse } from "@/lib/apiProxy";

export async function POST(request: Request) {
  const backendResponse = await fetch(BACKEND_API_URL + "/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: await request.text(),
    cache: "no-store",
  });

  return relayBackendResponse(backendResponse);
}
