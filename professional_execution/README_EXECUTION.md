# Professional Execution Package

This folder contains the minimal runtime release for the Autonomous Code Debugging Agent.

## Contents
- `pyproject.toml` and `requirements.txt` for dependency management
- `dashboard.py` for launching the desktop UI
- `generate_html_reports.py` for report generation
- `flowchart_fullscreen.html` for the polished visualization asset
- `run_agent.ps1` for Windows launcher convenience
- `src/autonomous_code_debugging_agent/` for the packaged application code

## Run locally
Install dependencies and run the dashboard:

```bash
python -m pip install -r requirements.txt
python dashboard.py
```

## Install as a package
For a reusable installable package, use:

```bash
python -m pip install -e .
```

Then launch the app from any terminal with:

```bash
autonomous-code-debugger
```
