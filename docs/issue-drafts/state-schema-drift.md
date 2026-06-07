# Issue draft — `state.json` shape drifts from canonical schema

This is the source-of-truth body for the GitHub issue. The published issue points back here for the full diagnosis.

---

## Title

`state.json` shape in production drifts from the canonical `state-schema` KB

## Labels

`bug`, `state-schema`, `housekeep`

## Body

### Summary

BodhiKit skills write `state.json` in shapes that diverge from the canonical schema documented in `knowledge/state-schema/SKILL.md`. Across four real `version: 2` projects in my own `learnWithBodhi/` directory — all created and maintained by current BodhiKit skills inside Claude Code — every single one drifts from the documented schema, in three distinct patterns.

The drift has been invisible until now because the skills reading these files tolerate whatever fields exist. A strict-typed external runtime (bodhi-cli, a parallel project that reads the same `skills/` / `agents/` / `knowledge/` markdown against any model provider) surfaced it. The cause is BodhiKit-internal: different skills, or different versions of the same skills, wrote different shapes over time.

### What the canonical schema says

`knowledge/state-schema/SKILL.md` lines 128–149 document `state.json` as:

```json
{
  "version": 2,
  "projectName": "string",
  "topic": "string",
  "createdAt": "ISO-8601",
  "lastSessionAt": "ISO-8601",
  "totalSessions": 0,
  "sessionDates": ["YYYY-MM-DD"],
  "currentStreak": 0,
  "currentPhase": "string",
  "currentModule": "string",
  "currentModuleIndex": 0,
  "lastActivity": "string",
  "initialBloomLevel": { "<sub-topic>": 0 },
  "currentBloomLevel": { "<sub-topic>": 0 },
  "overallCompletion": 0
}
```

In particular:

- `totalSessions` / `sessionDates` / `currentStreak` are **top-level** fields.
- Bloom tracking uses `currentBloomLevel` / `initialBloomLevel` (**singular**).
- No `currentPhaseName`, no `currentModuleName`, no `sessions` object, no `session` field.

### What real projects actually contain

Four projects, all `version: 2`, every one drifts differently:

| Project | Drift pattern |
|---|---|
| `system-design` | `totalSessions` / `sessionDates` / `currentStreak` nested under a `sessions` object. Has extra fields not in the canonical schema (`goal`, `standalone`, `targetDate`, `pace`, `previousModule`, etc.). |
| `rails-react-scaling` | Same nested `sessions` object. Uses `bloomLevels` and `initialBloomLevel` (where the schema says `currentBloomLevel` singular). No `currentPhaseName`. |
| `ai-elixir-architect` | No `sessions` object at all. Uses `lastSessionAt` + a singular `session` field. Bloom tracking is `currentBloomLevels` / `initialBloomLevels` (**plural**). |
| `senior-rails-growth` | Same shape as `ai-elixir-architect`. Also carries non-canonical `sourceBrief`. |

Drift correlation with `createdAt` date — i.e. whether successive BodhiKit versions wrote different shapes — has not yet been checked. That's the first thing to find out: is this a version-over-time issue (`/learn` evolved its `state.json` shape across releases) or a same-version skill-divergence issue (different skills currently write different fields)?

### Why this matters

1. **"Schema as documentation" is weaker than "schema as validator."** The `state-schema` KB is the documented single source of truth, but it describes the schema rather than enforcing it. The actual schema is whatever the skill that created the project happened to write at the time, plus whatever any later skill mutated.
2. **`dev/check.sh` doesn't catch this.** The lint validates content files (skills, agents, KBs reference `state-schema` and don't redeclare shapes inline) but doesn't validate runtime state in user projects. A skill can reference the KB *and* still write a non-conforming shape.
3. **The authoring contract leaks.** `CLAUDE.md` says "Every file that touches `.bodhi/state.json` ... references the `state-schema` KB and does NOT redeclare shapes." Skills are following the letter of that (they reference the KB) but not the spirit (the shapes they write don't match what the KB documents). The contract assumes a level of human-author discipline that hasn't held in practice.
4. **Multi-runtime risk.** A second runtime reading `.bodhi/` files (bodhi-cli today, an eventual web app or IDE plugin tomorrow) has to choose between (a) tolerating drift forever or (b) picking one shape and breaking projects that don't match. Neither is great long term, and the existence of multiple runtimes increases the cost of leaving this unresolved.

### Possible resolutions

**A. Schema follows reality.** Update `knowledge/state-schema/SKILL.md` to document what real projects actually contain. The drift patterns become "valid alternative shapes." Lowest disruption to existing projects; concedes that the canonical schema isn't really canonical and codifies the fragmentation.

**B. Reality follows schema.** Extend `/housekeep migrate` (or add a v2.x→v2.normalized step) so real projects are normalized to the documented shape. Possibly add a v2-shape lint to `dev/check.sh` or as a health flag in `/status all`. Highest fidelity; every existing `.bodhi/state.json` gets rewritten; needs a non-destructive migration story (similar to the existing v1→v2 backup pattern at `.pre-1.7.0-backup/`).

**C. Add a `state-validator` lint, fix forward.** Define the canonical shape strictly in the KB, add a runtime validator (in `dev/`, or as a helper KBs reference), have skills run it on read/write, and accept that older projects will fail validation until migrated. Most defensible long-term; most upfront work. Pairs naturally with B (B normalizes, C prevents re-drift).

The decision should be made deliberately rather than allowed to drift further. The longer the schema stays "documented but unvalidated," the more shapes accumulate in the wild.

### Reproduction

In any project with a `.bodhi/state.json` on `version: 2`:

```sh
jq 'keys' learnWithBodhi/<project>/.bodhi/state.json
```

Compare against the canonical key list in `knowledge/state-schema/SKILL.md`.

### Related

- bodhi-cli `src/state/StateStore.ts` defines a `DriftFlag` enum (`sessions-nested`, `bloom-levels-plural`, `session-singular`, `phase-name-missing`, `no-session-tracking`, `v1-fields-present`) — useful as a starting taxonomy if BodhiKit chooses resolution B or C.
- bodhi-cli `docs/SPIKE-FINDINGS.md` has the full diagnosis trail from when this surfaced.

### Scope

This is a BodhiKit-internal issue. bodhi-cli surfaced it but the cause and fix live entirely in this repo. No coordination with bodhi-cli is required to resolve it; bodhi-cli's `Option C` accommodation (tolerant reader + drift flags) is a defensive measure that stays useful regardless of how BodhiKit resolves the underlying shape question.

---

**Surfaced via:** bodhi-cli spike, 2026-06-07.
