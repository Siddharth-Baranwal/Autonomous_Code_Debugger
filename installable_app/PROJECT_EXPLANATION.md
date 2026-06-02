# Autonomous Code Debugging Agent — Project Explanation

This document explains what this project does, how it works from start to finish, and how to talk about it confidently in an interview.

---

## 1. What this project is

This project is a repository analysis and debugging assistant.

Its main goal is to help a developer understand a codebase faster by:
- loading a repository,
- analyzing files and structure,
- finding relevant code sections,
- generating debugging suggestions,
- and presenting the results in a simple dashboard or HTML report.

In short: it turns a messy repository into a structured debugging workflow.

---

## 2. What problem it solves

When someone opens a large project, it is often difficult to:
- know where to start,
- identify the real problem area,
- understand which files matter,
- or get meaningful suggestions quickly.

This project solves that by combining:
- repository inspection,
- code chunk retrieval,
- LLM-based reasoning,
- and an easy-to-use interface.

So instead of manually searching through many files, the app helps guide the analysis in a more organized way.

---

## 3. How the project works from start to finish

### Step 1: User provides a repository or error query
The user starts by giving one of the following:
- a local repository path,
- a GitHub repository link,
- or an error message / debugging question.

This is the starting point of the analysis flow.

### Step 2: The app loads and inspects the repository
The system reads the codebase and identifies relevant files.

It checks:
- project structure,
- source files,
- dependencies,
- and the context around the issue.

This is important because debugging starts with understanding the codebase, not guessing.

### Step 3: The code is split into manageable chunks
Large repositories cannot be analyzed as one giant block.

So the app breaks the code into smaller chunks or sections that are easier to search and reason about.

This makes the analysis more focused and efficient.

### Step 4: Relevant code is retrieved
The system finds the most relevant pieces of code based on the user’s error or query.

This is the part where the app tries to identify what is most likely related to the issue.

### Step 5: LLM reasoning is applied
Once relevant code context is gathered, the project uses an LLM interface to produce debugging suggestions.

This helps answer questions such as:
- why this error might be happening,
- which file or logic path is likely involved,
- or what the next debugging step should be.

The LLM does not replace the developer; it supports the developer by giving context-aware insight.

### Step 6: The result is shown in a dashboard or report
The output is presented in two main ways:
- through a desktop GUI dashboard, and/or
- through an HTML report.

This gives the user a clean summary of the analysis, making the results easy to review.

### Step 7: The notebook prototype supports experimentation
The notebook version is used for:
- testing ideas,
- trying iterative debugging loops,
- and prototyping the analysis flow before turning it into a full application.

So the notebook is not just extra code; it is part of the development and validation process.

---

## 4. Detailed low-level explanation of the major components

### 4.1 Entry points
There are three real entry paths in this project:

1. Desktop GUI
   - The file [dashboard.py](dashboard.py) launches the desktop app.
   - It imports the actual dashboard implementation from [src/autonomous_code_debugging_agent/gui/dashboard.py](src/autonomous_code_debugging_agent/gui/dashboard.py).
   - This is the main product-facing interface for a user.

2. Command-line workflow
   - The CLI entry point is [src/autonomous_code_debugging_agent/api/main.py](src/autonomous_code_debugging_agent/api/main.py).
   - It accepts a repository path, an error message, and optional report settings.
   - It then calls the analysis workflow and prints the JSON result.

3. Notebook prototype
   - The notebook [Project_Autonomous_Code_Debugging_Agent.ipynb](Project_Autonomous_Code_Debugging_Agent.ipynb) is the experimental version.
   - It is useful for testing ideas, iterative loops, and exploring the workflow before packaging it into the app.

### 4.2 Core pipeline: the main brain of the app
The central orchestration logic is in [src/autonomous_code_debugging_agent/workflows/debugging_loop.py](src/autonomous_code_debugging_agent/workflows/debugging_loop.py).

This file does the actual pipeline:

- load_repo
- validate_repo
- chunk_repo
- create embedding store
- retrieve relevant chunks
- build prompt
- ask LLM
- return answer

The most important function is `analyze_repository(...)`:

- It starts by building the retrieval index.
- Then it retrieves the top matching code blocks for the user’s error message.
- It formats those blocks into a prompt.
- It calls the LLM interface to get a debugging suggestion.

This file is the main connection point between the UI, retrieval layer, and reasoning layer.

### 4.3 Repository loading and filtering
The repository loader in [src/autonomous_code_debugging_agent/ingestion/repo_loader.py](src/autonomous_code_debugging_agent/ingestion/repo_loader.py) performs the following operations:

- detects whether the input is a local folder or a GitHub URL,
- clones or downloads the repository if needed,
- walks the tree of the project,
- ignores irrelevant directories such as `.git`, `.venv`, `build`, `dist`, `node_modules`, and `__pycache__`,
- keeps only supported code/text file types,
- and skips oversized files.

This stage is important because the analysis engine should not waste time on junk or unrelated files.

### 4.4 Chunking logic
The chunker in [src/autonomous_code_debugging_agent/ingestion/chunker.py](src/autonomous_code_debugging_agent/ingestion/chunker.py) breaks a file into meaningful pieces.

How it works:

- It reads each file as text.
- It tries to parse it using Python AST.
- If it finds functions, it extracts each function as a separate chunk.
- If parsing fails, it falls back to treating the whole file as one chunk.

This is critical because a large file is hard for a model to reason about, but a function-level chunk is much easier to match and explain.

### 4.5 Embedding and similarity search
The embedder in [src/autonomous_code_debugging_agent/embeddings/embedder.py](src/autonomous_code_debugging_agent/embeddings/embedder.py) converts code/text into vector form.

There are two paths:

- lightweight TF-IDF fallback, which is fast and dependency-light,
- optional sentence-transformer model, which is more semantic but heavier.

The vector store in [src/autonomous_code_debugging_agent/embeddings/vector_store.py](src/autonomous_code_debugging_agent/embeddings/vector_store.py) then:

- stores the chunk text,
- stores metadata for each chunk,
- converts the user query into a vector,
- compares it against all stored vectors,
- and returns the most relevant matches.

This is the retrieval engine behind the app.

### 4.6 How the LLM gets its context
The retrieval function in [src/autonomous_code_debugging_agent/retrieval/retriever.py](src/autonomous_code_debugging_agent/retrieval/retriever.py) simply returns the top relevant chunks from the vector store.

Those chunks are then combined into a prompt using the template in [src/autonomous_code_debugging_agent/reasoning/prompt_templates.py](src/autonomous_code_debugging_agent/reasoning/prompt_templates.py).

The prompt contains:

- the user’s error or question,
- the retrieved code snippets,
- and instructions that tell the model to act like a debugging assistant.

This is what makes the model answer based on actual repository context rather than generic knowledge.

### 4.7 LLM provider integration
The LLM interface in [src/autonomous_code_debugging_agent/reasoning/llm_interface.py](src/autonomous_code_debugging_agent/reasoning/llm_interface.py) is the bridge between the app and multiple AI providers.

It checks for keys such as:

- OPENAI_API_KEY
- GEMINI_API_KEY / GOOGLE_API_KEY
- ANTHROPIC_API_KEY
- GROQ_API_KEY
- GROK_API_KEY / XAI_API_KEY
- MISTRAL_API_KEY
- OPENROUTER_API_KEY
- DEEPSEEK_API_KEY
- AZURE_OPENAI_API_KEY

If a provider key exists, it uses that provider to generate the suggestion.

This makes the app flexible and practical because the user is not limited to one model provider.

### 4.8 HTML report generation
The reporting module in [src/autonomous_code_debugging_agent/reporting/html_reporter.py](src/autonomous_code_debugging_agent/reporting/html_reporter.py) takes the analysis output and converts it into a human-readable HTML summary.

It creates sections for:

- repository name,
- error/problem statement,
- matched code snippet,
- root-cause summary,
- suggested fix,
- and repository snapshot.

This is useful because the user may want to save, share, or review the result outside the dashboard.

### 4.9 GUI layer and runtime keys
The dashboard in [src/autonomous_code_debugging_agent/gui/dashboard.py](src/autonomous_code_debugging_agent/gui/dashboard.py) is the front-end layer.

It handles:

- repository input,
- provider selection,
- runtime key input,
- status messages,
- analysis execution,
- and display of results.

It also supports saving a custom key into `.env` and applying it for the current session.

This makes the desktop experience feel like a real tool rather than a raw script.

### 4.10 Validation and safety checks
Before analysis starts, the dependency validation logic in [src/autonomous_code_debugging_agent/validation/dependency_check.py](src/autonomous_code_debugging_agent/validation/dependency_check.py) checks whether the repository is in a usable state.

This step prevents the app from wasting effort on broken or invalid project inputs.

---

## 5. End-to-end explanation in one line

The project works by taking a repository and an error query, converting repository code into searchable chunks, finding the most relevant snippets, asking an LLM for debugging insight, and showing the result through a GUI or HTML report.

---

## 6. Why this project is useful

This project is useful because it combines three powerful ideas:

1. Repository understanding
   - It helps the user understand what is in the project.

2. Debugging assistance
   - It suggests likely problem areas and next steps.

3. Practical presentation
   - It presents findings in a dashboard or report instead of raw code only.

This makes the project more than just an AI demo. It is closer to a real developer tool.

---

## 7. How to explain it in an interview

A strong interview answer would be:

> “This project is a repository analysis and debugging assistant. It loads a project or error query, analyzes relevant code sections, uses AI-backed reasoning to generate debugging suggestions, and presents the results through a desktop dashboard or report. The main idea is to reduce the time spent manually searching through a codebase and make debugging more structured and guided.”

If the interviewer asks for more detail, you can expand with:
- how the repository is loaded,
- how the code is chunked and retrieved,
- how the LLM contributes to the suggestions,
- and how the GUI and notebook support different phases of development.

---

## 8. What to say if they ask deeper questions

### If they ask: “What was the hardest part?”
You can say:
- making the analysis flow reliable,
- connecting the UI and backend properly,
- and ensuring the LLM path produced useful results instead of generic output.

### If they ask: “Why did you build this?”
You can say:
- because debugging large repositories is time-consuming,
- and AI can help make that process more focused and practical.

### If they ask: “How is it different from a normal chatbot?”
You can say:
- this project is tied to real repository context,
- it works with actual code structure and file retrieval,
- and it produces a more structured debugging workflow instead of just conversation responses.

---

## 9. Short version for quick explanation

If you need a very short summary:

> This project analyzes repositories, finds relevant code context, uses AI to generate debugging suggestions, and presents the results through a desktop dashboard and reports. It is designed to make debugging large codebases faster and more structured.

---

## 10. Final takeaway

The real value of this project is not just the AI part.

Its true strength is the combination of:
- code understanding,
- structured analysis,
- practical reporting,
- and a user-friendly interface.

That is what makes it a strong project to discuss in interviews.
