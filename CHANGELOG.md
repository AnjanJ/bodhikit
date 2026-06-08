# Changelog

All notable changes to BodhiKit will be documented in this file.

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
