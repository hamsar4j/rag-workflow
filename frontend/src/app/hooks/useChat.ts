"use client";

import { FormEvent, useCallback, useState } from "react";
import { ChatMessage } from "../types/dashboard";
import { createId } from "../utils/id";

type UseChatOptions = {
  apiBase: string;
  model: string;
};

export function useChat({ apiBase, model }: UseChatOptions) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [pending, setPending] = useState(false);
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
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
      const response = await fetch(`${apiBase}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: trimmed,
          model,
          config: { configurable: { thread_id: "web-control-room" } },
        }),
      });

      if (!response.ok) {
        throw new Error(`API returned status ${response.status}`);
      }

      const payload = (await response.json()) as {
        segments?: { text: string; source: string | null }[];
      };

      if (!payload.segments || payload.segments.length === 0) {
        throw new Error("RAG API responded without segments payload.");
      }

      // Reconstruct the full text from segments for backward compatibility
      const fullText = payload.segments.map((seg) => seg.text).join("");

      setMessages((prev) => [
        ...prev,
        {
          id: createId(),
          role: "assistant",
          content: fullText,
          segments: payload.segments,
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

  const resetConversation = useCallback(() => {
    setMessages([]);
    setInput("");
    setError(null);
    setPending(false);
  }, []);

  return {
    messages,
    pending,
    error,
    input,
    setInput,
    setError,
    handleSubmit,
    resetConversation,
  };
}
