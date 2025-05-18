import time
from typing import Callable, Optional, TypeVar

import litellm

from game.action import Action
from game.logger import get_logger

logger = get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Action])


ACTION_CONTEXT_ARG = "action_context"
HIDDEN_ARG_START_WITH = "_"


def tool(
    tool_name: Optional[str] = None,
    description: Optional[str] = None,
    terminal: bool = False,
) -> Callable[[F], Action]:
    def decorator(func) -> Action:
        tic = time.time()
        logger.debug(f"Extracting function metadata for function {func.__name__}")

        metadata = litellm.utils.function_to_dict(func)
        if parameters := metadata.get("parameters"):
            if properties := parameters.get("properties"):
                delete_keys = [
                    k
                    for k in properties
                    if k.startswith(HIDDEN_ARG_START_WITH) or k == ACTION_CONTEXT_ARG
                ]
                logger.debug(
                    f"Removing hidden arguments from function {func.__name__}: '{delete_keys}'"
                )
                _ = [properties.pop(k) for k in delete_keys]
                required_params = parameters.get("required", [])
                parameters["required"] = [
                    p for p in required_params if p not in delete_keys
                ]

        _tool = Action(
            name=tool_name or metadata.get("name") or func.__name__,
            description=description or metadata.get("description") or func.__doc__,
            parameters=metadata.get("parameters", {}),
            terminal=terminal,
            function=func,
        )
        logger.debug(
            f"Extracting function metadata for function {func.__name__} took: {(time.time()-tic)} seconds"
        )
        return _tool

    return decorator
