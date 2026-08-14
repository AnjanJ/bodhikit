---
description: "Operational surface for BodhiKit tracking state — project discovery, the bodhi-state write path and subcommand table, session-type vocabulary, gate and mastery semantics. Field-level file shapes live in the state-schema KB."
user-invocable: false
---

# State Ops — The Per-Session Operational Surface

This KB is what a skill needs to *operate* on tracking state: find the project, invoke `scripts/bodhi-state`, write the markdown surfaces. Field-level file shapes live in the `state-schema` KB and are deliberately NOT loaded on routine fires — a skill that cannot see field shapes cannot hand-edit them.

Load the `state-schema` KB only when:

- performing one of the **manual carve-outs** — `/learn` project scaffolding, `/evaluate` profile writes, the `currentBloomLevel` / `initialBloomLevel` maps;
- running the **script-unavailable fallback** (see below);
- you are `/housekeep` (rotation and migration need the full shapes).

See also: `spaced-repetition` KB (box→interval mapping and update rules, implemented by `bodhi-state`), `state-lifecycle` KB (loaded by `/housekeep` only), `state-migration` KB (loaded by `/housekeep migrate` only).

## The Write Path: `scripts/bodhi-state` (canonical for ALL JSON writes)

Skills do not hand-edit tracking JSON. Every mutation of `state.json`, `spaced-review.json`, or the profile files goes through the plugin's deterministic writer:

```
"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project <project-dir> <subcommand> [options]
```

If `CLAUDE_PLUGIN_ROOT` is not set in the Bash environment, locate the script once with `find ~/.claude/plugins -type f -name bodhi-state -path "*bodhikit*" 2>/dev/null | head -1` (or the repo checkout's `scripts/bodhi-state` when running via `--plugin-dir`).

| Subcommand | Owns |
|---|---|
| `add-concept --concept N --module M [--question Q]` | New concept with canonical Box-1 defaults |
| `record-review --concept N --result correct\|incorrect\|partial --tested-bloom 0-6 [--confidence sure\|mostly\|guessing] [--module M] [--note S] [--source skill] [--retry]` | Leitner box math, nextReview dates, bloomLevel ratchet, `consecutiveCorrectAtL4Plus` rules, `reviewHistory[]` append. `--retry` = successive-relearning rep: history entry only, no box/counter/bloom movement (the original demotion stands). Output reports `crossedBloom3: true` when THIS write crossed Bloom <3 → ≥3 — the exact trigger for `bump-profile --counter totalConceptsLearned`; do not re-derive the crossing |
| `set-feynman --concept N` | `feynmanPassed = true` (set, never unset) |
| `record-session --type T [--subtype S] [--data '<json>']` | `sessionHistory[]` append, canonical-type enforcement (`type`/`subtype`/`date` in `--data` are ignored — flags only) |
| `record-assessment --trigger learn-phase2\|assess\|evaluate\|plan-regenerate --data '<entry json>'` | Append-only `assessment-history.json` entry, date-stamped |
| `forget --concepts "A, B" \| --concept N (repeatable) [--note S] [--activity S]` | Learner-initiated demote: box 1, counter reset, history + `learner-forget` session entry, `lastActivity`. Use `--concept` for names containing commas |
| `defer --concept N (repeatable) [--days D] [--note S]` | A due concept the session did not reach: `nextReview` = today + D (default 1), box/bloom/counters/`lastReviewed` untouched, history entry `{date, deferred: true, days}` with NO result — deferral is scheduling, never an outcome. Do NOT invent a `result` for an unreviewed concept |
| `normalize` | One-shot, idempotent repair of pre-1.11.0 executor drift. Backs up both files to `.bodhi/.pre-normalize-backup/` first; `verify` names this as the repair when it flags drift |
| `touch-state [--activity S] [--module M] [--module-index N] [--phase P] [--completion N]` | `state.json` session bookkeeping: dates, streak, totalSessions, module advance (records `previousModule`). The first touch of a new day also bumps the profile's `cumulativeStats.totalSessions` — no skill calls `bump-profile --counter totalSessions` |
| `bump-profile --counter <name>` | `cumulativeStats` increments in `.bodhi-profile.json` |
| `due [--limit N]` / `mastery` / `calibration` | Read-side rollups: due concepts — each tagged `neverTaught` (no review ever came from `--source teach`; a `/learn`-seeded or quiz-only concept) plus a `neverTaughtCount` rollup, so `/continue` routes never-taught-but-due concepts to `/teach` not `/quiz` (reviewing an untaught concept is not spaced repetition) — plus `unparseableDates` for schedule-broken entries (never silently skipped); canonical mastery % + `blockedOnFeynman`; retention tiers; confidence calibration |
| `retention` / `export-anonymized` | Read-side outcome analytics: retention-at-review rates by spacing gap and by `boxBefore`, and a shareable anonymized stats export (counts and rates only) |
| `session-brief --concept N` | Read-side branch detection for `/teach` (1.14.0): `firstExposure`/`pretestApplies` (pretest vs graded retrieval open), `isReteach` (targeted-reteach duty), box/bloom/Feynman position, `dueForReview`. Trust the brief over hand-reading tracking files |
| `snapshot` | Read-side single-call dashboard for `/progress` (1.14.0): position + Bloom maps (`project`), session cadence (`cadence`), due lists + box distribution + 3-tier retention rollup (`review`), per-module mastery + `blockedOnFeynman` (`mastery`), confidence calibration (`calibration`) |
| `gate-check [--module M] [--prereqs "A,B"] [--prior-module M]` | Prerequisite Bloom gate verdict (see below) |
| `migrate-spaced-review` | One-shot v1/v2 → v3 transform: backup, in-place field fill, marker, verification |
| `verify` | Schema sanity check (also run by the plugin's Stop hook and `dev/check.sh`) |

The script preserves unknown fields by mutating parsed JSON in place, writes atomically, and rejects invalid `sessionHistory` types in code. The skill's job is the pedagogical judgment (which result, which Bloom level, which confidence tag); the script's job is the file.

**Fallback (script unavailable):** only after BOTH the `${CLAUDE_PLUGIN_ROOT}` path and the `find ~/.claude/plugins` lookup come up empty, say so plainly, then load the `state-schema` KB and perform the minimal write by hand per its *Fallback discipline* — read → mutate the parsed JSON in place → write → verify, preserving every unknown field.

**Markdown surfaces** (`progress.md`, `assessments/latest.md`, plan files, `resources.md`) are still written with the Write tool directly: compose the new entry at the top, preserve all existing content verbatim below it.

## Project Discovery Config

Two layers. Per-project overrides global.

**Global:** `~/.bodhikit/config.json`. Optional.

```json
{ "searchPaths": ["$PWD", "~/learningWithBodhi"] }
```

**Per-project:** `<repo-root>/.bodhikit/config.json`. Optional. Highest precedence.

```json
{ "projectRoot": "study/" }
```

- `projectRoot` is a path (relative to the file's directory, or absolute) where the learner keeps `.bodhi/` for THIS repo.

**Discovery is a file-read, NOT a `bodhi-state` subcommand.** There is no `discover`, `--list`, or `list-projects` — do not call the script to find projects. The `bodhi-state` subcommand table above is the *complete* set; discovery is plain filesystem inspection (glob / `ls`), performed as follows:

**Discovery procedure (all skills use this exact procedure):**

1. From the current working directory, walk up to 3 parent levels looking for `.bodhikit/config.json`. If found and it declares `projectRoot`, treat that path as a project root and stop further search unless the caller explicitly wants `--all`.
2. Otherwise, read `~/.bodhikit/config.json` if it exists; if not, use the default `searchPaths: ["$PWD", "~/learningWithBodhi"]`.
3. For each path in `searchPaths`: resolve `$PWD` to cwd (and walk up 3 parents), expand `~`, then look for `learningWithBodhi/` directories.
4. Within each `learningWithBodhi/`, list subdirectories containing `.bodhi/state.json` — e.g. `ls -d <path>/learningWithBodhi/*/.bodhi/state.json 2>/dev/null`. Each match is one project (its dir is the parent of `.bodhi/`).

## Tracking-Surface Map (v2, 1.7.0)

| Surface | Pattern | Live doc | Archive |
|---|---|---|---|
| Sessions / progress | Live + archive + summary | `progress.md` | `progress/archive/<YYYY-MM-DD>[-N].md` |
| Assessments | Live + archive + summary | `assessments/latest.md` | `assessments/archive/<phase>-<topic>.md` |
| Plan | Sectional | `plan/README.md` + `plan/phase-{N}.md` | none |
| State | Slim JSON | `state.json` | none |
| Spaced review | Whole JSON | `spaced-review.json` | none |
| Profile | Split JSON | `.bodhi-profile.json` + `.bodhi-profile.projects.json` | none |
| Resources | Whole MD | `resources.md` | none |
| Assessment history | Append-only JSON | `assessment-history.json` | none |
| Teach-backs (capstone) | Per-post MD files | `teach-backs/<YYYY-MM-DD>-<slug>.md` | none |

Live-doc mechanics (summary growth, collapse, archive naming) live in the `state-lifecycle` KB. Skills load the live doc + current plan phase by default; `/plan` and `/evaluate` may load all phase files. Skills that read archive content MUST announce the read in their turn output.

## `sessionHistory[].type` Canonical Vocabulary (enforced in code by `record-session`)

| `type` | Written by | Meaning |
|---|---|---|
| `spaced-review` | `/quiz`, `/reflect` (due-concepts batch) | Routine spaced-review session |
| `quiz` | `/quiz` (explicit-topic invocation) | Quiz on a specific topic, not by schedule |
| `targeted-reteach` | `/teach` (re-entering a demoted concept) | Focused re-teach after demotion or precision-gap surfacing |
| `diagnostic-after-gap` | `/learn`, `/assess`, `/continue` (after absence) | Diagnostic after a meaningful gap |
| `learner-forget` | `/forget` | Learner-initiated demotion |
| `pair` | `/pair` Session End | Pair session touching tracked concepts |
| `practice` | `/practice` | Exercise session introducing/reviewing concepts |
| `evaluate` | `/evaluate` | Comprehensive evaluation snapshot |
| `other` | any skill | Escape hatch; **requires `subtype`**. Prefer extending this table over reaching for `other`. |

Optional fields on entries (writers MAY include via `--data`): `conceptsReviewed`, `passes`, `misses`, `partials`, `boxChanges`, `precisionGapMovement`, `habitObservations`, `notes`, `calibrationNote`, `conceptsDemoted`. Readers MUST tolerate unknown fields; the script preserves them.

## Mastery (canonical, computed by `bodhi-state mastery`)

```
mastered = (bloomLevel >= 4)
       AND (consecutiveCorrectAtL4Plus >= 3)
       AND (box >= 4)
       AND (feynmanPassed === true)
```

Skills MUST NOT redefine this formula inline. Field semantics (the Bloom ratchet, the counter rules, the Feynman flag) live in the `state-schema` KB; the underlying criteria in the `blooms-taxonomy` KB.

**Per-module tiers.** `mastery` and `snapshot` also return, per module, `tiers: {unclassified, introduced, familiar, mastered}` — each concept classified against the `blooms-taxonomy` KB's ordered tier ladder (that KB is the canonical definition; `mastered` reuses the formula above, so there is still one home for it). The counts always sum to the module's `concepts`. Skills render these counts and MUST NOT infer a tier from `mastered`/`classified`/`masteryPct` — those are module rollups, the ladder is per concept, and deriving one from the other loses the distribution.

**Legacy display rule:** a concept with `bloomLevel: 0` has never been classified by a v3 writer — gates treat it as "no opinion yet, allow advancement"; `/progress` displays `—` (not 0%) for modules where every concept is at `bloomLevel: 0`. `bodhi-state` implements both rules (the script reports `masteryPct: null` for such modules).

## Prerequisite Gate (canonical, computed by `bodhi-state gate-check`)

The `/teach` Phase 1 gate fires only on the first session of a new module (detected by: zero tracked concepts whose `module` matches `state.json.currentModule`). Per-prerequisite verdicts:

| Verdict | Condition | Gate behavior |
|---|---|---|
| `satisfied` | `bloomLevel >= 3` AND current evidence (`box >= 3` OR reviewed within 30 days) | Pass |
| `stale-reconfirm` | `bloomLevel >= 3` but box < 3 AND last review > 30 days ago | One quick reconfirm question — the Bloom ratchet alone is not current evidence |
| `no-opinion` | `bloomLevel == 0` | Pass (legacy fallthrough) |
| `apply-equivalent` | `1 <= bloomLevel < 3` but `box >= 3` AND last two reviews correct | Pass (gate-time read only; bloomLevel untouched) |
| `gap` | otherwise | Surface as an offer — never auto-block; the learner decides |

Prerequisites come from the plan's `**Prerequisites for next module:**` declaration (passed via `--prereqs`) or, as fallback, all concepts of the prior module (`previousModule` or inferred; the verdict JSON flags inference so the skill can tell the learner the mapping was inferred).

## Update Rules

- **JSON writes go through `bodhi-state`.** Hand-editing tracking JSON is the fallback of last resort, per the `state-schema` KB *Fallback discipline*.
- Markdown live docs: compose the new entry at the top; preserve existing content verbatim; never rotate (that is `/housekeep`'s job, per the `state-lifecycle` KB).
- Skills MUST NOT introduce new top-level fields, files, or directories under `.bodhi/` without updating the `state-schema` KB (and `bodhi-state`) first.
- Skills MUST NOT stuff long narrative into JSON fields — narrative belongs in `progress.md` / `assessments/latest.md`. `lastActivity` is one short sentence (≤120 chars).
- The per-topic Bloom maps in `state.json` (`initialBloomLevel` / `currentBloomLevel`) are an explicit **manual carve-out** — no script subcommand owns them. `/learn` seeds both; `/assess` and `/evaluate` may update `currentBloomLevel` by loading the `state-schema` KB and following its *Fallback discipline* (read → mutate in place → write → verify).
