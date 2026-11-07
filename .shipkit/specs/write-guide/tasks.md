# Tasks: Write a learner guide

Each task is one commit on branch `write-guide`, made after `bash dev/check.sh` passes. No push.

- [x] **T1** The repository ignores `output/`; the guide-writer test suite exists and `dev/check.sh` runs it → REQ-4
  - Files: .gitignore, dev/eval/test_guide_writer.py, dev/check.sh
  - Test: dev/eval/test_guide_writer.py::t_output_is_ignored
  - After: none
  - Done when: `python3 dev/eval/test_guide_writer.py` → all pass, and `bash dev/check.sh` → "guide-writer test suite passed"
- [x] **T2** `SKILL.md` with the eight phases, typed-only invocation, kept out of every package → REQ-1, REQ-2, REQ-5, REQ-6, REQ-7, REQ-8, REQ-10, REQ-12, REQ-13, REQ-14, REQ-17, REQ-22
  - Files: dev/guide-writer/SKILL.md, dev/eval/test_guide_writer.py
  - Test: dev/eval/test_guide_writer.py::t_typed_only, dev/eval/test_guide_writer.py::t_not_in_any_package
  - After: T1
  - Done when: `python3 dev/eval/test_guide_writer.py` → all pass
- [x] **T3** The command reference names exactly the learner commands, with no internal names → REQ-9, REQ-16
  - Files: dev/guide-writer/references/commands.md, dev/eval/test_guide_writer.py
  - Test: dev/eval/test_guide_writer.py::t_commands_match_skills, dev/eval/test_guide_writer.py::t_no_internals
  - After: T2
  - Done when: `python3 dev/eval/test_guide_writer.py` → all pass
- [x] **T4** Platform facts, each with a source and a checked date → REQ-11, REQ-15
  - Files: dev/guide-writer/references/platform-facts.md, dev/eval/test_guide_writer.py
  - Test: dev/eval/test_guide_writer.py::t_facts_dated_and_sourced
  - After: T3
  - Done when: `python3 dev/eval/test_guide_writer.py` → all pass
- [x] **T5** The guide template, with no internal names → REQ-16
  - Files: dev/guide-writer/references/guide-template.html, dev/eval/test_guide_writer.py
  - Test: dev/eval/test_guide_writer.py::t_no_internals
  - After: T4
  - Done when: `python3 dev/eval/test_guide_writer.py` → all pass
- [x] **T6** The intake question bank and the lessons file, naming no real learner → REQ-7, REQ-18
  - Files: dev/guide-writer/references/intake-questions.md, dev/guide-writer/references/lessons.md, dev/eval/test_guide_writer.py
  - Test: dev/eval/test_guide_writer.py::t_referenced_files_exist
  - After: T5
  - Done when: `python3 dev/eval/test_guide_writer.py` → all pass, and every file `SKILL.md` names exists
- [x] **T7** `render.sh`: PDF and DOCX beside the HTML and a contact sheet; refuses a folder inside the repo; names a missing tool → REQ-19, REQ-20, REQ-21
  - Files: dev/guide-writer/scripts/render.sh, dev/eval/test_guide_writer.py
  - Test: dev/eval/test_guide_writer.py::t_render_outputs, dev/eval/test_guide_writer.py::t_render_refuses_repo, dev/eval/test_guide_writer.py::t_render_names_missing_tool
  - After: T6
  - Done when: `python3 dev/eval/test_guide_writer.py` → all pass (the output test skips, saying which tool, where one is missing)
- [x] **T8** CLAUDE.md says where the skill lives and how to link it; the local link is made → REQ-3
  - Files: CLAUDE.md
  - Test: manual — after `ln -s ../../dev/guide-writer .claude/skills/write-guide`, a new session lists `/write-guide` in the `/` menu
  - After: T7
  - Done when: `bash dev/check.sh` → passes, and `ls -l .claude/skills/write-guide` → points at `../../dev/guide-writer`

## After the gate
- `/shipkit:ship write-guide`, then merge `write-guide` into `master` when the maintainer says so.
- The first real `/write-guide` run is the manual check of REQ-5–8, 10, 12–15, 17 and 22; record what it found in `intake.md` under *Answers*.
