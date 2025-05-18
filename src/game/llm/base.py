from abc import ABC, abstractmethod

from game.prompt import Prompt


class Llm(ABC):
    """Abstracts the interaction with an LLM"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the LLM model used"""

    @abstractmethod
    def __call__(self, prompt: Prompt) -> str:
        """The main method to interact with the LLM"""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model='{self.name}', ...)"
