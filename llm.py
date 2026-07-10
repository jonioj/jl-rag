from llama_cpp import Llama


prompt = str(input())
llm = Llama(
    model_path="/home/jonaszlaba/models/SmolLM2-360M-Instruct-Q4_K_M.gguf",
    n_ctx=2048,
    verbose=False
)

result = llm(
    prompt,
    max_tokens=50
)

print(result["choices"][0]["text"])
