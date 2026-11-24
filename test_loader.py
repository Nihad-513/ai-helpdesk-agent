
from rag.document_loader import load_documents

documents = load_documents("data/knowledge_base")

print("\nTotal documents loaded:", len(documents))

for document in documents:
    print("\nSource:", document["metadata"]["source"])
    print("Content:", document["text"])
