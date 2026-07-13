from pathlib import Path

from llama_cpp import Llama

from .base import LLMProvider


class LocalModelProvider(LLMProvider):
    """
    Example local backend using a HuggingFace transformers pipeline.
    Swap `pipeline(...)` for llama.cpp, Ollama, vLLM, etc. as needed —
    only this class changes, nothing else in the app.
    """

    def __init__(self):
        model_path = Path(__file__).resolve().parents[2] / "models" / "SmolLM2-360M-Instruct-Q4_K_M.gguf"
        self.llm = Llama(
            model_path=str(model_path),
            n_ctx=2048,
            verbose=False,
        )


    def answer(self, prompt: str) -> str:
        result = self.llm(
        prompt,
        max_tokens=100
        )

        return result["choices"][0]["text"].strip()