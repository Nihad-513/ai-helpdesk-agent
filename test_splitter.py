
from rag.document_loader import load_documents
from rag.text_splitter import split_documents

documents = load_documents("data/knowledge_base")

chunks = split_documents(
    documents,
    chunk_size=100,
    chunk_overlap=20,
)

print("\nTotal chunks:", len(chunks))

for chunk in chunks:
    print("\nSource:", chunk["metadata"]["source"])
    print("Chunk index:", chunk["metadata"]["chunk_index"])
    print("Content:", chunk["text"])
