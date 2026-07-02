---
description: "Spaced repetition: Ebbinghaus forgetting curve, Leitner box system, application to programming"
user-invocable: false
---

# Spaced Repetition (Ebbinghaus, Leitner)

**Evidence tier: bedrock.** Distributed practice is one of the two highest-utility techniques in Dunlosky et al.'s (2013) review of ten learning techniques.

See also: `state-schema` KB (`spaced-review.json` shape), `desirable-difficulties` KB (why spacing works), `metacognition` KB (calibrating self-rated confidence against actual retention).

## The Forgetting Curve

Without review, memory decays steeply: most forgetting happens within the first day, and the curve keeps falling over the following weeks. (The widely-quoted percentage tables are a pop rendering of Ebbinghaus's savings-method data — the shape of the curve is the finding, not the digits.) Each successful recall resets and flattens the curve. The first review is the most critical.

## Leitner Box System (BodhiKit Implementation)

| Box | Review Interval | Meaning |
|-----|----------------|---------|
| 1   | 1 day          | New or forgotten concept |
| 2   | 3 days         | Recalled once successfully |
| 3   | 7 days         | Building retention |
| 4   | 14 days        | Strong retention |
| 5   | 30 days        | Long-term mastery |

**Rules (canonical — skills MUST cite this KB, not redeclare; implemented in code by `bodhi-state record-review`):**
- New concepts start in Box 1, `nextReview` = tomorrow
- Correct recall: move up one box (max 5), `nextReview` = today + new box interval
- Incorrect recall: move to Box 1, `nextReview` = tomorrow
- Partial recall: box held, `nextReview` = tomorrow (re-test soon; partial is not a Leitner demotion — but it does reset the `consecutiveCorrectAtL4Plus` mastery streak, per the `state-schema` KB)
- Learner-initiated demote (`/forget` or self-rated low confidence in `/reflect`): same as incorrect recall
- `nextReview` = `lastReviewed` + box interval

For the JSON shape of `spaced-review.json` and the write path, see the `state-schema` KB.

## Successive Relearning (Rawson & Dunlosky)

A missed retrieval should not end with the demotion. Within the same session, after the remaining items, **re-ask the missed concept (reframed, not verbatim) until the learner produces one successful retrieval** — cap at 2 retries, then explain and move on. The demotion to Box 1 stands either way; the in-session relearning rep is additional, not a substitute. Combining retrieval practice with relearning-to-criterion roughly doubles long-term retention versus single-shot retrieval (Rawson & Dunlosky, *Optimizing schedules of retrieval practice for durable and efficient learning*, 2011). `/quiz` Phase 2 runs the loop; retries are recorded with `record-review --retry`, which appends the history entry WITHOUT box, counter, or bloom movement — the evidence is kept, the demotion stands.

## Retention Rollup Views (canonical — skills MUST cite this section)

For dashboards and reports, the 5-box system rolls up into one named 3-tier view. Skills MUST NOT invent their own bucket boundaries inline — `/progress` and `/evaluate` previously diverged on this and each invented a slightly different rollup.

**Canonical 3-tier rollup:**

| Tier | Boxes | Meaning |
|---|---|---|
| **Strong retention** | Box 4-5 | Long-term retention. Reviews are infrequent (14d / 30d intervals); the concept has held across multiple successful recalls. |
| **Building retention** | Box 2-3 | Mid-curve. The concept has been successfully recalled once or twice but has not yet stabilized at the long intervals. |
| **Needs review** | Box 1 | New concept OR demoted concept. Either freshly introduced (tomorrow's review) or returned-to-square-one by an incorrect recall / `/forget`. |

`/progress` Spaced Repetition Health section and `/evaluate` Phase 4 Spaced Repetition Health line cite this section by name ("Strong / Building / Needs review per the spaced-repetition KB rollup"). Both display the same buckets so a learner reading either skill sees consistent numbers.

## Application to Programming

Spaced repetition for coding is NOT just flashcards. It includes:
- **Spaced problem-solving**: Solve a coding problem, then solve it again from scratch at expanding intervals
- **Pattern-based spacing**: After learning a pattern, solve new problems using it at intervals
- **Code review as retrieval**: Revisit code you wrote days/weeks ago and explain what it does
- **Concept re-explanation**: Periodically explain previously learned concepts from memory
- **Predict before running**: Before executing code, predict the output — this forces retrieval
