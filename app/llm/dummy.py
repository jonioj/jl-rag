from .base import LLMProvider


class DummyLLM(LLMProvider):
    def __init__(self, *args, **kwargs):
        pass

    def answer(self, prompt: str) -> str:
        return "This is a dummy response."