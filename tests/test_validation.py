import subprocess
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from autonomous_code_debugging_agent.validation.dependency_check import validate_repository_dependencies


class DependencyValidationTests(unittest.TestCase):
    def test_validate_repository_dependencies_passes_for_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

            completed = subprocess.CompletedProcess(
                args=["uv", "run", "--with", "pytest", "pytest"],
                returncode=0,
                stdout="collected 1 item\n1 passed\n",
                stderr="",
            )

            with patch(
                "autonomous_code_debugging_agent.validation.dependency_check.subprocess.run",
                return_value=completed,
            ) as run_mock:
                result = validate_repository_dependencies(repo_root)

            self.assertTrue(result.ok)
            self.assertIn("pytest", run_mock.call_args.args[0])
            self.assertIn("passed", result.message.lower())

    def test_validate_repository_dependencies_fails_for_missing_dependency(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

            completed = subprocess.CompletedProcess(
                args=["uv", "run", "--with", "pytest", "pytest"],
                returncode=1,
                stdout="",
                stderr="ModuleNotFoundError: No module named 'logtools'\n",
            )

            with patch(
                "autonomous_code_debugging_agent.validation.dependency_check.subprocess.run",
                return_value=completed,
            ):
                result = validate_repository_dependencies(repo_root)

            self.assertFalse(result.ok)
            self.assertIn("logtools", result.message)

    def test_validate_repository_dependencies_skips_when_manifest_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            result = validate_repository_dependencies(repo_root)

            self.assertTrue(result.ok)
            self.assertIn("No dependency manifest", result.message)

    def test_validate_repository_dependencies_handles_nested_clone_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            nested_repo = repo_root / "blockexc-parser-main"
            nested_repo.mkdir()
            (nested_repo / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")

            completed = subprocess.CompletedProcess(
                args=["uv", "run", "--with", "pytest", "pytest"],
                returncode=0,
                stdout="collected 1 item\n1 passed\n",
                stderr="",
            )

            with patch(
                "autonomous_code_debugging_agent.validation.dependency_check.subprocess.run",
                return_value=completed,
            ) as run_mock:
                result = validate_repository_dependencies(repo_root)

            self.assertTrue(result.ok)
            self.assertEqual(result.repo_root, nested_repo)
            self.assertIn("pytest", run_mock.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
