"use client";

import { FormEvent, useState } from "react";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

const API_BASE =
  process.env.NEXT_PUBLIC_RAG_API?.replace(/\/$/, "") ??
  "http://localhost:8000";

function createId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return Math.random().toString(36).slice(2);
}

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: createId(),
      role: "assistant",
      content:
        "Welcome to the RAG control room. Ask anything about the knowledge base and I'll surface grounded answers backed by the latest retrieval run.",
    },
  ]);
  const [pending, setPending] = useState(false);
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSend = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || pending) return;

    setError(null);

    const userMessage: ChatMessage = {
      id: createId(),
      role: "user",
      content: trimmed,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setPending(true);

    try {
      const response = await fetch(`${API_BASE}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: trimmed,
          config: { configurable: { thread_id: "web-control-room" } },
        }),
      });

      if (!response.ok) {
        throw new Error(`API returned status ${response.status}`);
      }

      const payload = (await response.json()) as { answer?: string };
      const answer = payload.answer?.trim();

      if (!answer) {
        throw new Error("RAG API responded without an answer payload.");
      }

      setMessages((prev) => [
        ...prev,
        {
          id: createId(),
          role: "assistant",
          content: answer,
        },
      ]);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Unexpected error reaching the RAG API.";
      setError(message);
      setMessages((prev) => [
        ...prev,
        {
          id: createId(),
          role: "assistant",
          content:
            "I hit a snag reaching the backend. Verify the FastAPI service is running on the configured host and try again.",
        },
      ]);
    } finally {
      setPending(false);
    }
  };

  return (
    <div className="min-h-screen px-6 py-8 text-[13px] text-[#1f1d2c] sm:px-10 sm:py-10">
      <div className="mx-auto flex h-[calc(100vh-4rem)] max-w-[1200px] flex-col gap-6">
        <header className="panel-border panel-body px-8 py-6">
          <div className="flex flex-wrap items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="text-2xl font-semibold tracking-[0.45em] text-[var(--primary)] uppercase">
                RAG
              </div>
              <p className="text-[11px] tracking-[0.32em] text-[var(--primary)]/70 uppercase">
                RAG agent operations desk
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <div className="rounded-full border-2 border-[var(--primary)] bg-white px-4 py-1.5 text-[11px] tracking-[0.3em] text-[var(--primary)] uppercase">
                Time Elapsed: 00:08:06
              </div>
            </div>
          </div>
        </header>

        <main className="flex flex-1 flex-col gap-6 lg:flex-row">
          <section className="panel-border panel-body flex flex-1 flex-col overflow-hidden">
            <div className="border-b-2 border-[var(--primary)]/40 bg-[var(--primary-soft)] px-8 py-4 text-[11px] tracking-[0.35em] text-[var(--primary)] uppercase">
              Live Chat
            </div>

            <div className="flex flex-1 flex-col">
              <div className="flex-1 overflow-y-auto px-8 py-6">
                <div className="space-y-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${
                        message.role === "user"
                          ? "justify-end"
                          : "justify-start"
                      }`}
                    >
                      <div
                        className={`max-w-[70%] rounded-[1.6rem] border-2 px-5 py-3 leading-relaxed shadow-[0_4px_0_rgba(0,0,0,0.12)] ${
                          message.role === "user"
                            ? "border-[var(--primary)] bg-[var(--primary)] text-white"
                            : "border-[var(--primary)]/30 bg-white text-[#2f2c46]"
                        }`}
                      >
                        <p className="text-[10px] tracking-[0.3em] uppercase opacity-70">
                          {message.role === "user" ? "You" : "RAG"}
                        </p>
                        <p className="mt-2 whitespace-pre-line">
                          {message.content}
                        </p>
                      </div>
                    </div>
                  ))}
                  {pending && (
                    <div className="flex justify-start">
                      <div className="max-w-[70%] rounded-[1.6rem] border-2 border-[var(--primary)]/30 bg-white px-5 py-3 text-[#2f2c46] opacity-70 shadow-[0_4px_0_rgba(0,0,0,0.12)]">
                        <p className="text-[10px] tracking-[0.3em] uppercase opacity-70">
                          RAG
                        </p>
                        <p className="mt-2">Retrieving context…</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <form
                className="border-t-2 border-[var(--primary)]/30 bg-white/90 px-6 py-5"
                onSubmit={handleSend}
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                  <input
                    className="input-field flex-1"
                    type="text"
                    placeholder="Ask about sources, ingestion status, or response quality…"
                    value={input}
                    onChange={(event) => setInput(event.target.value)}
                  />
                  <button className="send-button shrink-0" type="submit">
                    {pending ? "Streaming…" : "Send"}
                  </button>
                </div>
                {error && (
                  <p className="mt-3 text-[11px] tracking-[0.24em] text-[#c23838] uppercase">
                    {error}
                  </p>
                )}
              </form>
            </div>
          </section>

          <aside className="panel-border panel-body w-full shrink-0 px-7 py-7 lg:w-[320px]">
            <div className="space-y-6">
              <section>
                <h2 className="text-base tracking-[0.35em] text-[var(--primary)] uppercase">
                  Operator Notes
                </h2>
                <p className="mt-3 text-[11px] leading-6 text-[#3f3c52]">
                  Use this console to supervise the RAG workflow. Responses
                  route through FastAPI → LangGraph → Qdrant before landing
                  here.
                </p>
              </section>

              <section>
                <h3 className="text-[10px] tracking-[0.35em] text-[var(--primary)] uppercase">
                  Quick Checks
                </h3>
                <ul className="mt-3 space-y-3 text-[11px] leading-6 text-[#3f3c52]">
                  <li>• Ingestion CLI: `uv run python -m app.ingestion.cli`</li>
                  <li>• Backend health: `GET /health` (expect 200)</li>
                  <li>• Latency guardrail: keep p95 under 1200ms</li>
                  <li>• Manual override when trust score &lt; 0.8</li>
                </ul>
              </section>

              <section className="rounded-3xl border-2 border-[var(--primary)]/35 bg-white px-5 py-4 text-[11px] leading-6 text-[#3f3c52] shadow-[0_4px_0_var(--primary-shadow)]">
                <h3 className="text-[10px] tracking-[0.35em] text-[var(--primary)] uppercase">
                  Active Signals
                </h3>
                <ul className="mt-3 space-y-2">
                  <li>
                    <span className="text-[var(--primary)]">Docs Indexed:</span>{" "}
                    1,248 (+36 today)
                  </li>
                  <li>
                    <span className="text-[var(--primary)]">
                      Latency (p95):
                    </span>{" "}
                    742ms (reranker on)
                  </li>
                  <li>
                    <span className="text-[var(--primary)]">Answer Rate:</span>{" "}
                    97% (last 50 chats)
                  </li>
                </ul>
              </section>
            </div>
          </aside>
        </main>
      </div>
    </div>
  );
}
