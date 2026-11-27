
"""Retrieve relevant knowledge-base chunks using hybrid search."""

import re

from rank_bm25 import BM25Okapi

from rag.vector_store import VectorStore

import logging

logger = logging.getLogger(__name__)

class Retriever:

    def __init__(self, n_results: int = 3):
        self.vector_store = VectorStore()
        self.n_results = n_results

        self.documents = self.vector_store.get_all_documents()

        self.tokenized_documents = [
            self._tokenize(document["text"])
            for document in self.documents
        ]

        self.bm25 = (
            BM25Okapi(self.tokenized_documents)
            if self.tokenized_documents
            else None
        )

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Normalize customer language and create searchable tokens."""

        text = text.lower()

        replacements = {
            "send back": "return",
            "sent back": "return",
            "sending back": "return",
            "wanna": "want to",
            "availble": "available",
            "avialable": "available",
            "u": "you",
            "pls": "please",
            "transaction": "payment",
            "transactions": "payment",
            "paymant": "payment",
            "didnt": "does not",
            "thru": "through",
        }


        for original, replacement in replacements.items():
          text = re.sub(
                 rf"\b{re.escape(original)}\b",
                 replacement,
                 text,
          )

        stopwords = {
            "i", "me", "my", "the", "a", "an", "is", "are",
            "do", "does", "did", "to", "for", "of", "in",
            "on", "what", "how", "much", "can", "you", "your",
            "please", "want","was", "it",
        }

        tokens = re.findall(r"\b\w+\b", text)

        return [
            token for token in tokens
            if token not in stopwords
        ]

    def retrieve(self, query: str) -> list[dict]:
        """Retrieve relevant chunks using Reciprocal Rank Fusion."""

        if not query.strip() or not self.documents:
            return []

        normalized_query = " ".join(self._tokenize(query))

        # Semantic search
        try:
           semantic_results = self.vector_store.search(
               query=normalized_query,
               n_results=len(self.documents),
           )
        except Exception:
            logger.exception("Semantic search failed; continuing with BM25.")
            semantic_results = []

        semantic_ranks = {
            (
                result["metadata"]["source"],
                result["metadata"]["chunk_index"],
            ): rank
            for rank, result in enumerate(semantic_results, start=1)
        }

        semantic_distances = {
            (
                result["metadata"]["source"],
                result["metadata"]["chunk_index"],
            ): result["distance"]
            for result in semantic_results
        }

        # Keyword search
        query_tokens = self._tokenize(query)

        if self.bm25:
            keyword_scores = self.bm25.get_scores(query_tokens)
        else:
            keyword_scores = []

        keyword_ranks = {}

        if len(keyword_scores):
            ranked_indices = sorted(
                range(len(keyword_scores)),
                key=lambda index: keyword_scores[index],
                reverse=True,
            )

            for rank, index in enumerate(ranked_indices, start=1):
                if keyword_scores[index] > 0:
                    document = self.documents[index]

                    key = (
                        document["metadata"]["source"],
                        document["metadata"]["chunk_index"],
                    )

                    keyword_ranks[key] = rank

        # Combine rankings using Reciprocal Rank Fusion
        combined_results = []

        for index, document in enumerate(self.documents):

            key = (
                document["metadata"]["source"],
                document["metadata"]["chunk_index"],
            )


            distance = semantic_distances.get(key)

            keyword_score = (
                float(keyword_scores[index])
                if len(keyword_scores) > index
                else 0.0
            )

            # Reject weak matches from both retrieval methods.
            if distance is not None and distance > 0.57 and keyword_score < 2.5:
                continue

            if distance is None and keyword_score <= 0:
                continue
            semantic_rank = semantic_ranks.get(key)
            keyword_rank = keyword_ranks.get(key)

            rrf_score = 0.0

            if semantic_rank is not None:
                rrf_score += 1 / (60 + semantic_rank)

            if keyword_rank is not None:
                rrf_score += 1 / (60 + keyword_rank)

            combined_results.append({
                "text": document["text"],
                "metadata": document["metadata"],
                "distance": distance,
                "keyword_score": keyword_score,
                "rrf_score": rrf_score,
            })

        combined_results.sort(
            key=lambda result: result["rrf_score"],
            reverse=True,
        )

        return combined_results[:self.n_results]

    def build_context(self, results: list[dict]) -> str:
        """Combine retrieved chunks into context for the LLM."""

        if not results:
            return "No relevant information was found in the knowledge base."

        context_parts = []

        for result in results:
            source = result["metadata"]["source"]
            content = result["text"]

            context_parts.append(
                f"Source: {source}\nContent: {content}"
            )

        return "\n\n".join(context_parts)
