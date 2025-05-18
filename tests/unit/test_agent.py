from typing import List, Optional

import pytest

from game.action import Action, tool
from game.action.context import ActionContext
from game.action.python_registry import PythonActionRegistry
from game.action.registry import ActionRegistry
from game.agent import Agent
from game.environment import Environment
from game.goal import Goal
from game.language.base import AgentLanguage
from game.llm.base import Llm
from game.memory import Memory
from game.memory.dict_memory import DictMemory
from game.prompt import Prompt


# Mocking external dependencies and configurations
class MockLlm(Llm):
    def __init__(self, response: str = "Mock response"):
        self._name = "MockLLM"
        self.response = response

    @property
    def name(self) -> str:
        return self._name

    def __call__(self, prompt: Prompt) -> str:
        return self.response


class MockAgentLanguage(AgentLanguage):
    def construct_prompt(
        self,
        actions: List[Action],
        goals: List[Goal],
        memory: Memory,
        managed_agent_descriptions: Optional[list[str]] = None,
    ) -> Prompt:
        return Prompt(messages=[{"role": "user", "content": "Mock prompt"}])

    def parse_response(self, response: str) -> dict:
        return {"tool": "test_action", "args": {}}


@tool(terminal=True)
def test_action() -> str:
    """A test tool."""
    return f"Tool executed"


# Fixtures
@pytest.fixture
def sample_goal():
    return Goal(priority=1, name="Test Goal", description="A test goal description.")


@pytest.fixture
def sample_action():
    def sample_function(arg1: str):
        return f"Action executed with {arg1}"

    return Action(
        name="test_action",
        function=sample_function,
        description="A test action.",
        parameters={"type": "object", "properties": {"arg1": {"type": "string"}}},
        terminal=False,
    )


@pytest.fixture
def sample_action_registry(sample_action):
    registry = ActionRegistry()
    registry.register(sample_action)
    return registry


@pytest.fixture
def sample_python_action_registry():
    @tool()
    def my_func(a: int, b: str) -> str:
        """My Function"""
        return f"{a}{b}"

    registry = PythonActionRegistry([my_func])
    return registry


@pytest.fixture
def sample_memory():
    memory = DictMemory()
    memory.add_memory({"type": "user", "content": "Initial memory."})
    return memory


@pytest.fixture
def sample_agent(sample_goal):
    return Agent(
        goals=[sample_goal],
        agent_language=MockAgentLanguage(),
        llm=MockLlm(),
        tools=[test_action],
    )


def test_agent_construct_prompt(sample_agent, sample_memory, sample_action_registry):
    prompt = sample_agent._construct_prompt(
        sample_agent.goals, sample_memory, sample_agent.actions
    )
    assert isinstance(prompt, Prompt)
    assert prompt.messages == [{"role": "user", "content": "Mock prompt"}]


def test_agent_get_action(sample_agent):
    action, invocation = sample_agent._get_action('{"tool": "test_tool", "args": {}}')
    assert action.name == "test_action"


def test_agent_should_terminate(sample_agent, sample_action):
    # Modify the action to be terminal for this test
    response = '{"tool": "test_tool", "args": {}}'
    assert sample_agent._should_terminate(response)


def test_agent_run(sample_agent, sample_memory):
    memory = sample_agent.run("Test input", memory=sample_memory)
    assert len(memory.get_memories()) > 1
