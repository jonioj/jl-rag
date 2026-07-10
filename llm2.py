from llama_cpp import Llama

llm = Llama(
    model_path="/home/jonaszlaba/models/SmolLM2-360M-Instruct-Q4_K_M.gguf",
    n_ctx=2048,
    verbose=False
)

while True:
    prompt = input("\nYou: ")

    if prompt.lower() in ["exit", "quit"]:
        break

    result = llm(
        f"### Instruction:\n{prompt}\n\n### Response:",
        max_tokens=100
    )

    print("AI:", result["choices"][0]["text"].strip())
