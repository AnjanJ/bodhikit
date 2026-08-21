# BodhiKit outcomes — what the tracking data actually shows

_Generated 2026-08-21 by `dev/outcomes.py` from `bodhi-state export-anonymized`. No concept names, topic names, or free text leave the learner's machine — only counts, distributions, and rates._

## Read this first

This is **one learner, 5 projects**. It is published because a project whose thesis is pedagogy should show its numbers, not because the numbers prove anything. They are too few to support a claim in either direction. What they can do is make the claim falsifiable over time: if BodhiKit works, the retention rate at long gaps should hold near the Leitner target and the mastered count should grow; if it does not, this table will say so.

## Per project

| | Days active | Sessions | Concepts | Classified | Mastered | Feynman passed | Reviews | Overall recall |
|---|---|---|---|---|---|---|---|---|
| P1 | 12 | 3 | 8 | 3 | 0 | 1 | 8 | 50% |
| P2 | — | 1 | 8 | 0 | 0 | 0 | 0 | — |
| P3 | 44 | 2 | 6 | 1 | 0 | 1 | 1 | 100% |
| P4 | 44 | 2 | 6 | 1 | 0 | 2 | 3 | 67% |
| P5 | 44 | 2 | 8 | 1 | 0 | 0 | 1 | 100% |
| **All** | | 10 | 36 | 6 | 0 | 4 | 13 | 62% |

_Classified_ = concepts a teaching or review session has actually graded (Bloom ≥ 1); the rest were scaffolded by the plan and never reached. _Mastered_ uses the four-part formula (Analyze-level or above, three consecutive correct at that level, Box 4-5, Feynman explain-back passed).

## Retention by gap since the previous review (all projects pooled)

The Leitner literature targets roughly 80-90% recall at each scheduled review. Below that, intervals are too long; far above it, too short.

| Gap | Reviews | Correct | Partial | Incorrect | Recall |
|---|---|---|---|---|---|
| same-day | 8 | 4 | 2 | 2 | 50% |
| 1d | 0 | 0 | 0 | 0 | — |
| 2-3d | 0 | 0 | 0 | 0 | — |
| 4-7d | 3 | 2 | 0 | 1 | 67% |
| 8-14d | 1 | 1 | 0 | 0 | 100% |
| 15-30d | 0 | 0 | 0 | 0 | — |
| 31d+ | 1 | 1 | 0 | 0 | 100% |

## Where concepts sit

| Bloom rung | Concepts |
|---|---|
| — (not yet observed) | 30 |
| Remember | 0 |
| Understand | 0 |
| Apply | 3 |
| Analyze | 3 |
| Evaluate | 0 |
| Create | 0 |

| Leitner box | Concepts |
|---|---|
| Box 1 | 30 |
| Box 2 | 4 |
| Box 3 | 2 |
| Box 4 | 0 |
| Box 5 | 0 |

## Confidence calibration

9 answers carried a confidence tag. Too few to report a rate.

## Session mix

| Session type | Count |
|---|---|
| spaced-review | 3 |
| practice | 1 |

## What this does and does not say

- It says the plugin's tracking pipeline records real reviews at real gaps and that the numbers are inspectable. That was not true before 1.11.0.
- It does not say the learner learned more than they would have otherwise. There is no control condition and the sample is a handful of sessions.
- The thing to watch over the next months is the **15-30d** and **31d+** rows: that is where spaced repetition either earns its keep or does not.
- If you use BodhiKit, `bodhi-state export-anonymized` on your own project produces the same JSON; the `learning-data-report` issue template is the place to send it.
