"""Pydantic models describing brand reporting artifacts."""

from __future__ import annotations

from datetime import date
from typing import Dict, Tuple

from pydantic import BaseModel, ConfigDict, Field


class BrandSignal(BaseModel):
    """Represents a single brand-related signal from an external source."""

    source: str
    headline: str
    impact: str = "medium"
    url: str | None = None
    summary: str | None = None

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)


class BrandReport(BaseModel):
    """Structured output produced by the ReporterAgent."""

    brand_id: str
    report_date: date
    highlights: Tuple[BrandSignal, ...] = ()
    metrics: Dict[str, float] = Field(default_factory=dict)
    actions: Tuple[str, ...] = ()
    overview: str | None = None
    risks: Tuple[str, ...] = ()

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)
