from rag.rag_pipeline import RAGPipeline
import re

pipeline = RAGPipeline()


questions = [
    {
        "question": "How long does standard shipping take?",
        "expected_source": "store_policy.txt",
        "required_phrases": ["3", "5", "business days"],
    },
    {
        "question": "How many days do I have to return a product?",
        "expected_source": "store_policy.txt",
        "required_phrases": ["14 days"],
    },
    {
        "question": "My payment failed. What should I do?",
        "expected_source": "store_policy.txt",
        "required_phrases": ["support team"],
    },
    {
        "question": "Do you offer free international shipping?",
        "expected_source": None,
        "required_phrases": [],
    },
    {
        "question": "Can I buy a laptop from your store?",
        "expected_source": None,
        "required_phrases": [],
    },
    {
        "question": "What coffee beans do you sell and how much do they cost?",
        "expected_source": "product_catalogue.txt",
        "required_phrases": ["399", "429", "449", "250"],
    },
    {
        "question": "My transaction was declined. How can I fix it?",
        "expected_source": "store_policy.txt",
        "required_phrases": ["support team"],
    },
    {
        "question": "my paymant didnt go thru",
        "expected_source": "store_policy.txt",
        "required_phrases": ["support team"],
    },
]

passed = 0
failed = 0

for item in questions:
    question = item["question"]
    expected_source = item["expected_source"]
    required_phrases = item["required_phrases"]

    print("\n" + "=" * 70)
    print(f"CUSTOMER: {question}")

    result = pipeline.answer(question)

    answer = result["answer"]
    sources = result["sources"]

    print(f"\nAI ASSISTANT: {answer}")
    print(f"\nSOURCES: {sources}")

    answer_lower = answer.lower()

    source_check = (
        expected_source in sources
        if expected_source
        else len(sources) == 0
    )

    phrase_check = all(
       phrase.lower() in answer_lower
       for phrase in required_phrases
    )

    if "return a product" in question.lower():
       phrase_check = phrase_check and any(
          term in answer_lower
          for term in ["delivery", "delivered"]
    )

    # Check for unsupported contact methods.
    forbidden_contact_patterns = [
        r"\bsupport page\b",
        r"\bwebsite\b",
        r"\be-?mail\b",
        r"\bphone number\b",
        r"\bcall us\b",
        r"\blive chat\b",
        r"\bcontact form\b",
        r"https?://\S+",
        r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b",
    ]

    contact_check = not any(
        re.search(pattern, answer, re.IGNORECASE)
        for pattern in forbidden_contact_patterns
    )

    # Product listings must include a stock qualification.
    stock_check = (
        "coffee beans" not in question.lower()
        or "subject to stock" in answer_lower
    )

    success = (
        source_check
        and phrase_check
        and contact_check
        and stock_check
    )

    if success:
        print("\nRESULT: PASS")
        passed += 1
    else:
        print("\nRESULT: FAIL")

        if not source_check:
            print("Reason: Expected source was not retrieved correctly.")

        if not phrase_check:
            print("Reason: One or more required phrases are missing.")

        if not contact_check:
            print("Reason: Unsupported contact method mentioned.")

        if not stock_check:
            print("Reason: Product availability disclaimer is missing.")

        failed += 1

print("\n" + "=" * 70)
print("RAG EVALUATION SUMMARY")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Total: {passed + failed}")

if failed:
    raise AssertionError("RAG response evaluation failed.")

print("All RAG response evaluations passed.")
