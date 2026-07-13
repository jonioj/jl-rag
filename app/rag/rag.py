import chromadb
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

client = chromadb.PersistentClient(path=f"{BASE_DIR}/dbs/chroma_db")

collection = client.get_or_create_collection(
    name="documents"
)
collection.add(
    ids=["doc1", "doc2", "doc3"],
    documents=[
        "chromadb is a database.",
        "ChromaDB is a vector database.",
        "Embeddings enable semantic search."
    ],
    metadatas=[
        {"source": "wiki"},
        {"source": "docs"},
        {"source": "blog"}
    ]
)
