from __future__ import annotations

import io
import os
import re
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

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


def _is_github_url(value: str | Path) -> bool:
    if not isinstance(value, str):
        return False
    return value.startswith(("http://", "https://")) and "github.com/" in value


def _has_code_files(root: Path) -> bool:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS:
            return True
    return False


def clone_repository_from_github(github_url: str, dest_dir: str | Path) -> str:
    dest = Path(dest_dir)
    if dest.exists() and any(dest.iterdir()):
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

        if not _has_code_files(dest) and len(candidates) == 1 and _has_code_files(candidates[0]):
            return str(candidates[0])

        for candidate in candidates:
            if candidate.name.endswith(("-master", "-main")) and _has_code_files(candidate):
                return str(candidate)

        return str(dest)
    except Exception as exc:
        raise RuntimeError(f"Failed to clone or download repo: {exc}") from exc


def list_code_files(root: str | Path):
    root_path = Path(root)
    code_files = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [directory for directory in dirnames if directory not in IGNORED_DIRS]
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


def load_repository(repo_source: str | Path):
    if _is_github_url(repo_source):
        repo_name = str(repo_source).rstrip("/").split("/")[-1]
        cache_root = Path(".cache") / repo_name
        cloned_root = clone_repository_from_github(str(repo_source), cache_root)
        root = Path(cloned_root)
    else:
        root = Path(repo_source)

    if not root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_source}")

    return {"root": str(root), "files": list_code_files(root)}
