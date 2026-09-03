import type {
  ConversationCreateResponse,
  ConversationDetail,
  ConversationSummary,
  ConversationTurn,
} from "@/types/conversation";

export class ConversationServiceError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = "ConversationServiceError";
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
  return "KelanaAI could not load this conversation. Please try again.";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch("/api/conversations" + path, {
    ...init,
    credentials: "same-origin",
  });

  if (!response.ok) {
    const error = new ConversationServiceError(
      await readError(response),
      response.status,
    );
    if (response.status === 401 && typeof window !== "undefined") {
      window.dispatchEvent(new Event("kelana:unauthorized"));
    }
    throw error;
  }

  return (await response.json()) as T;
}

export function listConversations(): Promise<ConversationSummary[]> {
  return request<ConversationSummary[]>("");
}

export function createConversation(
  title?: string,
): Promise<ConversationCreateResponse> {
  return request<ConversationCreateResponse>("", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: title ? JSON.stringify({ title }) : undefined,
  });
}

export function getConversation(id: number): Promise<ConversationDetail> {
  return request<ConversationDetail>(`/${id}/messages`);
}

export function sendConversationMessage(
  id: number,
  content: string,
): Promise<ConversationTurn> {
  return request<ConversationTurn>(`/${id}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
}

export function renameConversation(
  id: number,
  title: string,
): Promise<ConversationSummary> {
  return request<ConversationSummary>(`/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
}

export function getConversationFailureMessage(error: unknown): string {
  if (error instanceof ConversationServiceError) return error.message;
  if (error instanceof TypeError) {
    return "We couldn't connect to KelanaAI. Please try again in a moment.";
  }
  return error instanceof Error
    ? error.message
    : "KelanaAI could not continue this conversation.";
}
