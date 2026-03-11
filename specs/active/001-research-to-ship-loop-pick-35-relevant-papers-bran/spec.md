
# Spec: Voice Exemplar Injection

## Overview

Load brand voice exemplars (good and bad examples) from `references/voice-guide.md` and inject them into grading and healing prompts. This gives the LLM-as-judge concrete reference material for the `brand_voice` dimension, improving scoring calibration per Prometheus-style reference-anchored evaluation.

## Requirements

### R1: Voice Exemplars Data Model

**Given** a brand with a `references/voice-guide.md` file
**When** exemplars are loaded
**Then** they are returned as a `VoiceExemplars` dataclass with:
- `good_examples: list[str]` — on-brand content passages
- `bad_examples: list[str]` — off-brand content passages
- `raw_text: str` — full voice-guide text for fallback

```python
@dataclasses.dataclass
class VoiceExemplars:
    good_examples: list[str]
    bad_examples: list[str]
    raw_text: str
```

### R2: Exemplar Loader

New function in `src/brand_os/eval/grader.py`:

```python
def load_voice_exemplars(brand: str) -> VoiceExemplars | None
```

**Given** a brand "acme" with `brands/acme/references/voice-guide.md` containing:
```markdown
## Examples

### Good Example

> We don't just ship features — we ship outcomes. Here's what 200ms of
> latency reduction meant for our conversion rates.

### What to Avoid

> Our industry-leading platform leverages cutting-edge AI to synergize
> your workflow optimization journey.
```
**When** `load_voice_exemplars("acme")` is called
**Then** it returns `VoiceExemplars(good_examples=["We don't just ship..."], bad_examples=["Our industry-leading..."])`

**Given** a brand with no `references/voice-guide.md`
**When** `load_voice_exemplars("missing-brand")` is called
**Then** it returns `None`

**Given** a brand with `voice-guide.md` that has no examples (empty template)
**When** `load_voice_exemplars("empty-brand")` is called
**Then** it returns `None` (no useful exemplars to inject)

**Given** an invalid brand name or filesystem error
**When** `load_voice_exemplars(brand)` is called
**Then** it returns `None` without raising an exception

### R3: Markdown Parsing Rules

The parser extracts exemplars from blockquotes under known headers:

- `## Examples` / `### Good Example` / `### Good Examples` → `good_examples`
- `### What to Avoid` / `### Bad Example` / `### Bad Examples` → `bad_examples`
- Each `> ...` blockquote under a matching header becomes one exemplar entry
- Multiple blockquotes under one header → multiple entries
- Exemplars are stripped of `> ` prefixes and joined into paragraphs
- Maximum 3 good + 3 bad examples loaded (truncate if more — prompt budget)
- Each individual exemplar capped at 300 characters

### R4: Voice Context Extension

**Given** `_build_voice_context(brand)` returns a voice definition string AND `load_voice_exemplars(brand)` returns exemplars
**When** `grade_content()` builds the grading prompt
**Then** the voice context section includes both the definition AND exemplars:

```
## Brand Voice Definition (acme)
- Tone: bold
- Vocabulary: technical
- Rules: Never use passive voice

### On-Brand Examples
> We don't just ship features — we ship outcomes.

### Off-Brand Examples (avoid this style)
> Our industry-leading platform leverages cutting-edge AI...

Evaluate the brand_voice dimension against these guidelines and examples.
```

**Given** exemplars exist but voice definition is empty
**When** the context is built
**Then** exemplars are still included (they provide value independently)

**Given** no exemplars exist
**When** the context is built
**Then** behavior is identical to today (voice definition only, or empty string)

### R5: Token Budget

**Given** the combined voice context (definition + exemplars)
**When** it exceeds 1500 characters total
**Then** truncate exemplars first (keep definition intact), then truncate definition at 500 chars as today

The budget hierarchy:
1. Voice definition: up to 500 chars (existing behavior)
2. Good exemplars: up to 500 chars total
3. Bad exemplars: up to 500 chars total
4. Total cap: 1500 chars

### R6: Grading Prompt Integration

**Given** `grade_content(content, rubric, brand="acme")` where acme has voice exemplars
**When** the grading prompt is constructed
**Then** the exemplars appear in the prompt after the voice definition block

**Given** `grade_content(content, rubric)` (no brand)
**When** the prompt is constructed
**Then** no exemplars are included (backward compatible)

### R7: Healing Prompt Integration

**Given** content that fails `brand_voice` and enters the heal loop
**When** `_improve_content()` constructs the rewrite prompt with `brand="acme"`
**Then** the on-brand exemplars are included as targets:

```
### Voice Reference (target style)
> We don't just ship features — we ship outcomes.

### Voice Anti-Pattern (avoid this style)
> Our industry-leading platform leverages cutting-edge AI...
```

### R8: Template Update

**Given** the default template at `brands/_template/references/voice-guide.md`
**When** a new brand is created
**Then** the template includes clear parsing instructions as comments:

```markdown
## Examples

<!-- Add 1-3 on-brand examples as blockquotes. These are used by the
     grader to calibrate brand_voice scoring. -->

### Good Example

> [Your on-brand example here — a paragraph that nails your voice]

### What to Avoid

> [An off-brand example — content that violates your voice guidelines]
```

### R9: Backward Compatibility

**Given** any existing brand without voice-guide.md or with the empty template
**When** `grade_content()` or `heal_content()` is called with that brand
**Then** behavior is identical to today — no errors, no empty exemplar sections in prompts

## Non-Functional Requirements

- No new dependencies (only stdlib `re` for markdown parsing)
- No new files except tests — all code goes in existing `grader.py`
- Exemplar loading must be fast (single file read, no LLM calls)
- Total prompt addition from exemplars: ~200-400 tokens (well within context limits)

## Files Changed

| File | Change |
|------|--------|
| `src/brand_os/eval/grader.py` | Add `VoiceExemplars`, `load_voice_exemplars()`, extend `_build_voice_context()` |
| `src/brand_os/eval/heal.py` | Pass exemplars through to improvement prompt |
| `brands/_template/references/voice-guide.md` | Add parsing-friendly structure with HTML comments |
| `tests/eval/test_grader_exemplars.py` | New: test exemplar loading, formatting, prompt injection, edge cases |

