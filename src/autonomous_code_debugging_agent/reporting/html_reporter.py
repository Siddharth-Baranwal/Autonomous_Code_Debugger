from __future__ import annotations

from html import escape
from pathlib import Path
from urllib.parse import urlparse


class HTMLReportGenerator:
    # Run the init   logic used by this module.
    def __init__(self, reports_dir: Path | None = None) -> None:
        self.reports_dir = Path(reports_dir) if reports_dir is not None else Path.cwd() / "reports"

    # Run the repo name logic used by this module.
    def _repo_name(self, repo_source: str | Path) -> str:
        # Convert the repository input into a friendly display name for the report.
        if isinstance(repo_source, Path):
            repo_source = str(repo_source)

        repo_source = str(repo_source).rstrip("/")
        if repo_source.startswith(("http://", "https://")):
            parsed = urlparse(repo_source)
            parts = [segment for segment in parsed.path.split("/") if segment]
            if parts:
                return parts[-1]
            return "repository"

        path = Path(repo_source).expanduser()
        return path.name or "repository"

    # Run the safe filename logic used by this module.
    def _safe_filename(self, repo_name: str) -> str:
        safe = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in repo_name)
        return safe.strip("-") or "repository"

    # Run the root cause logic used by this module.
    def _root_cause(self, report: dict, error_message: str) -> str:
        results = report.get("results", [])
        first_result = results[0] if results else None
        if first_result:
            snippet = str(first_result.get("text", ""))
            if "FileNotFoundError" in snippet or "No such file or directory" in snippet:
                return (
                    "The retrieved code path is present, but the repository is trying to read a file path that does not exist. "
                    "This usually indicates an incorrect path constant or a missing resource file."
                )
            if "division by zero" in snippet.lower() or "zero division" in snippet.lower():
                return "The retrieved code path exposes an arithmetic edge case where the code does not guard against an invalid divisor."
            if "raise" in snippet.lower() and "error" in error_message.lower():
                return f"The code path related to the reported failure is the one surfaced by the retrieval step. The current implementation likely needs additional validation or guarding around the failing branch."

        if error_message:
            return (
                "The report contains a matching repository snapshot and a retrieved code context, but the root cause needs to be inferred from the failing path and the suggested fix."
            )

        return "No specific root cause could be inferred from the available report data."

    # Run the suggested solution logic used by this module.
    def _suggested_solution(self, report: dict) -> str:
        suggestion = str(report.get("suggestion", "")).strip()
        if suggestion:
            return suggestion
        return "No LLM suggestion was available for this run."

    # Run the render files logic used by this module.
    def _render_files(self, report: dict) -> str:
        files = report.get("snapshot", {}).get("files", [])
        if not files:
            return "<p>No files discovered in the repository snapshot.</p>"
        items = "".join(f"<li>{escape(str(path))}</li>" for path in files)
        return f"<ul>{items}</ul>"

    # Run the render code block logic used by this module.
    def _render_code_block(self, report: dict) -> str:
        results = report.get("results", [])
        if not results:
            return "<p>No matching code chunk was retrieved.</p>"

        first_result = results[0]
        code = str(first_result.get("text", ""))
        if not code:
            return "<p>No matching code chunk was retrieved.</p>"
        return f"<pre><code>{escape(code)}</code></pre>"

    # Build the internal data structure used by the analysis pipeline.
    def build_html(self, report: dict, repo_source: str | Path, error_message: str) -> str:
        repo_name = self._repo_name(repo_source)
        suggestion = self._suggested_solution(report)
        root_cause = self._root_cause(report, error_message)
        metadata = report.get("results", [{}])[0].get("metadata", {}) if report.get("results") else {}

        return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{escape(repo_name)} debugging summary</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; background: #f8fafc; color: #0f172a; }}
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
  <h1>{escape(repo_name)} – automated debugging HTML summary</h1>
  <p class=\"muted\">Source: {escape(str(repo_source))}</p>

  <div class=\"card\">
    <h2>Debugging summary</h2>
    <p><span class=\"label\">Error / problem:</span> {escape(error_message)}</p>
    <p><span class=\"label\">Status:</span> Analysis completed successfully.</p>
  </div>

  <div class=\"grid\">
    <div class=\"card\">
      <h2>Retrieved code context</h2>
      <p><span class=\"label\">Matched file:</span> {escape(str(metadata.get('path', 'N/A')))}</p>
      <p><span class=\"label\">Chunk kind:</span> {escape(str(metadata.get('kind', 'N/A')))}</p>
      <p><span class=\"label\">Chunk name:</span> {escape(str(metadata.get('name', 'N/A')))}</p>
      {self._render_code_block(report)}
    </div>

    <div class=\"card\">
      <h2>Root cause</h2>
      <p>{escape(root_cause)}</p>
    </div>

    <div class=\"card\">
      <h2>Suggested solution</h2>
      <p>{escape(suggestion)}</p>
    </div>
  </div>

  <div class=\"card\">
    <h2>Repository snapshot</h2>
    {self._render_files(report)}
  </div>
</body>
</html>
"""

    def get_output_path(
        self,
        repo_source: str | Path,
        output_dir: Path | None = None,
        report_name: str | None = None,
    ) -> Path:
        target_dir = Path(output_dir) if output_dir is not None else self.reports_dir
        repo_name = self._repo_name(repo_source)
        safe_name = self._safe_filename(report_name or repo_name)
        return target_dir / f"{safe_name}.html"

    # Save the generated result to the requested destination.
    def save_report(
        self,
        report: dict,
        repo_source: str | Path,
        error_message: str,
        output_dir: Path | None = None,
        report_name: str | None = None,
    ) -> Path:
        # Write the generated HTML report to disk for later review.
        target_dir = Path(output_dir) if output_dir is not None else self.reports_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        output_path = self.get_output_path(repo_source, output_dir=target_dir, report_name=report_name)
        output_path.write_text(self.build_html(report, repo_source, error_message), encoding="utf-8")
        return output_path


# Generate the output artifact or report described by the function.
def generate_html_summary(
    report: dict,
    repo_source: str | Path,
    error_message: str,
    output_dir: Path | None = None,
    report_name: str | None = None,
) -> Path:
    generator = HTMLReportGenerator(reports_dir=output_dir)
    return generator.save_report(report, repo_source, error_message, output_dir=output_dir, report_name=report_name)
