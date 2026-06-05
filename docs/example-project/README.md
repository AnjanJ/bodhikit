# Example Learning Project

This is a sample BodhiKit learning project showing what the `.bodhi/` tracking files look like after a few sessions. This is NOT a real project — it exists to help you understand the structure.

In a real project, these files are created and updated automatically by BodhiKit skills. You never need to edit them manually.

## Files

| File | Purpose |
|------|---------|
| `.bodhi/state.json` | Current position, session history, streak |
| `.bodhi/plan.md` | Personalized learning plan |
| `.bodhi/progress.md` | Per-module progress with Bloom's levels |
| `.bodhi/spaced-review.json` | Leitner box system for concept retention |
| `.bodhi/assessment.md` | Human-readable assessment journal |
| `.bodhi/assessment-history.json` | Structured assessment data (Bloom's-over-time for `/evaluate`) |
| `.bodhi/resources.md` | Curated learning resources |

The canonical shape of every file lives in `knowledge/state-schema/SKILL.md`.

## Discovery

BodhiKit finds your learning projects via:

1. Per-project: `<repo>/.bodhikit/config.json` (if you keep `.bodhi/` somewhere other than `learningWithBodhi/`)
2. Global: `~/.bodhikit/config.json` (`searchPaths` array)
3. Defaults: current directory (with parent walk) and `~/learningWithBodhi`
