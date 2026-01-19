"use client";

import {
  ChangeEvent,
  FormEvent,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  IngestionResponse,
  IngestionStatus,
  KnowledgeDocument,
} from "../types/dashboard";
import { deriveNameFromUrl, formatFileSize } from "../utils/formatters";
import { createId } from "../utils/id";

type UseKnowledgeBaseOptions = {
  apiBase: string;
};

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

export function useKnowledgeBase({ apiBase }: UseKnowledgeBaseOptions) {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [collectionName, setCollectionName] = useState<string | null>(null);

  const [urlState, setUrlState] = useState<UrlState>({
    input: "",
    pending: false,
    status: null,
  });

  const [pdfState, setPdfState] = useState<PdfState>({
    files: [],
    pending: false,
    status: null,
  });

  const filteredDocs = useMemo(() => {
    const term = searchTerm.trim().toLowerCase();
    if (!term) {
      return documents;
    }
    return documents.filter((doc) => {
      if (doc.name.toLowerCase().includes(term)) {
        return true;
      }
      return doc.tags.some((tag) => tag.toLowerCase().includes(term));
    });
  }, [documents, searchTerm]);

  const validSelectedDocIds = useMemo(
    () => selectedDocIds.filter((id) => documents.some((doc) => doc.id === id)),
    [documents, selectedDocIds],
  );

  const allFilteredSelected =
    filteredDocs.length > 0 &&
    filteredDocs.every((doc) => validSelectedDocIds.includes(doc.id));

  const usagePercent = Math.min(documents.length, 100);

  const updateUrlState = useCallback(
    (next: Partial<UrlState>) =>
      setUrlState((prev) => ({
        ...prev,
        ...next,
      })),
    [],
  );

  const updatePdfState = useCallback(
    (next: Partial<PdfState>) =>
      setPdfState((prev) => ({
        ...prev,
        ...next,
      })),
    [],
  );

  const addDocuments = useCallback((nextDocs: KnowledgeDocument[]) => {
    setDocuments((prev) => [...nextDocs, ...prev]);
  }, []);

  useEffect(() => {
    let cancelled = false;

    const fetchCollectionName = async () => {
      try {
        const response = await fetch(`${apiBase}/health`);
        if (!response.ok) {
          return;
        }
        const payload = (await response.json().catch(() => null)) as {
          postgres_table?: string;
        } | null;
        if (!cancelled && payload && typeof payload === "object") {
          const name = payload.postgres_table;
          if (typeof name === "string" && name.trim().length > 0) {
            setCollectionName(name);
          }
        }
      } catch {
        // Silently ignore health fetch errors; UI can function without metadata.
      }
    };

    fetchCollectionName();

    return () => {
      cancelled = true;
    };
  }, [apiBase]);

  const handleUrlSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (urlState.pending) return;

    const urls = urlState.input
      .split(/[\r\n,]+/)
      .map((url) => url.trim().replace(/^["']|["']$/g, ""))
      .filter((url) => url.length > 0 && url.startsWith("http"));

    if (urls.length === 0) {
      updateUrlState({
        status: {
          type: "error",
          message: "Enter at least one URL to ingest.",
        },
      });
      return;
    }

    updateUrlState({ pending: true, status: null });

    try {
      const response = await fetch(`${apiBase}/ingest/web`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ urls }),
      });

      const payload = (await response.json().catch(() => null)) as
        | (IngestionResponse & { detail?: never })
        | { detail?: string }
        | null;

      if (
        !response.ok ||
        !payload ||
        typeof payload !== "object" ||
        !("chunk_count" in payload)
      ) {
        const detail =
          payload && typeof payload === "object" && "detail" in payload
            ? payload.detail
            : null;
        throw new Error(
          typeof detail === "string"
            ? detail
            : `API returned status ${response.status}`,
        );
      }

      const warnings =
        payload.warnings?.filter((warning) => warning.trim().length > 0) ?? [];

      const createdDocs = urls.map<KnowledgeDocument>((url) => ({
        id: createId(),
        name: deriveNameFromUrl(url),
        sourceType: "URL",
        lastSync: new Date().toISOString(),
        size: "—",
        tags: ["URL"],
        status: "Ready",
      }));

      addDocuments(createdDocs);

      updateUrlState({
        input: "",
        status: {
          type: "success",
          message: `Indexed ${payload.chunk_count} chunks from ${payload.document_count} sources.`,
          warnings,
        },
      });
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Failed to ingest URLs. Check the FastAPI logs for details.";
      updateUrlState({
        status: {
          type: "error",
          message,
        },
      });
    } finally {
      updateUrlState({ pending: false });
    }
  };

  const handlePdfSelection = (event: ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) {
      updatePdfState({ files: [] });
      return;
    }
    updatePdfState({ files: Array.from(files), status: null });
    // Allow re-selecting identical files
    event.target.value = "";
  };

  const handlePdfSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (pdfState.pending) return;
    const formElement = event.currentTarget;

    const stagedFiles = [...pdfState.files];
    if (stagedFiles.length === 0) {
      updatePdfState({
        status: {
          type: "error",
          message: "Attach at least one PDF to ingest.",
        },
      });
      return;
    }

    updatePdfState({ pending: true, status: null });

    const formData = new FormData();
    stagedFiles.forEach((file) => formData.append("files", file));

    try {
      const response = await fetch(`${apiBase}/ingest/pdf`, {
        method: "POST",
        body: formData,
      });

      const payload = (await response.json().catch(() => null)) as
        | (IngestionResponse & { detail?: never })
        | { detail?: string }
        | null;

      if (
        !response.ok ||
        !payload ||
        typeof payload !== "object" ||
        !("chunk_count" in payload)
      ) {
        const detail =
          payload && typeof payload === "object" && "detail" in payload
            ? payload.detail
            : null;
        throw new Error(
          typeof detail === "string"
            ? detail
            : `API returned status ${response.status}`,
        );
      }

      const warnings =
        payload.warnings?.filter((warning) => warning.trim().length > 0) ?? [];

      const createdDocs = stagedFiles.map<KnowledgeDocument>((file) => ({
        id: createId(),
        name: file.name || "Uploaded Document.pdf",
        sourceType: "PDF",
        lastSync: new Date().toISOString(),
        size: formatFileSize(file.size),
        tags: ["Document"],
        status: "Ready",
      }));

      addDocuments(createdDocs);

      updatePdfState({
        files: [],
        status: {
          type: "success",
          message: `Indexed ${payload.chunk_count} chunks from ${payload.document_count} PDF${payload.document_count === 1 ? "" : "s"}.`,
          warnings,
        },
      });
      formElement.reset();
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Failed to ingest PDFs. Check the FastAPI logs for details.";
      updatePdfState({
        status: {
          type: "error",
          message,
        },
      });
    } finally {
      updatePdfState({ pending: false });
    }
  };

  const toggleDocumentSelection = (id: string) => {
    setSelectedDocIds((prev) =>
      prev.includes(id) ? prev.filter((docId) => docId !== id) : [...prev, id],
    );
  };

  const toggleAllDocuments = (checked: boolean) => {
    if (checked) {
      setSelectedDocIds((prev) => {
        const combined = new Set([
          ...prev,
          ...filteredDocs.map((doc) => doc.id),
        ]);
        return Array.from(combined);
      });
      return;
    }
    setSelectedDocIds((prev) =>
      prev.filter((docId) => !filteredDocs.some((doc) => doc.id === docId)),
    );
  };

  return {
    documents,
    filteredDocs,
    searchTerm,
    setSearchTerm,
    selectedDocIds: validSelectedDocIds,
    toggleDocumentSelection,
    toggleAllDocuments,
    allFilteredSelected,
    usagePercent,
    collectionName,
    urlState,
    setUrlInput: (value: string) => updateUrlState({ input: value }),
    handleUrlSubmit,
    pdfState,
    handlePdfSelection,
    handlePdfSubmit,
  };
}
