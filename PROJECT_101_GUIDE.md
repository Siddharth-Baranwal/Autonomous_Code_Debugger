# Autonomous Code Debugging Agent — 101 Guide

This is the beginner-friendly, spoon-fed walkthrough. If you follow this file exactly, you should be able to recreate this project from scratch.

---

## Chapter 1: First, understand the goal

We are building a project that:
1. reads a repository,
2. finds relevant code,
3. asks an AI model for debugging help,
4. and shows the result in a desktop app or report.

Do not try to understand everything at once. Just remember this simple flow:

Input → Read files → Find relevant code → Ask AI → Show result

---

## Chapter 2: Set up your environment exactly

Open PowerShell in your project folder and run these commands one by one:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install openai python-dotenv scikit-learn sentence-transformers tkinterweb anthropic numpy
```

If PowerShell blocks activation, run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Now verify Python works:

```powershell
python --version
```

You should see Python 3.10 or newer.

---

## Chapter 2b: Use the provided release artifacts
If you do not want to rebuild the package from scratch, the repository already includes prepared release folders:

- `windows_setup/` — packaged Windows executable.
- `installable_app/` — Python wheel and prepared Windows executable.
- `professional_execution/` — minimal runtime release package.
- `macos_setup/` — macOS bundle archive.
- `linux_setup/` — Linux bundle archive.

Use these folders for the fastest path to a working product and to avoid rebuilding the installer packages manually.

---

## Chapter 3: Create the project skeleton

Create these folders and files:

```text
Autonomous_Code_Debugging_Agent/
│
├── dashboard.py
├── pyproject.toml
├── README.md
├── src/
│   └── autonomous_code_debugging_agent/
│       ├── api/
│       ├── embeddings/
│       ├── gui/
│       ├── ingestion/
│       ├── reasoning/
│       ├── reporting/
│       ├── retrieval/
│       ├── validation/
│       └── workflows/
├── tests/
└── reports/
```

Create the folders with:

```powershell
mkdir src, src\autonomous_code_debugging_agent, src\autonomous_code_debugging_agent\api, src\autonomous_code_debugging_agent\embeddings, src\autonomous_code_debugging_agent\gui, src\autonomous_code_debugging_agent\ingestion, src\autonomous_code_debugging_agent\reasoning, src\autonomous_code_debugging_agent\reporting, src\autonomous_code_debugging_agent\retrieval, src\autonomous_code_debugging_agent\validation, src\autonomous_code_debugging_agent\workflows, tests, reports
```

---

## Chapter 4: Build the first tiny version

Before the fancy app, build the simplest possible version:

1. take a folder of code,
2. list files,
3. print their content,
4. find something relevant.

Create a file named `mini_probe.py` and run this:

```python
from pathlib import Path

# Walk through every Python file in the current folder
for file in Path(".").rglob("*.py"):
    print("FILE:", file)
    # Show only the first 300 characters for a quick preview
    print(file.read_text(encoding="utf-8", errors="ignore")[:300])
    print("\n--- END OF FILE ---\n")
```

Run it:

```powershell
python mini_probe.py
```

If this works, your foundation is correct.

---

## Chapter 5: Build the repository loader

Create `src/autonomous_code_debugging_agent/ingestion/repo_loader.py`.

Copy this exact code:

```python
from pathlib import Path

# Only include useful source/text files
ALLOWED_EXTENSIONS = {".py", ".md", ".txt", ".json", ".js", ".ts"}
# Skip folders that are usually large or irrelevant
IGNORED_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", "build", "dist"}


def list_code_files(root: str | Path):
    root_path = Path(root)
    files = []

    # Walk the repository tree and collect matching files
    for folder, dirnames, filenames in __import__('os').walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for name in filenames:
            if Path(name).suffix.lower() in ALLOWED_EXTENSIONS:
                files.append(str(Path(folder) / name))

    return files


def load_repository(repo_source: str | Path):
    root = Path(repo_source)
    if not root.exists():
        raise FileNotFoundError("Repository path does not exist")

    # Return the repo path plus the discovered files
    return {"root": str(root), "files": list_code_files(root)}
```

Test it:

```python
from autonomous_code_debugging_agent.ingestion.repo_loader import load_repository

result = load_repository(".")
print("Files found:", len(result["files"]))
for path in result["files"][:10]:
    print(path)
```

If you see file paths, the loader is working.

---

## Chapter 6: Build the chunker

Create `src/autonomous_code_debugging_agent/ingestion/chunker.py`.

Copy this exact code:

```python
import ast
from pathlib import Path


def chunk_code(source: str, path: str | Path):
    path = Path(path)

    # Try to parse Python code into an AST tree
    try:
        tree = ast.parse(source)
    except SyntaxError:
        # If parsing fails, fall back to whole-file chunking
        return [{"path": str(path), "name": path.stem, "kind": "file", "code": source}]

    chunks = []
    lines = source.splitlines()

    # Extract each function as its own chunk
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            chunk = "\n".join(lines[node.lineno - 1: node.end_lineno])
            chunks.append({"path": str(path), "name": node.name, "kind": "function", "code": chunk})

    # If no functions were found, use the whole file as one chunk
    return chunks or [{"path": str(path), "name": path.stem, "kind": "file", "code": source}]


def chunk_repository(files):
    chunks = []
    for file_path in files:
        text = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        chunks.extend(chunk_code(text, file_path))
    return chunks
```

Test it:

```python
from autonomous_code_debugging_agent.ingestion.repo_loader import load_repository
from autonomous_code_debugging_agent.ingestion.chunker import chunk_repository

result = load_repository(".")
chunks = chunk_repository(result["files"])
print("Total chunks:", len(chunks))
for item in chunks[:5]:
    print(item["name"], "->", item["kind"])
```

---

## Chapter 7: Build the simple search layer

Create `src/autonomous_code_debugging_agent/retrieval/retriever.py`.

Copy this:

```python
def retrieve_relevant_chunks(store, query: str, top_k: int = 5):
    return store.search(query, top_k=top_k)
```

You will later connect this to the vector store.

---

## Chapter 8: Build the embedding layer

Create `src/autonomous_code_debugging_agent/embeddings/embedder.py`.

This file converts text into numbers using a simple TF-IDF method.

Copy this starter version:

```python
import math
from collections import Counter


class TfidfEmbedder:
    def __init__(self):
        # Keep track of all text seen so far for IDF calculations
        self.seen_texts = []

    def _tokenize(self, text):
        # Convert text into simple lowercase word tokens
        return [t for t in text.lower().replace("\n", " ").split() if t.isalnum()]

    def encode(self, texts):
        self.seen_texts.extend(texts)
        # Build a vocabulary of all words used in the current corpus
        vocab = sorted(set(token for text in self.seen_texts for token in self._tokenize(text)))
        vocab_index = {token: i for i, token in enumerate(vocab)}
        vectors = []

        for text in texts:
            counts = Counter(self._tokenize(text))
            vector = [0.0] * len(vocab)
            total = sum(counts.values()) or 1

            # Compute TF-IDF value for each token
            for token, count in counts.items():
                tf = count / total
                idf = math.log((len(self.seen_texts) + 1) / (counts[token] + 1)) + 1.0
                vector[vocab_index[token]] = tf * idf
            vectors.append(vector)

        return vectors
```

This is enough to get started.

---

## Chapter 9: Build the vector store

Create `src/autonomous_code_debugging_agent/embeddings/vector_store.py`.

Copy this:

```python
import numpy as np


class InMemoryVectorStore:
    def __init__(self, embedder):
        self.embedder = embedder
        self.records = []

    def add(self, text: str, metadata=None):
        # Store each code chunk with its metadata
        self.records.append({"text": text, "metadata": metadata or {}})

    def search(self, query: str, top_k: int = 5):
        if not self.records:
            return []

        # Convert query to a vector and compare it with each stored chunk
        query_vector = np.asarray(self.embedder.encode([query])[0], dtype=float)
        results = []

        for record in self.records:
            record_vector = np.asarray(self.embedder.encode([record["text"]])[0], dtype=float)
            denom = np.linalg.norm(query_vector) * np.linalg.norm(record_vector)
            score = float(np.dot(query_vector, record_vector) / denom) if denom else 0.0
            results.append((score, record))

        results.sort(key=lambda x: x[0], reverse=True)
        # Only return meaningful matches above zero similarity
        return [{"text": item[1]["text"], "metadata": item[1].get("metadata", {}), "score": item[0]} for item in results[:top_k] if item[0] > 0]
```

---

## Chapter 10: Build the AI reasoning layer

Create `src/autonomous_code_debugging_agent/reasoning/llm_interface.py`.

Start with a simple placeholder that prints what it would send:

```python
class LLMInterface:
    def ask_llm(self, prompt: str) -> str:
        return "AI suggestion placeholder. Replace this with a real API call later."
```

This is your first working reasoning stub.

Later, you can connect OpenAI, Gemini, Anthropic, etc.

---

## Chapter 11: Build the main workflow

Create `src/autonomous_code_debugging_agent/workflows/debugging_loop.py`.

This file connects everything:

```python
from ..embeddings.embedder import TfidfEmbedder
from ..embeddings.vector_store import InMemoryVectorStore
from ..ingestion.chunker import chunk_repository
from ..ingestion.repo_loader import load_repository
from ..reasoning.llm_interface import LLMInterface
from ..retrieval.retriever import retrieve_relevant_chunks


def analyze_repository(repo_source, error_message, top_k=5):
    # Load the repository into a file list
    snapshot = load_repository(repo_source)
    # Split code files into smaller chunks for search and reasoning
    chunks = chunk_repository(snapshot["files"])
    # Create the search index in memory
    store = InMemoryVectorStore(TfidfEmbedder())

    for chunk in chunks:
        # Add each chunk to the vector store
        store.add(chunk["code"], metadata={"path": chunk["path"], "name": chunk["name"]})

    # Find the most relevant chunks for the user error
    results = retrieve_relevant_chunks(store, error_message, top_k=top_k)
    # Build a prompt that combines the error and the best matching code
    prompt = f"Error: {error_message}\n\nRelevant code:\n" + "\n\n".join(item["text"] for item in results)
    # Ask the AI layer for a debugging suggestion
    suggestion = LLMInterface().ask_llm(prompt)

    return {"snapshot": snapshot, "results": results, "suggestion": suggestion}
```

Test it:

```python
from autonomous_code_debugging_agent.workflows.debugging_loop import analyze_repository

report = analyze_repository(".", "division by zero", top_k=3)
print(report)
```

At this point, the full logic is alive.

---

## Chapter 12: Create the desktop GUI

Create `src/autonomous_code_debugging_agent/gui/dashboard.py`.

Start with a very simple Tkinter window:

```python
import tkinter as tk


class DebuggingDashboardApp:
    def __init__(self, root):
        self.root = root
        root.title("Autonomous Code Debugging Agent")
        root.geometry("700x400")

        # Input field for the repository path
        tk.Label(root, text="Repository path:").pack()
        self.repo_var = tk.StringVar(value=".")
        tk.Entry(root, textvariable=self.repo_var).pack(fill="x")

        # Input field for the user error or bug description
        tk.Label(root, text="Error message:").pack()
        self.error_var = tk.StringVar(value="division by zero")
        tk.Entry(root, textvariable=self.error_var).pack(fill="x")

        # Button to start the analysis
        tk.Button(root, text="Run", command=self.run).pack(pady=10)
        self.output = tk.Text(root, height=12)
        self.output.pack(fill="both", expand=True)

    def run(self):
        # Clear previous output and show the placeholder result
        self.output.delete("1.0", "end")
        self.output.insert("end", "This is your starter GUI. Connect the analysis workflow here next.\n")


def main():
    root = tk.Tk()
    DebuggingDashboardApp(root)
    root.mainloop()
```

Run it with:

```powershell
python dashboard.py
```

---

## Chapter 13: Create the CLI entry point

Create `src/autonomous_code_debugging_agent/api/main.py`.

Use this minimal version:

```python
import argparse


def main():
    # Parse command-line arguments for repo path and error message
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--error", default="division by zero")
    args = parser.parse_args()

    # Print the selected inputs for debugging
    print("Repo:", args.repo)
    print("Error:", args.error)


if __name__ == "__main__":
    main()
```

Run it:

```powershell
python -m autonomous_code_debugging_agent.api.main --repo . --error "division by zero"
```

---

## Chapter 14: Create the HTML report

Create `src/autonomous_code_debugging_agent/reporting/html_reporter.py`.

This can start as a simple HTML file writer:

```python
from pathlib import Path


def write_report(content: str, output_file: str = "reports/summary.html"):
    # Make sure the reports folder exists
    Path("reports").mkdir(exist_ok=True)
    # Save the HTML report to disk
    Path(output_file).write_text(content, encoding="utf-8")
    return output_file
```

---

## Chapter 15: Connect the parts

Now replace the placeholder AI response with real calls when you are ready.

Then connect the GUI to the workflow so that when the user clicks Run, the code:
1. loads the repository,
2. finds relevant chunks,
3. asks the AI,
4. and updates the result box.

This is the final integration step.

---

## Chapter 16: Test everything

Run the following checks:

```powershell
python -m pytest
```

If something fails, fix only one thing at a time.

---

## Chapter 17: Package it for sharing

When the project works, add `pyproject.toml` and package it with PyInstaller or a similar tool.

This makes it possible for others to run the app without installing dependencies manually.

---

## Chapter 18: What to remember

The complete project is built from these pieces:

1. repository reader,
2. chunker,
3. embedding/search layer,
4. AI reasoning,
5. GUI and CLI entry points,
6. HTML report generator.

If you can build these six pieces, you have recreated the project.

---

## Chapter 19: Final beginner rule

Do not try to build everything at once.

Build in this order:

1. read files,
2. split chunks,
3. search for relevance,
4. ask AI,
5. show output.

That is the real recipe.

