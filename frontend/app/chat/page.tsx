"use client";

import {
  FormEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import {
  createConversation,
  getConversation,
  getConversationFailureMessage,
  listConversations,
  renameConversation,
  sendConversationMessage,
} from "@/services/conversationService";
import type {
  ConversationMessage,
  ConversationSummary,
} from "@/types/conversation";

const timestampFormatter = new Intl.DateTimeFormat("en", {
  hour: "2-digit",
  minute: "2-digit",
});

function formatTimestamp(value: string) {
  return timestampFormatter.format(new Date(value));
}

function InlineMarkdown({ text }: { text: string }) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((part, index) =>
    part.startsWith("**") && part.endsWith("**") ? (
      <strong key={index} className="font-bold">
        {part.slice(2, -2)}
      </strong>
    ) : (
      <span key={index}>{part}</span>
    ),
  );
}

function MessageBody({ content }: { content: string }) {
  const lines = content
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  return (
    <div className="grid gap-2 text-sm leading-6">
      {lines.map((line, index) => {
        const heading = line.match(/^#{1,3}\s+(.+)$/);
        if (heading) {
          return (
            <p key={index} className="font-bold text-current">
              <InlineMarkdown text={heading[1]} />
            </p>
          );
        }
        if (line.startsWith("- ")) {
          return (
            <div key={index} className="flex gap-2">
              <span aria-hidden="true">•</span>
              <p>
                <InlineMarkdown text={line.slice(2)} />
              </p>
            </div>
          );
        }
        return (
          <p key={index}>
            <InlineMarkdown text={line} />
          </p>
        );
      })}
    </div>
  );
}

function Bubble({ message }: { message: ConversationMessage }) {
  const user = message.role === "user";
  return (
    <div className={user ? "flex justify-end" : "flex justify-start"}>
      <article
        className={
          "max-w-[88%] rounded-3xl px-5 py-4 shadow-sm sm:max-w-[76%] " +
          (user
            ? "rounded-br-md bg-teal-800 text-white"
            : "rounded-bl-md border border-slate-200 bg-white text-slate-700")
        }
      >
        <MessageBody content={message.content} />
        <time
          dateTime={message.created_at}
          className={
            "mt-2 block text-[11px] font-semibold " +
            (user ? "text-white/55" : "text-slate-400")
          }
        >
          {formatTimestamp(message.created_at)}
        </time>
      </article>
    </div>
  );
}

export default function ChatPage() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [pendingMessage, setPendingMessage] = useState<ConversationMessage | null>(null);
  const [loadingList, setLoadingList] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [creating, setCreating] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [editingTitle, setEditingTitle] = useState(false);
  const [titleDraft, setTitleDraft] = useState("");
  const [renaming, setRenaming] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const selected = useMemo(
    () => conversations.find((item) => item.id === selectedId) ?? null,
    [conversations, selectedId],
  );

  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const items = await listConversations();
        if (!active) return;
        setConversations(items);
        setLoadingMessages(items.length > 0);
        setSelectedId(items[0]?.id ?? null);
      } catch (requestError) {
        if (active) setError(getConversationFailureMessage(requestError));
      } finally {
        if (active) setLoadingList(false);
      }
    }
    void load();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    // A newly-created conversation can be selected while its first Bedrock turn
    // is still running. Defer reload until that atomic turn has committed so an
    // earlier empty GET cannot overwrite or duplicate the returned messages.
    if (selectedId === null || sending) return;

    let active = true;
    void getConversation(selectedId)
      .then((detail) => {
        if (active) setMessages(detail.messages);
      })
      .catch((requestError) => {
        if (active) setError(getConversationFailureMessage(requestError));
      })
      .finally(() => {
        if (active) setLoadingMessages(false);
      });
    return () => {
      active = false;
    };
  }, [selectedId, sending]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, pendingMessage, sending]);

  async function refreshConversationList(preferredId?: number) {
    const items = await listConversations();
    setConversations(items);
    if (preferredId !== undefined) {
      setMessages([]);
      setLoadingMessages(true);
      setSelectedId(preferredId);
    }
    return items;
  }

  async function startConversation(): Promise<number | null> {
    setCreating(true);
    setError("");
    try {
      const created = await createConversation();
      setMessages([]);
      await refreshConversationList(created.conversation_id);
      setEditingTitle(false);
      inputRef.current?.focus();
      return created.conversation_id;
    } catch (requestError) {
      setError(getConversationFailureMessage(requestError));
      return null;
    } finally {
      setCreating(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const content = draft.trim();
    if (!content || sending || creating) return;

    setError("");
    setDraft("");
    setPendingMessage({
      id: -Date.now(),
      role: "user",
      content,
      created_at: new Date().toISOString(),
    });
    setSending(true);

    let conversationId = selectedId;
    if (conversationId === null) conversationId = await startConversation();

    if (conversationId === null) {
      setPendingMessage(null);
      setSending(false);
      setDraft(content);
      return;
    }

    try {
      const turn = await sendConversationMessage(conversationId, content);
      setMessages((current) => [
        ...current,
        turn.user_message,
        turn.assistant_message,
      ]);
      setConversations((current) =>
        current.map((item) =>
          item.id === conversationId ? { ...item, title: turn.title } : item,
        ),
      );
    } catch (requestError) {
      setDraft(content);
      setError(getConversationFailureMessage(requestError));
    } finally {
      setPendingMessage(null);
      setSending(false);
      inputRef.current?.focus();
    }
  }

  function beginRename() {
    if (!selected) return;
    setTitleDraft(selected.title);
    setEditingTitle(true);
  }

  async function saveTitle(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const title = titleDraft.trim();
    if (!selectedId || !title || renaming) return;

    setRenaming(true);
    setError("");
    try {
      const renamed = await renameConversation(selectedId, title);
      setConversations((current) =>
        current.map((item) => (item.id === renamed.id ? renamed : item)),
      );
      setEditingTitle(false);
    } catch (requestError) {
      setError(getConversationFailureMessage(requestError));
    } finally {
      setRenaming(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-[#f5f7f2] text-slate-950">
      <SiteHeader />
      <main className="mx-auto grid w-full max-w-7xl flex-1 gap-5 px-4 py-5 sm:px-8 lg:grid-cols-[19rem_minmax(0,1fr)] lg:px-10 lg:py-8">
        <aside className="overflow-hidden rounded-[1.75rem] border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between border-b border-slate-100 p-4">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.16em] text-teal-700">
                Conversation history
              </p>
              <p className="mt-1 text-xs text-slate-400">Private to your account</p>
            </div>
            <button
              type="button"
              disabled={creating || sending}
              onClick={() => void startConversation()}
              className="grid size-10 place-items-center rounded-full bg-teal-800 text-xl text-white transition hover:bg-teal-700 disabled:cursor-wait disabled:opacity-50"
              aria-label="Start a new conversation"
              title="New conversation"
            >
              {creating ? "…" : "+"}
            </button>
          </div>

          <div className="max-h-52 overflow-y-auto p-2 lg:max-h-[36rem]">
            {loadingList ? (
              <p className="px-3 py-6 text-sm text-slate-400">Loading conversations…</p>
            ) : conversations.length === 0 ? (
              <div className="px-3 py-8 text-center">
                <p className="text-sm font-semibold text-slate-700">No conversations yet</p>
                <p className="mt-1 text-xs leading-5 text-slate-400">
                  Send a message or use the + button to begin.
                </p>
              </div>
            ) : (
              <ul className="grid gap-1">
                {conversations.map((conversation) => (
                  <li key={conversation.id}>
                    <button
                      type="button"
                      onClick={() => {
                        if (conversation.id === selectedId) return;
                        setMessages([]);
                        setLoadingMessages(true);
                        setError("");
                        setSelectedId(conversation.id);
                        setEditingTitle(false);
                      }}
                      className={
                        "w-full rounded-2xl px-3 py-3 text-left transition " +
                        (selectedId === conversation.id
                          ? "bg-teal-50 text-teal-950"
                          : "text-slate-600 hover:bg-slate-50 hover:text-slate-950")
                      }
                    >
                      <span className="block truncate text-sm font-semibold">
                        {conversation.title}
                      </span>
                      <time
                        dateTime={conversation.created_at}
                        className="mt-1 block text-[11px] text-slate-400"
                      >
                        {new Date(conversation.created_at).toLocaleDateString("en", {
                          day: "numeric",
                          month: "short",
                        })}
                      </time>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </aside>

        <section className="flex min-h-[42rem] min-w-0 flex-col overflow-hidden rounded-[1.75rem] border border-slate-200 bg-[#eef3ee] shadow-sm">
          <header className="flex min-h-20 items-center justify-between gap-4 border-b border-slate-200 bg-white px-5 py-4 sm:px-6">
            <div className="min-w-0">
              <p className="text-xs font-bold uppercase tracking-[0.16em] text-amber-600">
                Multi-turn travel planner
              </p>
              {editingTitle ? (
                <form onSubmit={saveTitle} className="mt-1 flex items-center gap-2">
                  <input
                    required
                    maxLength={256}
                    autoFocus
                    value={titleDraft}
                    onChange={(event) => setTitleDraft(event.target.value)}
                    className="min-w-0 flex-1 rounded-lg border border-teal-300 px-2 py-1 text-lg font-semibold outline-none focus:ring-2 focus:ring-teal-600/20"
                  />
                  <button
                    type="submit"
                    disabled={renaming}
                    className="text-xs font-bold text-teal-700 disabled:opacity-50"
                  >
                    Save
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditingTitle(false)}
                    className="text-xs font-bold text-slate-400"
                  >
                    Cancel
                  </button>
                </form>
              ) : (
                <h1 className="mt-1 truncate text-xl font-semibold tracking-[-0.03em] sm:text-2xl">
                  {selected?.title ?? "Start a conversation"}
                </h1>
              )}
            </div>
            {selected && !editingTitle && (
              <button
                type="button"
                onClick={beginRename}
                className="shrink-0 rounded-full border border-slate-200 px-3 py-2 text-xs font-bold text-slate-500 transition hover:border-teal-300 hover:text-teal-700"
              >
                Rename
              </button>
            )}
          </header>

          <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6" aria-live="polite">
            {loadingMessages ? (
              <div className="grid h-full place-items-center text-sm font-semibold text-slate-400">
                Loading messages…
              </div>
            ) : messages.length === 0 && !pendingMessage ? (
              <div className="grid h-full min-h-64 place-items-center text-center">
                <div className="max-w-md">
                  <span className="mx-auto grid size-14 place-items-center rounded-full bg-teal-100 text-2xl">
                    ✦
                  </span>
                  <h2 className="mt-4 text-2xl font-semibold tracking-[-0.03em] text-teal-950">
                    Plan in context
                  </h2>
                  <p className="mt-2 text-sm leading-6 text-slate-500">
                    Ask for an itinerary, then follow up with “What about Day 2?”
                    KelanaAI reloads this conversation before answering.
                  </p>
                </div>
              </div>
            ) : (
              <div className="grid gap-4">
                {messages.map((message) => (
                  <Bubble key={message.id} message={message} />
                ))}
                {pendingMessage && <Bubble message={pendingMessage} />}
                {sending && (
                  <div className="flex justify-start">
                    <div className="flex items-center gap-1 rounded-3xl rounded-bl-md border border-slate-200 bg-white px-5 py-4 shadow-sm">
                      <span className="size-2 animate-bounce rounded-full bg-teal-600 [animation-delay:-0.3s]" />
                      <span className="size-2 animate-bounce rounded-full bg-teal-600 [animation-delay:-0.15s]" />
                      <span className="size-2 animate-bounce rounded-full bg-teal-600" />
                      <span className="ml-2 text-xs font-semibold text-slate-400">
                        KelanaAI is typing
                      </span>
                    </div>
                  </div>
                )}
                <div ref={bottomRef} />
              </div>
            )}
          </div>

          <div className="border-t border-slate-200 bg-white p-4 sm:p-5">
            {error && (
              <p role="alert" className="mb-3 text-sm font-medium text-rose-700">
                {error}
              </p>
            )}
            <form onSubmit={handleSubmit} className="flex items-end gap-3">
              <label className="sr-only" htmlFor="chat-message">
                Message KelanaAI
              </label>
              <input
                ref={inputRef}
                id="chat-message"
                required
                maxLength={4000}
                value={draft}
                disabled={sending || creating}
                onChange={(event) => setDraft(event.target.value)}
                placeholder="Ask a travel question…"
                className="min-h-12 min-w-0 flex-1 rounded-full border border-slate-200 bg-slate-50 px-5 text-sm font-medium outline-none transition placeholder:text-slate-400 focus:border-teal-500 focus:bg-white focus:ring-4 focus:ring-teal-600/10 disabled:opacity-60"
              />
              <button
                type="submit"
                disabled={!draft.trim() || sending || creating}
                className="min-h-12 shrink-0 rounded-full bg-teal-800 px-5 text-sm font-bold text-white transition hover:bg-teal-700 disabled:cursor-not-allowed disabled:opacity-45"
              >
                {sending ? "Sending…" : "Send"}
              </button>
            </form>
            <p className="mt-2 px-2 text-[11px] text-slate-400">
              Messages are saved to your private history and sent to Amazon Bedrock
              to answer this turn.
            </p>
          </div>
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}
