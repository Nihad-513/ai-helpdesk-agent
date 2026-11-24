
"""Split documents into smaller overlapping text chunks."""


def split_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> list[str]:
    """Split text into chunks measured in characters."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    text = text.strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - chunk_overlap

    return chunks


def split_documents(
    documents: list[dict],
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> list[dict]:
    """Split loaded documents while preserving their metadata."""

    all_chunks = []

    for document in documents:
        chunks = split_text(
            document["text"],
            chunk_size,
            chunk_overlap,
        )

        for index, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "metadata": {
                    **document["metadata"],
                    "chunk_index": index,
                },
            })

    return all_chunks
