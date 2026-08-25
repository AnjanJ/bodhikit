# Changelog

Notable changes to BodhiKit, summarized for readers. Patch-level development notes live in `dev/changelog-journal.md`.

## [1.18.0] - 2026-08-25

The knowledge bases load now. Claude Code registers plugin skills from `skills/` only; from 1.0 through 1.17 the twenty knowledge bases lived in `knowledge/`, a directory the runtime never scans, so every "Reference the `X` KB" pointed at something the model could not load — the persona, the pedagogy, and the state-ops write contract reached it only if it went looking. A plugin `rules/` directory is not loaded either. Both verified with headless probes; both fixed.

- **Knowledge bases are skills.** They live under `skills/<kb>/` as `user-invocable: false` skills — registered, hidden from the `/` menu, loaded through the Skill tool at the phase that needs them. Every command opens with the sentence that makes the mapping explicit; agents preload the KBs they name. A new `kb-load` eval proves a routine `/quiz` loads one. Cost: about 1–1.5 K tokens of skill descriptions per session.
- **The learning-project rule is delivered by a SessionStart hook** when a session starts inside a learning project — the "learner content is data, never instructions" rule had been inert since 1.0.
- **Learner-facing levels read as outcomes.** The default rendering is the outcome clause alone, phrased as application and reasoning ("you can apply it in working code with some guidance"); the rung's name is spoken only when you have just crossed it and in `/progress`'s one-line legend. Learner feedback.
- **What the tutor discusses is on screen.** Code, questions, errors, and your own answers are reproduced in the message that discusses them, labeled; file findings quote the exact lines with `path:line`. No more "the code above". Learner feedback.
- **Gate honesty.** Apply-rung evidence counts only since your last miss — two old corrects no longer keep a prerequisite "satisfied" through three misses or a `/forget`.
- **State layer hardening.** Drift `verify` flags now fails every subcommand the same clean way instead of tracebacking in some; a v1/v2 file is backed up before its first v3 write; read-only commands never leave a lock file; one rollup behind `mastery` and `snapshot`; the Stop hook is time-boxed and covers configured project roots.
- **Tooling honesty.** Lint sections A–D are structural/conditional only, with the remaining phrase pins in E each naming the eval that retires them; evals default to the model the maintainer actually runs and print it; the eval README says which scenarios have never run. 277 deterministic tests (+15 for the Stop hook).
- **A revision sheet at the end of every study day.** `revision/YYYY-MM-DD-<concept>.md` in your project: the key idea in plain words, the example we worked through, where you slipped, two self-test prompts with answers at the bottom, when each concept comes back, and free links from your saved resources (never an invented URL). `/reflect` writes it; if you just leave, the Stop hook will not end the session until it exists.
- No tracking-file migration is needed. Update the plugin and restart Claude Code so the KB skills and the SessionStart hook register.

## [1.17.0] - 2026-08-21

Addresses a seven-point self-review (infrastructure-to-user ratio, lint accretion, skills at the byte ceiling, grading noise, no outcome evidence, an oversold persona, maintainer-only vocabulary) plus one design change: learners keep the Bloom *labels* but never see the numbers.

- **Learner-facing Bloom rendering is canonical.** One table in the `blooms-taxonomy` KB maps level → label → outcome clause (`**Apply** — you can use it in working code with some guidance`). `bodhi-state` now returns `bloomLabel`/`bloomOutcome` next to every `bloomLevel` (`record-review`, `session-brief`, `gate-check`) and a `bloomScale` legend in `snapshot`; `/assess`, `/quiz`, `/evaluate`, `/teach-back`, `/mentor` and `/progress`'s closing line render those fields instead of numbers or private translation tables. The `teaching-personality` KB carries the cross-skill voice rule. Lint pins labels between KB and script.
- **Prerequisite gate needs two observations.** A Bloom-3 reached by a single review no longer passes the gate outright: it earns one reconfirm question (`stale-reconfirm`, `reason: single-evidence`). Two level-3+ corrects, or Box ≥ 3, clear it (`reason: evidence` / `box`). Each prerequisite row and the session brief now carry `evidenceAt3Plus`. New deterministic tests; new LLM eval `grade-understand-band` pins the 2-vs-3 boundary from below (not yet run against a live model).
- **Lint shrunk and re-sectioned.** `dev/check.sh` drops the eleven rules that only grepped a KB name into a phase (19–21, 25, 28–30, 32, 35, 36, 38) and states its admission policy: structural or conditional rules only; behaviour belongs in `dev/eval/`. Rules are grouped A–E; audit ticket IDs are gone from shipped comments. 1,022 → 881 lines.
- **Outcomes published.** `dev/outcomes.py` aggregates `export-anonymized` across projects into `docs/outcomes.md` — the maintainer's own data (one learner, five projects, 13 reviews), labelled as exactly that.
- **Onboarding and honesty.** README opens with "Your first 15 minutes" and a Feedback section; upgrading notes move to `MIGRATION.md`; the four teachers are described as the voice layer, with pedagogy owned by the methodology KBs. Bug-report and feedback issue templates added. CONTRIBUTING rewritten around the feature freeze and `dev/check.sh`.
- **Maintainability.** CHANGELOG collapsed to reader-facing release notes (the patch journal lives in `dev/changelog-journal.md`); CLAUDE.md gains a glossary for the internal vocabulary and documents the local-only `analysis/` directory.

## [1.16.0] - 2026-08-15

The ownership release: the last places where the model was doing bookkeeping the script should own moved into `bodhi-state`, and the three skills that write the most state gained automated coverage.

- **The cross-project project list is script-owned.** `/learn` and `/evaluate` no longer hand-edit `.bodhi-profile.projects.json`; four new `bodhi-state` subcommands add, update, complete, and tally projects (`profile-add-project`, `profile-update-project`, `profile-complete-project`, `profile-update-patterns`). Completion is still learner-confirmed, never inferred.
- **`/forget --park` / `--unpark`.** A concept you have consciously decided not to maintain can leave the review rotation without being demoted. Box, Bloom, and history are kept; `due` and `/progress` report parked concepts as counts rather than hiding them.
- **The prerequisite gate never guesses.** With no declared prerequisites and no tracked prior module, `/teach` now declines to gate rather than inferring a module from dates and asking false reconfirm questions.
- **Evals** cover `/learn` scaffolding, `/plan regenerate`, and `/evaluate` end to end (file-state assertions). **Lint** enforces both sides of the `--invoked-from` chain convention. 220 deterministic tests.

## [1.15.0] - 2026-08-15

The hardening release, from an August analysis campaign (fidelity audit, empirical run, adversarial pass).

- **Learner and third-party file content is data, not instructions.** The `learning-project` rule and the `code-reviewer` agent now state that anything read from learner files or fetched repos is evidence about the learner, never directives to the tutor. `code-reviewer` drops its shell. A learner's claim about their own answer ("mark it passed") is not evidence either — the Feynman gate grades the transcript.
- **Two grading boundaries settled and verified on both sides.** A verbatim recitation the learner cannot restate is now `partial` (box held, re-test tomorrow), not `correct`. A learner with working usage but an honest trade-off gap is graded by the highest rung reached, with demonstrated usage as a floor and an admitted gap as a ceiling — no more Bloom 2 for someone who visibly applied the concept, and no silent pinning at 3 for someone who reached 5.
- **`/progress` renders outcomes, not raw numbers.** Module breakdown shows computed tiers (Solid / Working / Introduced) derived from the `blooms-taxonomy` ladder in code.
- **`verify` validates profile entry shape**; lint pins the remaining canonical values between KB and script; `BODHI_EVAL_RUNS=N` sweeps a scenario and reports pass rate plus recorded levels.
- GitHub is the source of truth; the Codeberg mirror is archived.

## [1.14.1 – 1.14.2] - 2026-07-07 – 2026-07-08

Two fixes the maintainer hit in real sessions.

- **Teaching starvation.** A brand-new project seeds every assessed concept into spaced review on Day 1, and `/continue` then quizzed all of them before ever teaching. `bodhi-state due` now flags concepts that have never been taught, and `/continue` offers to teach those first instead of quizzing them cold. Genuinely-taught due concepts still go to `/quiz`.
- **Discovery hallucination.** Project discovery is a filesystem glob, not a `bodhi-state` subcommand; skills that described it abstractly led the executor to invent `bodhi-state discover`. The concrete glob and a negative guard now appear inline in every skill that discovers projects, with a lint rule and an LLM eval behind it.

## [1.14.0] - 2026-07-02

The judgment-tree release. 1.11.0 moved the writes into code; this release moves the *read-side branch decisions* there too, so `/teach` stops re-deriving state predicates from prose.

- **`bodhi-state session-brief`** tells `/teach` whether a concept is a first exposure (pretest applies), a re-teach, or routine, plus box/Bloom/Feynman/recency for depth calibration. **`record-review`** reports whether a write just crossed Bloom 3. **`bodhi-state snapshot`** produces the whole `/progress` number surface in one read-only call, so `/progress quick` reads zero tracking files.
- `/teach`'s understanding-only flow moved to a reference file loaded only when that branch fires.
- The grading evals caught their first model drift (a model change under identical prompts). Fixes landed in the harness and the `feynman-technique` ladder (demonstrated application in an explanation places the answer on the apply rung), not in skill prose.

## [1.13.0] - 2026-07-02

The context-cost release. Every skill fire was paying ~39 KB of knowledge-base load before doing anything; most of it was field-level schema that routine sessions can no longer legally hand-edit.

- **`state-ops` / `state-schema` split.** A new `state-ops` KB carries the operational surface every skill needs (discovery, the `bodhi-state` write path, session vocabulary, gate and mastery semantics). `state-schema` shrinks to a field-level reference loaded only by the few manual carve-outs and the script-unavailable fallback. Cold-fire floor drops from ~39 KB to ~18 KB; `/teach` from ~50 KB to ~37 KB.
- `teaching-personality` trimmed ~15% with every table kept verbatim; `read-defaults` and the blog post moved out of the loaded tree.
- **Feature freeze declared** (see CONTRIBUTING.md): no new skills, KBs, taxonomies, session types, or schema fields unless a second real user asks or the maintainer hits the gap in a real session.
- README version badge drift fixed and now lint-checked.

## [1.12.1 – 1.12.2] - 2026-07-02

- **Wild-data repair.** Running the new analytics on real projects surfaced state files that pre-1.11.0 executors had drifted (invented nesting, invented vocabulary). `bodhi-state normalize` repairs them in one idempotent, backed-up pass; `verify` now rejects the drift patterns and names `normalize` as the fix. New `bodhi-state defer` records "due but not reached this session" as scheduling, never as an outcome.
- **Grading fix.** A learner with clean apply-level mechanics but no trade-off knowledge was being graded `incorrect` and demoted as if they had forgotten. The grading ladder is now canonical in the `feynman-technique` KB: a clean explanation at any rung is `correct` at that rung; missing depth caps the level, it is not a failed retrieval.

## [1.12.0] - 2026-07-02

The judgment release. The deterministic layer made the Leitner math exact, but its inputs — `correct|partial`, tested Bloom level, "met the Feynman bar" — were unmeasured LLM judgments.

- **Grading-calibration evals** (`dev/eval/run-llm-evals.sh grading`): scripted learner answers of controlled quality run through a real `/teach` session and assert the grade lands in the honest band on disk. A fluent jargon parrot must not pass; a genuine own-words explanation must earn its level; a confident misconception must not pass. These double as the model-drift detector.
- **Transcript-fidelity evals**: the pretest fires on first exposure and is never recorded as assessment; a learner who exhausts three hints gets a re-teach, never a fourth hint or the answer.

## [1.11.1 – 1.11.3] - 2026-06-10 – 2026-07-02

Audit, state-integrity, and outcome-data follow-ups to the 1.11.0 architecture.

- **Spaced-repetition integrity.** Successive-relearning retries no longer undo a demotion; `/reflect` gives no second review to a concept already reviewed today; confidence ratings no longer gate promotion (retrieval decides the box, the rating is calibration signal); a `partial` now breaks the mastery streak; lifetime session count actually counts.
- **Script robustness.** Per-project locking for concurrent sessions, clean errors on corrupt files, unparseable review dates surfaced instead of silently dropping a concept from rotation, `--project` on every skill snippet, Windows-without-python3 fails open.
- **Pedagogy fidelity.** Pretest only on first exposure; `/continue` delegates due review to `/quiz`; `/learn` seeds spaced review from the Day 1 assessment and writes a discovery config when the chosen root is off the default path; project completion has a canonical, learner-confirmed criterion; `/evaluate` asks for predictions before the fresh assessment.
- **Evidence tiers** on every pedagogy KB (bedrock → contested), the misquoted Ebbinghaus percentages removed, and a README "Evidence tiers" note with the Dunlosky et al. (2013) umbrella citation.
- **Outcome data.** `bodhi-state retention` shows your %-correct at review time by spacing gap and box; `bodhi-state export-anonymized` produces a shareable stats block with no concept names or free text; a "Share your learning data" issue template goes with it.

## [1.11.0] - 2026-06-10

The structural release. The 1.10.x dogfood sprint showed that the recurring failure class — specs read descriptively instead of imperatively, fields silently dropped, vocabulary invented — could not be closed with more prose. 1.11.0 closes it with architecture and spends the freed budget on pedagogy.

- **`scripts/bodhi-state`** (Python 3, stdlib-only): every tracking-JSON mutation now runs in code — Leitner box math, the Bloom ratchet, counters, session-type vocabulary, the prerequisite-gate verdict, the mastery formula, migration with backup and verification. Skills decide what happened; the script decides what the file looks like. Unknown learner fields are preserved; writes are atomic.
- **Stop hook** verifies tracking files before a session ends and blocks once with a repair instruction on structural breakage.
- **Test harness** (`dev/eval/`): deterministic tests run by `dev/check.sh`, plus headless LLM evals that run real skills against fixture projects and assert on resulting file state. Its very first run caught the executor silently falling back to hand-edits while claiming success — fixed before the release shipped.
- **Pedagogy additions**, all primary-sourced: pretesting (`/teach` opens with an ungraded guess), faded worked examples for novices (cognitive load theory), per-item confidence calibration in `/quiz`, successive relearning of missed concepts within the session, Bloom probes one level above a strong concept, and a recency rule on the prerequisite gate.
- **Two skills merged, nothing lost (20 → 18):** `/explain` became `/teach`'s understanding-only path; `/status` became `/progress quick` and `/progress all`.
- **Framing:** "research-backed" became "research-informed", with an explicit honesty note that outcome validation is ongoing. Hard 18 KB budget per skill.

## [1.10.1 – 1.10.13] - 2026-06-09

The dogfood sprint that followed 1.10.0: a pedagogy audit closed in code, then an end-to-end pass on real learning projects that found and fixed seven distinct bug classes. What changed for a learner:

- **`/reflect` checks retention before it records it.** You explain the concept in two sentences, then rate your confidence, then the tutor cross-checks both against today's actual quiz and teaching outcomes. Self-report alone no longer promotes a concept.
- **Partner skills are offered, not imposed.** `/teach` offers `/pair` when the work moves from talking to typing; `/teach` and `/practice` offer `/debug-together` when code breaks; `/evaluate` offers `/mentor` at a milestone. You accept or decline.
- **`/quiz` adapts mid-quiz** to where you actually are (ZPD signals), `/practice` targets Box-1 concepts from your current module and asks for a quick sketch before scaffolding, `/mentor` asks for your options before suggesting its own, and every plan declares which earlier concepts each phase revisits at greater depth.
- **The migration works on real data.** `/bodhikit:housekeep migrate` runs every missing transform in order (1.7.0 layout, then 1.10 per-concept fields), is idempotent per target, backs up first, and preserves every non-canonical field in your files.
- **The prerequisite gate fires at the right moment**, reads the evidence the system actually has (box and review history, not just Bloom), and is offer-shaped.
- **Session entries use a declared vocabulary** so downstream readers never meet an invented type.
- Lint promoted to hard-fail on every rule.

## [1.10.0] - 2026-06-09

Per-concept mastery made observable.

- **`spaced-review.json` v3:** each concept now carries `bloomLevel` (ratchet-up only), `feynmanPassed` (set once on a clear explain-back), and `consecutiveCorrectAtL4Plus`; each review records the Bloom level it tested. The canonical mastery formula — Bloom ≥ 4 and three consecutive correct at level 4+ and Box ≥ 4 and Feynman passed — lives in one KB and is computed, not fabricated, by `/progress`.
- **Prerequisite Bloom gate in `/teach`:** entering a new module surfaces any prerequisite that has not reached Apply and offers revisit, carry on, or pause.
- `/housekeep migrate` gains the v2 → v3 step.

## [1.9.0 – 1.9.2] - 2026-06-08

- **Analogy-Escalation Protocol** (`feynman-technique` KB): when you are stuck, the tutor reaches first for an analogy from a domain you know (recorded in your profile), asks once for one if none is on file, falls back to a physical analogy, and caps at two per concept before decomposing to a smaller sub-concept instead. Wired into `/teach`, `/debug-together`, and `/pair`.
- `learnerBackground` (domains and analogy history) added to the profile.
- **GUIDE.md rewritten** into a full manual: a 10-week worked example from install to capstone, a five-field card per skill, and "The Pedagogy Behind BodhiKit" — what, why, and when each methodology fires.

## [1.8.0] - 2026-06-08

- **`/teach-back`**, an optional capstone offered when `/evaluate` completes a project: write a Socratic-style post on a formerly-shaky, now-solid topic, read the masters *after* drafting, and decide for yourself whether to publish. The tutor never pronounces a post ready or not ready.

## [1.7.0 – 1.7.1] - 2026-06-05 – 2026-06-06

Progressive disclosure applied to your own learning state.

- **v2 tracking layout:** live documents hold the latest session and assessment with a summary of earlier ones; full history moves to archive directories; the plan is split per phase; `state.json` loses its narrative fields; the cross-project profile splits into profile + projects files. Routine skills read only the live slice.
- **`/housekeep`** rotates files at session boundaries; **`/housekeep migrate`** converts pre-1.7.0 projects with a backup.
- **`trajectory-analyzer` agent** reads full history for `/evaluate` in its own context.
- 1.7.1 fixed the migration on real data (it had written directories and receipts without rewriting `state.json`), added `/status all` with health flags, and added `/learn`'s cross-project reconciliation so a new topic is checked against existing projects before a fresh assessment.

## [1.6.0] - 2026-06-05

- **`/forget`** — demote a concept back to Box 1 when you feel it has slipped; `/reflect` offers it on low confidence.
- **Single sources of truth:** the `state-schema` KB for tracking-file shapes and project discovery, the `spaced-repetition` KB for Leitner intervals, the `teaching-personality` KB for voice. Skills reference, never restate.
- Configurable project discovery (`~/.bodhikit/config.json`, per-repo override); `assessment-history.json` for Bloom-over-time; cross-project profile feedback loops; the `--invoked-from=` chaining convention; `dev/check.sh` authoring-contract lint.

## [1.5.0] - 2026-03-16

- Teaching personality grounded in the four root teachers' actual teaching: Buddha's *upaya* and "test through experience", Ambedkar's "educate, agitate, organize" and education as empowerment, Oogway's patience, Yoda's directness. Context cost cut: personality KB 197 → 67 lines, skills trimmed ~20%, per-phase KB loading.

## [1.4.0] - 2026-03-16

- **`/mentor`** (GROW model + Kram's mentoring functions), **`/pair`** (strong-style, ping-pong TDD, navigator), **`/debug-together`** (Zeller's TRAFFIC method, wolf fence).
- Cross-project learner profile (`.bodhi-profile.json`).
- The monolithic methodology KB split into 13 focused KBs for progressive disclosure. CONTRIBUTING.md added.

## [1.2.0] - 2026-03-15

- **`/teach`** (explain, demonstrate, practice, verify), **`/reflect`** (end-of-session metacognition), **`/status`** (3-line check-in). `/continue` now chains check-in → teach → reflect for a one-command session.
- Example project in `docs/example-project/`; agent fallbacks in every agent-using skill.

## [1.1.0] - 2026-03-14

- Agent usage made mandatory in skills; respectful full names for the four teachers; two-step marketplace install instructions; research references for every methodology in the README.

## [1.0.0] - 2026-03-14

- Initial release: 11 skills (learn, continue, assess, review, quiz, plan, progress, resources, explain, practice, evaluate), 3 agents (skill-assessor, code-reviewer, resource-finder), 3 knowledge bases, the `learning-project` rule, README, GUIDE, MIT license.
