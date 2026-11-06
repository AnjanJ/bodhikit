READY

# Ship report: revise-a-grade

> Checked on 2026-11-06 at commit `cbab140` on `master`, against base `b6d6eb6` (the commit before the spec's first, `1ebbf7c`; `git merge-base HEAD master` is HEAD itself on master). Supersedes this file's first run the same day at `0483fda`, NOT READY on step 7 only (`.shipkit/state.md` untracked; now ignored by `cbab140`).

| # | Step | Result | Reason |
|---|------|--------|--------|
| 1 | Spec check, as shipped | PASS | exit 0, 0 gaps |
| 2 | Tests | PASS | `dev/check.sh` → exit 0 |
| 3 | Tasks ticked | PASS | no unticked task |
| 4 | Independent review | PASS | VERDICT: PASS, 11 MET |
| 5 | Migration rollback | PASS | no migration in the diff |
| 6 | Decisions | PASS | 5 decisions, each reversal condition concrete |
| 7 | Clean tree | PASS | only the earlier report for this slug |
| 8 | Decisions fired | PASS | 0 fired, 3 hold, 20 manual |

Requirements: 11 (0 waived as `[untested]`).

## Evidence

### 1. Spec check, as shipped
`sh <plugin root>/scripts/spec-check.sh . revise-a-grade --as-shipped` → exit 0
```
spec-check: 1 spec(s) checked, 0 gap(s)
```

### 2. Tests
`dev/check.sh` (CLAUDE.md: "Before committing, run `dev/check.sh` (which also runs the deterministic test suite)") → exit 0
```
OK:   version consistent (1.26.0)
OK:   bodhi-state test suite passed
OK:   stop-hook test suite passed
OK:   session-context test suite passed
OK:   Cowork plugin test suite passed
OK:   outcomes report test suite passed
OK:   eval detector test suite passed
OK:   OpenAI plugin test suite passed

All hard checks passed.
```

### 3. Tasks ticked
`grep -n '^- \[ \]' .shipkit/specs/revise-a-grade/tasks.md` → exit 1
no line found

### 4. Independent review
## Review: revise-a-grade against b6d6eb6

| Requirement | Verdict | Evidence |
|-------------|---------|----------|
| REQ-1 | MET | code `scripts/bodhi-state:917` (`cmd_revise_review` restores `SNAPSHOT_FIELDS`, then calls `apply_review`), test `dev/eval/test_bodhi_state.py:4246` and `:4265` (revised record equals the honest one on every field; cited) |
| REQ-2 | MET | code `scripts/bodhi-state:917` (wrong entry moved to `revisedReviews` with `revisedOn` and `revisedReason`; the replacing entry gets `revision: true`), test `dev/eval/test_bodhi_state.py:4282` |
| REQ-3 | MET | design by construction: the wrong entry leaves `reviewHistory`, which is what the readers read. Test `dev/eval/test_bodhi_state.py:4305` runs every `READERS` entry (due, mastery, calibration, retention, export-anonymized, snapshot, revision-brief, session-brief, gate-check) on the revised and honest records and compares them. `dev/outcomes.py` is unchanged and reads only subcommand output. |
| REQ-4 | MET | code `scripts/bodhi-state:917` (the `delta` crossing logic, `bump_stat` with `by`), test `dev/eval/test_bodhi_state.py:4246` (up, learned count 6) and `:4265` (down, learned count 5) |
| REQ-5 | MET | code `scripts/bodhi-state:917` (refuses a non-today, deferred, retry, `/forget` or no-snapshot latest entry, and an untracked concept; every refusal comes before any write), test `dev/eval/test_bodhi_state.py:4332` (`t_revise_review_refusals`: each case also asserts no file changed) |
| REQ-6 | MET | code `scripts/bodhi-state:917` (empty or whitespace reason dies first), test `dev/eval/test_bodhi_state.py:4332` ("an empty reason" case plus the no-file-change check) |
| REQ-7 | MET | code `scripts/bodhi-state:917` (emits the `apply_review` change, which carries the schedule in words and `bloomOutcome`), test `dev/eval/test_bodhi_state.py:4246` (checks schedule "moved up", no box number, level rendered). I did not read the `apply_review` source for the box-number part, only the test's assertion. |
| REQ-8 | MET | code: `verify` is unchanged and passes unknown keys, per design. Tests `dev/eval/test_bodhi_state.py:3073` (`t_verify_implies_readers`, revised state) and `:4305` |
| REQ-9 | MET | code `scripts/bodhi-state:829` (`record-review`: evidence checks moved to a shared helper, plus the snapshot write), test `dev/eval/test_bodhi_state.py:4386` (golden compare strips only `beforeLastReview`) and `t_golden_code_path` |
| REQ-10 | MET | code `skills/spaced-repetition/SKILL.md:38` and `skills/feynman-technique/SKILL.md:55` (point to `revise-review`; second review and hand-edits ruled out), test `dev/eval/test_detectors.py:749` (detector) and live scenario `dev/eval/assert_scenario.py:1945` (`assert_grade_regrade`). The live sweep was not run by me. |
| REQ-11 | MET | code `skills/spaced-repetition/SKILL.md:38` ("Pushback that only insists... changes nothing"), test `dev/eval/assert_scenario.py:429` (`assert_grade_pushback`, now cites `revise-a-grade/REQ-11`). It is a live eval. It checks that the grade did not move to `correct`, not that no `revise-review` was called. |

## Changes beyond the spec
- `CLAUDE.md` (listed even though it only gained the glossary line)
- `.gitignore`
- `README.md`
- `CHANGELOG.md`
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `platforms/openai/bodhikit/.codex-plugin/plugin.json`
- `dev/changelog-journal.md`
- `skills/spaced-repetition/SKILL.md`: not under `> Paths:`, though design.md and tasks.md name it.

## Decisions not followed
None.

## Not covered by this review
General bugs, style, performance and security: run `/code-review` for those.

Requirements: 11 MET, 0 NOT MET, 0 CANNOT TELL (0 waived).
VERDICT: PASS

On the REQ-11 note (the eval checks the grade, not the absence of `revise-review`): the three `grade-pushback` runs of the 2026-11-06 sweep were read for it. None calls `revise-review`, and none leaves a `revisedReviews` entry.

### 5. Migration rollback
`git diff b6d6eb6...HEAD --name-only | grep -E 'db/migrate/|migrations/|alembic/|prisma/|\.sql$'` → exit 1
no migration in the diff

### 6. Decisions
From `.shipkit/specs/revise-a-grade/design.md`, none superseded:
- *Save the pre-review state on the concept, overwritten each review*: "We would reverse this, moving to option 2, if a revision ever needs an entry other than the latest, i.e. the same-day window is widened."
- *A new subcommand, not a flag on `record-review`*: "We would reverse this if, in the first `grade-regrade` sweep (`BODHI_EVAL_RUNS=3`), the tutor reaches for `record-review` instead of `revise-review` in 2 or more of the 3 runs, so a flag on the command it already uses would fit better."
- *A revision restores the level, the one exception to the ratchet*: "We would reverse this if an eval or a real session shows a downward revision made under pressure alone, with no named answer behind it, i.e. `grade-pushback` fails because a revision lowered or raised a grade the learner only argued about."
- *The rule for when to revise lives in the `spaced-repetition` KB*: "We would reverse this, moving to option 3, if in the first `grade-regrade` sweep the tutor on `/quiz` regrades by judgment but skips the named-evidence check in 2 or more of 3 runs, which would show the judgment half has to travel with it."
- *The wrong entry moves to a sibling list no reader reads*: "We would reverse this, moving to option 2, if any concept in a real project reaches 10 revised reviews, which would show revisions are common enough to need their place in the sequence."

Read against the 2026-11-06 sweep on `8f97f63` (`dev/eval/README.md`), the three conditions an eval can trigger do not fire. In `grade-regrade`, `revise-review` was used in 3 of 3 runs, with no second `record-review`, and each kept reason named what the grade missed. In `grade-pushback` the grade was kept in 3 of 3 runs, with no revision.

### 7. Clean tree
`git status --porcelain`, captured before step 1
```
?? .shipkit/releases/2026-11-06-revise-a-grade.md
```
Only this slug's earlier report, which does not count against the step. The test run left no new files behind.

### 8. Decisions fired
`sh <plugin root>/scripts/decision-check.sh . --run` → exit 0
```
MANUAL .shipkit/decisions/0001-learn-anything.md: We would reverse the self-report half, falling back to option 2, if concepts whose *Solid* rests on `reported` practice fail their next delayed review at a recall rate at least 20 points below concepts resting on observed work, over the first 30 such reviews. We would also revisit the whole decision if, by 2027-01-31, no learner other than the maintainer has used BodhiKit on a non-code subject (intake goal 1).
MANUAL .shipkit/decisions/0002-record-review-names-the-duty.md: We would move to option 2 if `newlyLearned`, or the profile bump it triggers, is narrated to the learner in 2 or more of the next 10 live `kb-load` or `/teach` transcripts.
MANUAL .shipkit/decisions/0003-writers-say-the-schedule-not-the-box.md: We would extend this to option 3 if 2 or more of the next 10 live transcripts show a box number that came from a read command's output.
MANUAL .shipkit/decisions/0004-record-review-counts-the-learned-concept.md: We would revisit this if a live eval's file state shows `totalConceptsLearned` moving by anything other than the number of crossing writes, or if the tutor still tells the learner about the profile counter in 2 or more of the next 10 live `kb-load` or `/teach` transcripts. That would mean the narration comes from the harness's receipt, not from the key.
HOLDS  .shipkit/specs/explain-with-a-picture/design.md (The rule lives in the `evidence-kinds` KB): test "$(wc -c < skills/evidence-kinds/SKILL.md)" -gt 14336
MANUAL .shipkit/specs/explain-with-a-picture/design.md (Plain-text diagrams and traces in a `text` fence only): We would reverse this, adding a richer form for one host, if the maintainer's trial or an outside learner's issue names a concept a text picture could not show.
MANUAL .shipkit/specs/explain-with-a-picture/design.md (The picture stays out of the check): We would reverse this, allowing option 2, if in the first sweep of the picture scenario (`BODHI_EVAL_RUNS=3`) the tutor cannot ask an answerable check without the diagram in 2 or more of the 3 runs.
MANUAL .shipkit/specs/explain-with-a-picture/design.md (The concept decides, not a learning style): We would reverse this if a controlled study shows that matching the format to a learner's stated preference improves delayed recall.
MANUAL .shipkit/specs/learn-anything/design.md (Classify subjects by the kind of evidence, not by subject): We would reverse this if learners change the proposed kind on more than 5 of the first 20 non-code projects: the axis would not match how they see their subject.
MANUAL .shipkit/specs/learn-anything/design.md (The kind lives in `state.json`, written only by `bodhi-state`): We would reverse this, moving the override into the plan files, if `verify` reports an orphaned module override in two or more real projects.
MANUAL .shipkit/specs/learn-anything/design.md (Applied work gets a basis beside the existing flag, read through one helper): We would reverse this, moving to the enum and explicit parameters, if a reader is found counting `reported` work toward *Solid* or the gate on a non-performed concept twice after release.
MANUAL .shipkit/specs/learn-anything/design.md (A practice rep is recorded as its graded debrief): We would reverse this if concepts whose *Solid* rests on `reported` practice fail their next delayed review at a recall rate at least 20 points below concepts resting on `observed` work, over the first 30 such reviews.
HOLDS  .shipkit/specs/learn-anything/design.md (Non-code teaching lives in one KB that code sessions never load): test -f skills/evidence-kinds/SKILL.md && test "$(wc -c < skills/evidence-kinds/SKILL.md)" -gt 17408
MANUAL .shipkit/specs/learn-anything/design.md (Non-code work is judged against a key saved before the attempt): We would reverse this, enforcing order with a registered timestamp, if an eval shows the key written after the learner's attempt in more than 1 of 10 runs.
MANUAL .shipkit/specs/learn-anything/design.md (`/review` reviews problems and writing itself; `code-reviewer` stays code-only): We would reverse this, adding a second agent, if evals show `/review` rewriting the learner's work in 2 or more of 10 runs on non-code work.
HOLDS  .shipkit/specs/learn-anything/design.md (Safety lives in the learning-project rule): test "$(wc -c < rules/learning-project.md)" -gt 3584
MANUAL .shipkit/specs/learn-anything/design.md (Cowork gets a `.plugin` package, and support is claimed only after a probe): We would reverse this, building an adapter, if the probe shows `bodhi-state` cannot run in Cowork.
MANUAL .shipkit/specs/learn-anything/design.md (In a cloud chat, the hooks follow what the session touched, not its working folder): We would reverse this, moving the rule into the skills, if the second probe shows that neither `UserPromptExpansion` nor `PreToolUse` on `Skill` fires in a cloud chat.
MANUAL .shipkit/specs/revise-a-grade/design.md (Save the pre-review state on the concept, overwritten each review): We would reverse this, moving to option 2, if a revision ever needs an entry other than the latest, i.e. the same-day window is widened.
MANUAL .shipkit/specs/revise-a-grade/design.md (A new subcommand, not a flag on `record-review`): We would reverse this if, in the first `grade-regrade` sweep (`BODHI_EVAL_RUNS=3`), the tutor reaches for `record-review` instead of `revise-review` in 2 or more of the 3 runs, so a flag on the command it already uses would fit better.
MANUAL .shipkit/specs/revise-a-grade/design.md (A revision restores the level, the one exception to the ratchet): We would reverse this if an eval or a real session shows a downward revision made under pressure alone, with no named answer behind it, i.e. `grade-pushback` fails because a revision lowered or raised a grade the learner only argued about.
MANUAL .shipkit/specs/revise-a-grade/design.md (The rule for when to revise lives in the `spaced-repetition` KB): We would reverse this, moving to option 3, if in the first `grade-regrade` sweep the tutor on `/quiz` regrades by judgment but skips the named-evidence check in 2 or more of 3 runs, which would show the judgment half has to travel with it.
MANUAL .shipkit/specs/revise-a-grade/design.md (The wrong entry moves to a sibling list no reader reads): We would reverse this, moving to option 2, if any concept in a real project reaches 10 revised reviews, which would show revisions are common enough to need their place in the sequence.
decision-check: 23 decision(s), 0 fired, 3 hold, 20 manual, 0 error(s)
```
