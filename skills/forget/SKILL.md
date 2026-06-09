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

For every concept in the queue, update `.bodhi/spaced-review.json` per the `spaced-repetition` KB demote rule: `box: 1`, `nextReview: tomorrow`, append a `reviewHistory` entry with `result: "incorrect"` and a note that this was learner-initiated (or invoked from `/reflect`).

**Per-concept Bloom + Feynman semantics (v3 schema, see `state-schema` KB):**
- **Reset `concepts[].consecutiveCorrectAtL4Plus` to `0`** — the mastery streak is broken when the learner signals retention has slipped.
- **Preserve `concepts[].feynmanPassed` as-is** — Feynman passed once is forever; the demote is about retention, not understanding. The learner can re-pass the gate later if needed, but they do not "lose" the explanation they once produced.
- **Preserve `concepts[].bloomLevel` as-is** — this skill captures retention drift via the box, not Bloom regression. (If Bloom level itself needs to drop, the right path is a fresh assessment or `/teach` re-entry, not `/forget`.)
- Apply the v2 → v3 inline-fill from the `state-migration` KB if the file is at version 2.

Update `.bodhi/state.json` `lastActivity` with a summary like "Demoted N concepts: A, B, C".

---

## Phase 4: Close

Single concept: "It will surface tomorrow. We will look at it then with fresh eyes."
Multiple concepts: "All [N] will surface across the next few days as they cycle through review."

If the learner wants to revisit immediately rather than wait, suggest `/explain <concept>` or `/teach <concept>` — but do not force it.
