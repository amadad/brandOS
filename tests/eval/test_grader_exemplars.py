from __future__ import annotations


def test_load_voice_exemplars_parses_well_formed_examples(
    monkeypatch, tmp_path
) -> None:
    from brand_os.eval import grader

    brand_dir = tmp_path / "acme"
    voice_guide = brand_dir / "references" / "voice-guide.md"
    voice_guide.parent.mkdir(parents=True)
    voice_guide.write_text(
        """## Examples

### Good Example
> We don't just ship features - we ship outcomes.

### What to Avoid
> Our industry-leading platform leverages cutting-edge AI.
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(grader, "get_brand_dir", lambda _brand: brand_dir)

    result = grader.load_voice_exemplars("acme")

    assert result is not None
    assert result.good_examples == ["We don't just ship features - we ship outcomes."]
    assert result.bad_examples == [
        "Our industry-leading platform leverages cutting-edge AI."
    ]


def test_load_voice_exemplars_template_returns_none() -> None:
    from brand_os.eval import grader

    assert grader.load_voice_exemplars("_template") is None


def test_load_voice_exemplars_missing_file_returns_none(monkeypatch, tmp_path) -> None:
    from brand_os.eval import grader

    brand_dir = tmp_path / "acme"
    brand_dir.mkdir(parents=True)

    monkeypatch.setattr(grader, "get_brand_dir", lambda _brand: brand_dir)

    assert grader.load_voice_exemplars("acme") is None


def test_load_voice_exemplars_empty_file_returns_none(monkeypatch, tmp_path) -> None:
    from brand_os.eval import grader

    brand_dir = tmp_path / "acme"
    voice_guide = brand_dir / "references" / "voice-guide.md"
    voice_guide.parent.mkdir(parents=True)
    voice_guide.write_text("\n  \n", encoding="utf-8")

    monkeypatch.setattr(grader, "get_brand_dir", lambda _brand: brand_dir)

    assert grader.load_voice_exemplars("acme") is None


def test_load_voice_exemplars_no_blockquotes_returns_none(monkeypatch, tmp_path) -> None:
    from brand_os.eval import grader

    brand_dir = tmp_path / "acme"
    voice_guide = brand_dir / "references" / "voice-guide.md"
    voice_guide.parent.mkdir(parents=True)
    voice_guide.write_text(
        """## Examples

### Good Example
Plain text that is not a blockquote.

### What to Avoid
Also plain text.
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(grader, "get_brand_dir", lambda _brand: brand_dir)

    assert grader.load_voice_exemplars("acme") is None


def test_load_voice_exemplars_malformed_markdown_does_not_leak_sections(
    monkeypatch, tmp_path
) -> None:
    from brand_os.eval import grader

    brand_dir = tmp_path / "acme"
    voice_guide = brand_dir / "references" / "voice-guide.md"
    voice_guide.parent.mkdir(parents=True)
    voice_guide.write_text(
        """## Examples

### Good Example
> On-brand example.

###Bad Example
> This should not be parsed as good.
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(grader, "get_brand_dir", lambda _brand: brand_dir)

    result = grader.load_voice_exemplars("acme")

    assert result is not None
    assert result.good_examples == ["On-brand example."]
    assert result.bad_examples == []


def test_load_voice_exemplars_enforces_max_counts_and_length(
    monkeypatch, tmp_path
) -> None:
    from brand_os.eval import grader

    brand_dir = tmp_path / "acme"
    voice_guide = brand_dir / "references" / "voice-guide.md"
    voice_guide.parent.mkdir(parents=True)

    long_good = "G" * 350
    long_bad = "B" * 350
    voice_guide.write_text(
        f"""## Examples

### Good Examples
> Good 1

> {long_good}

> Good 3

> Good 4

### Bad Examples
> Bad 1

> {long_bad}

> Bad 3

> Bad 4
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(grader, "get_brand_dir", lambda _brand: brand_dir)

    result = grader.load_voice_exemplars("acme")

    assert result is not None
    assert len(result.good_examples) == 3
    assert len(result.bad_examples) == 3
    assert all(len(example) <= 300 for example in result.good_examples)
    assert all(len(example) <= 300 for example in result.bad_examples)
    assert result.good_examples[1] == "G" * 300
    assert result.bad_examples[1] == "B" * 300


def test_grade_content_prompt_renders_voice_exemplars_when_present(monkeypatch) -> None:
    from brand_os.eval import grader
    from brand_os.eval.rubric import Rubric, RubricDimension

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

    monkeypatch.setattr(grader, "complete_json", _fake_complete_json)
    monkeypatch.setattr(
        grader,
        "load_brand_config",
        lambda _brand: {"voice": {"tone": "bold", "vocabulary": "technical"}},
    )
    monkeypatch.setattr(
        grader,
        "load_voice_exemplars",
        lambda _brand: grader.VoiceExemplars(
            good_examples=["We ship outcomes, not just features."],
            bad_examples=["Our industry-leading platform synergizes workflows."],
            raw_text="raw",
        ),
    )

    rubric = Rubric(
        name="test",
        dimensions=[
            RubricDimension(name="brand_voice", description="Matches brand voice", weight=1.0)
        ],
    )

    grader.grade_content("hello", rubric=rubric, brand="acme")

    prompt = captured["prompt"]
    assert "## Brand Voice Definition (acme)" in prompt
    assert "### On-Brand Examples" in prompt
    assert "> We ship outcomes, not just features." in prompt
    assert "### Off-Brand Examples" in prompt
    assert "> Our industry-leading platform synergizes workflows." in prompt


def test_grade_content_prompt_omits_exemplar_sections_when_absent(monkeypatch) -> None:
    from brand_os.eval import grader
    from brand_os.eval.rubric import Rubric, RubricDimension

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

    monkeypatch.setattr(grader, "complete_json", _fake_complete_json)
    monkeypatch.setattr(
        grader,
        "load_brand_config",
        lambda _brand: {"voice": {"tone": "bold", "vocabulary": "technical"}},
    )
    monkeypatch.setattr(grader, "load_voice_exemplars", lambda _brand: None)

    rubric = Rubric(
        name="test",
        dimensions=[
            RubricDimension(name="brand_voice", description="Matches brand voice", weight=1.0)
        ],
    )

    grader.grade_content("hello", rubric=rubric, brand="acme")

    prompt = captured["prompt"]
    assert "## Brand Voice Definition (acme)" in prompt
    assert "### On-Brand Examples" not in prompt
    assert "### Off-Brand Examples" not in prompt
