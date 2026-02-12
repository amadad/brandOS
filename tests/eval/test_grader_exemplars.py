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
