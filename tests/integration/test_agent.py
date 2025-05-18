import pytest

from game.action import tool
from game.action.context import ActionContext
from game.action.library.default import terminate
from game.agent import Agent
from game.goal import Goal
from game.language import AgentFunctionCallingActionLanguage, AgentJsonActionLanguage
from game.llm.base import Llm
from game.prompt import Prompt


@tool()
def user_input(action_context: ActionContext, message: str) -> str:
    """
    Returns the `message` back to the agent
    Args:
        action_context: Contains the action context populated by the agent (this argument is hidden)
        message: The message from the LLM

    Returns:
        User's response as a string
    """
    return f"User Reply: {message}"


def test_agent_with_function_calling(dummy_function_calling_responses_llm, goals):
    """test agent with function calling language"""
    agent = Agent(
        llm=dummy_function_calling_responses_llm,
        agent_language=AgentFunctionCallingActionLanguage(),
        tools=[user_input, terminate],
        goals=goals,
    )
    memory = agent.run("hi")
    memories = memory.get_memories()
    assert len(memories) == 5
    assert len([m for m in memories if m["type"] == "environment"]) == 2
    assert len([m for m in memories if m["type"] == "assistant"]) == 2
    assert len([m for m in memories if m["type"] == "user"]) == 1


def test_agent_with_json_action_language(
    dummy_json_action_calling_responses_llm, goals
):
    """test agent with json action calling language"""
    agent = Agent(
        llm=dummy_json_action_calling_responses_llm,
        agent_language=AgentJsonActionLanguage(),
        tools=[user_input, terminate],
        goals=goals,
    )
    memory = agent.run("hi")
    memories = memory.get_memories()
    assert len(memories) == 5
    assert len([m for m in memories if m["type"] == "environment"]) == 2
    assert len([m for m in memories if m["type"] == "assistant"]) == 2
    assert len([m for m in memories if m["type"] == "user"]) == 1


def test_agent_with_json_action_language_and_mistakes_in_response(
    dummy_json_action_calling_responses_with_errors_llm, goals
):
    """test agent with json action calling language and incorrect or missing action block"""
    agent = Agent(
        llm=dummy_json_action_calling_responses_with_errors_llm,
        agent_language=AgentJsonActionLanguage(),
        tools=[user_input, terminate],
        goals=goals,
    )
    memory = agent.run("hi")
    memories = memory.get_memories()
    assert len(memories) == 9
    assert len([m for m in memories if m["type"] == "environment"]) == 4
    assert len([m for m in memories if m["type"] == "assistant"]) == 4
    assert len([m for m in memories if m["type"] == "user"]) == 1
