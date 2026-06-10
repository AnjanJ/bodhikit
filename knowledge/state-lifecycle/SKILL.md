---
description: "Rotation, archiving, summary-collapse, and retirement lifecycle for BodhiKit tracking surfaces. Loaded by /housekeep only — routine skills never rotate files."
user-invocable: false
---

# State Lifecycle — Rotation, Archiving, and Collapse

This KB owns the *lifecycle* of tracking surfaces: how live docs rotate into
archives, how summary blocks grow and collapse, and when concepts retire.
File *shapes* live in the `state-schema` KB; this KB is loaded by
`/housekeep` only. Routine skills append to live docs and never rotate.

See also: `state-migration` KB (version transforms, loaded by `/housekeep migrate`).

## Live + archive + summary pattern (sessions, assessments)

The live doc has two parts:

1. **Latest entry, in full.** The most recently written session log or assessment report.
2. **Summary of earlier entries.** A growing block where each archived entry is represented by 2–20 lines (target ~5), each with a date, headline, optional key Bloom moves / insights, and an explicit pointer to the archive file.

Skills read the live doc by default and follow a pointer into the archive only when the situation justifies it — the summary tells them whether following a pointer would be valuable.

**Summary block growth.** Routine sessions get ~2-5 lines; milestone sessions (phase complete, assessment done, breakthrough) get up to 20.

**Collapse rule.** When the cumulative summary block crosses 200 lines, the oldest summary entries roll into a *phase summary* (a single entry covering a contiguous range): "Phase 0 (M sessions, 2026-03-23 → 2026-04-30): outcomes summary. Archive: `archive/2026-03-*.md`." The original per-session archive files are not touched.

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
4. **Collapse old summary entries if the block exceeds 200 lines** per the collapse rule above.

**Idempotency.** Running `/housekeep` twice in a row is a no-op the second time — step 1 finds nothing new.

**Non-destruction.** Archive files are permanent. `/housekeep` never deletes archive content and never edits an existing archive file.

**Transparency.** `/housekeep` prints what it rotated and the before/after byte sizes of the live docs.

**Trigger.** `/housekeep` is invoked explicitly. Other skills do not embed this protocol. `/reflect` MAY invoke `/housekeep` at the end of its flow. `/continue` MAY detect un-housekept state and invoke `/housekeep` before resuming, silently.

## Concept retirement

When `spaced-review.json` `concepts.length` exceeds 200, `/housekeep` MAY (with user confirmation) move concepts with `lastReviewed` older than 180 days AND `box: 1` (demoted-and-forgotten) into a sibling `spaced-review.retired.json` file. Not automatic; surfaced as a suggestion in `/housekeep` output.

## Legacy path detection (one-time migration help)

If discovery finds projects under `~/code/learningWithBodhi` or `~/projects/learningWithBodhi` (pre-1.6.0 hardcoded paths) AND no `~/.bodhikit/config.json` exists, `/progress` (quick or all mode) SHOULD emit a single-line notice the first time it runs: "Found projects at <path>. Run `/bodhikit:housekeep migrate` to save these as search paths and convert tracking files to the current layout." This notice is one-shot.
