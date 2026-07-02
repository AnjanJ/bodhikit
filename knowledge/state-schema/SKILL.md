---
description: "Canonical shape of BodhiKit tracking files, discovery config, and the bodhi-state write path every skill uses for JSON mutations"
user-invocable: false
---

# State Schema — Canonical Shape of BodhiKit Tracking Files

All skills that read or write `.bodhi/` tracking files reference this KB. Skills MUST NOT redeclare these shapes inline.

If a field is not listed here, do not add it. If a new field is genuinely needed, update this KB first, then `scripts/bodhi-state`, then the skills that touch it.

See also:
- `spaced-repetition` KB — box→interval mapping and update rules (implemented by `bodhi-state`).
- `state-lifecycle` KB — rotation/archive/collapse protocol (loaded by `/housekeep` only).
- `state-migration` KB — version transforms (loaded by `/housekeep migrate`).

## Guiding Principle: Progressive Disclosure for the Learner's State

The learner's accumulated work is sacred — nothing is deleted, nothing is gatekept. But context is finite, so every tracking surface is shaped so that **the smallest useful slice is what loads by default**, and the full history remains on disk behind explicit pointers. Three mechanisms: live + archive + summary for narrative surfaces, sectional files for the plan, slim JSON for state. Rotation is `/housekeep`'s job alone (see `state-lifecycle` KB); every other skill stays oblivious to compaction.

## The Write Path: `scripts/bodhi-state` (1.11.0 — canonical for ALL JSON writes)

Skills do not hand-edit tracking JSON. Every mutation of `state.json`, `spaced-review.json`, or the profile files goes through the plugin's deterministic writer:

```
"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project <project-dir> <subcommand> [options]
```

If `CLAUDE_PLUGIN_ROOT` is not set in the Bash environment, locate the script once with `find ~/.claude/plugins -type f -name bodhi-state -path "*bodhikit*" 2>/dev/null | head -1` (or the repo checkout's `scripts/bodhi-state` when running via `--plugin-dir`).

| Subcommand | Owns |
|---|---|
| `add-concept --concept N --module M [--question Q]` | New concept with canonical Box-1 defaults |
| `record-review --concept N --result correct\|incorrect\|partial --tested-bloom 0-6 [--confidence sure\|mostly\|guessing] [--module M] [--note S] [--source skill] [--retry]` | Leitner box math, nextReview dates, bloomLevel ratchet, `consecutiveCorrectAtL4Plus` rules, `reviewHistory[]` append. `--retry` = successive-relearning rep: history entry only, no box/counter/bloom movement (the original demotion stands) |
| `set-feynman --concept N` | `feynmanPassed = true` (set, never unset) |
| `record-session --type T [--subtype S] [--data '<json>']` | `sessionHistory[]` append, canonical-type enforcement (`type`/`subtype`/`date` in `--data` are ignored — flags only) |
| `record-assessment --trigger learn-phase2\|assess\|evaluate\|plan-regenerate --data '<entry json>'` | Append-only `assessment-history.json` entry, date-stamped |
| `forget --concepts "A, B" \| --concept N (repeatable) [--note S] [--activity S]` | Learner-initiated demote: box 1, counter reset, history + `learner-forget` session entry, `lastActivity`. Use `--concept` for names containing commas |
| `touch-state [--activity S] [--module M] [--module-index N] [--phase P] [--completion N]` | `state.json` session bookkeeping: dates, streak, totalSessions, module advance (records `previousModule`). The first touch of a new day also bumps the profile's `cumulativeStats.totalSessions` — no skill calls `bump-profile --counter totalSessions` |
| `bump-profile --counter <name>` | `cumulativeStats` increments in `.bodhi-profile.json` |
| `due [--limit N]` / `mastery` / `calibration` | Read-side rollups: due concepts (plus `unparseableDates` for schedule-broken entries — never silently skipped), canonical mastery % + `blockedOnFeynman` (concepts meeting every criterion except the explain-back gate), retention tiers, confidence calibration |
| `retention` / `export-anonymized` | Read-side outcome analytics (1.11.3): retention-at-review rates grouped by actual spacing gap and by box-at-review-time (`boxBefore`) — the empirical check on whether the Leitner intervals are calibrated — and a shareable anonymized stats export (counts and rates only; no concept names, no free text) for the README's outcome-data ask |
| `gate-check [--module M] [--prereqs "A,B"] [--prior-module M]` | Prerequisite Bloom gate verdict (see below) |
| `migrate-spaced-review` | One-shot v1/v2 → v3 transform: backup, in-place field fill, marker, verification |
| `verify` | Schema sanity check (also run by the plugin's Stop hook and `dev/check.sh`) |

The script preserves unknown fields by mutating parsed JSON in place, writes atomically, and rejects invalid `sessionHistory` types in code. The skill's job is the pedagogical judgment (which result, which Bloom level, which confidence tag); the script's job is the file.

**Fallback (script unavailable):** only after BOTH the `${CLAUDE_PLUGIN_ROOT}` path and the `find ~/.claude/plugins` lookup come up empty, say so plainly, then perform the minimal write by hand following this KB's shapes — Read the file, mutate the parsed JSON in place preserving every unknown field, fill the three v3 per-concept defaults on any concept missing them and set `version: 3` (read-tolerance — the eval harness caught a manual fallback skipping exactly this), Write it back, re-read to verify. Never re-serialize from a schema template.

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

**Discovery procedure (all skills use this exact procedure):**

1. From the current working directory, walk up to 3 parent levels looking for `.bodhikit/config.json`. If found and it declares `projectRoot`, treat that path as a project root and stop further search unless the caller explicitly wants `--all`.
2. Otherwise, read `~/.bodhikit/config.json` if it exists; if not, use the default `searchPaths: ["$PWD", "~/learningWithBodhi"]`.
3. For each path in `searchPaths`: resolve `$PWD` to cwd (and walk up 3 parents), expand `~`, then look for `learningWithBodhi/` directories.
4. Within each `learningWithBodhi/`, list subdirectories containing `.bodhi/state.json`.

## Tracking-Surface Layout (v2, 1.7.0)

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

Live-doc mechanics (summary growth, collapse, archive naming) live in the `state-lifecycle` KB. Skills load the live doc + current plan phase by default; `/plan` and `/evaluate` may load all phase files.

## File Shapes

### `learningWithBodhi/<project>/.bodhi/state.json`

Slim. No long narrative fields — session narrative lives in `progress.md`.

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
  "previousModule": "string",
  "currentModuleIndex": 0,
  "lastActivity": "string",
  "initialBloomLevel": { "<sub-topic>": 0 },
  "currentBloomLevel": { "<sub-topic>": 0 },
  "overallCompletion": 0
}
```

- `currentStreak`: consecutive days. Reset to 1 if `sessionDates` gap exceeds 1 day. Maintained by `bodhi-state touch-state`.
- `previousModule`: set automatically by `touch-state --module` when the module advances; read by `gate-check`.
- `initialBloomLevel` / `currentBloomLevel`: the per-topic Bloom maps are an explicit **manual carve-out** — no script subcommand owns them. `/learn` seeds both; `/assess` and `/evaluate` may update `currentBloomLevel` via the fallback discipline (read → mutate in place → write → verify).
- `lastActivity`: one short sentence (≤120 chars) used by `/progress quick` and `/continue`. Anything longer belongs in `progress.md`.
- **No `lastSessionSummary` / `bloomResetNote` in v2** — migrated to `progress.md`.

### `learningWithBodhi/<project>/.bodhi/progress.md`

Live narrative document. Latest session in full, then a "Summary of earlier sessions" block with pointers.

```markdown
# Progress Log

## <YYYY-MM-DD> — Session <N> (<short label>)

**Duration:** <approx>
**Activities:**
- <bullets>

**Outcomes:**
- <bullets>

**Bloom adjustments:**
- <area>: <from> → <to>

**Next:** <what the next session should open with>

---

## Summary of earlier sessions

- **<YYYY-MM-DD> — <one-line headline>**
  <optional 1-3 more lines>
  → `archive/<filename>.md`
```

### `learningWithBodhi/<project>/.bodhi/assessments/latest.md`

Most recent assessment in full, then a "Summary of earlier assessments" block with `→ archive/<filename>.md` pointers. Multi-stack projects may have multiple assessments per phase; each becomes its own archive entry.

### `learningWithBodhi/<project>/.bodhi/plan/`

Sectional. Generated at plan creation; rewritten only by `/plan regenerate`.

`plan/README.md`: arc overview — current phase pointer, target arc, pace, bulleted phase list with `→ phase-<N>.md` pointers.

`plan/phase-{N}.md`: per-phase goals, duration, success criteria, then `### Module <N>.<M> — <name>` sections with concepts, exercises, success markers. From Module 2 onward each module section carries a `**Prerequisites for next module:**` line naming the concepts the next module builds on (feeds `gate-check --prereqs`).

### `learningWithBodhi/<project>/.bodhi/spaced-review.json`

Whole JSON; written exclusively through `bodhi-state`. `/housekeep` does not rotate this file.

```json
{
  "version": 3,
  "lastReviewCheck": "ISO-8601",
  "concepts": [
    {
      "name": "string",
      "module": "string",
      "introduced": "YYYY-MM-DD",
      "box": 1,
      "nextReview": "YYYY-MM-DD",
      "lastReviewed": "YYYY-MM-DD",
      "question": "string",
      "lastResult": "string",
      "bloomLevel": 0,
      "feynmanPassed": false,
      "consecutiveCorrectAtL4Plus": 0,
      "reviewHistory": [
        { "date": "YYYY-MM-DD", "result": "correct|incorrect|partial", "bloomLevel": 0, "boxBefore": 1, "confidence": "sure|mostly|guessing", "source": "string" }
      ]
    }
  ],
  "sessionHistory": [
    { "date": "YYYY-MM-DD", "type": "spaced-review", "conceptsReviewed": 0, "passes": 0, "misses": 0 }
  ]
}
```

- `box`: integer 1–5; intervals and update rules in the `spaced-repetition` KB, implemented by `record-review`.
- `reviewHistory[].retry` (optional, 1.11.1): `true` marks a successive-relearning rep — recorded evidence that did NOT move the box. `reviewHistory[].note` (optional): short free-text annotation (e.g. "learner-initiated demote"). The script caps `reviewHistory` at the most recent 100 entries per concept; older entries roll into a `reviewHistoryArchived` integer counter.
- `reviewHistory[].confidence` (optional, 1.11.0): the learner's pre-reveal confidence tag — `sure` / `mostly` / `guessing`, collected by `/quiz` and `/reflect` BEFORE the answer is judged. `bodhi-state calibration` aggregates these into overconfidence/underconfidence rates (see `metacognition` KB for why predict-before-reveal is the load-bearing order).
- `reviewHistory[].source` (optional): which skill produced the review.
- `reviewHistory[].boxBefore` (optional, 1.11.3): the box the concept occupied when this review was answered — the box whose interval scheduled it. Written by `record-review` on every new entry; absent on older entries (readers tolerate absence; `retention` reports how many legacy entries lack it). This is what makes retention-at-review analysis exact instead of reconstructed.
- `sessionHistory` is an append-only audit trail. `/evaluate` reads it; routine skills do not.

**`sessionHistory[].type` canonical vocabulary** (enforced in code by `record-session`):

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

**Per-concept Bloom + Feynman fields (v3).** These make mastery observable from state:

- `bloomLevel`: integer 0–6. `0` = uninitialized (no v3 writer has classified it). Ratchets up only — `record-review` takes `max(current, tested-bloom)` on a correct answer and never demotes; even `/forget` demotes the box, not the Bloom classification.
- `feynmanPassed`: boolean. Set by `set-feynman` when `/teach` (a full session or its understanding-only path) observes a genuine explain-back. Set, never unset.
- `consecutiveCorrectAtL4Plus`: incremented on correct at tested-bloom ≥ 4; reset to 0 on any incorrect, any partial, and on `/forget` (1.11.2 — a partial retrieval breaks the consecutive-correct streak; "3 consecutive correct" means uninterrupted corrects). A correct at a lower tested level leaves the counter untouched (a routine low-level recall between two L4 demonstrations is a different measurement, not counter-evidence). `--retry` reps never touch it.

**Mastery formula (canonical, computed by `bodhi-state mastery`):**

```
mastered = (bloomLevel >= 4)
       AND (consecutiveCorrectAtL4Plus >= 3)
       AND (box >= 4)
       AND (feynmanPassed === true)
```

Skills MUST NOT redefine this formula inline. See `blooms-taxonomy` KB for the underlying criteria.

**Legacy fallthrough (v2 → v3).** A concept with `bloomLevel: 0` has never been classified by a v3 writer — regardless of `lastReviewed` (real v2 data routinely has populated `lastReviewed` from pre-v3 quizzes; the 1.10.0 rule that also required `lastReviewed: null` was wrong and was corrected in 1.10.7). Gates treat `bloomLevel: 0` as "no opinion yet, allow advancement"; `/progress` displays `—` (not 0%) for modules where every concept is at `bloomLevel: 0`. `bodhi-state` implements both rules.

### Prerequisite gate (canonical, computed by `bodhi-state gate-check`)

The `/teach` Phase 1 gate fires only on the first session of a new module (detected by: zero tracked concepts whose `module` matches `state.json.currentModule`). Per-prerequisite verdicts:

| Verdict | Condition | Gate behavior |
|---|---|---|
| `satisfied` | `bloomLevel >= 3` AND current evidence (`box >= 3` OR reviewed within 30 days) | Pass |
| `stale-reconfirm` | `bloomLevel >= 3` but box < 3 AND last review > 30 days ago | One quick reconfirm question — the Bloom ratchet alone is not current evidence (1.11.0 recency rule) |
| `no-opinion` | `bloomLevel == 0` | Pass (legacy fallthrough) |
| `apply-equivalent` | `1 <= bloomLevel < 3` but `box >= 3` AND last two reviews correct | Pass (gate-time read only; bloomLevel untouched) |
| `gap` | otherwise | Surface as an offer — never auto-block; the learner decides |

Prerequisites come from the plan's `**Prerequisites for next module:**` declaration (passed via `--prereqs`) or, as fallback, all concepts of the prior module (`previousModule` or inferred; the verdict JSON flags inference so the skill can tell the learner the mapping was inferred).

### `learningWithBodhi/<project>/.bodhi/assessment-history.json`

Structured assessment data for `/evaluate` and `/progress`. Append-only; never edit past entries.

```json
{
  "version": 1,
  "entries": [
    {
      "date": "YYYY-MM-DD",
      "trigger": "learn-phase2 | assess | evaluate | plan-regenerate",
      "topic": "string",
      "subTopics": [
        { "name": "string", "bloomLevel": 0, "confidence": "high|medium|low", "evidence": "string" }
      ],
      "overallNote": "string",
      "predictionDelta": {
        "predictedBiggestGrowth": "string",
        "measuredBiggestGrowth": "string",
        "predictedBiggestGap": "string",
        "measuredBiggestGap": "string",
        "perTopicBloomPredictions": [ { "name": "string", "predicted": 0, "measured": 0 } ],
        "calibrationNote": "string"
      }
    }
  ]
}
```

- Skills that run assessments (`/learn` Phase 2, `/assess`, `/evaluate` Phase 2, `/plan regenerate`) MUST append an entry here (prose version goes to `assessments/latest.md`).
- `predictionDelta` is populated by `/evaluate` Phase 2.5 (predict-before-reveal); absent elsewhere. See `metacognition` KB.

### `learningWithBodhi/<project>/.bodhi/resources.md`

Markdown log, dated or status-grouped sections. Small; not housekept.

### `learningWithBodhi/<project>/teach-backs/`

Capstone artifacts from `/teach-back`, at the project root (learner-authored, not internal state). Each post: `teach-backs/<YYYY-MM-DD>-<slug>.md` with a header (thesis, reader, why-it-matters), the learner's prose, and a closing status block (`Status: draft | published | personal-notes`, `Decided:`, `Masters consulted:`, `Post-Phase-6 revisions:`). Only `/teach-back` writes here. Not housekept.

### `learningWithBodhi/.bodhi-profile.json`

Cross-project learner profile (v2 split layout: this file holds top-level fields; the project list lives in `.bodhi-profile.projects.json`).

```json
{
  "version": 2,
  "careerGoal": "string",
  "whyLearning": "string",
  "priorExperience": "string",
  "learningStyle": "string",
  "overallBloomLevels": { "<area>": 0 },
  "cumulativeStats": {
    "totalSessions": 0,
    "totalExercises": 0,
    "totalConceptsLearned": 0,
    "totalMilestonesReached": 0,
    "totalProjects": 0,
    "teachBacksWritten": 0,
    "teachBacksPublished": 0
  },
  "patterns": {
    "persistentChallenges": ["<topic>"],
    "consistentStrengths": ["<topic>"]
  },
  "learnerBackground": {
    "domains": ["<string>"],
    "analogyHistory": [
      { "concept": "string", "domain": "string", "landed": true, "date": "YYYY-MM-DD" }
    ]
  },
  "lastUpdated": "ISO-8601"
}
```

- `cumulativeStats` counters are incremented via `bodhi-state bump-profile` (the skill decides WHEN — e.g. `/teach` bumps `totalConceptsLearned` only when a concept first reaches Bloom 3+ and `progress.md` shows no prior count for it). Exception: `totalSessions` is bumped automatically by `touch-state` on the first touch of a new day — no skill calls it directly.
- `learnerBackground.domains[]` / `analogyHistory[]`: populated by the analogy-escalation protocol (see `feynman-technique` KB). Read-then-append; never overwrite.

### Project completion (canonical, 1.11.1)

A project is **complete** when every module in every plan phase is finished or explicitly skipped AND the learner confirms. Completion is never inferred silently — `/evaluate` asks ("Shall we mark this path complete?") and only the learner's yes moves the entry from `activeProjects` to `completedProjects`. Completion gates the capstone offer, the mentor offer, and `/teach-back` eligibility.

### `learningWithBodhi/.bodhi-profile.projects.json`

Per-project metadata, loaded only by cross-project skills (`/mentor`, `/evaluate`, `/learn`).

```json
{
  "version": 2,
  "activeProjects": [
    { "name": "string", "topic": "string", "startedAt": "YYYY-MM-DD", "currentPhase": "string", "currentModule": "string", "bloomLevel": 0, "pace": "string", "status": "string", "trackPurpose": "string" }
  ],
  "completedProjects": [
    { "name": "string", "completedAt": "YYYY-MM-DD", "finalBloomLevel": 0, "trackPurpose": "string" }
  ]
}
```

Writers: `/learn` (append on project start), `/evaluate` (refresh; move to `completedProjects` on completion), `/mentor` (career fields in the parent profile only).

## Update Rules

- **JSON writes go through `bodhi-state`.** Hand-editing tracking JSON is the fallback of last resort, performed read→mutate-in-place→write→verify with unknown fields preserved.
- Markdown live docs: compose the new entry at the top; preserve existing content verbatim; never rotate (that is `/housekeep`'s job, per the `state-lifecycle` KB).
- Skills MUST NOT introduce new top-level fields, files, or directories under `.bodhi/` without updating this KB (and `bodhi-state`) first.
- Skills MUST NOT stuff long narrative into JSON fields — narrative belongs in `progress.md` / `assessments/latest.md`.
- Skills that read archive content MUST announce the read in their turn output.
- Schemas evolve; readers tolerate older `version` values (the script read-tolerates v1/v2 and persists v3 on write). Skills MUST NOT branch behavior on version in prose. Full transforms live in the `state-migration` KB.
