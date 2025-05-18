from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Prompt:
    messages: list[dict] = field(default_factory=list)
    tools: Optional[list[dict]] = field(default=None)
    managed_agent_descriptions: Optional[list[str]] = field(default=None)
    metadata: dict = field(default_factory=dict)  # Fixing mutable default issue
