from __future__ import annotations

import argparse
import json

from ..workflows.debugging_loop import analyze_repository_with_html_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a repository for a failing error message.")
    parser.add_argument("--repo", required=True, help="Path to a local repository or a GitHub URL")
    parser.add_argument("--error", required=True, help="Error or query text to analyze")
    parser.add_argument("--top-k", type=int, default=5, help="Number of code chunks to retrieve")
    parser.add_argument("--report-dir", default="reports", help="Directory where the HTML report will be written")
    args = parser.parse_args()

    report = analyze_repository_with_html_report(
        args.repo,
        args.error,
        top_k=args.top_k,
        output_dir=args.report_dir,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
