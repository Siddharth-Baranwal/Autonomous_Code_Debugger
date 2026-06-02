from pathlib import Path
import tempfile
import unittest

from autonomous_code_debugging_agent.reporting.html_reporter import HTMLReportGenerator
from autonomous_code_debugging_agent.workflows.debugging_loop import analyze_repository_with_html_report


class ReportingTests(unittest.TestCase):
    # Run the test html report generator writes summary file logic used by this module.
    def test_html_report_generator_writes_summary_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            report = {
                "snapshot": {"files": ["src/example.py"]},
                "results": [
                    {
                        "text": "def divide(a, b):\n    if b == 0:\n        raise ZeroDivisionError\n    return a / b",
                        "metadata": {
                            "path": "src/example.py",
                            "name": "divide",
                            "kind": "function",
                        },
                    }
                ],
                "suggestion": "Guard against division by zero.",
            }

            output_path = HTMLReportGenerator().save_report(
                report=report,
                repo_source="https://github.com/example/debug-repo",
                error_message="ZeroDivisionError: division by zero",
                output_dir=Path(temp_dir),
            )

            self.assertTrue(output_path.exists())
            html = output_path.read_text(encoding="utf-8")
            self.assertIn("debug-repo", html)
            self.assertIn("ZeroDivisionError: division by zero", html)
            self.assertIn("Guard against division by zero.", html)
            self.assertIn("src/example.py", html)

    # Run the test analyze repository with html report writes file logic used by this module.
    def test_analyze_repository_with_html_report_writes_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / "sample.py").write_text(
                "def divide(a, b):\n    if b == 0:\n        raise ZeroDivisionError\n    return a / b\n",
                encoding="utf-8",
            )

            report = analyze_repository_with_html_report(
                str(repo_root),
                "ZeroDivisionError: division by zero",
                top_k=1,
                output_dir=Path(temp_dir),
            )

            report_path = Path(report["report_path"])
            self.assertTrue(report_path.exists())
            html = report_path.read_text(encoding="utf-8")
            self.assertIn("ZeroDivisionError: division by zero", html)
            self.assertIn("sample.py", html)


if __name__ == "__main__":
    unittest.main()
