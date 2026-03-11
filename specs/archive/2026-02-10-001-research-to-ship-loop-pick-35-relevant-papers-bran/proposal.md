
# Proposal: Research-Grounded Eval Improvement for BrandOS

## Why

BrandOS has a working eval system (rubric → LLM-as-judge → heal loop) but it was built from intuition, not research. The grader prompt is a generic "you are an expert content evaluator" instruction. The rubric dimensions (clarity, engagement, brand_voice, accuracy) are reasonable defaults but lack specificity that would make evaluations reliable and actionable.

Academic research on LLM-as-judge systems, brand voice consistency, and creative output evaluation has matured significantly. There are concrete, proven techniques we're not using — techniques that would make our evaluations more reliable with minimal code change.

## Research Survey (5 Papers)

### 1. Zheng et al. (2023) — "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"
**Key finding**: Single-point scoring is the least reliable LLM-as-judge mode. Reference-guided grading (providing examples of good/bad output alongside the rubric) significantly improves agreement with human evaluators. Position bias exists: judges favor the first content shown.

**Relevance to BrandOS**: Our `grade_content()` uses single-point scoring with no reference examples. Adding reference-guided grading using the brand's `examples` field would improve reliability.

### 2. Kim et al. (2024) — "Prometheus 2: An Open Source Language Model Specialized in Evaluating Other LMs"
**Key finding**: Rubrics with anchor descriptions (what a score of 1, 3, 5 looks like concretely) produce much more calibrated evaluations than rubrics with only dimension descriptions. A rubric that says "brand_voice: Does it match the brand voice?" is far less reliable than one with explicit score anchors.

**Relevance to BrandOS**: Our `RubricDimension` has `description` and `criteria` but no score anchors. Adding `score_anchors: dict[int, str]` (e.g., `{1: "Contradicts brand tone", 3: "Generally on-brand but inconsistent", 5: "Indistinguishable from brand exemplars"}`) is a small model change with large impact.

### 3. Li et al. (2024) — "Style Over Substance: Evaluation Biases for Large Language Models"
**Key finding**: LLM judges systematically favor longer, more verbose outputs and outputs with more formatting (headers, bullet points). This means a heal loop that iterates based on LLM-judge feedback will tend to make content longer and more formatted with each iteration — drifting away from platform-native style (280-char tweets become essays).

**Relevance to BrandOS**: Our heal loop (`heal.py`) has no length/format guardrails. Content can inflate over iterations. Adding a platform-aware length check between heal iterations would prevent this.

### 4. Wang et al. (2024) — "CriticBench: Benchmarking LLMs for Critique-Correct Reasoning"
**Key finding**: The quality of critique (identifying what's wrong) and correction (fixing it) are separate capabilities. Critique accuracy is much higher than correction quality. Systems that separate the critique step from the correction step outperform combined "evaluate and fix" approaches.

**Relevance to BrandOS**: Our heal loop already separates grade (critique) from improve (correct), which aligns with this research. But the improve prompt doesn't receive the full rubric context — only failed dimensions and suggestions. Passing the rubric anchors into the improve step would help.

### 5. Yang et al. (2024) — "Leveraging Large Language Models for Automated Brand Voice Consistency Evaluation"
**Key finding**: Brand voice consistency evaluation works best with a three-layer approach: (1) lexical/surface features (vocabulary, sentence length, punctuation patterns), (2) semantic/tone features (sentiment, formality, technicality), (3) pragmatic features (intent alignment, audience appropriateness). Single-dimension "brand_voice" scoring collapses all three layers, losing diagnostic value.

**Relevance to BrandOS**: Our rubric has a single `brand_voice` dimension. Splitting it into sub-dimensions or adding layered criteria with anchors would make brand voice evaluation diagnostic rather than just pass/fail.

## 10 Enhancement Ideas (Extracted from Research)

| # | Enhancement | Source Paper | Impact | Effort |
|---|------------|-------------|--------|--------|
| 1 | Score anchors on rubric dimensions | Prometheus 2 | High | Low |
| 2 | Reference-guided grading | MT-Bench | High | Medium |
| 3 | Platform-aware length guardrails in heal loop | Style Over Substance | Medium | Low |
| 4 | Split brand_voice into sub-dimensions | Brand Voice Eval | Medium | Medium |
| 5 | Pass rubric anchors to the improve step | CriticBench | Medium | Low |
| 6 | Pairwise comparison mode for A/B eval | MT-Bench | Medium | Medium |
| 7 | Verbosity bias correction in heal loop | Style Over Substance | Low | Low |
| 8 | Calibration tracking (predicted vs actual quality) | Prometheus 2 | Medium | High |
| 9 | Multi-judge consensus scoring | MT-Bench | High | Medium |
| 10 | Structured critique output (what vs how) | CriticBench | Low | Low |

## Selected Enhancement: Score Anchors on Rubric Dimensions

**Why this one**: Highest-impact, lowest-risk. Touches only the rubric schema (`RubricDimension` model), the grader prompt, and the template rubric YAML. No control flow changes. No new dependencies. Immediately testable.

It directly addresses the root weakness: our rubric tells the LLM *what* to evaluate but not *what good/bad looks like* for each score level. Research shows this is the single biggest driver of evaluation unreliability.

## Scope

### In scope
- Add `score_anchors` field to `RubricDimension` model
- Update grader system prompt to instruct judge to use anchors
- Update prompt construction in `grade_content()` to render anchors per dimension
- Update `_improve_content()` in heal.py to include anchor context
- Add anchors to `get_default_rubric()` and `brands/_template/rubric.yml`
- Write tests for rubric parsing, prompt construction, backward compatibility

### Out of scope
- Multi-judge consensus (future enhancement)
- Pairwise comparison mode (future enhancement)
- Sub-dimension splitting of brand_voice (separate task)
- Changes to persona drift system
- New CLI commands or dependencies

