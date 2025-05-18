import pytest

from game.goal import Goal
from game.llm.base import Llm
from game.prompt import Prompt


class DummyListResponsesLlm(Llm):
    def __init__(self, responses: list[str]) -> None:
        self.responses = iter(responses)

    @property
    def name(self) -> str:
        return "TestMockLlm"

    def __call__(self, prompt: Prompt) -> str:
        return next(self.responses)


@pytest.fixture
def goals() -> list[Goal]:
    return [
        Goal(
            priority=1,
            name="Ask user questions",
            description="You are a useful AI assistant that chats with user and responds to their questions. "
            "Always respond back to the user using a tool call. ",
        ),
        Goal(
            priority=2,
            name="Terminate",
            description="Call terminate when user requests to exit and provide a summary of the discussion",
        ),
    ]


@pytest.fixture
def dummy_function_calling_responses_llm() -> Llm:
    return DummyListResponsesLlm(
        responses=[
            '{"tool": "user_input", "args": {"message": "Hi there! How can I help you today?"}}',
            '{"tool": "terminate", "args": {"message": "It was nice chatting with you. Bye"}}',
        ]
    )


@pytest.fixture
def dummy_json_action_calling_responses_llm() -> Llm:
    return DummyListResponsesLlm(
        responses=[
            """
        Hi there! How can I help you today?
        ```action
        {"tool": "user_input", "args": {"message": "Hi there! How can I help you today?"}}
        ```
        """,
            """
        It was nice chatting with you. Bye
        ```action
        {"tool": "terminate", "args": {"message": "It was nice chatting with you. Bye"}}
        ```
        """,
        ]
    )


@pytest.fixture
def dummy_json_action_calling_responses_with_errors_llm() -> Llm:
    return DummyListResponsesLlm(
        responses=[
            # action block missing, should repeat
            "Hi there! How can I help you today?",
            # incorrect action label, should repeat
            """,
        ```potato
        {"tool": "user_input", "args": {"message": "Hi there! How can I help you today?"}}
        ```
        """,
            """,
        ```tool_call
        {"tool": "user_input", "args": {"message": "Hi there! How can I help you today?"}}
        ```
        """,
            """
        It was nice chatting with you. Bye
        ```tool_code
        {"tool": "terminate", "args": {"message": "It was nice chatting with you. Bye"}}
        ```
        """,
        ]
    )
