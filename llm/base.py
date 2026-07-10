from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Interface that every LLM backend must implement.
    Add new backends (local, Anthropic, OpenAI, etc.) by subclassing this.
    """

    @abstractmethod
    def answer(self, question: str) -> str:
        """Given a question, return the model's answer as a string."""
        raise NotImplementedError