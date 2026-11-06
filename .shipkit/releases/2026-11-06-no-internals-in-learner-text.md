READY

# Ship report: no-internals-in-learner-text

> Checked on 2026-11-06 at commit `b457076` on `master`, against base `ae3a1a5` (the commit before the spec's first, `47bdc4c`; `git merge-base HEAD master` is HEAD itself on master). A first run the same day at `59922ab` failed step 1 (REQ-2 to REQ-5 not cited as `slug/REQ-N`); `b457076` adds the citations, and every step was run again.

| # | Step | Result | Reason |
|---|------|--------|--------|
| 1 | Spec check, as shipped | PASS | exit 0, 0 gaps |
| 2 | Tests | PASS | `dev/check.sh` → exit 0 |
| 3 | Tasks ticked | PASS | no unticked task |
| 4 | Independent review | PASS | VERDICT: PASS, 5 MET |
| 5 | Migration rollback | PASS | no migration in the diff |
| 6 | Decisions | PASS | 1 live decision in design.md, reversal condition concrete; 0005 project-wide |
| 7 | Clean tree | PASS | nothing uncommitted |
| 8 | Decisions fired | PASS | 0 fired, 3 hold, 22 manual |

Requirements: 5 (0 waived as `[untested]`).

## Evidence

### 1. Spec check, as shipped
`sh <plugin root>/scripts/spec-check.sh . no-internals-in-learner-text --as-shipped` → exit 0
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
`grep -n '^- \[ \]' .shipkit/specs/no-internals-in-learner-text/tasks.md` → exit 1
no line found

### 4. Independent review
## Review: no-internals-in-learner-text against ae3a1a5

| Requirement | Verdict | Evidence |
|-------------|---------|----------|
| REQ-1 | MET | code `dev/eval/assert_scenario.py:2360-2373` (`assert_transcript_scenario` runs `assert_no_internal_names` for every scenario in `TRANSCRIPT_ASSERTIONS`, dispatched from `main()` at :2395-2398); the regex at :852-855 covers `bodhi-state`, hyphenated subcommands, and current and retired keys. Test `dev/eval/test_detectors.py:952` (`t_internal_names_everywhere`, cites REQ-1 and REQ-2, registered at :1171). |
| REQ-2 | MET | The check runs on `assistant_prose(transcript)`, so tool calls, tool output and the recap are excluded (`assert_scenario.py:908-912`, :2373). Test `test_detectors.py:952`: its clean transcript has a tool call, its output and a recap naming `pretestApplies`, and fails no scenario. |
| REQ-3 | MET | Voice rule `skills/teaching-personality/SKILL.md:37-39` ("Never name a script, a command, an output key or a tracking-file field"). It is enforced for live runs by the central check. I did not run any live runs. |
| REQ-4 | MET | `skills/teaching-personality/SKILL.md:39` ("Say what a step means for them", with a pretest example). The only automated check is the name check, which catches leaks but not whether the plain-words explanation is actually given. |
| REQ-5 | MET | The live runs are recorded in `dev/eval/README.md`. teach-vocabulary passed ×3 on `d6e504e`, two of them on re-check after `d10edfd` cut a harness summary. kind-intake-change passed on `d6e504e` with the name check on. The citation sits at `assert_scenario.py:2368-2369`. This rests on the README's account. I did not re-run the scenarios or check the transcripts. |

## Changes beyond the spec
- `CHANGELOG.md`

`dev/eval/` and `skills/teaching-personality/` are under the spec's Paths, and `.shipkit/decisions/` is too. `dev/changelog-journal.md` is also not under Paths. The other changed files are all within them.

## Decisions not followed
- None. "Run the name check centrally" is followed at `dev/eval/assert_scenario.py:2373`. The inner calls in `assert_kb_load` (:760) and `assert_teach_vocabulary` (:1212) stay, as the decision says. Decision 0005 is the project-wide record the spec's other decision points to. I only confirmed it exists, and did not weigh its alternatives.

## Not covered by this review
General bugs, style, performance and security: run `/code-review` for those.

Requirements: 5 MET, 0 NOT MET, 0 CANNOT TELL (0 waived).
VERDICT: PASS

### 5. Migration rollback
`git diff ae3a1a5...HEAD --name-only | grep -E 'db/migrate/|migrations/|alembic/|prisma/|\.sql$'` → exit 1
no migration in the diff

### 6. Decisions
From `.shipkit/specs/no-internals-in-learner-text/design.md`:
- *Run the name check centrally, in every transcript scenario*: "We would reverse this, adding a per-scenario opt-out, if a scenario's correct behaviour requires naming an internal to the learner."
- *The voice rule, not the engine*: recorded as `.shipkit/decisions/0005-the-tutor-says-what-a-step-means.md`: "We would move to option 2, for the command the leaked name came from, if 2 or more of the next 10 live stream transcripts that run the check still show a state-engine name in learner text." The 12 live stream transcripts on `d6e504e` show none.

### 7. Clean tree
`git status --porcelain`, captured before step 1
empty
The test run left no new files behind.

### 8. Decisions fired
`sh <plugin root>/scripts/decision-check.sh . --run` → exit 0
```
MANUAL .shipkit/decisions/0001-learn-anything.md: We would reverse the self-report half, falling back to option 2, if concepts whose *Solid* rests on `reported` practice fail their next delayed review at a recall rate at least 20 points below concepts resting on observed work, over the first 30 such reviews. We would also revisit the whole decision if, by 2027-01-31, no learner other than the maintainer has used BodhiKit on a non-code subject (intake goal 1).
MANUAL .shipkit/decisions/0002-record-review-names-the-duty.md: We would move to option 2 if `newlyLearned`, or the profile bump it triggers, is narrated to the learner in 2 or more of the next 10 live `kb-load` or `/teach` transcripts.
MANUAL .shipkit/decisions/0003-writers-say-the-schedule-not-the-box.md: We would extend this to option 3 if 2 or more of the next 10 live transcripts show a box number that came from a read command's output.
MANUAL .shipkit/decisions/0004-record-review-counts-the-learned-concept.md: We would revisit this if a live eval's file state shows `totalConceptsLearned` moving by anything other than the number of crossing writes, or if the tutor still tells the learner about the profile counter in 2 or more of the next 10 live `kb-load` or `/teach` transcripts. That would mean the narration comes from the harness's receipt, not from the key.
MANUAL .shipkit/decisions/0005-the-tutor-says-what-a-step-means.md: We would move to option 2, for the command the leaked name came from, if 2 or more of the next 10 live stream transcripts that run the check still show a state-engine name in learner text.
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
MANUAL .shipkit/specs/no-internals-in-learner-text/design.md (Run the name check centrally, in every transcript scenario): We would reverse this, adding a per-scenario opt-out, if a scenario's correct behaviour requires naming an internal to the learner.
MANUAL .shipkit/specs/revise-a-grade/design.md (Save the pre-review state on the concept, overwritten each review): We would reverse this, moving to option 2, if a revision ever needs an entry other than the latest, i.e. the same-day window is widened.
MANUAL .shipkit/specs/revise-a-grade/design.md (A new subcommand, not a flag on `record-review`): We would reverse this if, in the first `grade-regrade` sweep (`BODHI_EVAL_RUNS=3`), the tutor reaches for `record-review` instead of `revise-review` in 2 or more of the 3 runs, so a flag on the command it already uses would fit better.
MANUAL .shipkit/specs/revise-a-grade/design.md (A revision restores the level, the one exception to the ratchet): We would reverse this if an eval or a real session shows a downward revision made under pressure alone, with no named answer behind it, i.e. `grade-pushback` fails because a revision lowered or raised a grade the learner only argued about.
MANUAL .shipkit/specs/revise-a-grade/design.md (The rule for when to revise lives in the `spaced-repetition` KB): We would reverse this, moving to option 3, if in the first `grade-regrade` sweep the tutor on `/quiz` regrades by judgment but skips the named-evidence check in 2 or more of 3 runs, which would show the judgment half has to travel with it.
MANUAL .shipkit/specs/revise-a-grade/design.md (The wrong entry moves to a sibling list no reader reads): We would reverse this, moving to option 2, if any concept in a real project reaches 10 revised reviews, which would show revisions are common enough to need their place in the sequence.
decision-check: 25 decision(s), 0 fired, 3 hold, 22 manual, 0 error(s)
```
