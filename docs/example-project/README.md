# Example Learning Project

This is a sample BodhiKit learning project showing what the `.bodhi/` tracking files look like after a few sessions. This is NOT a real project — it exists to help you understand the structure.

In a real project, these files are created and updated automatically by BodhiKit skills. You never need to edit them manually.

The layout below reflects the v2 schema introduced in 1.7.0 (live + archive + summary for narrative surfaces, sectional plan, slim state). Pre-1.7.0 projects are converted by `/bodhikit:housekeep migrate`.

## Files

### Live surfaces (loaded by routine skills)

| File | Purpose |
|------|---------|
| `.bodhi/state.json` | Slim — current position, session counts, streak. **No long narrative.** |
| `.bodhi/progress.md` | Live document: latest session entry + "Summary of earlier sessions" block with pointers. |
| `.bodhi/plan/README.md` | Arc overview, phase titles, current-phase pointer. |
| `.bodhi/plan/phase-{N}.md` | Per-phase detailed plan. Routine skills load only the current phase. |
| `.bodhi/assessments/latest.md` | Most recent assessment + summary of earlier assessments with pointers. |
| `.bodhi/spaced-review.json` | Leitner box system for concept retention. |
| `.bodhi/assessment-history.json` | Structured Bloom's-over-time data for `/evaluate` trajectory analysis. |
| `.bodhi/resources.md` | Curated learning resources. |

### Archived surfaces (loaded only when justified)

| Path | Purpose |
|------|---------|
| `.bodhi/progress/archive/session-<YYYY-MM-DD>.md` | Full text of each archived session. Reached via pointers in `progress.md`'s summary block. |
| `.bodhi/assessments/archive/<name>.md` | Full text of each archived assessment. Reached via pointers in `assessments/latest.md`. |

The canonical shape of every file lives in `knowledge/state-schema/SKILL.md`. The universal housekeeping protocol that rotates live entries to archive lives in the same KB. Schema versioning and one-shot migration live in `knowledge/state-migration/SKILL.md`.

## Discovery

BodhiKit finds your learning projects via:

1. Per-project: `<repo>/.bodhikit/config.json` (if you keep `.bodhi/` somewhere other than `learningWithBodhi/`)
2. Global: `~/.bodhikit/config.json` (`searchPaths` array)
3. Defaults: current directory (with parent walk) and `~/learningWithBodhi`
