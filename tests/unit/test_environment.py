from game.action import tool
from game.action.context import ActionContext
from game.action.python_registry import PythonActionRegistry
from game.environment import Environment


def test_environment_execute_action():
    env = Environment()
    action_context = ActionContext()

    @tool()
    def my_tool(arg1: str, action_context: ActionContext) -> str:
        """"""
        return f"Action executed with {arg1} and {action_context.context_id}"

    action_registry = PythonActionRegistry(tools=[my_tool])
    action = action_registry.get_action("my_tool")

    result = env.execute_action(
        action_context=action_context,
        action=action,
        args={"arg1": "test", "action_context": action_context},
    )
    assert "Action executed with test" in result["result"]
