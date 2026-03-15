---
description: "Scientific debugging: TRAFFIC method (Zeller), debugging mindset (O'Dell), wolf fence, expert vs novice patterns"
user-invocable: false
---

# Scientific Debugging

## Zeller's TRAFFIC Method (2005)

1. **Track**: Document the problem precisely
2. **Reproduce**: Create reliable reproduction steps
3. **Automate**: Write an automated test that demonstrates the failure
4. **Find Origins**: Trace backward through dependencies
5. **Focus**: Narrow the search space (binary search / wolf fence)
6. **Isolate**: Scientific method — hypothesize, predict, probe (not fix), evaluate
7. **Correct**: Fix only after isolating the root cause

## The Debugging Mindset (O'Dell, 2017)

Applying Dweck's growth mindset to debugging:
- **Entity theorists** (fixed mindset): bugs = personal failure → frustration → random changes
- **Incremental theorists** (growth mindset): bugs = puzzles → systematic investigation → learning

Key insight: the debugging mindset can be taught. Frame bugs as puzzles, praise the process.

## Rubber Duck Debugging (Hunt & Thomas, 1999)

Self-explanation activates language processing, forces externalization of assumptions, and bridges implicit and explicit knowledge. Connected to the Feynman Technique: if you cannot explain the code simply, you do not understand it.

## Wolf Fence Algorithm (Gauss, 1982)

Binary search for bug location: place a checkpoint at the midpoint, determine which half contains the bug, repeat. O(log n) efficiency. Modern application: `git bisect`.

## Expert vs Novice Debugging (Ahmadzadeh et al., 2005)

Novice anti-patterns: tinkering (random changes), print spam without hypothesis, premature fixing, ignoring error messages, reading code without probing.

Expert behavior: form hypotheses quickly, use systematic strategies, read error messages carefully, probe before fixing.
