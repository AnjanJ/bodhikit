NOT READY

# Ship report: learn-anything

> Checked on 2026-10-22 at commit `9ebe04f` on `master`, against base `dde609a` (origin/master, the commit before the spec's first). A dry run before the release eval sweep; the spec stays `open`.

| # | Step | Result | Reason |
|---|------|--------|--------|
| 1 | Spec check, as shipped | PASS | exit 0, 0 gaps |
| 2 | Tests | PASS | `dev/check.sh` → exit 0 |
| 3 | Tasks ticked | PASS | no unticked task |
| 4 | Independent review | FAIL | VERDICT: FAIL — REQ-12 and REQ-17 NOT MET |
| 5 | Migration rollback | PASS | no migration in the diff |
| 6 | Decisions | PASS | 10 decisions, every reversal condition concrete |
| 7 | Clean tree | PASS | nothing uncommitted |
| 8 | Decisions fired | PASS | 0 fired, 2 hold, 9 manual |

Requirements: 43 (5 waived as `[untested]`: REQ-19, REQ-38, REQ-39, REQ-42, REQ-43).

## To fix before shipping
- Step 4, REQ-12: no test checks that a `writing` exercise saves its task before the learner writes, or that the task applies the concept to a case the lesson did not use. `assert_kind_key_before_attempt` checks only that `criteria.md` comes first.
- Step 4, REQ-17: no eval checks that a non-code `no-applied-evidence` reconfirm takes the kind's form (one problem, a written application, or a rep with its debrief). The reviewer also reads `skills/teach/references/prerequisite-gate.md:23` ("the same call with `--applied`") as recording observed work, which `bodhi-state` would refuse for a performed rep.

## Evidence

### 1. Spec check, as shipped
`sh <plugin root>/scripts/spec-check.sh . learn-anything --as-shipped` → exit 0
```
WAIVED learn-anything REQ-19
WAIVED learn-anything REQ-38
WAIVED learn-anything REQ-39
WAIVED learn-anything REQ-42
WAIVED learn-anything REQ-43
spec-check: 1 spec(s) checked, 0 gap(s)
```

### 2. Tests
`dev/check.sh` (the command CLAUDE.md names) → exit 0
```
OK:   version consistent (1.25.0)
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
The `reviewer` agent, given only the slug and `dde609a`. It stopped at its turn limit once and was told only to continue.

## Review: learn-anything against dde609a

| Requirement | Verdict | Evidence |
|-------------|---------|----------|
| REQ-1 | MET | code `scripts/bodhi-state:1932` (no recorded kind reads as code), routing `skills/teach/SKILL.md:37`, `skills/practice/SKILL.md:41`; tests `dev/eval/test_bodhi_state.py:3813` (`t_golden_code_path`) and `dev/eval/assert_scenario.py:1221` (`assert_code_never_loads_kinds`, run after every code transcript scenario). Note: commit f59a52b removed "(Box 4-5)" and the other box ranges from the `/progress` rows (`skills/progress/SKILL.md`). Code learners see that change too. It is a display change, not a change to how code is taught, graded, scheduled or tracked. |
| REQ-2 | MET | code `scripts/bodhi-state:844`; test `dev/eval/test_bodhi_state.py:3492` (reported and inspected refused on code, problems and writing; the error names the kind; the file is unchanged) |
| REQ-3 | MET | code `scripts/bodhi-state:1932`; tests `dev/eval/test_bodhi_state.py:3141`, `:3813` |
| REQ-4 | MET | code `skills/learn/SKILL.md:198`, `scripts/bodhi-state:1087`; tests `dev/eval/assert_scenario.py:789` (code topic records `code`), `:1450` (non-code: exactly one project-level `set-evidence-kind`), `dev/eval/test_bodhi_state.py:3277` |
| REQ-5 | MET | code `skills/learn/SKILL.md:33`; test `dev/eval/assert_scenario.py:1450`, which uses `proposal_then_record` with `ordered=True` (`:1420`). The "learner changes it" path has no test. |
| REQ-6 | MET | code `scripts/bodhi-state:1941`; tests `dev/eval/test_bodhi_state.py:3148`, `:3299` |
| REQ-7 | MET | code `scripts/bodhi-state:1087`; tests `dev/eval/test_bodhi_state.py:3308` (spaced-review.json is byte-identical), `:3418` (a kind change re-reads every review, archived ones included) |
| REQ-8 | MET | code `scripts/bodhi-state:1862`, `:2320`, `:2206`, `:2195`; test `dev/eval/test_bodhi_state.py:3585` |
| REQ-9 | MET | code `skills/continue/SKILL.md:59`, `scripts/bodhi-state:2322`; tests `dev/eval/assert_scenario.py:1472`, `:1486`, and `:1221` on the code `/continue` scenarios |
| REQ-10 | MET | code `skills/learn/SKILL.md:26`, `agents/skill-assessor.md`; test `dev/eval/assert_scenario.py:1450` (`PROGRAMMING_Q_RE`) |
| REQ-11 | MET | code `skills/evidence-kinds/SKILL.md:44`, `scripts/bodhi-state:772` (key must sit beside the evidence); tests `dev/eval/assert_scenario.py:1360` (scenarios `kind-teach-problems` and `kind-practice-problems`, `dev/eval/run-llm-evals.sh:826`), `dev/eval/test_bodhi_state.py:3520` |
| REQ-12 | NOT MET | The code is there: `skills/evidence-kinds/SKILL.md:45`. The only test is `dev/eval/assert_scenario.py:1360`, and it checks only that `criteria.md` is written before the learner's file. Nothing checks that the task (`README.md`) is saved before the writing. Nothing checks that the task uses a case the lesson did not use, which is the clause the user story depends on. |
| REQ-13 | MET | code `skills/evidence-kinds/SKILL.md:46`, `skills/practice/SKILL.md:41`; tests `dev/eval/assert_scenario.py:1660`, `dev/eval/test_detectors.py:336`. Exercised through `/practice` only; the `/teach` path has no scenario. |
| REQ-14 | MET | code `skills/teach/SKILL.md:37`, `skills/evidence-kinds/SKILL.md:34-36`, `skills/feynman-technique/SKILL.md` (rung 4); test `dev/eval/assert_scenario.py:1257`. The test checks for no code anywhere in the lesson. The scripted learner never struggles, so the scenario never reaches the analogy ladder's last rung. |
| REQ-15 | MET | code `skills/quiz/SKILL.md:58`, `scripts/bodhi-state:1357`; tests `dev/eval/assert_scenario.py:1270`, `dev/eval/test_bodhi_state.py:3627` |
| REQ-16 | MET | code `skills/teach/SKILL.md:112`, `:162`, `skills/practice/SKILL.md:168`, `:178`; test `dev/eval/assert_scenario.py:1305` |
| REQ-17 | NOT MET | Code: `skills/teach/references/prerequisite-gate.md:21`, `skills/evidence-kinds/SKILL.md:70`, the gate row's kind at `scripts/bodhi-state:2700`. The only test is `dev/eval/test_bodhi_state.py:3643`, which proves the gate row carries the kind. No eval checks that a non-code `no-applied-evidence` reconfirm takes the kind's form (one problem, a written application, or a rep with its debrief). Also, `prerequisite-gate.md:23` still says "the same call with `--applied`", which means observed. For a performed rep that call would be refused. |
| REQ-18 | MET | code `skills/review/SKILL.md:33`, `:41`; test `dev/eval/assert_scenario.py:1507` (scenario `kind-review`). Covers writing only; no `problems` review scenario. |
| REQ-19 (waived) | MET | `agents/resource-finder.md:27-29`, `skills/resources/SKILL.md:35`, `skills/learn/SKILL.md:204` |
| REQ-20 | MET | code `skills/evidence-kinds/SKILL.md:22`; test `dev/eval/run-llm-evals.sh:776` (the kind-grading block: parrot, apply-band and genuine on problems and on writing, read with the code grading assertions) |
| REQ-21 | MET | code `scripts/bodhi-state:735`; test `dev/eval/test_bodhi_state.py:3499` |
| REQ-22 | MET | code `scripts/bodhi-state:772`, `:852`; test `dev/eval/test_bodhi_state.py:3512-3533` (no path, a missing path, no key beside it, the key, a README, a tracking file, outside the project; performed included) |
| REQ-23 | MET | code `scripts/bodhi-state:1959`, `:2482`, `:2561`; tests `dev/eval/test_bodhi_state.py:3340`, `:3423` |
| REQ-24 | MET | code `scripts/bodhi-state:1383` (level, streak, box and explain-back conjuncts do not depend on kind); test `dev/eval/test_bodhi_state.py:3340` cites it but covers only the positive case. No test shows a performed concept with a reported rep held back from *Solid* by a missing conjunct; the pre-existing conjunct tests run on code. |
| REQ-25 | MET | code `scripts/bodhi-state:2495`, `skills/progress/SKILL.md:146`, `skills/progress/references/module-row.md:28`; tests `dev/eval/test_bodhi_state.py:3648`, `dev/eval/assert_scenario.py:1704` |
| REQ-26 | MET | code `skills/evidence-kinds/SKILL.md:97-98`, `skills/practice/SKILL.md:138`; test `dev/eval/assert_scenario.py:1730` |
| REQ-27 | MET | code `scripts/bodhi-state:1728`, `:1800`; test `dev/eval/test_bodhi_state.py:3696` |
| REQ-28 | MET | code `skills/evidence-kinds/SKILL.md:82`; test `dev/eval/assert_scenario.py:1606` |
| REQ-29 | MET | code `skills/evidence-kinds/SKILL.md:83`; test `dev/eval/assert_scenario.py:1606` (basis reported, graded result) |
| REQ-30 | MET | code `skills/evidence-kinds/SKILL.md:84`; test `dev/eval/assert_scenario.py:1639` |
| REQ-31 | MET | code `skills/quiz/SKILL.md:58`, `skills/continue/SKILL.md:91`; test `dev/eval/assert_scenario.py:1685`. The scenario goes through `/quiz`; `/continue` reaches it only by handing due concepts to `/quiz`. |
| REQ-32 | MET | code `skills/quiz/SKILL.md:58`; test `dev/eval/assert_scenario.py:1685` |
| REQ-33 | MET | code `rules/learning-project.md:28-31`; test `dev/eval/assert_scenario.py:1775` |
| REQ-34 | MET | code `rules/learning-project.md:32`; test `dev/eval/assert_scenario.py:1803` |
| REQ-35 | MET | code `skills/learn/SKILL.md:204`; test `dev/eval/assert_scenario.py:1336`, via `:1469` |
| REQ-36 | MET | code `skills/teach/SKILL.md:37`, `skills/evidence-kinds/SKILL.md:37`; test `dev/eval/assert_scenario.py:1336`, via `assert_kind_teach` `:1535` |
| REQ-37 | MET | code `platforms/cowork/build_plugin.py:48`; test `dev/eval/test_cowork_plugin.py:46` |
| REQ-38 (waived) | MET | `scripts/bodhi-session-context.py:44`, `scripts/bodhi-stop-hook.py:201`, `hooks/hooks.json`; `docs/cowork-probe.md:129` records the 2026-10-22 rerun with all five checks PASS |
| REQ-39 (waived) | MET | `skills/learn/references/host-without-files.md:19-20`, `skills/learn/SKILL.md:21`, `skills/continue/SKILL.md:43`; manual run recorded at `docs/hosts-without-files.md:60` |
| REQ-40 | MET | code `platforms/openai/build_plugin.py`; test `dev/eval/test_openai_plugin.py:344` |
| REQ-41 | MET | code `dev/outcomes.py:100`; test `dev/eval/test_outcomes.py:44` |
| REQ-42 (waived) | MET | `README.md:5`, `README.md:13`, `.claude-plugin/plugin.json:4`, `.claude-plugin/marketplace.json:7`, `:14`, `platforms/openai/bodhikit/.codex-plugin/plugin.json:4` |
| REQ-43 (waived) | MET | `skills/teaching-personality/SKILL.md:56` |

## Changes beyond the spec
- `CHANGELOG.md`
- `MIGRATION.md`

## Decisions not followed
- The kind lives in `state.json`: `skills/plan/SKILL.md:28` and `skills/progress/references/module-row.md`. The decision's "Case for" says "`/plan view` and `/progress` render `syllabus` output, so the learner still sees each module's kind." `syllabus` does emit `evidenceKind`, but neither renderer shows it, so the learner never sees a module's kind. This is a claim made in support of the decision, not the decision sentence itself.
- Applied work gets a basis beside the existing flag: `scripts/bodhi-state:663`. The "Case for" says "Only `_evidence_counts` changes its signature." `apply_review` also changed: it gained `evidence=` and its `applied` default went from `False` to `None`. The code output is unchanged, and the golden test covers it.

## Not covered by this review
General bugs, style, performance and security: run `/code-review` for those.

Requirements: 41 MET, 2 NOT MET, 0 CANNOT TELL (5 waived).
VERDICT: FAIL

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
