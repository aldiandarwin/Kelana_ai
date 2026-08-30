import type { LoginInput, RegisterInput, User } from "@/types/auth";

export class AuthServiceError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = "AuthServiceError";
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
  return "Unable to complete authentication. Please try again.";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch("/api/auth" + path, {
    ...init,
    credentials: "same-origin",
  });
  if (!response.ok) {
    throw new AuthServiceError(await readError(response), response.status);
  }
  return (await response.json()) as T;
}

export function register(data: RegisterInput): Promise<Omit<User, "total_trips">> {
  return request("/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function login(data: LoginInput): Promise<{ authenticated: boolean }> {
  return request("/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function getCurrentUser(): Promise<User> {
  return request<User>("/me", { cache: "no-store" });
}

export function logout(): Promise<{ authenticated: boolean }> {
  return request("/logout", { method: "POST" });
}

export function getAuthFailureMessage(error: unknown): string {
  if (error instanceof AuthServiceError) return error.message;
  if (error instanceof TypeError) {
    return "We couldn't connect to KelanaAI. Please try again in a moment.";
  }
  return error instanceof Error
    ? error.message
    : "Unable to complete authentication. Please try again.";
}
