from pathlib import Path

import chromadb

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "dbs" / "chroma_db"
DB_DIR.mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=str(DB_DIR))


def get_collection(reset: bool = False):
    global collection

    if reset:
        try:
            client.delete_collection(name="documents")
        except Exception:
            pass

    collection = client.get_or_create_collection(name="documents")
    return collection


collection = get_collection()
