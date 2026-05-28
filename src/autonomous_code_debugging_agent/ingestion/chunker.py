from __future__ import annotations

import ast
from pathlib import Path


def chunk_code(source: str, path: str | Path) -> list[dict[str, str | int]]:
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


def chunk_repository(files: list[str]) -> list[dict[str, str | int]]:
    chunks = []
    for file_path in files:
        source = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        chunks.extend(chunk_code(source, file_path))
    return chunks
