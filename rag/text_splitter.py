
"""Split documents into paragraph-aware, overlapping text chunks."""


def split_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> list[str]:
    """Split text into chunks while preserving paragraph and word boundaries."""

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    text = text.strip()

    if not text:
        return []

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:

        # Split unusually long paragraphs at word boundaries.
        if len(paragraph) > chunk_size:

            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""

            words = paragraph.split()
            piece_words = []
            piece_length = 0

            for word in words:

                additional_length = len(word) + (
                    1 if piece_words else 0
                )

                if piece_length + additional_length > chunk_size:

                    if piece_words:
                        chunks.append(" ".join(piece_words))

                    # Preserve whole words in the overlap.
                    overlap_words = []
                    overlap_length = 0

                    for previous_word in reversed(piece_words):

                        added_length = len(previous_word) + (
                            1 if overlap_words else 0
                        )

                        if overlap_length + added_length > chunk_overlap:
                            break

                        overlap_words.insert(0, previous_word)
                        overlap_length += added_length

                    piece_words = overlap_words
                    piece_length = overlap_length

                if piece_words:
                    piece_length += 1

                piece_words.append(word)
                piece_length += len(word)

            if piece_words:
                chunks.append(" ".join(piece_words))

            continue

        # Add the paragraph to the current chunk if it fits.
        candidate = (
            f"{current_chunk}\n{paragraph}"
            if current_chunk
            else paragraph
        )

        if len(candidate) <= chunk_size:
            current_chunk = candidate

        else:

            if current_chunk:
                chunks.append(current_chunk)

            # Create overlap using complete words only.
            overlap_words = []
            overlap_length = 0

            if chunk_overlap:
                for word in reversed(current_chunk.split()):

                    added_length = len(word) + (
                        1 if overlap_words else 0
                    )

                    if overlap_length + added_length > chunk_overlap:
                        break

                    overlap_words.insert(0, word)
                    overlap_length += added_length

            overlap = " ".join(overlap_words)

            if (
                overlap
                and len(overlap) + len(paragraph) + 1 <= chunk_size
            ):
                current_chunk = f"{overlap}\n{paragraph}"
            else:
                current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def split_documents(
    documents: list[dict],
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> list[dict]:
    """Split documents while preserving their metadata."""

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
