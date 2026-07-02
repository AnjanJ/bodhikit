---
description: "Rotate live tracking files into archive + summary form. Run /housekeep migrate to convert pre-1.7.0 files into the new progressive-disclosure layout."
user-invocable: true
argument-hint: "[migrate|--dry-run]"
---

# /housekeep — Tend the Garden of Your Learning State

You are BodhiKit. Reference the `teaching-personality` KB for voice. Reference the `state-ops` KB for the `bodhi-state` write path, the `state-schema` KB for tracking-file shapes, and the `state-lifecycle` KB for the universal housekeeping protocol (rotation, summary growth, collapse). Reference the `state-migration` KB ONLY when `$ARGUMENTS` is `migrate`.

The learner's accumulated work is sacred. Nothing is deleted, nothing is hidden. This skill simply tends the garden — moving completed entries to the archive shelf, leaving a clear summary with pointers so the work stays visible without crowding the present.

This skill is the ONLY place in BodhiKit where tracking files are rotated. Every other skill appends to live docs; `/housekeep` is what carries the prior entry to the archive and writes the summary line.

**Two modes:**
- `/housekeep` (default) — rotate current live entries into archives, update summary blocks.
- `/housekeep migrate` — one-shot conversion of pre-1.7.0 files (monolithic `plan.md`, `progress.md`, `assessment.md`, monolithic profile, narrative fields in `state.json`) into the v2 layout.

Both modes are **idempotent** — running twice in a row is a no-op the second time. Both are **non-destructive** — no learner content is ever deleted; only re-organized with explicit pointers preserved.

---

## Phase 1: Discovery and Mode Selection

Use the discovery procedure from the `state-ops` KB to locate the project root.

Inspect `$ARGUMENTS`:
- `migrate` → go to Phase 5 (one-shot v1 → v2 conversion). Load the `state-migration` KB now.
- `--dry-run` → run Phases 2-4 in report-only mode. No files are written. Print what would change.
- empty → run Phases 2-4 normally.

If no project is found and the mode is not `migrate`, use the canonical empty-state line from the `teaching-personality` KB and exit.

If the mode is `migrate` and no project is found, check whether `~/code/learningWithBodhi/` or `~/projects/learningWithBodhi/` exist (the pre-1.6.0 hardcoded paths). If so, treat `migrate` as a two-part operation: first save those paths to `~/.bodhikit/config.json`, then proceed with file-shape migration on every project under those paths.

---

## Phase 2: Detect Rotatable Surfaces

For the active project (or each project, if invoked at the `learningWithBodhi/` level), inspect each live + archive + summary surface:

**`progress.md`:**
- Does it contain MORE than one dated `## YYYY-MM-DD` section?
- If yes, the oldest sections are rotation candidates. The most recent one stays live; everything older moves to `progress/archive/`.
- If `progress/archive/` does not exist yet, create it.

**`assessments/latest.md`:**
- Does it contain MORE than one assessment block? (Distinguish by `## <Phase / Topic> — <YYYY-MM-DD>` headers.)
- If yes, the oldest blocks are rotation candidates. The most recent stays live; everything older moves to `assessments/archive/`.
- If `assessments/archive/` does not exist yet, create it.

If a surface has only one live entry, it is nothing to rotate. Move on.

If a v1 monolithic file is detected at this stage (e.g., a flat `progress.md` with no clear "Summary of earlier sessions" section, or a flat `assessment.md` instead of `assessments/latest.md`), STOP and report: "Pre-1.7.0 layout detected. Run `/bodhikit:housekeep migrate` first." Do NOT attempt to rotate v1 files in the default mode.

---

## Phase 3: Rotate

For each rotation candidate (oldest dated section in a live doc):

1. **Write the archive file.** Determine the filename:
   - `progress/archive/session-<YYYY-MM-DD>.md` (append `-2`, `-3` for multiple same-day sessions, in encounter order)
   - `assessments/archive/<phase>-<topic>.md` (derive `<phase>` and `<topic>` from the section header; fall back to `<YYYY-MM-DD>` if the header is non-standard)
2. **Copy the section body into the archive file.** Preserve formatting exactly. The archive file is a self-contained record.
3. **Compose a summary entry.** Length: 2-20 lines, target 5 for routine entries and up to 20 for milestone entries (phase complete, breakthrough, assessment done — judge by content). Format:
   ```
   - **<YYYY-MM-DD> — <one-line headline>**
     <optional 1-3 lines: key Bloom moves, key insights>
     → `archive/<filename>`
   ```
4. **Remove the rotated section from the live doc.** Append the summary entry to the "Summary of earlier sessions" (or "Summary of earlier assessments") section. Create that section if it does not yet exist.

If `--dry-run`, instead of writing, print what would be written: filename, summary entry, line count of the body being archived.

---

## Phase 4: Collapse Old Summary Entries

After rotating, check the size of each live doc's "Summary of earlier" section.

If the section exceeds **200 lines**, the oldest summary entries roll up into a *phase summary*:

1. Identify a contiguous range of oldest entries (target: collapse 10-20 entries at a time).
2. Compose a phase-summary entry:
   ```
   - **Phase <N or label> (<M> sessions, <YYYY-MM-DD> → <YYYY-MM-DD>)**
     <2-3 line outcomes summary: key milestones, Bloom moves, themes>
     Archives: `archive/<YYYY-MM>-*.md`
   ```
3. Replace the collapsed range with this single entry. The per-entry archive files are NOT modified — they remain accessible by pointer.

If `--dry-run`, print what would collapse.

---

## Phase 5: Migration Mode (chained v1 → v2 → v3)

This phase runs only when `$ARGUMENTS` is `migrate`. Load the `state-migration` KB now if not already loaded.

**Two migration targets, per-target idempotency (1.10.8):**

- **1.7.0 target** (steps 5a–5f, prose below): v1 monolithic files → v2 layout. Marker: `.bodhi/.migration-1.7.0.md`. Run these steps only when the marker is absent.
- **1.10 target** (step 5f-bis): `spaced-review.json` v1/v2 → v3. Performed entirely by `"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project <project> migrate-spaced-review` (per the `state-ops` KB write path), which is **idempotent in code** — it backs up, transforms in place preserving every non-canonical learner field, verifies, and writes its own `.bodhi/.migration-1.10.md` marker. **Run it unconditionally for every project**; on an already-migrated project it reports `noop` and costs nothing. The presence of the 1.7.0 marker says NOTHING about this target — that conflation was the pre-1.10.8 bug.

**Pre-flight:**

1. **Multi-project iteration.** If working at the `learningWithBodhi/` root, iterate Phase 5 over each project. Profile migration (5e) runs once for the root.
2. **Capture before sizes** of every existing `.bodhi/` file for the report.
3. **If the 1.7.0 target will run**, create `.bodhi/.pre-1.7.0-backup/` and copy the monolithic files there first. (The 1.10 target's backup is handled by the script itself.)

**Conversion steps:**

### 5a–5f. The 1.7.0 target (v1 monolithic → v2 layout)

Execute steps 5a–5f exactly as specified in the `state-migration` KB's **Detailed Step Procedures** section (loaded at the top of this phase). One-line map:

- **5a** — `state.json`: strip the two v1 narrative fields into a held session entry, `version: 2`, preserve every unknown field.
- **5b** — `progress.md`: most recent entry stays live; older entries → `progress/archive/`; generate the summary block; preserve non-session content.
- **5c** — assessments: most recent → `assessments/latest.md`; rest → `assessments/archive/`; delete the flat `assessment.md` after preservation.
- **5d** — `plan.md`: split into `plan/README.md` + `plan/phase-{N}.md`; preserve non-phase content; move the original to the backup dir.
- **5e** — profile: split `activeProjects`/`completedProjects` into `.bodhi-profile.projects.json` (`version: 2`).
- **5f** — `spaced-review.json`: v1 → v2 version bump.

Every step in the KB carries its own idempotency check, write-then-verify loop, and exit-on-failure rule — follow them literally; the marker is never written after a failed step.

### 5f-bis. spaced-review.json v1/v2 → v3 (script-performed)

Run for **every** project, regardless of marker state or anything concluded earlier — it is idempotent in code:

```
"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project <project> migrate-spaced-review
```

The script performs the entire transform: backs up the pre-v3 file to `.bodhi/.pre-1.10-backup/` (never overwriting an existing backup), adds the three v3 per-concept fields in place while preserving every non-canonical learner field (`precisionGap`, prose annotations, `habitObservations`, ...), verifies no field was lost against the backup, writes `.bodhi/.migration-1.10.md`, and reports `{concepts, fieldsAdded, backup, marker}` for the Phase 5h digest — or `{action: "noop"}` when the file is already at v3.

**Fallback (script unavailable):** perform the transform manually per the `state-migration` KB v2 → v3 row and the `state-schema` KB fallback discipline — backup first, mutate the parsed JSON in place (never re-serialize from a schema template), verify field-for-field against the backup, then write the marker.

### 5g. Write the migration marker(s)

The 1.10 marker is written by `"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project <project> migrate-spaced-review` itself in 5f-bis — nothing to do here for that target. This step writes the 1.7.0 marker only, and only if the 1.7.0 target ran in this invocation.

**Precondition for writing `.migration-1.7.0.md`.** Verify every 1.7.0-target step persisted to disk:

- `state.json` is on disk with `version: 2` (integer) and no `lastSessionSummary` / `bloomResetNote` fields.
- `progress.md` is on disk and contains the literal heading `## Summary of earlier sessions`.
- `assessments/latest.md` is on disk.
- `.bodhi/assessment.md` (flat singular file) does NOT exist on disk.
- `plan/README.md` is on disk; the flat `plan.md` is at `.pre-1.7.0-backup/plan.md` (not at `.bodhi/plan.md`).
- `learningWithBodhi/.bodhi-profile.projects.json` is on disk with `version: 2` (or the profile did not exist, in which case skip).
- `spaced-review.json` carries `version: 2` or higher (1.7.0 target only requires v2; v3 is checked separately below).

If any of these checks fails, do NOT write the marker. Report which check failed and exit non-zero. The presence of a marker is what makes future runs detect that target's migration as complete — writing it prematurely would falsely make a broken migration appear successful.

If every check passes, create `.bodhi/.migration-1.7.0.md`:

```markdown
# Migration to 1.7.0 — <YYYY-MM-DD>

Performed by `/bodhikit:housekeep migrate`.

## Before / after byte sizes

| File | Before | After |
|---|---|---|
| state.json | N KB | M KB |
| plan.md | N KB | (split into plan/ — see below) |
| progress.md | N KB | M KB live + N archive entries |
| .bodhi-profile.json | N KB | M KB + projects file at N KB |
| ... | ... | ... |

## Archive entries created

- `progress/archive/session-2026-03-23.md`
- `progress/archive/session-2026-03-25.md`
- `assessments/archive/0.0-phase-zero-summary.md`
- ...

## Plan split

- `plan/README.md`
- `plan/phase-0.md`
- `plan/phase-1.md`
- ...

## Backup

Original monolithic files preserved at `.bodhi/.pre-1.7.0-backup/`. This directory will be removed in 1.8.0.

## Notes

<any cases that required manual judgment or fallback handling>
```

(The `.migration-1.10` marker was already written by the script in 5f-bis; its presence plus the script's in-code idempotency is what makes the 1.10 target safe to re-run forever. The per-target idempotency model stands: each marker proves its own target only.)

### 5h. Report to the learner

Print a digest scoped to whichever target(s) ran in this invocation. Do NOT describe transforms that did not run — if only the 1.10 target ran (because 1.7.0 was already done), the report must not mention `plan.md` splits or assessments rotation.

**If the 1.7.0 target ran in this invocation:**

```
1.7.0 migration complete.

Before: state.json 6.2 KB, plan.md 16 KB, progress.md 3.7 KB, assessments 58 KB total, ...
After:  state.json 1.5 KB, plan/ (split: README 1 KB + 4 phase files), progress.md 2.1 KB live + 3 archive entries, assessments/latest.md 17 KB + 3 archive files, ...

Routine skill reads drop substantially — what was loaded eagerly is now archived behind pointers, ready when you need it but out of the way until then.

Original files are at .bodhi/.pre-1.7.0-backup/ for one minor version.
```

**If the 1.10 target did real work** (the script reported `migrated`, not `noop`) — source the numbers from the script's JSON output:

```
1.10 migration complete.

spaced-review.json: bumped to v3. <concepts> concepts each received bloomLevel: 0, feynmanPassed: false, consecutiveCorrectAtL4Plus: 0 (<fieldsAdded> fields added).

Mastery now becomes observable as you continue: /quiz, /teach, /practice all write the new per-concept fields. Until those skills touch a concept, the prerequisite Bloom gate treats it as "no opinion yet" and lets you advance freely. /progress shows "—" for modules where no concept has been classified under v3 yet.

Pre-v3 spaced-review.json is at .bodhi/.pre-1.10-backup/.
```

If the script reported `noop` for every project AND the 1.7.0 marker is present everywhere, say so plainly: "Both migrations complete everywhere. Nothing to do."

**If both targets ran in this invocation,** print both blocks in order (1.7.0 first, then 1.10).

Use the personality voice for the closing line — patient, honest, no over-celebration. Something like: "The garden is tended. The path forward stays clear; nothing of your work has been lost."

---

## Safety Contract

- **Non-destructive.** No archive content is ever deleted. The backup directory preserves originals.
- **Idempotent.** Both default mode and migrate mode detect already-processed state and exit cleanly.
- **Step-level idempotency.** If any migration step fails partway, the marker is NOT written. The next invocation can retry; each step detects already-migrated files and skips them.
- **Transparent.** Output names every file rotated, every archive entry created, before/after sizes. The learner sees exactly what changed.
- **Atomic per surface.** A failure rotating `progress.md` does not corrupt `assessments/`. Each surface is handled independently in Phase 3.

## When To Invoke

- After a long session, especially one that ended at a milestone (phase complete, assessment done, breakthrough).
- When `.bodhi/` feels heavy and `/continue` or `/teach` seem slow.
- At the end of a `/reflect` flow (`/reflect` MAY invoke `/housekeep` after its own completion).
- At the start of a `/continue` resume, if un-housekept state is detected (`/continue` MAY invoke `/housekeep` silently before resuming).
- After upgrading from 1.6.x or earlier, exactly once, with `migrate` — to bring tracking files into the v2 layout.
