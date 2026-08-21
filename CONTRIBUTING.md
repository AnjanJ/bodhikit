# Contributing to BodhiKit

Thank you for your interest. Please read the first section before opening a pull request — it will save us both time.

## Feature freeze

BodhiKit's audience is currently a very small number of real learners. Until that changes, the plugin accepts **no new skills, knowledge bases, taxonomies, session types, or schema fields** unless one of two things is true:

1. A second real user files an issue asking for it, or
2. The maintainer personally hits the gap during a real learning session — not while developing the plugin.

Bug fixes, and refactors that reduce per-fire context cost, are always welcome. When in doubt: the next feature the plugin needs is a user.

## The most valuable contribution right now

**Use it, then tell us how it went.** One honest account of one real session is worth more than any pull request. The [session feedback template](.github/ISSUE_TEMPLATE/feedback.md) takes five minutes; the [bug report template](.github/ISSUE_TEMPLATE/bug-report.md) is for when something broke or graded you wrong; the [learning data template](.github/ISSUE_TEMPLATE/learning-data-report.md) takes one command (`bodhi-state export-anonymized`) and shares numbers only — no concept names, no free text.

## If you are changing code or prose

`CLAUDE.md` at the repo root is the authoring contract. Read it first; the short version:

- **Voice:** every skill and agent references the `teaching-personality` KB for voice. Do not restate voice rules inline — the lint fails on it.
- **State:** every JSON mutation to tracking files goes through `scripts/bodhi-state`, with a test in `dev/eval/test_bodhi_state.py`. Skills carry pedagogical judgment and one-line script invocations, never hand-edited JSON. Schema changes go `state-schema` KB → script + test → skills, in that order.
- **Single sources of truth:** Leitner intervals live in the `spaced-repetition` KB; tracking-file shapes in `state-schema`; the routine operational surface in `state-ops`. Reference, never redeclare.
- **Agents:** skills that use one say "You MUST use the Agent tool" and carry a `**Fallback:**` paragraph. Agents are read-only.
- **Chaining:** a skill that auto-invokes another passes `--invoked-from=<caller>`.
- **Budget:** every `SKILL.md` stays under 18 KB. Knowledge bases load per phase, not up front.
- **Bugs in executor discipline** (the model skipped a write, invented a field) are fixed in `bodhi-state` with a reproducing fixture first — never with louder markdown.

## Before you submit

- `dev/check.sh` must pass clean. It runs the authoring-contract lint and the deterministic test suite.
- `dev/eval/run-llm-evals.sh` must pass before a release is tagged (it costs tokens; maintainers run it). If your change touches a grading ladder, see the release checklist in `CLAUDE.md` for the two-sided sweep it requires.
- Test locally with `claude --plugin-dir <path-to-checkout>`.
- New methodologies (if they clear the freeze) need a primary-source citation in the KB and a README "Science" entry.

## Submitting

1. Fork on GitHub and branch.
2. Keep the PR to one change. Describe what it fixes and how you verified it.
3. Update `CHANGELOG.md` under `[Unreleased]` if the change is user-visible.

## Code of conduct

Be respectful, patient, and constructive — the same values BodhiKit teaches.
