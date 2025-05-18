from datetime import datetime
from zoneinfo import ZoneInfo

from colorama import Fore, Style, init

from game.action import tool
from game.action.context import ActionContext
from game.logger import get_logger

init(autoreset=True)

logging = get_logger(__name__)


@tool(terminal=True)
def terminate(action_context: ActionContext, message: str) -> str:
    """Terminates the agent's execution with a final message.

    Args:
        action_context: Contains the action context populated by the agent
        message: The final message to return before terminating

    Returns:
        The message with a termination note appended
    """
    agent_name = action_context.get("name", "")
    print("------")
    print(f"{Fore.BLUE}[FINAL MESSAGE ('{agent_name}')] {message}{Style.RESET_ALL}")
    print("------")
    logging.debug(f"Final terminate message: '{message}'")
    return f"{message}"


@tool()
def user_input(action_context: ActionContext, message: str) -> str:
    """
    Receives user's question based on the LLM response tool call message
    Args:
        action_context: Contains the action context populated by the agent (this argument is hidden)
        message: The message from the LLM

    Returns:
        User's response as a string
    """
    agent_name = action_context.get("name", "")
    print("------")
    print(f"{Fore.YELLOW}[ASSISTANT ('{agent_name}')] {message}{Style.RESET_ALL}")
    print("------")
    return input(">")


@tool()
def get_current_date_and_time(
    action_context: ActionContext, _default_tz: str = "Europe/Berlin"
) -> str:
    """
    Returns the current date and time
    Args:
        action_context: Contains the action context populated by the agent (this argument is hidden)
        _default_tz: The default timezone (this argument is hidden)

    Returns:
        The current date and time
    """
    time_zone_name = action_context.get("time_zone", _default_tz)
    current_time = datetime.now(ZoneInfo(time_zone_name))

    # Add current time to system message
    return (
        f"Current time: "
        f"{current_time.strftime('%H:%M %A, %B %d, %Y')} "
        f"({time_zone_name})"
    )
