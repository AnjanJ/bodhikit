---
description: "Per-skill read defaults for BodhiKit tracking files — guidance, not gates. Loaded by /housekeep, the context audit, and the authoring lint."
user-invocable: false
---

# Read Defaults — What Each Skill Loads, and When It Reaches for Archive

This KB is the contract the context audit and authoring lint enforce. Skills themselves do not need to load this KB at runtime — they each know what they read. This KB exists so that one place defines the expected default-read shape across the plugin, and the audit can compare reality against the contract.

See also: `state-schema` KB (file shapes and discovery), `state-migration` KB (one-shot conversion of pre-1.7.0 files).

## Guiding Principle: Nothing Gatekept

The learner's accumulated work is theirs. Every skill MAY read every file when the learner's situation justifies it. This KB documents only the **default** read for each skill — what loads on routine invocations. The audit and lint flag *unconditional* archive reads as accidental waste, but a deliberate, situational read is always allowed and never penalized.

**Transparency rule.** When a skill pulls archive content beyond its default, it MUST announce in its turn output what was loaded and why. The learner never has hidden context pulled on their behalf.

## Default Reads Per Skill

| Skill | Reads by default | Reaches into archive when |
|---|---|---|
| `/progress quick` / `all` | `state.json` (per project; `all` also reads `.bodhi-profile.projects.json`) | never |
| `/continue` | `state.json`, `progress.md` (live + summary block), `plan/README.md`, `plan/phase-{currentPhase}.md`, `spaced-review.json.concepts` | learner has been gone >30 days (then last few `progress/archive/` entries for re-onboarding) |
| `/teach` | `state.json`, `plan/phase-{currentPhase}.md`, `progress.md` (understanding-only sessions skip the plan file) | building explicitly on a prior session the learner names |
| `/practice` | `state.json`, `plan/phase-{currentPhase}.md`, `spaced-review.json.concepts` | calibrating against a past struggle the learner references |
| `/quiz` | `spaced-review.json.concepts` (filtered to due) | never |
| `/reflect` | `state.json`, `progress.md` | rarely |
| `/forget` | `spaced-review.json` | never |
| `/progress` | `progress.md` (live + summary), `state.json` | learner asks for long-view trajectory |
| `/evaluate` | `state.json` + `plan/README.md` only in the parent skill. **Delegates the full archive load to the `trajectory-analyzer` agent**, which reads every archive + assessment + plan phase + spaced-review history in its own context. Parent stays light; structured report comes back. | fallback path (agent failure) reads everything itself |
| `/mentor` | `.bodhi-profile.json`, `.bodhi-profile.projects.json`, `state.json` for active project | learner asks about cross-track patterns or multi-month trajectory |
| `/plan` (view) | `plan/README.md` + all `plan/phase-*.md` | regenerating |
| `/assess` | `state.json`, `assessments/latest.md` | re-baselining against a prior assessment the learner names |
| `/review` | `state.json`, current code path under review | reviewing a past session's code |
| `/resources` | `state.json`, `resources.md` | never |
| `/learn` | `.bodhi-profile.json` (for context), then writes new project | reading `.bodhi-profile.projects.json` to detect overlapping projects |
| `/debug-together` | `state.json`, current code | never (scoped to current bug) |
| `/pair` | `state.json`, `plan/phase-{currentPhase}.md` | learner asks to revisit a past pairing pattern |
| `/housekeep` | all live docs + most recent archive entry per surface | implementation detail; reads to rotate |

## What the Audit Measures

For each skill, `dev/context-audit.sh` classifies each read as:

- **Unconditional** — appears in the skill body without any guarding `if` / `when` / phase header. Counts heavily in the pollution score.
- **Phase-conditional** — appears inside a phase that itself runs sometimes (e.g., a re-baselining phase). Counts moderately.
- **Branch-conditional** — appears inside an explicit `if learner asked X` / `if state shows Y` branch. Counts negligibly.

The default-read column above is what should appear **unconditionally**. Anything in the right-hand column should be **branch-conditional** — guarded by the situation that justifies it.

## What the Lint Flags

`dev/check.sh` warns (soft-warn initially; hard-fail once the punch list is clean) when:

- A skill reads `<surface>/archive/` unconditionally.
- A skill reads `plan/phase-{N}.md` for a phase other than `currentPhase` without a guarding branch.
- A skill reads a tracking file that this KB does not list for that skill, with no announcing prose nearby.

The lint never blocks a deliberate read. It catches accidental waste — defaults drifting from the contract.

## How to Update This KB

When a new skill is added, append a row. When an existing skill's default reads change, update the row in the same PR that changes the skill, and update the audit run output to reflect the new baseline.

The default-read column should stay short. If a skill needs many files by default, that is a signal the skill is doing too much — split it, or move some reads behind branches.
