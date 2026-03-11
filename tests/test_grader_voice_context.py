from __future__ import annotations


def test_build_voice_context_populated_brand(monkeypatch) -> None:
    from brand_os.eval import grader

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

    got = grader._build_voice_context("acme")
    expected = "\n".join(
        [
            "## Brand Voice Definition (acme)",
            "- Tone: bold",
            "- Vocabulary: technical",
            "- Speech patterns: Start with a provocative question, Use data points",
            "- Rules: Never use passive voice, Keep sentences under 20 words",
            "- Avoid phrases: industry-leading, synergy, leverage",
            "",
            "Evaluate the brand_voice dimension against these specific guidelines.",
        ]
    )

    assert got == expected


def test_build_voice_context_missing_or_empty_brand(monkeypatch) -> None:
    from brand_os.eval import grader

    def _fake_load_brand_config(brand: str):
        if brand == "does-not-exist":
            raise FileNotFoundError("brand not found")
        if brand == "empty-voice":
            return {"voice": {}}
        raise AssertionError(f"unexpected brand: {brand}")

    monkeypatch.setattr(grader, "load_brand_config", _fake_load_brand_config)

    # Missing/blank brand should short-circuit without loading config.
    assert grader._build_voice_context("") == ""
    assert grader._build_voice_context("   ") == ""
    assert grader._build_voice_context(None) == ""  # type: ignore[arg-type]

    # Invalid brand should not raise and should return empty.
    assert grader._build_voice_context("does-not-exist") == ""

    # Empty/minimal voice config should return empty.
    assert grader._build_voice_context("empty-voice") == ""


def test_grade_content_with_brand_includes_voice_context(monkeypatch) -> None:
    from brand_os.eval import grader
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

    captured: dict[str, str] = {}

    def _fake_complete_json(*, prompt: str, system: str, default: dict):
        captured["prompt"] = prompt
        captured["system"] = system
        return {
            "dimension_scores": [
                {"name": "brand_voice", "score": 1.0, "feedback": "ok", "passed": True}
            ],
            "red_flags_found": [],
            "summary": "ok",
            "suggestions": [],
        }

    monkeypatch.setattr(grader, "load_brand_config", _fake_load_brand_config)
    monkeypatch.setattr(grader, "complete_json", _fake_complete_json)

    rubric = Rubric(
        name="test",
        dimensions=[
            RubricDimension(name="brand_voice", description="Matches brand voice", weight=1.0)
        ],
    )

    result = grader.grade_content("hello", rubric=rubric, brand="acme")
    assert result.summary == "ok"

    prompt = captured["prompt"]
    assert "## Brand Voice Definition (acme)" in prompt
    assert "- Tone: bold" in prompt
    assert "- Vocabulary: technical" in prompt
    assert "Evaluate the brand_voice dimension against these specific guidelines." in prompt


def test_grade_content_without_brand_is_backward_compatible(monkeypatch) -> None:
    from brand_os.eval import grader
    from brand_os.eval.rubric import Rubric, RubricDimension

    def _fake_load_brand_config(_brand: str):
        raise AssertionError("load_brand_config should not be called when brand is omitted")

    captured: dict[str, str] = {}

    def _fake_complete_json(*, prompt: str, system: str, default: dict):
        captured["prompt"] = prompt
        captured["system"] = system
        return {
            "dimension_scores": [
                {"name": "brand_voice", "score": 1.0, "feedback": "ok", "passed": True}
            ],
            "red_flags_found": [],
            "summary": "ok",
            "suggestions": [],
        }

    monkeypatch.setattr(grader, "load_brand_config", _fake_load_brand_config)
    monkeypatch.setattr(grader, "complete_json", _fake_complete_json)

    rubric = Rubric(
        name="test",
        dimensions=[
            RubricDimension(name="brand_voice", description="Matches brand voice", weight=1.0)
        ],
    )

    result = grader.grade_content("hello", rubric=rubric)
    assert result.summary == "ok"

    expected_prompt = "\n".join(
        [
            "Grade this content against the rubric.",
            "",
            "## Content",
            "hello",
            "",
            "## Rubric",
            "Name: test",
            "",
            "### Dimensions",
            "- **brand_voice** (weight: 1.0, threshold: 0.7)",
            "  Matches brand voice",
        ]
    )

    assert captured["system"] == grader.GRADER_SYSTEM
    assert captured["prompt"] == expected_prompt
    assert "## Brand Voice Definition" not in captured["prompt"]
