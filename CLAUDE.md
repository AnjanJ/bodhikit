# CLAUDE.md — Dev notes for working on bodhikit

This is a Claude Code plugin. No build, no runtime. Edits are markdown + JSON. End users install via `/plugin marketplace add <codeberg-url>` then `/plugin install`.

Claude Code only loads `skills/`, `agents/`, `knowledge/`, `rules/`, and the `.claude-plugin/` manifests from an installed plugin. Root-level files (this CLAUDE.md, README, CHANGELOG, `dev/`) are inert at install time. Safe to commit anything here; nothing pollutes end-user context unless it sits in one of the loaded directories.

## Authoring contract (must hold for every PR)

- Every `skills/*/SKILL.md` and `agents/*.md` references `teaching-personality` KB for voice. Voice rules are NOT restated inline.
- Every file that touches `.bodhi/state.json`, `spaced-review.json`, `progress.md`, or `.bodhi-profile.json` references the `state-schema` KB and does NOT redeclare shapes.
- Every file that touches Leitner boxes references the `spaced-repetition` KB and does NOT redeclare box→interval intervals or update rules.
- Skills that use an agent include the literal phrase "You MUST use the Agent tool" and a `**Fallback:**` paragraph for agent failure.
- KBs are loaded per phase, not all upfront (progressive disclosure).
- New methodologies need a research citation in the KB and a README "Science" section update.

Before committing, run `dev/check.sh`.

## Where things live

- `skills/<name>/SKILL.md` — user-invocable commands (frontmatter `user-invocable: true`).
- `agents/<name>.md` — sub-agents (Sonnet/Haiku, read-only: `disallowedTools: Edit, Write, Agent`).
- `knowledge/<kb>/SKILL.md` — KBs (frontmatter `user-invocable: false`).
- `rules/<name>.md` — path-scoped rules (`paths:` glob array).
- `.claude-plugin/plugin.json` — install manifest. Update `version` here on release.
- `.claude-plugin/marketplace.json` — marketplace manifest. Keep `version` and counts in sync with `plugin.json` and README.
- `CHANGELOG.md` — append entries on release. Use absolute dates.
- `dev/` — dev-only scripts (lint). Never referenced by skills.

## Runtime artifacts (created in user projects, never in this repo)

- `learningWithBodhi/<project>/.bodhi/{state.json,plan.md,progress.md,spaced-review.json,assessment.md,resources.md}`
- `learningWithBodhi/.bodhi-profile.json`
- `~/.bodhikit/config.json` (optional, discovery overrides)

Schemas are pinned in `knowledge/state-schema/SKILL.md`. If a new field is needed, update that KB first, then the skills that touch it.

## Release checklist

1. Bump `version` in `.claude-plugin/plugin.json` AND `.claude-plugin/marketplace.json` (both places).
2. Update CHANGELOG.md with the new version, dated.
3. Update skill/agent/KB counts in README and `marketplace.json` if they changed.
4. Run `dev/check.sh` — should pass clean.
5. Tag and push to Codeberg (source of truth). GitHub mirror auto-updates via Codeberg push mirror.

## Don't do

- Don't add fields to tracking files without updating `state-schema` KB first.
- Don't restate Leitner intervals or voice rules in a skill. Reference the KB.
- Don't hardcode search paths beyond what `state-schema` defines.
- Don't commit `.claude/` (user-local Claude Code state — gitignored).
- Don't add backwards-compat shims for unused fields. Edit the schema, update readers.
