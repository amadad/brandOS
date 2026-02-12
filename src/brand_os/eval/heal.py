"""Self-healing content loop."""

from __future__ import annotations

from typing import Any

from brand_os.core.llm import complete
from brand_os.eval.grader import (
    GradeResult,
    _build_voice_context,
    grade_content,
    load_voice_exemplars,
)
from brand_os.eval.rubric import Rubric


def heal_content(
    content: str,
    rubric: Rubric | None = None,
    max_iterations: int = 3,
    target_score: float = 0.8,
    brand: str | None = None,
) -> dict[str, Any]:
    """Iteratively improve content until it passes.

    Args:
        content: Initial content
        rubric: Evaluation rubric
        max_iterations: Maximum improvement attempts
        target_score: Score to achieve

    Returns:
        Dict with final content, grades, and iteration history
    """
    history = []
    current_content = content

    for i in range(max_iterations):
        # Grade current content
        grade = grade_content(current_content, rubric, brand=brand)

        history.append(
            {
                "iteration": i + 1,
                "content": current_content,
                "score": grade.overall_score,
                "passed": grade.passed,
                "suggestions": grade.suggestions,
            }
        )

        # Check if we've reached target
        if grade.overall_score >= target_score and grade.passed:
            return {
                "success": True,
                "final_content": current_content,
                "final_score": grade.overall_score,
                "iterations": i + 1,
                "history": history,
            }

        # Generate improved version
        current_content = _improve_content(current_content, grade, rubric=rubric, brand=brand)

    # Final grade after all iterations
    final_grade = grade_content(current_content, rubric, brand=brand)

    return {
        "success": final_grade.overall_score >= target_score,
        "final_content": current_content,
        "final_score": final_grade.overall_score,
        "iterations": max_iterations,
        "history": history,
    }


def _improve_content(
    content: str,
    grade: GradeResult,
    rubric: Rubric | None = None,
    brand: str | None = None,
) -> str:
    """Improve content based on grade feedback.

    Args:
        content: Current content
        grade: Grade result with feedback
        rubric: Optional evaluation rubric (used for score anchor guidance if provided)
        brand: Optional brand name (used for brand voice context when supported)

    Returns:
        Improved content
    """
    prompt_parts = [
        "Improve this content based on the feedback.",
        "",
        "## Current Content",
        content,
        "",
        "## Feedback",
        f"Overall score: {grade.overall_score:.2f}",
        "",
        "### Dimension Feedback",
    ]

    for dim in grade.dimension_scores:
        if not dim.passed:
            prompt_parts.append(f"- {dim.name}: {dim.feedback}")

    # If we have rubric anchors, include "what good looks like" guidance for failed dimensions.
    if rubric is not None:
        rubric_by_name = {d.name: d for d in rubric.dimensions}
        for dim in grade.dimension_scores:
            if dim.passed:
                continue
            rubric_dim = rubric_by_name.get(dim.name)
            if rubric_dim is None or not rubric_dim.score_anchors:
                continue
            anchor_5 = rubric_dim.score_anchors.get(5)
            if not anchor_5:
                continue
            prompt_parts.extend(
                [
                    "",
                    f"### What good looks like for {dim.name}",
                    str(anchor_5),
                ]
            )

    if grade.red_flags_found:
        prompt_parts.extend(
            [
                "",
                "### Red Flags to Fix",
                *[f"- {rf}" for rf in grade.red_flags_found],
            ]
        )

    if grade.suggestions:
        prompt_parts.extend(
            [
                "",
                "### Suggestions",
                *[f"- {s}" for s in grade.suggestions],
            ]
        )

    if brand:
        exemplars = load_voice_exemplars(brand)
        voice_context = _build_voice_context(brand, exemplars)
        if voice_context:
            prompt_parts.extend(["", voice_context])

    prompt_parts.extend(
        [
            "",
            "Rewrite the content addressing the feedback. Output ONLY the improved content, "
            "no explanations.",
        ]
    )

    prompt = "\n".join(prompt_parts)

    return complete(
        prompt=prompt,
        system=(
            "You are a content improvement expert. Rewrite content to address feedback "
            "while maintaining the original intent and style."
        ),
    )
