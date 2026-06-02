from __future__ import annotations

import os
import queue
import threading
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from tkinterweb import HtmlFrame


DARK_BG = "#0b1120"
DARK_PANEL = "#111827"
DARK_CARD = "#111827"
DARK_INPUT = "#0f172a"
DARK_ACCENT = "#38bdf8"
DARK_ACCENT_STRONG = "#0ea5e9"
DARK_BORDER = "#1e293b"
DARK_TEXT = "#e2e8f0"
DARK_MUTED = "#94a3b8"
DARK_SUCCESS = "#34d399"
DARK_WARNING = "#f59e0b"
DARK_DANGER = "#f87171"
DARK_HOVER = "#162032"

SUPPORTED_LLM_PROVIDERS = [
    "OpenAI",
    "Gemini",
    "Anthropic",
    "Groq",
    "Grok",
    "Mistral",
    "OpenRouter",
    "Azure OpenAI",
    "DeepSeek",
]

PROVIDER_ENV_VARS = {
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "groq": "GROQ_API_KEY",
    "grok": "GROK_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "azure openai": "AZURE_OPENAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}

PROVIDER_DISPLAY_NAMES = {
    "openai": "OpenAI",
    "gemini": "Gemini",
    "anthropic": "Anthropic",
    "groq": "Groq",
    "grok": "Grok",
    "mistral": "Mistral",
    "openrouter": "OpenRouter",
    "azure openai": "Azure OpenAI",
    "deepseek": "DeepSeek",
}


# Run the normalize provider name logic used by this module.
def _normalize_provider_name(provider: str) -> str:
    # Normalize provider names so aliases like 'Azure' and 'Grok AI' map to the same backend.
    normalized = provider.strip().lower().replace("_", " ")
    aliases = {
        "google gemini": "gemini",
        "azure": "azure openai",
        "azureopenai": "azure openai",
        "openrouter.ai": "openrouter",
        "open router": "openrouter",
        "xai": "grok",
        "grok ai": "grok",
        "grokapi": "grok",
    }
    return aliases.get(normalized, normalized)


# Resolve the input into the repository path or source that the code needs.
def resolve_repository_source(source_type: str, repo_input: str) -> str:
    # Verify whether the user supplied a valid local path or a GitHub repository URL.
    value = repo_input.strip()

    if not value:
        if source_type == "GitHub":
            raise ValueError("Please enter a GitHub repository link.")
        raise ValueError("Please enter a local repository path.")

    if source_type == "GitHub":
        if not value.startswith(("http://", "https://")) or "github.com/" not in value:
            raise ValueError("Please enter a valid GitHub repository URL, for example https://github.com/owner/repo.")
        return value.rstrip("/")

    if source_type == "Local":
        path = Path(value).expanduser()
        if not path.exists():
            raise ValueError("The selected local path does not exist. Please choose an existing repository folder.")
        return str(path)

    raise ValueError(f"Unknown repository source type: {source_type}")


# Apply the runtime setting or key to the current session.
def apply_runtime_llm_key(provider: str, api_key: str) -> str:
    # Apply the chosen API key to the current shell session for immediate use.
    provider = _normalize_provider_name(provider)
    key = api_key.strip()

    if not key:
        raise ValueError("Please enter an API key before saving.")

    if provider not in PROVIDER_ENV_VARS:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    for env_name in set(PROVIDER_ENV_VARS.values()):
        if env_name != PROVIDER_ENV_VARS[provider]:
            os.environ.pop(env_name, None)

    os.environ[PROVIDER_ENV_VARS[provider]] = key
    return f"Custom {PROVIDER_DISPLAY_NAMES[provider]} key applied for this session."


# Persist the user setting or key to the project configuration.
def persist_llm_key_to_env(provider: str, api_key: str, env_path: Path | None = None) -> str:
    # Save the selected API key to the project .env file for later runs.
    provider = _normalize_provider_name(provider)
    key = api_key.strip()

    if not key:
        raise ValueError("Please enter an API key before saving.")

    if provider not in PROVIDER_ENV_VARS:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    target_path = env_path or Path(__file__).resolve().parents[3] / ".env"
    target_path.parent.mkdir(parents=True, exist_ok=True)

    existing_lines = []
    if target_path.exists():
        existing_lines = target_path.read_text(encoding="utf-8").splitlines()

    preserved_lines = []
    for line in existing_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            preserved_lines.append(line)
            continue

        key_name = stripped.split("=", 1)[0]
        if key_name in set(PROVIDER_ENV_VARS.values()) or key_name == "GOOGLE_API_KEY":
            continue
        preserved_lines.append(line)

    target_variable = PROVIDER_ENV_VARS[provider]
    persisted_lines = preserved_lines + [f"{target_variable}={key}"]
    target_path.write_text("\n".join(persisted_lines) + "\n", encoding="utf-8")

    return f"Custom {PROVIDER_DISPLAY_NAMES[provider]} key saved to .env."


class DebuggingDashboardApp:
    # Run the init   logic used by this module.
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Autonomous Code Debugging Agent Dashboard")
        self.root.geometry("1200x760")
        self.root.minsize(1024, 700)
        self.root.configure(bg=DARK_BG)
        self.root.option_add("*TCombobox*Listbox.background", DARK_INPUT)
        self.root.option_add("*TCombobox*Listbox.foreground", DARK_TEXT)
        self.root.option_add("*TCombobox*Listbox.selectBackground", DARK_ACCENT)
        self.root.option_add("*TCombobox*Listbox.selectForeground", DARK_BG)

        self.event_queue: queue.Queue[tuple[str, object]] = queue.Queue()
        self.current_report_path: Path | None = None
        self.analysis_thread: threading.Thread | None = None
        self.badge_state = "ready"

        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self._apply_theme()

        self._build_top_bar()

        self.notebook = ttk.Notebook(self.root, style="Dark.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.llm_provider_var = tk.StringVar(value="OpenAI")
        self.llm_key_status_var = tk.StringVar(value="Using existing environment variables by default.")

        self._build_run_tab()
        self._build_report_tab()
        self._setup_status_badge()

        self.root.after(120, self._process_queue)

    # Run the apply theme logic used by this module.
    def _apply_theme(self) -> None:
        style = self.style
        style.configure("TFrame", background=DARK_BG)
        style.configure("Dark.TFrame", background=DARK_BG)
        style.configure("Dark.TLabel", background=DARK_BG, foreground=DARK_TEXT)
        style.configure("Dark.TLabel.Muted", background=DARK_BG, foreground=DARK_MUTED)
        style.configure("Dark.TNotebook", background=DARK_BG, borderwidth=0, tabmargins=(0, 0, 0, 0))
        style.configure(
            "Dark.TNotebook.Tab",
            background=DARK_PANEL,
            foreground=DARK_MUTED,
            padding=(18, 10),
            borderwidth=0,
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Dark.TNotebook.Tab",
            background=[("selected", DARK_ACCENT), ("active", DARK_HOVER)],
            foreground=[("selected", DARK_BG), ("active", DARK_TEXT)],
        )

        style.configure(
            "Dark.TButton",
            background=DARK_PANEL,
            foreground=DARK_TEXT,
            borderwidth=1,
            relief="flat",
            padding=(16, 8),
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Dark.TButton",
            background=[("active", DARK_HOVER), ("pressed", DARK_ACCENT_STRONG), ("disabled", DARK_PANEL)],
            foreground=[("disabled", DARK_MUTED)],
            bordercolor=[("active", DARK_ACCENT), ("pressed", DARK_ACCENT_STRONG)],
        )

        style.configure(
            "Dark.TCombobox",
            fieldbackground=DARK_INPUT,
            background=DARK_INPUT,
            foreground=DARK_TEXT,
            bordercolor=DARK_BORDER,
            arrowsize=16,
            padding=8,
        )
        style.map(
            "Dark.TCombobox",
            fieldbackground=[("readonly", DARK_INPUT), ("disabled", DARK_INPUT)],
            foreground=[("readonly", DARK_TEXT), ("disabled", DARK_MUTED)],
        )

        style.configure(
            "Dark.TEntry",
            fieldbackground=DARK_INPUT,
            foreground=DARK_TEXT,
            bordercolor=DARK_BORDER,
            lightcolor=DARK_BORDER,
            darkcolor=DARK_BORDER,
            padding=8,
            font=("Segoe UI", 10),
        )

        style.configure(
            "Dark.Horizontal.TProgressbar",
            troughcolor=DARK_INPUT,
            background=DARK_SUCCESS,
            bordercolor=DARK_BORDER,
            lightcolor=DARK_SUCCESS,
            darkcolor=DARK_SUCCESS,
            thickness=18,
        )

        style.configure(
            "Dark.TLabelFrame",
            background=DARK_BG,
            foreground=DARK_TEXT,
            bordercolor=DARK_BORDER,
        )

        style.configure("Dark.TSeparator", background=DARK_BORDER)

    # Run the build top bar logic used by this module.
    def _build_top_bar(self) -> None:
        # Draw the top branding bar for the desktop dashboard.
        top_bar = tk.Frame(self.root, bg=DARK_BG)
        top_bar.pack(fill="x", padx=18, pady=(18, 6))

        title = tk.Label(
            top_bar,
            text="Autonomous Code Debugging Agent",
            bg=DARK_BG,
            fg=DARK_TEXT,
            font=("Segoe UI", 18, "bold"),
            anchor="w",
        )
        title.pack(side="left")

        subtitle = tk.Label(
            top_bar,
            text="Repository health, dependency validation, and HTML reporting in one dark-panel workspace.",
            bg=DARK_BG,
            fg=DARK_MUTED,
            font=("Segoe UI", 10),
            anchor="w",
        )
        subtitle.pack(side="left", padx=(14, 0))

    # Run the build run tab logic used by this module.
    def _build_run_tab(self) -> None:
        # Build the main analysis tab with repo input, status, and logging UI.
        frame = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(frame, text="Run Analysis")

        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(3, weight=1)

        header = ttk.Frame(frame, style="Dark.TFrame")
        header.grid(row=0, column=0, columnspan=2, padx=18, pady=(18, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        header_title = ttk.Label(header, text="Repository analysis workflow", style="Dark.TLabel")
        header_title.grid(row=0, column=0, sticky="w")
        header_title.configure(font=("Segoe UI", 14, "bold"))

        header_subtitle = tk.Label(
            header,
            text="Choose a source, inspect the realtime status, and load the generated HTML summary.",
            bg=DARK_BG,
            fg=DARK_MUTED,
            font=("Segoe UI", 10),
            anchor="w",
        )
        header_subtitle.grid(row=1, column=0, sticky="w", pady=(4, 0))

        form_card = ttk.Frame(frame, style="Dark.TFrame")
        form_card.grid(row=1, column=0, columnspan=2, padx=18, pady=(16, 8), sticky="ew")
        form_card.grid_columnconfigure(1, weight=1)

        ttk.Label(form_card, text="Repository source:", style="Dark.TLabel").grid(
            row=0, column=0, padx=0, pady=(8, 8), sticky="w"
        )
        self.source_type_var = tk.StringVar(value="GitHub")
        self.source_type_combo = ttk.Combobox(
            form_card,
            textvariable=self.source_type_var,
            values=["GitHub", "Local"],
            state="readonly",
            width=18,
            style="Dark.TCombobox",
        )
        self.source_type_combo.grid(row=0, column=1, padx=0, pady=(8, 8), sticky="ew")
        self.source_type_combo.bind("<<ComboboxSelected>>", lambda _event: self._sync_repository_input())

        self.repo_label = ttk.Label(form_card, text="Repository link:", style="Dark.TLabel")
        self.repo_label.grid(row=1, column=0, padx=0, pady=(0, 8), sticky="w")
        self.repo_entry = ttk.Entry(form_card, width=120, style="Dark.TEntry")
        self.repo_entry.insert(0, "https://github.com/owner/repo")
        self.repo_entry.grid(row=1, column=1, padx=0, pady=(0, 8), sticky="ew")

        self.hint_label = tk.Label(
            form_card,
            text="Example: https://github.com/owner/repo",
            bg=DARK_BG,
            fg=DARK_MUTED,
            font=("Segoe UI", 10),
            anchor="w",
        )
        self.hint_label.grid(row=2, column=1, padx=0, pady=(0, 10), sticky="w")

        status_row = ttk.Frame(form_card, style="Dark.TFrame")
        status_row.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(6, 10))
        status_row.grid_columnconfigure(1, weight=1)

        ttk.Label(status_row, text="Analysis status:", style="Dark.TLabel").grid(row=0, column=0, sticky="w")
        self.status_var = tk.StringVar(value="Ready. Choose a repository source and start the analysis.")
        self.status_label = ttk.Label(status_row, textvariable=self.status_var, style="Dark.TLabel")
        self.status_label.grid(row=0, column=1, padx=(12, 0), sticky="w")

        ttk.Label(status_row, text="Progress:", style="Dark.TLabel").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.progress = ttk.Progressbar(status_row, mode="determinate", maximum=100, value=0, style="Dark.Horizontal.TProgressbar")
        self.progress.grid(row=1, column=1, padx=(12, 0), pady=(10, 0), sticky="ew")

        button_row = ttk.Frame(form_card, style="Dark.TFrame")
        button_row.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(8, 8))
        self.run_button = ttk.Button(button_row, text="Start Analysis", command=self.start_analysis, style="Dark.TButton")
        self.run_button.pack(side="left")
        ttk.Button(button_row, text="Reset", command=self.reset_view, style="Dark.TButton").pack(side="left", padx=10)

        llm_card = tk.Frame(frame, bg=DARK_PANEL, highlightbackground=DARK_BORDER, highlightthickness=1)
        llm_card.grid(row=2, column=0, columnspan=2, padx=18, pady=(8, 8), sticky="ew")
        llm_card.grid_columnconfigure(1, weight=1)

        ttk.Label(llm_card, text="Custom LLM key (optional):", style="Dark.TLabel").grid(row=0, column=0, padx=14, pady=(14, 8), sticky="w")
        ttk.Label(llm_card, text="Provider:", style="Dark.TLabel").grid(row=1, column=0, padx=14, pady=(0, 8), sticky="w")
        self.llm_provider_combo = ttk.Combobox(
            llm_card,
            textvariable=self.llm_provider_var,
            values=SUPPORTED_LLM_PROVIDERS,
            state="readonly",
            width=18,
            style="Dark.TCombobox",
        )
        self.llm_provider_combo.grid(row=1, column=1, padx=(0, 14), pady=(0, 8), sticky="ew")

        ttk.Label(llm_card, text="API key:", style="Dark.TLabel").grid(row=2, column=0, padx=14, pady=(0, 8), sticky="w")
        self.llm_key_entry = ttk.Entry(llm_card, width=80, style="Dark.TEntry", show="•")
        self.llm_key_entry.grid(row=2, column=1, padx=(0, 14), pady=(0, 8), sticky="ew")

        button_row_llm = ttk.Frame(llm_card, style="Dark.TFrame")
        button_row_llm.grid(row=3, column=0, columnspan=2, padx=14, pady=(0, 14), sticky="w")
        ttk.Button(button_row_llm, text="Save custom key", command=self._save_custom_llm_key, style="Dark.TButton").pack(side="left")

        status_label = ttk.Label(llm_card, textvariable=self.llm_key_status_var, style="Dark.TLabel")
        status_label.grid(row=4, column=0, columnspan=2, padx=14, pady=(0, 14), sticky="w")

        log_frame = tk.Frame(frame, bg=DARK_PANEL, highlightbackground=DARK_BORDER, highlightthickness=1)
        log_frame.grid(row=3, column=0, columnspan=2, padx=18, pady=(8, 12), sticky="nsew")
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        ttk.Label(log_frame, text="Realtime analysis log:", style="Dark.TLabel").grid(row=0, column=0, padx=14, pady=(12, 6), sticky="w")
        self.log = scrolledtext.ScrolledText(
            log_frame,
            wrap="word",
            bg=DARK_INPUT,
            fg=DARK_TEXT,
            insertbackground=DARK_TEXT,
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            padx=14,
            pady=14,
            font=("Segoe UI", 10),
        )
        self.log.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self.log.configure(state="disabled")

        self._sync_repository_input()

    # Run the setup status badge logic used by this module.
    def _setup_status_badge(self) -> None:
        # Create the small status badge shown in the top-right corner.
        self.status_badge = tk.Label(
            self.root,
            text="Ready",
            bg=DARK_SUCCESS,
            fg=DARK_BG,
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=5,
            relief="flat",
            highlightbackground=DARK_BORDER,
            highlightthickness=1,
        )
        self.status_badge.place(relx=1.0, rely=0.0, anchor="ne", x=-22, y=12)

    # Run the build report tab logic used by this module.
    def _build_report_tab(self) -> None:
        # Build the HTML report preview tab used to show generated analysis output.
        frame = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(frame, text="HTML Report")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        header = ttk.Frame(frame, style="Dark.TFrame")
        header.grid(row=0, column=0, padx=18, pady=(18, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ttk.Label(header, text="Generated report preview", style="Dark.TLabel").grid(row=0, column=0, sticky="w")
        tk.Label(
            header,
            text="The current HTML summary is rendered directly in the dashboard.",
            bg=DARK_BG,
            fg=DARK_MUTED,
            font=("Segoe UI", 10),
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        report_container = tk.Frame(frame, bg=DARK_PANEL, highlightbackground=DARK_BORDER, highlightthickness=1)
        report_container.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="nsew")
        report_container.grid_rowconfigure(0, weight=1)
        report_container.grid_columnconfigure(0, weight=1)

        self.report_frame = HtmlFrame(report_container)
        self.report_frame.grid(row=0, column=0, sticky="nsew")
        self.report_frame.load_html(
            "<html><body style='background:#0b1120;color:#e2e8f0;font-family:Segoe UI,Arial,sans-serif;padding:24px;'><h2>HTML Report Preview</h2><p>The generated HTML summary will appear here after analysis or when a saved report is loaded.</p></body></html>"
        )

    # Run the sync repository input logic used by this module.
    def _sync_repository_input(self) -> None:
        source_type = self.source_type_var.get()
        if source_type == "GitHub":
            self.repo_label.configure(text="Repository link:")
            self.hint_label.configure(text="Example: https://github.com/owner/repo")
            current_value = self.repo_entry.get().strip()
            if not current_value or current_value == ".":
                self.repo_entry.delete(0, tk.END)
                self.repo_entry.insert(0, "https://github.com/owner/repo")
            return

        self.repo_label.configure(text="Local repository path:")
        self.hint_label.configure(text="Example: C:/path/to/repo or .")
        current_value = self.repo_entry.get().strip()
        if not current_value or current_value.startswith("https://"):
            self.repo_entry.delete(0, tk.END)
            self.repo_entry.insert(0, ".")

    # Run the append log logic used by this module.
    def _append_log(self, message: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", f"{message}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    # Run the update status badge logic used by this module.
    def _update_status_badge(self, state: str) -> None:
        mapping = {
            "ready": ("Ready", DARK_SUCCESS),
            "running": ("Analyzing", DARK_WARNING),
            "complete": ("Complete", DARK_SUCCESS),
            "error": ("Error", DARK_DANGER),
        }
        label, color = mapping.get(state, ("Ready", DARK_SUCCESS))
        self.badge_state = state
        self.status_badge.configure(text=label, bg=color)

    # Run the save custom llm key logic used by this module.
    def _save_custom_llm_key(self) -> None:
        try:
            provider = self.llm_provider_var.get()
            api_key = self.llm_key_entry.get()
            persist_message = persist_llm_key_to_env(provider, api_key)
            runtime_message = apply_runtime_llm_key(provider, api_key)
            message = f"{persist_message} {runtime_message}"
            self.llm_key_status_var.set(message)
            self._append_log(message)
            self.llm_key_entry.delete(0, tk.END)
        except ValueError as exc:
            self.llm_key_status_var.set(str(exc))
            messagebox.showwarning("Invalid LLM key", str(exc))

    # Run the apply status from text logic used by this module.
    def _apply_status_from_text(self, status_text: str) -> None:
        lowered = status_text.lower()
        if "error" in lowered or "failed" in lowered:
            self._update_status_badge("error")
            return
        if "complete" in lowered:
            self._update_status_badge("complete")
            return
        if "preparing" in lowered or "validating" in lowered or "loading" in lowered or "rendering" in lowered:
            self._update_status_badge("running")
            return
        if self.badge_state == "error":
            return
        self._update_status_badge("running")

    # Run the load existing report if available logic used by this module.
    def _load_existing_report_if_available(self, repo_source: str) -> bool:
        from ..reporting.html_reporter import HTMLReportGenerator

        report_path = HTMLReportGenerator().get_output_path(repo_source, output_dir=Path("reports"))
        if not report_path.exists():
            return False

        self.current_report_path = report_path
        self.progress.configure(value=100)
        self.status_var.set("Existing report found. Loading HTML report.")
        self._update_status_badge("complete")
        self._append_log(f"Using existing report: {report_path}")
        self.report_frame.load_html(report_path.read_text(encoding="utf-8"))
        self.notebook.select(self.notebook.tabs()[1])
        self.run_button.state(["!disabled"])
        return True

    # Run the reset view logic used by this module.
    def reset_view(self) -> None:
        self.progress.configure(value=0)
        self.status_var.set("Ready. Choose a repository source and start the analysis.")
        self._update_status_badge("ready")
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self.report_frame.load_html(
            "<html><body style='background:#0b1120;color:#e2e8f0;font-family:Segoe UI,Arial,sans-serif;padding:24px;'><h2>HTML Report Preview</h2><p>The generated HTML summary will appear here after analysis or when a saved report is loaded.</p></body></html>"
        )
        self.current_report_path = None
        self.run_button.state(["!disabled"])
        self._sync_repository_input()

    # Run the start analysis logic used by this module.
    def start_analysis(self) -> None:
        source_type = self.source_type_var.get()
        try:
            repo_source = resolve_repository_source(source_type, self.repo_entry.get())
        except ValueError as exc:
            messagebox.showwarning("Invalid repository input", str(exc))
            return

        if self._load_existing_report_if_available(repo_source):
            return

        self.run_button.state(["disabled"])
        self.progress.configure(value=0)
        self.status_var.set("Preparing analysis...")
        self._update_status_badge("running")
        self._append_log(f"Starting analysis for: {repo_source}")

        self.analysis_thread = threading.Thread(
            target=self._run_analysis,
            args=(repo_source,),
            daemon=True,
        )
        self.analysis_thread.start()

    # Run the run analysis logic used by this module.
    def _run_analysis(self, repo_source: str) -> None:
        # Execute the analysis pipeline in a background thread and emit progress events.
        try:
            from ..workflows.debugging_loop import analyze_repository_with_html_report

            self.event_queue.put(("status", "Validating repository input..."))
            self.event_queue.put(("progress", 10))
            self.event_queue.put(("log", f"Repository input received: {repo_source}"))

            self.event_queue.put(("status", "Loading repository snapshot..."))
            self.event_queue.put(("progress", 25))

            default_error = (
                "Analyze this repository and identify the most likely failure points, bugs, or misconfigurations "
                "based on its code and documentation."
            )

            report = analyze_repository_with_html_report(
                repo_source,
                default_error,
                top_k=5,
                output_dir=Path("reports"),
            )

            report_path = Path(report["report_path"])
            self.current_report_path = report_path
            self.event_queue.put(("status", "Rendering HTML report..."))
            self.event_queue.put(("progress", 90))
            self.event_queue.put(("log", f"HTML report generated at: {report_path}"))
            self.event_queue.put(("report_path", str(report_path)))
            self.event_queue.put(("status", "Analysis complete. Report is ready to review."))
            self.event_queue.put(("progress", 100))
        except Exception as exc:
            self.event_queue.put(("error", str(exc)))

    # Run the process queue logic used by this module.
    def _process_queue(self) -> None:
        # Handle queued UI updates from the background analysis thread.
        try:
            while True:
                event_type, payload = self.event_queue.get_nowait()

                if event_type == "status":
                    status_text = str(payload)
                    self.status_var.set(status_text)
                    self._apply_status_from_text(status_text)
                elif event_type == "progress":
                    self.progress.configure(value=int(payload))
                elif event_type == "log":
                    self._append_log(str(payload))
                elif event_type == "report_path":
                    report_path = Path(payload)
                    if report_path.exists():
                        html_content = report_path.read_text(encoding="utf-8")
                        self.report_frame.load_html(html_content)
                        self._append_log("HTML report tab has been refreshed.")
                        self._update_status_badge("complete")
                elif event_type == "error":
                    messagebox.showerror("Analysis failed", str(payload))
                    self.status_var.set(f"Analysis failed: {payload}")
                    self._update_status_badge("error")
                    self.run_button.state(["!disabled"])
                else:
                    continue
        except queue.Empty:
            pass

        if self.analysis_thread is not None and self.analysis_thread.is_alive():
            self.root.after(120, self._process_queue)
            return

        self.analysis_thread = None
        self.run_button.state(["!disabled"])


# Run the main logic used by this module.
def main() -> None:
    root = tk.Tk()
    app = DebuggingDashboardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
