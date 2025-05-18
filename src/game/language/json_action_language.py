"""JSON Action Language

https://www.coursera.org/learn/ai-agents-python/ungradedWidget/VNHjO/how-your-agent-communicates-with-the-llm-the-agent-language
"""

import json
from json import JSONDecodeError
from typing import Optional

from game.action import Action
from game.goal import Goal
from game.logger import get_logger
from game.memory.base import Memory
from game.prompt import Prompt

from .base import AgentLanguage
from .common import format_goals, format_managed_agents
from .exceptions import ActionNotPresentInResponseError

logger = get_logger(__name__)


ACTION_FORMAT = """
<Stop and think step by step. Insert your thoughts here.>

```action
{
    "tool": "tool_name",
    "args": {...fill in arguments...}
}
```"""


class AgentJsonActionLanguage(AgentLanguage):
    """This language allows the LLM to output text and specify actions in special ```action markdown blocks"""

    def __init__(self, action_labels: Optional[list[str]] = None):
        super().__init__()

        self.action_labels = action_labels or [
            "action",
            "tool",
            "tool_code",
            "tool_call",
            "",
        ]

    def _format_actions(self, actions: list[Action]) -> list:
        # Convert actions to a description the LLM can understand
        action_descriptions = [
            {
                "name": action.name,
                "description": action.description,
                "args": action.parameters,
            }
            for action in actions
        ]

        return [
            {
                "role": "system",
                "content": f"""
Available Tools: {json.dumps(action_descriptions, indent=4)}

{ACTION_FORMAT}
""",
            }
        ]

    def _format_goals_actions_agents(
        self,
        goals: list[Goal],
        actions: list[Action],
        managed_agents: Optional[list[str]] = None,
    ) -> list:
        # Map all goals to a single string that concatenates their description
        # and combine into a single message of type system
        available_tools = self._format_actions(actions)
        available_tools_str = "\n".join([t["content"] for t in available_tools])
        return [
            {
                "role": "system",
                "content": format_goals(goals)
                + format_managed_agents(managed_agents)
                + available_tools_str,
            }
        ]

    def format_memory(self, memory: Memory) -> list:
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

    def construct_prompt(
        self,
        actions: list[Action],
        goals: list[Goal],
        memory: Memory,
        managed_agent_descriptions: Optional[list[dict[str, str]]] = None,
    ) -> Prompt:

        prompt = []
        prompt += self._format_goals_actions_agents(
            goals, actions, managed_agent_descriptions
        )
        prompt += self.format_memory(memory)
        return Prompt(
            messages=prompt, managed_agent_descriptions=managed_agent_descriptions
        )

    def parse_response(self, response: str) -> dict:
        """
        Extract and parse the action block by attempting
        Args:
            response:

        Returns:

        """
        response_filtered = response.replace("\n", "")
        final_error_message = (
            f"Please use the following format in your responses: {ACTION_FORMAT}"
        )

        for action_label in self.action_labels:
            try:
                logger.debug(
                    f"Trying to parse response: '{response_filtered}' with '{action_label}'"
                )
                result = self._parse_response(
                    response, start_marker=f"```{action_label}", end_marker="```"
                )
                logger.debug(f"Success, the result is '{result}'")
                return result
            except ActionNotPresentInResponseError:
                logger.debug(
                    f"Failed to parse response: No '```{action_label}' found in response="
                    f"'{response_filtered}'. Trying again..."
                )
            except JSONDecodeError:
                logger.debug(
                    f"Failed to parse response: No '```{action_label}' found in response="
                    f"'{response_filtered}'. Trying again..."
                )
            except Exception as e:
                logger.debug(
                    f"Failed to parse response: '{response_filtered}'. "
                    f"Error raised: {e.__class__.__name__}('{e}'). {final_error_message}"
                )

        error_message = (
            f"Failed to parse response: '{response_filtered}'. {final_error_message}"
        )
        logger.error(error_message)
        # raise Exception(error_message)
        raise ActionNotPresentInResponseError(
            f"No action found in response. Please provide an appropriate action."
        )

    @staticmethod
    def _parse_response(response: str, start_marker: str, end_marker="```") -> dict:
        """
        Helper function that extracts the action json from an LLM response.

        Args:
            response: Response coming from the LLM
            start_marker: Start marker of the action json in the response
            end_marker: End marker of the action json in the response

        Returns:
            A dictionary of the action that was extracted from the response

        Raises:
            ActionNotPresentInResponseError: If the `start_marker` is not present in the response
            JSONDecodeError: If the json description of the action is malformed

        """
        stripped_response = response.strip()
        start_index = stripped_response.find(start_marker)

        if start_index <= -1:
            error_message = f"Error while parsing response, no '```{start_marker}' found in assistant response."
            logger.debug(error_message)
            raise ActionNotPresentInResponseError(error_message)

        if start_marker == "```":
            new_line_offset = stripped_response[start_index + len(start_marker) :].find(
                "\n"
            )
            start_index = start_index + new_line_offset

        end_index = (
            stripped_response[start_index + len(start_marker) :].find(end_marker)
            + start_index
            + len(start_marker)
        )
        json_str = stripped_response[
            start_index + len(start_marker) : end_index
        ].strip()

        return json.loads(json_str)
