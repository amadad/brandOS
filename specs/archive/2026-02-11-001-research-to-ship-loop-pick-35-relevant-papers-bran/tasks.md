
# Tasks: Produce-Eval Gate

## 1. Research & Preparation
- [x] 1.1 Read current `produce/copy.py` and map all public functions
- [x] 1.2 Read current `produce/cli.py` and identify where `--eval`/`--heal` flags fit
- [x] 1.3 Read `eval/grader.py` — confirm `grade_content()` signature and return type
- [x] 1.4 Read `eval/heal.py` — confirm `heal_content()` signature and return type
- [x] 1.5 Read `produce/queue.py` — confirm `enqueue()` accepts metadata
- [x] 1.6 Identify all callers of `generate_copy()` in the codebase

## 2. Build `produce_and_eval()` Pipeline
- [x] 2.1 Add `PLATFORM_LIMITS` dict to `produce/copy.py` (twitter=280, threads=500, linkedin=3000, instagram=2200, facebook=63206)
- [x] 2.2 Add `produce_and_eval()` function that chains generate → grade → (optional) heal
  - Accepts same params as `generate_copy()` plus `eval: bool`, `heal: bool`, `rubric: Rubric | None`
  - Calls `generate_copy()` to get initial content
  - If `eval` or `heal`: calls `grade_content(main, rubric, brand=brand)`
  - If `heal` and grade fails: calls `heal_content(main, rubric, brand=brand, target_score=pass_threshold)`
  - Returns enriched dict with eval results
- [x] 2.3 Write test: `produce_and_eval` with `eval=True` returns scores (mock LLM)
- [x] 2.4 Write test: `produce_and_eval` with `heal=True` runs heal loop when grade fails (mock LLM)
- [x] 2.5 Write test: `produce_and_eval` with `heal=True` skips heal when grade passes (mock LLM)
- [x] 2.6 Write test: `produce_and_eval` without eval/heal returns same as `generate_copy()` (no extra LLM calls)

## 3. Wire CLI Flags
- [x] 3.1 Add `--eval` flag to `copy_cmd` in `produce/cli.py`
- [x] 3.2 Add `--heal` flag to `copy_cmd` (implies `--eval`)
- [x] 3.3 When flags present, call `produce_and_eval()` instead of `generate_copy()`
- [x] 3.4 Display eval scores in output (Rich table for `--format text`, included in JSON for `--format json`)

## 4. Update Explore Command
- [x] 4.1 Add `--heal` flag to `explore_cmd`
- [x] 4.2 Replace `generate_copy()` call with `produce_and_eval(eval=True, heal=heal_flag)`
- [x] 4.3 Store eval score in queue item metadata: `metadata={"eval_score": score, "eval_passed": passed}`
- [x] 4.4 Show warning for queued content that didn't pass eval

## 5. Integration Verification
- [x] 5.1 Run `uv run pytest` — all tests pass
- [x] 5.2 Run `uv run ruff check src/` — no lint errors
- [x] 5.3 Run `uv run ruff format src/` — formatted
- [x] 5.4 Export `produce_and_eval` from `produce/__init__.py`
