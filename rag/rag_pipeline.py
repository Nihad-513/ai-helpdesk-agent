
"""Combine retrieval and LLM generation into a RAG pipeline."""

from llm import groq_chat
from rag.retriever import Retriever


RAG_SYSTEM_PROMPT = """You are the customer support assistant for Bean & Brew, an online coffee store.

Your role is to provide accurate, helpful and professional customer support.

KNOWLEDGE AND ACCURACY:
- Treat the supplied knowledge-base context as the only authoritative source for Bean & Brew policies, products, prices, delivery information and business details.
- Never invent or assume information that is not explicitly supported by the context.
- Do not infer what products or services the store offers from the products listed in the context.
- If a requested product is not listed, say that the knowledge base does not contain information about that product.
- Never claim that the store sells, does not sell, or specialises in a particular product category unless the context explicitly confirms it.
- Never invent email addresses, phone numbers, website links, discounts, delivery estimates, product availability or return conditions.
- If the context does not contain the answer, clearly explain that you do not have that information.
- When information is unavailable, offer to create a support ticket so the team can assist.
- Do not present assumptions as confirmed facts.

CONVERSATION:
- Use previous conversation messages to understand the customer's intent and follow-up questions.
- Resolve references such as "it", "that one", "the other product", "the first one", "the second one" and "the last one" using conversation history.
- When a customer refers to an item by its position, identify the item using the order in which products were presented in the most recent relevant conversation message.
- Use conversation history to identify the intended product, then use the knowledge-base context to verify its details.
- If the identified product appears in the retrieved knowledge-base context, answer using its available information. Never claim that the product is missing when it is present in the context.
- Do not contradict information already established in the conversation.
- If the customer's meaning is genuinely unclear, ask a short clarifying question.

CUSTOMER SUPPORT:
- Be friendly, concise and professional.
- For payment problems, acknowledge the issue and tell the customer to contact the Bean & Brew support team.
- Never invent or suggest contact methods such as phone, email, website forms, support pages or live chat unless explicitly provided in the knowledge base.
- Do not ask customers to reply to emails unless an email contact method is explicitly provided in the knowledge base.
- If the customer needs further assistance, offer to create a support ticket through the application.
- If the customer requests a human agent, acknowledge the request and support escalation.
- Never claim that a support ticket has been created unless the application confirms it.
- Never ask customers for passwords, full card numbers, CVVs or other sensitive payment credentials.

RESPONSE FORMAT:
- Answer the customer's actual question directly.
- Use bullet points or tables when they make product information easier to understand.
- Include relevant product prices and specifications only when supplied in the context.
- When discussing product availability, always preserve any stock-availability qualifications stated in the knowledge base.
- Never imply that a product is currently in stock unless the context explicitly confirms its current stock status.
- Do not mention internal retrieval processes, embeddings or technical implementation details.
- Whenever listing products, explicitly state that availability is subject to stock availability.
"""


class RAGPipeline:

    def __init__(self):
        self.retriever = Retriever(n_results=3)


    def answer(
        self,
        question: str,
        history: list[dict] | None = None,
    ) -> dict:
        """Generate a grounded answer using conversation history."""

        # Include the previous user question when retrieving context.
        retrieval_query = question
        previous_user_questions = []

        if history:
            previous_user_questions = [
                message["content"]
                for message in history
                if message["role"] == "user"
                and message["content"].strip() != question.strip()
            ]

        if previous_user_questions:
            retrieval_query = (
                f"Previous customer question: {previous_user_questions[-1]}\n"
                f"Current customer question: {question}"
            )

            # Include the previous assistant response for positional references.
            positional_references = (
                "first one",
                "second one",
                "third one",
                "last one",
                "other one",
                "first product",
                "second product",
                "third product",
                "last product",
            )

            if any(
                reference in question.lower()
                for reference in positional_references
            ):
                previous_assistant_responses = [
                    message["content"]
                    for message in history
                    if message["role"] == "assistant"
                ]

                if previous_assistant_responses:
                    retrieval_query += (
                        "\nPrevious assistant response: "
                        + previous_assistant_responses[-1]
                    )

        # Retrieve relevant knowledge-base information.
        results = self.retriever.retrieve(retrieval_query)
        context = self.retriever.build_context(results)

        prompt = f"""Knowledge-base context:

{context}

Customer's latest question:
{question}

Answer the customer using the rules provided."""

        # Build the conversation messages.
        messages = []

        if history:
            for message in history:
                messages.append({
                    "role": message["role"],
                    "content": message["content"],
                })

        messages.append({
            "role": "user",
            "content": prompt,
        })

        # Generate the response.
        response = groq_chat(
            messages=messages,
            system=RAG_SYSTEM_PROMPT,
        )

        # Check whether product information was retrieved.
        has_product_context = any(
            result["metadata"]["source"] == "product_catalogue.txt"
            for result in results
        )

        # Check whether the question or answer actually discusses products.
        response_lower = response.lower()
        question_lower = question.lower()

        product_terms = (
            "coffee",
            "beans",
            "blend",
            "roast",
            "₹",
        )

        discusses_products = any(
            term in question_lower or term in response_lower
            for term in product_terms
        )

        # Enforce the stock disclaimer only for product-related responses.
        if (
            has_product_context
            and discusses_products
            and "subject to stock" not in response_lower
        ):
            response += "\n\nAvailability is subject to stock."

        # Collect source filenames.
        sources = list({
            result["metadata"]["source"]
            for result in results
        })

        return {
            "answer": response,
            "sources": sources,
        }
