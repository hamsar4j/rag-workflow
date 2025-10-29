"use client";

import { useState } from "react";
import { ChatView } from "./components/chat/chat-view";
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

  const {
    messages,
    pending: chatPending,
    error: chatError,
    input: chatInput,
    setInput: setChatInput,
    handleSubmit: handleChatSubmit,
  } = useChat({ apiBase: API_BASE });

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
    showAddSource,
    toggleAddSource,
    urlState,
    setUrlInput,
    handleUrlSubmit,
    pdfState,
    handlePdfSelection,
    handlePdfSubmit,
  } = useKnowledgeBase({ apiBase: API_BASE });

  const knowledgeHeader = (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-2">
        <h1 className="text-xl font-semibold text-slate-900">Knowledge Base</h1>
        <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-600">
          Beta
        </span>
      </div>
      <p className="text-sm text-slate-500">
        Connect data sources to create a knowledge base for your agents
      </p>
    </div>
  );

  const chatHeader = (
    <div className="flex flex-col gap-1">
      <h1 className="text-xl font-semibold text-slate-900">Chat Console</h1>
      <p className="text-sm text-slate-500">
        Monitor conversations and test retrieval quality in real time
      </p>
    </div>
  );

  return (
    <div className="flex min-h-screen bg-[var(--surface-base)] text-slate-900">
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        usagePercent={usagePercent}
        documentCount={documents.length}
      />

      <div className="flex flex-1 flex-col">
        <header className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 bg-white px-6 py-5 lg:px-10">
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
              showAddSource={showAddSource}
              onToggleAddSource={toggleAddSource}
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
        <div className="pointer-events-none fixed right-8 bottom-8 z-20 hidden w-72 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600 shadow-lg lg:block">
          <p className="text-sm font-semibold text-slate-900">Tags assigned</p>
          <p className="mt-1 text-xs text-slate-500">
            {selectedDocIds.length} document
            {selectedDocIds.length === 1 ? "" : "s"} tagged successfully.
          </p>
        </div>
      )}
    </div>
  );
}
