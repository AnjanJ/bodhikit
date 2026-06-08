---
description: "Feynman Technique: 4 steps for deep understanding, when to use, implementation for programming"
user-invocable: false
---

# Feynman Technique

## The 4 Steps

1. **Choose a concept** and study it
2. **Explain it simply** — as if to a 12-year-old, no jargon, use analogies
3. **Identify gaps** — where did you struggle, use vague language, or skip steps?
4. **Simplify and refine** — go back to source for gaps, create better analogies, repeat until clean

## When to Use

- Deep conceptual understanding needed (design patterns, architectural principles)
- Suspected illusions of competence ("I think I understand but...")
- Abstract concepts that benefit from analogies
- Central, high-leverage concepts where deep understanding pays dividends

## When NOT to Use

- Procedural/motor skills (typing speed, keyboard shortcuts) — use deliberate practice
- Syntax memorization — use spaced repetition
- Simple, straightforward concepts — just practice
- Time-constrained situations — too time-intensive for universal application

## Implementation in BodhiKit

After teaching a concept, always ask: "Now, explain this back to me in your own words. Pretend I have never heard of it."

If the learner uses jargon, ask them to define each technical term simply. If they skip steps, ask about the missing steps. If they use vague language ("it kind of does..."), probe for precision.

## Analogy-Escalation Protocol

A single named protocol every skill reaches for when the learner is stuck. Analogy is not a default tactic — it is a *response to detected struggle*. Reaching for one too early teaches the analogy instead of the concept.

### When to trigger

Read the `zone-of-proximal-development` KB's *Beyond the ZPD* signals. Trigger this protocol when **any one** of these is observed:

- Learner cannot articulate what they are confused about ("I just don't get it").
- The first explanation drew a blank stare (no echo of the key terms, no question, no partial attempt).
- A hint at the **Approach** level (hint 2 of 3) did not unstick them.
- Their explain-back is correct in words but mechanical — no sign of the underlying mental model.
- Repeated misconception that survives one corrective re-explanation.

Do NOT trigger on:

- A single wrong answer to a Bloom-3+ question (that is normal productive struggle).
- A request for "more examples" (that is engagement, not stuckness — give the example, no analogy needed).
- Time pressure ("I need to ship this") — switch to `/explain` or just answer the question; analogy ladders cost time.

### The 4-rung ladder

Climb rungs in order. Do not skip. Do not reach for rung 4 first because it is easiest to author — the personalization in rungs 1 and 2 is the whole point.

**Rung 1 — Learner's own domain.** Read `learningWithBodhi/.bodhi-profile.json` `learnerBackground.domains[]`. If a domain is listed and not already used for this concept (check `learnerBackground.analogyHistory[]` for `{concept, domain}` pairs), construct the analogy from there. Examples:

- Domain `cooking` + concept *recursion* → "A recipe that, mid-step, says 'now do this entire recipe with half the ingredients, then continue.'"
- Domain `music` + concept *pure functions* → "A scale played at the same tempo on the same instrument sounds the same every time — no matter who is in the room, what time it is, or what was played before."

**Rung 2 — Ask once.** If `learnerBackground.domains[]` is empty OR every listed domain has been used for this concept, ask **one** question: *"Before we keep going — what is a field, hobby, or job you know well? Cooking, sports, music, plumbing, accounting, anything. The next explanation will land better if I can borrow from it."* When they answer, append to `learnerBackground.domains[]` (write-through) and use it for this analogy. If they decline or say "just explain it," drop straight to rung 3.

**Rung 3 — Universal physical.** Reach for a universally-shared physical analogy. Stoves, mailboxes, libraries, road maps, water flow, locks-and-keys, recipes. Use these only when rung 1 and rung 2 produced nothing — these are weakest because they are pre-cached for every learner; the magic of analogy is *novel mapping into their world*, not familiar mapping into everyone's.

**Rung 4 — Code-restatement.** A second concrete code example that restates the same concept differently (different data type, different scale, different domain). This is not "an analogy" in the strict sense — it is the same concept said again with different variables. Use when analogies have failed and the next move is to retreat to a simpler sub-concept anyway.

### Cap and exit

After **two** analogies on the same concept without traction, **stop laddering**. Reaching for a third analogy means the concept is above the learner's ZPD. The right move is not a better analogy — it is a smaller sub-concept.

Say (or equivalent in voice): *"Let us set [concept] down for a moment. There is a smaller piece underneath it that we should make solid first. Let us look at [prerequisite sub-concept]."*

Decompose to the missing prerequisite and teach that. The original concept comes back into view once its foundation is in place.

### Profile read/write contract

The protocol reads `learnerBackground.domains[]` and `learnerBackground.analogyHistory[]` from `.bodhi-profile.json` (the top-level file, not the projects file — domains are cross-project, like learning style). It appends to both fields when rung 2 fires, and appends a `{concept, domain, landed: true|false}` entry to `analogyHistory[]` whenever an analogy is used (so future invocations on the same concept reach for a different domain). Both fields are optional; absence means "no prior data" and the protocol falls through to rungs 2-3 naturally. See the `state-schema` KB for field shapes and the writers list.

### Voice

Frame analogy as offering, not instruction. *"Let us try this from a different angle"* not *"Here is an easier way to think about it."* The learner is not failing — the first explanation did not fit them, and the protocol is a kindness, not a remediation.
