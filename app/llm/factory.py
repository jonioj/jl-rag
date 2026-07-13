import os
from functools import lru_cache

from .base import LLMProvider
from .local_provider import LocalModelProvider
from .dummy import DummyLLM


@lru_cache()  # instantiate the provider once and reuse it across requests
def get_llm_provider() -> LLMProvider:
    backend = os.environ.get("LLM_BACKEND", "dummy").lower()

    if backend == 'local':
        return LocalModelProvider()
    elif backend == 'dummy':
        return DummyLLM()
    else:
        raise ValueError(f"Unknown LLM_BACKEND: {backend}")