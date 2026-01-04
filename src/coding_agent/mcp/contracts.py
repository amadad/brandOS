"""Pydantic contracts for key MCP tools used by the coding agent."""

from __future__ import annotations

import re
from typing import Iterable, List, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Windows drive letter pattern (e.g., C:, D:\)
_WINDOWS_DRIVE_PATTERN = re.compile(r"^[a-zA-Z]:[/\\]?")
# UNC path pattern (e.g., \\server\share)
_UNC_PATH_PATTERN = re.compile(r"^[/\\]{2}")


def _validate_relative_path(path: str) -> str:
    if not path:
        raise ValueError("path must not be empty")
    # Block Windows drive letters (C:\, D:/, etc.)
    if _WINDOWS_DRIVE_PATTERN.match(path):
        raise ValueError("path must be relative (Windows drive letter detected)")
    # Block UNC paths (\\server\share)
    if _UNC_PATH_PATTERN.match(path):
        raise ValueError("path must be relative (UNC path detected)")
    normalized = path.replace("\\", "/")
    if normalized.startswith("/"):
        raise ValueError("path must be relative")
    parts = normalized.split("/")
    if any(part in {"..", ""} for part in parts):
        raise ValueError("path must not traverse parent directories or contain empty segments")
    return path


class RepoReadRequest(BaseModel):
    """Request payload for reading a file through the repo MCP tool."""

    path: str
    ref: Optional[str] = None

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    _path_validator = field_validator("path", mode="before")(_validate_relative_path)


class RepoReadResponse(BaseModel):
    """Response payload containing file contents and metadata."""

    path: str
    content: str
    sha: Optional[str] = None

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)


class RepoWriteRequest(BaseModel):
    """Request payload for writing a file through the repo MCP tool."""

    path: str
    content: str
    allow_create: bool = False

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    _path_validator = field_validator("path", mode="before")(_validate_relative_path)


class RunnerCommandRequest(BaseModel):
    """Describes a command execution via the runner MCP tool."""

    command: List[str] = Field(alias="cmd")
    timeout_seconds: int = 600
    workdir: Optional[str] = None
    capture_output: bool = True

    model_config = ConfigDict(frozen=True, populate_by_name=True)

    @field_validator("command")
    @classmethod
    def _require_tokens(cls, tokens: List[str]) -> List[str]:
        if not tokens:
            raise ValueError("command must provide at least one token")
        return tokens

    @field_validator("timeout_seconds")
    @classmethod
    def _require_positive_timeout(cls, timeout: int) -> int:
        if timeout <= 0:
            raise ValueError("timeout_seconds must be positive")
        return timeout


class CodeSearchQuery(BaseModel):
    """Query payload for the code-search MCP tool."""

    query: str
    max_results: int = 20
    repo_filter: Optional[str] = None

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    @field_validator("query")
    @classmethod
    def _validate_query(cls, query: str) -> str:
        if not query or len(query) < 3:
            raise ValueError("query must contain at least 3 characters")
        return query

    @field_validator("max_results")
    @classmethod
    def _validate_max_results(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("max_results must be positive")
        if value > 200:
            raise ValueError("max_results must not exceed 200")
        return value


class CodeSearchResult(BaseModel):
    """Individual hit returned from the code-search MCP tool."""

    path: str
    start_line: int
    end_line: int
    snippet: str

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    _path_validator = field_validator("path", mode="before")(_validate_relative_path)

    @field_validator("start_line", "end_line")
    @classmethod
    def _validate_line_numbers(cls, value: int, info) -> int:
        if value <= 0:
            raise ValueError("line numbers must be positive")
        return value

    @field_validator("end_line")
    @classmethod
    def _validate_end_not_before_start(cls, end: int, info) -> int:
        start = info.data.get("start_line", 0)
        if end < start:
            raise ValueError("end_line must be >= start_line")
        return end


class CodeSearchResponse(BaseModel):
    """Response payload for the code-search MCP tool."""

    query: CodeSearchQuery
    results: Tuple[CodeSearchResult, ...]

    model_config = ConfigDict(frozen=True)

    @property
    def paths(self) -> Iterable[str]:
        return (result.path for result in self.results)
