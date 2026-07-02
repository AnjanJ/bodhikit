---
description: "Schema migration table and one-shot v1 → v2 conversion procedure for BodhiKit tracking files. Loaded by /bodhikit:housekeep migrate."
user-invocable: false
---

# State Migration — Schema Versioning and One-Shot Conversion

This KB documents how BodhiKit tracking files evolve across versions, and the exact transforms `/bodhikit:housekeep migrate` performs to bring pre-1.7.0 user data into the current shape.

See also: `state-schema` KB (current file shapes), `state-ops` KB (write path and discovery).

## Forward-Compatible Reads (Always)

Schemas evolve. Skills MUST tolerate older `version` values via inline migration:

**Pattern (all read paths):**

1. Read the file.
2. If `version` is missing, treat as `version: 0`.
3. If `version` < the current version declared in `state-schema`, apply the migration steps below in order until you reach current. Migrate in memory; persist the migrated shape only when the skill is about to write anyway.
4. Use the migrated shape.

Skills MUST NOT branch behavior on version (no "if v1 do X else do Y" littered through prose). All version handling lives in the read-time migration step above.

## Migration Table

| File | From → To | Steps |
|---|---|---|
| `state.json` | v1 → v2 | Strip `lastSessionSummary` and `bloomResetNote`. Their content has been migrated to `progress.md` by `/housekeep migrate`. If the v1 file is still present (no migration run yet), in-memory readers MUST treat these fields as absent and rely on `progress.md` for narrative. Persist v2 shape on next write. |
| `progress.md` | v1 (monolithic) → v2 (live + archive + summary) | One-shot conversion done by `/housekeep migrate`: latest dated section stays in `progress.md`; older dated sections move into `progress/archive/session-<YYYY-MM-DD>[-N].md`; new "Summary of earlier sessions" block generated with pointers. |
| `assessment.md` / `assessments/*.md` | v1 (free) → v2 (live + archive + summary) | One-shot by `/housekeep migrate`: most recent assessment becomes `assessments/latest.md`; older files move to `assessments/archive/`; summary block generated. Multi-stack projects already using an `assessments/` subdirectory have files redistributed into `latest.md` + `archive/`. |
| `plan.md` | v1 (monolithic) → v2 (sectional) | One-shot by `/housekeep migrate`: split on `## Phase {N}` headings into `plan/phase-{N}.md`; generate `plan/README.md` as an arc index pointing to each phase file. Original `plan.md` removed after split. |
| `.bodhi-profile.json` | v1 (monolithic) → v2 (split) | One-shot by `/housekeep migrate`: keep top-level fields and `cumulativeStats` + `patterns` in `.bodhi-profile.json`; move `activeProjects` and `completedProjects` arrays into `.bodhi-profile.projects.json`. Move `totalProjects` (formerly top-level) into `cumulativeStats.totalProjects`. |
| `spaced-review.json` | v1 → v2 | Add `question` and `lastResult` fields per concept if absent (no-op data-wise; just shape declaration to match observed real-data usage). Persist v2 shape on next write. |
| `spaced-review.json` | v2 → v3 | For each entry in `concepts[]`, add `bloomLevel: 0`, `feynmanPassed: false`, `consecutiveCorrectAtL4Plus: 0` if absent. `reviewHistory[]` entries without a `bloomLevel` field remain valid (readers treat absent as `0`); only new entries written post-v3 include it. Bump `version` to 3. **Legacy fallthrough (1.10.7-corrected):** a concept with `bloomLevel: 0` has not been classified by any v3 writer — regardless of `lastReviewed`. Skills checking prerequisite Bloom gates MUST treat `bloomLevel: 0` as "no opinion, allow advancement"; `/progress` Mastery % displays `—` for modules where every concept has `bloomLevel: 0`. Once any v3 writer sets `bloomLevel > 0`, normal logic applies to that concept. The 1.10.0 rule that required `lastReviewed: null` for fallthrough was wrong — real v2 data routinely has populated `lastReviewed` from pre-v3 quizzes. |

## Detailed Step Procedures — 1.7.0 target (`/housekeep migrate` steps 5a–5f)

`/housekeep migrate` is invoked explicitly by the learner. The 1.7.0 target is **idempotent** (each step detects already-migrated files and skips) and **non-destructive** (no learner content lost; `.bodhi/.pre-1.7.0-backup/` holds the originals). The marker file is written only after EVERY step has verified on disk. The v2 → v3 target is separate: `bodhi-state migrate-spaced-review` performs it entirely in code.

### 5a. State narrative extraction (`state.json` v1 → v2)

**Idempotency check.** If `version` is already `2` (number, not string) AND neither `lastSessionSummary` nor `bloomResetNote` is present, skip to 5b.

1. Compose a synthetic session entry from `lastSessionSummary` + `bloomResetNote` if either is present: date = `lastSessionAt` (or `updatedAt`), body = both fields concatenated under a `**Pre-1.7.0 migration note:**` prefix. Hold it in memory for 5b.
2. Construct the new content from the existing parsed JSON: delete the two narrative keys, set `version` to integer `2`. **Preserve every unknown field** — real v1 files carry `goal`, `standalone`, `pace`, `previousModule`, `nextActivity`, `bloomLevels`, and more; only the two narrative fields are removed.
3. Write the file (a real Write call — "remove the field" means rewrite the file to disk), then re-read to verify `version: 2` and the narrative fields absent. On failure: report and exit; never write the marker after a failed step.

If neither narrative field was present, still complete steps 2-3 so `version: 2` reaches disk.

### 5b. `progress.md` → live + archive + summary

**Idempotency check.** If `progress.md` already contains `## Summary of earlier sessions` AND `progress/archive/` has at least one `session-*.md`, skip to 5c.

Parse session entries, trying heading styles in order: (1) top-level dated `## YYYY-MM-DD[ — label]`; (2) hierarchical `## Session Log` + `### Session N[ — date]`; (3) numbered `## Session N` with date in body; (4) fallback — treat the whole file as one archived blob with synthetic date from `state.json`. Prepend the 5a synthetic entry if its date is not already covered.

**Non-session content preservation.** Timeline/Module-Status tables, description paragraphs, front-matter: keep current-state summaries at the bottom of the new live doc; move bulky historical content to `progress/notes.md` with a pointer line.

Single entry → write a new `progress.md` with an empty "Summary of earlier sessions" section appended. Multiple entries → most recent becomes the live head; each older entry written verbatim (heading included) to `progress/archive/session-<YYYY-MM-DD>[-N].md`; compose the summary block (2-5 lines per entry, up to 20 for milestones, derived from each section's Outcomes line or first bullet); write the new `progress.md` (live entry, `---`, summary section, preserved non-session content). Verify by re-reading: summary heading present, latest entry present, at least one archive file exists. On failure: report and exit.

### 5c. `assessment.md` / `assessments/` → live + archive + summary

**Idempotency check.** If `assessments/latest.md` exists AND no flat `.bodhi/assessment.md` exists, skip to 5d.

Detect layout: flat file only (parse dated sub-sections); `assessments/` subdirectory (each file a candidate); both (subdirectory takes precedence). Then: most recent assessment → `assessments/latest.md` (if ≥ 8 KB, write a summary-with-pointer instead and put the full content in the archive); every other assessment → `assessments/archive/<filename>.md` (preserve descriptive filenames, else `<YYYY-MM-DD>-<topic-slug>.md`); append a "Summary of earlier assessments" block with pointers; delete the old flat `.bodhi/assessment.md` (content preserved in archive + backup). Verify: `latest.md` exists with the summary section; flat file gone.

### 5d. `plan.md` → sectional `plan/`

Parse on `## Phase {N}` / `# Phase {N}` headings (colon variants accepted). Each phase section → `plan/phase-<N>.md` with the heading promoted to `#`. Write `plan/README.md` as the arc index (topic, arc/pace from front matter, phase list with pointers, current phase marked from `state.json.currentPhase`). **Preserve non-phase content** (goal/capacity metadata, schedule tables, "Not covering" sections) in `plan/README.md`. Move the original `plan.md` into the backup directory. No `## Phase` headings at all → leave `plan.md` in place, write a one-line `plan/README.md` pointing to it, note the case in the marker.

### 5e. `.bodhi-profile.json` → split

Extract `activeProjects` + `completedProjects` into `learningWithBodhi/.bodhi-profile.projects.json` (**must declare `"version": 2`**, cohort-consistent). Move top-level `totalProjects` into `cumulativeStats.totalProjects`. Bump the parent profile to `version: 2` and write it slimmed (top-level + cumulativeStats + patterns + learnerBackground). Missing profile → no-op.

### 5f. `spaced-review.json` v1 → v2 version bump

If `version` is 1 or missing, bump to 2 and persist. No structural change (real data already carries `question`/`lastResult`).

### Marker preconditions (housekeep step 5g)

Write `.bodhi/.migration-1.7.0.md` only after verifying ALL of: `state.json` at integer `version: 2` with no narrative fields; `progress.md` contains the summary heading; `assessments/latest.md` exists and flat `assessment.md` does not; `plan/README.md` exists and flat `plan.md` is in the backup dir; `.bodhi-profile.projects.json` at `version: 2` (or profile absent); `spaced-review.json` at `version: 2`+. Marker content: date, before/after byte sizes, archive entries created, plan split list, backup location, notes on fallback cases.

## Adding a Future Migration

1. Bump the file's `version` field default in `state-schema` KB.
2. Add a row to the Migration Table above with the explicit before→after transform.
3. Document in CHANGELOG which release introduced the bump.
4. If the migration requires a one-shot conversion (not just in-memory tolerance), extend `/housekeep migrate` with the new step and document it in the procedure.
5. Do NOT delete old migration rows. They accumulate; a v1 file may need to walk v1→v2→v3.
