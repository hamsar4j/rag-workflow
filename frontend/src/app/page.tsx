"use client";

import { useEffect, useState } from "react";
import { ChatView } from "./components/chat/chat-view";
import { ModelSelect, type ModelOption } from "./components/chat/model-select";
import { KnowledgeBaseView } from "./components/knowledge/knowledge-base-view";
import { Sidebar } from "./components/sidebar";
import { useChat } from "./hooks/useChat";
import { useKnowledgeBase } from "./hooks/useKnowledgeBase";
import { TabKey } from "./types/dashboard";

const API_BASE =
  process.env.NEXT_PUBLIC_RAG_API?.replace(/\/$/, "") ??
  "http://localhost:8000";

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabKey>("chat");
  const [modelOptions, setModelOptions] = useState<ModelOption[]>([
    {
      label: "kimi-k2-instruct-0905",
      value: "moonshotai/Kimi-K2-Instruct-0905",
    },
    { label: "gpt-oss-120b", value: "openai/gpt-oss-120b" },
  ]);
  const [model, setModel] = useState<string>(modelOptions[0]?.value ?? "");
  const [modelError, setModelError] = useState<string | null>(null);
  const [isModelUpdating, setIsModelUpdating] = useState(false);

  const {
    messages,
    pending: chatPending,
    error: chatError,
    input: chatInput,
    setInput: setChatInput,
    setError: setChatError,
    handleSubmit: handleChatSubmit,
    resetConversation,
  } = useChat({ apiBase: API_BASE, model });

  const {
    documents,
    filteredDocs,
    searchTerm,
    setSearchTerm,
    selectedDocIds,
    toggleDocumentSelection,
    toggleAllDocuments,
    allFilteredSelected,
    usagePercent,
    collectionName,
    urlState,
    setUrlInput,
    handleUrlSubmit,
    pdfState,
    handlePdfSelection,
    handlePdfSubmit,
  } = useKnowledgeBase({ apiBase: API_BASE });

  useEffect(() => {
    let isMounted = true;

    const fetchActiveModel = async () => {
      try {
        const response = await fetch(`${API_BASE}/settings/model`);
        if (!response.ok) {
          throw new Error(`Failed to load model (status ${response.status})`);
        }

        const payload = (await response.json()) as { model?: string };
        const activeModel = payload.model?.trim();
        if (!isMounted || !activeModel) {
          return;
        }

        setModelOptions((prev) => {
          if (prev.some((option) => option.value === activeModel)) {
            return prev;
          }
          return [...prev, { value: activeModel, label: activeModel }];
        });
        setModel(activeModel);
        setModelError(null);
      } catch (error) {
        if (!isMounted) return;
        setModelError("Unable to load active model. Using default preset.");
      }
    };

    fetchActiveModel();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleModelChange = async (nextValue: string) => {
    if (!nextValue || nextValue === model) return;

    const previousModel = model;
    setModel(nextValue);
    setModelError(null);
    setChatError(null);
    setIsModelUpdating(true);

    try {
      const response = await fetch(`${API_BASE}/settings/model`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ model: nextValue }),
      });

      if (!response.ok) {
        throw new Error(`Failed to update model (status ${response.status})`);
      }

      const payload = (await response.json()) as { model?: string };
      const appliedModel = payload.model?.trim() || nextValue;

      setModel(appliedModel);
      setModelOptions((prev) => {
        if (prev.some((option) => option.value === appliedModel)) {
          return prev;
        }
        return [...prev, { value: appliedModel, label: appliedModel }];
      });
      resetConversation();
    } catch (error) {
      console.error("Failed to update model", error);
      setModel(previousModel);
      setModelError("Failed to update model. Please try again.");
      setChatError(
        "Switching models failed. Confirm the backend configuration and retry.",
      );
    } finally {
      setIsModelUpdating(false);
    }
  };

  const activeModelLabel =
    modelOptions.find((option) => option.value === model)?.label ?? model;

  const knowledgeHeader = (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-3">
        <h1 className="text-xl font-semibold text-(--text-primary)">
          Knowledge Base
        </h1>
        {collectionName ? (
          <span className="rounded-full border border-(--border-subtle) bg-(--surface-muted) px-3 py-1 text-xs font-semibold text-(--text-secondary) shadow-sm">
            Collection: {collectionName}
          </span>
        ) : null}
      </div>
      <p className="text-sm text-(--text-muted)">
        Connect data sources to create a knowledge base for your agents
      </p>
    </div>
  );

  const chatHeader = (
    <div className="flex w-full flex-wrap items-end justify-between gap-4">
      <div className="flex flex-col gap-1">
        <h1 className="text-xl font-semibold text-(--text-primary)">
          Chat Console
        </h1>
        <p className="text-sm text-(--text-muted)">
          Monitor conversations and test retrieval quality in real time
        </p>
      </div>
      <div className="flex flex-col items-end gap-1 text-right">
        <ModelSelect
          value={model}
          options={modelOptions}
          onChange={handleModelChange}
          disabled={chatPending}
          isUpdating={isModelUpdating}
        />
        {modelError ? (
          <span className="text-xs text-(--error)">{modelError}</span>
        ) : null}
      </div>
    </div>
  );

  return (
    <div className="flex min-h-screen bg-(--surface-base) text-(--text-primary)">
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        usagePercent={usagePercent}
        documentCount={documents.length}
      />

      <div className="flex flex-1 flex-col">
        <header className="flex flex-wrap items-center justify-between gap-4 border-b border-(--border-subtle) bg-(--surface-panel) px-6 py-5 lg:px-10">
          {activeTab === "knowledge-base" ? knowledgeHeader : chatHeader}
        </header>

        <main className="flex-1">
          {activeTab === "chat" ? (
            <ChatView
              messages={messages}
              pending={chatPending}
              error={chatError}
              input={chatInput}
              onInputChange={setChatInput}
              onSubmit={handleChatSubmit}
              modelName={activeModelLabel}
            />
          ) : (
            <KnowledgeBaseView
              filteredDocs={filteredDocs}
              searchTerm={searchTerm}
              onSearchChange={setSearchTerm}
              selectedDocIds={selectedDocIds}
              onToggleDocument={toggleDocumentSelection}
              onToggleAll={toggleAllDocuments}
              allFilteredSelected={allFilteredSelected}
              urlState={urlState}
              onUrlInputChange={setUrlInput}
              onUrlSubmit={handleUrlSubmit}
              pdfState={pdfState}
              onPdfSelection={handlePdfSelection}
              onPdfSubmit={handlePdfSubmit}
            />
          )}
        </main>
      </div>

      {activeTab === "knowledge-base" && selectedDocIds.length > 0 && (
        <div className="pointer-events-none fixed right-8 bottom-8 z-20 hidden w-72 rounded-2xl border border-(--border-subtle) bg-(--surface-panel) px-4 py-3 text-sm text-(--text-secondary) shadow-lg lg:block">
          <p className="text-sm font-semibold text-(--text-primary)">
            Tags assigned
          </p>
          <p className="mt-1 text-xs text-(--text-muted)">
            {selectedDocIds.length} document
            {selectedDocIds.length === 1 ? "" : "s"} tagged successfully.
          </p>
        </div>
      )}
    </div>
  );
}
