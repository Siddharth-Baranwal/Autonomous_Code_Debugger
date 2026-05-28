from __future__ import annotations

from pathlib import Path

from ..embeddings.embedder import create_embedder
from ..embeddings.vector_store import InMemoryVectorStore
from ..ingestion.chunker import chunk_repository
from ..ingestion.repo_loader import load_repository
from ..reasoning.llm_interface import LLMInterface
from ..reasoning.prompt_templates import DEBUG_PROMPT
from ..reporting.html_reporter import HTMLReportGenerator
from ..retrieval.retriever import retrieve_relevant_chunks
from ..validation.dependency_check import validate_repository_dependencies


def build_index(repo_source, embedder=None):
    snapshot = load_repository(repo_source)
    validation = validate_repository_dependencies(snapshot["root"])
    if not validation.ok:
        raise RuntimeError(validation.message)

    chunks = chunk_repository(snapshot["files"])
    embedder = embedder or create_embedder("auto")
    store = InMemoryVectorStore(embedder)

    for chunk in chunks:
        metadata = {"path": str(chunk["path"]), "name": str(chunk["name"]), "kind": str(chunk["kind"])}
        store.add(str(chunk["code"]), metadata)

    return {"snapshot": snapshot, "chunks": chunks, "store": store}


def analyze_repository(repo_source, error_message, top_k: int = 5):
    index = build_index(repo_source)
    results = retrieve_relevant_chunks(index["store"], error_message, top_k=top_k)

    code_context = "\n\n".join(str(result["text"]) for result in results)
    prompt = DEBUG_PROMPT.format(error=error_message, code=code_context)
    suggestion = LLMInterface().ask_llm(prompt)

    return {"snapshot": index["snapshot"], "results": results, "suggestion": suggestion}


def analyze_repository_with_html_report(
    repo_source,
    error_message,
    top_k: int = 5,
    output_dir: str | Path | None = None,
    report_name: str | None = None,
):
    report = analyze_repository(repo_source, error_message, top_k=top_k)
    report_path = HTMLReportGenerator().save_report(
        report=report,
        repo_source=repo_source,
        error_message=error_message,
        output_dir=Path(output_dir) if output_dir is not None else None,
        report_name=report_name,
    )
    report["report_path"] = str(report_path)
    return report
