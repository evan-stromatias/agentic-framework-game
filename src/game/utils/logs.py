from typing import Optional

from game.logger import get_logger
from game.memory import Memory

logger = get_logger(__name__)


def log_memory(
    memory: Memory,
    message_types: Optional[list[str]] = None,
    is_log_level_info: bool = False,
    agent_name: str = "",
    agent_description: str = "",
) -> None:
    """"""
    memories = memory.get_memories()

    log = logger.info if is_log_level_info else logger.debug
    message_types = message_types or set([m["type"] for m in memories])
    log("")
    log("----------------------------------------------------------------")
    log(f"Log memory: '{agent_name}':'{agent_description}'")
    log("----------------------------------------------------------------")
    for memory in memories:
        if memory["type"] in message_types:
            log(memory)
    log("----------------------------------------------------------------")
    log("")
