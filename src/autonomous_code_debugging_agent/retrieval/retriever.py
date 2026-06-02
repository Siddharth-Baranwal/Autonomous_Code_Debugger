from __future__ import annotations


# Run the retrieve relevant chunks logic used by this module.
def retrieve_relevant_chunks(store, query: str, top_k: int = 5):
    # Delegate the search to the underlying vector store.
    return store.search(query, top_k=top_k)
