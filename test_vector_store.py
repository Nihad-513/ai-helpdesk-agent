
from rag.document_loader import load_documents
from rag.text_splitter import split_documents
from rag.vector_store import VectorStore


# Load documents
documents = load_documents("data/knowledge_base")

# Split documents
chunks = split_documents(
    documents,
    chunk_size=500,
    chunk_overlap=100,
)

# Initialize vector database
vector_store = VectorStore()

# Store chunks
vector_store.add_documents(chunks)

# Search the knowledge base
query = "How long does shipping take?"

results = vector_store.search(query, n_results=3)

print("\nSearch results:")

for result in results:
    print("\nSource:", result["metadata"]["source"])
    print("Distance:", result["distance"])
    print("Content:", result["text"])
