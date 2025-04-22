import logging
import requests
from typing import Optional, Any


class Reranker:
    def __init__(self, config):
        self.config = config
        self.base_url = config.reranker_base_url
        self.model = config.reranker_model
        self.api_key = config.reranker_api_key

    def rerank(self, query, documents, top_k) -> Optional[dict[str, Any]]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        doc_texts = [doc["document"] for doc in documents]
        data = {
            "model": self.model,
            "query": query,
            "top_n": top_k,
            "documents": doc_texts,
            "return_documents": False,
        }
        try:
            response = requests.post(self.base_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error during reranking API call: {e}")
            return None
