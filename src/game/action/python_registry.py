from typing import Optional

from game.action.registry import Action, ActionRegistry


class PythonActionRegistry(ActionRegistry):
    def __init__(self, tools: Optional[list[Action]] = None):
        super().__init__()
        self.terminate_tool = None
        if tools:
            self.register_tools(tools)

    def register_tools(self, tools: list[Action]) -> None:
        for tool in tools:
            self.register(
                Action(
                    name=tool.name,
                    function=tool.function,
                    description=tool.description,
                    parameters=tool.parameters,
                    terminal=tool.terminal,
                )
            )

    def register_terminate_tool(self):
        if self.terminate_tool:
            self.register(
                Action(
                    name="terminate",
                    function=self.terminate_tool["function"],
                    description=self.terminate_tool["description"],
                    parameters=self.terminate_tool.get("parameters", {}),
                    terminal=self.terminate_tool.get("terminal", False),
                )
            )
        else:
            raise Exception("Terminate tool not found in tool registry")
