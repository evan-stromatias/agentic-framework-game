"""
The AgentLanguage component is crucial because it:

- Centralizes Communication Logic: All prompt construction and response parsing is in one place
- Enables Experimentation: We can try different prompt strategies by creating new language implementations
- Improves Reliability: Structured response formats and error handling make the agent more robust
- Supports Evolution: As LLM capabilities change, we can adapt our communication approach without changing the agent’s core logic

By separating the “how to communicate” from the “what to do,” we create agents that can evolve and improve their
interaction with LLMs while maintaining their core functionality. This flexibility is essential as language model
capabilities continue to advance and new communication patterns emerge.

https://www.coursera.org/learn/ai-agents-python/ungradedWidget/VNHjO/how-your-agent-communicates-with-the-llm-the-agent-language
"""

from abc import ABC, abstractmethod
from typing import Optional

from game.action import Action
from game.goal import Goal
from game.memory.base import Memory
from game.prompt import Prompt


class AgentLanguage(ABC):
    """Serves as the translator between our structured agent components and the language model’s input/output format.

    The AgentLanguage component has two primary responsibilities:
        - Prompt Construction: Transforming our GAME components into a format the LLM can understand
        - Response Parsing: Interpreting the LLM’s response to determine what action the agent should take
    """

    @abstractmethod
    def construct_prompt(
        self,
        actions: list[Action],
        goals: list[Goal],
        memory: Memory,
        managed_agent_descriptions: Optional[list[dict[str, str]]] = None,
    ) -> Prompt:
        """Transforming our GAME components into a format the LLM can understand"""

    @abstractmethod
    def parse_response(self, response: str) -> dict:
        """
        Interpreting the LLM’s response to determine what action the agent should take
        Args:
            response:

        Returns:
            A dictionary with {"tool": "TOOL_NAME", "args": {"message": response}}

        Raises:
            ActionNotPresentInResponseError: When no tool is provided in the response
            JSONDecodeError: When it cannot decode the json in the response
        """
