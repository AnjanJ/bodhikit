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

## Phase 5: Migration Mode (chained v1 → v2 → v3)

This phase runs only when `$ARGUMENTS` is `migrate`. Load the `state-migration` KB now if not already loaded.

---

### ⚠️ STOP — Read this before checking any marker file

**The pre-1.10.8 broken behavior was: "if `.migration-1.7.0.md` exists, exit cleanly."** Do NOT do that. As of 1.10.0 there are TWO migration targets, and the presence of the 1.7.0 marker proves only that the v1→v2 transforms ran — it says nothing about whether v2→v3 ran. A project with `.migration-1.7.0.md` present and `.migration-1.10.md` absent **still needs migration work to run**.

If your instinct is to short-circuit on a single marker, that instinct is the bug. Work through the decision matrix below before exiting.

---

### Phase 5 decision matrix (resolve THIS before any other action)

For each project, check BOTH markers, then look up the row:

| `.migration-1.7.0.md` | `.migration-1.10.md` | What to run | Exit condition |
|---|---|---|---|
| absent | absent | Steps 5a–5f AND step 5f-bis (full chained migration) | Run, then write BOTH markers |
| absent | present | Steps 5a–5f only (this state is rare — 1.10 ran without 1.7.0 — but possible if a learner manually rolled forward) | Run 5a–5f, then write 1.7.0 marker |
| **present** | **absent** | **Step 5f-bis ONLY** (1.7.0 already on disk; v2→v3 transform still needs to run) | Run 5f-bis, then write 1.10 marker |
| present | present | Nothing | Exit cleanly: *"Both migrations complete. 1.7.0 marker dated `<date1>`; 1.10 marker dated `<date2>`. Nothing to do."* |

**CHECKPOINT: Name aloud (in your response to the learner) which row each project lands in, and which steps you are about to run, BEFORE running any step.** This is the load-bearing moment of the entire migration flow. Skipping this checkpoint is what caused the 1.10.10 dogfood run to silently report "nothing to do" against four projects that all needed the v2→v3 transform.

---

**Markers (referenced by the matrix):**

- `.bodhi/.migration-1.7.0.md` — proves v1 → v2 transforms (steps 5a–5f) have run.
- `.bodhi/.migration-1.10.md` — proves v2 → v3 transforms (step 5f-bis) have run.

**Per-target idempotency model (1.10.8).** Each migration target gets its own marker file in `.bodhi/`. A marker's presence proves *that target's* transforms are complete; a marker's absence means *that target's* transforms must run. The migrate command runs every target whose marker is missing, in version order. This replaces the 1.7.0 model where one marker exit-short-circuited the entire phase — that model became wrong as soon as a second migration target (1.10) shipped, because every learner already-1.7.0-migrated had `.migration-1.7.0.md` on disk and could never reach v3.

**Other pre-flight steps (after the checkpoint above):**

1. **Multi-project iteration.** If working at the `learningWithBodhi/` root (multiple projects), iterate Phase 5 over each project. Profile migration runs once for the root. **Each project gets its own row lookup in the decision matrix; do not assume four projects with the same 1.7.0-marker state share the same row** (they likely do, but the matrix lookup is per project).

2. **Capture before sizes.** Record byte sizes of every existing `.bodhi/` file. These will be reported back, scoped to whichever targets ran.

3. **Create backup directories for the target(s) that will run** (per the matrix row, not for every target unconditionally):
   - 1.7.0 target running → `.bodhi/.pre-1.7.0-backup/` (copy the monolithic files here before steps 5a–5f convert them; removable in 1.8.0 but exists now as a safety net).
   - 1.10 target running → `.bodhi/.pre-1.10-backup/` (5f-bis populates this with the pre-v3 spaced-review.json; removable in 1.11).

**Conversion steps (apply in this exact order, each step idempotent at the file level):**

If the 1.7.0 marker is present (matrix rows 3 and 4), steps 5a–5f are skipped — their data is already on disk in v2 shape, and skipping is cleaner than re-running for 0-delta.

5f-bis runs whenever the 1.10 marker is absent (matrix rows 1, 2 — wait, only row 1 in the strict sense; recheck the matrix). **Concretely: 5f-bis runs in matrix rows 1 and 3.**

### 5a. State narrative extraction

Read `state.json`.

**Idempotency check.** If `version` is already `2` (number, not string) AND neither `lastSessionSummary` nor `bloomResetNote` is present, this step is already done. Skip to step 5b.

Otherwise:

1. Compose a synthetic session entry from `lastSessionSummary` + `bloomResetNote` if either is present: date = `lastSessionAt` (or `updatedAt` if `lastSessionAt` is absent), body = the concatenation of the two fields with a `**Pre-1.7.0 migration note:**` prefix. **Hold this entry in memory for step 5b** — do not write it anywhere yet.
2. **Construct the new state.json content in memory.** Start from the existing parsed JSON, then: (a) delete the `lastSessionSummary` key, (b) delete the `bloomResetNote` key, (c) set `version` to the integer `2`.
3. **Write the new content to `.bodhi/state.json`, overwriting the existing file.** Use the Write tool (or equivalent file-write operation). Do not skip this — descriptive language like "remove the field" or "bump the version" means **rewrite the file to disk with the field removed and the version bumped**.
4. **Verify the write.** Re-read `.bodhi/state.json`. Confirm `version` is now `2` and the two narrative fields are absent. If either check fails, do NOT proceed to subsequent steps — report the failure and exit. The marker file MUST NOT be written until every step has actually persisted.

**Preserve unknown fields.** Real v1 `state.json` files in the wild carry fields from older minor versions (e.g., `goal`, `standalone`, `pace`, `previousModule`, `nextActivity`, `bloomLevels`, `initialBloomLevel`) that the current schema does not declare. The migration MUST preserve every field it does not explicitly strip. Only `lastSessionSummary` and `bloomResetNote` are removed; everything else stays verbatim in the rewritten file.

If neither narrative field was present, still complete steps 2-4 above to ensure `version` reaches `2` on disk.

### 5b. progress.md → live + archive + summary

Read existing `progress.md`.

**Idempotency check.** If `progress.md` already contains the literal heading `## Summary of earlier sessions` AND `progress/archive/` already exists with at least one `session-*.md` file, this step is already done. Skip to step 5c.

Otherwise, parse out session entries. Real v1 files use several heading styles — try them in this order:

1. Top-level dated: `## YYYY-MM-DD` or `## YYYY-MM-DD — <label>`.
2. Hierarchical: a top-level `## Session Log` header followed by `### Session N` or `### Session N — YYYY-MM-DD` entries.
3. Numbered: `## Session N` with a date in the body.
4. Fallback: if none match, treat the whole file as a single archived blob with synthetic date = `state.json.lastSessionAt` or `updatedAt`.

If a synthetic entry was held from step 5a and its date is NOT already covered by an existing section, prepend it to the parsed list as the most recent entry.

**Non-session content preservation.** Real v1 `progress.md` files often contain non-session content at the top: a "Timeline" or "Module Status" table summarizing module completion, a description paragraph, header front-matter. This content MUST be preserved. If it summarizes current state, keep it at the bottom of the new live `progress.md` (after the "Summary of earlier sessions" block). If it is bulky and historical, write it to a sibling file `progress/notes.md` instead, and add a single line in `progress.md` pointing to it.

If the parsed list has only one entry, no archive work is needed — but you still MUST write a new `progress.md` that contains an empty "Summary of earlier sessions" section appended below the entry. Use the Write tool to overwrite the existing file.

If the parsed list has multiple entries:

1. Identify the most recent entry. It becomes the new live head.
2. **For each older entry, write a file at `progress/archive/session-<YYYY-MM-DD>[-N].md`** (sequential `-N` suffix for multiple same-day sessions). Use the Write tool. Each archive file is self-contained: copy the full section body verbatim, including the heading.
3. Compose the "Summary of earlier sessions" block — one entry per archived session, derived from each section's bullet structure (Outcomes line if present; otherwise first non-empty bullet). Target 2-5 lines per entry; up to 20 for milestone sessions. Format per Phase 3 step 3.
4. **Write the new `progress.md`** using the Write tool, overwriting the existing file. Content structure: latest-entry heading + body, separator (`---`), `## Summary of earlier sessions`, generated summary entries, optional separator + preserved non-session content. Do not just "replace" mentally — emit the Write call.
5. **Verify the write.** Re-read `progress.md`. Confirm the file now contains `## Summary of earlier sessions` and the latest entry. Confirm at least one `progress/archive/session-*.md` exists. If either check fails, do NOT proceed — report the failure and exit. The marker file MUST NOT be written if this step did not persist.

### 5c. assessment.md / assessments/ → live + archive + summary

**Idempotency check.** If `assessments/latest.md` already exists AND no flat `.bodhi/assessment.md` (singular) exists, this step is already done. Skip to step 5d.

Otherwise, detect the existing assessment layout:
- Flat `assessment.md` only → treat as a single block in v1 format; parse out dated `## YYYY-MM-DD` sub-sections if any.
- `assessments/` subdirectory with multiple `.md` files → each file is a candidate.
- Both exist → merge (subdirectory files take precedence; flat file content appended to oldest if dates conflict).

Then:

1. Identify the most recent assessment (by date in filename or by date header).
2. **Write that content to `assessments/latest.md`** using the Write tool. If the content is large (≥ 8 KB), `latest.md` should be a summary-with-pointer pattern: header + key findings + a pointer line `> Full report preserved at archive/<filename>` — and the full content goes to the archive file instead.
3. **For each non-latest assessment, write it to `assessments/archive/<filename>.md`** using the Write tool. Preserve filenames where descriptive (`0.0-phase-zero-summary.md`); otherwise use `<YYYY-MM-DD>-<topic-slug>.md`.
4. **Append a "Summary of earlier assessments" block to `assessments/latest.md`** using the Edit tool. One entry per archived assessment with a `→ archive/<filename>` pointer.
5. **Delete the old flat `.bodhi/assessment.md`** using the Bash tool (`rm`). The content has been preserved in `assessments/archive/` and in the `.pre-1.7.0-backup/` safety net.
6. **Verify.** Confirm `assessments/latest.md` exists and contains the "Summary of earlier assessments" section. Confirm `.bodhi/assessment.md` (singular) no longer exists. If either check fails, do NOT proceed — report and exit.

### 5d. plan.md → sectional plan/

Read `plan.md`. Parse on `## Phase {N}` or `# Phase {N}` headings (both the bare form and the colon variant `## Phase 1: Foundations` are accepted).

1. For each phase section, write `plan/phase-<N>.md` containing the section body. Promote the `## Phase {N}` heading to `# Phase {N}` at the top of the new file (the file is now a stand-alone phase plan, not a section of a larger doc).
2. Write `plan/README.md` as the arc index: project topic, target arc / pace summary from the original plan front matter, then a bulleted list of phases with pointers to each `phase-<N>.md`. Mark the current phase based on `state.json.currentPhase`.
3. **Preserve non-phase content.** Real v1 plans often carry top-of-file metadata (goal, target date, capacity), a week-by-week schedule table, a resources table, and a "Not covering" section. All of this content lives outside the `## Phase` boundaries and MUST end up in `plan/README.md` (top-of-file content above the Phases list; tables and "Not covering" sections below it). Nothing from `plan.md` is discarded.
4. Move the original `plan.md` into the backup directory; do not leave it at the canonical path (its presence would confuse future readers).

If `plan.md` has no `## Phase` headings (rare; informal plans), do not split — leave `plan.md` in place and write a one-line `plan/README.md` pointing to it as a single-file plan. Note this case in the migration marker output.

### 5e. .bodhi-profile.json → split

Read the existing `learningWithBodhi/.bodhi-profile.json`.

1. Extract `activeProjects` and `completedProjects` arrays into a new file: `learningWithBodhi/.bodhi-profile.projects.json` with shape per `state-schema` KB. **The new file MUST declare `"version": 2`** — cohort-consistent with all other v2 files, per `state-schema` KB.
2. If `totalProjects` exists at top level, move it into `cumulativeStats.totalProjects`.
3. Bump `version` to 2 in the top-level profile.
4. Write the slimmed `.bodhi-profile.json` (top-level fields + cumulativeStats + patterns only).

If the file does not exist, this step is a no-op (the profile is created lazily by `/learn` on the first project).

### 5f. spaced-review.json version bump

Read `spaced-review.json`. If `version` is 1 (or missing — many real v1 files have no `version` field at all), bump to 2 and persist. No structural changes — observed real data already carries `question` and `lastResult` per concept; the bump just makes the schema declaration explicit.

### 5f-bis. spaced-review.json v2 → v3 (Bloom + Feynman field fill, 1.10.0)

**Defensive self-check (1.10.11).** Before checking idempotency or trusting any upstream gating, **read `.bodhi/spaced-review.json` from disk right now.** If `version` is already `3` AND every concept entry carries all three new fields, this step has nothing to do — exit 5f-bis cleanly. If NOT — that is, the file is at v2 OR concepts are missing the new fields — this step MUST run regardless of what Phase 5's Pre-flight decided, what markers exist on disk, or what the model "concluded" earlier in the conversation. This defensive check exists because the 1.10.10 dogfood caught a real failure mode: the model short-circuited Pre-flight on the 1.7.0 marker and exited "nothing to do" while four real projects all needed the v2→v3 transform. 5f-bis is the last line of defense; running it costs nothing on already-migrated data (the idempotency check below catches that), and running it on un-migrated data is exactly what the learner asked for.

Read `spaced-review.json` (after step 5f has it at version 2 in memory or on disk, OR — in matrix row 3 where 5f did not run — just read it from disk; it is already at v2).

**Idempotency check.** If `version` is already `3` AND every entry in `concepts[]` has `bloomLevel`, `feynmanPassed`, and `consecutiveCorrectAtL4Plus` keys present, this step is already done. Skip to step 5g.

Otherwise:

1. **Back up the pre-v3 file using imperative writes.** Per the 1.7.1 imperative-write discipline (which 1.10.8 also applies here):
   - **Idempotency check.** If `.bodhi/.pre-1.10-backup/spaced-review.json` already exists on disk, skip the backup write. Do NOT overwrite — the backup is the safety net for THIS migration invocation and any prior one's; preserving it is non-negotiable.
   - **Create the backup directory** with the Bash tool: `mkdir -p .bodhi/.pre-1.10-backup` (the `-p` flag makes it idempotent).
   - **Read the current `.bodhi/spaced-review.json`** with the Read tool.
   - **Write the contents verbatim** to `.bodhi/.pre-1.10-backup/spaced-review.json` with the Write tool. Do not paraphrase, reformat, or strip fields — the backup is byte-for-byte the pre-migration state.
   - **Verify the backup** at the parsed-JSON level, not byte-for-byte. Re-read `.bodhi/.pre-1.10-backup/spaced-review.json`. Confirm the file exists, parses as JSON, and is **key-for-key equal** to the source when both are parsed — same top-level keys, same `concepts[].length`, same field set on every concept entry (including non-canonical fields like `precisionGap`, `lastResult` prose, `flaggedForFullReteach`), same `sessionHistory[].length` with the same field set on every entry (including non-canonical fields like `boxChanges`, `precisionGapMovement`, `habitObservations`). Whitespace and key-order differences are NOT failures — JSON serializers routinely vary on both. Only structural or content differences count. If any check fails, do NOT proceed to step 2 — report which check failed and exit. The backup must exist before any in-place transformation begins; without it, a partial write to the source destroys the only copy of the pre-v3 data.
2. **For each entry in `concepts[]`**, add the three new fields if absent — per the v2 → v3 row in the `state-migration` KB:
   - `bloomLevel: 0` (uninitialized — the legacy fallthrough rule in the `state-schema` KB makes this safe for prerequisite gates)
   - `feynmanPassed: false`
   - `consecutiveCorrectAtL4Plus: 0`
   - Do NOT touch `reviewHistory[]` entries — readers treat absent `bloomLevel` on history rows as `0`; only new history rows written post-v3 include it.

   **Critical: mutate the parsed JSON object in place.** Do not re-serialize from a schema template or build a new object from the documented canonical fields. Real v2 `spaced-review.json` files in the wild carry non-canonical fields per concept (`precisionGap`, `lastResult` prose, `flaggedForFullReteach`) and per `sessionHistory[]` entry (`boxChanges`, `precisionGapMovement`, `habitObservations`, `partials`, `note`). These fields are the learner's teaching history and may carry hundreds of bytes of prose annotation each. The `state-schema` KB's Update Rules section is explicit: "Skills MUST preserve unknown fields when writing (forward compatibility)." An executing model that builds a new JSON from "the documented shape plus the three new fields" will silently drop every non-canonical field — wiping months of learner annotations. Read the parsed JSON, add the three keys to each concept, leave every other key untouched.
3. **Construct the new file content in memory.** Set top-level `version` to the integer `3`. Preserve every other field verbatim, per the in-place mutation discipline in step 2.
4. **Write `.bodhi/spaced-review.json`** using the Write tool, overwriting the existing file.
5. **Verify the write.** Re-read the file. Confirm:
   - Top-level `version` is `3`.
   - `concepts[].length` equals the source file's `concepts[].length` (no concepts dropped or duplicated).
   - The **first AND last** concept entries each carry all three new fields (`bloomLevel`, `feynmanPassed`, `consecutiveCorrectAtL4Plus`); if `concepts[].length > 5`, additionally sample one entry from the middle.
   - Each sampled concept retains its non-canonical fields if any were present in the source (spot-check: pick one concept that had `precisionGap` in the source; confirm it's still there in the rewritten file).

   If any check fails, do NOT proceed to step 5g — report which check failed and exit. The `.pre-1.10-backup/spaced-review.json` from step 1 is the rollback path; the source file can be restored from it.

If `concepts[]` is empty or absent, still complete steps 2-4 to ensure `version: 3` is on disk.

Track per-step stats for the report: number of concepts touched, number of fields added per concept (typically 3 × concept count for first migration; 0 for an already-migrated file).

### 5g. Write the migration marker(s)

Per the per-target idempotency model declared in Phase 5's Pre-flight, this step writes one OR two markers depending on which targets ran in this invocation.

**Precondition for writing `.migration-1.7.0.md`** (write only if the 1.7.0 target ran in this invocation). Verify every 1.7.0-target step persisted to disk:

- `state.json` is on disk with `version: 2` (integer) and no `lastSessionSummary` / `bloomResetNote` fields.
- `progress.md` is on disk and contains the literal heading `## Summary of earlier sessions`.
- `assessments/latest.md` is on disk.
- `.bodhi/assessment.md` (flat singular file) does NOT exist on disk.
- `plan/README.md` is on disk; the flat `plan.md` is at `.pre-1.7.0-backup/plan.md` (not at `.bodhi/plan.md`).
- `learningWithBodhi/.bodhi-profile.projects.json` is on disk with `version: 2` (or the profile did not exist, in which case skip).
- `spaced-review.json` carries `version: 2` or higher (1.7.0 target only requires v2; v3 is checked separately below).

**Precondition for writing `.migration-1.10.md`** (write only if the 1.10 target ran in this invocation). Verify the v2 → v3 transform persisted to disk:

- `.bodhi/.pre-1.10-backup/spaced-review.json` exists on disk, parses as JSON, and carries `version: 2`. The backup must be in place; without it, the v3 write happened without a safety net and the precondition fails even if the source file looks right.
- `.bodhi/spaced-review.json` carries `version: 3` AND every `concepts[]` entry has `bloomLevel`, `feynmanPassed`, and `consecutiveCorrectAtL4Plus` keys.

If any of these checks fails, do NOT write the corresponding marker. Report which check failed and exit non-zero. The presence of a marker is what makes future runs detect that target's migration as complete — writing it prematurely would falsely make a broken migration appear successful.

If every check for a target passes, write that target's marker. If both targets ran successfully in one invocation, write both markers.

For the 1.7.0 marker, create `.bodhi/.migration-1.7.0.md`:

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

For the 1.10 marker, create `.bodhi/.migration-1.10.md`:

```markdown
# Migration to 1.10 — <YYYY-MM-DD>

Performed by `/bodhikit:housekeep migrate`.

## What changed

`spaced-review.json` bumped from version 2 to version 3. Per-concept Bloom + Feynman fields added with safe defaults so the v3 mastery formula in the `state-schema` KB becomes computable:

- `bloomLevel: 0` on every concept (uninitialized — the legacy fallthrough rule allows advancement; once a v3 writer sets a non-zero value, normal gate logic applies).
- `feynmanPassed: false` on every concept.
- `consecutiveCorrectAtL4Plus: 0` on every concept.

## Before / after byte sizes

| File | Before | After |
|---|---|---|
| spaced-review.json | N KB | M KB (N concepts × 3 new fields added) |

## Backup

Pre-v3 `spaced-review.json` preserved at `.bodhi/.pre-1.10-backup/spaced-review.json`. This directory will be removed in 1.11.

## Notes

<any cases that required manual judgment or fallback handling>
```

Each marker's presence is what makes its target idempotent for future invocations.

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

**If the 1.10 target ran in this invocation:**

```
1.10 migration complete.

spaced-review.json: bumped from v2 to v3. N concepts each received bloomLevel: 0, feynmanPassed: false, consecutiveCorrectAtL4Plus: 0.

Before: spaced-review.json X.X KB
After:  spaced-review.json Y.Y KB (+N concepts × 3 fields)

Mastery now becomes observable as you continue: /quiz, /teach, /explain, /practice all write the new per-concept fields. Until those skills touch a concept, the prerequisite Bloom gate treats it as "no opinion yet" and lets you advance freely. /progress shows "—" for modules where no concept has been classified under v3 yet.

Pre-v3 spaced-review.json is at .bodhi/.pre-1.10-backup/ for one minor version.
```

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
