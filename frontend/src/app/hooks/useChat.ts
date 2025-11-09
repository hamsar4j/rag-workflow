"use client";

import { FormEvent, useCallback, useState } from "react";
import { ChatMessage, ChatWithMessages } from "../types/dashboard";
import { createId } from "../utils/id";

type UseChatOptions = {
  apiBase: string;
  model: string;
  chatId?: string | null;
  onChatCreated?: (chatId: string) => void;
};

export function useChat({
  apiBase,
  model,
  chatId: initialChatId,
  onChatCreated,
}: UseChatOptions) {
  const [chatId, setChatId] = useState<string | null>(initialChatId || null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [pending, setPending] = useState(false);
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);

  const loadChat = useCallback(
    async (loadChatId: string) => {
      setError(null);
      setPending(true);
      try {
        const response = await fetch(`${apiBase}/chats/${loadChatId}`);
        if (!response.ok) {
          throw new Error(`Failed to load chat (status ${response.status})`);
        }

        const chat = (await response.json()) as ChatWithMessages;
        setChatId(chat.id);
        setMessages(chat.messages);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to load chat";
        setError(message);
        console.error("Failed to load chat:", err);
      } finally {
        setPending(false);
      }
    },
    [apiBase],
  );

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
          chat_id: chatId,
          model,
        }),
      });

      if (!response.ok) {
        throw new Error(`API returned status ${response.status}`);
      }

      const payload = (await response.json()) as {
        chat_id: string;
        segments?: { text: string; source: string | null }[];
      };

      if (!payload.segments || payload.segments.length === 0) {
        throw new Error("RAG API responded without segments payload.");
      }

      // Update chat ID if this was a new chat
      if (!chatId && payload.chat_id) {
        setChatId(payload.chat_id);
        onChatCreated?.(payload.chat_id);
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

  const startNewChat = useCallback(() => {
    setChatId(null);
    setMessages([]);
    setInput("");
    setError(null);
    setPending(false);
  }, []);

  const resetConversation = useCallback(() => {
    setMessages([]);
    setInput("");
    setError(null);
    setPending(false);
  }, []);

  return {
    chatId,
    messages,
    pending,
    error,
    input,
    setInput,
    setError,
    handleSubmit,
    loadChat,
    startNewChat,
    resetConversation,
  };
}
