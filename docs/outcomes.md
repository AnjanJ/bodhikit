# BodhiKit outcomes — what the tracking data actually shows

_Generated 2026-10-21 by `dev/outcomes.py` from `bodhi-state export-anonymized`. No concept names, topic names, or free text leave the learner's machine — only counts, distributions, and rates._

## Read this first

This is **one learner, 5 projects**. It is published because a project whose thesis is pedagogy should show its numbers, not because the numbers prove anything. They are too few to support a claim in either direction. What they can do is make the claim falsifiable over time: if BodhiKit works, the retention rate at long gaps should hold near the Leitner target and the mastered count should grow; if it does not, this table will say so.

## Per project

| | Days since start | Sessions | Concepts | Classified | Mastered | Feynman passed | Reviews | Overall recall | Delayed recall |
|---|---|---|---|---|---|---|---|---|---|
| P1 | 105 | 3 | 6 | 1 | 0 | 1 | 2 | 100% | 100% |
| P2 | 105 | 3 | 6 | 1 | 0 | 2 | 3 | 67% | — |
| P3 | 105 | 2 | 8 | 1 | 0 | 0 | 1 | 100% | 100% |
| P4 | 48 | 8 | 17 | 13 | 0 | 10 | 32 | 88% | 62% |
| P5 | 7 | 1 | 6 | 4 | 0 | 0 | 0 | — | — |
| **All** | | 17 | 43 | 20 | 0 | 13 | 38 | 87% | 73% |

_Reviews_ and _Overall recall_ count tested outcomes only — a `/forget` is a self-report and is excluded. _Delayed recall_ further drops same-day reviews (immediate post-instruction performance) and is the number that answers whether the intervals are working. _Classified_ = concepts with a level on record (Bloom ≥ 1), from a graded session or, since 1.21.0, the starting assessment; the rest were scaffolded by the plan and never reached. _Mastered_ uses the five-part formula (Analyze-level or above, three consecutive correct at that level on due reviews, Box 4-5, an explain-back passed after the last miss, one correct in applied work since the last miss).

## By evidence kind (all projects pooled)

Since 1.25.0 a concept has a kind of evidence: `code`, `problems`, `writing` or `performed` (a project with none recorded is `code`). One of the intake's goals is delayed recall outside code within 10 points of code; this is where it shows. On a performed skill the practice itself is the learner's report, so Solid resting on it is counted apart.

| Kind | Concepts | Mastered | By the learner's account | Reviews | Delayed reviews | Delayed recall |
|---|---|---|---|---|---|---|
| `code` | 43 | 0 | 0 | 38 | 11 | 73% |

Solid by the learner's account: **0** of 0 Solid concept(s). Decision 0001 reverses the self-report half if such concepts fail their next delayed review at least 20 points more often than Solid resting on observed work, over the first 30 such reviews.

## Retention by gap since the previous review (all projects pooled)

The Leitner literature targets roughly 80-90% recall at each scheduled review. Below that, intervals are too long; far above it, too short.

| Gap | Reviews | Correct | Partial | Incorrect | Recall |
|---|---|---|---|---|---|
| same-day | 27 | 25 | 2 | 0 | 93% |
| 1d | 2 | 2 | 0 | 0 | 100% |
| 2-3d | 0 | 0 | 0 | 0 | — |
| 4-7d | 1 | 1 | 0 | 0 | 100% |
| 8-14d | 2 | 2 | 0 | 0 | 100% |
| 15-30d | 4 | 1 | 1 | 2 | 25% |
| 31d+ | 2 | 2 | 0 | 0 | 100% |

## Where concepts sit

| Bloom rung | Concepts |
|---|---|
| — (not yet observed) | 23 |
| Remember | 0 |
| Understand | 4 |
| Apply | 15 |
| Analyze | 1 |
| Evaluate | 0 |
| Create | 0 |

| Leitner box | Concepts |
|---|---|
| Box 1 | 29 |
| Box 2 | 9 |
| Box 3 | 4 |
| Box 4 | 1 |
| Box 5 | 0 |

## Confidence calibration

6 answers carried a confidence tag. Too few to report a rate.

## Session mix

Counts only sessions that wrote a `sessionHistory` entry (reviews, quizzes, practice, evaluations). Teaching sessions update the session counter above but do not write a history entry, so this table totals less than _Sessions_.

| Session type | Count |
|---|---|
| spaced-review | 3 |
| diagnostic-after-gap | 1 |
| targeted-reteach | 1 |
| other | 1 |

## What this does and does not say

- It says the plugin's tracking pipeline records real reviews at real gaps and that the numbers are inspectable. That was not true before 1.11.0.
- It does not say the learner learned more than they would have otherwise. There is no control condition and the sample is a handful of sessions.
- The thing to watch over the next months is the **15-30d** and **31d+** rows: that is where spaced repetition either earns its keep or does not.
- If you use BodhiKit, `bodhi-state export-anonymized` on your own project produces the same JSON; the `learning-data-report` issue template is the place to send it.
