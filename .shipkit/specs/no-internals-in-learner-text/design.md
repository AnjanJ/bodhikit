# Design: No state-engine internals in learner text

## Approach
Measure first, then fix at the voice. `assert_scenario.py`'s `main()` runs
`assert_no_internal_names` after every transcript scenario's own assertion, so every
scenario with a stream transcript counts the leak, not just `kb-load` and
`teach-vocabulary`. The fix is one voice rule in the `teaching-personality` KB, which every
skill and agent loads: text between tool calls reaches the learner, so it says what a step
means for them and never names the engine. Project-wide decision 0005 records why the
voice and not the engine.

## Decision: Run the name check centrally, in every transcript scenario   (→ REQ-1, REQ-2)

**Context.** `assert_no_internal_names` (541373d) runs only in `kb-load` and
`teach-vocabulary`. Re-running it over the 19 stream transcripts kept on 2026-11-06 found a
leak in `kind-intake-change`, whose assertion does not call it.

**Alternatives.**
1. Call it in `main()` after every `with_transcript` assertion.
2. Add a call to each scenario's assertion function.

**Case for 1.** One line covers all 32 transcript scenarios and every scenario added later.
It cannot be forgotten.

**Case against 1.** A scenario whose learner text has a legitimate reason to name an
internal would fail with no per-scenario opt-out. None does today: the 19 kept transcripts
hold 2 leaks, and both are real.

**Decision.** We chose option 1. The dispatch moves out of `main()` into
`assert_transcript_scenario`, so a test can run it. The calls inside `assert_kb_load` and
`assert_teach_vocabulary` stay, because their own tests call those functions directly. A
leak still fails at the first call.
**Falsifiability.** We would reverse this, adding a per-scenario opt-out, if a scenario's
correct behaviour requires naming an internal to the learner.
**Fired-if.** manual

## Decision: The voice rule, not the engine   (→ REQ-3, REQ-4)

Recorded project-wide as `.shipkit/decisions/0005-the-tutor-says-what-a-step-means.md`.
