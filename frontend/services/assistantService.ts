import type { AssistantAnswer, AssistantRequest } from "@/types/assistant";

export class AssistantServiceError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = "AssistantServiceError";
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
  return "Unable to reach the KelanaAI knowledge base. Please try again.";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch("/api/assistant" + path, {
    ...init,
    credentials: "same-origin",
  });

  if (!response.ok) {
    const error = new AssistantServiceError(await readError(response), response.status);
    if (response.status === 401 && typeof window !== "undefined") {
      window.dispatchEvent(new Event("kelana:unauthorized"));
    }
    throw error;
  }

  return (await response.json()) as T;
}

export function askAssistant(data: AssistantRequest): Promise<AssistantAnswer> {
  return request<AssistantAnswer>("", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export function getAssistantFailureMessage(error: unknown): string {
  if (error instanceof AssistantServiceError) return error.message;
  if (error instanceof TypeError) {
    return "We couldn't connect to KelanaAI. Please try again in a moment.";
  }
  return error instanceof Error
    ? error.message
    : "Unable to reach the KelanaAI knowledge base. Please try again.";
}
