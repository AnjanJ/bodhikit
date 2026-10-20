# Tasks: Learn anything

Order of work follows the repo rule: the `state-schema` KB first, then `scripts/bodhi-state`
plus tests, then skills, evals and platforms. Every new test cites `learn-anything/REQ-N` in a
comment.

`dev/check.sh` must pass after every task, and so must `t_golden_code_path` from T1 onward.
The golden test is the REQ-1 tripwire: engine output for code must stay byte-identical to
1.24.1.

**Precondition (maintainer, before T0):** commit or stash the six uncommitted OpenAI files
(`dev/eval/test_openai_plugin.py`, `docs/openai*.md`, `platforms/openai/**`). T13, T27 and T33
touch the same files.

## Release 1: learn anything (REQ-1–38, REQ-40)

- [x] **T0** Rewrite the feature-freeze section of `CLAUDE.md` for the learn-anything decision (intake conflict 1)
  - Files: CLAUDE.md
  - Test: none, docs only (CLAUDE.md is inert at install)
  - After: none
  - Done when: `dev/check.sh` → "All hard checks passed."
- [x] **T1** Golden baseline: 1.24.1 engine outputs as the code-path tripwire → REQ-1, REQ-3
  - Files: dev/eval/make_golden.py, dev/eval/golden/, dev/eval/test_bodhi_state.py
  - Test: dev/eval/test_bodhi_state.py::t_golden_code_path (characterization. It passes on the unchanged script; editing any golden file by hand must make it fail, checked once)
  - After: none
  - Done when: `python3 dev/eval/test_bodhi_state.py` → "0 failed", with t_golden_code_path ok
- [x] **T2** Free room in `state-schema` by removing duplication; its guiding principle moves to `state-lifecycle`
  - Files: skills/state-schema/SKILL.md, skills/state-lifecycle/SKILL.md
  - Test: none new; rule 49 (budget) and the rule 45/59 pins in dev/check.sh hold
  - After: none
  - Done when: `wc -c < skills/state-schema/SKILL.md` → at most 17100, and `dev/check.sh` passes
- [ ] **T3** Free room in `state-ops`: drop the repeated carve-out paragraph, move the verify note to CLAUDE.md, shorten the legacy rule
  - Files: skills/state-ops/SKILL.md, CLAUDE.md
  - Test: none new; rules 45, 51 and 59 hold
  - After: T0
  - Done when: `wc -c < skills/state-ops/SKILL.md` → at most 17700, and `dev/check.sh` passes
- [ ] **T4** Free room in `/teach`: the gate paragraph that repeats `prerequisite-gate.md`, the duplicate chaining note, the analogy ladder deferring to the KB → REQ-1
  - Files: skills/teach/SKILL.md
  - Test: dev/eval/assert_scenario.py::assert_teach_pretest and ::assert_teach_hint_discipline (existing; re-run in the release sweep)
  - After: none
  - Done when: `wc -c < skills/teach/SKILL.md` → at most 17800, and `dev/check.sh` passes
- [ ] **T5** `state-schema` documents `evidenceKind`, `moduleEvidenceKinds`, `appliedBasis`, `evidence` and the per-basis archive fields → REQ-3, REQ-4, REQ-6, REQ-21, REQ-22
  - Files: skills/state-schema/SKILL.md
  - Test: none new; the shape pins arrive with T6
  - After: T2
  - Done when: `dev/check.sh` passes, and `wc -c < skills/state-schema/SKILL.md` → at most 18432
- [ ] **T6** Engine: kind and basis constants, the resolver (`read_kinds`, `effective_kind`, `applied_basis`, `admits`), the shapes in verify/normalize, and lint pin 45(g) → REQ-3, REQ-6
  - Files: scripts/bodhi-state, dev/eval/test_bodhi_state.py, dev/check.sh
  - Test: dev/eval/test_bodhi_state.py::t_evidence_kind_resolver, ::t_evidence_kind_shapes (absent kind = code; module override wins; invalid kind degrades to code on read and is a verify error; basis without applied is a warning)
  - After: T1, T5
  - Done when: `python3 dev/eval/test_bodhi_state.py` → "0 failed", t_golden_code_path ok; `dev/check.sh` passes including 45(g)
- [ ] **T7** `set-evidence-kind --kind K [--module M] [--clear]`; lint 45(h) requires every subcommand to be named in `state-ops` → REQ-4, REQ-6, REQ-7
  - Files: scripts/bodhi-state, dev/eval/test_bodhi_state.py, dev/check.sh, skills/state-ops/SKILL.md
  - Test: dev/eval/test_bodhi_state.py::t_set_evidence_kind (spaced-review.json bytes unchanged; normalized module key; an unmatched module is rejected; `--clear` removes an override; an invalid kind exits 1)
  - After: T6, T3
  - Done when: `python3 dev/eval/test_bodhi_state.py` → "0 failed"; `dev/check.sh` passes including 45(h)
- [ ] **T8** Count applied work by basis through one helper in `_evidence_counts`, `archive_history` and `exposure_of`; per-basis archive counts → REQ-7, REQ-23, REQ-24
  - Files: scripts/bodhi-state, dev/eval/test_bodhi_state.py
  - Test: dev/eval/test_bodhi_state.py::t_basis_filter_every_reader (identical reported histories on a performed concept and a writing concept, through the gate, mastery, tiers, rollups, exposure, export, the archive cut and a later kind change), ::t_single_applied_reader
  - After: T7
  - Done when: `python3 dev/eval/test_bodhi_state.py` → "0 failed", t_golden_code_path ok
- [ ] **T9** `record-review --applied [observed|inspected|reported] [--evidence PATH]` → REQ-2, REQ-21, REQ-22
  - Files: scripts/bodhi-state, dev/eval/test_bodhi_state.py, skills/state-ops/SKILL.md
  - Test: dev/eval/test_bodhi_state.py::t_applied_basis_write, ::t_applied_cli_back_compat
    - REQ-2: `reported`/`inspected` off performed exits 1, names the kind, leaves the file unchanged.
    - REQ-22: `observed` off code needs an existing path with a key beside it; the key, a README, `.bodhi/` and paths outside the project are rejected.
    - REQ-1: bare `--applied` writes the same bytes as `--applied observed`.
  - After: T8
  - Done when: `python3 dev/eval/test_bodhi_state.py` → "0 failed", t_golden_code_path ok
- [ ] **T10** The kind on every read surface: `session-brief`, `due`, `revision-brief`, `snapshot` (with `evidenceKindRecorded`), `mastery`, `syllabus`, `gate-check` rows (the prerequisite's own kind) → REQ-8, REQ-9, REQ-15, REQ-17
  - Files: scripts/bodhi-state, dev/eval/test_bodhi_state.py, skills/state-ops/SKILL.md
  - Test: dev/eval/test_bodhi_state.py::t_kind_read_surfaces; the golden allowlist gains exactly these keys
  - After: T9
  - Done when: `python3 dev/eval/test_bodhi_state.py` → "0 failed", t_golden_code_path ok
- [ ] **T11** *Solid* by report: `snapshot`/`mastery` emit `solidByReport` and the `appliedBasis` behind each *Solid* → REQ-25
  - Files: scripts/bodhi-state, dev/eval/test_bodhi_state.py
  - Test: dev/eval/test_bodhi_state.py::t_solid_by_report
  - After: T10
  - Done when: `python3 dev/eval/test_bodhi_state.py` → "0 failed"
- [ ] **T12** `retention` and `export-anonymized` report top-level `byKind` and `byBasis` → REQ-27
  - Files: scripts/bodhi-state, dev/eval/test_bodhi_state.py
  - Test: dev/eval/test_bodhi_state.py::t_kind_breakdowns (no module or concept names; the `export.project` key set unchanged; debrief-graded entries not excluded from retention)
  - After: T11
  - Done when: `python3 dev/eval/test_bodhi_state.py` → "0 failed"
- [ ] **T13** The `evidence-kinds` KB: four kinds, the key protocol, quiz forms, review, reconfirm, sources, the debrief and reps, photos. Pin 45(g) also against the KB; the KB count goes 18 → 19 → REQ-10, REQ-11, REQ-12, REQ-13, REQ-26, REQ-28
  - Files: skills/evidence-kinds/SKILL.md, dev/check.sh, README.md, .claude-plugin/marketplace.json, dev/eval/test_openai_plugin.py
  - Test: dev/eval/test_openai_plugin.py::test_build_and_structure (expects 19 knowledge references, including `references/knowledge/evidence-kinds.md`)
  - After: T12
  - Done when: `dev/check.sh` passes, and `wc -c < skills/evidence-kinds/SKILL.md` → at most 17408
- [ ] **T14** `blooms-taxonomy` *Applied Evidence* names the basis and which kinds may use which; `feynman-technique` rung 4 keeps "code-restatement" for code and defers to the KB otherwise → REQ-14, REQ-21, REQ-23
  - Files: skills/blooms-taxonomy/SKILL.md, skills/feynman-technique/SKILL.md
  - Test: none new; the Bloom label/outcome pins hold, and behaviour is checked by kind-grading (T17)
  - After: T13
  - Done when: `dev/check.sh` passes
- [ ] **T15** Eval fixtures: genetics (`problems`), a political-theory copy with its kind recorded (`writing`; the original stays kind-less for REQ-3), cooking (`performed`), a one-point-perspective drawing PNG → REQ-20, REQ-26, REQ-33
  - Files: dev/eval/fixtures/problems-project/, dev/eval/fixtures/writing-project/, dev/eval/fixtures/performed-project/, dev/eval/fixtures/photo/
  - Test: none, data; each fixture is written through `bodhi-state` and verified
  - After: T10
  - Done when: `scripts/bodhi-state --project <each fixture project> verify` → `"ok": true` for all three
- [ ] **T16** Eval group `kind-fidelity`, plus code-path assertions: no code scenario loads `evidence-kinds`, `learn-scaffold` records `code`, `/continue` on SQL never proposes a kind → REQ-1, REQ-9, REQ-10, REQ-11, REQ-12, REQ-13, REQ-14, REQ-15, REQ-16, REQ-18, REQ-35, REQ-36
  - Files: dev/eval/assert_scenario.py, dev/eval/run-llm-evals.sh, dev/eval/README.md
  - Test: dev/eval/assert_scenario.py::assert_code_never_loads_kinds, ::assert_kind_quiz_no_code, ::assert_kind_teach_no_code, ::assert_kind_key_before_attempt, ::assert_kind_intake, ::assert_kind_offers, ::assert_kind_legacy_proposal, ::assert_kind_review_no_rewrite, ::assert_kind_sources
  - After: T15
  - Done when: each detector, run on a synthetic passing and failing transcript, passes the first and fails the second
- [ ] **T17** Eval group `kind-grading`: apply-band, genuine and parrot on `problems` and on `writing`, both sides of each boundary → REQ-20
  - Files: dev/eval/assert_scenario.py, dev/eval/run-llm-evals.sh, dev/eval/README.md
  - Test: dev/eval/assert_scenario.py::assert_grade_apply_band, ::assert_grade_genuine, ::assert_grade_jargon run with the kind fixtures through `BODHI_EVAL_FIXTURE`/`BODHI_EVAL_PROJECT`/`BODHI_EVAL_CONCEPT`
  - After: T16
  - Done when: `BODHI_EVAL_RUNS=3 dev/eval/run-llm-evals.sh kind-grading` → 18/18, and the recorded levels match the code-topic bands
- [ ] **T18** Eval groups `performed` and `photo` → REQ-25, REQ-26, REQ-28, REQ-29, REQ-30, REQ-31, REQ-32
  - Files: dev/eval/assert_scenario.py, dev/eval/run-llm-evals.sh, dev/eval/README.md
  - Test: dev/eval/assert_scenario.py::assert_performed_debrief_first, ::assert_performed_no_debrief_no_record, ::assert_performed_repless_review, ::assert_performed_by_your_account, ::assert_photo_inspected
  - After: T17
  - Done when: each detector, run on a synthetic passing and failing transcript, passes the first and fails the second
- [ ] **T19** Eval group `safety`: a home-canning request and a personal medical question → REQ-33, REQ-34
  - Files: dev/eval/assert_scenario.py, dev/eval/run-llm-evals.sh, dev/eval/README.md
  - Test: dev/eval/assert_scenario.py::assert_safety_canning, ::assert_safety_medical
  - After: T18
  - Done when: each detector, run on a synthetic passing and failing transcript, passes the first and fails the second
- [ ] **T20** `/teach`: route to the KB off the code path; gate the `/pair` and `/debug-together` offers on code; basis and `--evidence` on `--applied`; cite a source. `prerequisite-gate.md` shapes the reconfirm by kind. Lint: the orphan-KB rule; rule 54 extended to `--applied <basis>`/`--evidence` → REQ-11, REQ-12, REQ-13, REQ-14, REQ-16, REQ-17, REQ-36
  - Files: skills/teach/SKILL.md, skills/teach/references/prerequisite-gate.md, dev/check.sh
  - Test: dev/eval/assert_scenario.py::assert_kind_teach_no_code, ::assert_kind_offers, ::assert_kind_sources, ::assert_code_never_loads_kinds
  - After: T4, T13, T19
  - Done when: `dev/eval/run-llm-evals.sh kind-fidelity` → the teach scenarios pass; `dev/eval/run-llm-evals.sh fidelity` → the code scenarios pass unchanged; `dev/check.sh` passes
- [ ] **T21** `/practice`: one folder per exercise off the code path, the key saved before the attempt, basis and `--evidence`, the performed practice task, photos → REQ-11, REQ-12, REQ-13, REQ-22, REQ-26, REQ-28, REQ-29, REQ-30
  - Files: skills/practice/SKILL.md
  - Test: dev/eval/assert_scenario.py::assert_kind_key_before_attempt, ::assert_photo_inspected, ::assert_performed_debrief_first
  - After: T13, T19
  - Done when: `dev/eval/run-llm-evals.sh kind-fidelity photo performed` → the practice scenarios pass
- [ ] **T22** `/quiz`, `/continue`, `/reflect`: non-code question forms; a due performed concept → rep + debrief + knowledge question; no rep → knowledge alone; the legacy kind proposal → REQ-9, REQ-15, REQ-28, REQ-29, REQ-30, REQ-31, REQ-32
  - Files: skills/quiz/SKILL.md, skills/continue/SKILL.md, skills/reflect/SKILL.md
  - Test: dev/eval/assert_scenario.py::assert_kind_quiz_no_code, ::assert_kind_legacy_proposal, ::assert_performed_repless_review, ::assert_performed_no_debrief_no_record
  - After: T13, T19
  - Done when: `dev/eval/run-llm-evals.sh kind-fidelity performed` → pass; `dev/eval/run-llm-evals.sh quiz quiz-unlabelled reflect continue-gate` → the code scenarios pass unchanged
- [ ] **T23** `/learn`, `/assess`, `/resources` and the agents: the four-row kind table; propose, confirm, `set-evidence-kind`; non-code intake; subject sources saved before the first lesson; non-code instructions passed in agent prompts → REQ-4, REQ-5, REQ-10, REQ-19, REQ-35
  - Files: skills/learn/SKILL.md, skills/assess/SKILL.md, skills/resources/SKILL.md, agents/skill-assessor.md, agents/resource-finder.md
  - Test: dev/eval/assert_scenario.py::assert_learn_scaffold (records `code` for a code topic), ::assert_kind_intake, ::assert_kind_sources
  - After: T13, T19
  - Done when: `dev/eval/run-llm-evals.sh lifecycle kind-fidelity` → pass
- [ ] **T24** `/review` reviews problems and writing in place, with the code-reviewer line conditional on code; the revision sheet uses the subject's own material → REQ-18
  - Files: skills/review/SKILL.md, skills/reflect/references/revision-sheet.md
  - Test: dev/eval/assert_scenario.py::assert_kind_review_no_rewrite
  - After: T13, T19
  - Done when: `dev/eval/run-llm-evals.sh kind-fidelity` → the review scenario passes; `dev/check.sh` passes (rule 3 holds)
- [ ] **T25** `/progress` renders *Solid* resting on reported practice as "by your account" → REQ-25
  - Files: skills/progress/SKILL.md, skills/progress/references/module-row.md
  - Test: dev/eval/assert_scenario.py::assert_performed_by_your_account
  - After: T13, T19
  - Done when: `dev/eval/run-llm-evals.sh performed` → the progress scenario passes
- [ ] **T26** Safety rule and the key exception in `exercises/`; rule 49 caps `rules/learning-project.md` at 4096 bytes → REQ-33, REQ-34, REQ-11, REQ-12
  - Files: rules/learning-project.md, dev/check.sh
  - Test: dev/eval/assert_scenario.py::assert_safety_canning, ::assert_safety_medical
  - After: T20
  - Done when: `dev/eval/run-llm-evals.sh safety` → pass; `dev/check.sh` passes including the cap
- [ ] **T27** The OpenAI package carries the KB, the basis fields and the safety rule, and every packaged path exists → REQ-40
  - Files: dev/eval/test_openai_plugin.py, platforms/openai/build_plugin.py
  - Test: dev/eval/test_openai_plugin.py::test_learn_anything_packaged, ::test_packaged_paths_exist
  - After: T26
  - Done when: `python3 dev/eval/test_openai_plugin.py` → pass
- [ ] **T28** Cowork `.plugin` build and its package test; rule 46 runs the test → REQ-37
  - Files: platforms/cowork/build_plugin.py, dev/eval/test_cowork_plugin.py, dev/check.sh
  - Test: dev/eval/test_cowork_plugin.py::test_package_contents (skills, agents, hooks, scripts, rules and the manifest present; `${CLAUDE_PLUGIN_ROOT}` paths resolve; no `dev/` or `.shipkit/`)
  - After: T26
  - Done when: `python3 platforms/cowork/build_plugin.py --archive dist/bodhikit.plugin && python3 dev/eval/test_cowork_plugin.py` → pass
- [ ] **T29** Cowork probe checklist, run by the maintainer, with the result recorded → REQ-38
  - Files: docs/cowork-probe.md
  - Test: none, manual (REQ-38 is untested by design)
  - After: T28
  - Done when: docs/cowork-probe.md records a dated pass or fail for each check: `python3` present, `bodhi-state` writes, the session-start rule arrives, the Stop hook asks for the sheet, files persist across sessions
- [ ] **T30** Release 1 docs: README Science section with the research citations, CHANGELOG, MIGRATION, `dev/read-defaults.md`, the journal, version bump in both manifests and the badge
  - Files: README.md, CHANGELOG.md, MIGRATION.md, dev/read-defaults.md, dev/changelog-journal.md, .claude-plugin/plugin.json, .claude-plugin/marketplace.json
  - Test: none, docs; rules 1 and 11 in dev/check.sh (versions, counts)
  - After: T21, T22, T23, T24, T25, T27, T29
  - Done when: `dev/check.sh` passes

## Release 2: in the open (REQ-39, REQ-41–43)

- [ ] **T31** Claude hosts without files: a reference adapted from the OpenAI adapter's conversation-only mode, used by `/learn` and `/continue` when no project can be written → REQ-39
  - Files: skills/learn/references/host-without-files.md, skills/learn/SKILL.md, skills/continue/SKILL.md, docs/hosts-without-files.md
  - Test: none, manual (REQ-39 is untested by design)
  - After: T30
  - Done when: a manual claude.ai run is recorded in docs/hosts-without-files.md, and `dev/check.sh` passes
- [ ] **T32** `dev/outcomes.py` reports delayed recall per kind and counts *Solid* by report separately; rule 46 runs its test → REQ-41
  - Files: dev/outcomes.py, dev/eval/test_outcomes.py, dev/check.sh, docs/outcomes.md
  - Test: dev/eval/test_outcomes.py::t_recall_per_kind
  - After: T28, T30
  - Done when: `python3 dev/eval/test_outcomes.py` → pass; `dev/check.sh` passes
- [ ] **T33** Repositioning: a tutor for any subject, code first-class, and what it cannot verify → REQ-42
  - Files: README.md, GUIDE.md, .claude-plugin/plugin.json, .claude-plugin/marketplace.json, platforms/openai/bodhikit/.codex-plugin/plugin.json
  - Test: none, prose (REQ-42 is untested by design)
  - After: T30
  - Done when: `dev/check.sh` passes, and `python3 dev/eval/test_openai_plugin.py` → pass
- [ ] **T34** The voice: "the learner does the work", keeping "writes the code" for code, across the KBs every skill inherits → REQ-43
  - Files: skills/teaching-personality/SKILL.md, skills/ai-learning-safeguards/SKILL.md, skills/growth-mindset/SKILL.md, skills/metacognition/SKILL.md
  - Test: none, prose (REQ-43 is untested by design); the code sweep confirms no regression
  - After: T30
  - Done when: `dev/check.sh` passes

## After the gate

Release 1:
- Full sweep with the code groups at their recorded levels: executor-discipline, grading with `BODHI_EVAL_RUNS=3`, fidelity, lifecycle, applied.
- Every new group on both sides of each grading boundary.
- `BODHI_EVAL_RUNTIME=codex` executor-discipline.
- Record the results in `dev/eval/README.md`.
- The maintainer tags and pushes.
- Rebuild `dist/bodhikit-openai.zip`; re-upload the ChatGPT listing once the portal accepts skills-only submissions.
- Publish `dist/bodhikit.plugin` for Cowork only after T29 passes.

Release 2:
- The same sweep, then tag.
- Write `.shipkit/product.md` with the four intake goals.
