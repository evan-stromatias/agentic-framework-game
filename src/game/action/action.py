from typing import Any, Callable, Dict


class Action:
    """Returned when decorating a function with the @tool decorator"""

    def __init__(
        self,
        name: str,
        function: Callable,
        description: str,
        parameters: Dict,
        terminal: bool = False,
    ):
        self.name = name
        self.function = function
        self.description = description
        self.terminal = terminal
        self.parameters = parameters

    def __call__(self, *args, **kwargs) -> Any:
        """Invoke the underlying function (callable) with provided arguments."""
        return self.function(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(tool_name='{self.name}', description='{self.description.split('\n')[0]}', terminal={self.terminal}, parameters={len(self.parameters)}, function={self.function})"

    def execute(self, **args) -> Any:
        """Execute the action's function"""
        return self.function(**args)

    def to_dict(self) -> dict:
        """Return the current Action as a dictionary"""
        return {
            "tool_name": self.name or self.function.__name__,
            "description": self.description or self.function.__doc__,
            "parameters": self.parameters,
            "function": self.function,
            "terminal": self.terminal,
        }

    @classmethod
    def from_dict(cls, tool_metadata: dict) -> "Action":
        return cls(**tool_metadata)
