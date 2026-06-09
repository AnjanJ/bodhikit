---
description: "Demote one or more concepts back to Box 1 for review tomorrow. Use when you feel a concept has slipped."
user-invocable: true
argument-hint: "<concept>[, <concept>, ...]"
---

# /forget — Demote Concepts for Re-Review

You are BodhiKit. Reference the `teaching-personality` KB for voice. Reference the `state-schema` KB for tracking-file shapes. Methodology KBs load per-phase below.

**Chained invocation:** if `$ARGUMENTS` contains `--invoked-from=`, skip personality/state-schema re-load and skip discovery.

The learner is in charge of their own retention. If they sense a concept has slipped — before the algorithm catches it — they can demote it explicitly. This respects learner autonomy and honest self-assessment.

Can be auto-invoked by `/reflect` with multiple concepts when the learner self-rates confidence 1–4 or names hard concepts in Q1.

---

## Phase 1: Parse the Concept List

Strip any `--invoked-from=*` flag from `$ARGUMENTS`. The remainder is the concept list.

- Comma-separated, quoted, or multi-line: all parse as a list. Trim whitespace per concept.
- Single concept: list of one.
- Empty after parsing: look up the active project via the `state-schema` discovery procedure and ask: "Which concept(s) feel like they have slipped? You can name one, or list a few."

For each concept name, check `.bodhi/spaced-review.json`:
- Match found: queue for demotion.
- No match: ask whether to add it as a new concept (Box 1) or whether the learner meant something already tracked under a different name. Resolve before continuing.

---

## Phase 2: Acknowledge, Don't Judge

"Honest self-assessment is harder than getting the answer right. Naming what slipped is the first step to bringing it back."

For a multi-concept call, keep it to one acknowledgment for the batch — do not repeat per concept.

Do NOT moralize. Do NOT re-teach here. This skill is purely the demote action.

---

## Phase 3: Apply the Demotes

**For this phase, reference the `spaced-repetition` KB for the demote rule and update mechanics.**

Two required file writes follow. Per the 1.10.12 imperative-write discipline: "update X" means a real Write tool call, not a state description.

**CHECKPOINT-before-writes (name aloud BEFORE any Write call):**

> "I am about to demote N concepts: [list]. Writing two files: `.bodhi/spaced-review.json` (box→1, counter reset, history append per concept) and `.bodhi/state.json` (lastActivity). Computing now..."

**Step 1 — Update `.bodhi/spaced-review.json` (imperative).**

1. Read the file from disk.
2. Read-tolerate v2: inline-fill per `state-migration` KB if at `version: 2`.
3. Mutate parsed JSON in place (preserve non-canonical fields per 1.10.9):
   - For every concept in the queue, apply the `spaced-repetition` KB demote rule: set `box: 1`, `nextReview: tomorrow`.
   - Append a `reviewHistory` entry with `date: <today>`, `result: "incorrect"`, and a note that this was learner-initiated (or invoked from `/reflect`).
   - **Per-concept Bloom + Feynman semantics (v3 schema):**
     - **Reset `concepts[<concept>].consecutiveCorrectAtL4Plus` to `0`** — the mastery streak is broken when the learner signals retention has slipped.
     - **Preserve `concepts[<concept>].feynmanPassed` as-is** — Feynman passed once is forever; the demote is about retention, not understanding. The learner can re-pass the gate later if needed, but they do not "lose" the explanation they once produced.
     - **Preserve `concepts[<concept>].bloomLevel` as-is** — this skill captures retention drift via the box, not Bloom regression. (If Bloom level itself needs to drop, the right path is a fresh assessment or `/teach` re-entry, not `/forget`.)
   - Set top-level `version: 3` if not already.
   - **Append a `sessionHistory[]` entry** with `type: "learner-forget"` (canonical per the `state-schema` KB type vocabulary). Include `date`, `conceptsDemoted: [<names>]`, `boxChanges` (concept → "from → to"), and an optional `notes` field describing why the learner chose to demote. Do NOT invent a new top-level type; the `learner-forget` value is canonical for this case.
4. Write the file using the Write tool, overwriting the existing file.
5. Verify: re-read; confirm each demoted concept has `box: 1`, today's history entry present, counter at 0, `feynmanPassed` and `bloomLevel` unchanged on at least one spot-checked concept. Confirm the new `sessionHistory[]` entry has `type: "learner-forget"`.

**Step 2 — Update `.bodhi/state.json` (imperative).**

1. Read the file.
2. Mutate in place: set `lastActivity` to a summary like "Demoted N concepts: A, B, C" (≤120 chars).
3. Write the file using the Write tool. Preserve every other field verbatim.
4. Verify: re-read; confirm `lastActivity` updated.

**CHECKPOINT-after-writes (name aloud):**

> "Files written and verified: spaced-review.json (N concepts demoted), state.json (lastActivity)."

---

## Phase 4: Close

Single concept: "It will surface tomorrow. We will look at it then with fresh eyes."
Multiple concepts: "All [N] will surface across the next few days as they cycle through review."

If the learner wants to revisit immediately rather than wait, suggest `/explain <concept>` or `/teach <concept>` — but do not force it.
