
"""Store and search document embeddings using ChromaDB."""

import chromadb

from rag.embeddings import generate_embeddings


DB_PATH = "chroma_db"
COLLECTION_NAME = "bean_brew_knowledge"


class VectorStore:

    def __init__(self):
        self.client = chromadb.PersistentClient(path=DB_PATH)

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, chunks: list[dict]) -> None:
        """Generate embeddings and store document chunks."""

        if not chunks:
            print("No chunks to add.")
            return

        ids = []
        texts = []
        metadatas = []

        for index, chunk in enumerate(chunks):
            source = chunk["metadata"]["source"]
            chunk_index = chunk["metadata"]["chunk_index"]

            ids.append(f"{source}_{chunk_index}")
            texts.append(chunk["text"])
            metadatas.append(chunk["metadata"])

        embeddings = generate_embeddings(texts)

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        print(f"Stored {len(chunks)} chunks in ChromaDB.")

    def search(self, query: str, n_results: int = 3) -> list[dict]:
        """Retrieve the most relevant document chunks."""

        query_embedding = generate_embeddings([query])[0]

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, self.collection.count()),
        )

        retrieved_chunks = []

        if not results["documents"]:
            return retrieved_chunks

        for index, document in enumerate(results["documents"][0]):
            retrieved_chunks.append({
                "text": document,
                "metadata": results["metadatas"][0][index],
                "distance": results["distances"][0][index],
            })

        return retrieved_chunks
