---
description: "Canonical schema for BodhiKit tracking files, discovery config (global + per-project), migration rules, and structured assessment history"
user-invocable: false
---

# State Schema — Canonical Shape of BodhiKit Tracking Files

All skills that read or write `.bodhi/` tracking files reference this KB. Skills MUST NOT redeclare these shapes inline.

If a field is not listed here, do not add it. If a new field is genuinely needed, update this KB first, then the skills that touch it.

See also: `spaced-repetition` KB (box→interval mapping and update rules).

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

**Legacy path detection (one-time migration help):** If discovery finds projects under `~/code/learningWithBodhi` or `~/projects/learningWithBodhi` (pre-1.6.0 hardcoded paths) AND no `~/.bodhikit/config.json` exists, `/status` SHOULD emit a single-line notice the first time it runs: "Found projects at <path>. Run `/bodhikit:status migrate` to save these as search paths so discovery keeps finding them." This notice is one-shot — write `~/.bodhikit/config.json` with the detected path appended to `searchPaths` after the user confirms.

## `learningWithBodhi/<project>/.bodhi/state.json`

```json
{
  "version": 1,
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
  "lastSessionSummary": "string",
  "initialBloomLevel": { "<sub-topic>": 0 },
  "overallCompletion": 0
}
```

- `currentStreak`: consecutive days. Reset to 1 if `sessionDates` gap exceeds 1 day.
- `overallCompletion`: 0–100, integer. Calculated from modules completed.
- `lastSessionSummary`: 1–2 sentences. Trim aggressively.

## `learningWithBodhi/<project>/.bodhi/spaced-review.json`

```json
{
  "version": 1,
  "lastReviewCheck": "ISO-8601",
  "concepts": [
    {
      "name": "string",
      "box": 1,
      "nextReview": "YYYY-MM-DD",
      "lastReviewed": "YYYY-MM-DD",
      "reviewHistory": [
        { "date": "YYYY-MM-DD", "result": "correct|incorrect|partial" }
      ]
    }
  ]
}
```

- `box`: integer 1–5. Box→interval mapping is defined in the `spaced-repetition` KB. Skills MUST NOT redeclare intervals.
- New concept: `box: 1`, `nextReview: tomorrow`.
- Correct recall: `box` up one (max 5), recompute `nextReview` from the spaced-repetition table.
- Incorrect recall or learner-initiated `/forget`: `box: 1`, `nextReview: tomorrow`.

## `learningWithBodhi/<project>/.bodhi/progress.md`

Markdown, not JSON. Structure:

```markdown
## <Module Name>
- Status: not-started | in-progress | completed
- Bloom's Level: <0–6>
- Mastery: <0–100>%
- Concepts covered: <comma-separated list>
- Last touched: <YYYY-MM-DD>
```

One section per module. Append-only history is kept at the bottom under `## History` with dated entries.

## `learningWithBodhi/<project>/.bodhi/assessment.md`

Human-readable prose log. Dated `## YYYY-MM-DD` sections. The journal a learner reads when they want to see their own story.

## `learningWithBodhi/<project>/.bodhi/assessment-history.json`

Structured assessment data for analytical skills like `/evaluate` and `/progress`. Parallel to `assessment.md`, not a replacement.

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
- Skills that run assessments (`/learn` Phase 2, `/assess`, `/evaluate` Phase 2, `/plan regenerate`) MUST write an entry here. `assessment.md` gets the prose version of the same data.
- `/evaluate` reads this file for Bloom's-level-over-time analysis. Without it, evaluation can only compare initial vs current, not trajectory.

## `learningWithBodhi/<project>/.bodhi/resources.md`

Markdown log. Dated sections or status-grouped sections (as `/resources list` produces). No fixed JSON schema.

## `learningWithBodhi/.bodhi-profile.json`

Cross-project learner profile. Shared across all projects under the same `learningWithBodhi/` root.

```json
{
  "version": 1,
  "careerGoal": "string",
  "whyLearning": "string",
  "priorExperience": "string",
  "learningStyle": "string",
  "overallBloomLevels": { "<area>": 0 },
  "totalProjects": 0,
  "activeProjects": ["<projectName>"],
  "completedProjects": ["<projectName>"],
  "cumulativeStats": {
    "totalSessions": 0,
    "totalExercises": 0,
    "totalConceptsLearned": 0,
    "totalMilestonesReached": 0
  },
  "patterns": {
    "persistentChallenges": ["<topic>"],
    "consistentStrengths": ["<topic>"]
  },
  "lastUpdated": "ISO-8601"
}
```

Skills that write to this file:
- `/learn` — initialize/update on project start; bump `totalProjects`, append to `activeProjects`.
- `/mentor` — career goal, learning style, chosen path.
- `/reflect` — increment `cumulativeStats.totalSessions` on session end (one per session per project).
- `/practice` — increment `cumulativeStats.totalExercises` on exercise completion.
- `/teach` — increment `cumulativeStats.totalConceptsLearned` when a concept reaches Bloom's 3+.
- `/evaluate` — append topics to `patterns.persistentChallenges` (3+ assessments at Bloom's <3) or `patterns.consistentStrengths` (3+ assessments at Bloom's 4+); bump `totalMilestonesReached`; move project from `activeProjects` to `completedProjects` if complete.

Skills MUST read before writing and MUST NOT overwrite fields they did not modify.

## Migration (Forward-Compatible Reads)

Schemas evolve. Skills MUST tolerate older `version` values via inline migration:

**Pattern (all read paths):**

1. Read the file.
2. If `version` is missing, treat as `version: 0`.
3. If `version` < the current version declared here, apply the migration steps below in order until you reach current. Migrate in memory; persist the migrated shape only when the skill is about to write anyway.
4. Use the migrated shape.

**Migration steps:**

| File | From → To | Steps |
|---|---|---|
| (none yet) | — | Schemas are at v1 as of 1.6.0. First migration entry lands here when v2 ships. |

**Adding a migration:**

1. Bump the file's `version` field default in this KB.
2. Add a row above with the explicit before→after transform (e.g., "rename `oldField` to `newField`; default missing `newField` to X").
3. Document in CHANGELOG which release introduced the bump.
4. Do NOT delete old migration rows. They accumulate; a v1 file may need to walk v1→v2→v3.

Skills MUST NOT branch behavior on version (no "if v1 do X else do Y" littered through prose). All version handling lives in the read-time migration step above.

## Update Rules

- Skills MUST read before writing, never blind-overwrite.
- Skills MUST preserve unknown fields when writing (forward compatibility).
- Skills MUST NOT introduce new top-level fields without updating this KB first.
- `version` is incremented only when a breaking change to shape is introduced; readers MUST tolerate older versions per the Migration section.
