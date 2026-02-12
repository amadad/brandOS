
# Spec: Voice-Anchored Grading

## Overview

When `grade_content()` receives a `brand` parameter, it loads that brand's voice configuration and injects it into the grading prompt as structured context. This gives the LLM judge concrete criteria for the `brand_voice` dimension.

## Requirements

### R1: Brand Voice Context Builder

A helper function that takes a brand name and returns a formatted string containing the voice definition.

**Given** a brand "acme" with voice config:
```yaml
voice:
  tone: bold
  vocabulary: technical
  patterns: ["Start with a provocative question", "Use data points"]
  rules: ["Never use passive voice", "Keep sentences under 20 words"]
  avoid_phrases: ["industry-leading", "synergy", "leverage"]
```
**When** the voice context is built
**Then** it returns a structured string like:
```
## Brand Voice Definition (acme)
- Tone: bold
- Vocabulary: technical
- Speech patterns: Start with a provocative question, Use data points
- Rules: Never use passive voice, Keep sentences under 20 words
- Avoid phrases: industry-leading, synergy, leverage

Evaluate the brand_voice dimension against these specific guidelines.
```

**Given** a brand with an empty/minimal voice config
**When** the voice context is built
**Then** it returns an empty string (no noise added to the prompt)

**Given** an invalid or nonexistent brand name
**When** the voice context is built
**Then** it returns an empty string and does not raise an exception

### R2: grade_content Accepts Brand Parameter

**Given** `grade_content(content, rubric, brand="acme")`
**When** brand is provided
**Then** the brand's voice context is loaded and appended to the grading prompt alongside any existing `context` parameter

**Given** `grade_content(content, rubric)` (no brand)
**When** brand is not provided
**Then** behavior is identical to current implementation (backward compatible)

**Given** `grade_content(content, rubric, context="some context", brand="acme")`
**When** both context and brand are provided
**Then** both are included in the prompt — existing context is preserved, voice context is appended after it

### R3: heal_content Accepts Brand Parameter

**Given** `heal_content(content, rubric, brand="acme")`
**When** content fails the `brand_voice` dimension
**Then** the improvement prompt includes the brand voice definition so the LLM can fix voice-specific issues

**Given** `heal_content(content, rubric)` (no brand)
**When** brand is not provided
**Then** behavior is identical to current implementation

### R4: Voice Context in Healing Prompt

**Given** content that fails `brand_voice` with score 0.4
**When** `_improve_content()` is called during healing
**Then** the improvement prompt includes:
- The brand voice definition
- The specific voice feedback from the failed dimension
- Instruction to rewrite matching the brand voice attributes

### R5: Learnings Log Includes Brand

**Given** `log_evaluation(brand, content, grade_result)` is called
**When** the grade was performed with brand voice context
**Then** the logged entry includes a `brand` field (already present in the function signature — no change needed, just verification)

### R6: Backward Compatibility

**Given** any existing caller of `grade_content()`, `heal_content()`, or `quick_grade()`
**When** they do not pass a `brand` parameter
**Then** behavior is unchanged — no errors, same results

## Non-Functional Requirements

- No new dependencies
- No new files except the test file
- Voice config loading must handle missing/malformed brand gracefully (return empty string, don't crash)
- The voice context string should be under 500 characters to avoid prompt bloat

