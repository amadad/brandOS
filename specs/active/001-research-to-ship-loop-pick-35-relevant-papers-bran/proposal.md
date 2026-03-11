
# Proposal: Voice Exemplar Injection for Grading & Healing

## Problem

The BrandOS eval grader currently receives a compact text summary of brand voice attributes (tone, vocabulary, patterns, rules, avoid-phrases) capped at 500 characters. This is sufficient for directional guidance but insufficient for calibrated scoring. The `references/voice-guide.md` file — which contains concrete good/bad examples, vocabulary tables, and platform-specific notes — is never loaded or used anywhere in the codebase.

Research on LLM-as-judge evaluation (Prometheus, Kim et al. 2023; G-Eval, Liu et al. 2023) consistently shows that providing concrete exemplars alongside rubric criteria significantly improves scoring calibration and inter-rater reliability. Without exemplars, the grader must infer what "on-brand" means from abstract descriptors alone.

## Why Now

- **Score anchors** (spec 001) and **voice-anchored grading** (spec 002) are already shipped — they laid the foundation.
- The `voice-guide.md` template already has sections for good/bad examples — we just need to read them.
- This is the single highest-leverage improvement to brand_voice scoring accuracy with the least code change.

## Scope

### In Scope

- Load voice exemplars from `references/voice-guide.md` (or a brand-configurable path)
- Parse good and bad examples from the markdown
- Inject exemplars into the grading prompt as few-shot reference material
- Inject exemplars into the healing prompt so the improver has concrete targets
- Update `_template/references/voice-guide.md` with clearer structure for machine parsing

### Out of Scope

- Loading other reference docs (competitors.md, etc.)
- Sub-dimension decomposition of brand_voice
- Ensemble/multi-pass grading
- Embedding-based similarity checks
- Changes to the rubric schema itself

## Approach

1. Add `load_voice_exemplars(brand) -> VoiceExemplars` that reads `references/voice-guide.md`, extracts good/bad examples
2. Extend `_build_voice_context()` to accept and format exemplars (appended after voice definition, within token budget)
3. Update `grade_content()` and `_improve_content()` to pass exemplars through
4. Update the voice-guide template for reliable parsing (clear markdown headers with fenced quote blocks)
5. Tests: verify exemplars load, format correctly, appear in prompts, and degrade gracefully when absent

## Research Basis

| Paper | Key Technique | Application |
|-------|--------------|-------------|
| Prometheus (Kim et al., 2023) | Reference-answer calibrated scoring | Exemplars at different quality levels calibrate the judge |
| G-Eval (Liu et al., 2023) | Chain-of-thought + form-filling | Observations before scoring improve consistency |
| JudgeLM (Zhu et al., 2023) | Pairwise comparison with references | Contrastive good/bad examples sharpen discrimination |
| INSTRUCTSCORE (Xu et al., 2023) | Aspect-specific rubrics + examples | Per-dimension exemplars produce more reliable scores |
| PRD (Li et al., 2023) | Multi-evaluator voting | Future: ensemble mode for high-stakes content |

**Enhancement ideas extracted** (10 total, implementing #1):

1. **Voice exemplar injection** — load good/bad examples into grading prompts ← THIS SPEC
2. Contrastive prompting — explicitly explain why bad examples fail
3. Chain-of-thought grading — force observations before scores
4. Sub-aspect decomposition of brand_voice into formality/emotion/jargon/structure
5. Quantitative pre-filters (vocabulary overlap, readability) before LLM grading
6. Ensemble voting — grade 3x, flag high-variance dimensions
7. Pairwise comparison mode — rank candidate against exemplars
8. Platform-specific exemplars — different voice calibration per channel
9. Temporal drift tracking — track voice scores over time, alert on regression
10. Learnings feedback loop — inject weak_dimensions into copy generation constraints

## Risk

Low. Changes are additive and backward-compatible — when no voice-guide exists or contains no examples, behavior is identical to today.

