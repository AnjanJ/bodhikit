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
(simulated learner), `reflect-difficulty` (the learner names a hard concept,
retrieves it cleanly but rates it 3, and fails another outright: no `/forget`
may run, the clean retrieval is `correct` and promoted, the failure is an
observed `incorrect` — review finding 4, difficulty and confidence are not
forgetting), plus the **lifecycle group** (1.16.0): `learn-scaffold`
(/learn from the parent dir — scaffolds a second project, must preserve the
existing profile entry exactly), `plan-regenerate` (old plan archived, history
preserved), and `evaluate` (assessment + session + patterns + project-entry
refresh all land; run as `dev/eval/run-llm-evals.sh lifecycle`). These three
are the highest-write-count skills and ran on the honor system before 1.16.0.
Interactive teaching skills (`/teach`, `/pair`, `/continue`) still warrant a
manual dogfood pass on real learning data when their write paths change.

The grading group includes `grade-understand-band` (1.17.0): an accurate own-words explanation with an honest inability to write or choose an index must land at Bloom 1-2, never 3 — the 2-vs-3 line is the prerequisite gate's input. Read its recorded levels alongside `grade-apply-band` and `grade-genuine`: the three together are the rubric's low side, target, and top.

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
- `grade-jargon-heldout`, `grade-genuine-heldout`, `grade-apply-band-heldout`
  (2026-09-08) — the same three bands on *Connection pooling*, a topic the
  rubric never mentions. The three above share the rubric's own topic and
  anchor examples (the audit log, the `CREATE INDEX` line), so a pass there
  cannot tell transferable judgment from recognition of the anchors; a pass
  here can. Same assertions, via `BODHI_EVAL_CONCEPT`.
- `grade-terse`, `grade-second-language`, `grade-parrot-fails-probe`
  (2026-09-09, review finding on the ownership check) — the rubric's check 1
  used to record `partial` at level 1 the moment a learner could not produce
  a second phrasing, which fails a correct answer for being terse or
  non-native rather than for lacking understanding. Check 1 now accepts a
  correct prediction on a novel case as a second route to ownership.
  `grade-terse` scripts a short, correct, mechanics-only explanation that
  cannot rephrase but answers the probe right — must pass, Feynman gate set.
  `grade-second-language` scripts an accurate own-words analogy in rough
  grammar — must pass on the second-form route; grammar is not the signal.
  `grade-parrot-fails-probe` reuses the `grade-jargon` assertion: the
  original verbatim-textbook parrot, with its probe answer scripted wrong
  too, so a lucky guess cannot pass what the parrot anchor exists to catch.
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
- `continue-gate` — the complete-journey gate check the 2026-09-07 review
  asked for: `/continue` → option 1 → chained `/teach` at a module boundary
  must RUN `gate-check` (chaining used to skip it — the `--invoked-from`
  bypass) and the gate must FIRE on a module that only holds a seeded,
  never-graded concept (the membership bypass). Prep grades `Query planning`
  at Bloom 2 against the fixture's declared prerequisite line and seeds one
  concept into `Query Optimization`; asserts the gate ran, the gap was named
  in outcome terms, offer wording reached the learner, and carrying on wrote
  no unearned `correct`.
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

## Which scenarios have actually run (keep this table honest)

A scenario that has never been run against a live model is a hypothesis, not
a test. The run header prints the model; a pass certifies that executor only.

| Scenario | Group | Last live pass |
|---|---|---|
| migrate, forget, quiz, reflect | executor-discipline | 2026-09-03, all PASS (fable-5) on the 1.20.0 tree. Previously 2026-08-26, all PASS (fable-5), first live run of the 1.18.0 revision-sheet assertions on quiz/reflect |
| grade-apply-band, grade-genuine, grade-jargon | grading | 2026-09-03, single pass each, 3/3 PASS (fable-5) on the 1.20.0 tree: apply-band 3, genuine 5, jargon `partial`. Previously 2026-08-26, `BODHI_EVAL_RUNS=3` each, 9/9 PASS (fable-5) on the rubric rewrite with de-labelled learner scripts. Recorded levels had **no variance**: apply-band 3/3/3, genuine 5/5/5, jargon `partial` at 1 with the box held ×3. (The 1.14.0 sonnet-5 sweep had measured 3/3 vs 1/3 on the same tree.) |
| grade-jargon-heldout | grading (held-out) | 2026-09-08 (fable-5), first live run: graded `partial` at level 1, Feynman held, box held — the same verdict as on the rubric's own topic. The executor tracked the new concept as `connection-pooling`; the assertion now matches names on letters and digits only. |
| grade-genuine-heldout, grade-apply-band-heldout | grading (held-out) | 2026-09-08: both INCONCLUSIVE — the claude.ai usage limit hit mid-run before a review landed. Never yet passed live; hypotheses until re-run (`dev/eval/run-llm-evals.sh grading-heldout`). |
| grade-terse, grade-second-language, grade-parrot-fails-probe | grading | Added 2026-09-09 (review finding on the ownership check). Never yet run against a live model — hypotheses until run (`dev/eval/run-llm-evals.sh grading`). |
| grade-pushback, grade-misconception | grading | 2026-09-03, both PASS (fable-5), first run since the 1.19.0 rubric rewrite: pushback held at tested-bloom 1 through the escalation, misconception not passed. Previously 1.14.0 sweep (sonnet-5) |
| grade-understand-band | grading | 2026-09-04, single pass, PASS (fable-5): tested-bloom 2, gate threshold not crossed. Previously 2026-08-26, `BODHI_EVAL_RUNS=3`, 3/3 PASS (fable-5): tested-bloom 2/2/2, gate threshold not crossed (1.18.0 first run: 2) |
| teach-pretest | fidelity | 2026-09-04 PASS (fable-5) on the 1.20.0 tree (first attempt on 2026-09-03 was cut off by the usage limit). Previously 1.18.0 PASS (fable-5) |
| teach-hint-discipline | fidelity | 2026-09-04 PASS (fable-5) on the 1.20.0 tree: re-teach signal, artifacts shown, no unearned `correct`. Previously 1.18.0 PASS (fable-5) after the "hint turn shows its artifact" detector was anchored to line-initial `Hint N` (first sample matched the word in the closing recap) |
| continue-discovery | discovery | 1.14.1 (sonnet-5) |
| reflect-difficulty | executor-discipline | 2026-09-08 PASS (fable-5), first live run: no `/forget`, hard-and-low-rated clean retrieval promoted to Box 5, failed retrieval recorded `incorrect` at Box 1, sheet written. |
| continue-gate | fidelity | 2026-09-08 PASS (fable-5), first live run: `/continue` → option 1 → chained `/teach` ran `gate-check`, surfaced `Query planning` as a gap in outcome terms, learner carried on, no unearned correct. (The first attempt was refused by the API's safeguards before any turn ran — now labelled INCONCLUSIVE, not FAIL.) |
| kb-load | fidelity | 2026-09-04 PASS (fable-5) after a real catch: the first 1.20.0 sample printed "review recorded (Box 1 → 2, …)" in `/quiz`'s closing bookkeeping line — the skill had asked for "the box movement to report"; it now asks for the `nextReview` date, and the re-run is clean. Previously 1.18.0 (sonnet-5 first pass; then fable-5 ×4): KB always loaded. The bare-number detector caught one **real** miss ("Query planning — Box 1", read off the `due` output) — fixed by removing box/level numbers from `due` itself — and two recap false positives (now excluded). Learner-facing text clean in every sample after the reshape |
| learn-scaffold, plan-regenerate, evaluate | lifecycle | 1.18.0, first live runs, all PASS (fable-5). The first attempt at plan-regenerate/evaluate was cut off by the claude.ai usage limit — now labelled INCONCLUSIVE, not FAIL |

Update the row when you run a scenario. `BODHI_EVAL_RUNS=N` sweeps report a
rate; a single pass on a grading scenario is one sample.
