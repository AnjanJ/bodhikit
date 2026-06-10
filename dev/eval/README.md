# dev/eval — BodhiKit's two-layer test harness

The 1.10.x dogfood arc proved there are two distinct failure surfaces, so
there are two distinct test layers:

## Layer 1: deterministic (free, run on every change)

```
python3 dev/eval/test_bodhi_state.py
```

Unit tests for `scripts/bodhi-state` — Leitner math, the bloomLevel ratchet,
counter rules, sessionHistory vocabulary enforcement, unknown-field
preservation, migration idempotency + backup, gate verdicts (including the
1.11.0 recency rule), mastery formula, calibration. `dev/check.sh` runs this
suite automatically.

## Layer 2: LLM evals (costs tokens, run before tagging)

```
dev/eval/run-llm-evals.sh           # all scenarios
dev/eval/run-llm-evals.sh migrate   # one scenario
```

Copies `fixtures/v2-project/` (a realistic mid-journey learning project with
v2 tracking files and non-canonical learner annotations) into a temp dir,
runs a skill headlessly via `claude -p --plugin-dir`, then asserts on the
resulting **file state** with `assert_scenario.py`. This catches the
executor-discipline regression class (writes described but not performed,
fields silently dropped, invented vocabulary) that grep-based lint cannot
see by design — the automated successor to the manual dogfood passes
documented in the 1.10.7–1.10.13 CHANGELOG entries.

Scenarios: `migrate`, `forget`, `quiz` (simulated learner). Interactive
teaching skills (`/teach`, `/pair`, `/continue`) still warrant a manual
dogfood pass on real learning data when their write paths change.

## When to add a scenario

Any time a new bug class is found in the wild: reproduce it as a fixture +
assertion first, then fix. The fixture should carry non-canonical fields —
preserving learner annotations is the contract most worth guarding.
