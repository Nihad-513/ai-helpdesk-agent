
"""Store and search document embeddings using ChromaDB."""


import os
from dotenv import load_dotenv
import chromadb


from rag.embeddings import generate_embeddings

load_dotenv()


DB_PATH = os.getenv(
    "CHROMA_DB_PATH",
    "chroma_db",
)

COLLECTION_NAME = "bean_brew_knowledge"


class VectorStore:


    def __init__(
        self,
        db_path: str = DB_PATH,
        collection_name: str = COLLECTION_NAME,
    ):
        self.client = chromadb.PersistentClient(path=db_path)

        self.collection = self.client.get_or_create_collection(
           name=collection_name,
           metadata={"hnsw:space": "cosine"},
        )

    def clear(self) -> None:
        """Remove all existing documents from the collection."""

        existing = self.collection.get()
        existing_ids = existing["ids"]

        if existing_ids:
            self.collection.delete(ids=existing_ids)

        print("Existing vector-store documents cleared.")
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

    def sync_documents(self, chunks: list[dict]) -> None:
        """Synchronise the collection with the current knowledge base."""
        if not chunks:
           raise ValueError("Cannot synchronise an empty knowledge base.")
        expected_ids = {
            f"{chunk['metadata']['source']}_{chunk['metadata']['chunk_index']}"
            for chunk in chunks
        }

        existing = self.collection.get()

        obsolete_ids = [
            document_id
            for document_id in existing["ids"]
            if document_id not in expected_ids
        ]

        if obsolete_ids:
            self.collection.delete(ids=obsolete_ids)
            print(f"Removed {len(obsolete_ids)} obsolete chunks.")

        self.add_documents(chunks)

        print("Knowledge-base synchronisation completed.")



    def get_all_documents(self) -> list[dict]:
      """Retrieve all stored document chunks."""

      results = self.collection.get(
      include=["documents", "metadatas"]
      )

      documents = []

      for index, document in enumerate(results["documents"]):
          documents.append({
             "text": document,
             "metadata": results["metadatas"][index],
          })

      return documents

    def search(self, query: str, n_results: int = 3) -> list[dict]:
        """Retrieve the most relevant document chunks."""
        if self.collection.count() == 0:
           return []
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
