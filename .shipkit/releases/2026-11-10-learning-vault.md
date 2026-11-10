NOT READY

# Ship report: learning-vault

> Checked on 2026-11-10 at commit `891c4d8` on `learning-vault`, against base `d94fdea`.

| # | Step | Result | Reason |
|---|------|--------|--------|
| 1 | Spec check, as shipped | PASS | exit 0, 0 gaps; REQ-33 waived |
| 2 | Tests | PASS | `dev/check.sh` → exit 0 |
| 3 | Tasks ticked | PASS | no unticked task (exit 1) |
| 4 | Independent review | PASS | VERDICT: PASS |
| 5 | Migration rollback | PASS | no migration in the diff |
| 6 | Decisions | PASS | 6 decisions in design.md, each with a concrete reversal condition |
| 7 | Clean tree | FAIL | 1 modified file and 1 untracked file before the gate ran |
| 8 | Decisions fired | PASS | 0 fired, 0 errors |

Requirements: 34 (1 waived as `[untested]`: REQ-33).

## To fix before shipping
- Step 7: `dev/guide-writer/references/platform-facts.md` holds the maintainer's own uncommitted edit, made before this work started, and `.shipkit/specs/learning-vault/handoff.md` is untracked. Commit, stash or set each aside, then re-run the gate.

## Beyond the gate (not one of its eight steps, but it bears on a release)
- **The live eval `notes-setup-off` FAILED on REQ-5** (2026-11-10, `a6245e7`, fable-5; recorded in `dev/eval/README.md`). Read in the transcript: the tutor turned notes off straight after reading the setting, with no message showing it or offering a choice, then claimed in its recap that it had shown it. The reviewer's REQ-5 MET rests on the code and the canned detector tests, not on that run. `notes-setup` PASSED on every check.
- **The hand checks in `dev/eval/README.md` have not been run.** Decision *the hook speaks through `systemMessage`* depends on check 1.
- Release steps still open: CHANGELOG, the version bump, `PRIVACY.md`'s effective date, and the ChatGPT re-upload.
- The reviewer's summary line counts 31 MET, but its table lists 34 requirement rows, every one MET. The spec holds 34 live requirements (REQ-28, 30, 31 and 32 were retired to *Sprint 2*).

## Evidence

### 1. Spec check, as shipped
`sh <plugin root>/scripts/spec-check.sh . learning-vault --as-shipped` → exit 0
```
WAIVED learning-vault REQ-33
spec-check: 1 spec(s) checked, 0 gap(s)
```

### 2. Tests
`dev/check.sh` (the project's command, per CLAUDE.md "Before committing, run `dev/check.sh`") → exit 0
```
OK:   version consistent (1.26.1)
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
`git grep -n --untracked '^- \[ \]' .shipkit/specs/learning-vault/tasks.md` → exit 1 (no line found)

### 4. Independent review
The `reviewer` agent, given only the slug and the base ref `d94fdea`. Its reply, whole:

## Review: learning-vault against d94fdea

I read the spec, design, diff and files. I did not run any tests. REQ-3, REQ-5 and REQ-6 are covered only by LLM-eval and detector tests.

| Requirement | Verdict | Evidence |
|-------------|---------|----------|
| REQ-1 | MET | code `skills/notes-setup/SKILL.md:15` and `scripts/bodhi-state:3783`; tests `dev/eval/assert_scenario.py:2445`, `dev/eval/test_detectors.py:1218`, `dev/eval/test_bodhi_state.py:5209` |
| REQ-2 | MET | code `skills/notes-setup/SKILL.md:45` and `scripts/bodhi-state:3499` (apps offered per host); tests `dev/eval/test_bodhi_state.py:4598`, `dev/eval/assert_scenario.py:2445` |
| REQ-3 | MET | code `skills/notes-setup/SKILL.md:51-55` (the plain-words statement before recording, including the sync point); tests `dev/eval/assert_scenario.py:2445`, `dev/eval/test_detectors.py:1218` |
| REQ-4 | MET | code `scripts/bodhi-state:3783`; tests `dev/eval/test_bodhi_state.py:4496`, `:4628` |
| REQ-5 | MET | code `skills/notes-setup/SKILL.md:78`, `scripts/bodhi-state:3766`; tests `dev/eval/assert_scenario.py:2492`, `dev/eval/test_detectors.py:1267` |
| REQ-6 | MET | code `skills/notes-setup/SKILL.md` (turn-off phase) and `scripts/bodhi-state:3644`; tests `dev/eval/test_bodhi_state.py:5188`, `dev/eval/assert_scenario.py:2492` |
| REQ-7 | MET | code `scripts/bodhi-stop-hook.py:284`, `scripts/bodhi-state:3755`; tests `dev/eval/test_stop_hook.py:410`. I found no edits to `t_golden_code_path` (the only golden-test change in the diff is an added entry in a test-registration list) |
| REQ-37 | MET | code `scripts/bodhi-state:3551`; tests `dev/eval/test_bodhi_state.py:4533`, `:5209` |
| REQ-8 | MET | code `scripts/bodhi-stop-hook.py:342`; tests `dev/eval/test_stop_hook.py:426`, `:476` |
| REQ-9 | MET | code `scripts/bodhi-stop-hook.py:342`; tests `dev/eval/test_stop_hook.py:448`, `:476` |
| REQ-10 | MET | code `scripts/bodhi-state:3832`; tests `dev/eval/test_bodhi_state.py:4572`, `dev/eval/test_stop_hook.py:426` |
| REQ-11 | MET | The diff changes no existing `SKILL.md`. Test: `dev/check.sh:387`, `dev/eval/test_stop_hook.py:504` |
| REQ-38 | MET | code `scripts/bodhi-stop-hook.py:342`; tests `dev/eval/test_stop_hook.py:489`, `dev/eval/test_openai_plugin.py:243` |
| REQ-12 | MET | code `scripts/bodhi-state:3644`; test `dev/eval/test_bodhi_state.py:5012` |
| REQ-13 | MET | code `scripts/bodhi-state:2411`; tests `dev/eval/test_bodhi_state.py:4792`, `:4822` |
| REQ-14 | MET | code `scripts/bodhi-state:2411`; test `dev/eval/test_bodhi_state.py:4856` |
| REQ-15 | MET | code `scripts/bodhi-state:2411`; test `dev/eval/test_bodhi_state.py:4875` |
| REQ-16 | MET | code `scripts/bodhi-state:2411`; test `dev/eval/test_bodhi_state.py:4900` |
| REQ-17 | MET | code `scripts/bodhi-state:2411`, `:2497`; test `dev/eval/test_bodhi_state.py:4915` |
| REQ-18 | MET | code `scripts/bodhi-state:2411`; test `dev/eval/test_bodhi_state.py:4928` |
| REQ-19 | MET | code `scripts/bodhi-state:2411`; test `dev/eval/test_bodhi_state.py:4943` |
| REQ-20 | MET | code `scripts/bodhi-state:3644`; test `dev/eval/test_bodhi_state.py:5031` |
| REQ-21 | MET | code `scripts/bodhi-state:3644`; test `dev/eval/test_bodhi_state.py:5052` |
| REQ-22 | MET | code `scripts/bodhi-state:3644`; test `dev/eval/test_bodhi_state.py:5082` |
| REQ-23 | MET | code `scripts/bodhi-state:3622`, `:3823`; test `dev/eval/test_bodhi_state.py:5096` |
| REQ-24 | MET | code `scripts/bodhi-state:3567`; test `dev/eval/test_bodhi_state.py:5125` |
| REQ-25 | MET | no code reads the vault into a tracking file; test `dev/eval/test_bodhi_state.py:5167` |
| REQ-26 | MET | code `scripts/bodhi-stop-hook.py:352-378`; test `dev/eval/test_stop_hook.py:522` |
| REQ-27 | MET | code `scripts/bodhi-state:3737`, `scripts/bodhi-stop-hook.py:378`; test `dev/eval/test_stop_hook.py:542` |
| REQ-29 | MET | code `scripts/bodhi-state:3478`; test `dev/eval/test_bodhi_state.py:4702` (fails if a model-carried app has no probe PASS) |
| REQ-33 (waived) | MET | `PRIVACY.md:24-33` ("Optional notes copy"). I only skimmed the section, so check that it covers all four points the spec names. |
| REQ-34 | MET | docs and counts changed in the README, `GUIDE.md`, `marketplace.json`, `docs/openai.md`, `dev/guide-writer/references/commands.md`; test `dev/eval/test_openai_plugin.py:131`, `:275`, `:294` |
| REQ-35 | MET | code `platforms/openai/build_plugin.py`; tests `dev/eval/test_openai_plugin.py:265`, `dev/eval/test_cowork_plugin.py:97` |
| REQ-36 | MET | code `platforms/openai/bodhikit/references/openai-runtime.md:65-80`; test `dev/eval/test_openai_plugin.py:243` |

## Changes beyond the spec
None. Every changed file is under the spec's `Paths`, under `.shipkit/`, or inside this spec's own folder. The one file under `.claude/` is none that I found.

## Decisions not followed
None. I checked these decisions against the code:
- The freeze lift: `CLAUDE.md:46-52` admits the spec, and decision 0006 exists.
- `.bodhi-notes.json` as the settings file.
- The Stop hook runs `notes-sync` (`scripts/bodhi-stop-hook.py:352`).
- The hook speaks through `systemMessage`, not a block (`scripts/bodhi-stop-hook.py:378`).
- The offer's moments are read from the transcript.
- `bodhi-state` holds its own copy of the module-row words, with a drift test.

The release steps in the spec (the Obsidian hand check, and the eval runs at recorded levels) are not requirements, and I did not verify them.

## Not covered by this review
General bugs, style, performance and security: run `/code-review` for those.

Requirements: 31 MET, 0 NOT MET, 0 CANNOT TELL (1 waived).
VERDICT: PASS

### 5. Migration rollback
`git diff d94fdea...HEAD --name-only`, searched for `db/migrate/`, `migrations/`, `alembic/`, `prisma/migrations/` and `*.sql` → no match (grep exit 1). No migration.

### 6. Decisions
Six live decisions in `.shipkit/specs/learning-vault/design.md`, each with a concrete reversal condition:
- The feature freeze is lifted for this spec only: by 2027-03-31, no learner other than the maintainer with notes on.
- The setting lives in `.bodhi-notes.json`: a second learner-wide setting is specified.
- The Stop hook performs the session-close writes: `notes-sync` over 5 seconds on the largest fixture.
- The hook speaks through `systemMessage`: the hand check finds the message not shown in Claude Code or Codex.
- The offer's moments are read from the transcript: a new Claude Code release drops the `<command-name>` marker.
- `bodhi-state` holds its own copy of the module-row words: the drift test fails on two separate commits.

### 7. Clean tree
`git status --porcelain`, captured before step 1:
```
 M dev/guide-writer/references/platform-facts.md
?? .shipkit/specs/learning-vault/handoff.md
```

### 8. Decisions fired
`sh <plugin root>/scripts/decision-check.sh . --run` → exit 0. No `FIRED` and no `ERROR` line. The lines for this feature's records:
```
MANUAL .shipkit/decisions/0006-learning-vault-past-the-freeze.md: We would reverse this, freezing the feature again and dropping sprint 2, if by 2027-03-31 neither the survey nor an issue shows a learner other than the maintainer with notes turned on.
MANUAL .shipkit/specs/learning-vault/design.md (the feature freeze is lifted for this spec only): We would reverse this, and freeze the feature again with sprint 2 dropped, if by 2027-03-31 neither the survey nor an issue shows a learner other than the maintainer with notes turned on.
MANUAL .shipkit/specs/learning-vault/design.md (the setting lives in `.bodhi-notes.json`, not the profile): We would reverse this, and move the setting into a profile `preferences` object, if a second learner-wide setting is specified.
MANUAL .shipkit/specs/learning-vault/design.md (the Stop hook performs the session-close writes): We would reverse this, and move to option 2, if `notes-sync` on the largest test fixture with notes on takes more than 5 seconds.
MANUAL .shipkit/specs/learning-vault/design.md (the hook speaks through `systemMessage`, not a block): We would reverse this, for the host concerned, if the hand check finds that a Stop hook's `systemMessage` is not shown in the Claude Code terminal, or is not shown in Codex.
MANUAL .shipkit/specs/learning-vault/design.md (the offer's moments are read from the transcript): We would reverse this, and move to option 2, if a live `/continue` eval transcript on a new Claude Code release no longer carries the `<command-name>` marker.
MANUAL .shipkit/specs/learning-vault/design.md (`bodhi-state` holds its own copy of the module-row words): We would reverse this, and move to option 2, if the drift test fails on two separate commits.
decision-check: 38 decision(s), 0 fired, 3 hold, 35 manual, 0 error(s)
```
