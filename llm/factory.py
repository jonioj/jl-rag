import os
from functools import lru_cache

from llm.base import LLMProvider
from llm.local_provider import LocalModelProvider


@lru_cache()  # instantiate the provider once and reuse it across requests
def get_llm_provider() -> LLMProvider:
    backend = os.environ.get("LLM_BACKEND", "local").lower()

    if backend == 'local':
        return LocalModelProvider()
    else:
        raise ValueError(f"Unknown LLM_BACKEND: {backend}")