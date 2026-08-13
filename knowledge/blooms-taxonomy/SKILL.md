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

## Mastery Criteria

A concept is **mastered** when:
- Bloom's Level 4+ achieved
- 3 consecutive correct quiz answers at Level 4+
- Concept in Leitner Box 4 or 5
- Can explain to another person without jargon (Feynman check passed)

A concept is **familiar** when:
- Bloom's Level 3 achieved
- At least 1 correct quiz answer at Level 3
- Concept in Leitner Box 2 or 3

A concept is **introduced** when:
- Bloom's Level 1-2
- Concept in Leitner Box 1
