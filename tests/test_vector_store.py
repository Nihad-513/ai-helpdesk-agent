import pytest

from rag.vector_store import VectorStore


@pytest.fixture
def vector_store(tmp_path):
    return VectorStore(
        db_path=str(tmp_path / "test_chroma_db"),
        collection_name="test_bean_brew_knowledge",
    )


def test_documents_can_be_added_to_vector_store(vector_store):
    chunks = [
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

    vector_store.add_documents(chunks)

    assert vector_store.collection.count() == 2


def test_all_stored_documents_can_be_retrieved(vector_store):
    chunks = [
        {
            "text": "Standard shipping takes 3-5 business days.",
            "metadata": {
                "source": "shipping.txt",
                "chunk_index": 0,
            },
        }
    ]

    vector_store.add_documents(chunks)

    documents = vector_store.get_all_documents()

    assert len(documents) == 1
    assert documents[0]["text"] == (
        "Standard shipping takes 3-5 business days."
    )
    assert documents[0]["metadata"]["source"] == "shipping.txt"


def test_search_returns_relevant_documents(vector_store):
    chunks = [
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

    vector_store.add_documents(chunks)

    results = vector_store.search(
        "How long does shipping take?",
        n_results=2,
    )

    assert len(results) == 2
    assert results[0]["metadata"]["source"] == "shipping.txt"
    assert "shipping" in results[0]["text"].lower()
    assert "distance" in results[0]


def test_search_returns_empty_list_for_empty_collection(vector_store):
    results = vector_store.search(
        "How long does shipping take?",
    )

    assert results == []


def test_clear_removes_all_documents(vector_store):
    chunks = [
        {
            "text": "Standard shipping takes 3-5 business days.",
            "metadata": {
                "source": "shipping.txt",
                "chunk_index": 0,
            },
        }
    ]

    vector_store.add_documents(chunks)
    assert vector_store.collection.count() == 1

    vector_store.clear()

    assert vector_store.collection.count() == 0