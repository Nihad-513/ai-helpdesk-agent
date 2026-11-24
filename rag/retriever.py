
"""Retrieve relevant knowledge-base chunks for a user query."""

from rag.vector_store import VectorStore


class Retriever:

    def __init__(self, n_results: int = 3):
        self.vector_store = VectorStore()
        self.n_results = n_results

    def retrieve(self, query: str) -> list[dict]:
        """Find relevant knowledge-base chunks."""

        if not query.strip():
            return []

        results = self.vector_store.search(
            query=query,
            n_results=self.n_results,
        )

        return results

    def build_context(self, results: list[dict]) -> str:
        """Combine retrieved chunks into context for the LLM."""

        if not results:
            return "No relevant information was found in the knowledge base."

        context_parts = []

        for result in results:
            source = result["metadata"]["source"]
            content = result["text"]

            context_parts.append(
                f"Source: {source}\nContent: {content}"
            )

        return "\n\n".join(context_parts)
