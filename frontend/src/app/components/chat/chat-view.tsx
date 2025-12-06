"use client";

import { FormEvent, useEffect, useRef } from "react";
import { LoaderCircle, SendHorizontal } from "lucide-react";
import { ChatMessage } from "../../types/dashboard";

type ChatViewProps = {
  messages: ChatMessage[];
  pending: boolean;
  error: string | null;
  input: string;
  onInputChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  modelName: string;
};

export function ChatView({
  messages,
  pending,
  error,
  input,
  onInputChange,
  onSubmit,
  modelName,
}: ChatViewProps) {
  const hasMessages = messages.length > 0;
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, pending]);

  const baseButtonClasses =
    "flex items-center justify-center rounded-2xl text-(--accent-violet) transition hover:text-(--accent-primary) focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[rgba(168,85,247,0.25)] disabled:cursor-not-allowed disabled:opacity-60";

  const renderSubmitButton = (size: "compact" | "regular") => (
    <button
      className={`${baseButtonClasses} ${
        size === "compact" ? "h-11 w-11" : "h-12 w-12"
      }`}
      type="submit"
      aria-label={pending ? "Generating response" : "Send message"}
      disabled={pending}
    >
      {pending ? (
        <LoaderCircle className="h-5 w-5 animate-spin" strokeWidth={2.5} />
      ) : (
        <SendHorizontal className="h-5 w-5" strokeWidth={2.3} />
      )}
    </button>
  );

  if (!hasMessages) {
    return (
      <section className="flex h-full flex-col">
        <div className="flex flex-1 items-center justify-center px-6 py-12 lg:px-10">
          <div className="flex w-full max-w-2xl flex-col items-center gap-8 text-center">
            <div className="flex flex-col items-center gap-4">
              <div className="flex max-w-[16rem] items-center justify-center rounded-3xl border border-(--border-subtle) bg-(--surface-panel) px-6 py-3 shadow-lg shadow-black/10">
                <span className="truncate text-sm font-semibold text-(--accent-primary)">
                  {modelName}
                </span>
              </div>
            </div>

            <form className="w-full" onSubmit={onSubmit}>
              <div className="flex items-center gap-3 rounded-3xl border border-(--border-subtle) bg-(--surface-panel) px-6 py-4 shadow-lg shadow-black/10 transition focus-within:border-[rgba(168,85,247,0.45)] focus-within:ring-2 focus-within:ring-[rgba(168,85,247,0.25)]">
                <input
                  className="flex-1 bg-transparent text-sm text-(--text-primary) placeholder:text-(--text-muted) focus:outline-none"
                  type="text"
                  placeholder="How can I help you today?"
                  value={input}
                  onChange={(event) => onInputChange(event.target.value)}
                  disabled={pending}
                />
                {renderSubmitButton("compact")}
              </div>
            </form>

            {error && <p className="w-full text-sm text-(--error)">{error}</p>}
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="relative flex h-full flex-col">
      <div className="flex-1 overflow-y-auto px-6 py-8 pb-32 lg:px-10">
        <div className="mx-auto flex w-full max-w-3xl flex-col gap-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-5 py-3.5 text-sm leading-relaxed shadow-sm ${
                  message.role === "user"
                    ? "bg-(--accent-primary) text-(--surface-base)"
                    : "border border-(--border-subtle) bg-(--surface-panel) text-(--text-secondary)"
                }`}
              >
                <p className="mb-1.5 text-[10px] font-bold tracking-wider uppercase opacity-70">
                  {message.role === "user" ? "You" : "Agent"}
                </p>
                {message.role === "assistant" && message.segments ? (
                  <p className="whitespace-pre-line">
                    {message.segments.map((segment, idx) =>
                      segment.source ? (
                        <span
                          key={idx}
                          className="group relative cursor-help border-b border-dotted border-(--accent-violet) transition-colors hover:border-(--text-primary) hover:bg-[rgba(168,85,247,0.1)]"
                        >
                          {segment.text}
                          <span className="pointer-events-none absolute bottom-full left-1/2 z-50 mb-2 hidden w-max max-w-md -translate-x-1/2 rounded-xl border border-(--border-subtle) bg-(--surface-raised) px-3 py-2 text-xs text-(--text-primary) shadow-xl group-hover:block">
                            <span className="block break-all">
                              {segment.source}
                            </span>
                            <span className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-(--surface-raised)" />
                          </span>
                        </span>
                      ) : (
                        <span key={idx}>{segment.text}</span>
                      ),
                    )}
                  </p>
                ) : (
                  <p className="whitespace-pre-line">{message.content}</p>
                )}
              </div>
            </div>
          ))}
          {pending && (
            <div className="flex justify-start">
              <div className="max-w-[75%] rounded-2xl border border-(--border-subtle) bg-(--surface-panel) px-5 py-4 text-sm text-(--text-muted) shadow-sm">
                <div className="flex items-center gap-3">
                  <LoaderCircle className="h-4 w-4 animate-spin text-(--accent-violet)" />
                  <span className="text-xs font-medium">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="pointer-events-none absolute inset-x-0 bottom-0 bg-linear-to-t from-(--surface-base) via-(--surface-base) to-transparent pt-12 pb-6">
        <div className="pointer-events-auto px-6 lg:px-10">
          <form className="mx-auto w-full max-w-3xl" onSubmit={onSubmit}>
            <div className="relative flex items-center gap-3 rounded-full border border-(--border-subtle) bg-(--surface-panel)/80 px-2 py-2 shadow-lg backdrop-blur-xl transition-all duration-300 focus-within:border-(--accent-violet) focus-within:ring-4 focus-within:ring-(--focus-ring)">
              <input
                className="ml-4 flex-1 bg-transparent text-sm text-(--text-primary) placeholder:text-(--text-muted) focus:outline-none"
                type="text"
                placeholder="Ask anything about your documents..."
                value={input}
                onChange={(event) => onInputChange(event.target.value)}
                disabled={pending}
              />
              {renderSubmitButton("regular")}
            </div>
            {error && (
              <p className="mt-3 text-center text-xs font-medium text-(--error)">
                {error}
              </p>
            )}
          </form>
        </div>
      </div>
    </section>
  );
}
