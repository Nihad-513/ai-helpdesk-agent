
from rag.retriever import Retriever

retriever = Retriever(n_results=3)

query = "What is the delivery time?"

results = retriever.retrieve(query)

context = retriever.build_context(results)

print("\nRetrieved context:\n")
print(context)
