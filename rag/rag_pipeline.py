
"""Combine retrieval and Gemini generation into a RAG pipeline."""

from llm import chat
from llm import groq_chat
from rag.retriever import Retriever


RAG_SYSTEM_PROMPT = """You are the customer support assistant for Bean & Brew.

Answer customer questions using the provided knowledge-base context.

Rules:
- Use the supplied context as your source of truth.
- Do not invent store policies, delivery times, prices, or other facts.
- If the context does not contain the answer, clearly say you do not have
  that information and offer to create a support ticket.
- Be friendly, concise, and professional.
- Never ask for full card numbers or passwords.
- If the customer mentions a payment problem or asks for a human,
  offer human escalation.
"""


class RAGPipeline:

    def __init__(self):
        self.retriever = Retriever(n_results=3)

    def answer(self, question: str) -> dict:
        """Retrieve relevant context and generate a grounded answer."""

        results = self.retriever.retrieve(question)
        context = self.retriever.build_context(results)

        prompt = f"""Knowledge-base context:

{context}

Customer question:
{question}

Answer the customer using the rules provided."""

        response = groq_chat(
            messages=[
                {"role": "user", "content": prompt}
            ],
            system=RAG_SYSTEM_PROMPT,
        )

        sources = list({
            result["metadata"]["source"]
            for result in results
        })

        return {
            "answer": response,
            "sources": sources,
        }
