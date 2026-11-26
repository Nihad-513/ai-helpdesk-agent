
import pytest

from rag.text_splitter import split_text, split_documents


def test_split_text_returns_chunks_within_size_limit():
    text = " ".join(["coffee"] * 100)

    chunks = split_text(
        text,
        chunk_size=100,
        chunk_overlap=0,
    )

    assert len(chunks) > 1
    assert all(len(chunk) <= 100 for chunk in chunks)


def test_split_text_preserves_all_words():
    text = " ".join(["coffee"] * 100)

    chunks = split_text(
        text,
        chunk_size=100,
        chunk_overlap=0,
    )

    original_words = text.split()
    chunk_words = " ".join(chunks).split()

    assert chunk_words == original_words


def test_split_text_handles_empty_input():
    assert split_text("") == []
    assert split_text("   ") == []


def test_split_text_rejects_invalid_chunk_size():
    with pytest.raises(ValueError):
        split_text("Some text", chunk_size=0)

    with pytest.raises(ValueError):
        split_text("Some text", chunk_size=-1)


def test_split_text_rejects_invalid_overlap():
    with pytest.raises(ValueError):
        split_text("Some text", chunk_size=100, chunk_overlap=-1)

    with pytest.raises(ValueError):
        split_text("Some text", chunk_size=100, chunk_overlap=100)


def test_split_documents_preserves_metadata():
    documents = [
        {
            "text": "Coffee beans are roasted.\n\nCoffee can be brewed.",
            "metadata": {
                "source": "coffee_guide.txt",
            },
        }
    ]

    chunks = split_documents(
        documents,
        chunk_size=100,
        chunk_overlap=0,
    )

    assert len(chunks) >= 1

    for index, chunk in enumerate(chunks):
        assert chunk["metadata"]["source"] == "coffee_guide.txt"
        assert chunk["metadata"]["chunk_index"] == index
        assert chunk["text"].strip()
