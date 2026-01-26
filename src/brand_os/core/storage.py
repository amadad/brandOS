from __future__ import annotations

import os
from pathlib import Path


def data_dir() -> Path:
    root = os.getenv("BRANDOS_DATA_DIR", "~/.brand-os")
    path = Path(root).expanduser()
    path.mkdir(parents=True, exist_ok=True)
    return path


def output_dir() -> Path:
    path = data_dir() / "outputs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def identities_dir() -> Path:
    path = data_dir() / "identities"
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def resolve_output_path(filename: str, directory: Path | None = None) -> Path:
    base = directory or output_dir()
    return base / filename
