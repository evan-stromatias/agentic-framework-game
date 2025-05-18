"""Function Calling Language

Uses the LLM’s function calling capabilities to directly specify actions.
This approach helps alleviate the burden of parsing free-form text. The downside is that we don’t necessarily get
to see the LLM’s reasoning, but the upside is that it simplifies getting valid JSON as output.

https://www.coursera.org/learn/ai-agents-python/ungradedWidget/VNHjO/how-your-agent-communicates-with-the-llm-the-agent-language
"""

import json
from json import JSONDecodeError
from typing import Any, List, Optional

from game.action import Action
from game.goal import Goal
from game.language.base import AgentLanguage
from game.language.common import format_goals, format_managed_agents
from game.language.exceptions import (
    ActionNotPresentInResponseError,
    ResponseIsNoneError,
)
from game.logger import get_logger
from game.memory.base import Memory
from game.prompt import Prompt

logging = get_logger(__name__)


class AgentFunctionCallingActionLanguage(AgentLanguage):
    """
    This language uses the LLM’s function calling capabilities to directly specify actions.
    This approach helps alleviate the burden of parsing free-form text.
    The downside is that we don’t necessarily get to see the LLM’s reasoning,
    but the upside is that it simplifies getting valid JSON as output.

    The AgentLanguage will:
        1. Format our goals as system messages
        2. Present our actions as function definitions
        3. Maintain conversation history in the memory
        4. Parse function calls from the LLM’s responses
    """

    def __init__(self):
        super().__init__()

    def _format_goals_agents(
        self,
        goals: list[Goal],
        actions: list[Action],  # TODO
        managed_agent_descriptions: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        # Map all goals to a single string that concatenates their description
        # and combine into a single message of type system
        available_actions_str = "\n".join(
            [f"\t- {a.name}: {a.description}" for a in actions]
        )
        available_actions_str = f"\nAvailable Tools: \n{available_actions_str}\n"

        return [
            {
                "role": "system",
                "content": format_goals(goals)
                + format_managed_agents(managed_agent_descriptions),
                # + available_actions_str,
            }
        ]

    @staticmethod
    def _format_memory(memory: Memory) -> List:
        """Generate response from language model"""
        # Map all environment results to a role:user messages
        # Map all assistant messages to a role:assistant messages
        # Map all user messages to a role:user messages
        items = memory.get_memories()
        mapped_items = []
        for item in items:

            content = item.get("content", None)
            if not content:
                content = json.dumps(item, indent=4)

            if item["type"] == "assistant":
                mapped_items.append({"role": "assistant", "content": content})
            elif item["type"] == "environment":
                # here: https://www.coursera.org/learn/ai-agents-python/ungradedWidget/VCvzH/ai-agent-feedback-and-memory
                ##   type: is user
                #    also here: https://www.coursera.org/learn/ai-agents-python/lecture/9r3Ux/gail-goals-actions-information-language
                #    also here: https://www.coursera.org/learn/ai-agents-python/lecture/034la/tool-results-and-agent-feedback
                mapped_items.append({"role": "user", "content": content})
            else:
                mapped_items.append({"role": "user", "content": content})

        return mapped_items

    @staticmethod
    def _format_actions(
        actions: List[Action], description_max_size: int = 1024
    ) -> list[dict]:
        """Generate response from language model"""

        tools = [
            {
                "type": "function",
                "function": {
                    "name": action.name,
                    # Include up to 1024 characters of the description
                    "description": action.description[:description_max_size],
                    "parameters": action.parameters,
                },
            }
            for action in actions
        ]

        return tools

    def construct_prompt(
        self,
        actions: list[Action],
        goals: list[Goal],
        memory: Memory,
        managed_agent_descriptions: Optional[list[str]] = None,
    ) -> Prompt:

        prompt = []
        prompt += self._format_goals_agents(goals, actions, managed_agent_descriptions)
        tools = self._format_actions(actions)
        prompt += self._format_memory(memory)

        return Prompt(
            messages=prompt,
            tools=tools,
            managed_agent_descriptions=managed_agent_descriptions,
        )

    def parse_response(self, response: str) -> dict:
        """
        Parse LLM response into structured format by extracting the action
        Args:
            response: The raw response from the LLM as a string

        Returns:
            A dictionary with the action call.
        Raises:
            ActionNotPresentInResponseError: If no tool call (serialized dict) is present in the `response`.
        """
        try:
            return json.loads(response)
        except JSONDecodeError:
            logging.debug(f"No tool call specified in response='{response}'")
            raise ActionNotPresentInResponseError(
                "No tool call specified, please provide a tool call"
            )
        except Exception as e:
            error_message = (
                f"Failed to parse action in response='{response}'. "
                f"Error: {e.__class__.__name__}('{e}')"
            )
            logging.error(error_message)
            raise ResponseIsNoneError(error_message)
