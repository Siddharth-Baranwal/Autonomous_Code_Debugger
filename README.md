# Autonomous Code Debugging Agent

A desktop-friendly repository analysis tool that inspects a project, validates dependencies, and produces debugging insights with a polished dashboard.

## What this project does

- Loads a repository and inspects its source files
- Validates dependencies before analysis begins
- Generates debugging suggestions and HTML reports
- Provides a GUI dashboard for local use
- Supports an installable Python package and a packaged Windows executable

## Quick start

### Option 1: Use the packaged Windows app

The workspace already contains a ready-to-share executable bundle:

- `dist/Autonomous Code Debugging Agent.exe`
- `Autonomous_Code_Debugging_Agent_Install.zip`

Extract the ZIP file and run the `.exe` directly. This is the simplest path for end users.

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
python -m autonomous_code_debugging_agent.api.main --repo . --error "division by zero" --top-k 3
```

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

## Environment and keys

- Set `OPENAI_API_KEY` or `GEMINI_API_KEY` if you want provider-backed LLM suggestions.
- The dashboard also supports entering a custom runtime LLM key and saving it to `.env`.
- The default embedding path is lightweight and does not require downloading a large model.

## Notes

- The packaged desktop executable is intended for local Windows use.
- The notebook remains a useful interactive development entry point.
- The installable package is defined in `pyproject.toml` with the console entry point `autonomous-code-debugger`.
