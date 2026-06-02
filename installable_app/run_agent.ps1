param(
    [string]$Repo = ".",
    [string]$ErrorMessage = "division by zero",
    [int]$TopK = 3
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:PYTHONPATH = Join-Path $scriptDir "src"

if (Get-Command uv -ErrorAction SilentlyContinue) {
    uv run python -m autonomous_code_debugging_agent.api.main --repo $Repo --error $ErrorMessage --top-k $TopK
    return
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python is not available on PATH. Install Python, or run the notebook directly."
}

python -m autonomous_code_debugging_agent.api.main --repo $Repo --error $ErrorMessage --top-k $TopK
