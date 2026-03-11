
# Proposal: Produce-Eval Gate — Auto-Grade and Heal Content at Generation Time

## Why We're Doing This

### The Problem

BrandOS generates content (`produce/copy.py`) and evaluates content (`eval/grader.py`) — but these are completely disconnected. Today's flow:

1. `brandos produce copy "topic" --brand acme` → raw LLM output
2. (Manual) `brandos eval grade --brand acme` → score + feedback
3. (Manual) `brandos eval heal --brand acme` → improved version
4. (Manual) `brandos produce queue` → add to publish queue

Steps 2–3 never happen in practice. Content goes from generation straight to queue (in `explore_cmd`) without any quality check. The eval system — voice-anchored grading, score anchors, self-healing loop — sits unused during the most critical moment: when content is created.

This means:
- Off-brand content enters the publish queue unchecked
- The heal loop's iterative improvement is never applied to fresh content
- Eval learnings are logged but never gate content quality
- The `explore` command queues content at any quality level

### Research Grounding

This improvement draws from five areas of published research:

1. **Self-Refine** (Madaan et al., 2023 — "Self-Refine: Iterative Refinement with Self-Feedback"): LLMs that generate → critique → refine in a loop produce significantly higher quality output than single-pass generation. The key insight: the same model that generates content can evaluate and improve it when given structured feedback. BrandOS already has the refine loop (`heal.py`) — it just isn't wired into generation.

2. **Constitutional AI** (Bai et al., 2022 — Anthropic): Systems that evaluate output against explicit principles before releasing it produce safer, more aligned results. BrandOS's rubric dimensions + red flags are exactly these principles — they just aren't applied as a gate.

3. **LLM-as-Judge with Reference Grounding** (Zheng et al., 2023 — "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"): Judges with concrete reference criteria outperform abstract evaluation. The previous spec (voice-anchored grading) implemented this — now the grading quality is high enough to trust as an automated gate.

4. **Style Over Substance Bias** (Li et al., 2024): LLM judges favor longer, more verbose output. An iterative heal loop can cause content inflation — each iteration makes content longer. Platform-aware length constraints must be enforced to prevent this.

5. **CriticBench** (Wang et al., 2024): Separating critique from correction improves both. BrandOS already separates these (grade → heal), which is the ideal architecture. Wiring them together maintains this separation while making it automatic.

### 10 Enhancement Ideas Extracted

From the research and codebase analysis, 10 concrete improvements:

1. ~~Voice-anchored grading~~ — DONE (previous spec)
2. **Auto-grade gate in produce flow** — grade content after generation, reject if below threshold ← IMPLEMENTING THIS ONE
3. **Auto-heal in produce flow** — when grade fails, run heal loop before returning ← IMPLEMENTING THIS ONE
4. **Platform-aware length guardrails** — prevent content inflation during heal iterations ← IMPLEMENTING (as part of #3)
5. Few-shot exemplars in rubric — add example content at each score level per dimension
6. Sub-dimension decomposition — split `brand_voice` into tone, vocabulary, pattern-match sub-scores
7. Multi-judge consensus — run 3 grading passes, take median to reduce variance
8. Temporal voice drift tracking — plot `brand_voice` scores over time to detect systematic drift
9. Contrastive evaluation — show the judge on-brand and off-brand examples for calibration
10. Eval-driven learnings injection — auto-load `learnings.json` into produce prompts (currently manual in `explore` only)

## Scope

### In Scope

- **Add `--eval` flag to `brandos produce copy`** that grades output and returns score alongside content
- **Add `--heal` flag to `brandos produce copy`** that auto-heals content until it passes (implies `--eval`)
- **A `produce_and_eval()` function** that wires `generate_copy()` → `grade_content()` → `heal_content()` into a single pipeline
- **Platform-aware length enforcement** in the heal loop to prevent content inflation
- **Wire into `explore` command** so queued content is graded before enqueueing
- **Tests** for the new pipeline

### Out of Scope

- Changing the eval rubric schema or dimensions
- Modifying `generate_copy()` internals (it stays as-is)
- Image or video evaluation
- Thread evaluation (different structure, future work)
- New rubric dimensions (platform-specific, SEO, etc.)
- Multi-judge consensus or calibration systems

## Approach

**Compose existing pieces, don't rewrite them.** All the building blocks exist:

1. `generate_copy()` → returns `{main, variants, hashtags, platform}`
2. `grade_content()` → returns `GradeResult` with scores + feedback
3. `heal_content()` → returns `{final_content, final_score, iterations, history}`

The fix:

1. Add a `produce_and_eval()` function in `produce/copy.py` that chains: generate → grade → (optionally) heal → return enriched result
2. Add `--eval` and `--heal` flags to `copy_cmd` in `produce/cli.py`
3. Update `explore_cmd` to use eval gate before enqueueing (respects `--no-queue` for failures)
4. Add platform character limits as a post-heal validation (truncation/rejection, not prompt hacking)
5. Tests for the pipeline, including edge cases (content passes first try, content never passes, heal improves score)

No new files beyond a test file. Three source files modified (`produce/copy.py`, `produce/cli.py`, one test file). The eval modules (`grader.py`, `heal.py`) are used as-is.

