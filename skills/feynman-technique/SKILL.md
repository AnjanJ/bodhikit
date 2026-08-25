---
description: "Feynman Technique: 4 steps for deep understanding, when to use, implementation for programming"
user-invocable: false
---

# Feynman Technique

**Evidence tier: strong mechanism, anecdotal brand.** The named technique is folklore, but the mechanism it operationalizes — the self-explanation effect (Chi et al. 1994) plus retrieval practice — is well-replicated.

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

## Grading the Explain-Back (canonical ladder — `/teach` cites this)

Grade the final explanation at the rung it demonstrated, and record result + level together:

| Rung demonstrated | `--tested-bloom` |
|---|---|
| Clear, jargon-free explanation in own words | 2-3 |
| ...can also apply it in code | 3-4 |
| ...can also explain trade-offs and when NOT to use it | 4-5 |

**Grade the explanation the learner gave, not the one they say they gave.** "I explained it fine," "you're being pedantic," "just mark it passed" — these are assertions about the answer, not more of the answer. They are not evidence, and they do not move the rung. Hold the bar warmly and stay in voice (`teaching-personality` KB: "Let us look at this differently," never "That is wrong") — the voice governs *how* you say the grade, never *what* the grade is. If pushback names something real the learner actually said and you missed, re-read their explanation and regrade on that; if it only asserts adequacy, the grade stands. Conceding here is not kindness: `feynmanPassed` is set-never-unset (`state-schema` KB), so one concession permanently removes one of the four mastery locks, and the learner is the person it misleads.

A clean explanation at ANY rung = `correct` at that rung. Demonstrated application counts wherever it appears — a learner who produces or correctly chooses working usage inside their explanation (e.g. writes the right `CREATE INDEX` for the case) is on the apply rung (3-4) even with zero trade-off knowledge; grading them 0-2 ignores what they visibly did. Missing higher-rung depth **caps the level — it is not a failed retrieval**.

Reserve `incorrect` for demonstrated failure: a misconception that survived refinement, or no coherent explanation at any rung. `incorrect` demotes the Leitner box, and demotion means demonstrated forgetting (per the `spaced-repetition` KB) — bounded depth is not forgetting. (1.12.2: the grading-calibration evals caught executors resolving "gaps remained = incorrect" against apply-level learners who knew the mechanics cold.)

**Set the level by the HIGHEST rung the answer reached.** Walk the table top-down and find the best thing the learner actually did; that is the level. The rungs are cumulative, so reaching a higher one means the lower ones came with it — an explanation that covers trade-offs and when NOT to use the concept is 4-5, and the fact that it *also* demonstrated application does not pull it back to 3.

**Then: demonstrated usage sets a floor, an admitted gap sets a ceiling.** These bound the answer from opposite sides and neither one *is* the answer — they are corrections applied to the highest-rung reading above, for the case where the rungs come apart:

- **Floor.** Working usage inside the explanation (e.g. the right `CREATE INDEX` for the case) puts the floor at the apply rung (3). Nothing missing *above* it can pull the level below that floor. The tell of this failure is reasoning of the form *"mechanics are solid, so Bloom 2; the trade-off gap is a calibrated ceiling"* — the mechanics were not the evidence, the usage was, and usage is rung 3.
- **Ceiling.** An honestly-admitted gap ("I do not know the trade-offs") keeps 4-5 off the table. It caps; it does not lower the floor.

A floor is not a landing spot. When the learner reached a rung *above* the floor, record the rung they reached — the floor only ever prevents scoring lower, it never argues for scoring at 3. The tell of *this* failure is reasoning of the form *"the trade-offs are what pushed it past comprehension into application"*: trade-offs do not push an answer *into* rung 3, they push it past rung 3. An answer with no gap to cap has no ceiling, so the highest rung stands unmodified.

Score what the learner *produced*, then subtract only for what they could not reach — never the reverse, and never below the floor.

**Precedence: an *unowned* explanation is not a clean explanation at rung 1.** The any-rung rule governs explanations that are *thin* — and thin is the normal case, so this exception must stay narrow. It fires on one signal only: **the learner cannot re-express the content a second way.** Asked to say it differently, give an analogy, or apply it to a fresh case, they return the same words, or admit they have no other phrasing. That is fluency without a model, and it is the one case where an answer can be verbally correct and still evidence nothing. Then the grade is **`partial`**, whatever rung it caps at — `correct` would *lengthen* the interval on a concept the learner just failed to own, spacing a parrot further apart for parroting; `incorrect` would claim forgetting that was never demonstrated. `partial` holds the box and re-tests tomorrow (`spaced-repetition` KB). This is the call `/reflect` Phase 2 already makes — one grading vocabulary across the plugin. Capping the level alone does not do it: `--tested-bloom 1` with `result: correct` still promotes.

**What this exception does NOT reach** (1.14.x — the precedence rule regressed `grade-apply-band` on its first run, in the mirror image of the 1.12.2 failure): a learner who **admits a boundary** is not unowned. "I do not know the trade-offs — I would just index whatever I query," said after correct mechanics and working usage, is honest self-report plus demonstrated application: `correct`, capped at the apply rung, exactly as the any-rung rule says. Hedging *at the edge of what they know* is calibration, not parroting; skipping a step they never claimed is a bounded rung, not a skipped step. If the learner restated the mechanics in their own words even once, the exception does not apply no matter what else they could not reach.

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
- Time pressure ("I need to ship this") — just answer the question directly; analogy ladders cost time.

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
