"use client";

import { ChevronDown } from "lucide-react";

type ModelOption = {
  value: string;
  label: string;
};

type ModelSelectProps = {
  value: string;
  options: ModelOption[];
  onChange: (value: string) => void;
  disabled?: boolean;
  isUpdating?: boolean;
};

export type { ModelOption };

export function ModelSelect({
  value,
  options,
  onChange,
  disabled = false,
  isUpdating = false,
}: ModelSelectProps) {
  return (
    <div className="flex flex-col items-start gap-1 text-left">
      <span className="text-xs font-semibold tracking-wide text-(--text-muted) uppercase">
        Model
      </span>
      <div className="relative">
        <select
          className="appearance-none rounded-2xl border border-(--border-subtle) bg-(--surface-muted) py-2 pr-10 pl-3 text-sm text-(--text-primary) shadow-sm transition focus:border-[rgba(168,85,247,0.45)] focus:ring-2 focus:ring-[rgba(168,85,247,0.25)] focus:outline-none disabled:cursor-not-allowed disabled:opacity-60"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          disabled={disabled || isUpdating}
        >
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-(--text-muted)">
          {isUpdating ? "..." : <ChevronDown />}
        </span>
      </div>
    </div>
  );
}
