---
description: "Cognitive Load Theory (Sweller): worked examples, faded scaffolding, completion problems, the expertise-reversal effect"
user-invocable: false
---

# Cognitive Load Theory (Sweller)

Working memory holds ~4 chunks; learning fails when a task's *intrinsic* load (the concept itself) plus *extraneous* load (everything else the learner must juggle) exceeds it. For novices, a full problem is mostly extraneous load; for experts, scaffolding itself becomes the extraneous load.

## The Worked-Example Effect

Novices learn more from **studying a worked solution** than from solving the equivalent problem — problem-solving search consumes the working memory that schema-building needs. This is among the most-replicated findings in instructional design (Sweller & Cooper 1985; Sweller 1988).

## Faded Scaffolding (the canonical sequence for Bloom 1-2)

Do not jump from explanation to a blank exercise. Fade in three steps:

1. **Worked example** — a complete, annotated solution the learner studies and explains back ("why does step 2 come before step 3?").
2. **Completion problem** — the same shape with 1-2 key steps removed; the learner fills the gaps.
3. **Full problem** — the learner constructs the whole solution (a *different* surface context — see `desirable-difficulties` KB variation rule).

One concept can move through all three in a session; a struggling learner can stay at step 2 across sessions without shame.

## The Expertise-Reversal Effect

Scaffolding that helps novices actively *hurts* intermediate-and-above learners (Kalyuga et al. 2003) — redundant guidance becomes extraneous load and crowds out generation. Bloom 3+ learners get completion problems or full problems only; never re-introduce worked examples for a concept the learner already applies. This is why the scaffolding ladder in `/teach` and `/practice` is keyed to Bloom level.

## Application Rules

- Bloom 1-2: faded sequence above. The exercise README *is* step 1+2 (worked example + completion), not a TODO list.
- Bloom 3-4: completion problems or test-driven specs; no worked example.
- Bloom 5-6: problem statement only. Absence of scaffolding is the point.
- Split attention: keep code and its explanation together (annotate inline), never "see the explanation above."
- One new concept per example; everything else in the example must already be mastered.

**Primary sources:** John Sweller, *Cognitive load during problem solving* (Cognitive Science, 1988); Sweller, Ayres & Kalyuga, *Cognitive Load Theory* (2011); Kalyuga et al., *The Expertise Reversal Effect* (2003).
