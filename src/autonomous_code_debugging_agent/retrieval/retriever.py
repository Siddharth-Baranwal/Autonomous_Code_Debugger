from __future__ import annotations


def retrieve_relevant_chunks(store, query: str, top_k: int = 5):
    return store.search(query, top_k=top_k)
