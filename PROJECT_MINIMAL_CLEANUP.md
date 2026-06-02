# Project Cleanup Notes

## Goal
Identify workspace files/components that are not necessary to satisfy a professional execution of the project, while preserving the runtime application, key utilities, and core documentation.

## Minimal Professional Execution Set
These are the files and folders that should remain for a clean, professional project deliverable:
- `src/` and all runtime package code under `src/autonomous_code_debugging_agent/`
- `dashboard.py` for launching the desktop UI
- `generate_html_reports.py` for report generation utility
- `flowchart_fullscreen.html` as a polished visualization asset
- `README.md`, `PROJECT_FILE_REFERENCE.md`, `PROJECT_EXPLANATION.md` for documentation
- `pyproject.toml` and/or `requirements.txt` for dependency management
- `run_agent.ps1` for Windows launch convenience
- `LICENSE`
- `tests/` (optional, but useful for professional validation)

## Files/Components Not Necessary for Professional Run-Time Execution
These files are typically not needed in a polished production release:

### Generated / Build Artifacts
- `build/`
- `dist/`
- `Autonomous_Code_Debugging_Agent_Install.zip`
- `Autonomous_Code_Debugging_Agent_Source.zip`
- `build.log`
- `Autonomous Code Debugging Agent.spec`
- `uv.lock`

### Local Development / Environment Artifacts
- `.cache/`
- `.pytest_cache/`
- `__pycache__/`
- `.venv/`
- `.env` (should be excluded from distribution if it contains secrets)
- `env_vars.txt`

### Prototypes / Notes / Search Logs
- `Project_Autonomous_Code_Debugging_Agent.docx`
- `Project_Structure.docx`
- `create_source_zip.ipynb`
- `Project_Autonomous_Code_Debugging_Agent.ipynb`
- `gh_search.txt`
- `git_search.txt`
- `tool_search.txt`
- `generated_repos/` (if it contains temporary analysis data)

### Repository Metadata (not required for runtime)
- `.git/` (required for repository management, but not for runtime deployment)
- `.gitignore` (useful for repo hygiene, but not necessary to run the app)

## Notes
- `tests/` are not strictly required for execution, but they are valuable for verifying professional quality.
- `PROJECT_101_GUIDE.md` is developer-facing documentation; it can remain if you want a full package of docs, but it is not required for runtime.
- `CONTRIBUTING.md` is useful for open-source or team collaboration, but not required to execute the app.
- `installable_app/dist/` can be kept if you want a built wheel artifact for easy installation, but it is not required in the source-only runtime package.

## Recommendation
For the cleanest professional package, keep only the runtime code, essential docs, dependency files, and a small set of well-maintained utility scripts. Remove or archive generated artifacts, environment caches, prototypes, and temporary search logs.

## Verified Release Folders
The following verified folders have been created in this workspace:
- `professional_execution/` — contains the minimal runtime code, docs, and launch helpers needed for a polished release.
- `installable_app/` — contains the same package structure plus a Windows executable copy in `installable_app/windows_executable/` and a source package ready for pip-based installation.
- `windows_setup/` — contains the single-click Windows executable installable file alongside the general README.
- `macos_setup/` — contains a macOS-ready source archive (`Autonomous_Code_Debugging_Agent_mac.tar.gz`) and install guidance.
- `linux_setup/` — contains a Linux-ready source archive (`Autonomous_Code_Debugging_Agent_linux.tar.gz`) and install guidance.
