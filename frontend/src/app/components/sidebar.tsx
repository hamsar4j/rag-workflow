"use client";

import type { ComponentType } from "react";
import { TabKey, ChatSession } from "../types/dashboard";
import { BookCopy, BotMessageSquare } from "lucide-react";
import { ChatList } from "./chat/chat-list";

type SidebarProps = {
  activeTab: TabKey;
  onTabChange: (tab: TabKey) => void;
  usagePercent: number;
  documentCount: number;
  chats?: ChatSession[];
  activeChatId?: string | null;
  onSelectChat?: (chatId: string) => void;
  onNewChat?: () => void;
  onDeleteChat?: (chatId: string) => void;
};

type NavItem = {
  id: TabKey | string;
  label: string;
  icon: ComponentType<{ className?: string }>;
  disabled?: boolean;
};

const NAV_ITEMS: NavItem[] = [
  { id: "chat", label: "Chat", icon: BotMessageSquare },
  { id: "knowledge-base", label: "Knowledge Base", icon: BookCopy },
];

export function Sidebar({
  activeTab,
  onTabChange,
  usagePercent,
  documentCount,
  chats,
  activeChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
}: SidebarProps) {
  const showChatList =
    activeTab === "chat" && chats && onSelectChat && onNewChat && onDeleteChat;

  return (
    <aside className="flex w-20 flex-col border-r border-(--border-subtle) bg-(--surface-muted) px-3 py-6 text-(--text-secondary) lg:w-64">
      <nav className="space-y-1">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = item.id === activeTab;
          const isDisabled = Boolean(item.disabled);
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => {
                if (isDisabled) return;
                if (item.id === "chat" || item.id === "knowledge-base") {
                  onTabChange(item.id as TabKey);
                }
              }}
              disabled={isDisabled}
              className={`group flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition ${
                isActive
                  ? "bg-(--surface-raised) text-(--accent-primary) shadow-sm"
                  : "text-(--text-muted) hover:bg-(--surface-muted) hover:text-(--text-primary)"
              } ${isDisabled ? "cursor-not-allowed opacity-40" : ""}`}
            >
              <span
                className={`flex h-9 w-9 items-center justify-center rounded-lg border transition ${
                  isActive
                    ? "border-(--border-strong) bg-(--surface-panel) text-(--accent-primary)"
                    : "border-(--border-subtle) bg-(--surface-muted) text-(--text-muted) group-hover:border-(--border-strong) group-hover:text-(--text-primary)"
                }`}
              >
                <Icon className="h-4 w-4" />
              </span>
              <span className="hidden lg:inline">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {showChatList ? (
        <div className="mt-6 hidden flex-col gap-2 overflow-hidden lg:flex lg:flex-1">
          <ChatList
            chats={chats}
            activeChatId={activeChatId || null}
            onSelectChat={onSelectChat}
            onNewChat={onNewChat}
            onDeleteChat={onDeleteChat}
          />
        </div>
      ) : (
        <div className="mt-6 hidden flex-1 lg:block" />
      )}

      <div className="mt-6 hidden flex-col gap-3 rounded-2xl border border-(--border-subtle) bg-(--surface-muted) px-4 py-3 text-xs text-(--text-muted) lg:flex">
        <div className="flex items-center justify-between">
          <span>Usage</span>
          <span className="font-medium text-(--accent-primary)">
            {documentCount} / 100
          </span>
        </div>
        <div className="h-2 w-full rounded-full bg-(--border-subtle)">
          <div
            className="h-2 rounded-full bg-emerald-400 transition-all"
            style={{ width: `${usagePercent}%` }}
          />
        </div>
        <p className="text-(--text-secondary)">
          Selected documents have been tagged successfully.
        </p>
      </div>
    </aside>
  );
}
