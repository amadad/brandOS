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

### Iteration 9 - 04:10:18
Task: 3.1 Update `grade_content()` to call `load_voice_exemplars()` when `brand` is provided
Result: ✓ Complete

### Iteration 10 - 04:10:35
Task: 3.2 Pass exemplars to `_build_voice_context()`
Result: ✓ Complete

### Iteration 11 - 04:11:16
Task: 3.3 Verify prompt renders correctly with exemplars present and absent
Result: ✓ Complete

### Iteration 12 - 04:12:02
Task: 4.1 Update `_improve_content()` to load and inject exemplars when `brand` is provided
Result: ✓ Complete

### Iteration 13 - 04:12:34
Task: 4.2 Format exemplars as "Voice Reference (target style)" / "Voice Anti-Pattern" in healing prompt
Result: ✓ Complete

### Iteration 14 - 04:12:49
Task: 5.1 Rewrite `brands/_template/references/voice-guide.md` with machine-parseable structure
Result: ✓ Complete

### Iteration 15 - 04:13:01
Task: 5.2 Add HTML comments explaining how exemplars are used by the grader
Result: ✓ Complete

### Iteration 16 - 04:13:43
Task: 5.3 Verify the empty template returns `None` from `load_voice_exemplars()`
Result: ✓ Complete

### Iteration 17 - 04:14:04
Task: 6.1 Test `load_voice_exemplars()`: parses good/bad examples from well-formed voice-guide
Result: ✓ Complete

### Iteration 18 - 04:14:17
Task: 6.2 Test `load_voice_exemplars()`: returns None for missing/empty file
Result: ✓ Complete

### Iteration 19 - 04:14:36
Task: 6.3 Test `load_voice_exemplars()`: respects max 3 examples + 300 char limit
Result: ✓ Complete

### Iteration 20 - 04:14:54
Task: 6.4 Test `_build_voice_context()`: includes exemplars when provided
Result: ✓ Complete

### Iteration 21 - 04:15:45
Task: 6.5 Test `_build_voice_context()`: respects 1500 char total budget
Result: ✓ Complete

### Iteration 22 - 04:16:13
Task: 6.6 Test `grade_content()`: prompt includes exemplars when brand has voice-guide
Result: ✓ Complete
