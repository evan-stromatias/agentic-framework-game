"""E - Environment Implementation

In our original implementation, we hardcoded our “environment” interface as a series of if/else statements
and function calls. We would like to have a more modular interface that allows us to execute actions without
needing to know how they are implemented or have conditional logic in the loop. This is where the Environment
component comes in. It serves as a bridge between the agent and the outside world, executing actions and
returning results.

https://www.coursera.org/learn/ai-agents-python/ungradedWidget/3d8su/modular-ai-agent-design
"""

import inspect
import time
from typing import Any

from game.action import Action
from game.action.context import ActionContext


def has_named_parameter(func, param_name: str) -> bool:
    """Check if a function has a named parameter."""
    try:
        signature = inspect.signature(func)
        return param_name in signature.parameters
    except (ValueError, TypeError):
        return False


class Environment:
    def execute_action(
        self, action_context: ActionContext, action: Action, args: dict
    ) -> dict:
        """Execute an action with automatic dependency injection."""
        try:
            # Create a copy of args to avoid modifying the original
            args_copy = args.copy()

            # If the function wants action_context, provide it
            if has_named_parameter(action.function, "action_context"):
                args_copy["action_context"] = action_context

            # Inject properties from action_context that match _prefixed parameters
            for param_name, value in action_context.properties.items():
                # param_name = "_" + key
                if has_named_parameter(action.function, param_name):
                    args_copy[param_name] = value

            # Execute the function with injected dependencies
            result = action.execute(**args_copy)
            return self.format_result(result, action)
        except Exception as e:
            return {"tool_executed": False, "action": None, "error": str(e)}

    @staticmethod
    def format_result(result: Any, action: Action) -> dict:
        """Format the result with metadata."""
        return {
            "tool_executed": True,
            "action": action.name,
            "result": result,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
