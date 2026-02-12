from __future__ import annotations


def test_improve_content_includes_target_anchor_for_failed_dimensions(monkeypatch) -> None:
    from brand_os.eval import grader, heal
    from brand_os.eval.rubric import Rubric, RubricDimension

    captured: dict[str, str] = {}

    def _fake_complete(*, prompt: str, system: str) -> str:
        captured["prompt"] = prompt
        captured["system"] = system
        return "IMPROVED"

    monkeypatch.setattr(heal, "complete", _fake_complete)

    rubric = Rubric(
        name="test",
        dimensions=[
            RubricDimension(
                name="brand_voice",
                description="Matches brand voice",
                score_anchors={1: "Bad", 3: "OK", 5: "Great: indistinguishable from exemplars"},
            ),
            RubricDimension(
                name="clarity",
                description="Clear writing",
                score_anchors={5: "Crystal clear"},
            ),
            RubricDimension(
                name="engagement",
                description="Engaging content",
                score_anchors={},
            ),
        ],
    )

    grade = grader.GradeResult(
        overall_score=0.4,
        passed=False,
        dimension_scores=[
            grader.DimensionScore(
                name="brand_voice",
                score=0.4,
                feedback="Too generic",
                passed=False,
            ),
            grader.DimensionScore(
                name="clarity",
                score=0.9,
                feedback="Fine",
                passed=True,
            ),
            grader.DimensionScore(
                name="engagement",
                score=0.3,
                feedback="No hook",
                passed=False,
            ),
        ],
        red_flags_found=[],
        summary="Needs improvement",
        suggestions=[],
    )

    out = heal._improve_content("hello", grade, rubric=rubric)
    assert out == "IMPROVED"

    prompt = captured["prompt"]

    assert "### What good looks like for brand_voice" in prompt
    assert "Great: indistinguishable from exemplars" in prompt

    # Passed dimensions should not get anchor guidance.
    assert "### What good looks like for clarity" not in prompt

    # Failed dimensions with no anchors should not get anchor guidance.
    assert "### What good looks like for engagement" not in prompt


def test_improve_content_formats_voice_exemplars_for_healing_prompt(monkeypatch) -> None:
    from brand_os.eval import grader, heal

    captured: dict[str, str] = {}

    def _fake_complete(*, prompt: str, system: str) -> str:
        captured["prompt"] = prompt
        captured["system"] = system
        return "IMPROVED"

    monkeypatch.setattr(heal, "complete", _fake_complete)
    monkeypatch.setattr(heal, "load_voice_exemplars", lambda _brand: object())
    monkeypatch.setattr(
        heal,
        "_build_voice_context",
        lambda _brand, _exemplars: (
            "## Brand Voice Definition (acme)\n"
            "### On-Brand Examples\n"
            "> good\n"
            "### Off-Brand Examples\n"
            "> bad"
        ),
    )

    grade = grader.GradeResult(
        overall_score=0.3,
        passed=False,
        dimension_scores=[
            grader.DimensionScore(
                name="brand_voice",
                score=0.3,
                feedback="Off voice",
                passed=False,
            )
        ],
        red_flags_found=[],
        summary="Needs improvement",
        suggestions=[],
    )

    out = heal._improve_content("hello", grade, brand="acme")
    assert out == "IMPROVED"

    prompt = captured["prompt"]
    assert "### Voice Reference (target style)" in prompt
    assert "### Voice Anti-Pattern (avoid this style)" in prompt
    assert "### On-Brand Examples" not in prompt
    assert "### Off-Brand Examples" not in prompt
