from __future__ import annotations


def test_produce_and_eval_without_eval_or_heal_matches_generate_copy_without_extra_calls(monkeypatch) -> None:
    from brand_os.produce import copy

    expected = {
        "main": "Baseline copy.",
        "variants": ["Variant A", "Variant B"],
        "hashtags": ["#AI", "#Trends"],
        "platform": "twitter",
    }

    def _fake_generate_copy(
        topic: str,
        brand: str | None = None,
        platform: str = "twitter",
        hooks=None,
        learnings=None,
        voice=None,
    ):
        assert topic == "AI trends"
        assert brand == "acme"
        assert platform == "twitter"
        return expected

    def _fail_grade_content(*args, **kwargs):
        raise AssertionError("grade_content should not be called when eval=False and heal=False")

    def _fail_heal_content(*args, **kwargs):
        raise AssertionError("heal_content should not be called when eval=False and heal=False")

    monkeypatch.setattr(copy, "generate_copy", _fake_generate_copy)
    monkeypatch.setattr(copy, "grade_content", _fail_grade_content)
    monkeypatch.setattr(copy, "heal_content", _fail_heal_content)

    result = copy.produce_and_eval(topic="AI trends", brand="acme", platform="twitter")

    assert result == expected


def test_produce_and_eval_with_eval_true_returns_scores(monkeypatch) -> None:
    from brand_os.eval.grader import DimensionScore, GradeResult
    from brand_os.produce import copy

    def _fake_generate_copy(
        topic: str,
        brand: str | None = None,
        platform: str = "twitter",
        hooks=None,
        learnings=None,
        voice=None,
    ):
        assert topic == "AI trends"
        assert brand == "acme"
        assert platform == "twitter"
        return {
            "main": "Launch smarter workflows with AI.",
            "variants": ["Variant A", "Variant B"],
            "hashtags": ["#AI", "#Automation"],
            "platform": "twitter",
        }

    def _fake_grade_content(content: str, rubric=None, brand: str | None = None):
        assert content == "Launch smarter workflows with AI."
        assert brand == "acme"
        return GradeResult(
            overall_score=0.85,
            passed=True,
            dimension_scores=[
                DimensionScore(
                    name="clarity",
                    score=0.9,
                    feedback="Clear message.",
                    passed=True,
                )
            ],
            red_flags_found=[],
            summary="Strong",
            suggestions=["Add one concrete stat"],
        )

    monkeypatch.setattr(copy, "generate_copy", _fake_generate_copy)
    monkeypatch.setattr(copy, "grade_content", _fake_grade_content)

    result = copy.produce_and_eval(topic="AI trends", brand="acme", platform="twitter", eval=True)

    assert result["main"] == "Launch smarter workflows with AI."
    assert result["variants"] == ["Variant A", "Variant B"]
    assert result["hashtags"] == ["#AI", "#Automation"]
    assert result["platform"] == "twitter"

    assert result["eval"]["score"] == 0.85
    assert result["eval"]["passed"] is True
    assert result["eval"]["dimension_scores"] == [
        {
            "name": "clarity",
            "score": 0.9,
            "feedback": "Clear message.",
            "passed": True,
        }
    ]
    assert result["eval"]["suggestions"] == ["Add one concrete stat"]

    assert result["healed"] is False
    assert result["heal_iterations"] == 0
    assert result["original_score"] == 0.85


def test_produce_and_eval_with_heal_true_runs_heal_when_initial_grade_fails(monkeypatch) -> None:
    from brand_os.eval.grader import DimensionScore, GradeResult
    from brand_os.produce import copy

    heal_called = False

    def _fake_generate_copy(
        topic: str,
        brand: str | None = None,
        platform: str = "twitter",
        hooks=None,
        learnings=None,
        voice=None,
    ):
        assert topic == "AI trends"
        assert brand == "acme"
        assert platform == "twitter"
        return {
            "main": "Initial draft.",
            "variants": ["Variant A"],
            "hashtags": ["#AI"],
            "platform": "twitter",
        }

    def _fake_grade_content(content: str, rubric=None, brand: str | None = None):
        assert content == "Initial draft."
        assert brand == "acme"
        assert rubric is not None
        return GradeResult(
            overall_score=0.55,
            passed=False,
            dimension_scores=[
                DimensionScore(
                    name="clarity",
                    score=0.5,
                    feedback="Too vague.",
                    passed=False,
                )
            ],
            red_flags_found=[],
            summary="Needs improvement",
            suggestions=["Be more specific"],
        )

    def _fake_heal_content(content: str, rubric=None, target_score: float = 0.8, brand: str | None = None):
        nonlocal heal_called
        heal_called = True
        assert content == "Initial draft."
        assert rubric is not None
        assert target_score == rubric.pass_threshold
        assert brand == "acme"
        return {
            "final_content": "Healed draft with specifics.",
            "final_score": 0.82,
            "success": True,
            "iterations": 2,
        }

    monkeypatch.setattr(copy, "generate_copy", _fake_generate_copy)
    monkeypatch.setattr(copy, "grade_content", _fake_grade_content)
    monkeypatch.setattr(copy, "heal_content", _fake_heal_content)

    result = copy.produce_and_eval(topic="AI trends", brand="acme", platform="twitter", heal=True)

    assert heal_called is True
    assert result["main"] == "Healed draft with specifics."
    assert result["eval"]["score"] == 0.82
    assert result["eval"]["passed"] is True
    assert result["healed"] is True
    assert result["heal_iterations"] == 2
    assert result["original_score"] == 0.55


def test_produce_and_eval_with_heal_true_skips_heal_when_initial_grade_passes(monkeypatch) -> None:
    from brand_os.eval.grader import DimensionScore, GradeResult
    from brand_os.produce import copy

    heal_called = False

    def _fake_generate_copy(
        topic: str,
        brand: str | None = None,
        platform: str = "twitter",
        hooks=None,
        learnings=None,
        voice=None,
    ):
        assert topic == "AI trends"
        assert brand == "acme"
        assert platform == "twitter"
        return {
            "main": "Passing draft.",
            "variants": ["Variant A"],
            "hashtags": ["#AI"],
            "platform": "twitter",
        }

    def _fake_grade_content(content: str, rubric=None, brand: str | None = None):
        assert content == "Passing draft."
        assert brand == "acme"
        assert rubric is not None
        return GradeResult(
            overall_score=0.91,
            passed=True,
            dimension_scores=[
                DimensionScore(
                    name="clarity",
                    score=0.95,
                    feedback="Clear and specific.",
                    passed=True,
                )
            ],
            red_flags_found=[],
            summary="Strong",
            suggestions=["Optional: add a CTA"],
        )

    def _fake_heal_content(content: str, rubric=None, target_score: float = 0.8, brand: str | None = None):
        nonlocal heal_called
        heal_called = True
        return {
            "final_content": "Should not be used",
            "final_score": 0.99,
            "success": True,
            "iterations": 1,
        }

    monkeypatch.setattr(copy, "generate_copy", _fake_generate_copy)
    monkeypatch.setattr(copy, "grade_content", _fake_grade_content)
    monkeypatch.setattr(copy, "heal_content", _fake_heal_content)

    result = copy.produce_and_eval(topic="AI trends", brand="acme", platform="twitter", heal=True)

    assert heal_called is False
    assert result["main"] == "Passing draft."
    assert result["eval"]["score"] == 0.91
    assert result["eval"]["passed"] is True
    assert result["healed"] is False
    assert result["heal_iterations"] == 0
    assert result["original_score"] == 0.91
