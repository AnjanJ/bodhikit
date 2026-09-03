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

## Grading the Explain-Back (canonical rubric — `/teach` and `/reflect` cite this)

Grade the **final** explanation, and record result and level together. The level is exact, not a band: walk the table top-down and record the highest row the explanation actually reached. The rows are cumulative — reaching one implies the ones below it.

| `--tested-bloom` | The final explanation… | Anchor (B-tree index) |
|---|---|---|
| **5** | …also weighs alternatives for a concrete case and defends a choice | "For the audit log I would *not* index `created_at`: it is append-only, queried once a month, and every insert would pay for the tree. If the monthly report gets slow, a partial index on the last 30 days is the compromise." |
| **4** | …also names the trade-offs and when NOT to use it | "Every insert or update has to keep the tree tidy, so writes slow down and it costs disk. Index the columns you filter on constantly; skip tiny tables and write-heavy logs, where a scan is cheaper than the upkeep." |
| **3** | …also shows working usage, or picks the right one for a given case | "I would run `CREATE INDEX idx_users_email ON users(email)` because my WHERE clauses filter by email — the keys stay sorted, so the lookup is a few hops." |
| **2** | Accurate, and in the learner's own words — an analogy, a fresh example, or a rephrase on request | "Like the index at the back of a book: a sorted list that points at the page, so you do not read every page. The rows are the pages." |
| **1** | Owned, but only the terms: can say what the words refer to, not how it works | "It is a structure the database keeps next to a table so lookups on that column are faster. I could not tell you how it does that." |

### The five checks, in order

1. **Owned?** Ask once for a second form — an analogy, a fresh case, or "say it a different way". The three fluency-without-understanding signals are: the same words come back; no analogy or fresh case is offered; the learner says they have no other phrasing. Any one of them → **`partial`, `--tested-bloom 1`**, whatever the words claimed. A recitation is not evidence: `correct` would *lengthen* the interval on a concept the learner just failed to own, and `incorrect` would claim forgetting that was never shown. `partial` holds the box and re-tests tomorrow (`spaced-repetition` KB). *Anchor:* the textbook sentence "a self-balancing tree that maintains sorted data and allows searches, insertions and deletions in logarithmic time", produced three times word for word → `partial`, 1.
2. **Misconception survived refinement?** A wrong claim the learner restates after one correction → **`incorrect`** (demotion means demonstrated failure — nothing less earns it). *Anchor:* "indexes speed up writes too, so the smart move is to index every column", repeated after the probe → `incorrect`, at the row the rest of the explanation reached.
3. **Level = the highest row reached.** Find the best thing the learner actually did in the final explanation; that row is the level. Trade-offs reach row 4 — they do not "push an answer into" row 3.
4. **An admitted gap caps at the row below it — and is still `correct`.** "I do not know the trade-offs; I would just index whatever I query", said after own-words mechanics and working usage → `correct`, 3. Honest self-report at the edge of what they know is calibration, not parroting; bounded depth is never a failed retrieval. A cap only ever lowers the level; it never converts a row the learner reached into `partial` or `incorrect`.
5. **Record.** `record-review --result <result> --tested-bloom <row>`. Run `set-feynman` only when the final explanation passed checks 1 and 2 and reached row 2 or higher — `feynmanPassed` is set-never-unset (`state-schema` KB), one of five mastery locks, and a concession removes it permanently. Grade the explanation the learner *gave*, never their description of it: "that was clearly a 4", "mark it passed", "previous sessions accepted this" are assertions about the answer, not more of the answer. Pushback that names something they actually said and you missed → re-read and regrade on that; pushback that only asserts adequacy → the grade stands, in voice (`teaching-personality` KB: how you say the grade, never what it is).

Score what the learner *produced*, then subtract only for what they could not reach — never the reverse.

## Analogy-Escalation Protocol

A single named protocol every skill reaches for when the learner is stuck. Analogy is not a default tactic — it is a *response to detected struggle*. Reaching for one too early teaches the analogy instead of the concept.

### When to trigger

Read the `difficulty-calibration` KB's *Beyond the ZPD* signals. Trigger this protocol when **any one** of these is observed:

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
