
from rag.document_loader import load_documents


def test_knowledge_base_documents_are_loaded():
    documents = load_documents("data/knowledge_base")

    assert len(documents) > 0


def test_loaded_documents_have_text_and_metadata():
    documents = load_documents("data/knowledge_base")

    for document in documents:
        assert "text" in document
        assert isinstance(document["text"], str)
        assert document["text"].strip()

        assert "metadata" in document
        assert "source" in document["metadata"]
        assert document["metadata"]["source"]


def test_loaded_documents_have_unique_sources():
    documents = load_documents("data/knowledge_base")

    sources = [
        document["metadata"]["source"]
        for document in documents
    ]

    assert len(sources) == len(set(sources))
