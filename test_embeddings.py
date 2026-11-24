
from rag.embeddings import generate_embeddings

texts = [
    "How long does shipping take?",
    "What is the delivery duration?",
    "How do I reset my password?",
]

vectors = generate_embeddings(texts)

print("Number of vectors:", len(vectors))
print("Dimensions:", len(vectors[0]))
print("First vector (first 10 values):", vectors[0][:10])
