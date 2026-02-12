"""Rubric parsing and management."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class RubricDimension(BaseModel):
    """A single evaluation dimension."""

    name: str
    description: str
    weight: float = 1.0
    threshold: float = 0.7
    criteria: list[str] = Field(default_factory=list)
    score_anchors: dict[int, str] = Field(default_factory=dict)


class Rubric(BaseModel):
    """Evaluation rubric."""

    name: str = "default"
    description: str | None = None
    dimensions: list[RubricDimension] = Field(default_factory=list)
    red_flags: list[str] = Field(default_factory=list)
    pass_threshold: float = 0.7


def load_rubric(path: Path) -> Rubric:
    """Load a rubric from YAML file.

    Args:
        path: Path to rubric YAML

    Returns:
        Parsed Rubric
    """
    with open(path) as f:
        data = yaml.safe_load(f) or {}

    return parse_rubric(data)


def parse_rubric(data: dict[str, Any]) -> Rubric:
    """Parse rubric from dict.

    Args:
        data: Rubric data dict

    Returns:
        Parsed Rubric
    """
    dimensions = []

    for dim_data in data.get("dimensions", []):
        score_anchors: dict[int, str] = {}
        raw_anchors = dim_data.get("score_anchors") or {}
        if isinstance(raw_anchors, dict):
            for k, v in raw_anchors.items():
                try:
                    key = int(k)
                except (TypeError, ValueError):
                    continue
                if v is None:
                    continue
                score_anchors[key] = str(v)

        dimensions.append(
            RubricDimension(
                name=dim_data.get("name", ""),
                description=dim_data.get("description", ""),
                weight=dim_data.get("weight", 1.0),
                threshold=dim_data.get("threshold", 0.7),
                criteria=dim_data.get("criteria", []),
                score_anchors=score_anchors,
            )
        )

    return Rubric(
        name=data.get("name", "default"),
        description=data.get("description"),
        dimensions=dimensions,
        red_flags=data.get("red_flags", []),
        pass_threshold=data.get("pass_threshold", 0.7),
    )


def get_default_rubric() -> Rubric:
    """Get a sensible default rubric for content evaluation."""
    return Rubric(
        name="default",
        description="Default content evaluation rubric",
        dimensions=[
            RubricDimension(
                name="clarity",
                description="Is the content clear and easy to understand?",
                weight=1.0,
                criteria=["Clear language", "Logical structure", "No ambiguity"],
                score_anchors={
                    1: "Confusing structure; ambiguous meaning; reader must re-read to understand",
                    3: "Understandable but with some unclear phrasing or structural issues",
                    5: (
                        "Crystal clear; logical flow; every sentence communicates its point "
                        "on first read"
                    ),
                },
            ),
            RubricDimension(
                name="engagement",
                description="Is the content engaging and compelling?",
                weight=1.2,
                criteria=["Strong hook", "Maintains interest", "Call to action"],
                score_anchors={
                    1: (
                        "Bland, generic content that readers would scroll past; "
                        "no hook or call to action"
                    ),
                    3: (
                        "Moderately interesting but missing a strong hook or "
                        "compelling call to action"
                    ),
                    5: (
                        "Immediately grabs attention; maintains interest throughout; "
                        "compelling call to action"
                    ),
                },
            ),
            RubricDimension(
                name="brand_voice",
                description="Does it match the brand voice?",
                weight=1.0,
                criteria=["Consistent tone", "Appropriate vocabulary", "On-brand messaging"],
                score_anchors={
                    1: (
                        "Contradicts brand tone; uses forbidden vocabulary; feels like a "
                        "different brand"
                    ),
                    3: (
                        "Generally on-brand but with occasional inconsistencies in tone "
                        "or word choice"
                    ),
                    5: (
                        "Indistinguishable from the best brand exemplars; perfect tone, "
                        "vocabulary, and framing"
                    ),
                },
            ),
            RubricDimension(
                name="accuracy",
                description="Is the content factually accurate?",
                weight=1.5,
                criteria=["No false claims", "Verifiable statements", "Proper citations"],
                score_anchors={
                    1: (
                        "Contains false or misleading claims; unverifiable statements "
                        "presented as fact"
                    ),
                    3: "Mostly accurate but some claims lack specificity or nuance",
                    5: (
                        "Every claim is verifiable; precise language; no overstatements "
                        "or misleading framing"
                    ),
                },
            ),
        ],
        red_flags=[
            "Offensive content",
            "Misleading claims",
            "Competitor mentions (negative)",
        ],
        pass_threshold=0.7,
    )
