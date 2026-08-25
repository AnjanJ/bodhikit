# CLAUDE.md — Dev notes for working on bodhikit

This is a Claude Code plugin. Edits are markdown + JSON + one Python script. End users install via `/plugin marketplace add <github-url>` then `/plugin install`.

Claude Code loads `skills/`, `agents/`, `hooks/`, and the `.claude-plugin/` manifests from an installed plugin — and **nothing else**: a `knowledge/` tree is never registered and a plugin `rules/` directory is never loaded (both verified with headless probes in 1.18.0; from 1.0 to 1.17 every "Reference the `X` KB" pointed at a file the runtime could not load). Since 1.18.0 the 20 knowledge bases live under `skills/<kb>/SKILL.md` with `user-invocable: false` — registered, hidden from the `/` menu, loaded on demand through the Skill tool — and `rules/learning-project.md` is delivered by the SessionStart hook (`scripts/bodhi-session-context.py`). `scripts/` ships with the install and is executed via Bash (it never enters context). Root-level files (this CLAUDE.md, README, CHANGELOG, `dev/`) are inert at install time.

## The deterministic state layer (1.11.0)

`scripts/bodhi-state` performs every tracking-JSON mutation — Leitner math, the Bloom ratchet, sessionHistory vocabulary, the gate verdict, mastery formula, migration. Since 1.14.0 it also owns the read-side branch detection that skills used to re-derive from prose: `session-brief` (pretest-vs-retrieval, reteach duty, `crossedBloom3` in `record-review` output) and `snapshot` (the whole `/progress` number surface). Skills carry the pedagogical judgment and one-line script invocations, never hand-edited JSON or hand-derived state predicates. Consequences for authoring:

- A skill that writes tracking state MUST invoke `bodhi-state` and carry a `**Fallback:**` paragraph for script-unavailable. Lint enforces both.
- Do NOT reintroduce the retired 1.10.12 CHECKPOINT-before/after-writes prose — its reappearance means someone is hand-writing JSON again. Lint fails on it.
- Schema changes go: `state-schema` KB first → `scripts/bodhi-state` + `dev/eval/test_bodhi_state.py` in the same PR → then the skills (and `state-ops` if the operational surface changed). The lint pins the Leitner table (spaced-repetition KB) and the session-type vocabulary (state-ops KB) between KB and script.
- New executor-discipline bug found in the wild? Reproduce it as a `dev/eval/` fixture + assertion FIRST, then fix. Do not fix it with louder markdown.

## Sub-skill chaining (context efficiency)

When one skill auto-invokes another, it MUST pass `--invoked-from=<caller>` in the arguments. Example: `/continue` invokes `/teach` as `/bodhikit:teach --invoked-from=continue <topic>`.

Chainable skills MUST check `$ARGUMENTS` for `--invoked-from=` and, if present:
- Skip re-loading the `teaching-personality` KB (the caller already loaded it).
- Skip re-loading the `learning-project` rule (already active for the session).
- Skip discovery (the caller already resolved the project).

Currently chainable: `/teach`, `/practice`, `/reflect`, `/progress`, `/quiz`, `/forget`, `/pair`, `/debug-together`, `/mentor`. The caller passes any positional argument AFTER the flag.

Chain shape note (1.10.2): `/pair`, `/debug-together`, and `/mentor` are **offered** (opt-in), not auto-invoked, by their callers — `/teach` Phase 3 offers `/pair`; `/practice` Phase 3 and `/teach` Phase 4 offer `/debug-together`; `/evaluate` Closing offers `/mentor` at project completion or major milestone. The chain guard fires when the learner accepts the offer and the caller passes `--invoked-from=`, not unconditionally on every invocation. The Capstone offer pattern from 1.8.0 is the template.

## Authoring contract (must hold for every PR)

- Every `skills/*/SKILL.md` and `agents/*.md` references `teaching-personality` KB for voice. Voice rules are NOT restated inline.
- Every file that touches `.bodhi/state.json`, `spaced-review.json`, `progress.md`, or `.bodhi-profile.json` references the `state-ops` KB (the routine operational surface: write path, discovery, vocabulary, gate/mastery) and does NOT redeclare shapes. The field-level `state-schema` KB is loaded ONLY by the manual carve-outs (`/learn` scaffolding + `overallBloomLevels`, `/assess`/`/mentor`/`/evaluate` Bloom-map and career-field updates, `/housekeep`) and the script-unavailable fallback — the 1.13.0 split exists so routine fires stop paying ~24 KB for shapes they cannot legally hand-edit anyway. Since 1.16.0 the `.bodhi-profile.projects.json` list is script-owned (`profile-add/update/complete-project`, `profile-update-patterns`) — it is no longer a carve-out.
- Every file that touches Leitner boxes references the `spaced-repetition` KB and does NOT redeclare box→interval intervals or update rules.
- Learner-facing text never quotes a raw Bloom number or Leitner box, and does not lead with the rung's name. Levels render as the outcome clause alone (`you can apply it in working code with some guidance`) from the `blooms-taxonomy` KB *Learner-Facing Rendering* table; the label joins it only at a rung-crossing (`record-review` emits `crossedLevel`) and in the `/progress` legend (`bloomScale`). `bodhi-state` emits `bloomLabel`/`bloomOutcome` next to every `bloomLevel` so skills render rather than translate. Module rollups use the tier words (*Solid / Working / Introduced*). The three sanctioned exceptions for a bare number are listed in that KB.
- `dev/check.sh` sections A–D admit only **structural** or **conditional** rules; section E holds the remaining **phrase pins**, each naming the eval that retires it (policy in the header). A new grep-for-a-sentence rule does not go in; behaviour goes in `dev/eval/`. Rule numbers are stable identifiers and are not contiguous.
- JSON mutations route through `bodhi-state` (see above); markdown live docs are written directly (new entry on top, existing content verbatim).
- Skills that use an agent include the literal phrase "You MUST use the Agent tool" and a `**Fallback:**` paragraph for agent failure.
- KBs are loaded per phase, not all upfront (progressive disclosure).
- Every SKILL.md stays under the 18 KB lint budget — prose that wants to grow past it belongs in a phase-loaded KB or in `bodhi-state`.
- New methodologies need a research citation in the KB and a README "Science" section update.

Before committing, run `dev/check.sh` (which also runs the deterministic test suite). Before tagging, additionally run `dev/eval/run-llm-evals.sh` (costs tokens; asserts skills against fixture file state).

## Feature freeze (1.13.0)

The plugin's audience is currently one real learner. No new skills, KBs, taxonomies, session types, or schema fields unless (a) a second real user files an issue asking for it, or (b) the maintainer personally hits the gap during a real learning session — not while developing the plugin. Bug fixes, and refactors that reduce per-fire context cost, are exempt. When in doubt: the next feature the plugin needs is a user.

## Where things live

- `skills/<name>/SKILL.md` — user-invocable commands (frontmatter `user-invocable: true`). Every one opens with the **Knowledge bases are skills** sentence, which is how a `` `name` KB `` reference becomes a `Skill(bodhikit:name)` call; lint requires it.
- `agents/<name>.md` — sub-agents (Sonnet/Haiku, read-only: `disallowedTools: Edit, Write, Agent`).
- `skills/<kb>/SKILL.md` — KBs (frontmatter `user-invocable: false`; lint tells the two kinds apart by that line). `state-ops` is the routine operational surface; `state-schema` is the field-level reference behind it (1.13.0 split). The per-skill read contract lives in `dev/read-defaults.md` (dev-only, moved out of knowledge/ in 1.13.0).
- `rules/<name>.md` — the learning-project rule. Plugins cannot ship path-scoped rules, so the SessionStart hook injects this file's body when the session starts inside a learning project.
- `scripts/bodhi-state` — deterministic state writer (Python 3, stdlib-only). `scripts/bodhi-stop-hook.py` — Stop-hook safety net.
- `hooks/hooks.json` — plugin hook manifest (SessionStart → learning-project rule; Stop → schema verify).
- `.claude-plugin/plugin.json` — install manifest. Update `version` here on release.
- `.claude-plugin/marketplace.json` — marketplace manifest. Keep `version` and counts in sync with `plugin.json` and README.
- `CHANGELOG.md` — append entries on release. Use absolute dates.
- `dev/` — dev-only scripts (lint, `outcomes.py`) and `dev/eval/` (deterministic tests + LLM evals + fixtures). Never referenced by skills. `dev/changelog-journal.md` is the patch-by-patch development journal; `CHANGELOG.md` is the reader-facing summary.
- `docs/outcomes.md` — the maintainer's own anonymized learning data, regenerated with `python3 dev/outcomes.py <project-dirs…> > docs/outcomes.md`. `MIGRATION.md` — upgrade notes, out of the README's critical path.
- `analysis/` — gitignored, local-only review notes (empirical/adversarial/fidelity passes, the honest review, follow-ups). Commit messages cite it; it is not part of the plugin.

## Runtime artifacts (created in user projects, never in this repo)

- `learningWithBodhi/<project>/.bodhi/{state.json,plan.md,progress.md,spaced-review.json,assessment.md,resources.md}`
- `learningWithBodhi/.bodhi-profile.json`
- `~/.bodhikit/config.json` (optional, discovery overrides)

Schemas are pinned in `skills/state-schema/SKILL.md`. If a new field is needed, update that KB first, then the skills that touch it.

## Release checklist

1. Bump `version` in `.claude-plugin/plugin.json` AND `.claude-plugin/marketplace.json` (both places).
2. Update CHANGELOG.md with the new version, dated.
3. Update skill/agent/KB counts in README and `marketplace.json` if they changed.
4. Run `dev/check.sh` — should pass clean (includes the bodhi-state deterministic test suite).
5. Run `dev/eval/run-llm-evals.sh` — file-state assertions against a live model (costs tokens; this is the automated dogfood). Schema-touching releases additionally warrant a manual dogfood pass on real learning data for the interactive skills.
   - **If the release touched a grading ladder** (`feynman-technique`, `blooms-taxonomy`, or a `record-review` write site), a single pass is not sufficient — sweep the grading group with `BODHI_EVAL_RUNS=N` and read the recorded *levels*, not just the rate. These boundaries have measured 3/3 and 1/3 on the same tree hours apart.
   - **A grading rule that bounds a value needs a scenario on each side of the bound, read together.** A perfect score on the scenario a fix targets cannot distinguish "now correct" from "now constant" — a rule that pins the level passes it identically. `grade-apply-band` (capped at the apply rung) and `grade-genuine` (reaches the top rung) are that pair; in 1.14.x a floor rule scored 8/8 on the first while silently pulling the second from Bloom 5 down to 3.
6. Tag and push to GitHub (`origin`) — the source of truth. The Codeberg repo is archived (the push-mirror flow that made Codeberg canonical no longer applies).

## Glossary (internal vocabulary you will meet in commits and the journal)

- **Executor discipline** — whether the model actually *performs* the file writes a skill describes (vs. narrating them, inventing vocabulary, dropping fields). The 1.10.x dogfood passes showed prose cannot guarantee it; `bodhi-state` + file-state evals can. Hence "don't fix executor-discipline bugs with louder markdown."
- **Bloom ratchet** — `bloomLevel` only rises (`max(current, tested)`, and only on a `correct` result). Forgetting is carried by the Leitner box and the streak, never by lowering the level.
- **Prerequisite gate / verdicts** — `/teach`'s module-boundary check, computed by `gate-check`. Verdicts: `satisfied`, `stale-reconfirm` (reason `stale` or `single-evidence`), `no-opinion`, `apply-equivalent`, `gap`. Defined in the `state-ops` KB.
- **Legacy fallthrough** — a `bloomLevel: 0` concept has never been classified by a v3 writer: gates allow it, `/progress` shows `—` not 0%. **Apply-equivalent fallthrough** — a sub-3 concept with Box ≥ 3 and two straight corrects passes the gate at read time without touching the level.
- **Carve-out** — the few places a skill may still hand-edit JSON (plan scaffolding, the Bloom maps in `/assess`/`/evaluate`/`/mentor`, `/housekeep`); they load `state-schema`, everything else loads only `state-ops`.
- **Evidence tier** — a per-KB label for how strong the research behind a technique is (`bedrock`, `strong-qualitative`, `organizing framework`, `contested`). Not a per-concept field.
- **Teaching starvation** — `/continue` quizzing seeded concepts that were never taught; fixed in 1.14.2 via `due --never-taught` awareness.
- **Finding IDs** — `H*/M*/L*` are HIGH/MEDIUM/LOW-severity findings from `dev/gaps_of_pedagogy.md` (1.10.0 audit); `A*` adversarial, `D*` sprint-review corrections, `F-*` fidelity-audit and `P*` empirical findings from the local `analysis/` passes; `honest-review #N` indexes `analysis/bodhikit-honest-review.md`. Kept in the journal for traceability; do not introduce new ones into shipped files (lint comments, skills, KBs).

## Don't do

- Don't add fields to tracking files without updating `state-schema` KB AND `scripts/bodhi-state` first.
- Don't restate Leitner intervals or voice rules in a skill. Reference the KB.
- Don't hand-edit tracking JSON in a skill, and don't fix executor-discipline bugs with louder prose — fix them in `bodhi-state` with a test.
- Don't hardcode search paths beyond what `state-schema` defines.
- Don't commit `.claude/` (user-local Claude Code state — gitignored).
- Don't add backwards-compat shims for unused fields. Edit the schema, update readers.
