
"""Load text content from PDF, DOCX, and TXT knowledge-base files."""

from pathlib import Path
import pymupdf
from docx import Document


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def load_document(file_path: str | Path) -> dict:
    """Extract text from a supported file and return its content and metadata."""

    path = Path(file_path)
    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension}")

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    if extension == ".pdf":
        with pymupdf.open(path) as pdf:
            text = "\n".join(page.get_text() for page in pdf)

    elif extension == ".docx":
        document = Document(path)
        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    else:
        text = path.read_text(encoding="utf-8")

    text = text.strip()

    if not text:
        raise ValueError(f"No extractable text found in: {path.name}")

    return {
        "text": text,
        "metadata": {
            "source": path.name,
            "file_type": extension.lstrip("."),
        },
    }


def load_documents(directory: str | Path) -> list[dict]:
    """Load all supported documents from a directory."""

    folder = Path(directory)

    if not folder.is_dir():
        raise NotADirectoryError(f"Directory not found: {folder}")

    documents = []

    for file_path in sorted(folder.iterdir()):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            try:
                documents.append(load_document(file_path))
                print(f"[loaded] {file_path.name}")
            except Exception as exc:
                print(f"[skipped] {file_path.name}: {exc}")

    return documents
