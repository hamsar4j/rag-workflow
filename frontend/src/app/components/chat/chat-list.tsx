"use client";

import { MessageSquare, Plus, Trash2 } from "lucide-react";
import { ChatSession } from "../../types/dashboard";

type ChatListProps = {
  chats: ChatSession[];
  activeChatId: string | null;
  onSelectChat: (chatId: string) => void;
  onNewChat: () => void;
  onDeleteChat: (chatId: string) => void;
};

export function ChatList({
  chats,
  activeChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
}: ChatListProps) {
  return (
    <div className="flex min-h-0 flex-1 flex-col gap-2">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-(--text-primary)">
          Chat History
        </h3>
        <button
          onClick={onNewChat}
          className="flex items-center gap-1.5 rounded-lg border border-(--border-subtle) bg-(--surface-panel) px-3 py-1.5 text-xs font-medium text-(--accent-violet) transition hover:border-(--accent-violet) hover:bg-(--surface-muted) hover:text-(--accent-primary)"
          aria-label="Start new chat"
        >
          <Plus className="h-3.5 w-3.5" strokeWidth={2.5} />
          New Chat
        </button>
      </div>

      <div className="flex min-h-0 flex-1 flex-col gap-1 overflow-y-auto">
        {chats.length === 0 ? (
          <p className="py-4 text-center text-xs text-(--text-muted)">
            No chats yet. Start a new conversation!
          </p>
        ) : (
          chats.map((chat) => (
            <div
              key={chat.id}
              className={`group flex items-center gap-2 rounded-lg border px-3 py-2 text-sm transition ${
                activeChatId === chat.id
                  ? "border-(--accent-violet) bg-[rgba(168,85,247,0.1)] text-(--accent-primary)"
                  : "border-(--border-subtle) bg-(--surface-panel) text-(--text-secondary) hover:border-(--border-subtle) hover:bg-(--surface-muted)"
              }`}
            >
              <button
                onClick={() => onSelectChat(chat.id)}
                className="flex flex-1 items-center gap-2 overflow-hidden text-left"
              >
                <MessageSquare className="h-4 w-4 flex-shrink-0" strokeWidth={2} />
                <span className="truncate font-medium">{chat.title}</span>
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteChat(chat.id);
                }}
                className="opacity-0 transition hover:text-(--error) group-hover:opacity-100"
                aria-label="Delete chat"
              >
                <Trash2 className="h-3.5 w-3.5" strokeWidth={2} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
