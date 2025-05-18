"""M - Memory Implementation

Almost every agent needs to remember what happens from one loop iteration to the next.
This is where the Memory component comes in. It allows the agent to store and retrieve information about its
interactions, which is critical for context and decision-making.

https://www.coursera.org/learn/ai-agents-python/ungradedWidget/3d8su/modular-ai-agent-design
"""

from abc import ABC, abstractmethod


class Memory(ABC):
    @abstractmethod
    def add_memory(self, memory: dict):
        """Add memory to working memory"""

    @abstractmethod
    def get_memories(self, limit: int = None) -> list[dict]:
        """Get formatted conversation history for prompt"""
