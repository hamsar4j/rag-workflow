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
    <aside className="flex w-20 flex-col border-r border-(--border-subtle) bg-(--surface-muted) px-3 py-6 text-(--text-secondary) lg:w-72">
      <div className="mb-6 px-3">
        <div className="flex items-center gap-2 text-(--text-primary)">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-(--accent-violet) text-white">
            <BotMessageSquare className="h-5 w-5" />
          </div>
          <span className="hidden text-lg font-bold tracking-tight lg:inline">
            RAG Agent
          </span>
        </div>
      </div>

      <nav className="space-y-1.5">
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
              className={`group flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200 ${
                isActive
                  ? "bg-(--surface-raised) text-(--text-primary) shadow-sm ring-1 ring-(--border-subtle)"
                  : "text-(--text-muted) hover:bg-(--surface-raised) hover:text-(--text-primary)"
              } ${isDisabled ? "cursor-not-allowed opacity-40" : ""}`}
            >
              <Icon
                className={`h-5 w-5 transition-colors ${
                  isActive
                    ? "text-(--accent-violet)"
                    : "text-(--text-muted) group-hover:text-(--text-primary)"
                }`}
              />
              <span className="hidden lg:inline">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {showChatList ? (
        <div className="mt-8 hidden flex-col gap-2 overflow-hidden lg:flex lg:flex-1">
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

      <div className="mt-6 hidden flex-col gap-3 rounded-2xl border border-(--border-subtle) bg-(--surface-base) px-4 py-4 text-xs text-(--text-muted) lg:flex">
        <div className="flex items-center justify-between">
          <span className="font-medium text-(--text-secondary)">Storage</span>
          <span className="font-medium text-(--text-primary)">
            {documentCount} / 100
          </span>
        </div>
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-(--surface-raised)">
          <div
            className="h-full rounded-full bg-gradient-to-r from-(--accent-violet) to-(--accent-melon) transition-all duration-500 ease-out"
            style={{ width: `${usagePercent}%` }}
          />
        </div>
        <p className="text-[11px] leading-relaxed text-(--text-muted)">
          {usagePercent >= 100
            ? "Storage limit reached."
            : "Space available for more documents."}
        </p>
      </div>
    </aside>
  );
}
