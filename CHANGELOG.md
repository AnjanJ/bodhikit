# Changelog

All notable changes to BodhiKit will be documented in this file.

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
