
# Tasks: Voice-Anchored Grading

## 1. Research & Preparation
- [x] 1.1 Read current `grader.py` implementation and identify injection point
- [x] 1.2 Read current `heal.py` implementation and identify where brand context flows
- [x] 1.3 Read `brands.py` / `identity.py` to understand voice config loading
- [x] 1.4 Read `learnings.py` to verify brand parameter is already present
- [x] 1.5 Identify all callers of `grade_content()` in the codebase

## 2. Build Voice Context Helper
- [x] 2.1 Add `_build_voice_context(brand: str) -> str` function to `grader.py`
  - Load brand config via `get_brand_config(brand)`
  - Extract `voice` section
  - Format as structured prompt text
  - Return empty string if brand not found or voice is empty
- [x] 2.2 Write unit test for `_build_voice_context` with a populated brand
- [x] 2.3 Write unit test for `_build_voice_context` with missing/empty brand

## 3. Wire Brand into grade_content
- [x] 3.1 Add `brand: str | None = None` parameter to `grade_content()`
- [x] 3.2 Call `_build_voice_context(brand)` when brand is provided
- [x] 3.3 Append voice context to prompt (after existing `context` if present)
- [x] 3.4 Write test: `grade_content` with brand produces voice-anchored prompt
- [x] 3.5 Write test: `grade_content` without brand is backward compatible

## 4. Wire Brand into heal_content
- [x] 4.1 Add `brand: str | None = None` parameter to `heal_content()`
- [x] 4.2 Pass `brand` through to `grade_content()` calls inside the loop
- [x] 4.3 Include voice context in `_improve_content()` when brand is available
- [x] 4.4 Write test: `heal_content` with brand includes voice in improvement prompt

## 5. Verify Learnings Integration
- [x] 5.1 Confirm `log_evaluation` already receives `brand` (no change needed — verify only)
- [x] 5.2 Add `brand` to the logged entry metadata if not already present

## 6. Integration Verification
- [x] 6.1 Run `uv run pytest` — all tests pass
- [x] 6.2 Run `uv run ruff check src/` — no lint errors
- [x] 6.3 Run `uv run ruff format src/` — formatted
- [x] 6.4 Manual smoke test: `uv run brandos eval grade --brand _template` works
