---
description: "Canonical schema for BodhiKit tracking files (state.json, spaced-review.json, progress.md, .bodhi-profile.json) and discovery config"
user-invocable: false
---

# State Schema — Canonical Shape of BodhiKit Tracking Files

All skills that read or write `.bodhi/` tracking files reference this KB. Skills MUST NOT redeclare these shapes inline.

If a field is not listed here, do not add it. If a new field is genuinely needed, update this KB first, then the skills that touch it.

## Project Discovery Config

**Location:** `~/.bodhikit/config.json`. Optional — if absent, defaults apply.

```json
{
  "searchPaths": ["$PWD", "~/learningWithBodhi"]
}
```

- `$PWD` is resolved at runtime to the current working directory; parent directories up to 3 levels are also searched.
- `~/learningWithBodhi` is the canonical user home.
- Additional paths can be added by the user. Skills MUST NOT hardcode paths beyond these defaults.

**Discovery procedure (all skills use this exact procedure):**

1. Read `~/.bodhikit/config.json` if it exists; otherwise use the defaults above.
2. For each path in `searchPaths`, look for `learningWithBodhi/` directories.
3. Within each, list subdirectories containing `.bodhi/state.json`.

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
    "totalExercises": 0
  },
  "lastUpdated": "ISO-8601"
}
```

## `learningWithBodhi/<project>/.bodhi/assessment.md` and `resources.md`

Markdown logs. No fixed schema beyond dated sections (`## YYYY-MM-DD`).

## Update Rules

- Skills MUST read before writing, never blind-overwrite.
- Skills MUST preserve unknown fields when writing (forward compatibility).
- Skills MUST NOT introduce new top-level fields without updating this KB first.
- `version` is incremented only when a breaking change to shape is introduced; readers MUST tolerate older versions.
