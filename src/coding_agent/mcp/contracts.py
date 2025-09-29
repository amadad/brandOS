"""Pydantic contracts for key MCP tools used by the coding agent."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RepoWriteRequest(BaseModel):
    """Request payload for writing a file through the repo MCP tool."""

    path: str
    content: str
    allow_create: bool = False

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)

    @field_validator("path")
    @classmethod
    def _disallow_escape(cls, path: str) -> str:
        if not path:
            raise ValueError("path must not be empty")
        normalized = path.replace("\\", "/")
        if normalized.startswith("/"):
            raise ValueError("path must be relative")
        parts = normalized.split("/")
        if any(part in {"..", ""} for part in parts):
            raise ValueError("path must not traverse parent directories or contain empty segments")
        return path


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
