"""
Now, we are going to put the components together into a reusable agent class.
This class will encapsulate the GAME components and provide a simple interface for running the agent loop.
The agent will be responsible for constructing prompts, executing actions, and managing memory. We can create
different agents simply by changing the goals, actions, and environment without modifying the core loop.


https://www.coursera.org/learn/ai-agents-python/ungradedWidget/h7RLK/agent-loop-customization
"""

import json
import time
import uuid
from json import JSONDecodeError
from typing import Callable, Optional, Union

import game.action.library.multi_agent as multi_agent_communication
from game.action import Action
from game.action.context import ActionContext
from game.action.library.default import terminate
from game.action.python_registry import PythonActionRegistry
from game.action.registry import ActionRegistry
from game.environment import Environment
from game.goal import Goal
from game.language.base import AgentLanguage
from game.language.exceptions import (
    ActionNotPresentInResponseError,
    ResponseIsNoneError,
)
from game.llm.base import Llm
from game.llm.litellm_completion import LiteLlm
from game.logger import get_logger
from game.memory.base import Memory
from game.memory.dict_memory import DictMemory
from game.prompt import Prompt
from game.settings import get_settings
from game.utils.logs import log_memory

logger = get_logger(__name__)

settings = get_settings()


class AgentRegistry:
    def __init__(self, managed_agents: Optional[list["Agent"]]):
        self.agents = {}

        if managed_agents:
            for agent in managed_agents:
                self.register_agent(agent)

    def register_agent(self, agent: "Agent"):
        """Register an agent's run function."""
        self.agents[agent.name] = agent

    def get_agent(self, name: str) -> Optional["Agent"]:
        """Get an agent's run function by name."""
        return self.agents.get(name)

    def get_agent_descriptions(self) -> list[dict[str, str]]:
        """Returns a list of string descriptions (name: description) of the managed agents"""
        descriptions = []
        for name, agent in self.agents.items():
            descriptions.append({name: agent.description})
        return descriptions


class Agent:
    def __init__(
        self,
        goals: list[Goal],
        agent_language: AgentLanguage,
        tools: Optional[list[Action]] = None,
        environment: Optional[Environment] = None,
        llm: Optional[Llm] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        max_iterations: int = 50,
        managed_agents: Optional[list["Agent"]] = None,
        multi_agents_memory_model: Union[
            Action, Callable
        ] = multi_agent_communication.call_agent_memory_handoff,
        debug_log_memory: bool = True,
    ):
        """
        Initialize an agent with its core GAME components and capabilities.

        Goals, Actions, Memory, and Environment (GAME) form the core of the agent,
        while capabilities provide ways to extend and modify the agent's behavior.

        Args:
            goals: What the agent aims to achieve
            agent_language: How the agent formats and parses LLM interactions
            tools: Available tools the agent can use
            llm: A class responsible for making calls to the LLM
            environment: Manages tool execution and results
            managed_agents: An optional list of AI agents to manage
            multi_agents_memory_model: The memory model used between the managed agents and the coordinator agent
            max_iterations: Maximum number of action loops
            debug_log_memory: If set to `True` it will print the memory of the agent right before it terminates using
                the logger.
        """
        self.goals = goals
        self.agent_language = agent_language
        self.llm = llm or LiteLlm.from_settings()
        self.tools = tools or []
        if managed_agents:
            self.tools.append(multi_agents_memory_model)

        # if there isn't any terminal tool, add a basic one
        if not any([t.terminal for t in self.tools]):
            logger.debug(
                f"No terminal tool provided, using the default one '{terminate}'"
            )
            self.tools.append(terminate)

        self.agent_registry = AgentRegistry(managed_agents) if managed_agents else None

        self.actions = PythonActionRegistry(self.tools)
        self.environment = environment or Environment()
        self.max_iterations = max_iterations
        self.debug_log_memory = debug_log_memory

        self._name = name or str(uuid.uuid4())
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        if self._description:
            return self._description
        goals = sorted(self.goals, key=lambda g: g.priority)
        str_goals = "\n".join([f"- {g.name}: {g.description}" for g in goals])
        return f"{str_goals}"

    def __repr__(self):
        return f"Agent(name='{self.name}, description='{self.description}')"

    def _construct_prompt(
        self,
        goals: list[Goal],
        memory: Memory,
        actions: ActionRegistry,
    ) -> Prompt:
        """Build prompt with memory context"""
        return self.agent_language.construct_prompt(
            actions=actions.get_actions(),
            goals=goals,
            memory=memory,
            managed_agent_descriptions=(
                self.agent_registry.get_agent_descriptions()
                if self.agent_registry
                else None
            ),
        )

    def _get_action(self, response) -> tuple[Action, dict]:
        """
        Uses the agent language to parse the response and return the action

        Args:
            response: The LLM response as a string

        Returns:
            A tuple of the Action object and the deserialized `response` as dictionary
        """
        invocation = self.agent_language.parse_response(response)
        action = self.actions.get_action(invocation["tool"])
        logger.debug(
            f"Getting action for agent '{self.name}' for {response=} is {invocation=} {action=}"
        )
        return action, invocation

    def _should_terminate(self, response: str) -> bool:
        """
        Checks weather the agent loop should terminate based on the action taken from the `response`

        Args:
            response: The LLM response as a string

        Returns:
        `True` if the `Action` is terminal, `False` otherwise

        """
        try:
            action_def, _ = self._get_action(response)
            should_terminate_based_action = action_def.terminal if action_def else False
            logger.debug(
                f"Checking termination condition for agent '{self.name}': {should_terminate_based_action}"
            )
            return should_terminate_based_action
        except Exception as e:
            logger.error(
                f"'should_terminate' failed for for agent '{self.name}' response={response} with error: {e.__class__.__name__}('{str(e)}')"
            )
            return False

    @staticmethod
    def _update_memory(memory: Memory, response: str, result: dict) -> None:
        """Update memory with the agent's decision and the environment's response."""
        new_memories = [
            {"type": "assistant", "content": response},
            {"type": "environment", "content": json.dumps(result)},
        ]
        for m in new_memories:
            memory.add_memory(m)

    def _prompt_llm_for_action(self, full_prompt: Prompt) -> str:
        """Invokes the LLM with the `prompt` and returns the response as a string."""
        logger.debug(f"Agent '{self.name}' thinking...")
        response = self.llm(full_prompt)
        logger.debug(f"Agent '{self.name}' response: {response}")
        return response

    def _handle_agent_response(
        self, action_context: ActionContext, response: str
    ) -> dict:
        """
        Executes an `Action` from the parsed LLM `response` string.
        Args:
            action_context:
            response: The LLM response as a string

        Returns:
            The result of the executed `Action` as dictionary
        """
        error_message = (
            f"get_action failed for response={response} with error: ".replace("\n", "")
        )
        result_in_case_of_error = {"tool_executed": False}
        try:
            action_def, action = self._get_action(response)
            logger.info(f"Agent '{self.name}' executing action={action_def} {action=}")
            result = self.environment.execute_action(
                action_context, action_def, action["args"]
            )
        except ActionNotPresentInResponseError as e:
            error_str = f"{e.__class__.__name__}('{str(e)}')"
            logger.error(f"Agent '{self.name}' " + error_message + error_str)
            result = {
                **result_in_case_of_error,
                "error": error_str
                + f" Use one of the available tools: {[f'{a.name}: {a.description}' for a in self.tools]}",
            }
        except ResponseIsNoneError as e:
            error_str = f"{e.__class__.__name__}('{str(e)}')"
            logger.error(f"Agent '{self.name}' " + error_message + error_str)
            result = {
                **result_in_case_of_error,
                "error": error_str
                + f" Failed to receive response from LLM. Use one of the available tools: {[f'{a.name}: {a.description}' for a in self.tools]}",
            }
        except JSONDecodeError as e:
            error_str = f"{e.__class__.__name__}('{str(e)}')"
            logger.error(f"Agent '{self.name}' " + error_message + error_str)
            result = {**result_in_case_of_error, "error": error_str}
        except Exception as e:
            error_str = f"{e.__class__.__name__}('{str(e)}')"
            logger.error(f"Agent '{self.name}' " + error_message + error_str)
            raise
        return result

    def run(
        self,
        user_input: str,
        memory: Optional[Memory] = None,
        action_context_props: Optional[dict] = None,
    ) -> Memory:
        """
        Execute the GAME loop for this agent with a maximum iteration limit.

        Args:
            user_input: The initial user message request
            memory: An optional `Memory` object. If `None` an in-memory dictionary based memory will be used
            action_context_props: Additional optional parameters as a dictionary that are appended to the
                `ActionContext` object. The `ActionContext` is passed as an optional hidden argument to the tools

        Returns:
            The `Memory` object of the agent with all messages when the agent terminates
        """
        memory = memory or DictMemory()
        # Set's initial `user_input` as the current task
        memory.add_memory({"type": "user", "content": user_input})

        action_context_props = action_context_props or {}
        # Create context with all necessary resources
        action_context = ActionContext(
            {
                "name": self.name,
                "memory": memory,
                "llm": self.llm,
                "agent_registry": self.agent_registry,
                **action_context_props,
            }
        )

        # The agent loop
        for _ in range(self.max_iterations):
            tic = time.time()
            # Construct a prompt that includes the Goals, Actions, and the current Memory
            prompt = self._construct_prompt(self.goals, memory, self.actions)
            # Generate a response from the agent
            response = self._prompt_llm_for_action(prompt)
            # # Determine which action the agent wants to execute and execute it in the environment
            result = self._handle_agent_response(
                action_context=action_context, response=response
            )
            # Update the agent's memory with information about what happened
            self._update_memory(memory, response, result)
            # Check if the agent has decided to terminate
            if self._should_terminate(response):
                break
            logger.debug(
                f"Agent '{self.name}' iteration took {time.time()-tic} seconds"
            )

            # This is to prevent rate limits of the LLMs
            if sleep_for := settings.AGENT_SLEEP_SECS:
                logger.debug(f"Agent '{self.name}' sleeping for {sleep_for} seconds")
                time.sleep(sleep_for)

        if self.debug_log_memory:
            log_memory(memory, agent_name=self.name, agent_description=self.description)
        return memory
