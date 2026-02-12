
# Tasks: Voice Exemplar Injection

## 1. Voice Exemplars Data Model & Loader
- [x] 1.1 Add `VoiceExemplars` dataclass to `src/brand_os/eval/grader.py`
- [x] 1.2 Implement `load_voice_exemplars(brand: str) -> VoiceExemplars | None` with markdown parsing
- [x] 1.3 Handle edge cases: missing file, empty file, no blockquotes, malformed markdown
- [x] 1.4 Enforce limits: max 3 good + 3 bad examples, 300 chars each

## 2. Voice Context Extension
- [x] 2.1 Extend `_build_voice_context()` to accept optional `VoiceExemplars` parameter
- [x] 2.2 Format exemplars as `### On-Brand Examples` and `### Off-Brand Examples` sections
- [x] 2.3 Implement token budget: 500 chars definition + 500 chars good + 500 chars bad = 1500 total cap
- [x] 2.4 Update the instruction line to reference both guidelines and examples

## 3. Grading Integration
- [x] 3.1 Update `grade_content()` to call `load_voice_exemplars()` when `brand` is provided
- [x] 3.2 Pass exemplars to `_build_voice_context()`
- [ ] 3.3 Verify prompt renders correctly with exemplars present and absent

## 4. Healing Integration
- [ ] 4.1 Update `_improve_content()` to load and inject exemplars when `brand` is provided
- [ ] 4.2 Format exemplars as "Voice Reference (target style)" / "Voice Anti-Pattern" in healing prompt

## 5. Template Update
- [ ] 5.1 Rewrite `brands/_template/references/voice-guide.md` with machine-parseable structure
- [ ] 5.2 Add HTML comments explaining how exemplars are used by the grader
- [ ] 5.3 Verify the empty template returns `None` from `load_voice_exemplars()`

## 6. Tests
- [ ] 6.1 Test `load_voice_exemplars()`: parses good/bad examples from well-formed voice-guide
- [ ] 6.2 Test `load_voice_exemplars()`: returns None for missing/empty file
- [ ] 6.3 Test `load_voice_exemplars()`: respects max 3 examples + 300 char limit
- [ ] 6.4 Test `_build_voice_context()`: includes exemplars when provided
- [ ] 6.5 Test `_build_voice_context()`: respects 1500 char total budget
- [ ] 6.6 Test `grade_content()`: prompt includes exemplars when brand has voice-guide
- [ ] 6.7 Test `grade_content()`: backward compatible when brand has no voice-guide
- [ ] 6.8 Test `_improve_content()`: healing prompt includes exemplars

## 7. Verification
- [ ] 7.1 `uv run ruff check src/` — no lint errors
- [ ] 7.2 `uv run ruff format src/` — code formatted
- [ ] 7.3 `uv run pytest tests/eval/` — all tests pass
- [ ] 7.4 `uv run pytest tests/` — full suite passes (no regressions)
