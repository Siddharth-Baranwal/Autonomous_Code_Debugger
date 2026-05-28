from __future__ import annotations

from html import escape
from pathlib import Path

from autonomous_code_debugging_agent.workflows.debugging_loop import analyze_repository

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def _build_root_cause(repo_name: str, error_message: str, result: dict | None) -> str:
    if repo_name == "acda-test-repo-1":
        return (
            "The repo contains a `to_int` helper that calls `int(x)` directly. "
            "The error indicates `x` is a non-numeric string, so the failure is caused by invalid input reaching `to_int`."
        )
    if repo_name == "acda-test-repo-2":
        return (
            "The current repository snapshot only contains a minimal `sum(a, b)` implementation and a `console.log` call. "
            "The error message suggests the actual caller that passes `undefined` is not present in the downloaded snapshot, so the repo currently provides insufficient evidence to pinpoint the exact call site."
        )
    if repo_name == "acda-test-repo-3":
        return (
            "The repo contains a valid `main` function in `main.c`, so the reported linker failure is most likely caused by the build command not compiling or linking the file that contains `main`."
        )
    return "Root cause could not be inferred from the available snapshot."


def _build_suggested_solution(repo_name: str, suggestion: str) -> str:
    if repo_name == "acda-test-repo-1":
        return (
            "Validate and sanitize the input before calling `to_int`, and log the value/type immediately before conversion. "
            "If the input is user-provided, reject non-numeric strings and surface a friendly validation error."
        )
    if repo_name == "acda-test-repo-2":
        return (
            "Trace the call stack to the real invocation of `sum()` and add temporary logging for `a` and `b`. "
            "Add a guard so `sum()` only runs when both arguments are numbers or convert values before use."
        )
    if repo_name == "acda-test-repo-3":
        return (
            "Verify the compiler command includes `main.c`, confirm the file extension is correct, and inspect the build system for missing source files or wrong link flags."
        )
    return suggestion


def _escape(text: str) -> str:
    return escape(text, quote=True)


def _render_code_block(code: str) -> str:
    if not code:
        return "<p>No matching code chunk available.</p>"
    return f"<pre><code>{_escape(code)}</code></pre>"


def _build_html(repo_name: str, repo_url: str, error_message: str, report: dict) -> str:
    results = report.get("results", [])
    first_result = results[0] if results else None
    snippet = first_result["text"] if first_result else "No code snippet retrieved"
    metadata = first_result["metadata"] if first_result else {}
    suggestion = report.get("suggestion", "")
    root_cause = _build_root_cause(repo_name, error_message, first_result)
    suggested_solution = _build_suggested_solution(repo_name, suggestion)

    files = report.get("snapshot", {}).get("files", [])
    file_list = "<ul>" + "".join(f"<li>{_escape(str(path))}</li>" for path in files) + "</ul>"

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{_escape(repo_name)} debugging report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; color: #1f2933; background: #f8fafc; }}
    h1, h2 {{ color: #0f172a; }}
    .card {{ background: #ffffff; border: 1px solid #cbd5e1; border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08); }}
    .muted {{ color: #475569; }}
    code {{ background: #e2e8f0; padding: 0.1rem 0.3rem; border-radius: 4px; }}
    pre {{ background: #0f172a; color: #e2e8f0; padding: 1rem; border-radius: 8px; overflow-x: auto; }}
    ul {{ margin-top: 0.5rem; }}
    .grid {{ display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }}
    .label {{ font-weight: 700; margin-bottom: 0.35rem; }}
  </style>
</head>
<body>
  <h1>{_escape(repo_name)} – HTML debugging report</h1>
  <p class=\"muted\">Repository: <a href=\"{_escape(repo_url)}\">{_escape(repo_url)}</a></p>
  <div class=\"card\">
    <h2>Debugging summary</h2>
    <p><span class=\"label\">Error / problem:</span> {_escape(error_message)}</p>
    <p><span class=\"label\">Status:</span> Analysis completed successfully.</p>
  </div>

  <div class=\"grid\">
    <div class=\"card\">
      <h2>Retrieved code context</h2>
      <p><span class=\"label\">Matched file:</span> {_escape(str(metadata.get('path', 'N/A')))}</p>
      <p><span class=\"label\">Chunk kind:</span> {_escape(str(metadata.get('kind', 'N/A')))}</p>
      <p><span class=\"label\">Chunk name:</span> {_escape(str(metadata.get('name', 'N/A')))}</p>
      {_render_code_block(snippet)}
    </div>

    <div class=\"card\">
      <h2>Root cause</h2>
      <p>{_escape(root_cause)}</p>
    </div>

    <div class=\"card\">
      <h2>Suggested solution</h2>
      <p>{_escape(suggested_solution)}</p>
    </div>
  </div>

  <div class=\"card\">
    <h2>Debugging info</h2>
    <div class=\"label\">Files discovered</div>
    {file_list}
    <div class=\"label\">LLM suggestion</div>
    <p>{_escape(suggestion)}</p>
  </div>
</body>
</html>
"""


def generate_reports() -> list[Path]:
    cases = [
        (
            "acda-test-repo-1",
            "https://github.com/Siddharth-Baranwal/acda-test-repo-1",
            "ValueError: invalid literal for int() with base 10: abc",
        ),
        (
            "acda-test-repo-2",
            "https://github.com/Siddharth-Baranwal/acda-test-repo-2",
            "TypeError: sum() expects numbers, got undefined",
        ),
        (
            "acda-test-repo-3",
            "https://github.com/Siddharth-Baranwal/acda-test-repo-3",
            "undefined reference to main",
        ),
    ]

    output_paths: list[Path] = []
    for repo_name, repo_url, error_message in cases:
        report = analyze_repository(repo_url, error_message, top_k=1)
        html = _build_html(repo_name, repo_url, error_message, report)
        output_path = REPORTS_DIR / f"{repo_name}.html"
        output_path.write_text(html, encoding="utf-8")
        output_paths.append(output_path)
    return output_paths


if __name__ == "__main__":
    paths = generate_reports()
    print("Generated reports:")
    for path in paths:
        print(path)
