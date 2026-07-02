# dev/eval — BodhiKit's two-layer test harness

The 1.10.x dogfood arc proved there are two distinct failure surfaces, so
there are two distinct test layers:

## Layer 1: deterministic (free, run on every change)

```
python3 dev/eval/test_bodhi_state.py
```

Unit tests for `scripts/bodhi-state` — Leitner math, the bloomLevel ratchet,
counter rules, sessionHistory vocabulary enforcement, unknown-field
preservation, migration idempotency + backup, gate verdicts (including the
1.11.0 recency rule), mastery formula, calibration. `dev/check.sh` runs this
suite automatically.

## Layer 2: LLM evals (costs tokens, run before tagging)

```
dev/eval/run-llm-evals.sh           # all scenarios
dev/eval/run-llm-evals.sh migrate   # one scenario
```

Copies `fixtures/v2-project/` (a realistic mid-journey learning project with
v2 tracking files and non-canonical learner annotations) into a temp dir,
runs a skill headlessly via `claude -p --plugin-dir`, then asserts on the
resulting **file state** with `assert_scenario.py`. This catches the
executor-discipline regression class (writes described but not performed,
fields silently dropped, invented vocabulary) that grep-based lint cannot
see by design — the automated successor to the manual dogfood passes
documented in the 1.10.7–1.10.13 CHANGELOG entries.

Executor-discipline scenarios: `migrate`, `forget`, `quiz`, `reflect`
(simulated learner). Interactive teaching skills (`/teach`, `/pair`,
`/continue`) still warrant a manual dogfood pass on real learning data when
their write paths change.

## Layer 3: grading-calibration + transcript-fidelity evals (1.12.0)

The deterministic layer guarantees the file *mechanics*; these guarantee the
*judgment* feeding them. Same harness, two new assertion classes:

**Grading calibration** (`run-llm-evals.sh grading`) — scripted learner
answers of controlled quality, asserted against honest grading bands on the
resulting file state:

- `grade-jargon` — a fluent verbatim-textbook parrot must not be graded
  `correct` and must not pass the Feynman gate (fluency-without-understanding).
- `grade-genuine` — a clean own-words explanation with trade-offs must earn
  `correct`, tested-bloom in the 4-5 band, the Feynman gate, and the box promotion.
- `grade-apply-band` — mechanics + usage but explicitly no trade-offs must
  land tested-bloom 3-4: 5-6 is grade inflation, 0-2 ignores demonstrated
  application. (Bands, not exact values — grading is legitimately a judgment.)
- `grade-misconception` — a confident own-words explanation with a persisting
  misconception must not pass. Confidence is not understanding.

This class doubles as the **model-drift detector**: the mastery formula is
exactly as trustworthy as these gradings, and every model change can shift
them under identical prompts. Rerun `grading` on every model change, not just
before tags.

**Transcript fidelity** (`run-llm-evals.sh fidelity`) — protocol gates with no
file trace, asserted with wording-tolerant regexes over the full stream-json
assistant transcript:

- `teach-pretest` — first-exposure `/teach` must open with the ungraded
  guess-first question before the explanation, and must not record it.
- `teach-hint-discipline` — after 3 failed hints and a demand for the full
  solution: re-teach signal present, no Hint 4, and no unearned `correct` in
  the tracking files.

**Honesty note on flakiness:** transcript assertions match phrase families,
so they are drift detectors, not proofs. A failure means "read the transcript
before judging" — run the scenario twice before treating a red as real.

## When to add a scenario

Any time a new bug class is found in the wild: reproduce it as a fixture +
assertion first, then fix. The fixture should carry non-canonical fields —
preserving learner annotations is the contract most worth guarding.
