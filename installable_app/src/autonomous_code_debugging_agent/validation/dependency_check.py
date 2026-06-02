from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from ..ingestion.repo_loader import clone_repository_from_github


# Run the is github url logic used by this module.
def _is_github_url(value: str | Path) -> bool:
    if not isinstance(value, str):
        return False
    return value.startswith(("http://", "https://")) and "github.com/" in value


DEPENDENCY_MANIFESTS = (
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "poetry.lock",
    "Pipfile",
    "setup.py",
    "setup.cfg",
    "environment.yml",
    "environment.yaml",
)


@dataclass
class RepoValidationResult:
    repo_root: Path
    ok: bool
    command: list[str]
    message: str
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0


# Run the resolve repo root logic used by this module.
def _resolve_repo_root(repo_source: str | Path) -> Path:
    if _is_github_url(repo_source):
        repo_name = str(repo_source).rstrip("/").split("/")[-1]
        cloned_root = clone_repository_from_github(str(repo_source), Path(".cache") / repo_name)
        return _normalize_repo_root(Path(cloned_root))

    root = Path(repo_source)
    if not root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_source}")
    return _normalize_repo_root(root)


# Run the has dependency manifest logic used by this module.
def _has_dependency_manifest(repo_root: Path) -> bool:
    return any((repo_root / manifest).exists() for manifest in DEPENDENCY_MANIFESTS)


# Run the normalize repo root logic used by this module.
def _normalize_repo_root(repo_root: Path) -> Path:
    if _has_dependency_manifest(repo_root):
        return repo_root

    children = [child for child in repo_root.iterdir() if child.is_dir()]
    if len(children) == 1 and _has_dependency_manifest(children[0]):
        return children[0]

    return repo_root


# Run the build validation command logic used by this module.
def _build_validation_command() -> list[str]:
    if shutil.which("uv"):
        return ["uv", "run", "--with", "pytest", "pytest"]
    return [sys.executable, "-m", "pytest"]


# Run the summarize failure logic used by this module.
def _summarize_failure(result: subprocess.CompletedProcess[str]) -> str:
    combined = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()

    if not combined:
        return f"Dependency validation failed with exit code {result.returncode}."

    if "Git executable not found" in combined:
        return (
            "Dependency validation failed because the target repository depends on a git-based package "
            "and Git is not available in this environment."
        )

    if "ModuleNotFoundError" in combined:
        missing = [line for line in combined.splitlines() if "ModuleNotFoundError" in line]
        if missing:
            return f"Dependency validation failed: {missing[0].strip()}"

    if "Failed to resolve" in combined:
        return f"Dependency validation failed: {combined.splitlines()[-1].strip()}"

    return f"Dependency validation failed: {combined.splitlines()[-1].strip()}"


# Validate the repository or environment before continuing the workflow.
def validate_repository_dependencies(repo_source: str | Path) -> RepoValidationResult:
    # Resolve the target repository and validate whether its dependency setup works.
    repo_root = _resolve_repo_root(repo_source)

    if not _has_dependency_manifest(repo_root):
        return RepoValidationResult(
            repo_root=repo_root,
            ok=True,
            command=[],
            message="No dependency manifest found; skipped validation.",
        )

    command = _build_validation_command()
    completed = subprocess.run(
        command,
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    if completed.returncode == 0:
        return RepoValidationResult(
            repo_root=repo_root,
            ok=True,
            command=command,
            message=f"Dependency validation passed using {' '.join(command)}.",
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
        )

    if completed.returncode == 5 and (
        "no tests collected" in completed.stdout.lower() or "no tests collected" in completed.stderr.lower()
    ):
        return RepoValidationResult(
            repo_root=repo_root,
            ok=True,
            command=command,
            message=f"Dependency validation passed; pytest reported no tests in {' '.join(command)}.",
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
        )

    return RepoValidationResult(
        repo_root=repo_root,
        ok=False,
        command=command,
        message=_summarize_failure(completed),
        stdout=completed.stdout,
        stderr=completed.stderr,
        exit_code=completed.returncode,
    )
