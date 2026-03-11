
# Proposal: Voice-Anchored Grading — Closing the Brand Voice Gap in Evaluation

## Why We're Doing This

### The Problem

BrandOS evaluates content against a `brand_voice` rubric dimension, but the grader has no access to the brand's actual voice definition. `grade_content()` in `src/brand_os/eval/grader.py:49` receives a rubric and content — it never sees the brand's tone, vocabulary, patterns, rules, or avoid_phrases from `brand.yml`. The LLM judge is asked "Does it match the brand voice?" without being told what that voice *is*.

This means:
- The `brand_voice` dimension score is based on the LLM's generic notion of "brand voice consistency," not the specific brand's voice
- Two brands with opposite voice definitions would get similar `brand_voice` scores for the same content
- The healing loop (`heal.py`) can't fix voice drift because it also lacks the voice definition
- The learning system (`learnings.py`) tracks `brand_voice` as a weak dimension but can't identify *which* voice attributes are failing

### Research Grounding

This improvement draws from five areas of published research:

1. **LLM-as-Judge with Reference Grounding** (Zheng et al., 2023 — "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"): Judges perform better when given concrete reference criteria rather than abstract instructions. Position bias and vagueness degrade scoring quality. BrandOS currently suffers from the exact vagueness problem — the judge gets criteria like "Consistent tone" without defining what tone.

2. **Style Transfer Evaluation** (Reif et al., 2022 — "A Recipe for Arbitrary Text Style Transfer with Large Language Models"): Effective style evaluation decomposes style into measurable attributes (formality, sentiment, specificity). BrandOS already has a decomposed voice model (`tone`, `vocabulary`, `patterns`, `rules`) but doesn't pipe it into evaluation.

3. **Rubric-Enhanced Grading** (Kim et al., 2024 — "Prometheus: Inducing Fine-grained Evaluation Capability in Language Models"): LLM judges significantly improve when rubrics include scoring criteria with positive/negative examples specific to each level. BrandOS has criteria lists but no level-specific descriptions.

4. **Brand Voice Consistency in NLG** (Jain et al., 2023 — survey on controllable text generation): Maintaining brand voice is a constrained generation problem. Post-hoc evaluation is weaker than in-generation constraints, but combining both (generate with voice → evaluate against voice) is strongest.

5. **Calibration of LLM Evaluators** (Liu et al., 2023 — "Calibrating LLM-Based Evaluator"): Uncalibrated LLM judges exhibit score drift over time and inconsistency across prompts. Anchoring scores to concrete examples (reference-based evaluation) significantly improves inter-rater reliability.

### The Core Insight

All five research areas converge on one principle: **LLM judges need concrete, specific reference material to produce reliable scores.** BrandOS has the reference material (voice definitions in `brand.yml`) and has the judge (`grader.py`) — they're just not connected.

### 10 Enhancement Ideas Extracted

From the research, these are 10 concrete improvements that could apply to BrandOS:

1. **Voice-anchored grading** — inject brand voice config into grader prompt ← IMPLEMENTING THIS ONE
2. **Few-shot exemplars in rubric** — add example content at each score level (1, 3, 5) per dimension
3. **Pairwise comparison grading** — grade content by comparing against a known-good reference piece
4. **Sub-dimension decomposition** — split `brand_voice` into tone, vocabulary, pattern-match sub-scores
5. **Voice fingerprinting** — embed brand voice as a style vector; score cosine similarity
6. **Pre-generation voice prompt injection** — build system prompts from brand voice for `generate_copy()`
7. **Multi-judge consensus** — run 3 grading passes, take median to reduce variance
8. **Temporal voice drift tracking** — plot `brand_voice` scores over time to detect systematic drift
9. **Contrastive evaluation** — show the judge examples of on-brand AND off-brand content for calibration
10. **Voice-specific healing** — when `brand_voice` fails, rewrite targeting specific voice attributes (not generic improvement)

## Scope

### In Scope

- **Inject brand voice context into the grading prompt** so the LLM judge evaluates against the actual brand voice definition
- **Pass brand name through the grading pipeline** from `grade_content()` through `heal_content()` and `learnings.py`
- **Tests** for the new behavior

### Out of Scope

- Changing the rubric schema or adding new dimensions
- Modifying content generation (`produce/copy.py`)
- Persona-to-brand integration
- New CLI commands or flags
- Voice drift tracking over time (future work, builds on this)
- Multi-judge or calibration systems

## Approach

**Minimal change, maximum impact.** The grader already accepts a `context` parameter (string) that gets appended to the prompt. Today, callers either pass `None` or a brief string. The fix:

1. Add a `brand` parameter to `grade_content()` and `heal_content()`
2. When `brand` is provided, load the brand's voice config and format it as structured context
3. Inject this context into the grading prompt so the `brand_voice` dimension is evaluated against the actual definition
4. The healing loop also receives this context so it can fix voice-specific issues
5. Wire the brand parameter through learnings logging

No new files. No new dependencies. No schema changes. Three source files modified (`grader.py`, `heal.py`, `learnings.py`), one new test file.

