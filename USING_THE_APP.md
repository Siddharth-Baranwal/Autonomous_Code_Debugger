# Using the Autonomous Code Debugging Agent

This guide covers launching the installed app, analyzing a repository, and finding the generated report.

## Launch the app

### Windows standalone executable

1. Extract the Windows release ZIP, if you downloaded one.
2. Open `windows_setup/` and run `Autonomous Code Debugging Agent.exe`.
3. If Windows shows a security warning, only continue if you trust the source of the executable.

The standalone executable does not require a separate Python package installation.

### Python package

Use Python 3.10 or newer. From a terminal, create and activate a virtual environment, then install the wheel:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install "C:\path\to\autonomous_code_debugging_agent-0.1.0-py3-none-any.whl"
autonomous-code-debugger
```

On macOS or Linux, use the platform's Python 3 command and activate the environment with `source .venv/bin/activate`. If installing from a platform archive instead of a wheel, extract it, open a terminal in the folder containing `pyproject.toml`, and run `python3 -m pip install .`; then launch `autonomous-code-debugger`.

## Analyze a repository

1. In **Run Analysis**, choose **GitHub** and enter a reachable GitHub repository URL, or choose **Local** and enter the path to a repository folder on your computer.
2. Optionally configure a supported LLM provider as described below.
3. Select **Start Analysis** and follow the status, progress bar, and realtime log.
4. When analysis finishes, review the result in **HTML Report**. The report is also saved as an HTML file in a `reports/` folder under the app's current working directory; the log shows its path.

The dashboard performs a general repository review. To ask about a specific error or question, use the command line after installing the Python package:

```powershell
python -m autonomous_code_debugging_agent.api.main --repo "C:\path\to\repository" --error "Describe the error or question" --top-k 5 --report-dir reports
```

For a GitHub repository, use its URL as the `--repo` value. The command prints a JSON result and saves the HTML report in the directory given to `--report-dir`.

## Configure LLM suggestions

An API key is optional for repository retrieval and report generation. Without a configured provider key, the report will state that an LLM suggestion is unavailable. To enable suggestions, choose a provider in the dashboard, enter its API key, and select **Save custom key**. Supported providers are OpenAI, Gemini, Anthropic, Groq, Grok, Mistral, OpenRouter, Azure OpenAI, and DeepSeek. The provider account may require billing or have usage limits.

Treat API keys as secrets. The app applies the key for the current run and saves it to a local `.env` configuration file for future runs. Do not share that file or commit it to a repository.

When a provider key is configured, relevant repository code context is sent to that provider to generate suggestions. Only analyze repositories whose contents you are permitted to share with the selected provider.

## Reset and troubleshoot

- **Reset** clears the current dashboard status, log, and report preview. It does not delete previously saved report files.
- If a local repository is rejected, verify that the entered path exists and points to the repository folder.
- If a GitHub repository cannot be loaded, verify the URL and that the repository is reachable from your machine.
- If the report has no LLM suggestion, configure a valid provider key and check that the machine can reach that provider's API.
- If analysis fails during dependency validation, check the repository's dependency files and the error shown in the realtime log.
