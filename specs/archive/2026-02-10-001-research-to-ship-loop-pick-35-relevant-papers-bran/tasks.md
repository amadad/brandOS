
# Tasks: Score Anchors on Rubric Dimensions

## 1. Rubric Model Extension
- [x] 1.1 Add `score_anchors: dict[int, str] = Field(default_factory=dict)` to `RubricDimension` in `src/brand_os/eval/rubric.py`
- [x] 1.2 Update `parse_rubric()` to extract `score_anchors` from dimension data dict
- [x] 1.3 Update `get_default_rubric()` with anchors at levels 1, 3, 5 for all 4 default dimensions

## 2. Grader Prompt Enhancement
- [x] 2.1 Update `GRADER_SYSTEM` in `src/brand_os/eval/grader.py` to include anchor calibration instruction
- [x] 2.2 Update the dimension rendering loop in `grade_content()` to append anchors when present
- [x] 2.3 Verify prompt renders correctly for dimensions both with and without anchors

## 3. Heal Loop Context
- [x] 3.1 Update `_improve_content()` in `src/brand_os/eval/heal.py` to accept optional `rubric` parameter
- [x] 3.2 For each failed dimension with anchors, include the level-5 anchor as "what good looks like" guidance
- [x] 3.3 Update `heal_content()` to pass rubric to `_improve_content()`

## 4. Template Rubric Update
- [x] 4.1 Add `score_anchors` block to each dimension in `brands/_template/rubric.yml`
- [x] 4.2 Add inline YAML comments explaining anchor customization

## 5. Tests
- [x] 5.1 Create `tests/eval/test_rubric.py`: test `parse_rubric()` with and without `score_anchors`
- [x] 5.2 Create `tests/eval/test_grader.py`: test that `grade_content()` prompt includes anchors when present and omits them when absent (mock LLM)
- [x] 5.3 Create `tests/eval/test_heal.py`: test that `_improve_content()` includes target anchors for failed dimensions (mock LLM)

## 6. Verification
- [x] 6.1 Run `uv run ruff check src/` and fix any lint issues
- [x] 6.2 Run `uv run ruff format src/`
- [x] 6.3 Run `uv run pytest tests/eval/` and confirm all tests pass
- [x] 6.4 Manual smoke test: `uv run brandos eval grade` with default rubric, confirm anchors appear in output
