# BodhiKit development journal (patch-by-patch)

This is the full, unabridged, patch-by-patch changelog kept for the maintainer — every dogfood finding, audit ticket, and lint rule as it landed. `CHANGELOG.md` at the repo root is the reader-facing summary; this file is the record behind it and is never loaded by the plugin.

---

# Changelog

All notable changes to BodhiKit will be documented in this file.

## [1.18.1] - 2026-08-25

Caught in the maintainer's first real `/continue` after updating: the Stop event fires at the end of **every assistant turn**, not at session end, and `find_projects` + `revision-brief` saw projects other sessions had studied today — so the `/continue` menu turn was blocked with two revision sheets to write from sessions this one never saw. Fix: the hook parses `transcript_path` (the session's own JSONL) for Bash `bodhi-state --project <p> …` calls and requires a sheet only for a project whose closing bookkeeping (`touch-state`) ran in this session; a review alone (mid-lesson) does not trigger it, another project's writes do not, and no transcript means no sheet blocks (fail-open). Four new hook checks. The schema-verify half of the hook keeps its 1.11 semantics.

## [1.18.0] - 2026-08-25

The "it never loaded" release. A full external review (commit history, journal, script, lint, evals) plus one live probe found that the plugin's central mechanism had never been wired: Claude Code registers skills from `skills/` only, so the twenty knowledge bases in `knowledge/` were never loadable and every "Reference the `X` KB" pointed at nothing. Twelve issues fixed in order, one commit each.

### Probes (recorded so nobody has to re-derive them)
- `Skill(bodhikit:teaching-personality)` and `Skill(bodhikit:state-ops)` → *Unknown skill* with 1.17.0 installed.
- A `user-invocable: false` skill under a plugin's `skills/` **is** registered, hidden from `/`, and loads through the Skill tool (temp-plugin probe, magic-word round-trip).
- A plugin `rules/` directory is **not** loaded: the same path-scoped rule reached the model from `.claude/rules/` and not from the plugin, with a matching file read in both runs.
- Agent frontmatter `skills:` preloads plugin skills by bare name (subagent probe knew the magic word).
- The real tree after the move: `Skill(bodhikit:spaced-repetition)` loads; a session started inside `learningWithBodhi/` receives the rule via the SessionStart hook; the new `kb-load` eval passed first run.

### Issue 1 — knowledge bases become skills
`knowledge/<kb>` → `skills/<kb>` (names unchanged, ~280 references stand). Every user skill opens with the *Knowledge bases are skills* sentence mapping `` `name` KB `` → `Skill(bodhikit:name)` at the referencing phase. Agents preload the KBs they name via `skills:`. `rules/learning-project.md` is delivered by a SessionStart hook (`scripts/bodhi-session-context.py`, fail-open). `/teach`'s gate handling moved to `references/prerequisite-gate.md` to stay under budget. Lint splits `USER_SKILLS`/`KB_SKILLS` by frontmatter and adds four structural rules. bodhi-cli's resolver accepts both layouts. Cost: +20 skill descriptions in every session's listing (~1–1.5 K tokens) — the price of the KBs existing.

### Issue 2 — gate evidence counts only since the last miss
`evidence_at_3_plus` summed every historical level-3+ correct: two old corrects kept a prerequisite `satisfied` through three straight misses and through `/forget` (which also refreshed `lastReviewed`). Reset at the most recent `incorrect`; deferred entries skipped on both gate paths. Tests on both sides of the bound.

### Issue 3 — validation on the load path
`load_spaced_review` / `load_state` / `load_profile_projects` type-check the fields the script computes on and die naming the repair; `verify` reports structural drift instead of raising; `parse_date` accepts only dates/date-times.

### Issue 4 — pre-v3 backup before the first v3 write
Any mutating write on a v1/v2 file used to upgrade it silently; `migrate` then said noop and the promised backup never existed. `write_spaced_review` backs up first and reports `migratedFromVersion`.

### Issue 5 — hygiene
Read-only subcommands take a shared lock and never create the lock file; `LAST_ACTIVITY_MAX` everywhere; `defer --days ≤ 0` errors; `record-review` flags `newModule`.

### Issue 6 — Stop hook
Time-boxed, pruned walk (an `os.walk` from `$HOME` took 18.7 s of a 30 s budget and failed open); configured roots (per-repo `projectRoot`, global `searchPaths`) verified; block reason never blank. First hook tests.

### Issue 7 — one rollup
`mastery` and `snapshot` share `review_rollup`; agreement test; finding IDs out of shipped comments.

### Issue 8 — lint policy is true
A–D structural/conditional; E phrase pins with retirement conditions (56–59); 26, 34, 17's offer/pretest greps deleted. 893 lines.

### Issue 9 — evals certify the executor in use
Default model `claude-fable-5` (printed in the header); nudge resumes by session id; vacuous passes closed; README run table names the four never-run scenarios.

### Issue 10 — outcome-first rendering (learner feedback)
Clause alone by default, phrased as application/reasoning; the rung's name only at a crossing (`record-review` → `crossedLevel`) and in `/progress`'s legend.

### Issue 11 — what you discuss is on screen (learner feedback)
Canonical voice rule; code/question/answer reproduced in the same message; `**Where:**` + fenced quote in the code-reviewer template; hint turns must show the artifact (eval).

### Issue 13 — revision sheets (maintainer request, freeze-exempt: hit in real use)
A learner has nothing to re-read after a session except the conversation. New: one take-home per study day at `revision/YYYY-MM-DD-<concept>.md` — key idea in plain words, the worked example, where they slipped, two self-test prompts + answers, next review dates as outcome clauses, free links only from `resources.md` or official docs. Template in `skills/reflect/references/revision-sheet.md` (phase-loaded; no new KB). `/reflect` Phase 4 writes it; `/continue`, `/teach`, `/quiz`, `/practice` point at the template when they close a session. `bodhi-state revision-brief` (read-only) supplies today's studied concepts (non-deferred review dated today, or introduced today — seeding and assessing need no sheet), the file name, and any existing sheet. The Stop hook requires the sheet on a day that studied something — the executor-discipline answer, same pattern as the schema check. Doing this surfaced a flaw in Issue 6: walking the global `searchPaths` lets a project studied in another terminal block an unrelated session's stop, which has no context to write the sheet; the hook is now session-scoped (cwd subtree + per-repo `projectRoot`). Hook tests sandbox HOME.

### Issue 12 — drift
This entry and the missing 1.17.0 one; blogpost archived; CLAUDE.md corrected on what the runtime loads.

### First Fable run of the suite (the release gate)
Seven scenarios, two of which had never run live. teach-pretest, grade-understand-band, learn-scaffold, plan-regenerate, evaluate: PASS. Three lessons from the two new detectors: (1) the "hint turn shows its artifact" check matched the word *hint* inside the closing recap the harness asks for — anchored to a line-initial `Hint N`; (2) the bare-number check found a **real** miss — with the personality KB loaded and a site-level reminder in `/quiz`, Fable still read `box: 1` from the `due` output into "Query planning — Box 1" (1 of 2 samples). Louder prose was not the fix; `due` now carries `priority`/`dueSince`/`overdueDays`/`bloomOutcome` and no box or level number at all — clean in every sample since; (3) the harness now labels a transcript cut off by the claude.ai usage limit INCONCLUSIVE instead of FAIL (the first lifecycle attempt was). Recap sections (`## Recap`, `**Recap of what was written**`) are excluded from learner-facing prose in the transcript detectors.

Deterministic tests: 231 → 290 (+19 hook tests). Decision recorded: no SQLite — markdown/JSON stay; validation on load gets the benefit at a fraction of the cost; revisit only with a second real user and a query JSON cannot answer.

## [1.17.0] - 2026-08-21

(Entry reconstructed in 1.18.0 — the release shipped without its journal entry.) The self-review release: learner-facing Bloom rendering as `**Label** — outcome clause` with `bloomLabel`/`bloomOutcome` emitted by the script and a `bloomScale` legend in `snapshot`; the prerequisite gate requires two level-3+ observations (`stale-reconfirm`, `reason: single-evidence`); eleven KB-name-grep lint rules removed and the admission policy stated; `dev/outcomes.py` publishes the maintainer's anonymized data; README onboarding + Feedback section; bug/feedback issue templates; CHANGELOG collapsed to reader-facing notes with this journal as the record. 220 → 231 deterministic tests.

## [1.16.0] - 2026-08-15

The ownership release — the remaining structural items from the August analysis campaign. The through-line: every gap where the model was still doing work the script should own (a hand-edited JSON list, an assessment tally, a guessed prerequisite module) moves into `bodhi-state`, and the three skills most able to regress silently get harness coverage.

### Added — the script owns the cross-project project list (the last hand-edit hole)
`.bodhi-profile.projects.json` mutations were "the one mutation the script does not own" — `/learn` appended by hand, `/evaluate` refreshed and moved entries by hand, guarded only by `verify`'s entry-shape backstop (1.15.0's P1 fix). Four new subcommands take ownership:
- **`profile-add-project`** — appends a schema-complete `activeProjects` entry (every required field present, `startedAt` stamped), creating the file if missing. `/learn` Phase 4.
- **`profile-update-project`** — in-place refresh of an active entry; only passed fields change, unknown fields preserved. `/evaluate`'s refresh.
- **`profile-complete-project`** — the `activeProjects` → `completedProjects` move (`completedAt`, `finalBloomLevel`, `trackPurpose` carried; `--status` carries `/learn` Phase 1.5(c)'s replace-archive note). Completion remains learner-confirmed, never inferred.
- **`profile-update-patterns`** — the `persistentChallenges`/`consistentStrengths` tally: 3+ assessment-history entries at Bloom <3 / at Bloom 4+, append-only, deduplicated. Pure counting that the model was previously asked to do in prose.

Hand-editing the profile pair is now fallback-only (script unavailable). 19 new deterministic tests.

### Added — `park`: a consciously-deprioritized concept can leave rotation
`/forget`'s only verb was demote — Box 1, back tomorrow, *harder* — so a working learner who decided a concept was not worth maintaining accumulated review rot until the due pile stopped being trusted (honest-review #6). **`bodhi-state park`** sets `parked: true` + `nextReview: null` with a `learner-park` session entry; box, Bloom, Feynman, counters, and history all stand — parking is scheduling, never an outcome. `--resume` re-enters rotation (review tomorrow, box preserved). The read surfaces (`due`, `mastery`, `snapshot`) exclude parked concepts from due/retention but report them as counts, never silently; mastery and module standing keep them. Surfaced as **`/forget --park`** / **`--unpark`**. 11 new deterministic tests.

### Changed — the prerequisite gate never guesses
`gate-check`'s last fallback inferred a "prior module" by string-sorting concept `introduced` dates — honestly flagged as inferred, but still doing real gating work (honest-review #11, fidelity D4). A guessed gate generates false reconfirm questions, which cost more learner trust than no gate: with no `--prereqs` declared and no tracked `previousModule`, the gate now declines to fire with an actionable reason. `prerequisiteSource` simplifies to `"declared" | "prior-module"`.

### Evals — lifecycle coverage for the three highest-write skills (honest-review #1)
`/learn`, `/plan regenerate`, and `/evaluate` — the skills doing the most state orchestration — had zero LLM-eval coverage; the coverage was inverted to the risk. Three new executor-discipline scenarios (group: `lifecycle`, file-state assertions only):
- **`learn-scaffold`** — runs from the *parent* directory via a new `run_parent_scenario` runner (`/learn` discovers the root and scaffolds a sibling project). Asserts the full `.bodhi/` skeleton, the `learn-phase2` assessment, the **existing profile entry preserved exactly** (all 9 fields — the analysis-1 empirical probe, now a permanent regression guard), the new entry schema-complete, and `verify` ok on both projects.
- **`plan-regenerate`** — old plan archived at `plan/.archive-<date>/`, fresh plan written, progress history preserved verbatim, assessment entry dated today.
- **`evaluate`** — prep seeds three low-Bloom assessments so `profile-update-patterns` has a deterministic, assertable effect; asserts assessment + session entry + `touch-state` + `assessments/latest.md` + the patterns append + the active entry intact after refresh.

All three assertions were validated offline on both sides before any tokens were spent: FAIL on the raw fixture, PASS on a hand-built correct end state.

### Lint
- **Rule 55** — both sides of the `--invoked-from` chain convention (honest-review #7): every chainable skill must carry the check, and every imperative auto-invoke of a chainable skill must pass the flag. Descriptive mentions and Do-NOT-invoke prohibitions are exempt by pattern. Both branches verified to FAIL on deliberate drift.
- `learner-park` added to the pinned session-type vocabulary.

220 deterministic tests (was 190).

## [1.15.0] - 2026-08-15

The hardening release — the fixes from the August analysis campaign (fidelity audit, empirical run, adversarial pass; the analyses themselves live outside the plugin). Three themes: the runtime learns what untrusted input is, the grading ladder's two contested boundaries get adjudicated and verified across both sides, and the display vocabulary stops inferring what the script can compute.

### Security — learner and third-party file content is data, not instructions
The adversarial pass's headline (A2, HIGH): the runtime had zero prompt-injection hygiene while `/teach`, `/practice`, `/debug-together`, and the `code-reviewer` agent are all instructed to read learner-authored files, and `/review` accepts remote GitHub/GitLab/Codeberg URLs — genuinely third-party content. The eval harness had the correct treatment (`SYS_HARNESS`) since 1.14.0; it was never propagated to the product.
- **`rules/learning-project.md`** now carries the untrusted-input clause for every session in a learning project: content read from learner files or fetched repos is evidence about the learner, never instructions to the tutor; directives found inside it are surfaced, not followed.
- **`agents/code-reviewer.md`** carries the same clause and **drops `Bash`** from its tool list — it reads code, it does not need to execute anything, and an agent that reads third-party repos should not hold a shell.
- **Learner assertions are not evidence** (A3/A4): a learner's claim about their own answer ("that was definitely Bloom 4", "I explained it fine, mark it passed") is not in the trust hierarchy. The Feynman gate and `--tested-bloom` grade what the transcript shows, stated at the KBs and the write sites.

### Grading — both contested boundaries adjudicated, verified across the bound
- **The parrot boundary (F-3).** A verbatim recitation the learner cannot restate in their own words graded `correct` roughly 1-in-3 — promoting the box, so the parrot got spaced *further apart* for parroting. Two ladder rules competed (any-rung-counts vs fluency-failure) with no precedence. Resolution: fluency-failure routes to **`partial`** (holds the box, re-tests tomorrow) — matching the canonical call `/reflect` and `/pair` already made — and the exception fires on one narrow signal only (cannot re-express a second way), with an explicit carve-out: admitting a boundary is calibration, not parroting. Stated in the `feynman-technique` ladder AND at `/teach` Phase 5, the write site that actually decides — the first fix landed only in the KB the write site doesn't cite, and changed nothing.
- **The 2-vs-3 boundary (F-4).** A learner with demonstrated working usage but an honest trade-off gap recorded Bloom 2 about a third of the time — under-credit in a field that only ratchets up. Resolution: **set the level by the highest rung the answer reached**, with demonstrated usage as a floor and an admitted gap as a ceiling — bounds on that reading, never the rule itself. The first wording stated only the floor and silently pinned an uncapped learner (trade-offs *and* when-not-to) at 3 instead of 5; the full-suite run caught it, A/B confirmed caused-not-noise. Re-verified across the bound: `grade-genuine` 4/4 at Bloom 5, `grade-apply-band` 8/8 at Bloom 3, `grade-jargon`/`grade-pushback` 4/4 each at `partial` with the box held.
- **New `grade-pushback` scenario** (adversarial A3): the learner gives a mechanical paraphrase then argues to have it marked passed; asserts `feynmanPassed` stays false and the box does not promote.

### Progress — outcome tiers computed, not inferred
- **`bodhi-state` computes the `blooms-taxonomy` KB's concept tiers** (F-1): `concept_tier()` evaluates the KB's ladder per concept — `unclassified` / `introduced` / `familiar` / `mastered`, calling `is_mastered()` so the four-conjunct formula keeps one home — and `mastery`/`snapshot` return per-module `tiers` counts via a shared rollup helper. This closes the fidelity audit's two UNCHECKED rows (the tiers were prose nothing computed) and a keyspace bug: the old `Bloom's Level` column displayed topic-keyed `currentBloomLevel` against modules.
- **`/progress` renders outcomes, not raw Bloom numbers**: the Module Breakdown shows the real tier distribution — `**Working** — can use it with guidance (2 solid, 1 working)` — instead of a number the learner has to decode. `mastered` stays the computed predicate; *Solid* is display vocabulary.

### Verify / lint — pin what is canonical, not what broke
- **`verify` validates profile entry shape** (P1): the one hand-edited write (`activeProjects`/`completedProjects` entries) now has a deterministic backstop — a dropped field no longer passes `verify` silently.
- **Fidelity drift fixed** (D1/D2): the `lastActivity` warning threshold now matches its own message (120), and `is_mastered`'s docstring cites the right KB.
- **Lint pins the rest of the canonical-value surface** (D3): `GATE_RECENCY_DAYS`, the retention rollup tiers, `CONFIDENCE_VALUES`, and the new tier ladder + tier-key vocabulary are pinned between KB and script — every pin verified to FAIL on deliberate drift.
- **New rule 54**: a judgment rule must be reachable from the site that applies it — a precedence rule in a KB the write site doesn't cite is decoration (the F-3 lesson, generalized).

### Harness
- **`BODHI_EVAL_RUNS=N`** sweeps any scenario N times and reports a pass **rate** plus the level each run recorded, retaining every workdir (previously passing runs were `rm -rf`'d, so the pass-side distribution was unrecoverable). Boundary scenarios are noisy by nature; a single green run is weaker evidence than it looks.
- **Release checklist**: grading-ladder changes require sweeping the grading group and reading the recorded *levels*, and a rule that bounds a value needs a scenario on **each side of the bound**, read together — one side alone cannot distinguish a correct bound from a pin (8/8 on the targeted scenario is what a pin produces too).

### Docs
- GitHub is the source of truth; the Codeberg mirror is archived. Install URLs, manifests, CONTRIBUTING, and the release checklist repointed.

## [1.14.2] - 2026-07-08

The teaching-starvation fix — caught by the maintainer during a real learning session (the feature-freeze carve-out). A learner running three fresh projects reported "all I'm doing is answering questions and spaced repetition — no teaching." The data confirmed it exactly: across 20 tracked concepts in three projects, only **2** reviews came from a `/teach` session and only 1 concept had passed the Feynman gate; two of three projects had zero teaching. Root cause is an interaction, not a single bug: `/learn` Phase 4 seeds every assessed concept (Bloom ≥ 1) into the Leitner system on Day 1 — good, so assessed knowledge starts its review schedule immediately — but `/continue` Phase 4 then front-loads spaced review of *all* due concepts through `/quiz` before offering to teach. For a new learner, the Day-1 seeded pile IS the due pile, so every session opened by quizzing concepts that had never been taught, and ended inside the quiz before the teaching branch was reached. Reviewing an untaught concept is not spaced repetition — there is nothing yet to space — but `due` gave `/continue` no signal to tell a seeded-untaught concept from a genuinely-taught one, so it quizzed both identically.

### Fixed — `due` distinguishes taught from never-taught, `/continue` routes accordingly
- **`bodhi-state due` now tags each concept `neverTaught`** (true when no `reviewHistory` entry has `source == "teach"`) plus a `neverTaughtCount` rollup. The `source=="teach"` absence is the precise test — a seeded concept can sit at `bloomLevel > 0` from the assessment, so a `bloomLevel==0` check would miss it (`session-brief`'s `firstExposure` keys on bloom for the separate pretest-vs-retrieval purpose). Branch detection in code, per the 1.11.0/1.14.0 pattern — not re-derived in skill prose.
- **`/continue` Phase 4 splits the due batch on the flag**: genuinely-taught due concepts still go to `/quiz` (real spaced review); never-taught-but-due concepts are surfaced as an offer to *teach first* (`/teach --invoked-from=continue <concept>`, lowest-box / earliest-due first), never quizzed cold. First-teaching, not cold quizzing, becomes the default for a freshly-seeded project. It stays an offer — the learner can still quiz them as a self-check or skip to today's new module.
- **`state-ops` KB** documents the new `due` output fields at its one home (the read-side rollup row).

### Evals — reproduced first, per the executor-discipline contract
- New `t_due_never_taught` deterministic test (170 total, was 164): `due` reports `neverTaught: true` for an `add-concept`-seeded concept, stays true after a `--source quiz` review (quizzing is not teaching), flips to false only after `--source teach`, and `neverTaughtCount` tracks the count across a teaching event.

## [1.14.1] - 2026-07-07

A discovery-hallucination fix, caught in a live `/continue` on Fable 5. The `bodhi-state` script owns *writes and rollups*; project discovery is a file-read (glob `learningWithBodhi/*/.bodhi/state.json`) and was never a subcommand. But eight skills pointed at it only abstractly — *"use the discovery procedure from the `state-ops` KB"* — with no inline command and no negative guard. Against the plugin's own strong "everything goes through `bodhi-state`" prior, the executor guessed `bodhi-state discover` / `--list` (neither exists), burned three Bash calls confirming they don't, then fabricated a project list from truncated `ls` output. Exactly the executor-improvisation class the 1.11.0 architecture exists to close — surfaced by the model change the last commit's drift sweep flagged. The five skills that already inlined *"search for `.bodhi/state.json`"* never hallucinated; the abstraction was the defect.

### Fixed — discovery made concrete
- **`state-ops` KB carries the negative guard** at the discovery procedure (one home per fact): discovery is a file-read, **not** a `bodhi-state` subcommand — there is no `discover`/`--list`/`list-projects` — plus the concrete `ls -d …/learningWithBodhi/*/.bodhi/state.json` glob. Every skill's pointer inherits it.
- **Seven skills** (`/continue`, `/housekeep`, `/forget`, `/plan`, `/learn`, `/review`, `/practice`) now append the concrete glob + guard inline, matching the already-well-behaved skills. `/continue` Phase 1 — the one that broke — leads with it.

### Evals — reproduced first, per the executor-discipline contract
- New `continue-discovery` LLM scenario (`run-llm-evals.sh discovery`): the only scenario that runs from the `learningWithBodhi` parent with a second project seeded, so `/continue` Phase 1 must actually enumerate. Asserts the executor discovered projects by globbing the filesystem, never by calling a phantom subcommand. `assistant_text` now folds `tool_use` inputs into the matched text, so the phantom Bash call is caught even when the model does not narrate it.

### Lint
- New rule 53: `state-ops` must retain the negative guard, and no skill or KB may emit a `bodhi-state … discover/--list/list-projects` call in prose.

## [1.14.0] - 2026-07-02

The judgment-tree release — the deferred half of 1.13.0's context-cost work. 1.11.0's thesis was "prose cannot bind an executor, so move the mechanics into code"; that covered the writes. But `/teach` still asked the executor to *re-derive state predicates* from prose — is this a first exposure? a re-teach? did this write cross Bloom 3? — and the drift corpus showed the ~10% residue of those derivations accumulates. This release moves the mechanical branches into `bodhi-state` and phase-loads the rare sub-flows.

### Added — read-side branch detection in code
- **`bodhi-state session-brief --concept N`** — settles `/teach`'s opening branches deterministically: `firstExposure`/`pretestApplies` (bloomLevel 0 AND no non-deferred history; deferrals are scheduling, not exposure evidence), `isReteach` (real history AND Box 1 or latest-incorrect), plus box/bloom/Feynman/`daysSinceLastReview`/`dueForReview` for depth calibration. `/teach` Phase 1 runs it once; Phase 2 opens per the brief instead of per the executor's reading of the tracking files.
- **`record-review` output now reports `crossedBloom3`** — true exactly when this write moved `bloomLevel` from <3 to ≥3. `/teach`'s bump-profile duty drops its "if unsure, scan progress.md" residue and keys off the flag.
- **`bodhi-state snapshot`** — the whole `/progress` number surface in one read-only call: position + Bloom maps, session cadence (streak, sessions in last 7/30 days, days since last session), due lists + box distribution + 3-tier retention rollup, per-module mastery + `blockedOnFeynman`, confidence calibration. `/progress quick` is now one script call and zero tracking-file reads; the dashboard is one call plus the live `progress.md`. Context cost stays O(1) in session count.
- 20 new deterministic tests (164 total).

### Changed — progressive disclosure inside /teach
- The understanding-only session (explain-back loop, grading ladder, recording duties, time-pressed variant) moved to `skills/teach/references/understanding-only.md`, loaded only when that branch fires. SKILL.md keeps a pointer. The duplicated recording steps (Phase 2 understanding-only vs Phase 5) now exist once.
- `/housekeep` no longer names the `state-migration` KB in its header — the Phase 1/Phase 5 conditional loads were already the real contract (the audit's long-standing demotion candidate).

### Lint
- `/teach` must invoke `session-brief` and point at `references/understanding-only.md`; `/progress` must invoke `snapshot` (new rule 52).
- The `--project`-on-every-invocation check now covers `skills/*/references/*.md`.

### Evals — the drift detector fired (first Fable 5 sweep)
The pre-tag sweep was the first run since the maintainer's default model changed to Fable 5 — and the grading scenarios did exactly what 1.12.0 built them for. 7/10 first-pass (all four executor-discipline, both transcript-fidelity including the session-brief-driven pretest flow, and `grade-genuine`); the three failures were all grading scenarios, and a control run against untouched v1.12.2 failed a *different* subset the same way — model drift, not a 1.13/1.14 regression. Two failure modes, three fixes, none in skill prose:

- **Stop-and-wait**: the model ends its turn at a natural dialogue boundary awaiting the learner's live reply — correct interactive behavior, fatal in a one-shot headless run. And when the harness asserted "this is a headless eval" inside the *user prompt*, the model treated it as possible prompt injection and cross-examined it against fixture state — also correctly: user prompts are not where a harness gets to assert what is real. Fixes: (1) the simulation contract moved to the system prompt via `--append-system-prompt` (`SYS_HARNESS`), where the harness genuinely speaks; (2) a **learner-departure nudge** — if a grading scenario ends with no review recorded, the harness sends one `--continue` turn supplying the session-end signal a real learner would supply by leaving. The nudge is double-gated: grading scenarios only (it could mask the forgetting the executor-discipline scenarios exist to catch), and only on the "no review recorded" failure (a grade that landed out of band fails outright — a nudge there would hand the model a second bite at grading).
- **Apply-rung under-crediting**: one run graded a learner with correct `CREATE INDEX` usage but zero trade-off knowledge at tested-bloom 2. The `feynman-technique` KB ladder now states explicitly: demonstrated application inside the explanation places the answer on the apply rung (3-4); grading it 0-2 ignores what the learner visibly did. Same spec-defect class as 1.12.2's grading fix, opposite direction.

## [1.13.0] - 2026-07-02

The context-cost release. Every skill fire was paying a ~39 KB floor — `teaching-personality` (7.4 KB) plus the full `state-schema` KB (23.9 KB) — even though, since the 1.11.0 deterministic state layer, no routine session ever touches field shapes: `bodhi-state` owns the writes. This release splits the operational surface from the reference so routine fires stop paying for shapes they cannot legally hand-edit anyway.

### Changed — the state-ops / state-schema split
- **New `state-ops` KB** (11.9 KB): project discovery, the `bodhi-state` write path and full subcommand table, the `sessionHistory` type vocabulary, gate verdicts, the mastery formula, markdown-surface rules. This is what every skill now references.
- **`state-schema` KB slimmed to the field-level reference** (23.9 KB → 15.3 KB): file shapes, field semantics, the Fallback discipline, project completion. Loaded ONLY by the manual carve-outs (`/learn` scaffolding, `/evaluate` profile writes, `/assess`/`/mentor` field updates, `/housekeep`) and the script-unavailable fallback. An executor that cannot see field shapes cannot hand-edit them — the split is a discipline mechanism, not just a diet.
- All 18 skills, the `learning-project` rule, and the chain-skip guards now reference `state-ops` for routine operations; fallback paragraphs still deliberately load `state-schema`. Per the regenerated `dev/context-audit.txt`: the cold-fire floor drops from ~39 KB of KBs + skill to ~18 KB + skill (`/resources` 23.2 KB total, was ~44 KB); `/teach` cold-fires at 36.6 KB (was ~50 KB).
- **`teaching-personality` trimmed ~15%** (7.4 KB → 6.3 KB): the Four Roots and Core Teaching Principles compressed to their operative content; all tables (language rules, emotions, streaks, empty states, feedback ladder) kept verbatim.

### Changed — surface pruning
- **`read-defaults` demoted from `knowledge/` to `dev/read-defaults.md`.** Its own text said skills never load it at runtime; it is audit/lint contract documentation and now lives with the tooling that enforces it (dev/ is inert at install). KB count stays at 20 with `state-ops` taking its slot.
- **`blogpost.md` moved to `dev/`** — repo root is the storefront.
- **Feature freeze declared in CLAUDE.md**: no new skills, KBs, taxonomies, session types, or schema fields unless a second real user asks or the maintainer hits the gap in a real learning session. Bug fixes and context-cost reductions exempt.

### Fixed
- **README version badge drift** (said 1.11.1 since two release lines ago) — and the version-sync lint now covers the badge, so it cannot drift silently again.
- README "The Philosophy" section removed (verbatim duplicate of the TL;DR purpose block).

### Lint
- Rule 4 now accepts `state-ops` for routine files and additionally requires `state-schema` in the five manual-carve-out skills.
- New rule 51 pins the operational surface: `state-ops` must carry the subcommand table, gate, mastery formula, and full session-type vocabulary; `state-schema` must not re-grow the subcommand table (one home per fact).
- Session-type vocabulary pin now points at `state-ops`; the broken-predicate scan (rule 40) covers `state-ops` too.

## [1.12.2] - 2026-07-02

The first full grading-eval sweep (10 scenarios) caught one real spec defect and one eval-script defect — both fixed the same day. 8/10 passed on the first run, including all four executor-discipline scenarios and three of four grading scenarios.

### Fixed — the spec defect (`grade-apply-band` failure)
- `/teach`'s understanding-only recording rule ("strong final explanation = correct; **gaps remained = incorrect**") contradicted its own quality ladder ("can apply it in code = tested-bloom 3-4") — and the executor resolved the ambiguity harshly, grading a learner with clean apply-level mechanics but no trade-off knowledge as `incorrect`, demoting their box as if they had *forgotten* what they visibly knew. The grading ladder is now canonical in the `feynman-technique` KB (*Grading the Explain-Back*): a clean explanation at ANY rung = `correct` at that rung's `--tested-bloom`; missing depth caps the level, it is not a failed retrieval; `incorrect` is reserved for demonstrated failure (misconception surviving refinement, mechanical paraphrase, no coherent rung). Same failure class as 1.11.1's "struggled-but-got-there = correct" — box demotion must mean demonstrated forgetting.
- `/teach` now cites the KB ladder instead of restating it inline (also recovers skill byte budget).

### Fixed — the eval defect (`teach-hint-discipline` failure)
- The scenario's transcript assertions passed — the model refused the demanded solution, decomposed, and re-taught, exactly per protocol — but the script left the learner's post-re-teach behavior unspecified ("continue as the skill specifies"), so the model simulated the learner legitimately solving the exercise after the re-teach and recorded an *earned* `correct` (struggled-but-got-there). The assertion had assumed a learner the script never pinned. The learner is now scripted to stay stuck through the re-teach and stop, making "no unearned correct" assertable. Filed under the harness README's own warning: read the transcript before judging.

## [1.12.1] - 2026-07-02

The wild-data release. Running the new 1.11.3 analytics against four real learning projects surfaced a drift corpus the fixtures never modeled: pre-1.11.0 executors had invented a parallel `state.json` schema (session bookkeeping nested under `session`/`sessions` dicts, `lastActivity`/`previousModule` as dicts, plural `*BloomLevels`, duplicate `sessionDates`) and invented vocabulary (`result: "skipped"` in `reviewHistory`, a free-form `sessionHistory` type) — and `verify` waved all of it through. Every pattern was reproduced as a deterministic fixture FIRST (per the authoring contract), then fixed in code.

### Added
- **`bodhi-state defer`** — the missing operation the wild data revealed: a due concept the session never reached. Rolls `nextReview` forward (default 1 day) and appends a `{deferred: true, days}` history entry with NO result — deferral is scheduling, never an outcome. `/quiz` Phase 3 now directs unreached due concepts here instead of leaving executors to improvise (the pre-1.12.1 improvisation was hand-writing `result: "skipped"` and hand-rolling the date — exactly the bug class). `retention` reports `deferralsExcluded` and never counts deferrals as retrieval evidence.
- **`bodhi-state normalize`** — one-shot, idempotent repair for the drift corpus: lifts nested session bookkeeping to top level, dedupes/sorts `sessionDates`, stringifies dict `lastActivity`/`previousModule` (originals preserved under `lastActivityLegacy`/`previousModuleLegacy` — learner data is sacred), renames plural bloom maps to singular, converts invented `reviewHistory` results to canonical deferrals (note preserved), rewrites non-canonical `sessionHistory` types to `other` + `subtype` (lossless — the invented type becomes the subtype). Backs up both files to `.bodhi/.pre-normalize-backup/` before writing; never overwrites an existing backup.
- **`verify` hardening** — now errors on: nested session bookkeeping, non-string `lastActivity`/`previousModule`/`currentModule`, non-canonical `reviewHistory` results, and deferral entries that carry a result; warns on plural bloom maps and duplicate `sessionDates`. Every message names `normalize` as the repair — the Stop hook blocks once and tells you the one command to run.
- 26 new deterministic tests (143 total), including the full drifted-state fixture modeled on the real files.

### Notes
- The drift checks mean projects with pre-1.11.0 hand-edited state will fail `verify` (and trip the Stop hook once) after upgrading — intentionally. `bodhi-state normalize` is the one-command repair, and the hook's message says so.

## [1.12.0] - 2026-07-02

The judgment release. 1.11.0's thesis was "prose cannot bind an executor, so move the mechanics into code." Its completion: **unmeasured judgment cannot anchor a mastery claim, so measure the judgment.** The deterministic state layer made the Leitner math exact, but the inputs to that math — `--result correct|partial`, `--tested-bloom N`, "met the Feynman bar" — were LLM judgments with no evidence about their noise. Deterministic math over unmeasured classifications is false precision. This release measures the classifier.

### Added — grading-calibration evals (`dev/eval/run-llm-evals.sh grading`)
Four scenarios script a learner answer of *controlled quality* through a real headless `/teach` session and assert the grade lands in the honest band on disk:
- **`grade-jargon`** — a fluent, verbatim textbook recitation (repeated word-for-word under every probe) must NOT be graded `correct` and must NOT pass the Feynman gate. Targets the fluency-without-understanding signal — the single likeliest place an LLM grader is generous.
- **`grade-genuine`** — a clean own-words explanation covering mechanics, range-scan behavior, write costs, and when NOT to index must earn `correct`, tested-bloom in the **4-5 band**, `set-feynman`, and the box promotion. Over-harsh grading punishes real understanding; this scenario guards the other direction.
- **`grade-apply-band`** — correct mechanics and usage but an explicit "I do not know the trade-offs" must land tested-bloom **3-4**: 5-6 is grade inflation, 0-2 ignores demonstrated application. Bands, not exact values — grading is legitimately a judgment.
- **`grade-misconception`** — a confident, own-words explanation carrying a misconception that survives every correction attempt ("indexes speed up writes; index everything") must not pass. Confidence is not understanding.

These double as the **model-drift detector**: the mastery formula is exactly as trustworthy as these gradings, and a model change can shift them under identical prompts with nothing else noticing. Rerun `grading` on every model change, not only before tags.

### Added — transcript-fidelity evals (`dev/eval/run-llm-evals.sh fidelity`)
Protocol gates with no file trace, asserted with wording-tolerant regexes over the full assistant transcript (the runner captures `--output-format stream-json` for these — plain `claude -p` prints only the final message):
- **`teach-pretest`** — first-exposure `/teach` must open with the ungraded guess-first question in the first half of the session, and must not record it into `reviewHistory` (pretesting is priming, never assessment).
- **`teach-hint-discipline`** — a learner who exhausts 3 hints and demands the complete solution must get a re-teach, never Hint 4 or the answer — and no unearned `correct` may land in the tracking files (checked on disk, not just in prose).

Documented as drift *detectors*, not proofs: they match phrase families; a red means "read the transcript before judging," and the harness README says to run twice before treating a failure as real.

### Changed
- `assert_scenario.py` grows the two assertion classes plus shared helpers (`concept`, `todays_entries`, `assistant_text`); every new assertion was validated offline in both directions (passes on honest state, fails on dishonest state) before any live run.
- `run_scenario` gains a transcript mode; scenario groups (`grading`, `fidelity`) are addressable from the CLI.
- README Reliability Architecture reframed as the three-layer harness.

### Why this exists
The eval harness could prove a skill *performed the writes it described*; nothing measured whether the judgments inside those writes were honest. A tutor whose core loop is "LLM grades human" needs a grading conformance suite the way a compiler needs a test suite — most of all because the model underneath changes on someone else's schedule.

## [1.11.3] - 2026-07-02

The outcome-data release. `reviewHistory` has been a longitudinal retention dataset all along — every due-review outcome is a natural experiment on whether the Leitner intervals are calibrated. This release makes that data readable, and makes contributing it a one-command act.

### Added
- **`bodhi-state retention`** — retention-at-review analysis: %-correct grouped by *actual* spacing gap (same-day / 1d / 2-3d / 4-7d / 8-14d / 15-30d / 31d+) and by box-at-review-time. Relearning retries are excluded (same-session reps are not spacing evidence); a concept's first-review gap runs from its `introduced` date. The Leitner literature targets roughly 80-90% success at review time — persistently above suggests the intervals are too conservative, persistently below too aggressive. This is the empirical check the intervals have never had.
- **`reviewHistory[].boxBefore`** (state-schema KB first, per the authoring contract): `record-review` now stamps each entry with the box the concept was answered *from* — the box whose interval scheduled the review — making by-box retention exact for all future data. Older entries lack it; `retention` reports the legacy count honestly instead of guessing.
- **`bodhi-state export-anonymized`** — a shareable stats block: box/Bloom distributions, mastery and Feynman counts, session-type counts, the full retention summary, and calibration rates with the per-concept event lists stripped. **No concept names, no questions, no notes, no free text** — the test suite asserts this on a fixture salted with private strings.
- **"Share your learning data" issue template** (`.github/ISSUE_TEMPLATE/learning-data-report.md`): run one command, paste the JSON. The README honesty note now points at it — the lowest-friction path from N=1 to real outcome data.
- 12 new deterministic tests (117 total): boxBefore stamping (including on retries), gap bucketing, retry exclusion, legacy-entry accounting, and the export's no-private-strings guarantee.

### Changed
- `calibration` internals refactored into a shared summary helper (identical output) so the export reuses it.

## [1.11.2] - 2026-07-02

### Fixed — mastery-streak semantics
- **A `partial` retrieval now resets `consecutiveCorrectAtL4Plus`.** The mastery criterion reads "3 *consecutive correct* at L4+", but the counter previously ignored partials — correct → partial → correct → correct counted as 3 consecutive, so mastery could be declared across a demonstrated wobble. The box hold is unchanged (partial is still not a Leitner demotion); only the streak breaks. A correct at a lower tested level still leaves the counter untouched, and `--retry` reps still never touch it. Order per the authoring contract: `state-schema` KB rule first, failing test (`t_partial_breaks_streak`, reproducing the exact bug), then the one-line `apply_review` change. GUIDE and `spaced-repetition` KB partial-rule wording aligned.

### Changed — epistemic honesty pass on the science
- **Evidence tiers on every pedagogy KB.** Each of the 15 methodology KBs now opens with a one-line evidence tier: *bedrock* (spaced repetition, desirable difficulties, cognitive load), *strong* (metacognition), *strong-theoretical / strong-qualitative / strong-mechanism* (ZPD, scientific debugging, Feynman), *organizing framework / practitioner framework / derived* (Bloom's, mentoring, assessment-framework), *moderate* (pair programming), *qualified* (constructivism — guided over pure discovery, per Kirschner, Sweller & Clark 2006), *emerging* (ai-learning-safeguards), and *contested* with explicit caveats (growth mindset — Sisk et al. 2018; deliberate practice — Macnamara et al. 2014). README Science section gains an "Evidence tiers" paragraph with the Dunlosky et al. (2013) umbrella citation. Rationale: the project's differentiator is the honesty note — fencing the weak claims is what lets a reader trust the strong ones.
- **Ebbinghaus percentages removed.** The `spaced-repetition` KB's forgetting-curve section stated the widely-misquoted pop percentages (42% at 20 minutes, etc.) as fact; replaced with the qualitative claim (steep early decay, recall flattens the curve) — false precision in the KB that anchors the scheduling system was exactly what this project polices elsewhere.

## [1.11.1] - 2026-06-10

The audit release. A four-dimension adversarial audit (pedagogy fidelity, learner journeys, cross-artifact consistency, failure modes) ran against 1.11.0; every high-severity finding was hand-verified against source before fixing. The theme: state-integrity seams where the new 1.11.0 mechanics met older flows.

### Fixed — spaced-repetition state integrity
- **Successive-relearning retries no longer undo the demotion.** `record-review --retry` records the relearning rep as history evidence WITHOUT box/counter/bloom movement; `/quiz` uses it for the relearning loop. Previously a correct retry promoted the just-demoted concept and silently cancelled tomorrow's review — the exact opposite of Rawson & Dunlosky's design.
- **`/reflect` same-day guard.** Concepts already reviewed today (by `/quiz`/`/teach`/`/practice`) get no second review from reflection — one day of evidence, one box movement. Previously a chained day double-promoted boxes, and reflect's "hold" mapped to `partial`, clobbering a just-earned 7/14-day interval back to tomorrow.
- **Confidence ratings no longer gate promotion in `/reflect`.** The retrieval outcome decides the box; the rating is pure calibration signal. The old confidence-≥8 gate punished exactly the underconfidence pattern the metacognition KB says to name and support (and which `/quiz` already handled correctly).
- **`cumulativeStats.totalSessions` actually counts.** `touch-state` bumps the cross-project counter itself on the first touch of a new day. Previously only `/reflect` bumped it, gated on its own `touch-state` reporting a new session — which `/teach`'s earlier call had already consumed, so the lifetime counter sat near zero forever.
- **Stale-reconfirm misses at the prerequisite gate are recorded** (`incorrect`, Bloom 3) instead of silently dropped — demonstrated forgetting belongs in the schedule.

### Fixed — script robustness (all live-repro'd by the audit, all now unit-tested)
- **Concurrency:** unique temp filenames + per-project `flock` spanning the read-mutate-write run. Two terminals on one project previously produced both tracebacks and silently lost reviews.
- **`record-session --data` can no longer smuggle `type`/`subtype`/`date`** past the vocabulary enforcement (a smuggled type then tripped the Stop hook on the script's own write).
- **Re-migration verifies against this run's input snapshot**, not a stale on-disk backup — the old comparison produced a false mismatch whose error message advised a data-destroying restore.
- **Corrupt/mistyped tracking files die cleanly** ("not valid JSON — run verify") instead of raw tracebacks; `gate-check` declines on an empty `currentModule` instead of gating a nonsense module.
- **Unparseable `nextReview` dates are surfaced** by `due` (`unparseableDates`) and flagged as errors by `verify` — previously a schedule-broken concept silently left review rotation forever. `verify` also now warns on a missing `spaced-review.json` and errors on case-insensitive duplicate concept names.
- **Comma-containing concept names** demotable via repeatable `forget --concept`; `reviewHistory` capped at 100 entries per concept (older roll into `reviewHistoryArchived`); `due --limit` caps context spill at scale; every skill snippet now carries `--project` (previously ~14 inline one-liners errored when cwd ≠ project).
- **Stop hook fail-open hardened at the interpreter layer**: `command -v python3 || exit 0` in hooks.json, so Windows-without-python3 gets silence, not a blocking hook error. README documents the Windows story (WSL or a `python3` alias).

### Fixed — pedagogy fidelity
- **Pretest gated on first exposure** — on re-teaches it was both false to the learner ("you have not seen this yet") and outside the pretesting research; re-teaches now open with a graded retrieval instead.
- **`/continue` delegates due-concept review to `/quiz --invoked-from=continue`** — the inline review was a second-class copy with no confidence tags, no relearning loop, no session entry. Chained `/teach`/`/practice` invocations now pass the resolved topic (and Box-1 target) their callees expect; the long-absence branch records `diagnostic-after-gap` (previously a canonical type with zero writers).
- **`/learn` Day 1 fixed four ways:** writes `~/.bodhikit/config.json` when the chosen root is off the default search paths (previously Day 2 dead-ended with "No active learning projects"); never re-asks the project root when one exists (previously forked the profile); seeds `spaced-review.json` from the assessment (assessed knowledge enters the Leitner system on Day 1 — "the first review is the most critical"); the first exercise follows the cognitive-load fade instead of the forbidden TODO-starter shape (also fixed in the `assessment-framework` KB template). Closing now names `/bodhikit:continue` — the one onboarding handoff that keeps a new learner on the path.
- **Project completion has a canonical criterion** (state-schema KB): all modules finished or explicitly skipped AND the learner confirms — `/evaluate` asks, never infers. The entire endgame (capstone, mentor offer, `/teach-back` eligibility) previously rested on executor improvisation.
- **`/evaluate` predictions moved before the fresh assessment** (Koriat ordering) — predicting "biggest gap" right after feeling yourself struggle on 15 assessment questions measures the last 20 minutes, not your self-model.
- **Quiz-only learners see why mastery is pinned:** `mastery` reports `blockedOnFeynman`, and `/progress` renders "N concepts meet every criterion except the explain-back — one `/teach` (understanding-only) completes each."
- **The understanding-only path carries full bookkeeping** (concept-learned bump, targeted-reteach entry) and gains a time-pressed variant; `/pair` records struggled concepts (`partial`), not just wins; `/debug-together` and `/teach-back` sessions become visible (`touch-state` + session entries); the orphaned `ai-learning-safeguards` KB is wired into the hint flows with a dependency-pattern watch; quiz questions pitch at each concept's recorded Bloom level.

### Added — guardrails
- `dev/eval` grows a fourth LLM scenario (`reflect` — asserts the same-day guard, no-confidence-gate, interval preservation, and single profile bump against a live model) and 32 new deterministic tests (93 total). `dev/check.sh` rule 50 pins the new contracts (`--retry` usage, same-day guard, completion criterion, first-exposure pretest, `--project` on every snippet, safeguards KB non-orphaned); rule 2 now covers agents; rule 45 pins the full session-type vocabulary.
- GUIDE sync pass: every stale "auto-invoked" claim corrected to the 1.10.2 offer contract, skill count fixed, mastery formula completed, `/review` and `/reflect` cards aligned with actual behavior.

## [1.11.0] - 2026-06-10

The structural release. The 1.10.x dogfood arc established that the recurring failure class — specs read descriptively instead of imperatively, fields silently dropped, vocabulary invented — could not be closed with more prose. 1.11.0 closes it with architecture, then spends the freed budget on pedagogy.

### Added — deterministic state layer
- **`scripts/bodhi-state`** (Python 3, stdlib-only): every tracking-JSON mutation now runs in code. Subcommands: `add-concept`, `record-review` (Leitner box math, bloomLevel ratchet, `consecutiveCorrectAtL4Plus` rules, confidence tags), `set-feynman`, `record-session` (canonical type vocabulary enforced — invalid types are rejected, `other` requires `subtype`), `record-assessment`, `forget`, `touch-state` (streak/session bookkeeping that never double-counts a day), `bump-profile`, `due`, `mastery` (canonical formula + legacy `—` display rule + 3-tier retention rollup), `calibration`, `gate-check` (full prerequisite-gate verdict), `migrate-spaced-review` (backup → in-place transform preserving non-canonical fields → field-loss verification → marker), `verify`. Unknown learner fields preserved in code; writes are atomic (temp + rename).
- **Stop hook** (`hooks/hooks.json` + `scripts/bodhi-stop-hook.py`): verifies tracking-file schemas for recently-touched projects before a session stops; blocks once with a repair instruction on structural breakage. Fail-open, `stop_hook_active`-guarded, bounded walk.
- **Two-layer test harness** (`dev/eval/`): 61 deterministic tests for the script (run by `dev/check.sh` on every change) + headless LLM evals (`run-llm-evals.sh`: migrate / forget / quiz scenarios against a realistic v2 fixture with non-canonical learner annotations, asserting on resulting file state). The automated successor to the 1.10.7–1.10.13 manual dogfood passes.

### Changed — skills rewired to the script
- All eight v3 writers (`/quiz`, `/teach`, `/explain` — since merged into `/teach`, `/practice`, `/forget`, `/reflect`, `/pair`, `/evaluate`) plus `/continue`, `/progress`, `/assess`, `/plan`, `/debug-together`, `/teach-back` now route JSON writes through `bodhi-state`. The CHECKPOINT-before/after-writes prose discipline (1.10.12), the `/housekeep` STOP banner + decision matrix + defensive self-check (1.10.11), and the per-skill imperative-write step lists are **retired** — the failure mode they defended against is now structurally impossible, and `dev/check.sh` fails any skill that reintroduces the prose or hand-appends `sessionHistory`.
- **`/housekeep migrate` 5f-bis** is one idempotent script call run unconditionally per project (the single-marker short-circuit class is dead by construction). The 1.7.0 step bodies (5a–5f) moved into the `state-migration` KB — default-mode rotation runs no longer pay for migration-only prose. `/housekeep` shrinks 23.3 KB → 14.7 KB.

### Changed — context diet
- **`state-schema` KB split**: lifecycle content (rotation protocol, summary collapse, retirement) moved to the new `state-lifecycle` KB, loaded by `/housekeep` only. `state-schema` (loaded by nearly everything) shrinks 521 → ~355 lines while gaining the write-path table and gate documentation.
- **`dev/check.sh` rule 49**: hard 18 KB size budget per SKILL.md — ratchet down, never up.

### Added — pedagogy
- **Prerequisite-gate recency rule.** `bloomLevel` is a ratchet (nothing ever lowers it — `/forget` demotes the box, not the classification), so Bloom ≥ 3 alone is stale evidence. The gate's happy path now requires current evidence (`box >= 3` OR reviewed within 30 days); otherwise the verdict is `stale-reconfirm` and `/teach` asks one quick reconfirm question instead of waving the concept through.
- **Per-item confidence calibration** (Koriat 1997, new `metacognition` KB section): `/quiz` collects a sure/mostly/guessing tag with every answer BEFORE the reveal; tags land in `reviewHistory[].confidence`; `bodhi-state calibration` aggregates over/underconfidence; `/progress` gains a Calibration section; `/reflect` maps its 1-10 ratings onto the same tags.
- **Pretesting** (Kornell, Hays & Bjork 2009, new `desirable-difficulties` KB section): `/teach` Phase 2 opens with one ungraded guess-first question before the I-Do explanation, and the explanation resolves it.
- **Cognitive Load Theory KB** (Sweller — worked-example effect, faded scaffolding, expertise reversal): the Bloom 1-2 scaffolding tier in `/teach` and `/practice` becomes a worked-example → completion-problem → full-problem fade instead of TODO-starter files; Bloom 3+ gets no worked examples (expertise reversal).
- **Successive relearning** (Rawson & Dunlosky 2011, new `spaced-repetition` KB section): `/quiz` re-asks missed concepts (reframed) at the end of the session until one successful retrieval, capped at 2 retries; the demotion stands.
- **Bloom probes**: each `/quiz` includes one question pitched one level above a strong concept's recorded level, giving classifications a channel to rise outside `/teach`.
- **Canonical `partial` rule** in the `spaced-repetition` KB: box held, re-test tomorrow (formalizing what `/reflect` already practiced).

### Removed — two skills merged, zero capability lost (20 → 18)
- **`/explain` merged into `/teach`.** `/teach` already ran explain → explain-back → analogy escalation → Feynman gate; `/explain` was that flow without the exercise. `/teach` Phase 2 now has an explicit **understanding-only path**: when the learner just wants to understand ("explain X", declines the exercise offer), it runs the full Feynman depth — uninterrupted explain-back, gap analysis with the three fluency-without-understanding signals, per-gap refinement, final full explanation — records via `record-review` with the quality ladder (+ the Feynman gate), and stops without guilt-tripping toward the exercise.
- **`/status` merged into `/progress` as modes.** `/progress quick` is the flourish-free 3-line check-in (2 file reads, chained by `/continue` as `/progress quick --invoked-from=continue`); `/progress all` is the one-line-per-project table with staleness + health flags (v1 fields, unparseable JSON, missing files, legacy layout); no argument stays the full dashboard. One dashboard skill with three depths replaces two overlapping entry points.
- Lint updated in lockstep: chainable set, `/continue` chain check, v1-boundary exemptions (now `/housekeep` + `/progress`), and writer lists all reflect the new topology; the README count check enforces 18.

### Changed — docs and framing
- README/manifests reframed from "research-backed" to **"research-informed"**, with an explicit honesty note: the design follows the literature; outcome validation is ongoing. New "Reliability Architecture" README section; Science section gains Sweller, Kornell/Hays/Bjork, Rawson & Dunlosky, and Koriat citations. Counts: 18 skills, 4 agents, 20 KBs.
- `docs/example-project` migrated to spaced-review v3 (via the script itself) and now pinned by lint: `bodhi-state verify` must pass on it.

### First catch (before this release even shipped)
The eval harness's very first run failed — and the failure was the thesis in miniature. The headless executor could not locate `bodhi-state` (bare name, not on PATH), silently degraded to the manual fallback, and the fallback under-delivered while *claiming success in prose*: box demoted, but no v3 fields filled, version left at 2, and (first run) no `learner-forget` session entry despite the closing message saying one was written. Fixes, all caught pre-tag by file-state assertions: every skill snippet now carries the full `"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state"` path (the command itself is the resolution — unskippable), the harness exports `CLAUDE_PLUGIN_ROOT` for `--plugin-dir` runs, and the `state-schema` KB fallback rule now requires v3 read-tolerance and both lookup paths to fail before hand-editing is permitted. All three scenarios pass against a live model.

### Why this exists
Each 1.10.x fix was a correct patch to an instance of the same disease: prose cannot bind an executor. 1.10.12's own CHANGELOG named the problem structural; this release gives it the structural answer. Moving the writes into code simultaneously (a) deletes the bug class, (b) deletes the defensive prose that was crowding out teaching content, (c) makes the contracts testable for free, and (d) creates the portable core (script + fixtures + evals) that any future runtime can reuse. The pedagogy additions are the dividend: pretesting, faded worked examples, confidence calibration, and successive relearning are among the most-replicated effects in the learning literature, and they fit in the budget the deleted prose freed up.

## [1.10.13] - 2026-06-09

### Added
- **Canonical `sessionHistory[].type` vocabulary** documented in the `state-schema` KB. The pre-1.10.13 schema declared only `spaced-review` as an example, but live data in the wild carried at least four other types (`quiz`, `targeted-reteach`, `diagnostic-after-gap`, `learner-forget`) that skill executors invented without spec guidance. The 1.10.13 fix enumerates the full vocabulary as canonical:

  | `type` | Written by | Meaning |
  |---|---|---|
  | `spaced-review` | `/quiz`, `/reflect` (spaced-review batch) | Routine spaced-review session covering due concepts |
  | `quiz` | `/quiz` (explicit-topic invocation) | Quiz on a specific topic, not by schedule |
  | `targeted-reteach` | `/teach` (re-entering a demoted concept) | Focused re-teach after demotion or precision-gap surfacing |
  | `diagnostic-after-gap` | `/learn` Phase 1.5, `/assess`, `/continue` (after absence) | Diagnostic after meaningful gap |
  | `learner-forget` | `/forget` | Learner-initiated demotion |
  | `pair` | `/pair` Session End | Pair session touching tracked concepts |
  | `practice` | `/practice` | Exercise session that introduced or reviewed concepts |
  | `evaluate` | `/evaluate` | Comprehensive evaluation snapshot |
  | `other` | any skill (escape hatch) | Genuinely novel; **MUST pair with a `subtype` field**; update this table if recurring |

  Skills MUST use one of the canonical types OR `"other"` with a `subtype`. Inventing a new top-level type without updating the KB first is a contract violation — the same discipline that applies to top-level file shapes now applies to `sessionHistory[].type`.

- **`/quiz` Phase 3 step 6** explicitly directs writing a `sessionHistory[]` entry, picking `spaced-review` vs `quiz` based on invocation context (due-concepts vs explicit-topic). Optional fields listed: `boxChanges`, `precisionGapMovement`, `habitObservations`, `calibrationNote`, `notes`.
- **`/forget` Phase 3 step 1** explicitly directs writing a `sessionHistory[]` entry with `type: "learner-forget"`, including `conceptsDemoted`, `boxChanges`, and optional `notes` describing why the learner chose to demote.
- **`dev/check.sh` rule 44** enforces that any skill writing to `sessionHistory[]` cites the canonical type vocabulary. Narrow check — looks for "append/write sessionHistory" verbs near a sessionHistory mention, not bare reads (so `/evaluate`'s read-only mention does not trigger).

### Why this exists
The 1.10.12 dogfood caught two live skills (`/quiz` and `/forget`) writing useful, well-formed sessionHistory entries with novel types. The data was fine — `learner-forget` is a perfectly reasonable classification — but the executor was inventing the contract on the fly, with no schema constraint guiding what types are valid. The 1.10.12 imperative-write fix made writes happen; 1.10.13 makes them happen *within a declared vocabulary*. Without this, two different executors could write the same situation under different type strings (`learner-forget` vs `forget` vs `manual-demote`), and downstream readers (`/evaluate`, `/progress`) would either crash on the inconsistency or silently miss entries.

The `other` escape hatch is deliberate. The vocabulary table is meant to grow when real usage justifies it (add the row, ship the update), but the moment-to-moment escape hatch exists for executors that genuinely encounter a novel case mid-skill. The required `subtype` field for `other` entries surfaces the novelty so a future audit can see what types should be promoted to canonical.

The `/forget` spec violation I initially diagnosed (writing `bloomLevel: 3` against the preserve rule) was a misreading on my part — the value came from the prior `/quiz` write, and `/forget` correctly preserved it. The diff format that Write tools emit makes every line look "added" because the whole file is rewritten; that visual cue mislead me into thinking `/forget` was the source. The actual `/forget` behavior on the live disk state is correct.

## [1.10.12] - 2026-06-09

### Fixed
- **Imperative-write discipline applied across every v3 writer.** The 1.10.11 dogfood ran `/quiz` against `system-design` post-migration. The executor computed correct results — Bloom levels assessed, box transitions decided, demote logic applied honestly to "I forgot" answers — and rendered a beautiful results table with growing-well / needs-sunlight commentary. **Zero files were written.** Phase 3's "Update spaced-review.json" / "Update progress.md" / "Update state.json" instructions were read descriptively (compute the change, describe it) instead of imperatively (compute the change, perform the Write tool call). Same defect 1.7.1 fixed in `/housekeep migrate`; same defect 1.10.8 fixed in 5f-bis; surfacing again in `/quiz` proved the pattern is structural across the codebase.

  Fix: every skill that touches tracking state now has the imperative-write discipline applied to each file write — explicit Read → mutate-in-place → Write tool call → re-read verification, with **CHECKPOINT-before-writes** (name aloud the files about to be written, before any Write call) and **CHECKPOINT-after-writes** (name aloud verified writes, before any user-facing report). The user-facing report is now explicitly framed as *the receipt of the writes*, not a substitute for them.

  Skills updated: `/quiz` Phase 3, `/teach` Phase 5, `/explain` Update Tracking, `/practice` Phase 3 step 6, `/forget` Phase 3, `/reflect` Phase 4, `/pair` Session End, `/evaluate` Update Tracking. Every "update X" / "append to X" / "write X" instruction now reads as a Write tool call, not state description.

### Added
- **`dev/check.sh` rule 43** enforces the imperative-write CHECKPOINT discipline. Any of the eight state-writing skills missing CHECKPOINT-before-writes or CHECKPOINT-after-writes markers fails the lint. Prevents the descriptive-vs-imperative defect from creeping back into any of them.

### Why this exists
The dogfood loop's catch at 1.10.12 was the largest in the series. Prior passes caught skill-by-skill bugs (`/housekeep migrate` at 1.10.8, `/teach` Phase 1 gate at 1.10.10, `/quiz` Phase 3 at 1.10.12). Each pattern was the same: spec correct, executor reading descriptively instead of imperatively. The cumulative evidence makes it a structural problem, not a per-skill bug — and the fix has to be structural too.

The pattern now codified across the eight v3 writers:
- **STOP banner or equivalent** at the top of the write section, naming the failure mode.
- **CHECKPOINT-before-writes** — executor names aloud the files about to be written, before the Write calls. This makes the writes a public commitment the executor cannot silently skip.
- **Imperative steps for each file**: Read → mutate in place (per the 1.10.9 in-place mutation discipline preserving non-canonical fields) → Write → re-read verify.
- **CHECKPOINT-after-writes** — executor names aloud the verified writes, before any user-facing report.
- **User-facing prose framed as receipt**, not substitute.

The lint rule 43 enforces the discipline at PR time. Future skill additions that touch state must adopt this pattern from the start; the lint catches missing checkpoints.

This is the deepest dogfood-driven fix yet. It does not catch a new spec bug — it catches the *structural* problem that produces spec bugs of this class across every skill that writes state. The case for "schema-touching changes get an end-to-end dogfood pass before tagging" is now complete: pure-read traces (passes 1-4) catch spec bugs; live execution (passes 5+) catches executor-discipline bugs that pure-read cannot see by design.

## [1.10.11] - 2026-06-09

### Fixed
- **`/housekeep migrate` Phase 5 prominence rewrite.** The first real execution run at 1.10.10 caught a spec-vs-executor problem: the spec was correct (per-target idempotency with `.migration-1.7.0.md` and `.migration-1.10.md` as separate markers), but the *executing model* skimmed past the per-target explanatory framing, latched onto the first concrete check (the 1.7.0 marker), and exited "nothing to do" against four projects that all needed the v2→v3 transform. The spec was unmissable to a careful reader; it was missable to an executor scanning for procedural steps. The rewrite makes the per-target check the *first concrete instruction* in Phase 5:
  - A **STOP banner** opens Phase 5 explicitly naming the pre-1.10.8 broken behavior and warning the executor against it ("If your instinct is to short-circuit on a single marker, that instinct is the bug").
  - A **decision matrix in tabular form** replaces the bulleted sub-list — tables are harder to skim past than bullets, and each of the four marker-state combinations has its own row with explicit "what to run" and "exit condition" columns.
  - A **CHECKPOINT** requires the executor to name aloud (in the response to the learner) which row each project lands in AND which steps it is about to run, BEFORE running any step. This is the load-bearing moment of the migration flow.

- **5f-bis defensive self-check (last line of defense).** Even if Phase 5's Pre-flight is short-circuited by a model that skimmed past the matrix, 5f-bis now opens with its own independent check: read `spaced-review.json` from disk right now; if the file is at v2 OR concepts are missing the new fields, run regardless of any upstream gating, marker state, or earlier "conclusions." Running 5f-bis on already-migrated data costs nothing (the idempotency check catches it); running it on un-migrated data is exactly what the learner asked for. The defensive check exists because the 1.10.10 dogfood run proved a determined model can talk itself past even a well-specified Pre-flight; the right response is a backstop that runs the work the learner came for.

### Added
- **`dev/check.sh` rules** (single severity err): Phase 5 must lead with the STOP banner AND the decision matrix; the CHECKPOINT marker requiring name-aloud reasoning must be present; 5f-bis must declare its defensive self-check.

### Why this exists
The dogfood pattern shifted at 1.10.11. The first four passes (1.10.7–1.10.10) caught spec bugs at increasing depth — pure-read traces revealed wrong boundary checks, broken architectural models, ambiguous wording, and single-signal logic in a multi-signal data world. Each fix tightened the spec. 1.10.11 caught a different category: the spec was correct but *non-binding* to an executor that defaulted to the simpler old behavior. This is the gap between *specifying* a process and *forcing* it.

The fix uses two complementary mechanisms. The prominence rewrite addresses the *first* failure mode: the executor reading the spec and following the wrong path through it. The defensive 5f-bis self-check addresses the *second* failure mode: the executor short-circuiting upstream gating entirely, by giving the actual work step its own non-bypassable preflight. Belt and suspenders.

Worth saving as a habit: any spec whose correct execution requires multiple sequential reasoning steps under a "decide first, then act" preamble has a built-in skimming risk. The mitigation is to make the decision visible (matrix instead of bullets), make the decision named (CHECKPOINT requiring spoken-aloud reasoning), and make the action step independently safe (defensive self-check at the actual work site). Future schema migrations should follow this pattern from the start.

## [1.10.10] - 2026-06-09

### Fixed
- **`/teach` Phase 1 prerequisite gate trigger model re-specified.** The 1.10.0 spec said the gate fires when "selecting a concept from a module *different* from the learner's current module." But `state.json.currentModule` is advanced by `/learn` Phase 4, `/continue` Phase 4, or the prior session's Phase 5 wrap-up BEFORE the first session on the new module runs — so a literal "different module" check fires too late (or never) on real flows. The corrected trigger is: scan `spaced-review.json.concepts[]` for any entry whose `module` field matches `state.json.currentModule`. If at least one matches, this is a continuation session — gate does NOT fire. If zero match, this is the first session on a new module — proceed to the prerequisite check. The gate also explicitly does not fire on first-ever-`/teach` (no prior module), `--invoked-from=` chained calls (caller's intent overrides), or explicit-topic `$ARGUMENTS` (learner's request overrides).

- **Prerequisite identification mechanism made explicit, with safe fallback.** The 1.10.0 spec referenced "prerequisite concepts named in the prior module's `plan/phase-{N}.md` success criteria" — but real plan files do not declare prerequisites structurally. The corrected spec defines two paths: (a) structured declaration via a `**Prerequisites for next module:**` line in each module section (now required by `/learn` Phase 3 and `/plan` Regenerate from 1.10.10 onward); (b) fallback when no structured declaration exists — treat all concepts in `spaced-review.json` whose `module` matches the prior module as prerequisites. The fallback is conservative (some may be irrelevant); the gate's prompt to the learner notes that the mapping was inferred and offers a "skip irrelevant" choice.

- **Strong v2 retention evidence fallthrough added.** The 1.10.0 gate keyed only off `bloomLevel`. Real data showed concepts with strong v2 retention signals (Box 3+, two consecutive correct recalls in `reviewHistory[]`) that would block module advancement just because no v3 writer had run a Level-3+ question on them yet — `bloomLevel` would be artificially low while box-and-history evidence pointed at Apply-level mastery. The corrected rule: when `1 <= bloomLevel < 3` AND `box >= 3` AND the last 2 `reviewHistory[]` entries both have `result: "correct"`, treat the concept as Apply-equivalent for *gate purposes only*. Do NOT mutate `bloomLevel` — the fallthrough is a gate-time read, not a state write. The v3 writers will catch up to the v2 evidence on their own schedule.

- **Gate is offer-shaped, not auto-blocking.** The 1.10.0 spec said "Do NOT advance" on a prerequisite gap. The corrected gate mirrors the 1.10.2 opt-in-offer discipline: surface the gap, name the trade-off, let the learner pick. Choices: revisit a specific prerequisite, carry on into the new module (recorded in `progress.md` as a conscious decision), skip an inferred-but-irrelevant prerequisite (per-session dismissal — no permanent reclassification), or end the session. Do not auto-override.

### Added
- **`/learn` Phase 3 and `/plan` Regenerate now require per-module `**Prerequisites for next module:**` lines** in `plan/phase-{N}.md` files from Module 2 onward. The line names the specific concepts from this module that the next module builds on — gives the `/teach` gate a structured declaration to consult instead of the broad fallback.
- **`dev/check.sh` rules**: rule 17 expanded with three sub-checks (corrected trigger model, strong-v2-evidence fallthrough, offer-shape rather than auto-block); rule 42 requires the per-module Prerequisites declaration in `/learn` and `/plan`.

### Why this exists
The fourth dogfood step (trace `/teach` Phase 1 gate against `system-design` after a hypothetical 5f-bis run) caught four real bugs in the gate's logic. The 1.10.7 *legacy fallthrough* fix was correct as far as it went, but it only addressed the freshly-migrated case — once a learner starts running v3 writers on the project, three more bugs surface in sequence:

- The gate may never fire at all (trigger condition mismatched the real session flow).
- The gate has no defined input source for prerequisites (forces the executing model to invent the list per invocation).
- The gate's single-signal `bloomLevel` check ignores the strongest retention evidence the system actually has (box + history).
- The gate hard-blocks when the rest of the plugin (per 1.10.2) is offer-shaped.

This is a deeper class of finding than 1.10.7/1.10.8/1.10.9 — those caught spec wording and architectural model bugs; this one caught a model-correctness issue. The 1.10.7 fix was a *boundary* correction; 1.10.10 is a *model* correction.

Pattern across the four dogfood passes:
- 1.10.7 — read one real file → caught a boundary check on a single field
- 1.10.8 — trace migration logic → caught an architectural model bug (single marker as universal idempotency)
- 1.10.9 — trace 5f-bis against real concept data → caught spec ambiguity that could silently drop data
- 1.10.10 — trace the gate that the migration enables → caught a single-signal model in a multi-signal data world

Each step exposed a deeper class than the prior. None visible without real `learn_with_bodhi/` data to trace against. The case for "schema-touching changes get a dogfood pass before tagging" is now overwhelming.

## [1.10.9] - 2026-06-09

### Fixed
- **5f-bis step 1 backup verification specifies parsed-JSON equality, not byte-for-byte.** The 1.10.8 spec said "matches the source" — ambiguous between a byte comparison and a parsed-JSON comparison. The Write tool routinely re-emits JSON with different whitespace or key ordering than the source; a byte comparison would false-fail on a healthy backup and abort the migration before any real work happened. The corrected check verifies key-for-key equality at the parsed-JSON level: same top-level keys, same `concepts[].length`, same field set on every concept entry (including non-canonical fields), same `sessionHistory[].length` with same field set on every entry. Whitespace and key-order differences are not failures.

- **5f-bis step 2 now declares in-place mutation discipline.** The original step 2 said "For each entry in `concepts[]`, add the three new fields if absent." Step 3 added "Preserve every other field verbatim." Both correct at the contract level, but an executing model could legitimately read these as "build the new JSON from the documented canonical fields plus the three new ones" — which would silently drop every non-canonical field. Real v2 `spaced-review.json` files in the wild carry non-canonical fields per concept (`precisionGap`, `lastResult` prose, `flaggedForFullReteach`) and per `sessionHistory[]` entry (`boxChanges`, `precisionGapMovement`, `habitObservations`, `partials`, `note`) — these are the learner's teaching history, sometimes hundreds of bytes of prose annotation each. The corrected step 2 makes the discipline explicit: read the parsed JSON, add the three keys to each concept, leave every other key untouched. Do not re-serialize from a schema template.

- **5f-bis step 5 verify checks first AND last concepts plus length equality.** The 1.10.0 spec said "sample a concept entry" — singular. If a JSON re-serialization bug dropped concepts 2 through 5 from a 6-concept array, the verify check would pass on the sampled-and-still-intact first concept. The corrected check requires sampling the first AND last concept, plus a middle one if length > 5, plus an explicit `concepts[].length` equality check against the source, plus a non-canonical-field spot-check on at least one concept that had non-canonical fields in the source.

### Added
- **`dev/check.sh` rules** enforcing the in-place mutation declaration AND the parsed-JSON equality specification in `/housekeep migrate`. Prevents both regressions.

### Why this exists
The third dogfood step (trace `/housekeep migrate` against `system-design`'s `.bodhi/`) caught seven spec gaps; two were MEDIUM severity (silent data loss risk and false-fail risk on the backup verify) and five were LOW (cosmetic / ambiguity). The two MEDIUMs land in 1.10.9; the LOWs are filed as known papercuts for a future cleanup pass.

The pattern continues: each dogfood step exposes a category of bug that schema and lint checks cannot. 1.10.7 caught a data-shape misread; 1.10.8 caught an architectural model bug (single marker as universal idempotency); 1.10.9 caught spec-wording ambiguity that an executing model could read into broken behavior. None were visible without real `learn_with_bodhi/` data to trace against. The case for "schema-touching changes get a dogfood pass before tagging" gets stronger with each iteration.

## [1.10.8] - 2026-06-09

### Fixed
- **`/housekeep migrate` per-target idempotency model.** The 1.7.0 spec used a single marker (`.bodhi/.migration-1.7.0.md`) as the idempotency check — Phase 5 step 1 exited cleanly whenever that marker existed. This was correct for 1.7.0 (only one migration target), but became a showstopper as soon as 1.10 added a second target: every learner already-migrated to 1.7.0 had `.migration-1.7.0.md` on disk, so running `/housekeep migrate` would short-circuit on step 1 and **never run the v2 → v3 spaced-review transform**. The whole 1.10.0 schema fix would have been unreachable via the documented path. **Caught by the second dogfood step** (tracing the migration logic against `rails-react-scaling/.bodhi/`, which has the 1.7.0 marker but no v3 data).

  The fix introduces a per-target marker model: each migration target gets its own marker (`.migration-1.7.0.md`, `.migration-1.10.md`); Phase 5 runs each target whose marker is missing; only when ALL target markers are present does migrate exit with "nothing to do." Already-1.7.0-migrated projects can now reach v3 by running `/housekeep migrate` — the 1.7.0 transforms are skipped (already on disk), 5f-bis fires, the new `.migration-1.10.md` marker is written.

- **5f-bis step 1 (backup) now uses imperative writes** matching the 1.7.1 pattern. The original instruction ("Back up the pre-v3 file to `.bodhi/.pre-1.10-backup/spaced-review.json`") was declarative and could be interpreted by an executing model as a state-description rather than an action — the same defect 1.7.1 fixed across steps 5a/5b/5c. The corrected step uses explicit `mkdir -p` + Read + Write + re-Read verification, with rollback if any check fails. The backup must be on disk before any in-place transformation begins.

- **5g precondition list extended.** The 1.7.0-target marker and 1.10-target marker now have separate precondition blocks. The 1.10 block verifies `.bodhi/.pre-1.10-backup/spaced-review.json` exists, parses as JSON, and carries `version: 2` — closing the loop on the imperative-write discipline above. Without this check, a silently-skipped backup write could not be caught at marker-write time.

- **5h report block scoped to which targets ran.** The original report template described 1.7.0-era files (`plan.md` split, `assessments` rotation) regardless of which targets actually ran. The corrected version prints a 1.7.0 block, a 1.10 block, or both — describing only the transforms that actually ran in this invocation.

### Added
- **New marker template `.migration-1.10.md`** documents what 5f-bis did per project: which target version, what fields were added, byte-size deltas, and where the backup lives.
- **`dev/check.sh` rule 41** enforces the per-target idempotency declaration in `/housekeep migrate` and the presence of the 1.10 marker reference. Prevents the single-marker model from creeping back.

### Why this exists
The second dogfood step (trace the migration logic without running it) caught four defects (D1–D4) in step 5f-bis and the surrounding flow. D3 was the showstopper: the single-marker idempotency model would have made the entire 1.10.0 schema fix unreachable for any learner with an existing project. D1 was the same declarative-vs-imperative defect 1.7.1 had already fixed in 5a/5b/5c, repeated in the new step 1 of 5f-bis. D2 closed the loop on D1 at the marker-write side. D4 was a reporting honesty issue — the report block was a 1.7.0-era artifact that did not describe a 1.10-only run.

Pattern recognition: each dogfood step (1.10.7 from reading one file, 1.10.8 from tracing the spec) caught a category of bug that test data without a real environment would not have surfaced. The 1.10.0 sprint passed every lint rule and every CHANGELOG cross-check; both bugs needed a real `learn_with_bodhi/` shape to expose. Worth filing this as a habit — schema-touching changes get a dogfood pass against real v2 data before tagging.

## [1.10.7] - 2026-06-09

### Fixed
- **Legacy fallthrough rule corrected — `bloomLevel: 0` alone is the predicate, not `bloomLevel: 0 AND lastReviewed: null`.** The 1.10.0 rule paired the two checks as a conservative guard: a concept with `bloomLevel: 0` only fell through to "allow advancement" if `lastReviewed` was also null. Dogfooding against a real v2 `spaced-review.json` (in `learn_with_bodhi/rails-react-scaling/`) showed every concept had a populated `lastReviewed` from pre-v3 quizzes — which is the normal state of real v2 data. The combined predicate would have **false-blocked module advancement on every existing learner immediately after migration** and would have made `/progress` Mastery % compute `0%` for legacy modules instead of displaying `—`. The corrected predicate uses `bloomLevel: 0` alone — the field has never been written by any v3 writer, so the gate has no opinion; `lastReviewed` is not part of the check.
- **`/teach` Phase 1 prerequisite gate** now allows advancement on any prerequisite with `bloomLevel: 0` regardless of `lastReviewed`; only `1 <= bloomLevel < 3` blocks (the prerequisite has been classified but has not reached Apply).
- **`/progress` Mastery % display** shows `—` for any module where every concept has `bloomLevel: 0`; once at least one concept has `bloomLevel > 0`, the formula computes against the v3-classified subset.
- **`state-schema` and `state-migration` KBs** document the corrected predicate as canonical and carry a historical note explaining why the 1.10.0 rule was wrong, so future contributors do not re-derive the broken combination.

### Added
- **`dev/check.sh` rule 40** catches any file pairing `bloomLevel: 0` with `lastReviewed: null` in the same logical predicate, exempting paragraphs that explicitly mark the combination as historical / broken / corrected. Prevents the regression that the 1.10.0 → 1.10.7 chain just walked through.

### Why this exists
The first real dogfood pass — reading a single live `spaced-review.json` end-to-end before running any skill — surfaced this bug. The 1.10.0 design intent was correct (do not block on a value that no v3 writer ever wrote), but the implementation was overdetermined: requiring both `bloomLevel: 0` AND `lastReviewed: null` mis-modeled how migration interacts with pre-v3 data. The corrected rule keeps the design intent and matches the data shape that migration actually produces.

The good news: the 1.10.7 fix is a four-file edit (`state-schema` KB, `state-migration` KB, `/teach`, `/progress`) and the lint rule preventing regression is one paragraph. The five other v3 writers (`/quiz`, `/explain`, `/practice`, `/forget`, `/pair`) never used the `lastReviewed`-paired check — they all set `bloomLevel` directly on the concepts they touch, which is the correct shape.

This is a tail patch on a tail patch (1.10.6 closed the audit, 1.10.7 closes a regression the audit-closure work introduced) — but the rationale for keeping it as its own minor release is the same as 1.10.6's: v1.10.5 and v1.10.6 are tagged and on Codeberg. Retroactively editing them would mislead anyone who installed at the old SHA.

## [1.10.6] - 2026-06-09

### Changed
- **`/quiz` Phase 2 now ZPD-signal-gated, not Bloom-distribution-only** (M4). The original Question Mix table set the prior distribution; the new within-quiz adjustment treats the mix as a *budget* and shifts the *distribution* on the fly based on `zone-of-proximal-development` KB signals. Below-ZPD signals (quick correct, no engagement) move the next question up one Bloom level; two consecutive Below signals drop the easier band entirely. Beyond-ZPD signals (repeated "I do not know," hint did not help) step down one level; two consecutive Beyond signals drop the harder band and ground out where the learner can demonstrate something. Total question count unchanged; the distribution adapts to where the learner actually is rather than where the prior assessment said they were.
- **`/learn` Phase 3 Plan Principles now require a Spiral Revisit per phase** (M21). Each phase after Phase 0 MUST name at least one concept from an earlier phase that this phase revisits at a *higher* target Bloom level — the `constructivism` KB's spiral-curriculum mechanic made enforceable rather than aspirational. Each `plan/phase-{N}.md` file includes a `## Spiral Revisits` section near the top declaring which concepts are being deepened and from which earlier phase. `/plan` View mode (1.10.5) reads these sections to surface the spiral arc; `/plan` Regenerate (1.10.3) preserves them.
- **Two new lint rules in `dev/check.sh`** (rules 38, 39 — single-severity err since 1.10.5): `/quiz` Phase 2 must reference `zone-of-proximal-development` KB; `/learn` Phase 3 must declare the per-phase Spiral Revisit requirement.

### Why this exists
Two audit findings (M4, M21) were missed during the 1.10.0–1.10.5 sprint despite each being listed and validated in `dev/gaps_of_pedagogy.md`. The post-tag verification turned them up by diffing the audit's finding-ID set against the CHANGELOG's references. Both fixes are small (one phase reference + one principle each); shipping them under their own patch release rather than retroactively editing the 1.10.5 tag preserves the as-shipped record while honestly closing the audit.

With M4 and M21 closed, **every finding in the audit's confirmed and adjusted lists is now addressed in code**, with M32 documented as deliberately dropped per the sprint-review D3 rationale. The audit-closure receipt in `dev/gaps_of_pedagogy.md` and the sprint-summary table in the 1.10.5 CHANGELOG remain accurate for their respective releases; this entry adds the missing pair as a tail patch.

## [1.10.5] - 2026-06-09

### Changed
- **Hardcoded Leitner box destinations replaced with KB references** (H4, M7). `/explain` Update Tracking no longer says "Strong → Box 2, Gaps → Box 1" (which silently demoted a learner already in Box 3); now it says "treat as correct recall per the `spaced-repetition` KB — move up one box (max 5)." `/teach` Phase 5 no longer says "Struggled but got there → Box 1" (which conflated productive struggle with failure); now treats struggled-but-arrived as correct (move up one box). The KB defines no "partial" demote rule, and the audit caught both skills inventing one.
- **`/mentor` Phase 4 inverted to learner-generates-first** (H10). The original presented 2-3 paths for the learner to choose from, directly contradicting the `mentoring-theory` KB's explicit Options rule: "The learner generates options, not the mentor." The rewrite asks first ("From where you are now, what paths do you see ahead?"), handles "I do not know" via the negative-space prompt ("What do you NOT want to do next?"), and only after the learner has generated their own paths offers 1-2 augmentation options as a complement — never as the primary list.
- **Canonical retention rollup view** added to the `spaced-repetition` KB (L2). The "Retention Rollup Views" section defines one named 3-tier rollup (Strong = Box 4-5, Building = Box 2-3, Needs review = Box 1). `/evaluate` Phase 4 and `/progress` Spaced Repetition Health both cite the section by name and display the same buckets. Previously each invented its own rollup with subtly different boundaries.
- **`/explain` Phase 2 promoted to CHECKPOINT** (L3). The "Do NOT skip this phase" line read as guidance; the new CHECKPOINT marker matches the formatting used in `/teach-back` and makes the gate enforceable.
- **`/explain` Phase 3 adds a fifth gap bucket: fluency-without-understanding** (A4). The `feynman-technique` KB names three failure signals (jargon-without-definition, vague hedging, skipped steps); Phase 3's original four buckets caught none of them. The new fifth bucket routes any of the three signals into Phase 4's mini-explanation loop.
- **`/mentor` Phase 1 label corrected** from "(Reality)" to "(Kram: Acceptance)" (L6). Phase 3 is the canonical GROW Reality phase; Phase 1 is the Kram acceptance/setup phase. The duplicate label was a mis-tagging, not a phase-order issue — phases 2-5 already flow Goal → Reality → Options → Will canonically.
- **`/practice` Phase 1 prioritizes Box-1 concepts from the current module** (A1). When `$ARGUMENTS` is "next" or absent, the skill now reads `.bodhi/spaced-review.json` for Box-1 concepts tied to the current module and prefers one of those for the exercise — Box 1 is the highest-leverage deliberate-practice target the system can name. Falls through to plan-position only if no Box-1 concept exists for the module. Explicit `$ARGUMENTS` always wins; the skill does not override the learner's stated choice.
- **`/practice` Phase 2 sketch-before-scaffolding gate + variation enforcement** (A2). Per the `desirable-difficulties` KB's **generation** principle, Beginner and Intermediate tiers now run a 30-second sketch step before scaffolding is delivered ("Walk me through how you would approach this in 2-3 sentences"); obvious wrong-turns get surfaced before the learner invests in implementation. Per the **variation** principle, the skill reads prior entries in `exercises/<current-module>/` before designing the exercise and varies context if a prior exercise covers the same concept. Advanced tier skips the sketch gate — the absence of scaffolding *is* the sketch step.
- **`/plan` View mode surfaces Spiral Revisits** (A7). New section in the view output reads each `plan/phase-{N}.md` and extracts concepts that reappear in later phases at higher target Bloom levels. If the plan does not declare target Bloom levels for revisits, the section says so honestly ("Spiral revisits not declared in current plan — run `/plan regenerate` to apply the constructivism principle.") rather than omitting silently.
- **`/mentor` Phase 5 success-measurement prompt** (A8). The Will phase now asks the third canonical GROW-Will question — "How will you know you have succeeded?" — capturing the answer in the learner's own words. Timeline and commitment are already operationalized via the `/learn` handoff; success-measurement was the missing third.
- **All M1-M5 lint warns promoted to hard fails.** `dev/check.sh` is now single-severity — every rule emits `err` and exits 1 on violation. The `warn()` helper is kept for future intentionally-soft checks but no current rule uses it. The pre-existing 1.7.0 soft-warn rules (12-15) are also promoted; the `docs/example-project/` is in v2 layout per 1.7.1 so the promotion is no-op on current data.

### Why this exists
M6 closes the remaining single-finding fixes the audit identified — eleven targeted edits across nine surfaces. The cluster has two themes: (a) the audit caught skills that *cited* the KB but then invented inline mechanics that contradicted it (H4, M7 hardcoded boxes; H10 inverted Options; L2 reinvented rollup), and (b) the audit caught skills that *honored* the KB in spirit but missed a specific operationalization the KB calls out by name (L3 missing CHECKPOINT; A4 missing fluency-without-understanding bucket; A1 missing Box-1 prioritization; A2 missing generation gate; A7 missing spiral revisits in View; A8 missing success-measurement prompt; L6 label correction). The fixes are individually small; in aggregate they tighten the contract between every cited KB and the skill that cites it. The lint promotion makes future drift catchable at PR time rather than surfacing in audit form months later — which was the whole point of the authoring contract in the first place.

### Sprint summary (1.10.0 → 1.10.5)
This release closes the pedagogy audit (`gaps_of_pedagogy.md`): **35 confirmed findings + 9 adjusted = 44 actionable items**, plus the sprint review's D1/D2/D3/D5 corrections, all landed across six minor releases. Per-release summaries:

| Release | Closes | Theme |
|---|---|---|
| 1.10.0 | H1, H2, H3, M2, M3 | Per-concept Bloom + Feynman tracking makes mastery observable |
| 1.10.1 | H5, H6, H9, M13, A5 | `/reflect` Phase 2 rewritten as retrieval-first calibration |
| 1.10.2 | H11, H12, H13, M27, A3, A9 | 1.4.0 chains wired as opt-in offers (not auto-invocations) |
| 1.10.3 | M10, M12, M14, M16, M18, M20, M23, M24, M26, A6 | KB references batch + `/evaluate` Phase 2.5 calibration |
| 1.10.4 | M5, M6, M8, L8 | `/pair` fully wired with ZPD-signal-gated reversal |
| 1.10.5 | H4, M7, H10, L2, L3, L6, A1, A2, A4, A7, A8 | Targeted fixes + lint promotion to single severity |

**Total: 44 findings closed.** Lint is now hard-fail on every rule. The plugin's authoring contract is fully enforced — any future drift between cited KB and citing skill, between schema declaration and skill writer, between offer text and chain flag, will surface as a build failure.

## [1.10.4] - 2026-06-09

### Changed
- **`/pair` Mode 1 step 7 (role reversal) is now ZPD-signal-gated, not time-gated.** The hardcoded "After 10-15 minutes of strong-style, offer the switch" was scaffolding-by-clock, contradicting the `zone-of-proximal-development` KB's principle that scaffolding must fade as competence grows. The rewrite uses four observable-in-conversation signals (re-specified per the sprint review's D5 correction): the learner volunteers the next navigation step before being asked; their post-piece explain-back goes deeper than asked (trade-offs, edge cases, connections); a divergence they pushed turned out to be the better approach; or they preempt a syntax hint two or more times. When at least two fire, the switch is offered. A 5-minute floor prevents premature offers (the learner needs surface to demonstrate signals); a 25-minute ceiling triggers the Analogy-Escalation Protocol or sub-concept decomposition instead of pushing reversal that is not coming.
- **`/pair` Session End now references the `spaced-repetition` KB** and writes the v3 per-concept fields per the `state-schema` KB — new concepts initialize with `bloomLevel: 0`, `feynmanPassed: false`, `consecutiveCorrectAtL4Plus: 0`; mastery-demonstrated concepts move up one box per the KB's correct-recall rule. `feynmanPassed` is NOT set here — pairing's step-6 explain-back is necessary-but-not-sufficient for the gate (that field is owned by `/teach` and `/explain` Phase 5). Closes the v3-fields lint warn that was deferred from M1.
- **`/teach` Phase 4 has a Below-ZPD escalation gate.** Before delivering the calibrated exercise, the skill checks whether the Phase 2 Checkpoint signaled the learner is *Below* the ZPD (instant correctness AND flat acknowledgment AND no questions). If so, the planned exercise would be busywork; the skill instead skips ahead within the module, escalates the Bloom tier, or surfaces the choice to the learner. Beyond-ZPD is already covered via the Analogy-Escalation Protocol; this gate covers the opposite tail.
- **`/practice` Phase 3 now offers `/pair` as a collaboration alternative** to decomposition when the learner is stuck before starting. The decomposition path stays available; pair is named as a peer alternative, not a replacement, for learners who would do better with collaboration than further breakdown.
- **Four new lint rules in `dev/check.sh`** (warn for now, promoted in 1.10.5): `/pair` Mode 1 must reference ZPD for reversal gating; `/pair` Session End must reference spaced-repetition; `/teach` Phase 4 must reference ZPD (Below-ZPD gate); `/practice` Phase 3 must offer `/pair`.

### Why this exists
Four audit findings (M5, M6, M8, L8) clustered on `/pair`'s under-instrumentation relative to its documented pedagogical surface area. The audit named `/pair` as the most under-cited skill in the plugin: time-gated where it should be competence-gated, silent on the spaced-repetition contract it actually applies, and absent from `/practice`'s stuck-branch offer list. M3 already wired the `/teach → /pair` offer; M5 finishes the work — ZPD-gated reversal, spaced-repetition contract honored, and the bidirectional `/practice → /pair` offer added.

The sprint review (D5) caught that the audit's original "typing without hesitation" / "anticipating the next step" signals were not observable in a chat-based skill (the AI sees turns, not keystrokes or pauses). The re-specified signals are observable-in-conversation: volunteering navigation, going deeper than asked, divergence-as-navigation, preempting hints. They map to the same Below-ZPD detection rationale without requiring keystroke analytics.

The Below-ZPD gate in `/teach` closes the opposite tail of the ZPD gate the plugin already had. The original Phase 4 scaffolding selector keyed off Bloom level alone — never re-evaluating whether the learner's actual session signals matched the Bloom level on file. A learner who reaches Phase 4 with engaged-and-confident answers gets escalated; a learner who reaches it with flat-and-disengaged answers gets skipped past. Both responses respect what the conversation just showed.

## [1.10.3] - 2026-06-09

### Added
- **`/evaluate` Phase 2.5 — Predict Your Trajectory.** Before the Phase 3 trajectory-analyzer reveal, the skill collects three quick predictions from the learner: biggest growth, biggest gap, per-topic Bloom snapshot. Phase 4's report surfaces the calibration delta explicitly — what was predicted vs what the data shows — framed as the metacognition signal underneath every other skill. Across multiple evaluations the gap should shrink; that shrinkage *is* the calibration meta-skill. Capped at 60 seconds; quick predictions, not deliberation.
- **`predictionDelta` field on `assessment-history.json` entries** (optional). Populated by `/evaluate` Phase 2.5; absent for other triggers. Fields: `predictedBiggestGrowth`, `measuredBiggestGrowth`, `predictedBiggestGap`, `measuredBiggestGap`, `perTopicBloomPredictions[]` (each `{name, predicted, measured}`), one-sentence `calibrationNote`. Documented in `state-schema` KB.
- **`learnerSelfRating` collection in `skill-assessor` agent.** Before the first question on each sub-topic, the agent asks a single 1-5 self-rating. Output table gains a `Self-rating (1-5)` column. Parent skills (`/learn`, `/assess`, `/evaluate`) can compute Dunning-Kruger calibration deltas at sub-topic granularity. The rating does not bias question difficulty — the adaptive sequence remains independent.

### Changed
- **Eight KB references added at the canonical phase / mode** where the methodology was implicitly honored but not cited — closing the audit's "implicit citation" pattern:
  - `/pair` Mode 2 now references `deliberate-practice` (Ping-Pong IS deliberate practice — edge-of-ability per round, immediate red→green feedback, variation across rounds enforced).
  - `/teach` Phase 4 now references `desirable-difficulties` (the "slightly harder" framing now grounds in **generation** and **variation** specifically).
  - `/debug-together` Phase 0 now references `growth-mindset` (the "praise the debugging process" instruction grounds in the false-effort nuance with concrete strategy-praise examples).
  - `/evaluate` now references `metacognition` (Phase 2.5 is the load-bearing application).
  - `/teach-back` Phase 4 now references `constructivism` (the Phase 4 silence rule is the KB's "fully independent" tier; teach-back is the plugin's capstone instance of project progression by level).
  - `/mentor` Phase 4 now references `constructivism` for the spiral-curriculum mechanic; each suggested option must name the concept it revisits at a higher Bloom level.
  - `/plan` Regenerate now references `zone-of-proximal-development`, `constructivism`, and `spaced-repetition` at the top of the mode; the cross-reference fix points to `/learn` Phase 3 (principles) plus Phase 4 (layout), not Phase 4 alone.
  - `/practice` Phase 2 now cross-references the `constructivism` KB's 5-tier project ladder, noting Beginner/Intermediate/Advanced map to tiers 2-4 at exercise scope.
- **Six new lint rules in `dev/check.sh`** (warn for now, promoted in 1.10.5): rules 28-33 enforce each of the above references at the right phase / mode.

### Why this exists
Ten audit findings (M10, M12, M14, M16, M18, M20, M23, M24, M26, A6) flagged a single pattern: the methodology was honored in practice — the right framing, the right pacing, the right principles — but not cited explicitly. The progressive-disclosure contract requires the cite: a phase that uses a methodology MUST load its KB, both so a contributor can trust the file is the canonical home and so the lint can catch drift. The fixes are mostly one-line additions; `/evaluate` Phase 2.5 is the substantive change because the audit identified it as the highest-leverage Dunning-Kruger calibration moment in the plugin — and one the existing flow simply skipped past.

## [1.10.2] - 2026-06-09

### Changed
- **CHANGELOG 1.4.0's auto-invoke chains are wired** — but as **opt-in offers**, not auto-invocations, mirroring the 1.8.0 Capstone pattern. The original 1.4.0 contract overstated the integration ("/teach Phase 3 auto-invokes /pair", "/practice + /teach auto-invoke /debug-together when code breaks", "/evaluate auto-invokes /mentor at milestones"); 1.10.2 honors the spirit (the partner skill is named, the chain flag is wired, the moment is identified) without the loss of learner agency that an unconditional auto-invoke would cause. Each offer surfaces at the canonical moment, names the trade-off ("the longer path that teaches the skill"), and lets the learner accept or decline.
  - **`/teach` Phase 3** now offers `/bodhikit:pair --invoked-from=teach <concept>` when the We-Do step would move from talking-through-approach to typing code. Skipped when the concept is purely conceptual, the learner already declined pair this session, or the session is in its last 5-10 minutes.
  - **`/practice` Phase 3 step 4** ("If the code does not work") now offers `/bodhikit:debug-together --invoked-from=practice <brief description>` after Hint 2 (Approach) — before the Near-solution hint, so accepting the offer routes to TRAFFIC rather than collapsing to a near-solution that teaches the fix more than the debugging.
  - **`/teach` Phase 4 step 4** ("Not working") now offers `/bodhikit:debug-together --invoked-from=teach <brief description>` instead of going straight to the Socratic-method one-liner. Per the CLAUDE.md chain convention, the failing code is discovered from `exercises/<current-module>/` — no file path is passed positionally.
  - **`/evaluate` Closing** now offers `/bodhikit:mentor` after the existing Capstone offer (when shown) or as the sole offer at a major milestone. Triggers: project moves to `completedProjects` OR ≥2-level Bloom delta on any major topic since the previous evaluation OR ≥1-level delta on 3+ topics simultaneously. Skipped on mid-journey evaluations without a milestone.
- **Chain-guard pattern extended to `/pair`, `/debug-together`, and `/mentor`.** Each now checks `$ARGUMENTS` for `--invoked-from=`; when present, they skip personality/state-schema reload and skip their setup framing (the caller has context). `CLAUDE.md`'s "Currently chainable" list expands from 6 skills to 9, with a chain-shape note clarifying that the three new entries are offered (opt-in), not auto-invoked.
- **Five new lint rules in `dev/check.sh`** (warn for now, promoted in 1.10.5): rule 9 expanded to enforce the chain guard on the new chainable trio; rules 22-26 enforce offer language at the canonical moments (`/teach` Phase 3 → `/pair`, `/practice` Phase 3 → `/debug-together`, `/teach` Phase 4 → `/debug-together`, `/evaluate` → `/mentor`) and check that the three new chainable skills declare their offer/opt-in framing in the opening 30 lines.

### Why this exists
Five audit findings (H11, H12, H13, M27, A3, A9) traced to the same gap: CHANGELOG 1.4.0 documented four auto-invoke chains, GUIDE.md referenced them, but none was actually wired in the relevant phases. The audit's recommended fix was to wire the chains; the sprint review (D2) pushed back against unconditional auto-invocation as a state-machine risk (no return semantics exist in the plugin today; the existing `/continue → /status → /teach → /reflect` chain is sequential composition by the caller, not nested with handback). Opt-in offers close the same findings — the partner skill is named at the moment the audit identified, the chain flag is wired, the learner's agency is preserved — without inventing new return semantics. Accepting an offer transfers control; declining keeps the current skill's flow intact. The Capstone pattern (1.8.0) is the template: a structured invitation framed as credibility-protection, not gatekeeping.

The "decline by default" framing matters pedagogically. An auto-invoked `/debug-together` would teach the learner that bugs require a heavy ceremony; an *offered* `/debug-together` teaches that there is a longer path available when the shorter path stalls — and that choosing the longer path is itself a learning move. Same goes for `/pair` (collaboration is a tool, not a default mode) and `/mentor` (cross-project reflection is invited, not imposed at every milestone).

## [1.10.1] - 2026-06-09

### Changed
- **`/reflect` Phase 2 rewritten as a retrieval-first calibration loop.** The bare 1-10 confidence rating is gone; in its place, Q3 runs retrieval → rating → cross-check. Step 1 asks the learner to explain the concept in 2 sentences before rating, applying the `feynman-technique` KB's three fluency-without-understanding signals (jargon-without-definition, vague hedging, skipped steps) silently. Step 2 collects the rating. Step 3 cross-references today's `progress.md` and the day's `reviewHistory[]` entries on this concept. Only then does the Leitner update fire: promote ONLY IF confidence ≥ 8 AND retrieval was clean AND observed outcomes align; hold the box (naming the calibration gap aloud) if confidence is high but retrieval or outcomes disagree; demote to Box 1 on confidence ≤ 4, retrieval failure, or learner decline. The invented "5-7 → Box 1-2 depending on current box" rule is gone — there was no canonical home for it in the `spaced-repetition` KB; mid-band now holds and retests tomorrow.
- **`/reflect` Phase 3 strategy-naming acknowledgment.** Per the `growth-mindset` KB's false-effort nuance, high-confidence-with-aligned-outcome acknowledgments now name the *strategy* that worked ("your approach of breaking it into smaller cases"), never the *trait* ("you got it"). The mismatched-outcome row reinforces the calibration framing rather than glossing it.
- **`/reflect` → `/practice` handoff at weak signals.** For any concept named in Q1 as hard OR rated 1-4 in Q3 OR with retrieval failure, the skill offers (does not auto-invoke) `/practice <concept>` for the next session. Acceptance writes the concept into `state.json.lastActivity` so the next `/continue` opens with the targeted deliberate-practice rep.
- **Four lint rules added in `dev/check.sh`** (warn for now; promoted in 1.10.5): `/reflect` Phase 2 must reference `metacognition` and `feynman-technique` KBs; Phase 3 must reference `growth-mindset` and `deliberate-practice` KBs.

### Why this exists
Five audit findings (H5, H6, H9, M13, A5) clustered in `/reflect` Phase 2 around a single mistake: the bare confidence rating promoted concepts up a Leitner box on self-report alone, with no comparison against demonstrated performance. That is exactly the Dunning-Kruger trap the `metacognition` KB names and the illusion-of-competence pattern the `feynman-technique` KB is designed to catch. The KB said "compare to actual result"; the skill compared to nothing. One Phase 2 rewrite closes all five — and changes the retention contract from "the learner reports retention" to "the learner demonstrates retention, then reports it, then we cross-check." The 30-60 seconds this adds per concept is itself a deliberate-practice rep (the `desirable-difficulties` KB's retrieval principle) — Bjork-correct cost.

## [1.10.0] - 2026-06-09

### Added
- **Per-concept Bloom + Feynman tracking** in `spaced-review.json`. Three new fields on `concepts[]`: `bloomLevel` (0–6, current per-concept level; ratchet-up only — never demoted by routine writers), `feynmanPassed` (boolean; set once by `/teach` Phase 2 Checkpoint or Phase 5 retention check or `/explain` Phase 5 on a strong explain-back; never unset), `consecutiveCorrectAtL4Plus` (counter; incremented by `/quiz` on correct AND `bloomLevel ≥ 4`; reset to 0 on any incorrect or on `/forget`). `reviewHistory[]` entries now also carry `bloomLevel` (which level the question tested at). The canonical mastery formula now lives in the `state-schema` KB: `mastered = (bloomLevel ≥ 4) AND (consecutiveCorrectAtL4Plus ≥ 3) AND (box ≥ 4) AND (feynmanPassed === true)`. Skills MUST NOT redeclare this formula inline.
- **Prerequisite Bloom gate in `/teach` Phase 1.** When selecting a concept from a *new* module (not concept-to-concept within the same module), the skill reads `spaced-review.json` for the prior module's prerequisite concepts. If any has `bloomLevel < 3` AND has been observed post-migration (`lastReviewed !== null`), the gate fires — surfaces the gap to the learner with the seeds metaphor and offers revisit / defer / pause. Pure legacy entries (`bloomLevel: 0` AND `lastReviewed: null`) fall through as "allow advancement" — the gate cannot judge what was never observed.
- **`/progress` Mastery % column is now computed**, not fabricated. Uses the canonical formula. When every concept in a module is in pure legacy state, displays `—` instead of `0%` to avoid the false implication that the learner tried and failed.
- **`/housekeep migrate` v2 → v3 step (5f-bis).** Inline-fills the three new per-concept fields with safe defaults; preserves pre-v3 `spaced-review.json` at `.bodhi/.pre-1.10-backup/spaced-review.json` for one minor version; idempotent and step-verifying per the 1.7.1 imperative-write pattern. The migration marker is gated on `spaced-review.json` reaching `version: 3` with all three fields present on every concept.
- **Three new lint rules in `dev/check.sh`** (currently `warn`, promoted to `err` in 1.10.5): skills writing `spaced-review.json` must mention at least one v3 field; `/teach` must mention the prerequisite Bloom gate; `/progress` must mention the canonical mastery formula or the legacy fallthrough.

### Changed
- `spaced-review.json` schema bumped to `version: 3`. All other tracking files remain `version: 2` — per-file version is a schema-shape generation, not a cohort marker; the `state-migration` KB documents the v2 / v3 split explicitly. Skills MUST read-tolerate v2 (auto-fill defaults) before writing v3.
- `/quiz` Phase 3 now writes `bloomLevel` per `reviewHistory[]` entry, updates `concepts[].bloomLevel` to the highest correctly-answered level (never demote), and maintains the `consecutiveCorrectAtL4Plus` counter.
- `/teach` Phase 2 Checkpoint and Phase 5 retention check now write `feynmanPassed: true` when the learner produces a clear, jargon-free explanation. Phase 5 writes per-concept `bloomLevel` (preserve higher; never demote).
- `/explain` Phase 5 writes `feynmanPassed: true` on a strong final explanation and updates `concepts[].bloomLevel` to the inferred upper bound.
- `/practice` Phase 3 step 6 writes `concepts[].bloomLevel` on successful exercise completion — capped at the highest level the learner actually demonstrated, not the exercise's nominal tier. Does NOT write `feynmanPassed` (that field is owned by skills that run an explicit explain-back gate).
- `/forget` resets `consecutiveCorrectAtL4Plus: 0` on demote; preserves `feynmanPassed` (passed once is forever; the demote captures retention drift, not understanding regression).

### Why this exists
Five audit findings (H1, H2, H3, M2, M3 — see `gaps_of_pedagogy.md`) converged on a single root cause: the `blooms-taxonomy` KB defined mastery as "Level 4+ AND 3 consecutive correct AND Box 4–5 AND Feynman passed," but none of those pieces was tracked per concept. `state.json.currentBloomLevel` was sub-topic-coarse; `spaced-review.json.concepts[]` carried no Bloom or Feynman fields; no skill recorded the level a quiz question tested at. So every skill that surfaced "mastery" (the `/progress` Mastery column, the implied `/teach` advancement gate, the assessment-framework's Progression Gates) was either fabricating or silently omitting the answer. One schema extension closes all five — and makes Bloom advancement observable in the place a learner actually feels it: the moment `/teach` would otherwise wave them past a half-rooted prerequisite.

The legacy fallthrough rule (`bloomLevel: 0` AND `lastReviewed: null` = allow advancement) is the M1.4 backfill-bug fix from the sprint review: the gate cannot judge concepts the migration created from thin air with no observation history. Once any v3 writer touches a concept, normal gate logic applies.

## [1.9.2] - 2026-06-08

### Changed
- `GUIDE.md` adds **"The Pedagogy Behind BodhiKit"** — a new section between *Understanding Your Progress* and *How Spaced Repetition Works* answering three questions for the learner: what pedagogy, why, when each fires. Twelve per-methodology cards (Bloom, Spaced Repetition, ZPD, Feynman, Deliberate Practice, Desirable Difficulties, Growth Mindset, Metacognition, Constructivism, Mentoring/GROW, Pair Programming, Scientific Debugging). Each card: what it is, why BodhiKit uses it (the specific learning problem), when it fires (skills + phases), one link to a primary source. Closes with a "How they compose" table showing which methodologies fire at each phase of a learner's journey.
- `Pedagogy:` cross-links added under the Example of 10 skill entries (`/teach`, `/reflect`, `/quiz`, `/forget`, `/explain`, `/practice`, `/pair`, `/debug-together`, `/mentor`, `/teach-back`) so a learner reading about a skill can click through to the underlying research without leaving the GUIDE.

### Why
The GUIDE previously named methodologies in passing (Bloom in `/assess`, Feynman in `/explain`, etc.) but offered no answer to a learner who asked "what pedagogy and why?" The Science section in the README has the citations but no "when it fires" mapping, and the GUIDE did not link to it. The new section closes that gap with deep-dive links at the card level, and the per-skill cross-links make the pedagogy discoverable from any direction.

## [1.9.1] - 2026-06-08

### Changed
- `GUIDE.md` expanded from a thin reference (538 lines) into a complete usage manual (~992 lines). Two structural additions: (1) a "Your Journey from Zero to Completion" worked example following a backend Python engineer learning Rust over 10 weeks — Day 1 install through capstone, with real dialogue snippets and which skill to invoke when; (2) Skills Reference rewritten with a 5-field template per skill (What it does / When to use / When NOT to use / Pairs well with / Example) covering all 20 skills, grouped into six functional categories. Redundant prior sections (Starting a Project, Resuming, Daily Workflow) absorbed into the journey arc — no information lost.
- README link blurb to `GUIDE.md` updated to advertise the new scope.

### Why
The 1.9.0 GUIDE was a reference, not a how-to. Users had no zero-to-completion path and no guidance on when to reach for each skill. A concrete worked example carries more weight than topic-neutral prose, and the 5-field per-skill template makes optimal usage scannable and comparable.

## [1.9.0] - 2026-06-08

### Added
- **Analogy-Escalation Protocol** in `knowledge/feynman-technique/SKILL.md` — a single named protocol every struggle-sensitive skill reaches for when the learner is stuck. Trigger conditions tied to the ZPD "Beyond" signals (cannot articulate confusion, Approach-level hint did not move them, mechanical explain-back, surviving misconception). 4-rung ladder: (1) learner's own domain from `.bodhi-profile.json` `learnerBackground.domains[]`, (2) ask-once for a domain if none on file or all used for this concept, (3) universal-physical analogy as fallback, (4) code-restatement as last resort. Hard 2-analogy cap per concept — after two, the protocol decomposes to a smaller sub-concept rather than reach for a third analogy (correct ZPD response).
- `learnerBackground` object on `.bodhi-profile.json`: `domains[]` (cross-project list of fields/hobbies/jobs the learner knows well) and `analogyHistory[]` (append-only `{concept, domain, landed, date}` log so future invocations on the same concept pick a different domain). Both fields optional; absence means "no prior data" and the protocol falls through naturally. Documented in the `state-schema` KB; writers list updated.

### Changed
- `/teach` Phase 2 Checkpoint and Phase 4 hint chain (between Approach and Near-solution) now invoke the Analogy-Escalation Protocol instead of the one-line "different analogy" instruction.
- `/explain` Phase 1 prefers learner-domain analogies when `learnerBackground.domains[]` is populated; Phase 4 routes gap-refinement through the protocol's ladder rather than picking a random angle. The 2-analogy cap applies per gap.
- `/debug-together` Phase 2 (Hypothesize) pauses debugging and applies the protocol when rubber-ducking surfaces a conceptual gap underneath the bug. Phase 5 (Fix) applies the protocol between Approach and Near-solution hints.
- `/pair` strong-style step 6 (post-piece explain-back) and ping-pong step 3 (learner makes the test pass) invoke the protocol when the explanation is mechanical or the Approach hint did not unstick them.

### Why this exists
Analogies were already mentioned in three places (`feynman-technique` KB step 2, `/teach` Phase 2, `/explain` Phases 1 and 2), but as scattered instructions without a shared trigger condition, escalation order, or cap. The result was that analogies appeared inconsistently across skills — present in `/teach` and `/explain`, absent in `/debug-together` and `/pair` where struggle is most acute — and when they did fire, they reached for universal-physical analogies (mailboxes, libraries) before any attempt to ground in the learner's actual world. The new protocol makes analogy a **response to detected struggle**, escalates from the learner's domain first (highest leverage, lowest reuse if not personalized), caps at two before falling back to sub-concept decomposition (the real ZPD answer), and records what worked so the next session does not repeat. The "ask once for a domain" rung is gated to the moment struggle is detected — the learner is not interrogated at project start about their hobbies, only asked when an analogy is actually about to land.

## [1.8.0] - 2026-06-08

### Added
- `/teach-back` skill — optional capstone offered after `/evaluate` moves a project to `completedProjects`. The learner writes a Socratic-style blog post on a *formerly-shaky-now-solid* topic (multiple assessments climbing from Bloom <3 to ≥4, at least one demote-and-recover in spaced review, currently Bloom ≥4 AND Box ≥3), reads 3–5 acknowledged masters' work on the same topic *after* drafting (Bjork desirable-difficulty sequence — read after, not before), and decides for themselves whether to publish. **The skill never pronounces a post ready or not-ready** — that verdict is earned by the learner against the field, framed as credibility-protection rather than gatekeeping. Posts saved to `learningWithBodhi/<project>/teach-backs/<YYYY-MM-DD>-<slug>.md` (sibling to `.bodhi/`, not inside it, so the learner can edit them in their normal workflow). Reuses `trajectory-analyzer` for candidate topic surfacing and `resource-finder` (with masters-only instruction) for source discovery.
- `/evaluate` Closing section now emits a one-paragraph opt-in offer for `/teach-back` whenever this evaluation moves the project from `activeProjects` to `completedProjects`. Mid-journey evaluations skip the offer. Never auto-invokes.
- `cumulativeStats.teachBacksWritten` and `cumulativeStats.teachBacksPublished` fields added to `.bodhi-profile.json` (default 0; learner self-reports `published` if they actually publish). Profile-writer table in `state-schema` KB updated to list `/teach-back` as a writer.
- `teach-backs/` registered as a new tracking-surface family in `state-schema` KB. Per-post markdown files. Not housekept. Only `/teach-back` writes.

### Why this exists
The system already had a clear ending — `/evaluate` confirms completion and moves the project to `completedProjects`. But "completed" was the *measurement* of mastery, not the *demonstration* of it. The capstone gives the learner a way to demonstrate mastery the way the masters themselves did: by writing something defensible on a topic that was once hard. Picking *formerly-shaky* topics (rather than easy ones) honors Bjork's desirable-difficulty principle and produces the more useful post — the next learner benefits more from "I kept getting this wrong until I realized X" than from "here's how X works." Reading the masters *after* drafting (not before) is the second half of Feynman's technique; reading first would turn the post into a summary of what was read. And the publish question is framed as credibility-*protection* ("publish only when you can defend every claim") not credibility-*building* ("publish to be seen") — the former keeps the learner's interests aligned with the bodhi metaphor of awakening passed forward; the latter would have made BodhiKit into a hype engine at the moment of graduation.

## [1.7.1] - 2026-06-06

### Fixed
- **`/housekeep migrate` write defects.** The v1.7.0 migrate spec used declarative language ("remove the field", "bump the version", "replace progress.md with...") for steps that mutate `state.json` and `progress.md`. Executing models interpreted these as state-descriptions rather than file-write actions, so on real data the migration created the new directories, split `plan.md`, and wrote the receipt — but never actually rewrote `state.json` (left v1 `lastSessionSummary` + `bloomResetNote` fields intact and `version: "1.5.0"` unchanged) or rewrote `progress.md` to v2 live+archive+summary shape. Steps 5a, 5b, and 5c rewritten with explicit imperative writes ("Write the new content using the Write tool"), per-step idempotency checks, and post-write verification. The marker file (5g) now has an explicit precondition block — verify every preceding step persisted to disk before declaring migration complete. A broken migration can no longer falsely report success.
- `.bodhi-profile.projects.json` was being written as `version: 1` because the `state-schema` KB declared it that way. Pinned to `version: 2` in the KB for cohort consistency with every other v2 file; `/housekeep` skill spec updated to enforce.
- `docs/example-project/.bodhi-profile.json` was still in v1 single-file layout (despite v1.7.0 PR 5b claiming otherwise). Split into v2 layout: top-level profile + `.bodhi-profile.projects.json` sibling.

### Added
- `/status all` — table view of every project (active/stale/dormant classification, last-session, completion, health flags). Reads `.bodhi-profile.projects.json` plus each project's `state.json` only — no progress/plan/archive reads.
- `/status <project-name>` — single-project glance for a specific project regardless of which is most recently active.
- Health flags in `/status all`: `⚠ v1 fields` (unmigrated narrative fields in `state.json`), `⚠ unparseable` (JSON parse failure), `⚠ missing files` (state.json present but plan/ or progress.md absent), `⚠ legacy layout` (incomplete migration — `.bodhi/plan.md` or `.bodhi/assessment.md` singular still exist).
- `/learn` **Phase 1.5 — Cross-Project Reconciliation.** Before running skill assessment for a new project, read `.bodhi-profile.json` + `.bodhi-profile.projects.json` and surface: overlap with existing projects, relevant Bloom priors from prior work, capacity flag when ≥ 3 active projects exist. Presents structured options — standalone / fold into existing / replace existing / defer. Phase 2 (skill assessment) now receives Bloom priors as input. First-time learners with no profile see no change.
- `dev/check.sh` extended: rule 15 verifies `docs/example-project` profile uses v2 split layout (no inline `activeProjects` / `completedProjects`; both files declare `version: 2`). Rules 12 and 13 exempt `/status` alongside `/housekeep` — both are v1-boundary skills by design (one migrates, one detects).

### Changed
- `/continue` Phase 5 was already correct in v1.7.0 (Do NOT write `lastSessionSummary` / `bloomResetNote`); no behavioral change. Mentioned here so contributors don't re-flag it during 1.7.1 review.

## [1.7.0] - 2026-06-05

### Added
- `/housekeep` skill — tends the garden of tracking files. Rotates the previous entries of narrative surfaces (`progress.md`, `assessments/latest.md`) into archive directories and writes a 2–20 line summary block with explicit pointers so nothing is lost and nothing is hidden. Idempotent, non-destructive. Single source of all file-rotation logic — every other skill stays oblivious.
- `/housekeep migrate` — one-shot v1 → v2 conversion of pre-1.7.0 tracking files. Splits monolithic `plan.md` into `plan/README.md` + `plan/phase-<N>.md` files; lifts narrative fields (`lastSessionSummary`, `bloomResetNote`) out of `state.json` into `progress.md`; splits `.bodhi-profile.json` into top-level profile + `.bodhi-profile.projects.json`; reorganizes existing assessment files into `assessments/latest.md` + `assessments/archive/`. Preserves the original monolithic files at `.bodhi/.pre-1.7.0-backup/` for one minor version. Reports before/after byte sizes.
- `trajectory-analyzer` agent (Sonnet, read-only, max 15 turns) — reads a learner's full project history (live + archive + assessments + assessment-history + spaced-review + plan phases) and returns a structured trajectory report: per-topic Bloom movement with evidence quotes, retention distribution, activity timeline, precision-gap movements, completion, patterns. Used by `/evaluate` Phase 1 and Phase 3 so the parent skill stays light; for a learner six months in, ~80 KB of archive load happens in the agent's context instead of the parent's. Learner conversation is unchanged from the previous flow.
- `knowledge/read-defaults` KB — per-skill default-read contract, transparency rule, audit/lint guidance. Loaded only by `/housekeep`, the audit, and the lint; skills do not load it at runtime.
- `knowledge/state-migration` KB — schema versioning, migration table, and the full `/housekeep migrate` procedure. Loaded only by `/housekeep migrate`.

### Changed
- `knowledge/state-schema` KB rewritten for v2 tracking-file layout:
  - **Live + archive + summary pattern** for narrative surfaces (sessions, assessments). The live doc holds the latest entry plus a growing summary block with pointers; full prior text lives in the archive directory.
  - **Sectional layout** for plans. `plan/README.md` + `plan/phase-<N>.md` files. Routine skills load only the current phase.
  - **Slim JSON** for `state.json`. No more long narrative fields — `lastSessionSummary` and `bloomResetNote` removed; their content lives in `progress.md`.
  - **Split JSON** for the cross-project profile. `.bodhi-profile.json` keeps top-level + cumulativeStats + patterns; `.bodhi-profile.projects.json` holds `activeProjects` + `completedProjects` arrays.
  - Universal housekeeping protocol documented; only `/bodhikit:housekeep` rotates files.
- `state.json`, `progress.md`, `assessments/`, `plan/`, `.bodhi-profile.json`, `spaced-review.json` all bumped to schema `version: 2`. Older versions are read-tolerated via inline migration per the `state-migration` KB.
- `/status migrate` removed — the `migrate` subcommand moved to `/housekeep migrate` because all file-shape work now lives in one place. `/status` keeps its legacy-path detection notice but redirects users to `/housekeep migrate`.
- `marketplace.json` `metadata.description` and `plugins[0].description` updated to reflect new counts (19 skills, 18 KBs).
- Version bumped in both `plugin.json` and `marketplace.json`.

### Guiding principle

Progressive disclosure applied to the learner's own state. Nothing deleted. Nothing gatekept. Skills load the smallest useful slice by default and reach into the archive only when the learner's situation justifies it — announcing the read in their turn output. The audit and lint catch *accidental* eager loading; a deliberate, situational read is always allowed.

## [1.6.0] - 2026-06-05

### Added
- `/forget` skill — learner-initiated demotion of one or more concepts back to Box 1; comma-separated lists supported; auto-invoked by `/reflect` (batched once per session) when self-rated confidence is 1–4
- `knowledge/state-schema/` KB — canonical shape for `state.json`, `spaced-review.json`, `progress.md`, `.bodhi-profile.json`, plus the project discovery procedure (single source for all skills)
- `~/.bodhikit/config.json` optional global discovery config (`searchPaths` array). Defaults: `$PWD` (with parent walk) and `~/learningWithBodhi`
- Per-project `<repo>/.bodhikit/config.json` override with `projectRoot` — for users who keep `.bodhi/` somewhere other than `learningWithBodhi/` in a specific repo
- One-shot legacy-path migration via `/bodhikit:status migrate` — detects pre-1.6.0 `~/code/learningWithBodhi` or `~/projects/learningWithBodhi` and writes them into `~/.bodhikit/config.json` so discovery keeps finding them
- `.bodhi/assessment-history.json` — structured Bloom's-over-time data appended by `/learn` Phase 2, `/assess`, `/evaluate`, and `/plan regenerate`. `/evaluate` reads it for trajectory analysis. `assessment.md` remains the prose journal
- `--invoked-from=<caller>` convention for sub-skill chaining. Caller skills (currently `/continue`) pass the flag; chainable skills (`/teach`, `/practice`, `/reflect`, `/status`, `/quiz`, `/forget`) check for it and skip personality/state-schema reload and discovery when set
- Migration discipline section in `state-schema` KB — inline read-time migration pattern for forward-compatible schema changes
- Streak acknowledgment table and empty-state language table moved into `teaching-personality` KB (single source for all skills that open sessions or hit empty states)
- Profile feedback loops — `/reflect`, `/practice`, `/teach`, `/evaluate` now update `learningWithBodhi/.bodhi-profile.json` `cumulativeStats` and `patterns` (persistent challenges, consistent strengths)
- New profile fields: `cumulativeStats.totalConceptsLearned`, `cumulativeStats.totalMilestonesReached`, `patterns.persistentChallenges`, `patterns.consistentStrengths`
- `/resources remove <name>` mode
- `dev/install-hooks.sh` — installs a pre-commit hook that runs `dev/check.sh`
- `CLAUDE.md` at repo root — author/dev notes (not loaded by end-user installs)
- `dev/check.sh` — authoring-contract lint (version drift, frontmatter, agent fallback presence, KB references, voice duplication, chain-flag presence, README skill count)

### Changed
- Leitner box→interval mapping and update rules consolidated into the `spaced-repetition` KB. `/continue`, `/teach`, `/explain`, `/quiz`, `/reflect`, `/practice`, `/debug-together`, `/evaluate`, `/progress` no longer restate intervals
- Tracking file shapes consolidated into `state-schema` KB. Skills now reference it instead of restating field lists
- Project discovery consolidated into `state-schema` KB. Removed hardcoded `~/code/...` and `~/projects/...` paths
- Personality voice rules consolidated into `teaching-personality` KB. Skills, agents, and the path-scoped rule reference it with one line instead of restating DO/NEVER lists
- `/teach` and `/practice` now skip the `code-reviewer` agent invocation when no code file exists for the exercise (saves tokens on prose-only or thought-experiment exercises)
- KBs cross-link (`see also` lines) so the KB graph is navigable in both directions
- `marketplace.json` `metadata.description` corrected (was advertising "11 skills, 3 agents, 3 KBs"; now matches the actual 18/3/16 totals)
- Version bumped in both `plugin.json` and `marketplace.json`; README now displays a version badge
- `docs/example-project/README.md` updated for the new file list and discovery layers
- `.gitignore` adds `learningWithBodhi/` (defensive — prevents accidental commits when contributors test the plugin against this repo)

### Fixed
- Drift between `marketplace.json` `metadata.description` and `plugins[0].description`

## [1.5.0] - 2026-03-16

### Changed
- Teaching personality grounded in authentic Buddha and Ambedkar philosophies
- Buddha: Upaya (skillful means), four learner types, Kalama Sutta ("test through experience"), sandassetva teaching process, gradual progression
- Dr. B.R. Ambedkar: "Educate, Agitate, Organize", vachan-manan-chintan-adyeyan (listening, reflection, study), education as empowerment and transformation
- Every principle, language rule, and emotional response now traces to a specific teaching from the four root teachers
- Context optimization: teaching-personality 197→67 lines, skills trimmed 20%, phase-specific KB loading, shared-context in /continue chains

## [1.4.0] - 2026-03-16

### Added
- `/mentor` skill — career and learning path guidance using the GROW model (Whitmore) and Kram's mentoring theory
- `/pair` skill — research-backed pair programming with 3 modes: strong-style (Falco), ping-pong with TDD, navigator (Freudenberg)
- `/debug-together` skill — scientific debugging using Zeller's TRAFFIC method, O'Dell's Debugging Mindset, wolf fence algorithm
- Learner profile system (`learningWithBodhi/.bodhi-profile.json`) for cross-project personalization
- CONTRIBUTING.md for open source contributors
- New research references in README: Kram, Whitmore, Beck, Williams & Kessler, Falco, Zeller, O'Dell, Gauss

### Changed
- Learning methodology KB expanded with mentoring, pair programming, and debugging sections
- Teaching personality KB expanded with debugging, mentoring, and pairing language guidance
- `/learn` now creates and updates the learner profile
- `/mentor` auto-invoked by `/evaluate` at major milestones
- `/pair` auto-invoked by `/teach` during guided practice
- `/debug-together` auto-invoked by `/practice` and `/teach` when code has bugs
- Split monolithic `learning-methodology` KB (392 lines) into 13 focused KBs for progressive disclosure (ETH Zurich 2025 research compliance)
- All skills now reference only the specific KBs they need, reducing context load per interaction
- Knowledge base count: 3 → 16
- Skill count: 14 → 17

## [1.2.0] - 2026-03-15

### Added
- `/teach` skill — proactive guided teaching with explain, demonstrate, practice, verify flow
- `/reflect` skill — end-of-session metacognitive reflection with confidence self-rating
- `/status` skill — quick 3-line check-in (project, module, streak, concepts due)
- Example learning project in `docs/example-project/` showing realistic tracking files
- Error handling fallbacks in all skills that use agents (learn, assess, evaluate, review, resources, plan, practice)
- CHANGELOG.md

### Changed
- `/continue` now auto-invokes `/status`, `/teach`, `/reflect` for complete guided sessions
- Skill count: 11 → 14

## [1.1.0] - 2026-03-14

### Changed
- Made agent usage mandatory in all skills (changed "Delegate to agent" to "You MUST use the Agent tool")
- Used respectful full names: Gautama Buddha, Dr. B.R. Ambedkar, Master Oogway
- Fixed install instructions to match marketplace plugin format (two-step install)
- Added research references and credits for all learning methodologies in README

### Added
- .gitignore for OS files, editor state, and local Claude config
- Author signature and buy-me-a-coffee link in README

## [1.0.0] - 2026-03-14

### Added
- Initial release
- 11 skills: learn, continue, assess, review, quiz, plan, progress, resources, explain, practice, evaluate
- 3 agents: skill-assessor (Sonnet), code-reviewer (Sonnet), resource-finder (Haiku)
- 3 knowledge bases: learning-methodology, assessment-framework, teaching-personality
- 1 path-scoped rule: learning-project (activates in learningWithBodhi/)
- README, GUIDE, LICENSE (MIT)
- Plugin manifests for Claude Code marketplace
