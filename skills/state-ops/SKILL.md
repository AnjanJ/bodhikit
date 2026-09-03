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

Every skill carries its own exact invocation; `bodhi-state <subcommand> --help` prints the flags. What each one owns — the contracts a skill must not work around:

**Writers**

- `add-concept` — a new concept with the canonical Box-1 defaults.
- `record-review` — Leitner box and `nextReview`, the Bloom ratchet, `consecutiveCorrectAtL4Plus`, the `reviewHistory[]` append. `--confidence sure|mostly|guessing` is the learner's pre-reveal calibration tag — recorded, never a gate on promotion. `--retry` is a successive-relearning rep: history only, no box/counter/bloom movement (the demotion stands). `--applied` marks an outcome demonstrated in working code the tutor read (an exercise, a driven piece), never an explanation or a quiz answer: it is the only evidence the gate and the mastery formula accept for "can build with it", so a verbal review must not carry it. Its output's `crossedBloom3: true` is the one trigger for `bump-profile --counter totalConceptsLearned`.
- `set-feynman` — `feynmanPassed = true`, never unset.
- `record-session` — a `sessionHistory[]` entry in the canonical type vocabulary (below); `type`, `subtype` and `date` come from flags, never from `--data`.
- `record-assessment` — an append-only, date-stamped `assessment-history.json` entry.
- `forget` — the learner-initiated demote: box 1, counter reset, history and `learner-forget` entries, `lastActivity`. `--concept` (repeatable) for names containing commas.
- `defer` / `park [--resume]` — scheduling, never an outcome. A deferral rolls `nextReview` and writes a history entry with **no result**; parking leaves rotation with box, bloom, Feynman and counters intact and is reported as a count, never hidden. Do not invent a `result` for a concept that was not reviewed.
- `touch-state` — `state.json` session bookkeeping: dates, streak, `totalSessions`, module advance (`previousModule`). The first touch of a day also bumps the profile's `cumulativeStats.totalSessions` — no skill calls `bump-profile` for that.
- `bump-profile --counter` — `cumulativeStats` increments in `.bodhi-profile.json`.
- `profile-add-project` / `profile-update-project` / `profile-complete-project` / `profile-update-patterns` — the `.bodhi-profile.projects.json` list (schema-complete entries, unknown fields preserved) and the count-based `patterns`. Completion is learner-confirmed, never inferred; the skill never tallies assessments in prose.

**Readers** (no lock file, no writes)

- `due` — due concepts in review order (`priority`, `dueSince`, `overdueDays`, `bloomOutcome`) — by design no box or Bloom number, so narrating it cannot leak one. Each is tagged `neverTaught` (no review ever came from `--source teach`): route those to `/teach`, not `/quiz`. `unparseableDates` lists schedule-broken entries rather than skipping them.
- `session-brief --concept` — `/teach`'s branches: pretest vs graded retrieval (`firstExposure`/`pretestApplies`), `isReteach`, box/bloom/Feynman position, `dueForReview`.
- `snapshot` — the whole `/progress` surface in one call (`project`, `cadence`, `review`, `mastery`, `calibration`). `mastery` / `calibration` / `retention` / `export-anonymized` — its parts and the outcome analytics (retention by spacing gap and `boxBefore`; an anonymized counts-only export).
- `revision-brief` — today's facts for the revision sheet (`sessionToday`, `suggestedFile`, `existing`); the Stop hook reads it.
- `gate-check` — the prerequisite verdict (*Prerequisite Gate* below).

**Maintenance**

- `migrate-spaced-review` — v1/v2 → v3 once: backup, in-place field fill, marker, verification.
- `normalize` — idempotent repair of executor drift (invented result/type vocabulary, nested bookkeeping, the lossless type fixes: a numeric-string box or level, a string boolean), both files backed up first. `verify` names it only when it can perform the repair.
- `verify` — the schema check the Stop hook and `dev/check.sh` run.

The script preserves unknown fields by mutating parsed JSON in place, writes atomically, and rejects invalid `sessionHistory` types in code. The skill's job is the pedagogical judgment (which result, which Bloom level, which confidence tag); the script's job is the file.

**Fallback (script unavailable):** only after BOTH the `${CLAUDE_PLUGIN_ROOT}` path and the `find ~/.claude/plugins` lookup come up empty, say so plainly, then load the `state-schema` KB and perform the minimal write by hand per its *Fallback discipline* — read → mutate the parsed JSON in place → write → verify, preserving every unknown field.

**Markdown surfaces** (`progress.md`, `assessments/latest.md`, plan files, `resources.md`, and the learner-facing `revision/` sheets) are still written with the Write tool directly: compose the new entry at the top, preserve all existing content verbatim below it.

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
| Revision sheets | Per-day MD files (learner take-home, outside `.bodhi/`) | `revision/<YYYY-MM-DD>-<concept>.md` — written at session end per `/reflect`'s `references/revision-sheet.md`; `revision-brief` names the file; the Stop hook requires it on a day that studied something | none |

Live-doc mechanics (summary growth, collapse, archive naming) live in the `state-lifecycle` KB. Skills load the live doc + current plan phase by default; `/plan` and `/evaluate` may load all phase files. Skills that read archive content MUST announce the read in their turn output.

## `sessionHistory[].type` Canonical Vocabulary (enforced in code by `record-session`)

| `type` | Written by | Meaning |
|---|---|---|
| `spaced-review` | `/quiz`, `/reflect` (due-concepts batch) | Routine spaced-review session |
| `quiz` | `/quiz` (explicit-topic invocation) | Quiz on a specific topic, not by schedule |
| `targeted-reteach` | `/teach` (re-entering a demoted concept) | Focused re-teach after demotion or precision-gap surfacing |
| `diagnostic-after-gap` | `/learn`, `/assess`, `/continue` (after absence) | Diagnostic after a meaningful gap |
| `learner-forget` | `/forget` | Learner-initiated demotion |
| `learner-park` | `/forget --park` (and `--unpark`) | Learner-initiated exit from / return to review rotation |
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
       AND (appliedEvidence >= 1)
```

`appliedEvidence` is the count of `correct` reviews flagged `applied` since the most recent miss (`state-schema` KB). Without it, every other conjunct can be met in conversation and a learner who has never run the code reads as *Solid*. `mastery` and `snapshot` report `blockedOnApplied` (every criterion but this one) beside `blockedOnFeynman`, and each module row carries `applied` (concepts with at least one build since the last miss).

Skills MUST NOT redefine this formula inline. Field semantics (the Bloom ratchet, the counter rules, the Feynman flag) live in the `state-schema` KB; the underlying criteria in the `blooms-taxonomy` KB.

**Per-module tiers.** `mastery` and `snapshot` also return, per module, `tiers: {unclassified, introduced, familiar, mastered}` — each concept classified against the `blooms-taxonomy` KB's ordered tier ladder (that KB is the canonical definition; `mastered` reuses the formula above, so there is still one home for it). The counts always sum to the module's `concepts`. Skills render these counts and MUST NOT infer a tier from `mastered`/`classified`/`masteryPct` — those are module rollups, the ladder is per concept, and deriving one from the other loses the distribution.

**Legacy display rule:** a concept with `bloomLevel: 0` has never been classified by a v3 writer — gates treat it as "no opinion yet, allow advancement"; `/progress` displays `—` (not 0%) for modules where every concept is at `bloomLevel: 0`. `bodhi-state` implements both rules (the script reports `masteryPct: null` for such modules).

## Prerequisite Gate (canonical, computed by `bodhi-state gate-check`)

The `/teach` Phase 1 gate fires only on the first session of a new module (detected by: zero tracked concepts whose `module` matches `state.json.currentModule`). Per-prerequisite verdicts:

| Verdict | Condition | Gate behavior |
|---|---|---|
| `satisfied` | `bloomLevel >= 3` AND (`box >= 3` OR two or more correct reviews graded at Bloom 3+ **since the most recent miss** — an `incorrect` review or a `/forget` resets the count — with the latest reviewed within 30 days) AND at least one `applied` correct since that miss | Pass (`reason: box` or `evidence`) |
| `stale-reconfirm` | `bloomLevel >= 3` but box < 3 AND either fewer than two level-3+ corrects since the last miss (`reason: single-evidence` — zero after a `/forget`) or last review > 30 days ago (`reason: stale`); OR the recall evidence above would pass but no `applied` correct exists since the last miss (`reason: no-applied-evidence`, 1.20.0 — every concept tracked before the flag meets this once) | One quick reconfirm — a single grade is noisy and the Bloom ratchet is one-way, so one review is not settled evidence. For `no-applied-evidence` the reconfirm is a few lines of code the learner writes, recorded `--applied`; for the other reasons a question. Phrase by reason: "we have only seen this once" / "it has been a while" / "you have explained this well; show me once in code" |
| `no-opinion` | `bloomLevel == 0` | Pass (legacy fallthrough) |
| `apply-equivalent` | `1 <= bloomLevel < 3` but `box >= 3` AND last two reviews correct AND one `applied` correct since the last miss (without it: `stale-reconfirm` / `no-applied-evidence`) | Pass (gate-time read only; bloomLevel untouched) |
| `gap` | otherwise | Surface as an offer — never auto-block; the learner decides |

Each prerequisite row also carries `evidenceAt3Plus` (count of level-3+ corrects since the last miss), `appliedEvidence` (built corrects since the last miss) and `bloomLabel`/`bloomOutcome` for learner-facing phrasing (`blooms-taxonomy` KB rendering rule).

Prerequisites come from the plan's `**Prerequisites for next module:**` declaration (passed via `--prereqs`) or, as fallback, all concepts of the tracked `previousModule` (the verdict JSON reports `prerequisiteSource: "declared" | "prior-module"` so the skill can tell the learner which mapping it used). When neither is available the gate declines to fire (`fires: false` with the reason) — it never infers a prerequisite module from concept dates; a guessed gate generates false reconfirm questions, which cost more trust than no gate.

## Update Rules

- **JSON writes go through `bodhi-state`.** Hand-editing tracking JSON is the fallback of last resort, per the `state-schema` KB *Fallback discipline*.
- Markdown live docs: compose the new entry at the top; preserve existing content verbatim; never rotate (that is `/housekeep`'s job, per the `state-lifecycle` KB).
- Skills MUST NOT introduce new top-level fields, files, or directories under `.bodhi/` without updating the `state-schema` KB (and `bodhi-state`) first.
- Skills MUST NOT stuff long narrative into JSON fields — narrative belongs in `progress.md` / `assessments/latest.md`. `lastActivity` is one short sentence (≤120 chars).
- The per-topic Bloom maps in `state.json` (`initialBloomLevel` / `currentBloomLevel`) are an explicit **manual carve-out** — no script subcommand owns them. `/learn` seeds both; `/assess` and `/evaluate` may update `currentBloomLevel` by loading the `state-schema` KB and following its *Fallback discipline* (read → mutate in place → write → verify).
