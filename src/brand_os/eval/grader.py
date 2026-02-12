"""Content grading using LLM-as-judge."""

from __future__ import annotations

import dataclasses
from typing import Any

from pydantic import BaseModel, Field

from brand_os.core.brands import load_brand_config
from brand_os.core.llm import complete_json
from brand_os.eval.rubric import Rubric, get_default_rubric


class DimensionScore(BaseModel):
    """Score for a single dimension."""

    name: str
    score: float
    feedback: str
    passed: bool


class GradeResult(BaseModel):
    """Full grading result."""

    overall_score: float
    passed: bool
    dimension_scores: list[DimensionScore] = Field(default_factory=list)
    red_flags_found: list[str] = Field(default_factory=list)
    summary: str
    suggestions: list[str] = Field(default_factory=list)


@dataclasses.dataclass
class VoiceExemplars:
    """Parsed voice exemplar content from a brand voice guide."""

    good_examples: list[str]
    bad_examples: list[str]
    raw_text: str


GRADER_SYSTEM = """You are an expert content evaluator.
Grade the content against each dimension of the rubric.

For each dimension, provide:
- score: 0.0 to 1.0
- feedback: specific feedback
- passed: boolean (score >= threshold)

When score anchors are provided for a dimension, use them to calibrate your scores.
A score of 0.2 corresponds to anchor level 1, 0.6 to level 3, and 1.0 to level 5.
Interpolate between anchor levels for intermediate scores.

Also check for red flags and provide overall suggestions.

Output JSON with:
- dimension_scores: array of {name, score, feedback, passed}
- red_flags_found: array of any red flags detected
- summary: overall evaluation summary
- suggestions: array of improvement suggestions"""


def _build_voice_context(brand: str) -> str:
    """Build a compact brand voice definition for grading prompts.

    Returns an empty string if the brand cannot be loaded or voice is empty.
    """

    def _clean_str(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        return str(value).strip()

    def _as_str_list(value: Any) -> list[str]:
        if not value:
            return []
        if isinstance(value, str):
            s = value.strip()
            return [s] if s else []
        if isinstance(value, list):
            out: list[str] = []
            for item in value:
                s = _clean_str(item)
                if s:
                    out.append(s)
            return out
        s = _clean_str(value)
        return [s] if s else []

    brand = (brand or "").strip()
    if not brand:
        return ""

    try:
        config = load_brand_config(brand) or {}
    except Exception:
        return ""

    if not isinstance(config, dict):
        return ""

    voice = config.get("voice") or {}
    if not isinstance(voice, dict):
        return ""

    tone = _clean_str(voice.get("tone"))
    vocabulary = _clean_str(voice.get("vocabulary"))
    patterns = _as_str_list(voice.get("patterns"))
    rules = _as_str_list(voice.get("rules"))
    avoid_phrases = _as_str_list(voice.get("avoid_phrases"))

    bullets: list[str] = []
    if tone:
        bullets.append(f"- Tone: {tone}")
    if vocabulary:
        bullets.append(f"- Vocabulary: {vocabulary}")
    if patterns:
        bullets.append(f"- Speech patterns: {', '.join(patterns)}")
    if rules:
        bullets.append(f"- Rules: {', '.join(rules)}")
    if avoid_phrases:
        bullets.append(f"- Avoid phrases: {', '.join(avoid_phrases)}")

    if not bullets:
        return ""

    context = "\n".join(
        [
            f"## Brand Voice Definition ({brand})",
            *bullets,
            "",
            "Evaluate the brand_voice dimension against these specific guidelines.",
        ]
    )

    # Keep under 500 characters to avoid prompt bloat.
    if len(context) > 500:
        context = context[:497].rstrip() + "..."

    return context


def grade_content(
    content: str,
    rubric: Rubric | None = None,
    context: str | None = None,
    brand: str | None = None,
) -> GradeResult:
    """Grade content against a rubric.

    Args:
        content: Content to grade
        rubric: Evaluation rubric (uses default if not provided)
        context: Optional context (brand, topic, etc.)
        brand: Optional brand name (used for brand voice context when supported)

    Returns:
        GradeResult with scores and feedback
    """
    rubric = rubric or get_default_rubric()

    prompt_parts = [
        "Grade this content against the rubric.",
        "",
        "## Content",
        content,
        "",
        "## Rubric",
        f"Name: {rubric.name}",
        "",
        "### Dimensions",
    ]

    for dim in rubric.dimensions:
        prompt_parts.append(f"- **{dim.name}** (weight: {dim.weight}, threshold: {dim.threshold})")
        prompt_parts.append(f"  {dim.description}")
        if dim.criteria:
            prompt_parts.append(f"  Criteria: {', '.join(dim.criteria)}")
        if dim.score_anchors:
            prompt_parts.append("  Score anchors:")
            for level in sorted(dim.score_anchors):
                prompt_parts.append(f"    {level} = {dim.score_anchors[level]}")

    if rubric.red_flags:
        prompt_parts.extend(
            [
                "",
                "### Red Flags to Check",
                *[f"- {rf}" for rf in rubric.red_flags],
            ]
        )

    if context:
        prompt_parts.extend(["", "## Context", context])

    if brand:
        voice_context = _build_voice_context(brand)
        if voice_context:
            # Append after any existing `context` block (if present).
            prompt_parts.extend(["", voice_context])

    prompt = "\n".join(prompt_parts)

    default = {
        "dimension_scores": [],
        "red_flags_found": [],
        "summary": "Unable to grade",
        "suggestions": [],
    }

    result = complete_json(prompt=prompt, system=GRADER_SYSTEM, default=default)

    # Calculate overall score
    dimension_scores = []
    total_weight = 0
    weighted_sum = 0

    for score_data in result.get("dimension_scores", []):
        dim_score = DimensionScore(
            name=score_data.get("name", ""),
            score=score_data.get("score", 0.0),
            feedback=score_data.get("feedback", ""),
            passed=score_data.get("passed", False),
        )
        dimension_scores.append(dim_score)

        # Find weight from rubric
        weight = 1.0
        for dim in rubric.dimensions:
            if dim.name.lower() == dim_score.name.lower():
                weight = dim.weight
                break

        weighted_sum += dim_score.score * weight
        total_weight += weight

    overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0
    passed = overall_score >= rubric.pass_threshold and not result.get("red_flags_found")

    return GradeResult(
        overall_score=overall_score,
        passed=passed,
        dimension_scores=dimension_scores,
        red_flags_found=result.get("red_flags_found", []),
        summary=result.get("summary", ""),
        suggestions=result.get("suggestions", []),
    )


def quick_grade(content: str) -> float:
    """Quick grade returning just a score 0-1.

    Args:
        content: Content to grade

    Returns:
        Score 0-1
    """
    result = grade_content(content)
    return result.overall_score
