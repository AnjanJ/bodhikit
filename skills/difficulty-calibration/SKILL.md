---
description: "Difficulty calibration — where to pitch a task (Vygotsky's ZPD), how to scaffold it (Sweller's cognitive load), and which difficulties to keep (Bjork): the three calibration frameworks every teaching phase loads together"
user-invocable: false
---

# Difficulty Calibration

Three frameworks that answer one question — *how hard should this be, right now, for this learner?* — and are loaded together because no teaching phase uses one without the others: the ZPD says where to pitch a task, cognitive-load theory says how to scaffold it and when to stop, and desirable difficulties says which kinds of hard are worth keeping. Each section keeps its own evidence tier and primary sources.

## Zone of Proximal Development (Vygotsky)

**Evidence tier: strong-theoretical.** ZPD is a theoretical construct, but the scaffolding-and-fading research it inspired is well-supported — see *Cognitive Load Theory* below for the experimental version of the same claim.

### Three Zones

1. **Can do alone** (current level): Tasks requiring no help. Too easy = no learning.
2. **Can do with guidance** (ZPD): Tasks achievable with support. THIS IS WHERE LEARNING HAPPENS.
3. **Cannot do even with help** (beyond reach): Tasks causing cognitive overload. Too hard = frustration.

### Detecting the Learner's Zone

**In the ZPD (productive struggle):**
- Can articulate what they are trying to do but unsure how
- Make partial progress and ask specific questions
- With a small hint, make forward progress
- Errors show partial understanding (correct approach, wrong details)

**Below the ZPD (too easy):**
- Complete tasks quickly without engagement
- Show boredom or impatience
- Do not learn anything new from the exercise

**Beyond the ZPD (overwhelmed):**
- Cannot articulate what they are confused about
- Hints do not help — they cannot act on guidance
- Show frustration, disengagement, or random guessing
- Cognitive overload: too many new concepts at once

### Scaffolding Strategy

Use the **Gradual Release of Responsibility** model:

1. **I Do** (Modeling): Tutor solves a problem while thinking aloud
2. **We Do** (Guided Practice): Learner and tutor work through a problem together
3. **You Do Together** (Collaborative): Learner attempts with tutor available for questions
4. **You Do Alone** (Independent): Learner solves independently, tutor reviews afterward

**Scaffolding must fade as competence grows.** The goal is independence.

## Cognitive Load Theory (Sweller)

**Evidence tier: bedrock.** The worked-example and expertise-reversal effects are among the most-replicated findings in instructional design.

Working memory holds ~4 chunks; learning fails when a task's *intrinsic* load (the concept itself) plus *extraneous* load (everything else the learner must juggle) exceeds it. For novices, a full problem is mostly extraneous load; for experts, scaffolding itself becomes the extraneous load.

### The Worked-Example Effect

Novices learn more from **studying a worked solution** than from solving the equivalent problem — problem-solving search consumes the working memory that schema-building needs. This is among the most-replicated findings in instructional design (Sweller & Cooper 1985; Sweller 1988).

### Faded Scaffolding (the canonical sequence for Bloom 1-2)

Do not jump from explanation to a blank exercise. Fade in three steps:

1. **Worked example** — a complete, annotated solution the learner studies and explains back ("why does step 2 come before step 3?").
2. **Completion problem** — the same shape with 1-2 key steps removed; the learner fills the gaps.
3. **Full problem** — the learner constructs the whole solution (a *different* surface context — see the *Desirable Difficulties* variation rule below).

One concept can move through all three in a session; a struggling learner can stay at step 2 across sessions without shame.

### The Expertise-Reversal Effect

Scaffolding that helps novices actively *hurts* intermediate-and-above learners (Kalyuga et al. 2003) — redundant guidance becomes extraneous load and crowds out generation. Bloom 3+ learners get completion problems or full problems only; never re-introduce worked examples for a concept the learner already applies. This is why the scaffolding ladder in `/teach` and `/practice` is keyed to Bloom level.

### Application Rules

- Bloom 1-2: faded sequence above. The exercise README *is* step 1+2 (worked example + completion), not a TODO list.
- Bloom 3-4: completion problems or test-driven specs; no worked example.
- Bloom 5-6: problem statement only. Absence of scaffolding is the point.
- Split attention: keep code and its explanation together (annotate inline), never "see the explanation above."
- One new concept per example; everything else in the example must already be mastered.

**Primary sources:** John Sweller, *Cognitive load during problem solving* (Cognitive Science, 1988); Sweller, Ayres & Kalyuga, *Cognitive Load Theory* (2011); Kalyuga et al., *The Expertise Reversal Effect* (2003).

## Desirable Difficulties (Bjork)

**Evidence tier: bedrock** for retrieval practice and spacing (the two highest-utility techniques in Dunlosky et al. 2013); interleaving and generation are well-supported with more moderate effect sizes.

### The 5 Key Difficulties

1. **Spacing**: Distribute practice over time (not cramming)
2. **Interleaving**: Mix different problem types in a session (not blocking)
3. **Retrieval practice**: Recall from memory (not re-reading)
4. **Generation**: Produce answers before being shown them
5. **Variation**: Practice in varied contexts (not identical conditions)

### Interleaving as a test condition

Interleaving helps most where it forces a choice: mixed practice makes the learner decide *which* idea a problem needs, a step blocked practice hands over by announcing the topic (Rohrer & Taylor, *The shuffling of mathematics problems improves learning*, 2007). A meta-analysis of 59 studies puts the average benefit at a moderate g ≈ 0.42, largest for categories that look alike — and weak for material that shares little (Brunmair & Richter, *Similarity matters*, 2019). So a review question that names its concept tests recall of an answer the learner has already been given half of. `/quiz` states the situation, not the concept, and puts confusable concepts back to back; a correct there is recall **and** discrimination at once, with no extra field to track.

### The Paradox

These all SLOW DOWN apparent progress but produce significantly STRONGER long-term retention and transfer. Learners often rate these methods as less effective precisely because the struggle feels bad — even when outcomes are superior.

### Pretesting (Kornell, Hays & Bjork 2009)

A special case of generation: asking the learner a question **before** the material is taught — one they will probably get wrong — measurably improves learning of the subsequent explanation. The failed retrieval attempt primes the relevant schema and makes the correction stick. Rules:

- One question, asked with explicit permission to be wrong: "You have not seen this yet — take a guess anyway. Being wrong here is the point."
- Never grade or record the pretest answer (it is priming, not assessment — no `reviewHistory` entry).
- The explanation that follows should explicitly resolve the pretest: "Remember your guess? Here is where it was close and where it breaks."

`/teach` Phase 2 opens with a pretest before the I-Do explanation.

### Vocabulary Preview (Marzano; Beck, McKeown & Kucan; Ausubel)

**Evidence tier: strong** for direct vocabulary instruction — teaching the words a passage uses, before the passage, raises comprehension of that passage with a large effect (Stahl & Fairbanks, *The effects of vocabulary instruction: a model-based meta-analysis*, 1986) — and **moderate** for the advance-organizer framing (Ausubel, *The use of advance organizers in the learning and retention of meaningful verbal material*, 1960; Luiten, Ames & Ackerson's 1980 meta-analysis finds a small, consistent benefit). Marzano's six-step process (Marzano & Pickering, *Building Academic Vocabulary*, 2005) is the classroom form: the teacher describes the term with an example, the learner restates it in their own words, then uses it. Beck, McKeown & Kucan (*Bringing Words to Life*, 2002) sort words into tiers; the ones worth previewing here are the domain's own (*Tier 3*: `index`, `planner`, `isolation level`), not everyday words.

Why it matters for code: a lesson that introduces six new terms in passing asks working memory to hold the words *and* the idea — extraneous load in Sweller's sense. Naming the words first turns them into labelled slots the explanation fills. Rules:

- **After the pretest, before the explanation.** The pretest needs the learner not to have seen the material; a term list would leak the answer. The preview is the bridge from the guess into the I-Do.
- **Three to six terms, one plain line each,** every one a word the explanation will actually use, defined without another new term. Mark the ones the learner has met before (`progress.md`, the session brief). A module's `**Key terms:**` line in the plan, when `/learn` wrote one, is the starting list.
- **Then use exactly those words.** A term that was not previewed is defined at its first use, not after.
- **The checkpoint retrieves a word, not a definition:** "use *X* in a sentence about your own code" (Marzano step 2). A recited definition is the parrot the `feynman-technique` KB already grades; a sentence about their code is the word in use.
- **The revision sheet carries the list** (`## Words`), with the learner's own restatement where they gave one, so tomorrow's reading has the labels.
- **On a re-teach, preview only the terms the learner stumbled on.** Nothing is recorded; this is instruction, not assessment.

### Application

- Never present 10 problems of the same type in a row (interleave)
- After teaching a concept, ask the learner to solve a problem BEFORE showing examples (generation)
- Ask one question BEFORE teaching at all (pretesting, above)
- Mix old and new concepts in every session (spacing + interleaving)
- Vary the format: sometimes explanation, sometimes code, sometimes debugging (variation)
