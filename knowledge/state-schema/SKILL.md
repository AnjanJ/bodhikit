---
description: "Canonical shape of BodhiKit tracking files, discovery config (global + per-project), tracking-surface layout, and the universal housekeeping protocol"
user-invocable: false
---

# State Schema — Canonical Shape of BodhiKit Tracking Files

All skills that read or write `.bodhi/` tracking files reference this KB. Skills MUST NOT redeclare these shapes inline.

If a field is not listed here, do not add it. If a new field is genuinely needed, update this KB first, then the skills that touch it.

See also:
- `spaced-repetition` KB — box→interval mapping and update rules.
- `read-defaults` KB — per-skill read defaults (loaded by `/housekeep`, audit, lint; skills do not load it at runtime).
- `state-migration` KB — schema versioning and one-shot conversion procedure (loaded by `/housekeep migrate`).

## Guiding Principle: Progressive Disclosure for the Learner's State

The learner's accumulated work is sacred — nothing is deleted, nothing is gatekept. But context is finite. So every tracking surface is shaped so that **the smallest useful slice is what loads by default**, and **the full history remains available on disk, fetched only when the situation justifies it**.

Three mechanisms achieve this:

1. **Live + archive + summary layout** for narrative surfaces (progress, assessments). The live doc holds the latest entry plus a growing summary block with pointers; the full prior text lives in an archive directory.
2. **Sectional files** for static-but-fat surfaces (plan). The plan is split into per-phase files at generation time; routine skills load the current phase only.
3. **Slim JSON** for state. JSON files carry pointers, counts, and current values — never long narrative.

Compaction is performed by a single dedicated skill: `/bodhikit:housekeep`. No other skill rotates files or rewrites archives. Every other skill stays oblivious to compaction.

## Project Discovery Config

Two layers. Per-project overrides global.

**Global:** `~/.bodhikit/config.json`. Optional.

```json
{
  "searchPaths": ["$PWD", "~/learningWithBodhi"]
}
```

**Per-project:** `<repo-root>/.bodhikit/config.json`. Optional. Highest precedence.

```json
{
  "projectRoot": "study/"
}
```

- `projectRoot` is a path (relative to the file's directory, or absolute) where the learner keeps `.bodhi/` for THIS repo. Lets a user say "in this Rails repo, learning lives at `study/`" without polluting `~/learningWithBodhi`.

**Discovery procedure (all skills use this exact procedure):**

1. From the current working directory, walk up to 3 parent levels looking for `.bodhikit/config.json`. If found and it declares `projectRoot`, treat that path as a project root and stop further search unless the caller explicitly wants `--all`.
2. Otherwise, read `~/.bodhikit/config.json` if it exists; if not, use the default `searchPaths: ["$PWD", "~/learningWithBodhi"]`.
3. For each path in `searchPaths`: resolve `$PWD` to cwd (and walk up 3 parents), expand `~`, then look for `learningWithBodhi/` directories.
4. Within each `learningWithBodhi/`, list subdirectories containing `.bodhi/state.json`.

**Legacy path detection (one-time migration help):** If discovery finds projects under `~/code/learningWithBodhi` or `~/projects/learningWithBodhi` (pre-1.6.0 hardcoded paths) AND no `~/.bodhikit/config.json` exists, `/status` SHOULD emit a single-line notice the first time it runs: "Found projects at <path>. Run `/bodhikit:housekeep migrate` to save these as search paths and convert tracking files to the 1.7.0 layout." This notice is one-shot.

## Tracking-Surface Layout (v2, 1.7.0)

Every `.bodhi/` surface follows one of three patterns. The pattern dictates how skills read and how `/housekeep` rotates.

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

### Live + archive + summary pattern (sessions, assessments)

The live doc has two parts:

1. **Latest entry, in full.** The most recently written session log or assessment report.
2. **Summary of earlier entries.** A growing block where each archived entry is represented by 2–20 lines (target ~5), each with a date, headline, optional key Bloom moves / insights, and an explicit pointer to the archive file.

Skills read the live doc by default. They follow a pointer into the archive only when the situation justifies it — and the live doc's summary tells them whether following a pointer would be valuable.

**Summary block grows from 2 to 20 lines per entry.** Routine sessions get ~2-5 lines; milestone sessions (phase complete, assessment done, breakthrough) get up to 20.

**Collapse rule.** When the cumulative summary block crosses 200 lines, the oldest summary entries roll into a *phase summary* (a single entry covering a contiguous range): "Phase 0 (M sessions, 2026-03-23 → 2026-04-30): outcomes summary. Archive: `archive/2026-03-*.md`." The original per-session archive files are not touched.

### Sectional pattern (plan)

Plans are split at generation time. `plan/README.md` is the arc overview: phase titles, durations, and a pointer to the current phase. `plan/phase-{N}.md` files hold the detailed plan for each phase (modules, exercises, success criteria).

Skills load `plan/README.md` + the current phase file by default. `/plan` (when regenerating or displaying the full arc) and `/evaluate` (computing trajectory) load all `plan/phase-*.md`.

### Slim JSON pattern (state)

`state.json` carries pointers, counts, and current values. No long narrative. Fields like `lastSessionSummary` and `bloomResetNote` that existed in v1 have moved to `progress.md` (the live narrative surface).

### Split JSON pattern (profile)

`.bodhi-profile.json` carries top-level fields (career goal, cumulative stats, overall Bloom's levels). `activeProjects` (a per-project array that grows linearly with project count) lives in `.bodhi-profile.projects.json`. Skills read the smaller one by default; cross-project skills (`/mentor`, `/evaluate`, `/learn` scoping a new project) read both.

## Universal Housekeeping Protocol

When `/bodhikit:housekeep` runs, it performs, for each *live + archive + summary* surface (currently sessions and assessments):

1. **Detect new content.** Is there a latest entry in the live doc that postdates the most recent archive file?
2. **Archive the previous live entry.** Move it to `<surface>/archive/<date>[-N].<ext>`. Naming: ISO date; append `-2`, `-3` for multiple same-day entries.
3. **Append a summary line/block to the live doc's "Summary of earlier" section.** Min 2 lines, max 20 lines, target ~5. Format:
   ```
   - **<date> — <one-line headline>**
     <optional 1-3 lines: key Bloom moves, key insights>
     → `archive/<filename>`
   ```
4. **Collapse old summary entries if the block exceeds 200 lines.** Oldest entries roll into a phase-summary entry. The per-entry archive files are not modified.

**Idempotency.** Running `/housekeep` twice in a row is a no-op the second time — step 1 finds nothing new.

**Non-destruction.** Archive files are permanent. `/housekeep` never deletes archive content and never edits an existing archive file.

**Transparency.** `/housekeep` prints what it rotated and the before/after byte sizes of the live docs.

**Trigger.** `/housekeep` is invoked explicitly. Other skills do not embed the protocol. `/reflect` and `/wrap` (when present) MAY invoke `/housekeep` at the end of their flow. `/continue` MAY detect un-housekept state and invoke `/housekeep` before resuming, silently.

**Migration mode.** `/housekeep migrate` performs the one-shot v1 → v2 conversion. See `state-migration` KB for the full migration table and procedure.

## File Shapes

### `learningWithBodhi/<project>/.bodhi/state.json`

Slim. No long narrative fields. Session-narrative content lives in `progress.md`.

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

- `currentStreak`: consecutive days. Reset to 1 if `sessionDates` gap exceeds 1 day.
- `overallCompletion`: 0–100, integer. Calculated from modules completed.
- `lastActivity`: one short sentence (≤120 chars). Used by `/status` and `/continue` for the "where you left off" line. Anything longer belongs in `progress.md`.
- **No `lastSessionSummary` field in v2.** Migrated to `progress.md`.
- **No `bloomResetNote` field in v2.** Migrated to `progress.md` as a session entry.

### `learningWithBodhi/<project>/.bodhi/progress.md`

Live narrative document. Latest session in full, followed by a "Summary of earlier sessions" block with pointers.

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
  <optional 1-3 more lines: key Bloom moves, key insights>
  → `archive/<filename>.md`
- **<YYYY-MM-DD> — <one-line headline>**
  → `archive/<filename>.md`
```

- One session entry at the top, in full.
- Summary block grows by 2-20 lines per archived session (target ~5).
- When summary block exceeds 200 lines, oldest entries roll into a phase-summary entry (handled by `/housekeep`).
- Archive files at `progress/archive/session-<YYYY-MM-DD>[-N].md`.

### `learningWithBodhi/<project>/.bodhi/assessments/latest.md`

Live assessment document. Most recent assessment in full, followed by a "Summary of earlier assessments" block.

```markdown
# Latest Assessment

## <Phase / Topic> — <YYYY-MM-DD>

<full assessment report: bloom table, evidence, recommendations>

---

## Summary of earlier assessments

- **<YYYY-MM-DD> — <phase / topic>**
  <2-20 line digest: key bloom levels, headline finding>
  → `archive/<filename>.md`
```

- One assessment in full at the top.
- Multi-stack projects (like a multi-track architect path) may have multiple assessments per phase; each becomes its own archive entry.
- Archive files at `assessments/archive/<phase>-<topic>.md`.

### `learningWithBodhi/<project>/.bodhi/plan/`

Sectional layout. Generated at plan creation time; rewritten only when `/plan regenerate` is invoked.

```
plan/
  README.md              # arc overview, phase titles, current pointer
  phase-0.md             # detailed phase 0 plan
  phase-1.md             # detailed phase 1 plan
  phase-2.md             # ...
```

`plan/README.md` structure:

```markdown
# Learning Plan — <topic>

**Current phase:** <N> (`phase-<N>.md`)
**Target arc:** <duration>
**Pace:** <intent>

## Phases

- **Phase 0 — <name>** (<duration>) → `phase-0.md`
- **Phase 1 — <name>** (<duration>) → `phase-1.md`
- ...
```

`plan/phase-{N}.md` structure:

```markdown
# Phase <N> — <name>

**Goals:** <bullets>
**Duration:** <estimate>
**Success criteria:** <bullets>

## Modules

### Module <N>.1 — <name>
<module detail: concepts, exercises, success markers>

### Module <N>.2 — <name>
...
```

Skills load `plan/README.md` (always small) + the current phase file. Loading all phase files is reserved for `/plan` (view/regen) and `/evaluate` (trajectory).

### `learningWithBodhi/<project>/.bodhi/spaced-review.json`

Whole JSON; concepts grow but stay queryable. `/housekeep` does not rotate this file.

```json
{
  "version": 2,
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
      "reviewHistory": [
        { "date": "YYYY-MM-DD", "result": "correct|incorrect|partial" }
      ]
    }
  ],
  "sessionHistory": [
    {
      "date": "YYYY-MM-DD",
      "type": "spaced-review",
      "conceptsReviewed": 0,
      "passes": 0,
      "misses": 0
    }
  ]
}
```

- `box`: integer 1–5. Box→interval mapping is defined in the `spaced-repetition` KB. Skills MUST NOT redeclare intervals.
- New concept: `box: 1`, `nextReview: tomorrow`.
- Correct recall: `box` up one (max 5), recompute `nextReview` from the spaced-repetition table.
- Incorrect recall or learner-initiated `/forget`: `box: 1`, `nextReview: tomorrow`.
- `sessionHistory` is append-only audit trail. `/evaluate` reads it; routine skills do not.

**Concept retirement.** When `concepts.length` exceeds 200, `/housekeep` MAY (with user confirmation) move concepts with `lastReviewed` older than 180 days AND `box: 1` (i.e., demoted-and-forgotten) into a sibling `spaced-review.retired.json` file. Not automatic; surfaced as a suggestion in `/housekeep` output.

### `learningWithBodhi/<project>/.bodhi/assessment-history.json`

Structured assessment data for analytical skills like `/evaluate` and `/progress`. Parallel to `assessments/latest.md`, not a replacement.

```json
{
  "version": 1,
  "entries": [
    {
      "date": "YYYY-MM-DD",
      "trigger": "learn-phase2 | assess | evaluate | plan-regenerate",
      "topic": "string",
      "subTopics": [
        {
          "name": "string",
          "bloomLevel": 0,
          "confidence": "high|medium|low",
          "evidence": "string"
        }
      ],
      "overallNote": "string"
    }
  ]
}
```

- Append-only. Never edit past entries; always append a new dated entry.
- Skills that run assessments (`/learn` Phase 2, `/assess`, `/evaluate` Phase 2, `/plan regenerate`) MUST write an entry here. The prose version goes to `assessments/latest.md` (with the prior latest rotated to archive by `/housekeep`).
- `/evaluate` reads this file for Bloom's-level-over-time analysis. Without it, evaluation can only compare initial vs current, not trajectory.
- Not housekept. Routine skills read tail-N; only `/evaluate` reads the full series.

### `learningWithBodhi/<project>/.bodhi/resources.md`

Markdown log. Dated sections or status-grouped sections (as `/resources list` produces). No fixed JSON schema. Small; not housekept.

### `learningWithBodhi/.bodhi-profile.json`

Cross-project learner profile. Shared across all projects under the same `learningWithBodhi/` root. **Split layout in v2:** `.bodhi-profile.json` holds top-level fields; `.bodhi-profile.projects.json` holds the project list.

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
    "totalProjects": 0
  },
  "patterns": {
    "persistentChallenges": ["<topic>"],
    "consistentStrengths": ["<topic>"]
  },
  "lastUpdated": "ISO-8601"
}
```

Routine skills load this small file (~1-2 KB at typical use). No `activeProjects` array here in v2.

### `learningWithBodhi/.bodhi-profile.projects.json`

Per-project metadata. Grows with project count. Loaded only by skills that need cross-project context. Version pinned to `2` for cohort consistency with all other 1.7.0 v2 files — the file did not exist in v1, but the version field denotes schema-family generation (v2), not per-file iteration count.

```json
{
  "version": 2,
  "activeProjects": [
    {
      "name": "string",
      "topic": "string",
      "startedAt": "YYYY-MM-DD",
      "currentPhase": "string",
      "currentModule": "string",
      "bloomLevel": 0,
      "pace": "string",
      "status": "string",
      "trackPurpose": "string"
    }
  ],
  "completedProjects": [
    {
      "name": "string",
      "completedAt": "YYYY-MM-DD",
      "finalBloomLevel": 0,
      "trackPurpose": "string"
    }
  ]
}
```

Skills that write to the profile (across both files):
- `/learn` — initialize/update on project start; append to `.bodhi-profile.projects.json.activeProjects`; bump `cumulativeStats.totalProjects` in `.bodhi-profile.json`.
- `/mentor` — career goal, learning style, chosen path (`.bodhi-profile.json` only).
- `/reflect` — increment `cumulativeStats.totalSessions` (`.bodhi-profile.json`).
- `/practice` — increment `cumulativeStats.totalExercises` (`.bodhi-profile.json`).
- `/teach` — increment `cumulativeStats.totalConceptsLearned` when a concept reaches Bloom's 3+ (`.bodhi-profile.json`).
- `/evaluate` — append topics to `patterns.persistentChallenges` or `patterns.consistentStrengths`; bump `totalMilestonesReached`; move a project from `activeProjects` to `completedProjects` if complete.

Skills MUST read before writing and MUST NOT overwrite fields they did not modify.

## Schema Versioning

Schemas evolve. Skills MUST tolerate older `version` values via inline migration. The full migration table and one-shot conversion procedure live in the `state-migration` KB (loaded by `/housekeep migrate`).

Skills MUST NOT branch behavior on version (no "if v1 do X else do Y" littered through prose).

## Update Rules

- Skills MUST read before writing, never blind-overwrite.
- Skills MUST preserve unknown fields when writing (forward compatibility).
- Skills MUST NOT introduce new top-level fields without updating this KB first.
- Skills MUST NOT introduce new directories or files under `.bodhi/` without updating this KB first.
- Skills MUST NOT stuff long narrative into JSON fields. Narrative belongs in `progress.md` (sessions) or `assessments/latest.md` (assessments).
- `version` is incremented only when a breaking change to shape is introduced; readers MUST tolerate older versions per the `state-migration` KB.
- Skills that read archive content MUST announce the read in their turn output. The learner never has hidden context pulled on their behalf.
- Only `/bodhikit:housekeep` rotates files, writes archive entries, or rewrites summary blocks. Other skills append to live docs only.
