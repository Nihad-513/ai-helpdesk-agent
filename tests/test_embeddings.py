
from rag.embeddings import generate_embeddings


def test_embedding_generation_returns_one_vector_per_text():
    texts = [
        "How long does shipping take?",
        "What is the delivery duration?",
        "How do I reset my password?",
    ]

    vectors = generate_embeddings(texts)

    assert len(vectors) == len(texts)


def test_embeddings_have_expected_dimensions():
    texts = ["How long does shipping take?"]

    vectors = generate_embeddings(texts)

    assert len(vectors[0]) == 384


def test_embeddings_contain_valid_numeric_values():
    texts = ["How long does shipping take?"]

    vectors = generate_embeddings(texts)

    assert all(
        isinstance(value, (int, float))
        for value in vectors[0]
    )
