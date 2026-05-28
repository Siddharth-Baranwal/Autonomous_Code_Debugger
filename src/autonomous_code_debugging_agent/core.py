from __future__ import annotations

import ast
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

ALLOWED_EXTENSIONS = {
    ".py",
    ".ipynb",
    ".js",
    ".ts",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".go",
    ".rs",
    ".rb",
    ".sh",
    ".ps1",
    ".php",
    ".swift",
    ".kt",
    ".kts",
    ".cs",
    ".json",
    ".yaml",
    ".yml",
    ".ini",
    ".md",
    ".txt",
}

IGNORED_DIRS = {
    "venv",
    ".venv",
    "__pycache__",
    ".git",
    ".hg",
    ".idea",
    ".vscode",
    "node_modules",
    "build",
    "dist",
    ".pytest_cache",
}


def load_env_file(env_path: str | Path = ".env") -> None:
    path = Path(env_path)
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def has_code_files(root: Path) -> bool:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS:
            return True
    return False


def clone_repository_from_github(github_url: str, dest_dir: str | Path) -> str:
    dest = Path(dest_dir)
    destination_exists = dest.exists() and any(dest.iterdir())
    if destination_exists:
        print(f"Repository destination exists and non-empty; reusing: {dest}")
        return str(dest)

    dest.mkdir(parents=True, exist_ok=True)
    print(f"Cloning {github_url} into {dest}")

    try:
        if shutil.which("git"):
            subprocess.run(["git", "clone", github_url, str(dest)], check=True, timeout=60)
            return str(dest)
    except Exception as exc:
        print(f"Git clone failed: {exc}")

    try:
        match = re.match(r"https://github.com/([^/]+)/([^/]+)", github_url)
        if not match:
            raise ValueError("Invalid GitHub URL")

        owner, repo = match.group(1), match.group(2)
        archive_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip"
        print(f"Downloading zip archive from {archive_url}")

        data = urllib.request.urlopen(archive_url, timeout=30).read()
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            archive.extractall(str(dest))

        candidates = [child for child in dest.iterdir() if child.is_dir()]

        if not has_code_files(dest) and len(candidates) == 1 and has_code_files(candidates[0]):
            return str(candidates[0])

        for candidate in candidates:
            if candidate.name.endswith(("-master", "-main")) and has_code_files(candidate):
                return str(candidate)

        return str(dest)
    except Exception as exc:
        raise RuntimeError(f"Failed to clone or download repo: {exc}") from exc


def list_code_files(root: str | Path):
    root_path = Path(root)
    code_files = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for filename in filenames:
            if filename.startswith("."):
                continue

            ext = Path(filename).suffix.lower()
            if ext not in ALLOWED_EXTENSIONS:
                continue

            full_path = Path(dirpath) / filename
            try:
                if full_path.stat().st_size > 5 * 1024 * 1024:
                    continue
            except OSError:
                continue

            code_files.append(str(full_path))

    return code_files


def extract_chunks_from_file(path: str | Path):
    path = Path(path)
    ext = path.suffix.lower()

    if ext == ".ipynb":
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as handle:
                notebook = json.load(handle)

            chunks = []
            for idx, cell in enumerate(notebook.get("cells", [])):
                if cell.get("cell_type") != "code":
                    continue
                code = "\n".join(cell.get("source", []))
                if code.strip():
                    chunks.append(
                        {
                            "id": f"{path}:cell:{idx}",
                            "code": code,
                            "meta": {"path": str(path), "kind": "notebook_code", "name": f"cell_{idx}"},
                        }
                    )
            if chunks:
                return chunks
        except Exception:
            pass

    if ext == ".py":
        try:
            source = path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source)
            lines = source.splitlines()
            chunks = []

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    code = "\n".join(lines[node.lineno - 1 : node.end_lineno])
                    kind = "class" if isinstance(node, ast.ClassDef) else "function"
                    chunks.append(
                        {
                            "id": f"{path}:{kind}:{node.name}",
                            "code": code,
                            "meta": {"path": str(path), "kind": kind, "name": node.name},
                        }
                    )

            if chunks:
                return chunks
        except Exception:
            pass

    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        return [
            {
                "id": str(path),
                "code": source,
                "meta": {"path": str(path), "kind": "file", "name": path.name},
            }
        ]
    except Exception:
        return []


def build_index(root: str | Path):
    files = list_code_files(root)
    chunks = []
    for file_path in files:
        chunks.extend(extract_chunks_from_file(file_path))

    docs = [chunk["code"] for chunk in chunks]
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words="english")
    matrix = vectorizer.fit_transform(docs) if docs else None
    return {"chunks": chunks, "vectorizer": vectorizer, "X": matrix}


def query_index(index, query_text: str, top_k: int = 5):
    if index["X"] is None or index["X"].shape[0] == 0:
        return []

    query_vector = index["vectorizer"].transform([query_text])
    similarities = cosine_similarity(query_vector, index["X"])[0]
    identifiers = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", query_text))

    name_matches = [
        idx
        for idx, chunk in enumerate(index["chunks"])
        if chunk["meta"].get("name") in identifiers
    ]

    if name_matches:
        name_matches = sorted(name_matches, key=lambda idx: similarities[idx], reverse=True)
        others = [idx for idx in range(len(index["chunks"])) if idx not in set(name_matches)]
        others = sorted(others, key=lambda idx: similarities[idx], reverse=True)
        ranked = name_matches + others
    else:
        ranked = sorted(range(len(index["chunks"])), key=lambda idx: similarities[idx], reverse=True)

    return [
        (index["chunks"][idx], float(similarities[idx]))
        for idx in ranked[:top_k]
        if similarities[idx] > 0
    ]


def get_llm_fix(error_message: str, relevant_code: str):
    prompt = f"Error: {error_message}\nRelevant code:\n{relevant_code}\nGive one fix."
    from .reasoning.llm_interface import LLMInterface

    return LLMInterface().ask_llm(prompt)
