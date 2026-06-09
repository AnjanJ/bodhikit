---
description: "Schema migration table and one-shot v1 → v2 conversion procedure for BodhiKit tracking files. Loaded by /bodhikit:housekeep migrate."
user-invocable: false
---

# State Migration — Schema Versioning and One-Shot Conversion

This KB documents how BodhiKit tracking files evolve across versions, and the exact transforms `/bodhikit:housekeep migrate` performs to bring pre-1.7.0 user data into the current shape.

See also: `state-schema` KB (current file shapes), `read-defaults` KB (per-skill read contract).

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

## One-Shot Conversion Procedure (`/housekeep migrate`)

`/housekeep migrate` is invoked explicitly by the learner. It is **idempotent** (running twice in a row is a no-op the second time) and **non-destructive** (no archive content is lost; only re-organized).

**Procedure:**

1. **Detect project root.** Use discovery from `state-schema` KB.
2. **Check migration marker.** If `.bodhi/.migration-1.7.0.md` exists, exit cleanly with "Already migrated on <date>. Nothing to do."
3. **Pre-flight snapshot.** Record current byte sizes of all `.bodhi/` files. This will be reported back to the learner.
4. **Apply migrations in this order:**
   1. `state.json` v1 → v2: extract `lastSessionSummary` and `bloomResetNote` into a temporary buffer.
   2. `progress.md` v1 → v2: parse dated `## YYYY-MM-DD` sections; keep the most recent; move others into `progress/archive/`; append the temp buffer from step (1) as the most recent session if it represents content not already in `progress.md`; generate the "Summary of earlier sessions" block from archived sections.
   3. `assessment.md` / `assessments/*.md` v1 → v2: identify the most-recent assessment file; copy/move it to `assessments/latest.md`; move other assessment files to `assessments/archive/`; generate the summary block.
   4. `plan.md` v1 → v2: parse `## Phase {N}` headings; write one `plan/phase-{N}.md` per phase; generate `plan/README.md` as the arc index; remove the original `plan.md` after writing the splits.
   5. `.bodhi-profile.json` v1 → v2: split into `.bodhi-profile.json` (top-level + cumulativeStats + patterns) and `.bodhi-profile.projects.json` (activeProjects + completedProjects). Migrate `totalProjects` into `cumulativeStats.totalProjects` if present.
   6. `spaced-review.json` v1 → v2: bump version. No data change; existing files already carry `question` and `lastResult` per concept in real data.
5. **Write migration marker.** Create `.bodhi/.migration-1.7.0.md` containing: date, before/after byte sizes per file, list of archive files created, list of summary blocks generated.
6. **Report to learner.** Print a clear before/after summary:
   ```
   Migration complete.

   Before: state.json 6.2 KB, plan.md 16 KB, progress.md 3.7 KB, ...
   After:  state.json 1.5 KB, plan/ (split: README 1 KB + 6 phase files),
           progress.md 2.1 KB live + 3 archive entries, ...

   Total: 73 KB → 14 KB live + 59 KB archive. Routine skill reads drop by ~80%.
   Archive content is permanent and accessible via pointers in live docs.
   ```

**Safety:**
- All archive content is preserved; no learner data is deleted.
- A `.bodhi/.pre-1.7.0-backup/` directory holds the original monolithic files for one minor version (removed in 1.8.0).
- If any step fails partway, the marker is NOT written, and the next invocation can retry from the failed step (each migration step is itself idempotent — already-migrated files are detected and skipped).

## Adding a Future Migration

1. Bump the file's `version` field default in `state-schema` KB.
2. Add a row to the Migration Table above with the explicit before→after transform.
3. Document in CHANGELOG which release introduced the bump.
4. If the migration requires a one-shot conversion (not just in-memory tolerance), extend `/housekeep migrate` with the new step and document it in the procedure.
5. Do NOT delete old migration rows. They accumulate; a v1 file may need to walk v1→v2→v3.
