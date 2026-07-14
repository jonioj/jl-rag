from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional


def chunk_text(text: str, chunk_size: int = 50, overlap: int = 10) -> list[str]:
    if not text.strip():
        return []

    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(0, end - overlap)
    print(chunks)
    return chunks


def ingest_documents_from_directory(directory: str | Path, collection=None, chunk_size: int = 50, overlap: int = 10) -> int:
    docs_dir = Path(directory)
    if not docs_dir.exists():
        raise FileNotFoundError(f"Directory does not exist: {docs_dir}")

    documents: list[str] = []
    ids: list[str] = []
    metadatas: list[dict[str, str]] = []

    for file_path in sorted(docs_dir.rglob("*")):
        print(file_path)
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in {".txt", ".md", ".json", ".csv"}:
            continue

        text = file_path.read_text(encoding="utf-8", errors="ignore")
       
        for chunk_index, chunk in enumerate(chunk_text(text, chunk_size=chunk_size, overlap=overlap)):
           
            print(chunk)
            print(chunk_index)
            ids.append(f"{file_path.as_posix()}::chunk_{chunk_index}")
            metadatas.append({"source": str(file_path), "chunk": str(chunk_index)})

    if not documents:
        return 0

    if collection is None:
        from .rag import get_collection

        collection = get_collection()

    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    return len(documents)
