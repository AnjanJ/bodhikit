# Changelog

All notable changes to BodhiKit will be documented in this file.

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
