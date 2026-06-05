---
description: "Rotate live tracking files into archive + summary form. Run /housekeep migrate to convert pre-1.7.0 files into the new progressive-disclosure layout."
user-invocable: true
argument-hint: "[migrate|--dry-run]"
---

# /housekeep — Tend the Garden of Your Learning State

You are BodhiKit. Reference the `teaching-personality` KB for voice. Reference the `state-schema` KB for tracking-file shapes and the universal housekeeping protocol. Reference the `state-migration` KB ONLY when `$ARGUMENTS` is `migrate`.

The learner's accumulated work is sacred. Nothing is deleted, nothing is hidden. This skill simply tends the garden — moving completed entries to the archive shelf, leaving a clear summary with pointers so the work stays visible without crowding the present.

This skill is the ONLY place in BodhiKit where tracking files are rotated. Every other skill appends to live docs; `/housekeep` is what carries the prior entry to the archive and writes the summary line.

**Two modes:**
- `/housekeep` (default) — rotate current live entries into archives, update summary blocks.
- `/housekeep migrate` — one-shot conversion of pre-1.7.0 files (monolithic `plan.md`, `progress.md`, `assessment.md`, monolithic profile, narrative fields in `state.json`) into the v2 layout.

Both modes are **idempotent** — running twice in a row is a no-op the second time. Both are **non-destructive** — no learner content is ever deleted; only re-organized with explicit pointers preserved.

---

## Phase 1: Discovery and Mode Selection

Use the discovery procedure from the `state-schema` KB to locate the project root.

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

## Phase 5: Migration Mode (One-Shot v1 → v2)

This phase runs only when `$ARGUMENTS` is `migrate`. Load the `state-migration` KB now if not already loaded.

**Pre-flight:**

1. Check for the migration marker. If `.bodhi/.migration-1.7.0.md` exists, exit cleanly:
   "Already migrated on <date>. Nothing to do." Show the marker file's path so the learner can inspect it if curious.
2. If working at the `learningWithBodhi/` root (multiple projects), iterate Phase 5 over each project. Profile migration runs once for the root.
3. **Capture before sizes.** Record byte sizes of every existing `.bodhi/` file. These will be reported back.
4. **Create the backup directory.** `.bodhi/.pre-1.7.0-backup/` — copy the unmodified monolithic files here before any conversion. This is removable in 1.8.0 but exists now as a safety net.

**Conversion steps (apply in this exact order, each step idempotent):**

### 5a. State narrative extraction

Read `state.json`. If `lastSessionSummary` or `bloomResetNote` fields are present:
1. Compose a synthetic session entry from them: date = `lastSessionAt` (or `updatedAt` if `lastSessionAt` is absent), body = the concatenation of the two fields with a `**Pre-1.7.0 migration note:**` prefix.
2. Hold this entry in memory for use by step 5b.
3. Remove the two fields from the `state.json` shape. Bump `state.json` `version` to 2.

**Preserve unknown fields.** Real v1 `state.json` files in the wild carry fields from older minor versions (e.g., `goal`, `standalone`, `pace`, `previousModule`, `nextActivity`, `bloomLevels`, `initialBloomLevel`) that the current schema does not declare. The migration MUST preserve every field it does not explicitly strip. Only `lastSessionSummary` and `bloomResetNote` are removed; everything else stays verbatim.

If neither field is present, this step is a no-op (still bump `version` to 2).

### 5b. progress.md → live + archive + summary

Read existing `progress.md`. Parse out session entries. Real v1 files use several heading styles — try them in this order:

1. Top-level dated: `## YYYY-MM-DD` or `## YYYY-MM-DD — <label>`.
2. Hierarchical: a top-level `## Session Log` header followed by `### Session N` or `### Session N — YYYY-MM-DD` entries.
3. Numbered: `## Session N` with a date in the body.
4. Fallback: if none match, treat the whole file as a single archived blob with synthetic date = `state.json.lastSessionAt` or `updatedAt`.

If a synthetic entry was held from step 5a and its date is NOT already covered by an existing section, prepend it to the parsed list as the most recent entry.

**Non-session content preservation.** Real v1 `progress.md` files often contain non-session content at the top: a "Timeline" or "Module Status" table summarizing module completion, a description paragraph, header front-matter. This content MUST be preserved. If it summarizes current state, keep it at the bottom of the new live `progress.md` (after the "Summary of earlier sessions" block). If it is bulky and historical, write it to a sibling file `progress/notes.md` instead, and add a single line in `progress.md` pointing to it.

If the parsed list has only one entry, no archive work needed — just ensure the file has a "Summary of earlier sessions" section (empty for now) appended.

Otherwise:
1. Keep the most recent entry as the new live `progress.md` head.
2. For each older entry, write `progress/archive/session-<YYYY-MM-DD>[-N].md` (sequential `-N` for same-day).
3. Generate a "Summary of earlier sessions" block with one entry per archived session, derived from each section's bullet structure (Outcomes line if present; otherwise first non-empty bullet). Target 2-5 lines per entry; up to 20 for milestone sessions.
4. Replace `progress.md` with: latest-entry header + body, separator (`---`), `## Summary of earlier sessions`, generated entries, optional separator + preserved non-session content.

### 5c. assessment.md / assessments/ → live + archive + summary

Detect the existing assessment layout:
- Flat `assessment.md` only → treat as a single block in v1 format; parse out dated `## YYYY-MM-DD` sub-sections if any.
- `assessments/` subdirectory with multiple `.md` files → each file is a candidate.
- Both exist → merge (subdirectory files take precedence; flat file content appended to oldest if dates conflict).

Then:
1. Identify the most recent assessment (by date in filename or by date header). Make it `assessments/latest.md`.
2. Move all other assessment files to `assessments/archive/`, preserving filenames where they are already descriptive (`0.0-phase-zero-summary.md`); otherwise rename to `<YYYY-MM-DD>-<topic-slug>.md`.
3. Generate the "Summary of earlier assessments" block at the bottom of `assessments/latest.md`.
4. Remove the old flat `assessment.md` after content is preserved in `assessments/archive/`.

### 5d. plan.md → sectional plan/

Read `plan.md`. Parse on `## Phase {N}` or `# Phase {N}` headings (both the bare form and the colon variant `## Phase 1: Foundations` are accepted).

1. For each phase section, write `plan/phase-<N>.md` containing the section body. Promote the `## Phase {N}` heading to `# Phase {N}` at the top of the new file (the file is now a stand-alone phase plan, not a section of a larger doc).
2. Write `plan/README.md` as the arc index: project topic, target arc / pace summary from the original plan front matter, then a bulleted list of phases with pointers to each `phase-<N>.md`. Mark the current phase based on `state.json.currentPhase`.
3. **Preserve non-phase content.** Real v1 plans often carry top-of-file metadata (goal, target date, capacity), a week-by-week schedule table, a resources table, and a "Not covering" section. All of this content lives outside the `## Phase` boundaries and MUST end up in `plan/README.md` (top-of-file content above the Phases list; tables and "Not covering" sections below it). Nothing from `plan.md` is discarded.
4. Move the original `plan.md` into the backup directory; do not leave it at the canonical path (its presence would confuse future readers).

If `plan.md` has no `## Phase` headings (rare; informal plans), do not split — leave `plan.md` in place and write a one-line `plan/README.md` pointing to it as a single-file plan. Note this case in the migration marker output.

### 5e. .bodhi-profile.json → split

Read the existing `learningWithBodhi/.bodhi-profile.json`.

1. Extract `activeProjects` and `completedProjects` arrays into a new file: `learningWithBodhi/.bodhi-profile.projects.json` with shape per `state-schema` KB.
2. If `totalProjects` exists at top level, move it into `cumulativeStats.totalProjects`.
3. Bump `version` to 2 in the top-level profile.
4. Write the slimmed `.bodhi-profile.json` (top-level fields + cumulativeStats + patterns only).

If the file does not exist, this step is a no-op (the profile is created lazily by `/learn` on the first project).

### 5f. spaced-review.json version bump

Read `spaced-review.json`. If `version` is 1 (or missing — many real v1 files have no `version` field at all), bump to 2 and persist. No structural changes — observed real data already carries `question` and `lastResult` per concept; the bump just makes the schema declaration explicit.

### 5g. Write the migration marker

Create `.bodhi/.migration-1.7.0.md`:

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

The marker file's presence is what makes the migration idempotent.

### 5h. Report to the learner

Print a clear before/after summary (not the full marker file; a digest):

```
Migration complete.

Before: state.json 6.2 KB, plan.md 16 KB, progress.md 3.7 KB, assessments 58 KB total, ...
After:  state.json 1.5 KB, plan/ (split: README 1 KB + 4 phase files), progress.md 2.1 KB live + 3 archive entries, assessments/latest.md 17 KB + 3 archive files, ...

Routine skill reads drop substantially — what was loaded eagerly is now archived behind pointers, ready when you need it but out of the way until then.

Archive content is permanent and accessible via pointers in live docs. Original files are at .bodhi/.pre-1.7.0-backup/ for one minor version.
```

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
