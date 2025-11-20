import logging
from typing import Any, Optional

import requests


class Reranker:
    """Client for interacting with reranking APIs."""

    def __init__(self, config: Any):
        self.config = config
        self.base_url = config.reranker_base_url
        self.model = config.reranker_model
        self.api_key = config.reranker_api_key

    def rerank(
        self, query: str, documents: list[dict[str, Any]], top_k: int
    ) -> Optional[dict[str, Any]]:
        """Rerank documents based on their relevance to a query."""

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
            response = requests.post(
                self.base_url, headers=headers, json=data, timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error during reranking API call: {e}")
            return None
        except Exception as e:
            logging.error(f"Error during reranking API call: {e}")
            return None
