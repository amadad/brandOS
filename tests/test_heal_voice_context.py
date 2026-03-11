from __future__ import annotations


def test_heal_content_with_brand_includes_voice_context_in_improvement_prompt(monkeypatch) -> None:
    from brand_os.eval import grader, heal
    from brand_os.eval.rubric import Rubric, RubricDimension

    def _fake_load_brand_config(brand: str):
        assert brand == "acme"
        return {
            "voice": {
                "tone": "bold",
                "vocabulary": "technical",
                "patterns": ["Start with a provocative question", "Use data points"],
                "rules": ["Never use passive voice", "Keep sentences under 20 words"],
                "avoid_phrases": ["industry-leading", "synergy", "leverage"],
            }
        }

    monkeypatch.setattr(grader, "load_brand_config", _fake_load_brand_config)

    def _fake_grade_content(content: str, rubric: Rubric | None = None, brand: str | None = None):
        assert brand == "acme"
        return grader.GradeResult(
            overall_score=0.4,
            passed=False,
            dimension_scores=[
                grader.DimensionScore(
                    name="brand_voice",
                    score=0.4,
                    feedback="Too generic; not bold or technical enough.",
                    passed=False,
                )
            ],
            red_flags_found=[],
            summary="Needs voice fixes",
            suggestions=[],
        )

    monkeypatch.setattr(heal, "grade_content", _fake_grade_content)

    captured: dict[str, str] = {}

    def _fake_complete(*, prompt: str, system: str) -> str:
        captured["prompt"] = prompt
        captured["system"] = system
        return "IMPROVED"

    monkeypatch.setattr(heal, "complete", _fake_complete)

    rubric = Rubric(
        name="test",
        dimensions=[
            RubricDimension(name="brand_voice", description="Matches brand voice", weight=1.0),
        ],
    )

    heal.heal_content(
        "hello",
        rubric=rubric,
        max_iterations=1,
        target_score=0.8,
        brand="acme",
    )

    prompt = captured["prompt"]
    assert "## Brand Voice Definition (acme)" in prompt
    assert "- Tone: bold" in prompt
    assert "- Vocabulary: technical" in prompt
    assert "Evaluate the brand_voice dimension against these specific guidelines." in prompt
    assert "- brand_voice: Too generic; not bold or technical enough." in prompt

