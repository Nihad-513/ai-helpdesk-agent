
from rag.rag_pipeline import RAGPipeline

pipeline = RAGPipeline()

# First conversation: follow-up about returns
history = [
    {
        "role": "user",
        "content": "How long does standard shipping take?",
    },
    {
        "role": "assistant",
        "content": "Standard shipping takes 3-5 business days.",
    },
]

question = "What about returns?"

print("\n" + "=" * 70)
print("TEST: Follow-up question about returns")
print(f"CUSTOMER: {question}")

result = pipeline.answer(question, history=history)

print(f"\nAI ASSISTANT: {result['answer']}")
print(f"\nSOURCES: {result['sources']}")

answer = result["answer"].lower()

if (
    "store_policy.txt" in result["sources"]
    and "14" in answer
):
    print("\nRESULT: PASS")
else:
    print("\nRESULT: FAIL")


# Second conversation: follow-up about a product price
product_history = [
    {
        "role": "user",
        "content": "Tell me about House Blend.",
    },
    {
        "role": "assistant",
        "content": "House Blend is a balanced everyday coffee blend with a smooth flavour profile.",
    },
]

product_question = "How much does it cost?"

print("\n" + "=" * 70)
print("TEST: Product price follow-up")
print(f"CUSTOMER: {product_question}")

product_result = pipeline.answer(
    product_question,
    history=product_history,
)

product_answer = product_result["answer"]
product_sources = product_result["sources"]

print(f"\nAI ASSISTANT: {product_answer}")
print(f"\nSOURCES: {product_sources}")

product_answer_lower = product_answer.lower()

product_success = (
    "product_catalogue.txt" in product_sources
    and "399" in product_answer
    and "subject to stock" in product_answer_lower
)

if product_success:
    print("\nRESULT: PASS")
else:
    print("\nRESULT: FAIL")
    print("Expected: House Blend price of ₹399 and stock disclaimer.")


# Third conversation: identify the second product mentioned
comparison_history = [
    {
        "role": "user",
        "content": "Tell me about House Blend and Dark Roast.",
    },
    {
        "role": "assistant",
        "content": (
            "House Blend Coffee Beans cost ₹399 for 250g. "
            "Dark Roast Coffee Beans cost ₹449 for 250g."
        ),
    },
]

comparison_question = "How much is the second one?"

print("\n" + "=" * 70)
print("TEST: Ambiguous product reference")
print(f"CUSTOMER: {comparison_question}")


comparison_result = pipeline.answer(
    comparison_question,
    history=comparison_history,
)

comparison_answer = comparison_result["answer"]
comparison_sources = comparison_result["sources"]

print(f"\nAI ASSISTANT: {comparison_answer}")
print(f"\nSOURCES: {comparison_sources}")

comparison_answer_lower = comparison_answer.lower()

comparison_success = (
    "product_catalogue.txt" in comparison_sources
    and "dark roast" in comparison_answer_lower
    and "449" in comparison_answer
    and "subject to stock" in comparison_answer_lower
)

if comparison_success:
    print("\nRESULT: PASS")
else:
    print("\nRESULT: FAIL")
    print("Expected: Dark Roast, ₹449 and stock disclaimer.")


# Fourth conversation: return to an earlier topic after switching topics
context_history = [
    {
        "role": "user",
        "content": "Tell me about House Blend.",
    },
    {
        "role": "assistant",
        "content": "House Blend Coffee Beans cost ₹399 for 250g.",
    },
    {
        "role": "user",
        "content": "What is your return policy?",
    },
    {
        "role": "assistant",
        "content": "You can return products within 14 days after delivery.",
    },
]

context_question = "Going back to House Blend, how much was it again?"

print("\n" + "=" * 70)
print("TEST: Context switching")
print(f"CUSTOMER: {context_question}")

context_result = pipeline.answer(
    context_question,
    history=context_history,
)

context_answer = context_result["answer"]
context_sources = context_result["sources"]

print(f"\nAI ASSISTANT: {context_answer}")
print(f"\nSOURCES: {context_sources}")

context_answer_lower = context_answer.lower()

context_success = (
    "product_catalogue.txt" in context_sources
    and "399" in context_answer
    and "subject to stock" in context_answer_lower
)

if context_success:
    print("\nRESULT: PASS")
else:
    print("\nRESULT: FAIL")
    print("Expected: House Blend, ₹399 and stock disclaimer.")
