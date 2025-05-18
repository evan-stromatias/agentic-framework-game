from colorama import Fore, Style, init

from game.memory.base import Memory

init(autoreset=True)


def _get_color_based_on_msg_type(msg_type: str):
    msg_type = msg_type.lower()
    if msg_type == "user":
        return Fore.GREEN
    elif msg_type == "assistant":
        return Fore.YELLOW
    elif msg_type == "environment":
        return Fore.CYAN
    else:
        return Fore.RED


def print_memory(memory: Memory, info: str = "") -> None:
    """
    Prints the `memory` of an agent using color for the different roles
    :param memory:
    :param info:
    """
    memories = memory.get_memories()
    if info:
        print("Printing the memory object of:")
        print("")
        print("─" * len(info))
        print(info)
        print("─" * len(info))
        print("")
    for memory in memories:
        type_ = memory.get("type")
        content_ = memory.get("content")
        color_ = _get_color_based_on_msg_type(type_)
        print(f"{color_}{type_.upper()}")
        print("─" * (len(type_)))
        print(f"└──────> {content_} {Style.RESET_ALL}")
        print("")
