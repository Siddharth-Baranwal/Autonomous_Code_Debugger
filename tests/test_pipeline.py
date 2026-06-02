import importlib
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from autonomous_code_debugging_agent.ingestion.repo_loader import load_repository
from autonomous_code_debugging_agent.ingestion.chunker import chunk_code
from autonomous_code_debugging_agent.embeddings.embedder import create_embedder
from autonomous_code_debugging_agent.embeddings.vector_store import InMemoryVectorStore
from autonomous_code_debugging_agent.retrieval.retriever import retrieve_relevant_chunks


class PipelineTests(unittest.TestCase):
    # Run the test load repository collects python files logic used by this module.
    def test_load_repository_collects_python_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / "sample.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
            (repo_root / "helper.py").write_text("def multiply(a, b):\n    return a * b\n", encoding="utf-8")

            snapshot = load_repository(str(repo_root))

            self.assertEqual(snapshot["root"], str(repo_root))
            self.assertIn(str(repo_root / "sample.py"), snapshot["files"])
            self.assertIn(str(repo_root / "helper.py"), snapshot["files"])

    # Run the test chunk code extracts function chunks logic used by this module.
    def test_chunk_code_extracts_function_chunks(self):
        source = "def add(a, b):\n    return a + b\n\nclass Calculator:\n    def subtract(self, a, b):\n        return a - b\n"

        chunks = chunk_code(source, path="sample.py")

        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0]["name"], "add")
        self.assertEqual(chunks[1]["name"], "subtract")

    # Run the test retriever returns most relevant chunk logic used by this module.
    def test_retriever_returns_most_relevant_chunk(self):
        embedder = create_embedder("fallback")
        store = InMemoryVectorStore(embedder)
        store.add("def safe_divide(a, b):\n    if b == 0:\n        raise ValueError('division by zero')\n    return a / b\n", {"path": "utils.py", "name": "safe_divide"})
        store.add("def add(a, b):\n    return a + b\n", {"path": "calc.py", "name": "add"})

        results = retrieve_relevant_chunks(store, "division by zero", top_k=1)

        self.assertEqual(results[0]["metadata"]["name"], "safe_divide")

    # Run the test embedder import does not eagerly import sentence transformers logic used by this module.
    def test_embedder_import_does_not_eagerly_import_sentence_transformers(self):
        import builtins

        original_import = builtins.__import__

        # Run the guarded import logic used by this module.
        def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "sentence_transformers":
                raise AssertionError("sentence_transformers should not be imported during embedder import")
            return original_import(name, globals, locals, fromlist, level)

        sys.modules.pop("sentence_transformers", None)
        sys.modules.pop("autonomous_code_debugging_agent.embeddings.embedder", None)

        try:
            builtins.__import__ = guarded_import
            embedder_module = importlib.import_module("autonomous_code_debugging_agent.embeddings.embedder")
        finally:
            builtins.__import__ = original_import

        self.assertTrue(hasattr(embedder_module, "create_embedder"))

    # Run the test load repository accepts string root from clone logic used by this module.
    def test_load_repository_accepts_string_root_from_clone(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / "sample.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")

            with patch(
                "autonomous_code_debugging_agent.ingestion.repo_loader.clone_repository_from_github",
                return_value=str(repo_root),
            ):
                snapshot = load_repository("https://github.com/example/repo")

            self.assertEqual(snapshot["root"], str(repo_root))
            self.assertIn(str(repo_root / "sample.py"), snapshot["files"])


if __name__ == "__main__":
    unittest.main()
