# /teach — Prerequisite Bloom Gate

Loaded on demand by `/teach` Phase 1 at a module-start boundary. The verdict is computed by `bodhi-state gate-check`; this file says how to act on it. `--tested-bloom` values written here ratchet and feed the gate (`blooms-taxonomy` KB).

The gate's trigger detection and per-prerequisite verdicts are computed by `"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project <project> gate-check` — the canonical logic (trigger model, recency rule, legacy fallthrough, apply-equivalent fallthrough) is documented in the `state-ops` KB's *Prerequisite gate* section. Do not re-derive it in prose.

Skip the gate entirely (do not even run the check) when: the caller passed a specific concept via `--invoked-from=`, or the learner passed an explicit topic in `$ARGUMENTS` — an explicit request overrides the gate.

Otherwise, run:

```
"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project <project> gate-check --prereqs "<declared list>"
```

passing `--prereqs` from the prior module's `**Prerequisites for next module:**` line in `plan/phase-{N}.md` when it exists (omit the flag when it does not; the script falls back to the tracked `previousModule`, or declines to gate when neither exists — it never guesses).

Act on the verdict JSON:

- **`fires: false`** — continuation session or first-ever project. Proceed to Phase 2.
- **`verdict: "clear"`** — proceed to Phase 2, no ceremony.
- **`staleReconfirm` non-empty** — for each stale concept, ask ONE quick reconfirm question (Bloom 3, applied) before proceeding. Clean answer → run `"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project <project> record-review --concept "<c>" --result correct --tested-bloom 3 --source teach` and continue. Missed → record it too (`--result incorrect --tested-bloom 3 --source teach` — a demonstrated forgetting event belongs in the schedule, per the `spaced-repetition` KB), then treat as a gap below.
- **`gaps` non-empty** — surface as an **offer, never an auto-block**. The learner decides:

  > "Before we move into `<new module>`, [one earlier concept / a few earlier concepts] might still need more time to root: `<concept>` — [what they can do with it today, and what the new module will ask of it]... Revisit one first, carry on into `<new module>`, or end here?"

  Name the gap in outcome terms, not as a level. The learner is deciding whether to press on; "you can explain what it does, but the next module asks you to debug it" is a decision they can act on, where "(Bloom 2)" is a grade delivered at a moment of friction.

  If the verdict JSON reports `prerequisiteSource: "prior-module"` (no declared list), add: "I am reading the prior module's concept list because the plan does not declare specific prerequisites — say if any of these do not apply and I will skip them."

  Learner choices: **revisit** (re-enter Phase 2 on that prerequisite first), **carry on** (record `**Prerequisite gate carry-on:** <concepts>` in this session's `progress.md` entry so the next evaluation sees the conscious choice), **skip an irrelevant item** (per-session dismissal — no state change), or **end the session**.
