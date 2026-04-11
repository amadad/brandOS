from __future__ import annotations

import sys
from typing import Any

import typer
import yaml
from pydantic import BaseModel
from rich.console import Console
from rich.pretty import Pretty

from brand_os._agent_cli import emit_json

console = Console()


def _derive_command() -> str:
    """Derive a "group subcommand" string from sys.argv, skipping flags.

    Falls back to "<unknown>" when the argv shape is unexpected (e.g. running
    under a test harness). Keeps call sites untouched while still producing a
    useful `command` field in the canonical {status, command, data} envelope.
    """
    argv = sys.argv[1:] if len(sys.argv) > 1 else []
    parts: list[str] = []
    for tok in argv:
        if tok.startswith("-"):
            # Stop at the first flag — everything before is "group subcommand",
            # everything after is flags/values we don't want in the command key.
            break
        parts.append(tok)
    return " ".join(parts) if parts else "<unknown>"


def emit(data: Any, format: str = "json", *, command: str | None = None) -> None:
    """Emit `data` in the requested format.

    When `format == "json"`, wraps the payload in the canonical
    `{status, command, data}` envelope (see ~/agents/_rules/general/cli.md rule
    3) via `emit_json`. `command` is optional — when omitted, it's derived from
    `sys.argv` so existing call sites don't need to thread it through.
    """
    normalized = _normalize(data)
    if format == "json":
        emit_json(
            status="ok",
            command=command or _derive_command(),
            data=normalized,
        )
        return
    if format == "yaml":
        typer.echo(yaml.safe_dump(normalized, sort_keys=False))
        return

    console.print(Pretty(normalized))


def _normalize(data: Any) -> Any:
    if isinstance(data, BaseModel):
        return data.model_dump()
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        return [_normalize(item) for item in data]
    if hasattr(data, "model_dump"):
        return data.model_dump()
    return data


def parse_fields(fields: str | None) -> list[str] | None:
    """Parse a comma-separated --fields value into a list of field names."""
    if not fields:
        return None
    return [f.strip() for f in fields.split(",") if f.strip()]


def project_fields(data: Any, fields: list[str] | None) -> Any:
    """Project `data` down to only the requested fields.

    Works on a single dict/model or a list of dicts/models. When `fields` is
    None, returns the normalized data unchanged. Unknown fields are silently
    skipped so a caller can safely pass a shared default projection.
    """
    if fields is None:
        return _normalize(data)

    if isinstance(data, list):
        return [_project_one(item, fields) for item in data]
    return _project_one(data, fields)


def _project_one(item: Any, fields: list[str]) -> dict[str, Any]:
    normalized = _normalize(item)
    if not isinstance(normalized, dict):
        return normalized  # can't project a scalar
    return {k: normalized[k] for k in fields if k in normalized}
