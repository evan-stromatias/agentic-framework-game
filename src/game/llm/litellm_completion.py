"""Interact with LLMs using litellm"""

import json
from typing import Optional, Union

import litellm
from litellm import completion
from litellm.litellm_core_utils.streaming_handler import CustomStreamWrapper
from litellm.types.utils import ModelResponse

from game.llm import Llm
from game.logger import get_logger
from game.prompt import Prompt
from game.settings import Settings, get_settings

logger = get_logger(__name__)


class LiteLlm(Llm):
    def __init__(
        self,
        model: str,
        temperature: float = 0.0,
        max_reties: int = 3,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ):
        """litellm"""

        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = base_url
        self.max_retries = max_reties

    @property
    def name(self) -> str:
        return self.model

    def _run_completion(
        self, messages: list[dict], tools: Optional[list[dict]] = None
    ) -> Union[ModelResponse, CustomStreamWrapper]:
        return completion(
            model=self.model,
            messages=messages,
            tools=tools,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            api_key=self.api_key,
            base_url=self.base_url,
            max_retries=self.max_retries,
        )

    def __call__(self, prompt: Prompt) -> str:

        # if tools are provided check if the llm supports tool calling
        if prompt.tools and not litellm.supports_function_calling(model=self.model):
            raise RuntimeError(
                f"Model: '{self.name}' doesn't support tool calling and tool calling was requested!"
            )

        response = self._run_completion(messages=prompt.messages, tools=prompt.tools)
        logger.debug(response)
        if response.choices[0].message.tool_calls:
            tool = response.choices[0].message.tool_calls[0]
            result = {
                "tool": tool.function.name,
                "args": json.loads(tool.function.arguments),
            }
            result = json.dumps(result)
        else:
            result = response.choices[0].message.content

        return result

    @classmethod
    def from_settings(cls, settings: Optional[Settings] = None) -> "LiteLlm":
        """
        Instantiate a `LiteLlm` object from a `settings` object.
        Args:
            settings: An optional `Settings` object. If `None` it will contract a new `settings` objects from the
                env variables.
        Returns:
            A `LiteLlm` object.
        """
        settings = settings or get_settings()
        return cls(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.LLM_API_KEY,
            max_reties=settings.LITE_LLM_MAX_RETRIES,
            base_url=settings.LLM_BASE_URL,
            max_tokens=settings.LLM_MAX_TOKENS,
        )
