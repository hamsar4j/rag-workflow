"use client";

import { ChangeEvent, FormEvent } from "react";
import { ToyBrick, RotateCcw, Search, Tag } from "lucide-react";

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
        <div className="flex flex-col gap-6">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex flex-wrap items-center gap-3">
              <div className="relative flex-1">
                <span className="pointer-events-none absolute inset-y-0 left-3 flex items-center text-slate-400">
                  <Search className="h-4 w-4" />
                </span>
                <input
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2.5 pr-4 pl-10 text-sm text-slate-700 transition focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-100 focus:outline-none"
                  placeholder="Search documents…"
                  value={searchTerm}
                  onChange={(event) => onSearchChange(event.target.value)}
                />
              </div>
              <button
                type="button"
                className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 transition hover:border-slate-300 hover:text-slate-800"
              >
                <Tag className="h-4 w-4" />
                Filter by tags
              </button>
              <button
                type="button"
                className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 transition hover:border-slate-300 hover:text-slate-800"
                onClick={() => onSearchChange("")}
              >
                <RotateCcw className="h-4 w-4" />
                Refresh
              </button>
            </div>

            <div className="mt-5 overflow-x-auto">
              <table className="min-w-full border-separate border-spacing-y-2 text-sm">
                <thead>
                  <tr className="text-xs tracking-wide text-slate-500 uppercase">
                    <th className="w-10 text-left">
                      <input
                        aria-label="Select all documents"
                        type="checkbox"
                        className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                        checked={allFilteredSelected}
                        onChange={(event) => onToggleAll(event.target.checked)}
                      />
                    </th>
                    <th className="py-1 text-left">Name</th>
                    <th className="py-1 text-left">Last Sync</th>
                    <th className="py-1 text-left">Size</th>
                    <th className="py-1 text-left">Tags</th>
                    <th className="py-1 text-left">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredDocs.length === 0 ? (
                    <tr>
                      <td
                        colSpan={6}
                        className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-8 text-center text-sm text-slate-500"
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
                          className="rounded-2xl border border-slate-200 bg-white text-slate-700 shadow-sm"
                        >
                          <td className="rounded-l-2xl px-4 py-3 align-middle">
                            <input
                              type="checkbox"
                              className="h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                              checked={isChecked}
                              onChange={() => onToggleDocument(doc.id)}
                              aria-label={`Select ${doc.name}`}
                            />
                          </td>
                          <td className="py-3 pr-4 align-middle font-medium text-slate-900">
                            {doc.name}
                          </td>
                          <td className="py-3 pr-4 align-middle text-slate-600">
                            {formatDateString(doc.lastSync)}
                          </td>
                          <td className="py-3 pr-4 align-middle text-slate-600">
                            {doc.size || "—"}
                          </td>
                          <td className="py-3 pr-4 align-middle">
                            <div className="flex flex-wrap gap-2">
                              {doc.tags.map((tag) => (
                                <span
                                  key={tag}
                                  className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600"
                                >
                                  {tag}
                                </span>
                              ))}
                            </div>
                          </td>
                          <td className="rounded-r-2xl py-3 pr-4 align-middle">
                            <span
                              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                                doc.status === "Ready"
                                  ? "bg-emerald-50 text-emerald-600"
                                  : doc.status === "Processing"
                                    ? "bg-blue-50 text-blue-600"
                                    : "bg-rose-50 text-rose-600"
                              }`}
                            >
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
              className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <div>
                <h3 className="text-sm font-semibold text-slate-900">
                  Ingest website URLs
                </h3>
                <p className="text-xs text-slate-500">
                  Paste one URL per line. We&apos;ll crawl, chunk, and embed the
                  contents automatically.
                </p>
              </div>
              <textarea
                className="h-32 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700 transition focus:border-blue-500 focus:bg-white focus:ring-2 focus:ring-blue-100 focus:outline-none"
                placeholder="https://example.com/report"
                value={urlState.input}
                onChange={(event) => onUrlInputChange(event.target.value)}
                disabled={urlState.pending}
              />
              <div className="flex flex-wrap items-center justify-between gap-3">
                <button
                  className="flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-blue-300"
                  type="submit"
                  disabled={urlState.pending}
                >
                  {urlState.pending ? "Ingesting…" : "Ingest URLs"}
                </button>
                {urlState.pending && (
                  <span className="text-sm text-slate-500">
                    Initializing crawler…
                  </span>
                )}
              </div>
              {urlState.status && (
                <div
                  className={`rounded-xl border px-4 py-3 text-sm ${
                    urlState.status.type === "success"
                      ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                      : "border-rose-200 bg-rose-50 text-rose-600"
                  }`}
                >
                  <p className="font-medium">{urlState.status.message}</p>
                  {urlState.status.warnings?.length ? (
                    <ul className="mt-2 space-y-1 text-xs text-amber-600">
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
              className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
            >
              <div>
                <h3 className="text-sm font-semibold text-slate-900">
                  Upload PDF documents
                </h3>
                <p className="text-xs text-slate-500">
                  Drop contract PDFs, operating manuals, or reports to keep the
                  knowledge base fresh.
                </p>
              </div>
              <label
                htmlFor="pdf-upload"
                className="flex h-32 cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 text-sm text-slate-500 transition hover:border-blue-400 hover:bg-blue-50"
              >
                <ToyBrick className="h-6 w-6 text-blue-500" />
                <span className="font-medium text-slate-700">
                  Select PDF files
                </span>
                <span className="text-xs text-slate-400">
                  Supports multiple uploads
                </span>
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
                <ul className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-600">
                  {pdfState.files.map((file) => (
                    <li key={file.name} className="flex justify-between">
                      <span className="truncate">{file.name}</span>
                      <span className="pl-2 text-slate-400">
                        {formatFileSize(file.size)}
                      </span>
                    </li>
                  ))}
                </ul>
              )}
              <div className="flex flex-wrap items-center justify-between gap-3">
                <button
                  className="flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-blue-300"
                  type="submit"
                  disabled={pdfState.pending}
                >
                  {pdfState.pending ? "Uploading…" : "Ingest PDFs"}
                </button>
                {pdfState.pending && (
                  <span className="text-sm text-slate-500">
                    Computing embeddings…
                  </span>
                )}
              </div>
              {pdfState.status && (
                <div
                  className={`rounded-xl border px-4 py-3 text-sm ${
                    pdfState.status.type === "success"
                      ? "border-emerald-200 bg-emerald-50 text-emerald-700"
                      : "border-rose-200 bg-rose-50 text-rose-600"
                  }`}
                >
                  <p className="font-medium">{pdfState.status.message}</p>
                  {pdfState.status.warnings?.length ? (
                    <ul className="mt-2 space-y-1 text-xs text-amber-600">
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
