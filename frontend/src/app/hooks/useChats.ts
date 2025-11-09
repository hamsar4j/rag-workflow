"use client";

import { useCallback, useEffect, useState } from "react";
import { ChatSession } from "../types/dashboard";

type UseChatsOptions = {
  apiBase: string;
};

export function useChats({ apiBase }: UseChatsOptions) {
  const [chats, setChats] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchChats = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiBase}/chats`);
      if (!response.ok) {
        throw new Error(`Failed to fetch chats (status ${response.status})`);
      }
      const data = (await response.json()) as ChatSession[];
      setChats(data);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to fetch chats";
      setError(message);
      console.error("Failed to fetch chats:", err);
    } finally {
      setLoading(false);
    }
  }, [apiBase]);

  const createChat = useCallback(
    async (title?: string): Promise<ChatSession | null> => {
      setError(null);
      try {
        const response = await fetch(`${apiBase}/chats`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ title }),
        });

        if (!response.ok) {
          throw new Error(`Failed to create chat (status ${response.status})`);
        }

        const newChat = (await response.json()) as ChatSession;
        setChats((prev) => [newChat, ...prev]);
        return newChat;
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to create chat";
        setError(message);
        console.error("Failed to create chat:", err);
        return null;
      }
    },
    [apiBase],
  );

  const deleteChat = useCallback(
    async (chatId: string): Promise<boolean> => {
      setError(null);
      try {
        const response = await fetch(`${apiBase}/chats/${chatId}`, {
          method: "DELETE",
        });

        if (!response.ok) {
          throw new Error(`Failed to delete chat (status ${response.status})`);
        }

        setChats((prev) => prev.filter((chat) => chat.id !== chatId));
        return true;
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to delete chat";
        setError(message);
        console.error("Failed to delete chat:", err);
        return false;
      }
    },
    [apiBase],
  );

  useEffect(() => {
    fetchChats();
  }, [fetchChats]);

  return {
    chats,
    loading,
    error,
    fetchChats,
    createChat,
    deleteChat,
  };
}
