# Autonomous Code Debugging Agent

A desktop-friendly repository analysis tool that inspects a project, validates dependencies, and generates debugging insights through a polished Tkinter dashboard, a CLI workflow, and a notebook prototype.

## What this project does

- Loads a local repository or GitHub URL for analysis
- Validates dependencies and repository structure before analysis begins
- Produces debugging suggestions and HTML reports for review
- Provides a GUI dashboard for interactive use on Windows
- Supports an installable Python package and a packaged Windows executable
- Uses provider-backed LLM suggestions from OpenAI, Gemini, Anthropic, Groq, Grok, Mistral, OpenRouter, Azure OpenAI, and DeepSeek

## Quick start

### Option 1: Use the packaged Windows app

The workspace already contains a ready-to-share executable bundle:

- `dist/Autonomous Code Debugging Agent.exe`
- `Autonomous_Code_Debugging_Agent_Install.zip`

Extract the ZIP file and run the `.exe` directly. This is the simplest path for end users and matches the current desktop app model.

### Option 2: Install the Python package

```bash
python -m pip install -e .
```

After installation, launch the GUI from anywhere with:

```bash
autonomous-code-debugger
```

### Option 3: Run from the repository

```bash
python dashboard.py
```

## CLI usage

You can also invoke the analysis workflow from the command line:

```bash
python -m autonomous_code_debugging_agent.api.main --repo . --error "division by zero" --top-k 3 --report-dir reports
```

This runs the same repository-analysis path used by the dashboard and writes an HTML report into the `reports/` folder.

## Notebook usage

Open `Project_Autonomous_Code_Debugging_Agent.ipynb` and run the cells in order. The notebook imports the package from `src/autonomous_code_debugging_agent`.

## Windows launcher

If you prefer the helper script, you can still use:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_agent.ps1
```

You can override the defaults with:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_agent.ps1 -Repo . -ErrorMessage "division by zero" -TopK 3
```

## Current app model

The current working model of the app is:

- GUI dashboard for interactive analysis and report viewing
- Shared repository-analysis workflow used by both the GUI and CLI
- Notebook prototype for experimentation and iterative debugging loops

## Environment and keys

Set one or more of the following keys if you want provider-backed LLM suggestions:

- `OPENAI_API_KEY`
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- `ANTHROPIC_API_KEY`
- `GROQ_API_KEY`
- `GROK_API_KEY` or `XAI_API_KEY`
- `MISTRAL_API_KEY`
- `OPENROUTER_API_KEY`
- `DEEPSEEK_API_KEY`
- `AZURE_OPENAI_API_KEY`

The dashboard also supports entering a custom runtime key and saving it to `.env` for the selected provider.

## Notes

- The packaged desktop executable is intended for local Windows use.
- The notebook remains a useful interactive development entry point for prototyping and debugging loops.
- The installable package is defined in `pyproject.toml` with the console entry point `autonomous-code-debugger`.
- The current release model favors the desktop GUI first, with CLI and notebook support as complementary workflows.
