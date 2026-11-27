
"""Ingest Bean & Brew knowledge-base documents into ChromaDB."""

from pathlib import Path

from rag.document_loader import load_documents
from rag.text_splitter import split_documents
from rag.vector_store import VectorStore


# Resolve paths relative to the project root.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "data" / "knowledge_base"


def main():
    """Load, split, and index knowledge-base documents."""

    print("Loading knowledge-base documents...")

    documents = load_documents(KNOWLEDGE_BASE_DIR)

    if not documents:
        raise RuntimeError(
            "No valid knowledge-base documents were loaded."
        )

    print(f"Loaded {len(documents)} documents.")

    print("\nSplitting documents into chunks...")

    chunks = split_documents(documents)

    if not chunks:
        raise RuntimeError(
            "No chunks were generated from the documents."
        )

    print(f"Generated {len(chunks)} chunks.")

    print("\nIndexing documents in ChromaDB...")

    vector_store = VectorStore()
    vector_store.sync_documents(chunks)

    print("\nKnowledge-base ingestion completed successfully.")
    print(f"Documents processed: {len(documents)}")
    print(f"Chunks indexed: {len(chunks)}")


if __name__ == "__main__":
    main()
