
# Spec: Produce-Eval Gate

## Overview

When content is generated via `brandos produce copy`, it can optionally be graded against the brand's rubric and auto-healed if it fails. This closes the gap between production and evaluation, ensuring only quality-checked content reaches the publish queue.

## Requirements

### R1: `produce_and_eval()` Pipeline Function

A function that composes generation, grading, and healing into a single call.

**Given** `produce_and_eval(topic="AI trends", brand="acme", platform="twitter")`
**When** content is generated and graded
**Then** the return dict includes:
```python
{
    "main": "...",              # Final content (healed if applicable)
    "variants": [...],          # Original variants (not healed)
    "hashtags": [...],
    "platform": "twitter",
    "eval": {                   # NEW: eval results
        "score": 0.85,
        "passed": True,
        "dimension_scores": [...],
        "suggestions": [...],
    },
    "healed": False,            # NEW: whether healing was applied
    "heal_iterations": 0,       # NEW: number of heal iterations (0 if not healed)
    "original_score": 0.85,     # NEW: score before healing (same as score if not healed)
}
```

**Given** `produce_and_eval(topic="...", brand="acme", platform="twitter", heal=True)`
**When** content is generated, graded, and fails (score < pass_threshold)
**Then** the heal loop runs on the `main` content and the return dict shows:
```python
{
    "main": "...",              # Healed content
    "eval": {
        "score": 0.82,         # Post-heal score
        "passed": True,
    },
    "healed": True,
    "heal_iterations": 2,
    "original_score": 0.55,    # Pre-heal score
}
```

**Given** `produce_and_eval(topic="...", brand="acme", heal=True)` and content passes on first grade
**When** score >= pass_threshold
**Then** healing is skipped, `healed=False`, `heal_iterations=0`

**Given** `produce_and_eval(topic="...", brand=None)`
**When** no brand is provided
**Then** grading uses the default rubric without voice context (backward compatible)

### R2: `--eval` CLI Flag

**Given** `brandos produce copy "AI trends" --brand acme --eval`
**When** the flag is present
**Then** output includes eval scores alongside the generated content

**Given** `brandos produce copy "AI trends" --brand acme` (no `--eval`)
**When** the flag is absent
**Then** behavior is identical to current implementation (no eval overhead)

### R3: `--heal` CLI Flag

**Given** `brandos produce copy "AI trends" --brand acme --heal`
**When** the flag is present
**Then** content is graded and auto-healed if it fails. `--heal` implies `--eval`.

**Given** `brandos produce copy "AI trends" --brand acme --heal` and content fails after max iterations
**When** healing cannot reach the pass threshold
**Then** the best iteration is returned with `passed=False` and the final score. Content is NOT silently dropped — the user sees the score and decides.

### R4: Platform Length Enforcement

**Given** content is healed for platform "twitter"
**When** the healed content exceeds 280 characters
**Then** the heal prompt includes the character limit as a hard constraint

Platform limits used:

| Platform | Limit |
|----------|-------|
| twitter | 280 |
| threads | 500 |
| linkedin | 3000 |
| instagram | 2200 |
| facebook | 63206 |

**Given** content is healed without a platform specified
**When** no platform limit applies
**Then** no length constraint is added to the heal prompt

### R5: Explore Command Uses Eval Gate

**Given** `brandos produce explore "AI trends" --brand acme`
**When** the explore command generates content for each platform
**Then** each piece is graded before enqueueing. Content that fails is reported but still queued (with a warning), preserving current behavior. The eval score is stored in the queue item's `metadata`.

**Given** `brandos produce explore "AI trends" --brand acme --heal`
**When** the `--heal` flag is passed to explore
**Then** content that fails grading is healed before enqueueing.

### R6: Backward Compatibility

**Given** any existing caller of `generate_copy()`, `generate_thread()`, or the produce CLI
**When** they do not use `--eval` or `--heal` flags
**Then** behavior is unchanged — no additional LLM calls, no performance impact

## Non-Functional Requirements

- No new dependencies
- `produce_and_eval()` makes at most 1 (generate) + 1 (grade) + N (heal iterations, max 3) LLM calls
- When `--eval` is used without `--heal`, exactly 1 additional LLM call (the grade)
- The function is synchronous (matching existing `generate_copy` pattern)
- Platform limits are defined as a simple dict, not a config file (YAGNI)

