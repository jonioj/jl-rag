from pathlib import Path

from app.rag.ingest import ingest_documents_from_directory
from app.rag.rag import get_collection


def test_ingest_documents_from_directory_populates_collection(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    sample_file = docs_dir / "sample.txt"
    sample_file.write_text("This is a test document about vector databases and embeddings.", encoding="utf-8")

    collection = get_collection(reset=True)
    ingested_count = ingest_documents_from_directory(docs_dir, collection=collection)

    assert ingested_count == 1
    results = collection.get(include=["documents", "metadatas"])
    assert len(results["documents"]) == 1
    assert "vector databases" in results["documents"][0]
    assert results["metadatas"][0]["source"] == str(sample_file)
