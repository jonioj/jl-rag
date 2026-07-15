from ..rag.rag import get_collection


def build_contextual_prompt(question: str) -> str:
    collection = get_collection()
    search_results = collection.query(query_texts=[question], n_results=3)
    documents = search_results.get("documents", [[]])[0] if search_results else []
    distances = search_results.get("distances", [[]])[0] if search_results else []
    relevant_documents = []
    for document, distance in zip(documents, distances):
        if distance < .7:
            relevant_documents.append(document)
            print(document, distance)

    context_text = "\n".join(relevant_documents) if relevant_documents else ""

    if not context_text:
        return question

    return (
        "Use the following context to answer the question.\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {question}"
    )
