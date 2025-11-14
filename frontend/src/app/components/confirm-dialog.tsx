"use client";

import { AlertTriangle } from "lucide-react";

type ConfirmDialogProps = {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
};

export function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmLabel = "Delete",
  cancelLabel = "Cancel",
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-100 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onCancel}
      />

      {/* Dialog */}
      <div className="animate-in fade-in zoom-in-95 relative z-101 w-full max-w-md duration-200">
        <div className="mx-4 rounded-2xl border border-(--border-subtle) bg-(--surface-panel) p-6 shadow-2xl">
          {/* Icon and Title */}
          <div className="flex items-start gap-4">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[rgba(239,68,68,0.1)]">
              <AlertTriangle
                className="h-5 w-5 text-[rgb(239,68,68)]"
                strokeWidth={2}
              />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-(--text-primary)">
                {title}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-(--text-secondary)">
                {message}
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="mt-6 flex gap-3">
            <button
              onClick={onCancel}
              className="flex-1 rounded-xl border border-(--border-subtle) bg-(--surface-base) px-4 py-2.5 text-sm font-medium text-(--text-primary) transition hover:bg-(--surface-muted) focus-visible:ring-2 focus-visible:ring-(--accent-violet)/25 focus-visible:outline-none"
            >
              {cancelLabel}
            </button>
            <button
              onClick={onConfirm}
              className="flex-1 rounded-xl border border-[rgba(239,68,68,0.35)] bg-[rgba(239,68,68,0.15)] px-4 py-2.5 text-sm font-medium text-[rgb(239,68,68)] transition hover:bg-[rgba(239,68,68,0.25)] focus-visible:ring-2 focus-visible:ring-[rgba(239,68,68,0.25)] focus-visible:outline-none"
            >
              {confirmLabel}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
