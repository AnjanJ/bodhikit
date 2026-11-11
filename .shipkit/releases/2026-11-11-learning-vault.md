READY

# Ship report: learning-vault

> Checked on 2026-11-11 at commit `38d0d8b` on `learning-vault`, against base `d94fdea`.

| # | Step | Result | Reason |
|---|------|--------|--------|
| 1 | Spec check, as shipped | PASS | exit 0 |
| 2 | Tests | PASS | `dev/check.sh` → exit 0 |
| 3 | Tasks ticked | PASS | no unticked task (11 of 11 ticked) |
| 4 | Independent review | PASS | VERDICT: PASS |
| 5 | Migration rollback | PASS | no migration in the diff |
| 6 | Decisions | PASS | 7 decisions, each reversal condition concrete |
| 7 | Clean tree | PASS | nothing uncommitted |
| 8 | Decisions fired | PASS | 39 Fired-if records, 0 fired, 3 hold, 36 manual |

Requirements: 34 (1 waived as `[untested]`: REQ-33). REQ-28 and REQ-30 to REQ-32 are not in the spec. The reviewer's count line reads "31 MET", but its table below has a row for all 34, each MET.

This gate supersedes `.shipkit/releases/2026-11-10-learning-vault.md` (READY at `181d79e`), which predates hand check 3's Codex finding and its fixes (`8b888a2`, `cfc7bcb`).

## Evidence

### 1. Spec check, as shipped
`sh <plugin root>/scripts/spec-check.sh . learning-vault --as-shipped` → exit 0
```
WAIVED learning-vault REQ-33
spec-check: 1 spec(s) checked, 0 gap(s)
```
The first run before the gate, at `84e52e9`, found 4 gaps, all in the new T11 (an `After:` naming a hand check, and no order against T8 and T9, which edit the same test file). They were fixed in `38d0d8b` before this gate began.

### 2. Tests
`( dev/check.sh ) > shipkit-ship-tests.out 2>&1` → exit 0
```
OK:   version consistent (1.27.0)
OK:   bodhi-state test suite passed
OK:   stop-hook test suite passed
OK:   session-context test suite passed
OK:   Cowork plugin test suite passed
OK:   outcomes report test suite passed
OK:   eval detector test suite passed
OK:   guide-writer test suite passed
OK:   OpenAI plugin test suite passed

All hard checks passed.
```

### 3. Tasks ticked
`git grep -n --untracked '^- \[ \]' .shipkit/specs/learning-vault/tasks.md` → exit 1
no line found

### 4. Independent review
## Review: learning-vault against d94fdea

I did not run the tests. I read the spec, design, tasks, diff and files. Many tests cite requirements in short or list forms, so I confirmed the citation text by grep. Line numbers are working-tree lines from `git grep -n`. Test cites are in `dev/eval/` and code cites are in `scripts/`.

| Requirement | Verdict | Evidence |
|-------------|---------|----------|
| REQ-1 | MET | code `skills/notes-setup/SKILL.md:34-38`; test `test_detectors.py:1224` (`t_notes_setup`, cites `learning-vault/REQ-1`). It checks canned transcripts only; the live scenario is a release step. |
| REQ-2 | MET | code `skills/notes-setup/SKILL.md:28,45`; tests `test_bodhi_state.py:4598` (cloud chat gives no app), `test_detectors.py:1224` |
| REQ-3 | MET | code `skills/notes-setup/SKILL.md` Phase 3; tests `test_detectors.py:1224`, `assert_scenario.py:2461` |
| REQ-4 | MET | code `scripts/bodhi-state:3784`; tests `test_bodhi_state.py:4496,4628` |
| REQ-5 | MET | code `skills/notes-setup/SKILL.md:29` (Phase 4); test `test_detectors.py:1273` (`t_notes_setup_off`) |
| REQ-6 | MET | tests `test_bodhi_state.py:5187` (`t_notes_off_writes_nothing`), `test_detectors.py:1273`; `assert_scenario.py:2508` |
| REQ-7 | MET | code `scripts/bodhi-state:3755,3852`, `scripts/bodhi-stop-hook.py:287`; test `test_stop_hook.py:410` |
| REQ-8 | MET | code `scripts/bodhi-stop-hook.py:202,354`; tests `test_openai_plugin.py:735,764`. Per tasks.md, `t_offer_after_learn` is in `test_stop_hook.py` and I did not locate its exact line. |
| REQ-9 | MET | code `scripts/bodhi-stop-hook.py:202`; tests `test_stop_hook.py:448,476,512` |
| REQ-10 | MET | code `scripts/bodhi-state:3833`; tests `test_bodhi_state.py:4571`, `test_stop_hook.py:426` |
| REQ-11 | MET | code: the only skill file in the diff is the new `skills/notes-setup/`; tests `test_stop_hook.py:540`, `check.sh:387` |
| REQ-12 | MET | code `scripts/bodhi-state:3645`; test `test_bodhi_state.py:5012` |
| REQ-13 | MET | code `scripts/bodhi-state:2351,2412`; tests `test_bodhi_state.py:4792,4822` |
| REQ-14 | MET | test `test_bodhi_state.py:4856`; the renderer is in the same syllabus code |
| REQ-15 | MET | test `test_bodhi_state.py:4875` |
| REQ-16 | MET | test `test_bodhi_state.py:4900` |
| REQ-17 | MET | test `test_bodhi_state.py:4915` |
| REQ-18 | MET | test `test_bodhi_state.py:4928` |
| REQ-19 | MET | test `test_bodhi_state.py:4943` |
| REQ-20 | MET | test `test_bodhi_state.py:5031` |
| REQ-21 | MET | test `test_bodhi_state.py:5052` |
| REQ-22 | MET | test `test_bodhi_state.py:5082` |
| REQ-23 | MET | code `scripts/bodhi-state:3624,3823`; test `test_bodhi_state.py:5096` |
| REQ-24 | MET | code `scripts/bodhi-state:3567`; test `test_bodhi_state.py:5125` |
| REQ-25 | MET | test `test_bodhi_state.py:5167` |
| REQ-26 | MET | test `test_stop_hook.py:558` |
| REQ-27 | MET | test `test_stop_hook.py:578` |
| REQ-29 | MET | code `scripts/bodhi-state:3478`; test `test_bodhi_state.py:4702` |
| REQ-33 (waived) | MET | `PRIVACY.md:24-38` covers all four points: only with permission and only where the learner chose; a folder their app may sync; optional; nothing breaks without it. |
| REQ-34 | MET | `README.md:187`, `GUIDE.md:569`, `dev/guide-writer/references/commands.md:94`, `.claude-plugin/marketplace.json:14`, `docs/openai.md`; tests `test_openai_plugin.py:132,276` |
| REQ-35 | MET | tests `test_openai_plugin.py:266`, `test_cowork_plugin.py:97`; build change in `platforms/openai/build_plugin.py` |
| REQ-36 | MET | code `platforms/openai/bodhikit/references/openai-runtime.md:77-88`; test `test_openai_plugin.py:244` (cites `learning-vault/REQ-36`) |
| REQ-37 | MET | code `scripts/bodhi-state:3551`; test `test_bodhi_state.py:4533` |
| REQ-38 | MET | tests `test_stop_hook.py:525`, `test_openai_plugin.py:244` |

## Changes beyond the spec
- `.gitignore` adds `.shipkit/specs/learning-vault/handoff.md`. It is not under `> Paths:` and is not a setup-installed file. The blob id `git hash-object .gitignore` prints is `804d6b88…`. `.claude/rules/shipkit/.setup-files` does not exist, so it cannot be matched against that.
- Every other changed file is under `> Paths:` or under `.shipkit/`.

## Decisions not followed
- None. I read the six decisions that matter here: separate `.bodhi-notes.json`, Stop hook runs `notes-sync`, `systemMessage` not a block, transcript-read offer moments, Codex script-changed projects, and own module-row tables. I also read the freeze decision. The code follows each one. `state-schema` and every existing `SKILL.md` are untouched.

## Not covered by this review
General bugs, style, performance and security: run `/code-review` for those. I did not run tests, the live `notes-setup` scenario, the Obsidian hand check, or the 5-second timing check, which are listed as release steps.

Requirements: 31 MET, 0 NOT MET, 0 CANNOT TELL (1 waived).
VERDICT: PASS

### 5. Migration rollback
`git diff d94fdea...HEAD --name-only` lists 37 files; none under `db/migrate/`, `migrations/`, `priv/repo/migrations/`, `alembic/` or `prisma/migrations/`, and no `*.sql`. No migration in the diff. (BodhiKit's tracking-file migrations are `bodhi-state` subcommands; this release adds none.)

### 6. Decisions
Seven live decisions in `.shipkit/specs/learning-vault/design.md`, none superseded. Their reversal conditions:
- *the feature freeze is lifted for this spec only*: "if by 2027-03-31 neither the survey nor an issue shows a learner other than the maintainer with notes turned on."
- *the setting lives in `.bodhi-notes.json`, not the profile*: "if a second learner-wide setting is specified."
- *the Stop hook performs the session-close writes*: "if `notes-sync` on the largest test fixture with notes on takes more than 5 seconds." (Measured 0.04 s, 2026-11-10.)
- *the hook speaks through `systemMessage`, not a block*: "if the hand check finds that a Stop hook's `systemMessage` is not shown in the Claude Code terminal, or is not shown in Codex." (Shown in both: Claude Code 2026-11-10, Codex 2026-11-11.)
- *the offer's moments are read from the transcript*: "if a live `/continue` eval transcript on a new Claude Code release no longer carries the `<command-name>` marker."
- *in Codex, `touch-state` run from a script counts for the projects it changed*: "if a Codex session is asked for a revision sheet or shown the notes offer for a course it did not study, or if Codex stops recording a command's completion time or duration."
- *`bodhi-state` holds its own copy of the module-row words*: "if the drift test fails on two separate commits."

### 7. Clean tree
`git status --porcelain`, captured before step 1
empty

### 8. Decisions fired
`sh <plugin root>/scripts/decision-check.sh . --run` → exit 0
```
MANUAL .shipkit/decisions/0001-learn-anything.md: We would reverse the self-report half, falling back to option 2, if concepts whose *Solid* rests on `reported` practice fail their next delayed review at a recall rate at least 20 points below concepts resting on observed work, over the first 30 such reviews. We would also revisit the whole decision if, by 2027-01-31, no learner other than the maintainer has used BodhiKit on a non-code subject (intake goal 1).
MANUAL .shipkit/decisions/0002-record-review-names-the-duty.md: We would move to option 2 if `newlyLearned`, or the profile bump it triggers, is narrated to the learner in 2 or more of the next 10 live `kb-load` or `/teach` transcripts.
MANUAL .shipkit/decisions/0003-writers-say-the-schedule-not-the-box.md: We would extend this to option 3 if 2 or more of the next 10 live transcripts show a box number that came from a read command's output.
MANUAL .shipkit/decisions/0004-record-review-counts-the-learned-concept.md: We would revisit this if a live eval's file state shows `totalConceptsLearned` moving by anything other than the number of crossing writes, or if the tutor still tells the learner about the profile counter in 2 or more of the next 10 live `kb-load` or `/teach` transcripts. That would mean the narration comes from the harness's receipt, not from the key.
MANUAL .shipkit/decisions/0005-the-tutor-says-what-a-step-means.md: We would move to option 2, for the command the leaked name came from, if 2 or more of the next 10 live stream transcripts that run the check still show a state-engine name in learner text.
MANUAL .shipkit/decisions/0006-learning-vault-past-the-freeze.md: We would reverse this, freezing the feature again and dropping sprint 2, if by 2027-03-31 neither the survey nor an issue shows a learner other than the maintainer with notes turned on.
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
MANUAL .shipkit/specs/learning-vault/design.md (the feature freeze is lifted for this spec only): We would reverse this, and freeze the feature again with sprint 2 dropped, if by 2027-03-31 neither the survey nor an issue shows a learner other than the maintainer with notes turned on.
MANUAL .shipkit/specs/learning-vault/design.md (the setting lives in `.bodhi-notes.json`, not the profile): We would reverse this, and move the setting into a profile `preferences` object, if a second learner-wide setting is specified.
MANUAL .shipkit/specs/learning-vault/design.md (the Stop hook performs the session-close writes): We would reverse this, and move to option 2, if `notes-sync` on the largest test fixture with notes on takes more than 5 seconds.
MANUAL .shipkit/specs/learning-vault/design.md (the hook speaks through `systemMessage`, not a block): We would reverse this, for the host concerned, if the hand check finds that a Stop hook's `systemMessage` is not shown in the Claude Code terminal, or is not shown in Codex.
MANUAL .shipkit/specs/learning-vault/design.md (the offer's moments are read from the transcript): We would reverse this, and move to option 2, if a live `/continue` eval transcript on a new Claude Code release no longer carries the `<command-name>` marker.
MANUAL .shipkit/specs/learning-vault/design.md (in Codex, `touch-state` run from a script counts for the projects it changed): We would reverse this if a Codex session is asked for a revision sheet or shown the notes offer for a course it did not study, or if Codex stops recording a command's completion time or duration (then the window cannot be computed).
MANUAL .shipkit/specs/learning-vault/design.md (`bodhi-state` holds its own copy of the module-row words): We would reverse this, and move to option 2, if the drift test fails on two separate commits.
MANUAL .shipkit/specs/no-internals-in-learner-text/design.md (Run the name check centrally, in every transcript scenario): We would reverse this, adding a per-scenario opt-out, if a scenario's correct behaviour requires naming an internal to the learner.
MANUAL .shipkit/specs/revise-a-grade/design.md (Save the pre-review state on the concept, overwritten each review): We would reverse this, moving to option 2, if a revision ever needs an entry other than the latest, i.e. the same-day window is widened.
MANUAL .shipkit/specs/revise-a-grade/design.md (A new subcommand, not a flag on `record-review`): We would reverse this if, in the first `grade-regrade` sweep (`BODHI_EVAL_RUNS=3`), the tutor reaches for `record-review` instead of `revise-review` in 2 or more of the 3 runs, so a flag on the command it already uses would fit better.
MANUAL .shipkit/specs/revise-a-grade/design.md (A revision restores the level, the one exception to the ratchet): We would reverse this if an eval or a real session shows a downward revision made under pressure alone, with no named answer behind it, i.e. `grade-pushback` fails because a revision lowered or raised a grade the learner only argued about.
MANUAL .shipkit/specs/revise-a-grade/design.md (The rule for when to revise lives in the `spaced-repetition` KB): We would reverse this, moving to option 3, if in the first `grade-regrade` sweep the tutor on `/quiz` regrades by judgment but skips the named-evidence check in 2 or more of 3 runs, which would show the judgment half has to travel with it.
MANUAL .shipkit/specs/revise-a-grade/design.md (The wrong entry moves to a sibling list no reader reads): We would reverse this, moving to option 2, if any concept in a real project reaches 10 revised reviews, which would show revisions are common enough to need their place in the sequence.
MANUAL .shipkit/specs/write-guide/design.md (The skill lives in `dev/guide-writer/`, linked from `.claude/skills/`): We would reverse this if a second maintainer works in the repo, since a committed `.claude/skills/` then saves each of them the link step, or if `/write-guide` fails to appear in the `/` menu with the link in place on a current Claude Code.
MANUAL .shipkit/specs/write-guide/design.md (The skill runs only when typed): We would reverse this if the maintainer asks for a guide in plain words and the skill does not start, three times, and says the extra context of a default description is worth paying.
MANUAL .shipkit/specs/write-guide/design.md (Repository facts are read at run time; platform facts live in one dated file the skill corrects): We would reverse the re-check-everything rule, re-checking only facts older than 30 days, if five consecutive runs change nothing in `platform-facts.md`.
MANUAL .shipkit/specs/write-guide/design.md (A claim ledger is a separate file beside the guide): We would reverse this if a guide's review finds a factual sentence missing from its ledger in two separate guides; the ledger would then move inline, next to each claim (option 2).
MANUAL .shipkit/specs/write-guide/design.md (The guide is written in HTML and rendered by WeasyPrint and pandoc): We would reverse the DOCX step if a reader reports that the DOCX loses a prompt's text or a table's rows.
MANUAL .shipkit/specs/write-guide/design.md (The command reference is written by hand and checked against `skills/` by a test): We would reverse this if a guide ships with a stale command description that the test did not catch, twice.
decision-check: 39 decision(s), 0 fired, 3 hold, 36 manual, 0 error(s)
```
