# Load model directly
from transformers import AutoModelForSequenceClassification
import torch
import logging


class Reranker:
    def __init__(self, config):
        self.config = config
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.config.reranker_model,
            torch_dtype="auto",
            trust_remote_code=True,
        )
        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "mps" if torch.backends.mps.is_available() else "cpu"
        )
        self.model.to(self.device)
        self.model.eval()
        logging.info(f"Reranker model loaded on {self.device}")

    def rerank(self, query, documents, top_k):
        document_texts = [doc["document"] for doc in documents]

        try:
            result = self.model.rerank(
                query,
                document_texts,
                max_query_length=512,
                max_length=1024,
                top_n=top_k,
            )
            for item in result:
                if "index" in item:
                    item["index"] = int(item["index"])
            return result
        except Exception as e:
            logging.error(f"Error during reranking: {e}")
