import json
from contextlib import nullcontext as does_not_raise
from unittest.mock import Mock

import pytest

from game.language.exceptions import (
    ActionNotPresentInResponseError,
    ResponseIsNoneError,
)
from game.language.function_calling_language import AgentFunctionCallingActionLanguage

EXPECTED_EXTRACTED_TOOL = {
    "tool": "user_input",
    "args": {"message": "How can I help you today?"},
}


@pytest.fixture
def dummy_goal():
    return Mock(name="Goal", description="Find the answer to a question")


@pytest.fixture
def dummy_memory():
    mock_memory = Mock()
    mock_memory.get_memories.return_value = [
        {"type": "user", "content": "What is the capital of France?"},
        {"type": "assistant", "content": "The capital of France is Paris."},
        {"type": "environment", "content": "Confirmed Paris is the capital."},
    ]
    return mock_memory


@pytest.fixture
def lang():
    return AgentFunctionCallingActionLanguage()


def test_format_memory(lang, dummy_memory):
    formatted = lang._format_memory(dummy_memory)
    assert len(formatted) == 3
    assert formatted[0]["role"] == "user"
    assert formatted[1]["role"] == "assistant"
    assert formatted[2]["role"] == "user"  # environment is mapped to user


@pytest.mark.parametrize(
    "response,exception",
    [
        ("Hi", pytest.raises(ActionNotPresentInResponseError)),
        (json.dumps(EXPECTED_EXTRACTED_TOOL), does_not_raise()),
        (None, pytest.raises(ResponseIsNoneError)),
    ],
)
def test_agent_json_function_calling_action_language_parse_response(
    response: str, exception: Exception
):
    language = AgentFunctionCallingActionLanguage()
    with exception:
        parsed_response = language.parse_response(response)
        assert parsed_response == EXPECTED_EXTRACTED_TOOL


def test_parse_response_valid(lang):
    valid_response = json.dumps(
        {"name": "search", "arguments": {"query": "weather in Berlin"}}
    )
    parsed = lang.parse_response(valid_response)
    assert parsed["name"] == "search"
    assert parsed["arguments"]["query"] == "weather in Berlin"
