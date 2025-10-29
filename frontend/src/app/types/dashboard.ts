export type TabKey = "chat" | "knowledge-base";

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
};

export type IngestionResponse = {
  chunk_count: number;
  document_count: number;
  warnings?: string[];
};

export type IngestionStatus = {
  type: "success" | "error";
  message: string;
  warnings?: string[];
};

export type KnowledgeDocument = {
  id: string;
  name: string;
  sourceType: "URL" | "PDF" | "Document";
  lastSync: string;
  size: string;
  tags: string[];
  status: "Ready" | "Processing" | "Failed";
};
