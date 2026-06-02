from __future__ import annotations

import math
import os
from collections import Counter

import numpy as np


class BaseEmbedder:
    # Run the encode logic used by this module.
    def encode(self, texts: list[str]) -> np.ndarray:
        raise NotImplementedError


class TfidfEmbedder(BaseEmbedder):
    # TF-IDF builds a bag-of-words vector where each token gets a term frequency and inverse document frequency weight.
    # Run the init   logic used by this module.
    def __init__(self) -> None:
        self._seen_texts: list[str] = []

    # Run the tokenize logic used by this module.
    def _tokenize(self, text: str) -> list[str]:
        return [token for token in text.lower().replace("\n", " ").split() if token.isalnum()]

    # Run the idf logic used by this module.
    def _idf(self, terms: list[str]) -> dict[str, float]:
        document_count = len(self._seen_texts) or 1
        counts = Counter(terms)
        return {term: math.log((document_count + 1) / (count + 1)) + 1.0 for term, count in counts.items()}

    # Run the encode logic used by this module.
    def encode(self, texts: list[str]) -> np.ndarray:
        self._seen_texts.extend(texts)
        vocab = sorted({token for text in self._seen_texts for token in self._tokenize(text)})
        vocab_index = {token: idx for idx, token in enumerate(vocab)}
        vectors = []

        for text in texts:
            token_counts = Counter(self._tokenize(text))
            vector = np.zeros(len(vocab), dtype=float)
            total = sum(token_counts.values()) or 1
            for token, count in token_counts.items():
                tf = count / total
                idf = self._idf(self._tokenize(text)).get(token, 1.0)
                vector[vocab_index[token]] = tf * idf
            vectors.append(vector)

        return np.asarray(vectors, dtype=float)


# Run the load sentence transformer logic used by this module.
def _load_sentence_transformer() -> type | None:
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:  # pragma: no cover - optional dependency
        return None
    return SentenceTransformer


class SentenceTransformerEmbedder(BaseEmbedder):
    # Run the init   logic used by this module.
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        sentence_transformer = _load_sentence_transformer()
        if sentence_transformer is None:
            raise RuntimeError("sentence-transformers is not installed")
        self.model = sentence_transformer(model_name)

    # Run the encode logic used by this module.
    def encode(self, texts: list[str]) -> np.ndarray:
        return np.asarray(self.model.encode(texts, convert_to_numpy=True), dtype=float)


# Create the embedding, report, or runtime object used by the app.
def create_embedder(kind: str = "auto") -> BaseEmbedder:
    # Choose the best available embedding backend for the current environment.
    env_kind = os.getenv("EMBEDDING_KIND", "fallback")

    if kind == "fallback":
        return TfidfEmbedder()

    if kind == "auto":
        if env_kind == "sentence-transformers" and _load_sentence_transformer() is not None:
            return SentenceTransformerEmbedder()
        return TfidfEmbedder()

    if kind == "sentence-transformers" and _load_sentence_transformer() is not None:
        return SentenceTransformerEmbedder()

    return TfidfEmbedder()
