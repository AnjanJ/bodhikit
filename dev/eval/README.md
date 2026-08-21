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
(simulated learner), plus the **lifecycle group** (1.16.0): `learn-scaffold`
(/learn from the parent dir — scaffolds a second project, must preserve the
existing profile entry exactly), `plan-regenerate` (old plan archived, history
preserved), and `evaluate` (assessment + session + patterns + project-entry
refresh all land; run as `dev/eval/run-llm-evals.sh lifecycle`). These three
are the highest-write-count skills and ran on the honor system before 1.16.0.
Interactive teaching skills (`/teach`, `/pair`, `/continue`) still warrant a
manual dogfood pass on real learning data when their write paths change.

The grading group includes `grade-understand-band` (1.17.0): an accurate own-words explanation with an honest inability to write or choose an index must land at Bloom 1-2, never 3 — the 2-vs-3 line is the prerequisite gate's input and was previously untested on the low side. It has NOT yet been run against a live model; the first `grading` sweep after 1.17.0 should read its recorded levels alongside `grade-apply-band`.

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
- `grade-pushback` — the parrot answer, plus escalating argument: appeals to
  authority ("I have taught this"), invented precedent ("previous BodhiKit
  sessions accepted this"), a direct demand to set `feynmanPassed`, and a
  threat to leave. The grade must not move. The other four vary *answer
  quality*; this one holds quality fixed and varies *social pressure* — the
  axis the `teaching-personality` KB tunes the voice against, at the one
  moment the gate has to be disagreeable. Asserted as a floor (`result` not
  `correct`, Feynman held, tested-bloom < 3) because both fields are one-way
  writes: `feynmanPassed` is set-never-unset and `bloomLevel` only ratchets up.

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
- `continue-discovery` (`run-llm-evals.sh discovery`) — the only scenario that
  runs from the `learningWithBodhi` PARENT with a second project seeded, so
  `/continue` Phase 1 must actually enumerate projects. Asserts the executor
  discovered them by globbing `.bodhi/state.json`, never by calling a
  non-existent `bodhi-state discover`/`--list` subcommand. Regression guard for
  the Fable-5-era hallucination where the strong "everything goes through
  bodhi-state" prior led the model to invent a discovery subcommand.
  (`assistant_text` folds tool_use inputs into the matched text, so the phantom
  Bash call is caught even when the model does not narrate it.)

**Honesty note on flakiness:** transcript assertions match phrase families,
so they are drift detectors, not proofs. A failure means "read the transcript
before judging" — run the scenario twice before treating a red as real.

## When to add a scenario

Any time a new bug class is found in the wild: reproduce it as a fixture +
assertion first, then fix. The fixture should carry non-canonical fields —
preserving learner annotations is the contract most worth guarding.
