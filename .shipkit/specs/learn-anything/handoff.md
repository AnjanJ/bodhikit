# Handoff: BodhiKit "learn anything" (written 2026-10-19)

You are picking up work on BodhiKit at `/Users/anjan/code/bodhi-projects/bodhikit`, a Claude
Code plugin that is a Socratic tutor. The maintainer is Anjan, its one real learner so far. The
previous session planned and specced a major expansion. Nothing has been implemented yet. Read
this whole note before acting.

## 1. What BodhiKit is (the parts that matter for this work)

- **18 user commands and 18 knowledge bases**, all under `skills/*/SKILL.md`.
  - Commands have `user-invocable: true`. KBs have `user-invocable: false` and are loaded
    through the Skill tool as `bodhikit:<name>`.
  - There are 4 read-only agents in `agents/`.
  - `rules/learning-project.md` is injected by a SessionStart hook.
- **`scripts/bodhi-state`** (Python, stdlib only, about 3,000 lines, 27 subcommands) performs
  every tracking-JSON write. "Skills judge, the script records."
- **Tracking files** live in the learner's project:
  - `.bodhi/state.json`, `spaced-review.json`, `progress.md`, `plan/`
  - `learningWithBodhi/.bodhi-profile.json`
- **Hooks** (`hooks/hooks.json`):
  - SessionStart runs `scripts/bodhi-session-context.py` and injects the rule.
  - Stop runs `scripts/bodhi-stop-hook.py`, which calls `verify`. It blocks on verify
    *errors*, and on a missing daily revision sheet when this session ran `touch-state`.
- **Mastery (*Solid*)** has five conditions:
  - Bloom level of at least 4
  - three consecutive correct answers on due reviews
  - box 4 or higher
  - an explain-back (`feynmanPassed`) dated after the last miss
  - at least one `applied` correct since the last miss

  Only a due review moves the Leitner box (1/3/7/14/30 days). Bloom only ever rises.
- **Lint and tests:**
  - `dev/check.sh` is the lint and runs the deterministic suites: `dev/eval/test_bodhi_state.py`
    (536 pass), `test_stop_hook.py` and `test_openai_plugin.py`.
  - `dev/eval/run-llm-evals.sh` plus `assert_scenario.py` are LLM evals asserting on file state
    and transcripts. They cost tokens, so run them at release time, not per commit.
  - Fixtures live in `dev/eval/fixtures/`: a SQL project (`v2-project/sql-deep-dive`) and a
    political-theory project (`non-code-project/political-theory`).
- **OpenAI port:** `platforms/openai/build_plugin.py` generates the Codex and ChatGPT package
  from the same source. It turns each KB into a single file at `references/knowledge/<kb>.md`
  and **drops a KB's `references/` folder**.
- CLAUDE.md, loaded automatically, has the authoring contract: the 18 KB budget per SKILL.md,
  `--invoked-from=` chaining, "You MUST use the Agent tool" plus a `**Fallback:**` paragraph,
  and schema changes going KB, then script plus tests, then skills.

## 2. How Anjan works (follow this)

- Plan first, get approval, then **one commit per task**. Run `dev/check.sh` before every commit.
  Stage files by name, never `git add -A`. Never use `--no-verify`.
- Commit style: an `<area>: <what>` subject, then plain paragraphs on what and why, ending with
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Recent commits in `git log` show the
  tone.
- **Don't push unless told.** When told, push over HTTPS with gh's credentials, because the SSH
  agent has no keys:
  `git -c credential.helper='!gh auth git-credential' push https://github.com/AnjanJ/bodhikit.git master`
  Afterwards run `git update-ref refs/remotes/origin/master HEAD`.
- Anjan tags releases. LLM evals cost tokens, so ask before running them. Record their results
  in `dev/eval/README.md`'s run table.
- Shipkit rules are injected each session: spec-driven, decision records with falsifiability,
  test-first.
- When handing a spec task to an agent, give it `brief.sh`'s output unchanged and verify with
  `brief-verify.sh`. The shipkit plugin root is in the session context.
- Anjan likes direct recommendations with reasons, not surveys. Plain words. Learner-facing text
  never shows raw Bloom numbers or box numbers.

## 3. What happened in the previous session

1. **Codebase review.** It found two problems, and both are fixed, committed and pushed:
   - `983c1f1`: `dev/context-audit.sh` had its sections inverted since 1.18.0, so it measured
     KBs as if they were commands.
   - `dde609a`: `docs/outcomes.md` regenerated with five-part mastery wording, "Days since
     start", and the 1.23.0 delayed-quiz data (15–30 day gap: 1 of 4).
   - The push also published 11 earlier local commits, including `release: 1.24.1` (`cfe290b`).
     **v1.24.1 is not tagged.** Its evals hadn't run.
2. **Learner data.** It lives at `/Users/anjan/code/learnings/learningWithBodhi 1/learningWithBodhi/`
   (the path contains a space).
   - Every track was reset on 2026-08-31 (`d18e1d2`). Pre-reset data is readable at commit
     `55e265e` in that repo: frontend-mechanism, rails-mastery and system-design.
   - Live data: `ruby-object-model` (32 reviews) and `political-theory-foundations`.
   - Regenerate outcomes with `python3 dev/outcomes.py <dirs…> > docs/outcomes.md`, extracting
     the pre-reset tracks with `git archive 55e265e … | tar -x` into a scratch directory.
3. **The decision.** Make BodhiKit a learning tool for **any subject** (humanities, sciences,
   cooking, art, music, languages), mainly on Claude (Claude Code and Cowork), and also
   Codex/ChatGPT.
   - Where the tutor can't check the work, it trusts the learner's word, **labelled as the
     learner's account**.
   - **Hard constraint from Anjan: coding curricula must not change.** Code's applied evidence
     stays "code the tutor read and saw run".
4. **The spec was written with shipkit and both gates passed.** All four files are in
   `.shipkit/specs/learn-anything/`:
   - `intake.md`
   - `spec.md`: 43 EARS requirements, accepted at `dde609a`, status open
   - `design.md`: 9 decision records, corrected after review, approved in plan mode
   - `tasks.md`: T0–T34

   The project-wide record is `.shipkit/decisions/0001-learn-anything.md`, which supersedes the
   1.13.0 feature freeze for this work. `spec-check.sh . learn-anything` shows 0 gaps (38
   pending tests, 5 waived), and `decision-check.sh . --run` shows 0 fired and 0 errors.
   **`.shipkit/` is untracked and has never been committed.**

## 4. Anjan's answers (do not re-ask)

- **Goals:**
  - 3 or more outside learners on non-code subjects this quarter.
  - Delayed recall on non-code within 10 points of code.
  - Anjan's own non-code project reaching *Solid* on 5 or more concepts.
  - "Keep the coding as good as is and bring non-code up to par with the coding experience."
- **Phones and claude.ai:** they answered "1 and 3". Read as: desktop surfaces first, then full
  phone support as a later, separate spec that starts with a research spike. Until then REQ-39
  covers it: say that tracked study needs the desktop, and offer teaching with no schedule.
- **Performed skills:** spaced **practice reps plus knowledge questions**.
- **Releases:** ship the old A and B as one Release 1 (REQ-1–38, REQ-40). Release 2 is REQ-39 and
  REQ-41–43: hosts without files, outcomes per kind, repositioning, and the voice.
- **Requirements:** approved as written. Paths: `skills/, agents/, rules/, scripts/, hooks/, dev/,
  platforms/, docs/, README.md, GUIDE.md, CLAUDE.md, .claude-plugin/`.
- **REQ-22 amendment** (approved with the design): `observed` evidence on any non-code kind needs
  a real path inside the project that is not the exercise's key, its README or a tracking file.

## 5. The design, in short (details in design.md)

- **Four evidence kinds:** `code`, `problems` (checkable answers), `writing` (an argued written
  piece), `performed` (off-screen skills).
  - `state.json` stores `evidenceKind` and `moduleEvidenceKinds` (keyed by `norm_module_name`),
    written only by the new `set-evidence-kind`.
  - An absent kind means `code`.
- **Kinds reach the counters through a resolver** that `main()` installs once (`read_kinds`
  falls back to `code` and never fails a reader).
  - Only **three** places read `applied`: `_evidence_counts` (~`scripts/bodhi-state:2141`),
    `archive_history` (~2173) and `exposure_of` (~2256). They go through `applied_basis()` and
    `admits(kind, basis)`.
  - A test pins that nothing else reads `applied`.
  - Don't add parameters everywhere, and don't inject keys into concept dicts.
- **Evidence basis:** `appliedBasis` on history entries is written **only** for `inspected` or
  `reported`. Absent means `observed`.
  - `record-review --applied [basis]` uses `nargs='?'` with const `observed`, so bare `--applied`
    writes byte-identical output. The review verified this in argparse.
  - `reported` and `inspected` are allowed only on `performed`.
  - The archive keeps per-basis counts: `appliedEvidence` = observed; `appliedInspected`,
    `appliedReported` and `builtBy` are written only when non-zero.
- **The referee for non-code:** one folder per exercise. The tutor writes `answers.md` or
  `criteria.md` before the attempt, and the script checks a key sits beside the evidence.
  `rules/learning-project.md` gets an exception for that key in `exercises/`.
- **A practice rep is recorded as its graded debrief.** The debrief's grade moves the box, the
  rep is `reported`, and retention does not exclude these entries. Keep the helper distinct from
  `is_self_report`.
- **One new KB, `evidence-kinds`,** loaded only when the kind isn't code.
  - Agents must never name it: lint rule 2 would make them preload it into code sessions.
    Callers pass the instructions in the agent's prompt instead.
  - The plain-words table of the four kinds lives in `/learn`.
- **Read surfaces gain `evidenceKind`:** `session-brief`, `due`, `revision-brief`, `snapshot`
  (plus `evidenceKindRecorded`), `mastery`, `syllabus`, and the `gate-check` rows (using the
  prerequisite's own kind). There is no `reconfirmForm`.
- **Breakdowns:** `retention` and `export-anonymized` gain top-level `byKind` and `byBasis`.
- **Warnings, not errors:** an orphaned override or a basis without `applied` is a verify
  *warning*, so the Stop hook won't block on something no subcommand can repair.
- **Other choices:**
  - Safety goes in the learning-project rule, capped at 4,096 bytes.
  - `/review` handles non-code itself, and `code-reviewer` stays code-only.
  - Cowork gets a `.plugin` zip and a manual probe. Make no claim about Cowork until T29 passes.
- **Proof that code is unchanged (REQ-1):**
  - T1 builds a golden baseline by running `git show cfe290b:scripts/bodhi-state` over the
    fixtures. Reader JSON must match minus an allowlist of new keys; a scripted write sequence
    must leave the files byte-identical; writer stdout must match exactly.
  - Evals: the code groups at their recorded levels, plus an assertion that no code scenario
    loads `evidence-kinds`.

## 6. Traps (each one cost the reviewer time)

- **Budget:** `state-ops` and `state-schema` have 5 bytes of headroom, `teach` 158, `teach-back`
  188. Free space by **removing duplication** (T2–T4 list exact blocks). **Never move KB text
  into `references/`**: the OpenAI build drops it.
- **Lint pins you must not break:**
  - `check.sh:311` and `:342` grep exact source lines in `bodhi-state`.
  - Don't reword `state-ops` line 26; `neutralize()` in `build_plugin.py:77` matches it with a
    regex.
  - Keep `120 chars`, `reviewed within 30 days`, the backticked session types and the
    sure/mostly/guessing tokens.
- **More lint rules:**
  - Rule 14: the routing line must not sit in a skill's first 8 body lines.
  - Rules 22–24 and 37: the `/pair` and `/debug-together` offer lines stay in their phases. Gate
    them with a separate sentence.
  - Rule 3: `/review` keeps "You MUST use the Agent tool".
- **Counts and key sets:**
  - The README says `Knowledge Bases (18)`, and `test_openai_plugin.py:130–134` hardcodes 18.
    Both go to 19 in T13.
  - `test_bodhi_state.py:835` asserts the exact key set of `export.project`, so put the new
    export keys at top level.
- **Commands that never read `state.json`** (`due`, `mastery`, `retention`, `calibration`,
  `record-review`) need the resolver, and it must never fail them.
- **Fixtures:** the original political-theory fixture must stay **kind-less** (REQ-3). Make a
  copy for `writing`.
- **The SessionStart hook** only checks markers in the working folder; the Stop hook parses the
  Claude Code transcript format. Either may not hold in Cowork, so let the T29 probe decide.

## 7. Research context (cite it, don't re-research)

- **Market (October 2026):**
  - Claude's Learning mode, ChatGPT study mode and Gemini Guided Learning have no spaced
    schedule.
  - ChatGPT has flashcards (September 2026) but no review schedule.
  - Gemini study notebooks track Strengths and Focus areas.
  - Anki and RemNote schedule reviews but don't tutor.
  - **Gaps nobody fills:** tutor and spaced review together; a published definition of mastery;
    scheduled practice for performed skills; labelling how evidence was judged; confidence
    calibration; learner-owned state; a written safety policy for hazards.
  - Anthropic reportedly made Learning a skill in mid-2026. Unverified, from one secondary source.
- **Science:**
  - Spacing performed practice: Moulton et al. 2006 (surgery, randomized); Lee & Genovese 1988.
  - Interleaving motor skills is **contested** (Ammar et al. 2023/2024), so offer it, don't
    impose it.
  - Debriefs: Tannenbaum & Cerasoli 2013, d = 0.67.
  - Specific self-assessment questions beat vague ones: Zell & Krizan 2014, r ≈ .29.
  - Self-report is weak: Dunlosky & Rawson 2012.
  - Retrieval in non-STEM: Karpicke & Roediger 2008 (Swahili–English); Carpenter et al. 2009
    (history); Yang et al. 2021 (g = 0.50 across 18 subjects).
  - Interleaving maths: Rohrer & Taylor 2007.
  - Languages: spacing works for vocabulary and grammar (Kim & Webb 2022), but speaking needs
    production (Swain).
  - Photo or still-image feedback on cooking and drawing: **no controlled evidence**.
  - Safety: no standard exists for AI tutors on hazardous practical work. References: ACS RAMP,
    USDA safe-temperature chart.

## 8. Next steps

1. **Precondition (Anjan):** six uncommitted OpenAI files are Anjan's work in progress. Don't
   touch them; they overlap T13, T27 and T33. Ask Anjan to commit or stash them:
   - `dev/eval/test_openai_plugin.py`
   - `docs/openai-submission.md`, `docs/openai.md`
   - `platforms/openai/bodhikit/.codex-plugin/plugin.json`
   - `platforms/openai/bodhikit/references/openai-runtime.md`
   - `platforms/openai/build_plugin.py`
2. Ask whether to commit `.shipkit/` on its own or with T0.
3. Start **T0** (rewrite the CLAUDE.md feature-freeze section to point at decision 0001), then
   **T1** (the golden baseline). After that, work task by task in `tasks.md` order:
   - write the failing test first;
   - `dev/check.sh` must be green, with `t_golden_code_path` passing, before each commit;
   - one commit per task;
   - tick the box in `tasks.md`.
4. Run `spec-check.sh . learn-anything` after changing `tasks.md`, and `decision-check.sh . --run`
   after changing a decision.
5. Unknowns to keep visible, not assume away:
   - whether `python3`, the hooks and the working-folder markers hold in Cowork (T29);
   - the ChatGPT portal currently refuses skills-only submissions, so the listing is stuck at
     1.23.0;
   - Gemini and Antigravity are deferred.
