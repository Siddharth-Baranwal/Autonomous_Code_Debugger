from __future__ import annotations

import ast
from pathlib import Path


# Run the chunk code logic used by this module.
def chunk_code(source: str, path: str | Path) -> list[dict[str, str | int]]:
    # ast.parse() converts Python text into a syntax tree; walking that tree gives each function node.
    # The line numbers from the AST are used to slice the original source text into the exact function body.
    path = Path(path)
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [
            {
                "path": str(path),
                "name": path.stem,
                "kind": "file",
                "code": source,
                "line_start": 1,
            }
        ]

    chunks = []
    lines = source.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            chunk = "\n".join(lines[node.lineno - 1 : node.end_lineno])
            chunks.append(
                {
                    "path": str(path),
                    "name": node.name,
                    "kind": "function",
                    "code": chunk,
                    "line_start": node.lineno,
                }
            )

    if not chunks:
        chunks.append(
            {
                "path": str(path),
                "name": path.stem,
                "kind": "file",
                "code": source,
                "line_start": 1,
            }
        )

    return chunks


# Run the chunk repository logic used by this module.
def chunk_repository(files: list[str]) -> list[dict[str, str | int]]:
    # Build the full chunk list for all discovered repository files.
    chunks = []
    for file_path in files:
        source = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        chunks.extend(chunk_code(source, file_path))
    return chunks
