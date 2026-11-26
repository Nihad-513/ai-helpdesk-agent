
from rag.retriever import Retriever

retriever = Retriever(n_results=3)

questions = [
    # Paraphrased questions
    {
        "question": "When should my order reach me?",
        "expected": "shipping",
    },
    {
        "question": "What is the deadline for sending an item back?",
        "expected": "return",
    },
    {
        "question": "My transaction was declined. How can I fix it?",
        "expected": "payment",
    },

    # Informal language and typos
    {
        "question": "how long for delivery pls?",
        "expected": "shipping",
    },
    {
        "question": "i wanna send back my coffee",
        "expected": "return",
    },
    {
        "question": "my paymant didnt go thru",
        "expected": "payment",
    },

    # Unsupported questions
    {
        "question": "Do you deliver orders to Mars?",
        "expected": None,
    },
    {
        "question": "Can I buy a smartphone?",
        "expected": None,
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
    raise AssertionError("Retrieval edge-case benchmark failed.")

print("All retrieval edge-case tests passed.")
