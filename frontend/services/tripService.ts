import type {
  GeneratedTrip,
  Trip,
  TripRequest,
  TripUpdate,
} from "@/types/trip";

const API_URL = "/api/trips";

export class TripServiceError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = "TripServiceError";
  }
}

async function readError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as {
      detail?: string | Array<{ msg?: string }>;
    };
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail.map((item) => item.msg).filter(Boolean).join(". ");
    }
  } catch {
    // Fall through to the stable user-facing message.
  }
  return "The travel service could not complete this request.";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(API_URL + path, {
    ...init,
    credentials: "same-origin",
  });

  if (!response.ok) {
    const error = new TripServiceError(await readError(response), response.status);
    if (response.status === 401 && typeof window !== "undefined") {
      window.dispatchEvent(new Event("kelana:unauthorized"));
    }
    throw error;
  }

  return (await response.json()) as T;
}

export function getTrips(): Promise<Trip[]> {
  return request<Trip[]>("", { cache: "no-store" });
}

export function getTrip(id: number): Promise<Trip> {
  return request<Trip>("/" + id, { cache: "no-store" });
}

export function createTrip(data: TripRequest): Promise<Trip> {
  return request<Trip>("", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function generateTripRecommendation(id: number): Promise<GeneratedTrip> {
  return request<GeneratedTrip>("/" + id + "/generate", {
    method: "POST",
  });
}

export function updateTrip(id: number, data: TripUpdate): Promise<Trip> {
  return request<Trip>("/" + id, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function deleteTrip(
  id: number,
): Promise<{ deleted_id: number; status: string }> {
  return request("/" + id, { method: "DELETE" });
}

export function getRequestFailureMessage(error: unknown): string {
  if (error instanceof TripServiceError) return error.message;

  if (error instanceof TypeError) {
    return "We couldn't connect to the travel service. Please try again in a moment.";
  }

  return error instanceof Error
    ? error.message
    : "Unable to complete this request. Please try again.";
}
