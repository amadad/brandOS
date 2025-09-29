"""Domain models for coding agent planning artifacts."""

from __future__ import annotations

from typing import Tuple

from pydantic import BaseModel, ConfigDict, Field


class PlannedEdit(BaseModel):
    """Represents a single planned edit in the source tree."""

    path: str
    intent: str

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)


class ChangePlan(BaseModel):
    """PlannerAgent output that guides downstream activities."""

    ticket_id: str = Field(alias="ticket_id")
    goal: str
    constraints: Tuple[str, ...] = Field(default_factory=tuple)
    edits: Tuple[PlannedEdit, ...]
    risk: Tuple[str, ...] = Field(default_factory=tuple)
    checks: Tuple[str, ...] = Field(default_factory=tuple)

    model_config = ConfigDict(
        frozen=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )
