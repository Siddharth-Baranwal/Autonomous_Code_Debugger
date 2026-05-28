import os
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from autonomous_code_debugging_agent.gui.dashboard import apply_runtime_llm_key, persist_llm_key_to_env, resolve_repository_source


class DashboardRepositorySourceTests(unittest.TestCase):
    def test_resolve_repository_source_for_github(self):
        self.assertEqual(
            resolve_repository_source("GitHub", "https://github.com/example/repo"),
            "https://github.com/example/repo",
        )

    def test_resolve_repository_source_for_local_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            resolved = resolve_repository_source("Local", str(repo_path))
            self.assertEqual(resolved, str(repo_path))

    def test_resolve_repository_source_rejects_empty_input(self):
        with self.assertRaises(ValueError):
            resolve_repository_source("GitHub", "   ")

    def test_resolve_repository_source_rejects_invalid_github_link(self):
        with self.assertRaises(ValueError):
            resolve_repository_source("GitHub", "not-a-github-link")


class RuntimeLLMKeyTests(unittest.TestCase):
    def test_apply_runtime_llm_key_sets_openai_key(self):
        with patch.dict("os.environ", {}, clear=True):
            status = apply_runtime_llm_key("OpenAI", "sk-test-key")
            self.assertEqual(os.environ["OPENAI_API_KEY"], "sk-test-key")
            self.assertEqual(status, "Custom OpenAI key applied for this session.")

    def test_apply_runtime_llm_key_supports_groq_provider(self):
        with patch.dict("os.environ", {}, clear=True):
            status = apply_runtime_llm_key("Groq", "gq-test-key")
            self.assertEqual(os.environ["GROQ_API_KEY"], "gq-test-key")
            self.assertEqual(status, "Custom Groq key applied for this session.")

    def test_apply_runtime_llm_key_supports_grok_provider(self):
        with patch.dict("os.environ", {}, clear=True):
            status = apply_runtime_llm_key("Grok", "xai-test-key")
            self.assertEqual(os.environ["GROK_API_KEY"], "xai-test-key")
            self.assertEqual(status, "Custom Grok key applied for this session.")

    def test_apply_runtime_llm_key_rejects_empty_key(self):
        with self.assertRaises(ValueError):
            apply_runtime_llm_key("Gemini", "   ")

    def test_persist_llm_key_to_env_writes_selected_provider(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("OPENAI_API_KEY=old-key\nEXTRA=keep\n", encoding="utf-8")

            status = persist_llm_key_to_env("Gemini", "gemini-key", env_path=env_path)

            self.assertEqual(status, "Custom Gemini key saved to .env.")
            self.assertEqual(env_path.read_text(encoding="utf-8"), "EXTRA=keep\nGEMINI_API_KEY=gemini-key\n")

    def test_persist_llm_key_to_env_supports_openrouter_provider(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text("OPENAI_API_KEY=old-key\n", encoding="utf-8")

            status = persist_llm_key_to_env("OpenRouter", "or-key", env_path=env_path)

            self.assertEqual(status, "Custom OpenRouter key saved to .env.")
            self.assertIn("OPENROUTER_API_KEY=or-key", env_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
