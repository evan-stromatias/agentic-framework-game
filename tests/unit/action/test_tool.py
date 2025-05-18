import pytest

from game.action import Action, tool
from game.action.context import ActionContext


@tool()
def my_func(a: int, b: str) -> str:
    """
    Sample tool function that concatenates two arguments into a string
    Args:
        a: first argument
        b: second argument

    Returns:
        A string concatenation of `a` and `b`
    """
    return f"{a}{b}"


@tool()
def my_func_hidden_arguments_from_description(
    action_context: ActionContext, a: int, b: str, _hidden_arg: float
) -> str:
    """
    Sample tool function that concatenates two arguments into a string
    Args:
        a: first argument
        b: second argument

    Returns:
        A string concatenation of `a` and `b`
    """
    action_context.get("something", 0.1) + _hidden_arg
    return f"{a}{b}"


@tool()
def my_func_no_arguments() -> str:
    """DESCRIPTION"""
    return "hello"


EXPECTED_FUNC_NO_ARGUMENTS_DICT = {
    "description": "DESCRIPTION",
    "function": my_func_no_arguments.function,
    "parameters": {"properties": {}, "type": "object"},
    "terminal": False,
    "tool_name": "my_func_no_arguments",
}


EXPECTED_FUNC_DICT = {
    "description": "Sample tool function that concatenates two arguments into a "
    "string\n"
    "Args:\n"
    "a: first argument\n"
    "b: second argument",
    "function": "<FUNCTION_ADDRESS_HERE>",
    "parameters": {
        "properties": {"a": {"type": "integer"}, "b": {"type": "string"}},
        "required": ["a", "b"],
        "type": "object",
    },
    "terminal": False,
    "tool_name": "<FUNCTION_NAME_HERE>",
}


@pytest.mark.parametrize(
    "decorated_tool_function,expected_function_dict",
    [
        (my_func_no_arguments, EXPECTED_FUNC_NO_ARGUMENTS_DICT),
        (my_func, EXPECTED_FUNC_DICT),
        (my_func_hidden_arguments_from_description, EXPECTED_FUNC_DICT),
    ],
)
def test_tool_decorator(decorated_tool_function: Action, expected_function_dict: dict):
    expected_function_dict["tool_name"] = decorated_tool_function.name
    expected_function_dict["function"] = decorated_tool_function.function

    assert isinstance(decorated_tool_function, Action)
    assert decorated_tool_function.to_dict() == expected_function_dict
