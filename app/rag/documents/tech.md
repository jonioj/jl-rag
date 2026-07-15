# Technical Notes

The ingestion pipeline reads text files from a directory, splits them into chunks, and stores them in ChromaDB.
Each chunk includes metadata with the source path and chunk number.
This makes retrieval more reliable for question answering.
