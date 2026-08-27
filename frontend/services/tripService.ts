import type { GeneratedTrip, Trip, TripRequest } from "@/types/trip";

const API_URL = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1"
).replace(/\/+$/, "");

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
    const body = (await response.json()) as { detail?: string };
    return body.detail ?? "The travel service could not complete this request.";
  } catch {
    return "The travel service could not complete this request.";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(API_URL + path, init);

  if (!response.ok) {
    throw new TripServiceError(await readError(response), response.status);
  }

  return (await response.json()) as T;
}

export function getTrips(): Promise<Trip[]> {
  return request<Trip[]>("/trips", { cache: "no-store" });
}

export function getTrip(id: number): Promise<Trip> {
  return request<Trip>("/trips/" + id, { cache: "no-store" });
}

export function createTrip(data: TripRequest): Promise<Trip> {
  return request<Trip>("/trips", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function generateTripRecommendation(id: number): Promise<GeneratedTrip> {
  return request<GeneratedTrip>("/trips/" + id + "/generate", {
    method: "POST",
  });
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
