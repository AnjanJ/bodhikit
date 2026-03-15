---
description: "Spaced repetition: Ebbinghaus forgetting curve, Leitner box system, application to programming"
user-invocable: false
---

# Spaced Repetition (Ebbinghaus, Leitner)

## The Forgetting Curve

Without review, memory decays exponentially:
- 20 minutes: ~42% forgotten
- 1 hour: ~56% forgotten
- 24 hours: ~67% forgotten
- 1 week: ~75% forgotten
- 1 month: ~79% forgotten

Each successful recall resets and flattens the curve. The first review is the most critical.

## Leitner Box System (BodhiKit Implementation)

| Box | Review Interval | Meaning |
|-----|----------------|---------|
| 1   | 1 day          | New or forgotten concept |
| 2   | 3 days         | Recalled once successfully |
| 3   | 7 days         | Building retention |
| 4   | 14 days        | Strong retention |
| 5   | 30 days        | Long-term mastery |

**Rules:**
- New concepts start in Box 1
- Correct recall: move up one box
- Incorrect recall: move back to Box 1 (regardless of current box)
- `nextReview` = `lastReviewed` + box interval

## Application to Programming

Spaced repetition for coding is NOT just flashcards. It includes:
- **Spaced problem-solving**: Solve a coding problem, then solve it again from scratch at expanding intervals
- **Pattern-based spacing**: After learning a pattern, solve new problems using it at intervals
- **Code review as retrieval**: Revisit code you wrote days/weeks ago and explain what it does
- **Concept re-explanation**: Periodically explain previously learned concepts from memory
- **Predict before running**: Before executing code, predict the output — this forces retrieval
