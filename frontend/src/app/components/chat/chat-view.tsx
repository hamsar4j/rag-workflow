"use client";

import { FormEvent } from "react";
import { ChatMessage } from "../../types/dashboard";

type ChatViewProps = {
  messages: ChatMessage[];
  pending: boolean;
  error: string | null;
  input: string;
  onInputChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
};

export function ChatView({
  messages,
  pending,
  error,
  input,
  onInputChange,
  onSubmit,
}: ChatViewProps) {
  return (
    <section className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto px-6 py-8 lg:px-10">
        <div className="mx-auto flex w-full max-w-3xl flex-col gap-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[75%] rounded-2xl border px-4 py-3 text-sm leading-relaxed shadow-sm ${
                  message.role === "user"
                    ? "border-transparent bg-blue-600 text-white"
                    : "border-slate-200 bg-white text-slate-700"
                }`}
              >
                <p className="mb-1 text-xs font-medium tracking-wide text-slate-400 uppercase">
                  {message.role === "user" ? "You" : "Agent"}
                </p>
                <p className="whitespace-pre-line">{message.content}</p>
              </div>
            </div>
          ))}
          {pending && (
            <div className="flex justify-start">
              <div className="max-w-[75%] rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500 shadow-sm">
                <p className="text-xs font-medium tracking-wide text-slate-400 uppercase">
                  Agent
                </p>
                <p className="mt-1">Retrieving context…</p>
              </div>
            </div>
          )}
        </div>
      </div>

      <form
        className="border-t border-slate-200 bg-white px-6 py-5 lg:px-10"
        onSubmit={onSubmit}
      >
        <div className="mx-auto flex w-full max-w-3xl flex-col gap-3 sm:flex-row sm:items-center">
          <div className="relative flex-1">
            <input
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-800 shadow-sm transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 focus:outline-none"
              type="text"
              placeholder="Ask about sources, ingestion status, or response quality…"
              value={input}
              onChange={(event) => onInputChange(event.target.value)}
            />
          </div>
          <button
            className="flex items-center justify-center rounded-2xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-blue-300"
            type="submit"
            disabled={pending}
          >
            {pending ? "Generating…" : "Send"}
          </button>
        </div>
        {error && (
          <p className="mx-auto mt-2 w-full max-w-3xl text-sm text-rose-500">
            {error}
          </p>
        )}
      </form>
    </section>
  );
}
