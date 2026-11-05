READY

# Ship report: learn-anything

> Checked on 2026-11-05 at commit `16c921d` on `master`, against base `dde609a` (the commit before the spec's first; `git merge-base HEAD master` is HEAD itself on master). Supersedes the dry run in `2026-10-22-learn-anything.md` (NOT READY on REQ-12 and REQ-17, fixed by T39 and T40).

| # | Step | Result | Reason |
|---|------|--------|--------|
| 1 | Spec check, as shipped | PASS | exit 0, 0 gaps |
| 2 | Tests | PASS | `dev/check.sh` → exit 0 |
| 3 | Tasks ticked | PASS | no unticked task |
| 4 | Independent review | PASS | VERDICT: PASS |
| 5 | Migration rollback | PASS | no migration in the diff |
| 6 | Decisions | PASS | 10 decisions, every reversal condition concrete |
| 7 | Clean tree | PASS | nothing uncommitted |
| 8 | Decisions fired | PASS | 0 fired, 2 hold, 9 manual |

Requirements: 44 (6 waived as `[untested]`: REQ-19, REQ-38, REQ-39, REQ-42, REQ-43, REQ-44).

## Evidence

### 1. Spec check, as shipped
`sh <plugin root>/scripts/spec-check.sh . learn-anything --as-shipped` → exit 0
```
WAIVED learn-anything REQ-44
WAIVED learn-anything REQ-19
WAIVED learn-anything REQ-38
WAIVED learn-anything REQ-39
WAIVED learn-anything REQ-42
WAIVED learn-anything REQ-43
spec-check: 1 spec(s) checked, 0 gap(s)
```
The first attempt at this gate, on `57b1e8f`, stopped here: spec-check reported three CONFLICT gaps (T41 shared files with T25 and T30 without coming after them). The gate was stopped before its review finished, the task order was fixed in `16c921d`, and every step below ran on that commit.

### 2. Tests
`dev/check.sh` (the command CLAUDE.md names) → exit 0
```
OK:   version consistent (1.25.1)
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
`grep -n '^- \[ \]' .shipkit/specs/learn-anything/tasks.md` → exit 1
no line found

### 4. Independent review
The `reviewer` agent, given only the slug and `dde609a`.

## Review: learn-anything against dde609a

This is a sampled review. The diff has 141 files and about 11,000 lines, so I did not read every changed line. I checked, for each requirement, that a test or eval cites it and that matching code or prose exists. I then read the code for REQ-2, 21, 22 and 23. I did not run any tests. Most non-`bodhi-state` rows rest on LLM-eval assertions in `dev/eval/assert_scenario.py`. Those are scenario detectors that only pass or fail when a live-model run uses them, and I did not check that such a run has happened.

| Requirement | Verdict | Evidence |
|---|---|---|
| REQ-1 | MET | `dev/eval/make_golden.py:4`, golden fixtures in `dev/eval/golden/`, tests `dev/eval/test_bodhi_state.py:3559` and `:3814`, `dev/eval/assert_scenario.py:1120`. The Box-label exception is in the amended text. |
| REQ-2 | MET | code `scripts/bodhi-state:838-844`, test `dev/eval/test_bodhi_state.py:3471` |
| REQ-3 | MET | code `scripts/bodhi-state:1929` and `:1945`, tests `dev/eval/test_bodhi_state.py:3128` and `:3184` |
| REQ-4 | MET | code `scripts/bodhi-state:1087`, `skills/learn/SKILL.md`, tests `dev/eval/test_bodhi_state.py:3278` and `dev/eval/assert_scenario.py:1542` |
| REQ-5 | MET | `skills/learn/SKILL.md` four-row table, `dev/eval/assert_scenario.py:1542` |
| REQ-6 | MET | `scripts/bodhi-state:1945` (`effective_kind`), test `dev/eval/test_bodhi_state.py:3128` |
| REQ-7 | MET | `scripts/bodhi-state:1087-1118`, tests `dev/eval/test_bodhi_state.py:3279` and `:3343` |
| REQ-8 | MET | `scripts/bodhi-state:1357`, `:1535`, `:2195`, test `dev/eval/test_bodhi_state.py:3586` |
| REQ-9 | MET | `scripts/bodhi-state:2322` (`evidenceKindRecorded`), `skills/continue/SKILL.md`, tests `dev/eval/assert_scenario.py:1564` and `:1578` |
| REQ-10 | MET | `skills/learn/SKILL.md:26`, `dev/eval/assert_scenario.py:1542` |
| REQ-11 | MET | `skills/evidence-kinds/SKILL.md`, `dev/eval/assert_scenario.py:1420` |
| REQ-12 | MET | `skills/evidence-kinds/SKILL.md`, `dev/eval/assert_scenario.py:1420` and `:1452` |
| REQ-44 (waived) | MET | `skills/evidence-kinds/SKILL.md` writing exercise rule, read-only check. I found no `kind-teach-writing` transcript, so I checked the rule only. |
| REQ-13 | MET | `skills/evidence-kinds/SKILL.md`, `dev/eval/assert_scenario.py:1771` |
| REQ-14 | MET | `skills/teach/SKILL.md:37`, `dev/eval/assert_scenario.py:1317` |
| REQ-15 | MET | `skills/quiz/SKILL.md:58`, `dev/eval/assert_scenario.py:1330` |
| REQ-16 | MET | `skills/evidence-kinds/SKILL.md:38`, `dev/eval/assert_scenario.py:1365` |
| REQ-17 | MET | `skills/teach/references/prerequisite-gate.md`, `dev/eval/assert_scenario.py:1747`, `dev/eval/test_bodhi_state.py:3589` |
| REQ-18 | MET | `skills/review/SKILL.md:33` and `:41`, `dev/eval/assert_scenario.py:1600` |
| REQ-19 (waived) | MET | `skills/resources/SKILL.md:35` and `:39`, `agents/resource-finder.md`. Prose rule only. |
| REQ-20 | MET | `skills/feynman-technique/SKILL.md` (one rubric), `dev/eval/run-llm-evals.sh:776` |
| REQ-21 | MET | `scripts/bodhi-state:55` and `:734-759`, test `dev/eval/test_bodhi_state.py:3472` |
| REQ-22 | MET | `scripts/bodhi-state:841-851` (`evidence_path`), test `dev/eval/test_bodhi_state.py:3473` |
| REQ-23 | MET | `scripts/bodhi-state` (`admits`, `strongest_basis`), tests `dev/eval/test_bodhi_state.py:3341` and `:3424` |
| REQ-24 | MET | `scripts/bodhi-state:2481-2498`, test `dev/eval/test_bodhi_state.py:3342` |
| REQ-25 | MET | `scripts/bodhi-state:1446`, `skills/progress/SKILL.md:146`, tests `dev/eval/test_bodhi_state.py:3649` and `dev/eval/assert_scenario.py:1815` |
| REQ-26 | MET | `skills/evidence-kinds/SKILL.md`, `dev/eval/assert_scenario.py:1842` |
| REQ-27 | MET | `scripts/bodhi-state:1759`, test `dev/eval/test_bodhi_state.py:3697` |
| REQ-28 | MET | `skills/evidence-kinds/SKILL.md` debrief, `dev/eval/assert_scenario.py:1698` |
| REQ-29 | MET | `skills/quiz/SKILL.md:120`, `dev/eval/assert_scenario.py:1699` |
| REQ-30 | MET | `skills/quiz/SKILL.md:120`, `dev/eval/assert_scenario.py:1731` |
| REQ-31 | MET | `skills/continue/SKILL.md`, `skills/quiz/SKILL.md`, `dev/eval/assert_scenario.py:1796` |
| REQ-32 | MET | same skills, `dev/eval/assert_scenario.py:1797` |
| REQ-33 | MET | `rules/learning-project.md:28-31`, `dev/eval/assert_scenario.py:1886` |
| REQ-34 | MET | `rules/learning-project.md:32`, `dev/eval/assert_scenario.py:1914` |
| REQ-35 | MET | `skills/learn/SKILL.md:204`, `dev/eval/assert_scenario.py:1396` |
| REQ-36 | MET | `skills/evidence-kinds/SKILL.md` Sources, `dev/eval/assert_scenario.py:1397` |
| REQ-37 | MET | `platforms/cowork/build_plugin.py`, `dev/eval/test_cowork_plugin.py:4` |
| REQ-38 (waived) | MET | `hooks/hooks.json`, `scripts/bodhi-session-context.py`, `scripts/bodhi-stop-hook.py`. It also has tests at `dev/eval/test_session_context.py:81` and `dev/eval/test_stop_hook.py:218` and `:277`. The manual probe record is `docs/cowork-probe.md`. |
| REQ-39 (waived) | MET | `skills/learn/references/host-without-files.md:15-27`, `docs/hosts-without-files.md` |
| REQ-40 | MET | `platforms/openai/build_plugin.py`, `dev/eval/test_openai_plugin.py:345` |
| REQ-41 | MET | `dev/outcomes.py:100-121`, `dev/eval/test_outcomes.py:4` |
| REQ-42 (waived) | MET | `README.md:5` and `:13`, `.claude-plugin/plugin.json:4`, `.claude-plugin/marketplace.json:7`, `platforms/openai/bodhikit/.codex-plugin/plugin.json:4` |
| REQ-43 (waived) | MET | `skills/teaching-personality/SKILL.md:56` |

## Changes beyond the spec
- `CHANGELOG.md`
- `MIGRATION.md`
- `LICENSE` (copyright holder changed to "Abhaya Code Labs")
- `PRIVACY.md`
- `TERMS.md`

None of these is under the spec's `> Paths:` line. `.shipkit/decisions/0001-learn-anything.md` and the other `.shipkit/` files are exempt. No other spec's folder was touched.

## Decisions not followed
None. I spot-checked these decisions against the code:
- Classify by evidence kind.
- The kind lives in `state.json` and is written only by `bodhi-state`.
- Applied work gets a basis.
- Non-code teaching lives in one KB that code sessions never load.
- `/review` reviews problems and writing itself.
- Safety lives in the learning-project rule.
- Cowork gets a `.plugin` package.
- The cloud-chat hooks follow what the session touched.

The remaining decisions (a practice rep is recorded as its graded debrief; non-code work is judged against a key saved before the attempt) I only skimmed, through the REQ-11, 12, 28 and 29 rows. No decision is marked superseded.

## Not covered by this review
General bugs, style, performance and security: run `/code-review` for those.

Requirements: 44 MET, 0 NOT MET, 0 CANNOT TELL (6 waived).
VERDICT: PASS

### 5. Migration rollback
`git diff dde609a...HEAD --name-only | grep -E '(^|/)(db/migrate|migrations|priv/repo/migrations|alembic|prisma/migrations)/|\.sql$'` → exit 1
no migration in the diff

### 6. Decisions
- **Classify subjects by the kind of evidence, not by subject** — "We would reverse this if learners change the proposed kind on more than 5 of the first 20 non-code projects: the axis would not match how they see their subject."
- **The kind lives in `state.json`, written only by `bodhi-state`** — "We would reverse this, moving the override into the plan files, if `verify` reports an orphaned module override in two or more real projects."
- **Applied work gets a basis beside the existing flag, read through one helper** — "We would reverse this, moving to the enum and explicit parameters, if a reader is found counting `reported` work toward *Solid* or the gate on a non-performed concept twice after release."
- **A practice rep is recorded as its graded debrief** — "We would reverse this if concepts whose *Solid* rests on `reported` practice fail their next delayed review at a recall rate at least 20 points below concepts resting on `observed` work, over the first 30 such reviews."
- **Non-code teaching lives in one KB that code sessions never load** — "We would reverse this, splitting it into several KBs, if it passes 17,408 bytes, 1 KB short of the lint budget that would otherwise fail first."
- **Non-code work is judged against a key saved before the attempt** — "We would reverse this, enforcing order with a registered timestamp, if an eval shows the key written after the learner's attempt in more than 1 of 10 runs."
- **`/review` reviews problems and writing itself; `code-reviewer` stays code-only** — "We would reverse this, adding a second agent, if evals show `/review` rewriting the learner's work in 2 or more of 10 runs on non-code work."
- **Safety lives in the learning-project rule** — "We would reverse this, moving to a KB loaded per phase, if the rule passes 3,584 bytes, 512 short of the lint cap that would otherwise fail first."
- **Cowork gets a `.plugin` package, and support is claimed only after a probe** — "We would reverse this, building an adapter, if the probe shows `bodhi-state` cannot run in Cowork."
- **In a cloud chat, the hooks follow what the session touched, not its working folder** — "We would reverse this, moving the rule into the skills, if the second probe shows that neither `UserPromptExpansion` nor `PreToolUse` on `Skill` fires in a cloud chat."

### 7. Clean tree
`git status --porcelain`, captured before step 1
empty
The test run left no new files behind.

### 8. Decisions fired
`sh <plugin root>/scripts/decision-check.sh . --run` → exit 0
```
MANUAL .shipkit/decisions/0001-learn-anything.md: We would reverse the self-report half, falling back to option 2, if concepts whose *Solid* rests on `reported` practice fail their next delayed review at a recall rate at least 20 points below concepts resting on observed work, over the first 30 such reviews. We would also revisit the whole decision if, by 2027-01-31, no learner other than the maintainer has used BodhiKit on a non-code subject (intake goal 1).
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
decision-check: 11 decision(s), 0 fired, 2 hold, 9 manual, 0 error(s)
```
