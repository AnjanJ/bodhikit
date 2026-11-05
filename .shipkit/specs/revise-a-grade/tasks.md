# Tasks: Revise a grade

- [x] **T1** Document `beforeLastReview`, `revisedReviews`, the `revision` flag and the ratchet exception in the schema KB → REQ-2, REQ-8
  - Files: skills/state-schema/SKILL.md
  - Test: dev/eval/test_bodhi_state.py::t_revise_review_keeps_the_wrong_entry (written in T2; red until T2's code lands)
  - After: none
  - Done when: `dev/check.sh` → all hard checks pass, and `wc -c < skills/state-schema/SKILL.md` ≤ 18432
- [x] **T2** `record-review` saves the snapshot; `revise-review` refuses, restores and re-applies → REQ-1, REQ-2, REQ-3, REQ-4, REQ-5, REQ-6, REQ-7, REQ-8, REQ-9
  - Files: scripts/bodhi-state, dev/eval/test_bodhi_state.py, skills/state-ops/SKILL.md (lint rule: its table names every subcommand)
  - Test: dev/eval/test_bodhi_state.py::t_revise_review_restores_a_wrong_incorrect, t_revise_review_lowers_a_wrong_correct, t_revise_review_refusals, t_revise_review_readers_match_honest, t_revise_review_keeps_the_wrong_entry, t_verify_implies_readers (revised state), t_golden_code_path (snapshot registered)
  - After: T1
  - Done when: `python3 dev/eval/test_bodhi_state.py` → 0 failed
- [x] **T3** Teach the skills when to revise → REQ-10, REQ-11
  - Files: skills/spaced-repetition/SKILL.md, skills/feynman-technique/SKILL.md, CLAUDE.md
  - Test: the live `grade-regrade` scenario (red today) and `grade-pushback` (must stay green)
  - After: T2
  - Done when: `dev/check.sh` → all hard checks pass
- [ ] **T4** `grade-regrade` asserts a `revise-review` call and joins `all` and `grading` → REQ-10
  - Files: dev/eval/test_detectors.py, dev/eval/assert_scenario.py, dev/eval/run-llm-evals.sh, dev/eval/README.md
  - Test: dev/eval/test_detectors.py::t_grade_regrade (a second `record-review` that reaches the right numbers some other way fails; a `revise-review` call passes)
  - After: T3
  - Done when: `python3 dev/eval/test_detectors.py` → 0 failed and `dev/check.sh` → all hard checks pass

## After the gate
At the release, run the live scenarios: `dev/eval/run-llm-evals.sh regrade`,
`BODHI_EVAL_RUNS=3 dev/eval/run-llm-evals.sh grade-pushback` and
`BODHI_EVAL_RUNS=3 dev/eval/run-llm-evals.sh predict-key`. Record the results in
`dev/eval/README.md`'s run table. Then `/shipkit:ship revise-a-grade`, and a CHANGELOG entry
with the release.
