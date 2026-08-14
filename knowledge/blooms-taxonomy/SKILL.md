---
description: "Bloom's Taxonomy: 6 cognitive levels for programming, mastery criteria, per-concept tracking"
user-invocable: false
---

# Bloom's Taxonomy for Programming

**Evidence tier: organizing framework.** A classification scheme, not an intervention with effect sizes — its value here is making "level" observable and consistent across skills, not a claimed learning gain.

## The 6 Levels

| Level | Name | Programming Indicators | Example Assessment |
|-------|------|----------------------|-------------------|
| 1 | **Remember** | Recall syntax, name methods, recite definitions | "What keyword creates a variable in JavaScript?" |
| 2 | **Understand** | Explain code behavior, predict output, paraphrase concepts | "Explain what this function does in your own words" |
| 3 | **Apply** | Write code from requirements, use patterns in guided context | "Write a function that filters even numbers from an array" |
| 4 | **Analyze** | Debug code, compare approaches, identify performance issues | "This code has a bug when the array is empty. Find it." |
| 5 | **Evaluate** | Critique design decisions, justify choices, review code | "Which of these two implementations is better and why?" |
| 6 | **Create** | Design systems from scratch, build novel solutions, architect | "Design an API for a task management system" |

## Key Principles

- Track Bloom's level PER CONCEPT, not globally
- Progression is not always linear
- Exercises should target one level above the learner's current level (ZPD alignment)
- If a learner fails at Level N, *teach* at Level N-1 to reinforce — but the recorded `bloomLevel` does not drop. It is a one-way ratchet in the implementation (`max(current, tested)`): the forgetting signal is carried by the Leitner box and the `consecutiveCorrectAtL4Plus` streak, both of which reset on a miss, not by the classification. Even `/forget` demotes the box, never the level.

### The recorded level is what the learner demonstrated, not what they claim

`--tested-bloom N` is the level the question *actually tested at* and the answer *actually reached* — judged by you, from the exchange. A learner's assertion about their own performance ("that was definitely a Level 4 answer," "I'd have gotten it in an interview") is not evidence that it was; grade the answer they gave.

This matters more than it looks, because the ratchet above makes the write one-way and `bloomLevel >= 3` is an input to the prerequisite gate (`state-ops` KB). An inflated level does not just overstate a trophy — it silently passes the learner into a module whose prerequisite was never secured, and no later correct answer lowers it back.

## Concept Tiers (canonical — computed by `bodhi-state`, never re-derived in prose)

Every classified concept sits in exactly one tier. The ladder is ordered and evaluated top-down: the first row whose criteria hold is the concept's tier. `bodhi-state mastery` and `snapshot` compute this per concept and return per-module counts (`{unclassified, introduced, familiar, mastered}`); skills render those counts and MUST NOT infer a tier from other fields.

| Tier | Criteria | Learner-facing word |
|---|---|---|
| **mastered** | Bloom 4+ AND 3 consecutive correct at Level 4+ AND Box 4-5 AND Feynman check passed | *Solid* — can debug it and explain the trade-offs |
| **familiar** | Bloom 3+ AND Box 2+ (not yet mastered) | *Working* — can use it with guidance |
| **introduced** | classified (Bloom 1+), everything below familiar | *Introduced* — can explain what it does |
| **unclassified** | Bloom 0 — no v3 writer has classified it yet | *—* (not "introduced": nothing has been observed) |

**`mastered` is the predicate; *Solid* is the display word.** The four-conjunct formula is the canonical one from the `state-ops` KB (`is_mastered`) — this table names its tier, it does not restate or fork it. The right-hand column is display vocabulary for `/progress`: the plugin's internal scales are instructor-facing instruments, and a learner reads a position ("can use it with guidance"), not a number. Always render the word with its outcome clause; the clause is what makes the word mean something.

**Why `familiar` is Bloom 3 + Box 2, and not more.** The two conjuncts test different things and both are load-bearing: Bloom 3 says the learner reached the apply rung at least once, Box 2 says at least one retrieval survived a delay. Dropping either would let a single lucky answer read as *Working*. But the tier deliberately does NOT require a consecutive-correct streak or the Feynman gate — those are what separate *familiar* from *mastered*. A concept can sit at *familiar* indefinitely; that is the honest state of most working knowledge.

**Unclassified is not a zero.** A module whose concepts are all Bloom 0 has not been failed, it has not been *reached* — which is why `masteryPct` is `null` rather than `0` there (`state-ops` KB legacy display rule) and why the tier is rendered `—`. Displaying a score for untouched material tells a learner they fell short of something they never attempted.
