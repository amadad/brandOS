from __future__ import annotations

import json
from typing import Any

import typer
import yaml
from pydantic import BaseModel
from rich.console import Console
from rich.pretty import Pretty

console = Console()


def emit(data: Any, format: str = "json") -> None:
    normalized = _normalize(data)
    if format == "json":
        console.print_json(json.dumps(normalized, indent=2))
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
