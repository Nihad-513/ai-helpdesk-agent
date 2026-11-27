
from rag.retriever import Retriever


class FailingVectorStore:
    def search(self, query, n_results):
        raise RuntimeError("Simulated semantic-search failure")


class MockBM25:
    def get_scores(self, query_tokens):
        return [3.0, 0.0]


def test_bm25_fallback_works_when_semantic_search_fails():
    retriever = Retriever.__new__(Retriever)

    retriever.vector_store = FailingVectorStore()
    retriever.n_results = 3
    retriever.documents = [
        {
            "text": "Standard shipping takes 3-5 business days.",
            "metadata": {
                "source": "shipping.txt",
                "chunk_index": 0,
            },
        },
        {
            "text": "Customers can return products within 30 days.",
            "metadata": {
                "source": "returns.txt",
                "chunk_index": 0,
            },
        },
    ]
    retriever.bm25 = MockBM25()

    results = retriever.retrieve("How long does shipping take?")

    assert len(results) == 1
    assert results[0]["metadata"]["source"] == "shipping.txt"
    assert "shipping" in results[0]["text"].lower()
