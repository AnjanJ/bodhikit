# Tasks: Learning vault (sprint 1)

One commit per task, each after `dev/check.sh` passes. Every new test cites its requirement as
`learning-vault/REQ-N` in its docstring. The tests named below are written first and fail
before the change.

- [x] **T1** Admit this spec past the feature freeze → (design: *the feature freeze is lifted for this spec only*)
  - Files: .shipkit/decisions/0006-learning-vault-past-the-freeze.md, CLAUDE.md
  - Test: none: prose. `CLAUDE.md` *Feature freeze* names decision 0006 beside 0001 and admits only this spec's sprint 1; read by the maintainer
  - After: none
  - Done when: `dev/check.sh` → "All hard checks passed."

- [x] **T2** The settings file and its record commands: `notes-show`, `notes-set` (recording and refusals only), `notes-offered`, and `verify` on the file → REQ-4, REQ-10, REQ-37, REQ-2
  - Files: scripts/bodhi-state, dev/eval/test_bodhi_state.py, skills/notes-setup/references/notes-file.md, CLAUDE.md (*Where things live* names the file), dev/check.sh (added while building: rule (h) wants every command named in `state-ops`, which REQ-11 freezes, so `notes-*` commands are named in `notes-file.md` instead)
  - Test: dev/eval/test_bodhi_state.py::t_notes_set_records_the_choice (REQ-4), ::t_notes_set_refuses_bad_vaults (REQ-37: missing folder, inside `learningWithBodhi/`, holding it, no profile; nothing recorded), ::t_notes_offered_once (REQ-10), ::t_notes_show_no_apps_on_cloud_chat (REQ-2: empty `appsOffered` under the marker), ::t_verify_checks_notes_file
  - After: T1
  - Done when: `python3 dev/eval/test_bodhi_state.py` → all pass, including `t_golden_code_path` and `t_verify_implies_readers`

- [x] **T3** The supported-apps table is held to the recorded probes → REQ-29
  - Files: scripts/bodhi-state, dev/eval/test_bodhi_state.py
  - Test: dev/eval/test_bodhi_state.py::t_notes_apps_need_a_probe_pass. It passes on today's table (no `model` entry), and fails on a synthetic table with a `model` entry and no matching PASS row in either probe document
  - After: T2
  - Done when: `python3 dev/eval/test_bodhi_state.py` → all pass

- [x] **T4** `syllabus --markdown` renders `Syllabus.md` → REQ-13, REQ-14, REQ-15, REQ-16, REQ-17, REQ-18, REQ-19
  - Files: scripts/bodhi-state, dev/eval/test_bodhi_state.py
  - Test: dev/eval/test_bodhi_state.py::t_syllabus_md_modules_in_order (REQ-13: planned, then unplanned), ::t_syllabus_md_words_match_module_row (REQ-13: every status, tier and kind phrase in the Python tables appears in `skills/progress/references/module-row.md`, and the reverse), ::t_syllabus_md_concepts (REQ-14: outcome clause and date, or "parked"), ::t_syllabus_md_due_week (REQ-15: due at −3, 0, +7 and +8 days; the first three listed earliest first, the first two as `due now`, the last absent), ::t_syllabus_md_no_internals (REQ-16: `assert_no_internal_names`, and no Bloom or box number), ::t_syllabus_md_deterministic (REQ-17: two runs give the same bytes), ::t_syllabus_md_header (REQ-18: both facts before the first `##`), ::t_syllabus_md_by_your_account (REQ-19)
  - After: T3
  - Done when: `python3 dev/eval/test_bodhi_state.py` → all pass, `t_golden_code_path` unchanged

- [x] **T5** `notes-sync`, and the first full copy when a vault is recorded → REQ-12, REQ-20, REQ-21, REQ-22, REQ-23, REQ-24, REQ-25, REQ-6
  - Files: scripts/bodhi-state, dev/eval/test_bodhi_state.py, skills/notes-setup/references/notes-file.md (added while building: check.sh rule (h) wants `notes-sync` named there)
  - Test: dev/eval/test_bodhi_state.py::t_notes_sync_files_only (REQ-12), ::t_notes_sync_copies_syllabus (REQ-20), ::t_notes_sync_sheet_rule (REQ-21: a new sheet copied, today's replaced, an earlier day's edited in the vault left alone), ::t_notes_sync_courses_index (REQ-22), ::t_notes_set_vault_copies_every_course (REQ-23: active and completed), ::t_notes_sync_stays_in_home (REQ-24: sentinel files outside the home unchanged; a second run changes no mtime; a course name that resolves outside the home is refused), ::t_notes_sync_reads_nothing_back (REQ-25), ::t_notes_off_writes_nothing (REQ-6: earlier files remain, no new writes)
  - After: T4
  - Done when: `python3 dev/eval/test_bodhi_state.py` → all pass

- [x] **T6** The Stop hook runs `notes-sync` at session close and makes the one-time offer → REQ-7, REQ-8, REQ-9, REQ-11, REQ-26, REQ-27, REQ-38
  - Files: scripts/bodhi-stop-hook.py, hooks/hooks.json, dev/eval/test_stop_hook.py, scripts/bodhi-state and platforms/openai/build_plugin.py (added while building: `notes-sync` takes its locks only when it will write, so a learner with no notes file gets no new lock file; the OpenAI build renames the offer's command for Codex)
  - Test: dev/eval/test_stop_hook.py::t_no_notes_file_same_as_before (REQ-7: no notes file and no offer moment gives the same output and the same files as before), ::t_offer_after_learn (REQ-8), ::t_offer_after_continue (REQ-9: both the typed `<command-name>` form and the `Skill` call form), ::t_offer_not_with_a_choice (REQ-8, REQ-9), ::t_no_offer_in_cloud_chat (REQ-38), ::t_existing_skills_unchanged (REQ-11: no `skills/*/SKILL.md` that `v1.26.1` shipped names the notes feature; changed while building from a byte comparison with `v1.26.1`, which failed on the maintainer's unrelated citation fix `131cf5b` and would block other specs), ::t_copy_failure_reported (REQ-26: read-only vault; exit 0, no block, `systemMessage` names the failure), ::t_saved_only_after_success (REQ-27)
  - After: T5
  - Done when: `python3 dev/eval/test_stop_hook.py` → all pass, and `dev/check.sh` → "All hard checks passed."

- [x] **T7** The `/bodhikit:notes-setup` skill, with its transcript assertion and a live scenario → REQ-1, REQ-2, REQ-3, REQ-5, REQ-6
  - Files: skills/notes-setup/SKILL.md, dev/eval/assert_scenario.py, dev/eval/test_detectors.py, dev/eval/run-llm-evals.sh; added while building, because `dev/check.sh` fails the moment a 19th skill exists: README.md (the `Skills (19)` count and its row), dev/eval/test_openai_plugin.py (the 19-skill count), dev/guide-writer/references/commands.md (its entry), skills/notes-setup/references/notes-file.md (the Stop-hook line names the ChatGPT path); and scripts/bodhi-state with dev/eval/test_bodhi_state.py (the notes commands accept the learning folder as `--project`)
  - Test: dev/eval/test_detectors.py::t_notes_setup_detector, on canned transcripts that pass and fail each point: the question lists the apps, "I use none" and "files only" (REQ-1); exactly one suggestion with a reason (REQ-2); what, where, sync, optional and off said before `notes-set` runs (REQ-3); with a choice on record, the current choice shown and change or off offered (REQ-5); on off, the learner told the files stay and will not be refreshed (REQ-6)
  - After: T2
  - Done when: `python3 dev/eval/test_detectors.py` → all pass, and `dev/check.sh` → "All hard checks passed." (the 18 KB budget and the skill lint included)

- [x] **T8** The OpenAI adapter states the sync and offer steps where no hook runs → REQ-36, REQ-38
  - Files: platforms/openai/bodhikit/references/openai-runtime.md, dev/eval/test_openai_plugin.py
  - Test: dev/eval/test_openai_plugin.py check "adapter: the close procedure runs notes-sync and makes the one-time offer in local state mode, and neither in conversation-only mode" (cites learning-vault/REQ-36, REQ-38)
  - After: T6
  - Done when: `python3 dev/eval/test_openai_plugin.py` → all pass

- [x] **T9** Both packages carry the skill and the commands; the counts read 19 → REQ-34, REQ-35
  - Files: README.md, GUIDE.md, .claude-plugin/marketplace.json, docs/openai.md, dev/guide-writer/references/commands.md, dev/eval/test_openai_plugin.py, dev/eval/test_cowork_plugin.py
  - Test: dev/eval/test_openai_plugin.py check "build: reports 19 user skills" and "bundle carries notes-setup and the notes commands" (REQ-35); dev/eval/test_cowork_plugin.py check "package carries notes-setup and the notes commands" (REQ-35); dev/eval/test_openai_plugin.py check "docs: each REQ-34 file names /bodhikit:notes-setup and counts 19 skills, and docs/openai-submission.md is unchanged" (REQ-34)
  - After: T7, T8
  - Done when: `dev/check.sh` → "All hard checks passed."

- [ ] **T10** `PRIVACY.md` says what the notes copy does → REQ-33
  - Files: PRIVACY.md
  - Test: none: REQ-33 is `[untested: prose]`; read by the maintainer
  - After: none
  - Done when: `dev/check.sh` → "All hard checks passed."

## After the gate
These are release steps, not tasks:
- Run the live `notes-setup` scenario once (`dev/eval/run-llm-evals.sh notes-setup`, which costs tokens, so ask first) and record it in `dev/eval/README.md`.
- Do the hand checks and record each in `dev/eval/README.md`:
  - A Stop hook's `systemMessage` is shown in the Claude Code terminal, and in Codex.
  - In Obsidian, the home appears, `Courses.md` opens each syllabus, and a revision sheet reads as it does on disk.
- Check these decision clauses:
  - `notes-sync` takes no more than 5 s on the largest fixture.
  - The `<command-name>` marker is still present in a fresh `/continue` eval transcript.
- Release as usual: CHANGELOG, the version bump in both manifests, the code eval groups at their recorded levels, `t_golden_code_path`, and the ChatGPT re-upload (`CLAUDE.md` *Release checklist*).
