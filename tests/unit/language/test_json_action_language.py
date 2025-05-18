import json

import pytest

from game.action import tool
from game.action.python_registry import PythonActionRegistry
from game.action.registry import ActionRegistry
from game.goal import Goal
from game.language import AgentJsonActionLanguage
from game.memory.dict_memory import DictMemory
from game.prompt import Prompt

EXPECTED_EXTRACTED_TOOL = {"tool": "my_tool", "args": {"arg1": "value1"}}


@pytest.fixture
def sample_goal():
    return Goal(priority=1, name="Test Goal", description="A test goal description.")


@pytest.fixture
def sample_action():
    @tool()
    def my_tool(arg1: int, b: str) -> str:
        """My Function"""
        return f"{arg1}{b}"

    action_registry = PythonActionRegistry(tools=[my_tool])
    return action_registry.get_action("my_tool")


@pytest.fixture
def sample_action_registry(sample_action):
    registry = ActionRegistry()
    registry.register(sample_action)
    return registry


@pytest.mark.parametrize(
    "action_label,should_raise_exception",
    [
        # ("action", False), ("tool", False), ("tool_code", False),
        ("", False),
        ("Potato", True),
    ],
)
def test_agent_json_action_language_parse_response(
    action_label: str, should_raise_exception: bool
):
    language = AgentJsonActionLanguage()
    response = f"""
    ```{action_label}
    {json.dumps(EXPECTED_EXTRACTED_TOOL)}
    ```
    """
    try:
        parsed_response = language.parse_response(response)
        assert parsed_response == EXPECTED_EXTRACTED_TOOL
    except Exception:
        assert should_raise_exception


def test_agent_json_action_language_construct_prompt(sample_action, sample_goal):
    language = AgentJsonActionLanguage()
    memory = DictMemory()
    # TODO fix this it should be role
    memory.add_memory({"type": "user", "content": "test memory"})
    prompt = language.construct_prompt(
        actions=[sample_action],
        goals=[sample_goal],
        memory=memory,
    )
    assert isinstance(prompt, Prompt)
    assert prompt.messages[0]["role"] == "system"
    assert prompt.messages[-1]["content"] == memory.get_memories()[-1]["content"]
