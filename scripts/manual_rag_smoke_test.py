
from rag.rag_pipeline import RAGPipeline

rag = RAGPipeline()

questions = [
    "How long does shipping take?",
    "What is your return policy?",
    "Do you offer free international shipping?",
]

for question in questions:
    result = rag.answer(question)

    print("\nCustomer:", question)
    print("Agent:", result["answer"])
    print("Sources:", result["sources"])
    print("-" * 50)
