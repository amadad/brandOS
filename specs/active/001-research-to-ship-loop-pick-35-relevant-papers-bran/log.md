# Log: Research-to-ship loop: pick 3–5 relevant papers (brand governance, brand voice control, style consistency, evals for creative output) → extract 10 concrete enhancement ideas → implement ONE small, testable improvement (docs or code) in BrandOS.

## 2026-02-12
- Spec generated from backlog

### Iteration 1 - 04:05:33
Task: 1.1 Add `VoiceExemplars` dataclass to `src/brand_os/eval/grader.py`
Result: ✓ Complete

### Iteration 2 - 04:06:13
Task: 1.2 Implement `load_voice_exemplars(brand: str) -> VoiceExemplars | None` with markdown parsing
Result: ✓ Complete

### Iteration 3 - 04:07:16
Task: 1.3 Handle edge cases: missing file, empty file, no blockquotes, malformed markdown
Result: ✓ Complete

### Iteration 4 - 04:07:47
Task: 1.4 Enforce limits: max 3 good + 3 bad examples, 300 chars each
Result: ✓ Complete

### Iteration 5 - 04:08:07
Task: 2.1 Extend `_build_voice_context()` to accept optional `VoiceExemplars` parameter
Result: ✓ Complete

### Iteration 6 - 04:08:34
Task: 2.2 Format exemplars as `### On-Brand Examples` and `### Off-Brand Examples` sections
Result: ✓ Complete

### Iteration 7 - 04:09:39
Task: 2.3 Implement token budget: 500 chars definition + 500 chars good + 500 chars bad = 1500 total cap
Result: ✓ Complete

### Iteration 8 - 04:09:56
Task: 2.4 Update the instruction line to reference both guidelines and examples
Result: ✓ Complete
