
# Spec: Score Anchors on Rubric Dimensions

## Overview

Add score anchor descriptions to `RubricDimension` so the LLM-as-judge grader receives concrete examples of what each score level looks like. Based on Prometheus 2 research showing anchored rubrics produce significantly more calibrated evaluations.

## Requirements

### R1: Rubric Model Extension

**Given** the existing `RubricDimension` model in `src/brand_os/eval/rubric.py`
**When** a developer defines a rubric dimension
**Then** they can optionally provide `score_anchors: dict[int, str]` mapping score levels (1-5) to descriptions of what that score looks like

**Given** a rubric YAML file without `score_anchors`
**When** it is loaded via `load_rubric()` or `parse_rubric()`
**Then** it parses successfully with an empty `score_anchors` dict (backward compatible)

**Given** a rubric YAML file with `score_anchors`
**When** it is loaded
**Then** the anchors are preserved as `dict[int, str]` on the dimension

Example YAML:
```yaml
dimensions:
  - name: brand_voice
    description: "Does it match the brand voice?"
    weight: 1.0
    threshold: 0.7
    criteria:
      - Consistent tone
      - Appropriate vocabulary
      - On-brand messaging
    score_anchors:
      1: "Contradicts brand tone; uses forbidden vocabulary; feels like a different brand"
      3: "Generally on-brand but with occasional inconsistencies in tone or word choice"
      5: "Indistinguishable from the best brand exemplars; perfect tone, vocabulary, and framing"
```

### R2: Grader Prompt Enhancement

**Given** a rubric with score anchors on one or more dimensions
**When** `grade_content()` constructs the grading prompt
**Then** the anchors are rendered inline under each dimension, formatted as:
```
- **brand_voice** (weight: 1.0, threshold: 0.7)
  Does it match the brand voice?
  Criteria: Consistent tone, Appropriate vocabulary, On-brand messaging
  Score anchors:
    1 = Contradicts brand tone; uses forbidden vocabulary; feels like a different brand
    3 = Generally on-brand but with occasional inconsistencies in tone or word choice
    5 = Indistinguishable from the best brand exemplars; perfect tone, vocabulary, and framing
```

**Given** a rubric with NO score anchors on a dimension
**When** `grade_content()` constructs the grading prompt
**Then** no anchors section is rendered for that dimension (identical to current behavior)

### R3: System Prompt Update

**Given** any rubric with at least one dimension that has score anchors
**When** the grader system prompt is constructed
**Then** it includes an instruction to use the anchors:
```
When score anchors are provided for a dimension, use them to calibrate your scores.
A score of 0.2 corresponds to anchor level 1, 0.6 to level 3, and 1.0 to level 5.
Interpolate between anchor levels for intermediate scores.
```

### R4: Heal Loop Context

**Given** content that failed grading and enters the heal loop
**When** `_improve_content()` constructs the rewrite prompt
**Then** for each failed dimension that has score anchors, the anchor for the target level (typically 5) is included as guidance:
```
### What good looks like for brand_voice
Indistinguishable from the best brand exemplars; perfect tone, vocabulary, and framing
```

### R5: Default Rubric Anchors

**Given** the default rubric returned by `get_default_rubric()`
**When** a developer uses it without customization
**Then** all 4 default dimensions (clarity, engagement, brand_voice, accuracy) have score anchors at levels 1, 3, and 5

Default anchors:

**clarity**:
- 1: "Confusing structure; ambiguous meaning; reader must re-read to understand"
- 3: "Understandable but with some unclear phrasing or structural issues"
- 5: "Crystal clear; logical flow; every sentence communicates its point on first read"

**engagement**:
- 1: "Bland, generic content that readers would scroll past; no hook or call to action"
- 3: "Moderately interesting but missing a strong hook or compelling call to action"
- 5: "Immediately grabs attention; maintains interest throughout; compelling call to action"

**brand_voice**:
- 1: "Contradicts brand tone; uses forbidden vocabulary; feels like a different brand"
- 3: "Generally on-brand but with occasional inconsistencies in tone or word choice"
- 5: "Indistinguishable from the best brand exemplars; perfect tone, vocabulary, and framing"

**accuracy**:
- 1: "Contains false or misleading claims; unverifiable statements presented as fact"
- 3: "Mostly accurate but some claims lack specificity or nuance"
- 5: "Every claim is verifiable; precise language; no overstatements or misleading framing"

### R6: Template Rubric Update

**Given** the template rubric at `brands/_template/rubric.yml`
**When** a new brand is created from the template
**Then** the rubric includes `score_anchors` with the same defaults as R5, with comments explaining how to customize

## Non-Functional Requirements

- **Backward compatibility**: Rubrics without `score_anchors` must continue to work identically
- **No new dependencies**: Only Pydantic model changes and string formatting
- **Prompt length**: Anchors add ~200 tokens per dimension to the grading prompt; this is well within context limits

## Files Changed

| File | Change |
|------|--------|
| `src/brand_os/eval/rubric.py` | Add `score_anchors` field to `RubricDimension`; update `parse_rubric()` and `get_default_rubric()` |
| `src/brand_os/eval/grader.py` | Update `GRADER_SYSTEM` prompt; update prompt construction in `grade_content()` to render anchors |
| `src/brand_os/eval/heal.py` | Update `_improve_content()` to include target anchors for failed dimensions |
| `brands/_template/rubric.yml` | Add `score_anchors` to each dimension |
| `tests/eval/test_rubric.py` | New: test parsing with/without anchors |
| `tests/eval/test_grader.py` | New: test prompt construction includes anchors |

