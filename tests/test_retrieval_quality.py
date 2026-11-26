
from rag.retriever import Retriever

retriever = Retriever(n_results=3)

questions = [
    {
        "question": "How long does standard shipping take?",
        "expected": "shipping",
    },
    {
        "question": "How many days do customers have to return products?",
        "expected": "return",
    },
    {
        "question": "What should I do if my payment fails?",
        "expected": "payment",
    },
    {
        "question": "Do you offer free international shipping?",
        "expected": None,
    },
    {
        "question": "Can I buy a laptop from your store?",
        "expected": None,
    },
    {
        "question": "Do you sell coffee beans?",
        "expected": "coffee",
    },
]

passed = 0
failed = 0

for item in questions:
    question = item["question"]
    expected = item["expected"]

    results = retriever.retrieve(question)

    combined_text = " ".join(
        result["text"].lower() for result in results
    )

    if expected is None:
        success = not results
    else:
        success = expected in combined_text

    print("\n" + "=" * 65)
    print(f"QUESTION: {question}")
    print(f"EXPECTED: {expected or 'No relevant results'}")
    print(f"RETRIEVED CHUNKS: {len(results)}")

    if success:
        print("RESULT: PASS")
        passed += 1
    else:
        print("RESULT: FAIL")
        failed += 1

        for result in results:
            print(f"Source: {result['metadata']['source']}")
            print(f"Content: {result['text'][:250]}")

print("\n" + "=" * 65)
print(f"SUMMARY: {passed} passed, {failed} failed")

if failed:
    raise AssertionError("Retrieval quality benchmark failed.")

print("All retrieval quality tests passed.")
