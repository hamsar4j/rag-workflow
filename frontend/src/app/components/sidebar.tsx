"use client";

import { TabKey } from "../types/dashboard";
import { UserRound, BookCopy, Settings, BotMessageSquare } from "lucide-react";

type SidebarProps = {
  activeTab: TabKey;
  onTabChange: (tab: TabKey) => void;
  usagePercent: number;
  documentCount: number;
};

type NavItem = {
  id: TabKey | string;
  label: string;
  icon: (props: { className?: string }) => JSX.Element;
  disabled?: boolean;
};

const NAV_ITEMS: NavItem[] = [
  { id: "chat", label: "Chat", icon: BotMessageSquare },
  { id: "agents", label: "Agents", icon: UserRound, disabled: true },
  { id: "knowledge-base", label: "Knowledge Base", icon: BookCopy },
  { id: "settings", label: "Settings", icon: Settings, disabled: true },
];

export function Sidebar({
  activeTab,
  onTabChange,
  usagePercent,
  documentCount,
}: SidebarProps) {
  return (
    <aside className="flex w-20 flex-col border-r border-slate-200 bg-linear-to-b from-[#1d2856] via-[#182346] to-[#11182f] px-3 py-6 text-slate-200 lg:w-64">
      <nav className="flex-1 space-y-1">
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
                  ? "bg-white/10 text-white shadow-sm"
                  : "text-slate-200/80 hover:bg-white/5 hover:text-white"
              } ${isDisabled ? "cursor-not-allowed opacity-40" : ""}`}
            >
              <span
                className={`flex h-9 w-9 items-center justify-center rounded-lg border transition ${
                  isActive
                    ? "border-white/30 bg-white/10 text-white"
                    : "border-white/10 bg-transparent text-slate-200/70 group-hover:border-white/20 group-hover:text-white"
                }`}
              >
                <Icon className="h-4 w-4" />
              </span>
              <span className="hidden lg:inline">{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="mt-6 hidden flex-col gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-xs text-slate-200/80 backdrop-blur lg:flex">
        <div className="flex items-center justify-between">
          <span>Usage</span>
          <span className="font-medium text-white">
            {documentCount} / 10.0M
          </span>
        </div>
        <div className="h-2 w-full rounded-full bg-white/10">
          <div
            className="h-2 rounded-full bg-emerald-400 transition-all"
            style={{ width: `${usagePercent}%` }}
          />
        </div>
        <p>Selected documents have been tagged successfully.</p>
      </div>
    </aside>
  );
}
