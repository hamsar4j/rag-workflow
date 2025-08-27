from openai import OpenAI
from typing import Optional, Any
import json
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with LLM APIs through OpenAI-compatible interface."""

    def __init__(self, config: Any):
        self.config = config
        self.base_url = self.config.llm_base_url
        self.api_key = self.config.llm_api_key
        self.model = self.config.llm_model
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def chat_completion(self, prompt: str) -> Optional[dict[str, Any]]:
        """Generate a chat completion response from the LLM."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            response_text = response.choices[0].message.content
            if response_text is None:
                logger.warning("Received None response from LLM")
                return None
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            return None
        except Exception as e:
            logger.error(f"Error during LLM API call: {e}")
            return None
