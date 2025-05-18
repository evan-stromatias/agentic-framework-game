import uuid
from typing import Any, Optional

from game.memory import Memory


class ActionContext:
    """Passed to the tools as an optional hidden argument (`action_context`)"""

    def __init__(self, properties: Optional[dict] = None):
        self.context_id = str(uuid.uuid4())
        self.properties = properties or {}

    def get(self, key: str, default=None):
        return self.properties.get(key, default)

    def set(self, key: str, value: Any):
        self.properties[key] = value

    def get_memory(self) -> Optional[Memory]:
        return self.properties.get("memory", None)

    def get_agent_registry(self):
        return self.properties.get("agent_registry", None)
