# Tasks: Explain with a picture

## Gate
No task starts until the maintainer's hand-run trial of the learner-summarizes-first reading
loop, two or three sessions in the political-theory project, shows a concept that words alone
explained badly. That is the freeze's condition (b) (`CLAUDE.md`, *Feature freeze*). Record
what the trial found in `intake.md` under *Answers* before T1. If it shows no such concept,
set `spec.md` to `Status: dropped`.

## Tasks

- [ ] **T1** Detector tests and assertions for the picture rule → REQ-1, REQ-2, REQ-3, REQ-4
  - Files: dev/eval/test_detectors.py, dev/eval/assert_scenario.py
  - Test: dev/eval/test_detectors.py::t_kind_teach_picture (cites explain-with-a-picture/REQ-1 to REQ-4). Each side has a good and a bad synthetic run: exactly one `text`-fenced picture vs none or two; words in the same message vs a bare picture; a check without the picture vs one that repeats it; no `record-review` after a viewed-only picture vs one.
  - After: none
  - Done when: `python3 dev/eval/test_detectors.py` → 0 failed
- [ ] **T2** Live scenarios `kind-teach-picture` and `kind-teach-picture-viewed` on the writing fixture → REQ-1, REQ-2, REQ-3, REQ-4
  - Files: dev/eval/run-llm-evals.sh, dev/eval/README.md
  - Test: `dev/eval/run-llm-evals.sh picture` fails on today's KB. The tutor describes the argument's structure in words and shows no picture.
  - After: T1
  - Done when: `bash -n dev/eval/run-llm-evals.sh` passes and `dev/check.sh` passes
- [ ] **T3** Open and confirm the citations (Pashler et al. 2008; Mayer, *Multimedia Learning*), then write the KB section *Explaining with a picture* in place of "a diagram described in words", and the README Science line → REQ-1, REQ-2, REQ-3, REQ-4, REQ-6
  - Files: skills/evidence-kinds/SKILL.md, README.md
  - Test: the T2 scenarios, red before this task
  - After: T2
  - Done when: `dev/check.sh` passes, `BODHI_EVAL_RUNS=3 dev/eval/run-llm-evals.sh picture` → 3/3 on each side, `dev/eval/run-llm-evals.sh kind-fidelity` holds, and `wc -c < skills/evidence-kinds/SKILL.md` ≤ 14336
- [ ] **T4** Confirm code is unchanged → REQ-5
  - Files: dev/eval/README.md
  - Test: dev/eval/test_bodhi_state.py::t_golden_code_path, and `assert_code_never_loads_kinds` on the code transcript scenarios
  - After: T3
  - Done when: `dev/check.sh` passes and `dev/eval/run-llm-evals.sh kb-load` passes, recorded in the run table

## After the gate
`/shipkit:ship explain-with-a-picture`, then a CHANGELOG entry with the release.
