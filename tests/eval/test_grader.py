from __future__ import annotations


def _extract_dimension_block(prompt: str, *, dim_name: str, weight: float, threshold: float) -> str:
    lines = prompt.splitlines()
    header = f"- **{dim_name}** (weight: {weight}, threshold: {threshold})"
    start = lines.index(header)

    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("- **"):
            end = i
            break

    return "\n".join(lines[start:end])


def test_grade_content_prompt_renders_score_anchors_only_when_present(monkeypatch) -> None:
    from brand_os.eval import grader
    from brand_os.eval.rubric import Rubric, RubricDimension

    captured: dict[str, str] = {}

    def _fake_complete_json(*, prompt: str, system: str, default: dict):
        captured["prompt"] = prompt
        captured["system"] = system
        return {
            "dimension_scores": [],
            "red_flags_found": [],
            "summary": "ok",
            "suggestions": [],
        }

    monkeypatch.setattr(grader, "complete_json", _fake_complete_json)

    rubric = Rubric(
        name="test",
        dimensions=[
            RubricDimension(
                name="with_anchors",
                description="Has anchors",
                weight=1.0,
                threshold=0.7,
                criteria=["A", "B"],
                score_anchors={1: "Bad", 3: "OK", 5: "Great"},
            ),
            RubricDimension(
                name="without_anchors",
                description="No anchors",
                weight=2.0,
                threshold=0.8,
                criteria=["C"],
                score_anchors={},
            ),
        ],
    )

    grader.grade_content("hello", rubric=rubric)

    prompt = captured["prompt"]

    with_block = _extract_dimension_block(prompt, dim_name="with_anchors", weight=1.0, threshold=0.7)
    assert "  Score anchors:" in with_block
    assert "    1 = Bad" in with_block
    assert "    3 = OK" in with_block
    assert "    5 = Great" in with_block

    without_block = _extract_dimension_block(
        prompt, dim_name="without_anchors", weight=2.0, threshold=0.8
    )
    assert "Score anchors:" not in without_block

