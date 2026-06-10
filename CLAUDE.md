# CLAUDE.md — Dev notes for working on bodhikit

This is a Claude Code plugin. Edits are markdown + JSON + one Python script. End users install via `/plugin marketplace add <codeberg-url>` then `/plugin install`.

Claude Code loads `skills/`, `agents/`, `knowledge/`, `rules/`, `hooks/`, and the `.claude-plugin/` manifests from an installed plugin; `scripts/` ships with the install and is executed via Bash (it never enters context). Root-level files (this CLAUDE.md, README, CHANGELOG, `dev/`) are inert at install time. Safe to commit anything here; nothing pollutes end-user context unless it sits in one of the loaded directories.

## The deterministic state layer (1.11.0)

`scripts/bodhi-state` performs every tracking-JSON mutation — Leitner math, the Bloom ratchet, sessionHistory vocabulary, the gate verdict, mastery formula, migration. Skills carry the pedagogical judgment and one-line script invocations, never hand-edited JSON. Consequences for authoring:

- A skill that writes tracking state MUST invoke `bodhi-state` and carry a `**Fallback:**` paragraph for script-unavailable. Lint enforces both.
- Do NOT reintroduce the retired 1.10.12 CHECKPOINT-before/after-writes prose — its reappearance means someone is hand-writing JSON again. Lint fails on it.
- Schema changes go: `state-schema` KB first → `scripts/bodhi-state` + `dev/eval/test_bodhi_state.py` in the same PR → then the skills. The lint pins the Leitner table and the session-type vocabulary between KB and script.
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
- Every file that touches `.bodhi/state.json`, `spaced-review.json`, `progress.md`, or `.bodhi-profile.json` references the `state-schema` KB and does NOT redeclare shapes.
- Every file that touches Leitner boxes references the `spaced-repetition` KB and does NOT redeclare box→interval intervals or update rules.
- JSON mutations route through `bodhi-state` (see above); markdown live docs are written directly (new entry on top, existing content verbatim).
- Skills that use an agent include the literal phrase "You MUST use the Agent tool" and a `**Fallback:**` paragraph for agent failure.
- KBs are loaded per phase, not all upfront (progressive disclosure).
- Every SKILL.md stays under the 18 KB lint budget — prose that wants to grow past it belongs in a phase-loaded KB or in `bodhi-state`.
- New methodologies need a research citation in the KB and a README "Science" section update.

Before committing, run `dev/check.sh` (which also runs the deterministic test suite). Before tagging, additionally run `dev/eval/run-llm-evals.sh` (costs tokens; asserts skills against fixture file state).

## Where things live

- `skills/<name>/SKILL.md` — user-invocable commands (frontmatter `user-invocable: true`).
- `agents/<name>.md` — sub-agents (Sonnet/Haiku, read-only: `disallowedTools: Edit, Write, Agent`).
- `knowledge/<kb>/SKILL.md` — KBs (frontmatter `user-invocable: false`).
- `rules/<name>.md` — path-scoped rules (`paths:` glob array).
- `scripts/bodhi-state` — deterministic state writer (Python 3, stdlib-only). `scripts/bodhi-stop-hook.py` — Stop-hook safety net.
- `hooks/hooks.json` — plugin hook manifest (Stop → schema verify).
- `.claude-plugin/plugin.json` — install manifest. Update `version` here on release.
- `.claude-plugin/marketplace.json` — marketplace manifest. Keep `version` and counts in sync with `plugin.json` and README.
- `CHANGELOG.md` — append entries on release. Use absolute dates.
- `dev/` — dev-only scripts (lint) and `dev/eval/` (deterministic tests + LLM evals + fixtures). Never referenced by skills.

## Runtime artifacts (created in user projects, never in this repo)

- `learningWithBodhi/<project>/.bodhi/{state.json,plan.md,progress.md,spaced-review.json,assessment.md,resources.md}`
- `learningWithBodhi/.bodhi-profile.json`
- `~/.bodhikit/config.json` (optional, discovery overrides)

Schemas are pinned in `knowledge/state-schema/SKILL.md`. If a new field is needed, update that KB first, then the skills that touch it.

## Release checklist

1. Bump `version` in `.claude-plugin/plugin.json` AND `.claude-plugin/marketplace.json` (both places).
2. Update CHANGELOG.md with the new version, dated.
3. Update skill/agent/KB counts in README and `marketplace.json` if they changed.
4. Run `dev/check.sh` — should pass clean (includes the bodhi-state deterministic test suite).
5. Run `dev/eval/run-llm-evals.sh` — file-state assertions against a live model (costs tokens; this is the automated dogfood). Schema-touching releases additionally warrant a manual dogfood pass on real learning data for the interactive skills.
6. Tag and push to Codeberg (source of truth). GitHub mirror auto-updates via Codeberg push mirror.

## Don't do

- Don't add fields to tracking files without updating `state-schema` KB AND `scripts/bodhi-state` first.
- Don't restate Leitner intervals or voice rules in a skill. Reference the KB.
- Don't hand-edit tracking JSON in a skill, and don't fix executor-discipline bugs with louder prose — fix them in `bodhi-state` with a test.
- Don't hardcode search paths beyond what `state-schema` defines.
- Don't commit `.claude/` (user-local Claude Code state — gitignored).
- Don't add backwards-compat shims for unused fields. Edit the schema, update readers.
