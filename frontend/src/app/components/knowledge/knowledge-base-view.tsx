"use client";

import { ChangeEvent, FormEvent } from "react";
import {
  ToyBrick,
  RotateCcw,
  Search,
  Tag,
  FileUp,
  Upload,
  LoaderCircle,
} from "lucide-react";

import { IngestionStatus, KnowledgeDocument } from "../../types/dashboard";
import { formatDateString, formatFileSize } from "../../utils/formatters";

type UrlState = {
  input: string;
  pending: boolean;
  status: IngestionStatus | null;
};

type PdfState = {
  files: File[];
  pending: boolean;
  status: IngestionStatus | null;
};

type KnowledgeBaseViewProps = {
  filteredDocs: KnowledgeDocument[];
  searchTerm: string;
  onSearchChange: (value: string) => void;
  selectedDocIds: string[];
  onToggleDocument: (id: string) => void;
  onToggleAll: (checked: boolean) => void;
  allFilteredSelected: boolean;
  urlState: UrlState;
  onUrlInputChange: (value: string) => void;
  onUrlSubmit: (event: FormEvent<HTMLFormElement>) => void;
  pdfState: PdfState;
  onPdfSelection: (event: ChangeEvent<HTMLInputElement>) => void;
  onPdfSubmit: (event: FormEvent<HTMLFormElement>) => void;
};

export function KnowledgeBaseView({
  filteredDocs,
  searchTerm,
  onSearchChange,
  selectedDocIds,
  onToggleDocument,
  onToggleAll,
  allFilteredSelected,
  urlState,
  onUrlInputChange,
  onUrlSubmit,
  pdfState,
  onPdfSelection,
  onPdfSubmit,
}: KnowledgeBaseViewProps) {
  return (
    <section className="flex h-full flex-col">
      <div className="flex-1 overflow-y-auto px-6 py-8 lg:px-24">
        <div className="flex flex-col gap-8">
          <div className="rounded-3xl border border-(--border-subtle) bg-(--surface-panel) p-6 shadow-sm">
            <div className="flex flex-wrap items-center gap-4">
              <div className="relative flex-1">
                <span className="pointer-events-none absolute inset-y-0 left-3.5 flex items-center text-(--text-muted)">
                  <Search className="h-4 w-4" />
                </span>
                <input
                  className="w-full rounded-xl border border-(--border-subtle) bg-(--surface-muted) py-2.5 pr-4 pl-10 text-sm text-(--text-secondary) transition focus:border-(--accent-violet) focus:bg-(--surface-panel) focus:ring-2 focus:ring-(--focus-ring) focus:outline-none"
                  placeholder="Search documents…"
                  value={searchTerm}
                  onChange={(event) => onSearchChange(event.target.value)}
                />
              </div>
              <button
                type="button"
                className="flex items-center gap-2 rounded-xl border border-(--border-subtle) bg-(--surface-muted) px-4 py-2.5 text-sm font-medium text-(--text-secondary) transition hover:border-(--border-strong) hover:text-(--text-primary)"
              >
                <Tag className="h-4 w-4" />
                Filter by tags
              </button>
              <button
                type="button"
                className="flex items-center gap-2 rounded-xl border border-(--border-subtle) bg-(--surface-muted) px-4 py-2.5 text-sm font-medium text-(--text-secondary) transition hover:border-(--border-strong) hover:text-(--text-primary)"
                onClick={() => onSearchChange("")}
              >
                <RotateCcw className="h-4 w-4" />
                Refresh
              </button>
            </div>

            <div className="mt-6 overflow-x-auto">
              <table className="min-w-full border-separate border-spacing-y-2 text-sm">
                <thead>
                  <tr className="text-xs font-medium tracking-wider text-(--text-muted) uppercase">
                    <th className="w-12 px-4 py-2 text-left">
                      <input
                        aria-label="Select all documents"
                        type="checkbox"
                        className="h-4 w-4 rounded border-(--border-subtle) bg-(--surface-muted) text-(--accent-violet) focus:ring-(--focus-ring)"
                        checked={allFilteredSelected}
                        onChange={(event) => onToggleAll(event.target.checked)}
                      />
                    </th>
                    <th className="px-4 py-2 text-left">Name</th>
                    <th className="px-4 py-2 text-left">Last Sync</th>
                    <th className="px-4 py-2 text-left">Size</th>
                    <th className="px-4 py-2 text-left">Tags</th>
                    <th className="px-4 py-2 text-left">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredDocs.length === 0 ? (
                    <tr>
                      <td
                        colSpan={6}
                        className="rounded-2xl border border-dashed border-(--border-subtle) bg-(--surface-muted)/50 px-4 py-12 text-center text-sm text-(--text-muted)"
                      >
                        No documents match your filters yet. Ingest new content
                        with the controls below.
                      </td>
                    </tr>
                  ) : (
                    filteredDocs.map((doc) => {
                      const isChecked = selectedDocIds.includes(doc.id);
                      return (
                        <tr
                          key={doc.id}
                          className={`group transition-colors ${
                            isChecked
                              ? "bg-(--surface-raised)"
                              : "bg-(--surface-panel) hover:bg-(--surface-raised)/50"
                          }`}
                        >
                          <td className="rounded-l-2xl border-y border-l border-(--border-subtle) px-4 py-3 align-middle first:border-l">
                            <input
                              type="checkbox"
                              className="h-4 w-4 rounded border-(--border-subtle) bg-(--surface-muted) text-(--accent-violet) focus:ring-(--focus-ring)"
                              checked={isChecked}
                              onChange={() => onToggleDocument(doc.id)}
                              aria-label={`Select ${doc.name}`}
                            />
                          </td>
                          <td className="border-y border-(--border-subtle) px-4 py-3 align-middle font-medium text-(--text-primary)">
                            {doc.name}
                          </td>
                          <td className="border-y border-(--border-subtle) px-4 py-3 align-middle text-(--text-muted)">
                            {formatDateString(doc.lastSync)}
                          </td>
                          <td className="border-y border-(--border-subtle) px-4 py-3 align-middle text-(--text-muted)">
                            {doc.size || "—"}
                          </td>
                          <td className="border-y border-(--border-subtle) px-4 py-3 align-middle">
                            <div className="flex flex-wrap gap-2">
                              {doc.tags.map((tag) => (
                                <span
                                  key={tag}
                                  className="rounded-full border border-(--border-subtle) bg-(--surface-muted) px-2.5 py-0.5 text-xs font-medium text-(--text-secondary)"
                                >
                                  {tag}
                                </span>
                              ))}
                            </div>
                          </td>
                          <td className="rounded-r-2xl border-y border-r border-(--border-subtle) px-4 py-3 align-middle">
                            <span
                              className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                                doc.status === "Ready"
                                  ? "bg-emerald-500/10 text-emerald-400"
                                  : doc.status === "Processing"
                                    ? "bg-blue-500/10 text-blue-400"
                                    : "bg-rose-500/10 text-rose-400"
                              }`}
                            >
                              <span
                                className={`h-1.5 w-1.5 rounded-full ${
                                  doc.status === "Ready"
                                    ? "bg-emerald-400"
                                    : doc.status === "Processing"
                                      ? "bg-blue-400"
                                      : "bg-rose-400"
                                }`}
                              />
                              {doc.status}
                            </span>
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <form
              onSubmit={onUrlSubmit}
              className="flex flex-col gap-4 rounded-3xl border border-(--border-subtle) bg-(--surface-panel) p-6 shadow-sm transition hover:border-(--border-strong)"
            >
              <div>
                <h3 className="flex items-center gap-2 text-base font-semibold text-(--text-primary)">
                  <Upload className="h-4 w-4 text-(--accent-violet)" />
                  Ingest website URLs
                </h3>
                <p className="mt-1 text-xs text-(--text-muted)">
                  Paste one URL per line. We&apos;ll crawl, chunk, and embed the
                  contents automatically.
                </p>
              </div>
              <textarea
                className="h-32 w-full rounded-xl border border-(--border-subtle) bg-(--surface-muted) px-4 py-3 text-sm text-(--text-secondary) transition placeholder:text-(--text-muted) focus:border-(--accent-violet) focus:bg-(--surface-panel) focus:ring-2 focus:ring-(--focus-ring) focus:outline-none"
                placeholder="https://example.com/report"
                value={urlState.input}
                onChange={(event) => onUrlInputChange(event.target.value)}
                disabled={urlState.pending}
              />
              <div className="flex flex-wrap items-center justify-between gap-3">
                <button
                  className="flex h-10 items-center justify-center gap-2 rounded-xl bg-(--surface-raised) px-4 text-sm font-medium text-(--text-primary) transition hover:bg-(--surface-muted) hover:text-(--accent-primary) focus-visible:ring-2 focus-visible:ring-(--focus-ring) focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-60"
                  type="submit"
                  disabled={urlState.pending}
                >
                  {urlState.pending ? (
                    <>
                      <LoaderCircle className="h-4 w-4 animate-spin" />
                      <span>Processing...</span>
                    </>
                  ) : (
                    <>
                      <span>Start Ingestion</span>
                      <Upload className="h-4 w-4" />
                    </>
                  )}
                </button>
              </div>
              {urlState.status && (
                <div
                  className={`rounded-xl border px-4 py-3 text-sm ${
                    urlState.status.type === "success"
                      ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-200"
                      : "border-rose-500/20 bg-rose-500/10 text-rose-200"
                  }`}
                >
                  <p className="font-medium">{urlState.status.message}</p>
                  {urlState.status.warnings?.length ? (
                    <ul className="mt-2 space-y-1 text-xs text-amber-300">
                      {urlState.status.warnings.map((warning) => (
                        <li key={warning}>• {warning}</li>
                      ))}
                    </ul>
                  ) : null}
                </div>
              )}
            </form>

            <form
              onSubmit={onPdfSubmit}
              className="flex flex-col gap-4 rounded-3xl border border-(--border-subtle) bg-(--surface-panel) p-6 shadow-sm transition hover:border-(--border-strong)"
            >
              <div>
                <h3 className="flex items-center gap-2 text-base font-semibold text-(--text-primary)">
                  <FileUp className="h-4 w-4 text-(--accent-violet)" />
                  Upload PDF documents
                </h3>
                <p className="mt-1 text-xs text-(--text-muted)">
                  Drop contract PDFs, operating manuals, or reports to keep the
                  knowledge base fresh.
                </p>
              </div>
              <label
                htmlFor="pdf-upload"
                className="group flex h-32 cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-(--border-subtle) bg-(--surface-muted)/50 text-sm text-(--text-muted) transition hover:border-(--accent-violet) hover:bg-(--surface-muted)"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-(--surface-raised) transition group-hover:scale-110 group-hover:bg-(--accent-violet) group-hover:text-white">
                  <ToyBrick className="h-5 w-5" />
                </div>
                <div className="text-center">
                  <span className="font-medium text-(--text-primary)">
                    Click to upload
                  </span>
                  <span className="text-(--text-muted)"> or drag and drop</span>
                </div>
                <input
                  id="pdf-upload"
                  type="file"
                  accept="application/pdf"
                  multiple
                  className="hidden"
                  onChange={onPdfSelection}
                  disabled={pdfState.pending}
                />
              </label>
              {pdfState.files.length > 0 && (
                <ul className="rounded-xl border border-(--border-subtle) bg-(--surface-muted) px-4 py-3 text-xs text-(--text-secondary)">
                  {pdfState.files.map((file) => (
                    <li key={file.name} className="flex justify-between">
                      <span className="truncate">{file.name}</span>
                      <span className="pl-2 text-(--text-muted)">
                        {formatFileSize(file.size)}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
              <div className="flex flex-wrap items-center justify-between gap-3">
                <button
                  className="flex h-10 items-center justify-center gap-2 rounded-xl bg-(--surface-raised) px-4 text-sm font-medium text-(--text-primary) transition hover:bg-(--surface-muted) hover:text-(--accent-primary) focus-visible:ring-2 focus-visible:ring-(--focus-ring) focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-60"
                  type="submit"
                  disabled={pdfState.pending}
                >
                  {pdfState.pending ? (
                    <>
                      <LoaderCircle className="h-4 w-4 animate-spin" />
                      <span>Uploading...</span>
                    </>
                  ) : (
                    <>
                      <span>Start Upload</span>
                      <FileUp className="h-4 w-4" />
                    </>
                  )}
                </button>
              </div>
              {pdfState.status && (
                <div
                  className={`rounded-xl border px-4 py-3 text-sm ${
                    pdfState.status.type === "success"
                      ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-200"
                      : "border-rose-500/20 bg-rose-500/10 text-rose-200"
                  }`}
                >
                  <p className="font-medium">{pdfState.status.message}</p>
                  {pdfState.status.warnings?.length ? (
                    <ul className="mt-2 space-y-1 text-xs text-amber-300">
                      {pdfState.status.warnings.map((warning) => (
                        <li key={warning}>• {warning}</li>
                      ))}
                    </ul>
                  ) : null}
                </div>
              )}
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}
