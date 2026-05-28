from __future__ import annotations

import os
from pathlib import Path


def get_settings(env_path: str | Path = ".env") -> dict[str, str]:
    settings = dict(os.environ)
    env_file = Path(env_path)
    if not env_file.exists():
        return settings

    for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        settings.setdefault(key.strip(), value.strip().strip('"').strip("'"))

    return settings
