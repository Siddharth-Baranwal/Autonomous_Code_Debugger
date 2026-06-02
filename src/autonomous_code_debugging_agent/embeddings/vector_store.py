from __future__ import annotations

import numpy as np


class InMemoryVectorStore:
    # Run the init   logic used by this module.
    def __init__(self, embedder) -> None:
        self.embedder = embedder
        self.records: list[dict[str, object]] = []

    # Run the add logic used by this module.
    def add(self, text: str, metadata: dict[str, str] | None = None) -> None:
        # Encode the chunk once so it is ready for similarity search.
        self.embedder.encode([text])
        self.records.append(
            {
                "text": text,
                "metadata": metadata or {},
            }
        )

    # Run the search logic used by this module.
    def search(self, query: str, top_k: int = 5) -> list[dict[str, object]]:
        # np.dot computes the numerator of cosine similarity, and the norms in the denominator normalize the vectors.
        # We keep only scores greater than zero so unrelated chunks are discarded.
        if not self.records:
            return []

        query_vector = np.asarray(self.embedder.encode([query])[0], dtype=float)
        scored = []

        for record in self.records:
            record_vector = np.asarray(self.embedder.encode([str(record["text"])])[0], dtype=float)
            denominator = np.linalg.norm(query_vector) * np.linalg.norm(record_vector)
            score = float(np.dot(query_vector, record_vector) / denominator) if denominator else 0.0
            scored.append((score, record))

        scored.sort(key=lambda item: item[0], reverse=True)
        results = []
        for score, record in scored[:top_k]:
            if score <= 0:
                continue
            results.append(
                {
                    "text": record["text"],
                    "metadata": record["metadata"],
                    "score": score,
                }
            )

        return results
