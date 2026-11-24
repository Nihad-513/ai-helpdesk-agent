
"""Generate vector embeddings for text using Sentence Transformers."""

from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_model():
    """Load the embedding model once and reuse it."""

    global _model

    if _model is None:
        print(f"Loading embedding model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Convert a list of texts into numerical vectors."""

    if not texts:
        return []

    model = get_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embeddings.tolist()


def generate_embedding(text: str) -> list[float]:
    """Generate an embedding for a single text."""

    return generate_embeddings([text])[0]
