# Autonomous Code Debugging Agent

A desktop-friendly repository analysis tool that inspects a project, validates dependencies, and generates debugging insights through a polished Tkinter dashboard, a CLI workflow, and a notebook prototype.

## What this project does

- Loads a local repository or GitHub URL for analysis
- Validates dependencies and repository structure before analysis begins
- Produces debugging suggestions and HTML reports for review
- Provides a GUI dashboard for interactive use on Windows
- Supports an installable Python package, a packaged Windows executable, and source ZIP packaging helpers
- Uses provider-backed LLM suggestions from OpenAI, Gemini, Anthropic, Groq, Grok, Mistral, OpenRouter, Azure OpenAI, and DeepSeek

## Quick start

### Option 1: Use the Windows executable in this folder

This folder contains the current Windows desktop executable:

- `Autonomous Code Debugging Agent.exe`

Run the executable directly for the packaged Windows app experience.

### Option 2: Install the companion Python package

From the repository root or `installable_app/`, install the wheel or package:

```bash
python -m pip install installable_app/dist/autonomous_code_debugging_agent-0.1.0-py3-none-any.whl
```

Or install the repository in editable mode:

```bash
cd installable_app
python -m pip install -e .
```

Then launch:

```bash
autonomous-code-debugger
```

### Option 3: Run from the repository root

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

You can also use the helper notebook `create_source_zip.ipynb` to recreate the source archive in a notebook-friendly workflow.

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
- Packaging helpers for source ZIP generation and desktop distribution

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
- The current release model favors the desktop GUI first, with CLI, notebook, and packaging helpers as complementary workflows.
- Utility scripts such as `create_source_zip.py` help create a cleaner handoff archive without build or cache folders.
