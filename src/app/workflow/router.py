import json
import logging
from typing import Any, Optional, Union

from openai import OpenAI
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with LLM APIs through OpenAI-compatible interface."""

    def __init__(self, config: Any):
        self.config = config
        self.base_url = self.config.llm_base_url
        self.api_key = self.config.llm_api_key
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def chat_completion(
        self,
        prompt: str,
        response_model: type[BaseModel] | None = None,
        model_override: str | None = None,
    ) -> Optional[Union[dict[str, Any], BaseModel]]:
        """Generate a chat completion response from the LLM.

        Args:
            prompt: User prompt or an iterable of preconstructed chat messages.
            response_model: Optional Pydantic model describing the expected
                structured output. When provided, the model's schema is supplied
                to the API and the validated model instance is returned. When
                omitted, the response is parsed into a plain dictionary via
                JSON auto mode.
            model_override: Optional model identifier to use for this request.
        """

        if response_model is not None:
            response_format = {
                "type": "json_schema",
                "schema": response_model.model_json_schema(),
            }
        else:
            response_format = "auto"

        model = model_override or self.config.llm_model

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format=response_format,
            )
            response_text = response.choices[0].message.content
            if response_text is None:
                logger.warning("Received None response from LLM")
                return None

            if response_model is not None:
                try:
                    return response_model.model_validate_json(response_text)
                except ValidationError as e:
                    logger.error(f"Structured output validation failed: {e}")
                    return None

            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            return None
        except Exception as e:
            logger.error(f"Error during LLM API call: {e}")
            return None
