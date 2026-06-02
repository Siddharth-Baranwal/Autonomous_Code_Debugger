from __future__ import annotations

from ..workflows.debugging_loop import analyze_repository


class DebuggerAgent:
    # Run the debug logic used by this module.
    def debug(self, repo_source: str, error_message: str, top_k: int = 5):
        return analyze_repository(repo_source, error_message, top_k=top_k)
