# Installable App Package

This folder contains the installable version of the project.

## Windows Executable
The Windows executable is available at:

- `windows_executable/Autonomous Code Debugging Agent.exe`

Double-click the `.exe` file to run the packaged desktop application.

## Python Package Installation
The source package is also available here for pip-based installation.

From this folder, install the package with:

```bash
python -m pip install .
```

Or install directly from the built wheel artifact:

```bash
python -m pip install dist/autonomous_code_debugging_agent-0.1.0-py3-none-any.whl
```

Once installed, launch the GUI with:

```bash
autonomous-code-debugger
```

## Notes
- This folder supports both a ready-to-run Windows app and a Python package installation path.
- A wheel file has been built into `dist/` for easy installation on other environments.
- For the cleanest OS-neutral installable setup, use the `pyproject.toml` and install with pip on your target system.
