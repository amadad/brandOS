from __future__ import annotations


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
