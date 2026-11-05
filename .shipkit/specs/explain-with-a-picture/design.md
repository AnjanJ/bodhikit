# Design: Explain with a picture

## Approach
One new section in the `evidence-kinds` KB, *Explaining with a picture*, replaces the clause
"a diagram described in words" (line 34). It says when a picture fits, what form it takes,
that it comes with words, and that it stays out of the check. Code sessions never load that
KB, so code is untouched by construction. `/teach` gains no bytes. No field, no subcommand:
a picture is never evidence, so `bodhi-state` has nothing to record. Two transcript
scenarios, built detector-first, hold the rule.

## Decision: The rule lives in the `evidence-kinds` KB   (→ REQ-1, REQ-5)

**Context.** `/teach` is at 18,052 of 18,432 bytes (lint rule 49). The product non-goal keeps
code as it is. The learn-anything design already routes all non-code teaching through one
KB that code sessions never load.

**Alternatives.**
1. A section in the `evidence-kinds` KB.
2. A new `skills/teach/references/picture.md`, with a one-line pointer in `/teach`.
3. Inline in `/teach`, after trimming other prose to make room.

**Case for 1.** Code cannot reach it: `assert_code_never_loads_kinds` already fails any code
session that loads the KB. It costs `/teach` nothing, and it sits beside the rules it
modifies (examples, checkpoints, line 34).

**Case against 1.** Every off-code fire pays for the section, about 1 KB, even when the
concept needs no picture. Extending the rule to code later means moving it. And the KB grows
toward the size where it should be split.

**Decision.** We chose option 1.
**Falsifiability.** We would reverse this, moving the rule to a reference file loaded only
when needed, if the `evidence-kinds` KB passes 14 KB.
**Fired-if.** `test "$(wc -c < skills/evidence-kinds/SKILL.md)" -gt 14336`

## Decision: Plain-text diagrams and traces in a `text` fence only   (→ REQ-1, REQ-2)

**Context.** BodhiKit runs in a terminal (Claude Code, Codex), in ChatGPT and in Cowork. Only
some of these render Mermaid or HTML, and the Artifact tool is off in at least one real setup.
The non-code detector flags fences tagged with a programming language, not `text`.

**Alternatives.**
1. Plain-text diagrams and step-by-step traces in a `text` (or untagged) fence, with the
   same content in words.
2. Mermaid diagrams.
3. An HTML file written into the learner's `notes/`.

**Case for 1.** It renders the same on every host, it can be read aloud through its words
(REQ-2), it never reads as code to the detector, and it is cheap to verify by eye.

**Case against 1.** Some structures are hard to draw in text: a dense graph, anything that
needs curves or colour. Text art can also misalign in a proportional font. A learner used to
NotebookLM's visuals may find it plain.

**Decision.** We chose option 1.
**Falsifiability.** We would reverse this, adding a richer form for one host, if the
maintainer's trial or an outside learner's issue names a concept a text picture could not
show.
**Fired-if.** manual

## Decision: The picture stays out of the check   (→ REQ-3, REQ-4)

**Context.** Karpathy's formats lower the effort of understanding. Retrieval is what makes
learning last, and it needs effort. Bastani et al. (PNAS 2025) found that help which raised
in-session scores cut later unassisted scores by 17%.

**Alternatives.**
1. The Checkpoint and retention questions never repeat the diagram. A learner may still be
   asked to draw or complete their own.
2. A check may show the diagram with a part missing ("what goes here?").
3. No rule: the tutor decides per question.

**Case for 1.** The answer then comes from memory, which is what the review schedule
measures. Asking the learner to draw the structure themselves stays allowed, and it is
generation, the stronger task.

**Case against 1.** "Complete the diagram" is a real, useful question type, and option 1
forbids showing even part of the picture. Some trace questions ("what is the state after
step 3?") need the steps before them, which the tutor must then give in words.

**Decision.** We chose option 1.
**Falsifiability.** We would reverse this, allowing option 2, if in the first sweep of the
picture scenario (`BODHI_EVAL_RUNS=3`) the tutor cannot ask an answerable check without the
diagram in 2 or more of the 3 runs.
**Fired-if.** manual

## Decision: The concept decides, not a learning style   (→ REQ-1)

**Context.** "I'm a visual learner" is a common request. The research does not support
matching instruction to a stated learning style (Pashler et al., *Learning Styles: Concepts
and Evidence*, Psychological Science in the Public Interest, 2008; to be opened and
confirmed in T3).

**Alternatives.**
1. A picture when the concept is about how parts relate or how something changes over time.
2. A picture when the learner says they prefer pictures.
3. A picture in every explanation.

**Case for 1.** It follows the content, which is what the multimedia research measures
(Mayer, *Multimedia Learning*; to be confirmed in T3). It keeps most explanations in words.

**Case against 1.** A learner who asks for a picture of a concept outside those two kinds
gets one only because the rule does not forbid it, not because it is advised. Classifying a
concept as "about relationships" is a judgment the model can get wrong.

**Decision.** We chose option 1.
**Falsifiability.** We would reverse this if a controlled study shows that matching the
format to a learner's stated preference improves delayed recall.
**Fired-if.** manual

## Data / interface changes
None. No tracking field, no `bodhi-state` subcommand, no change to `/teach`. The KB section
replaces one clause and adds about 1 KB. REQ-4 holds because `record-review` runs only on a
graded answer, and the eval checks that.

## Evidence, stated in the KB (→ REQ-6)
Tier: weak. The one controlled test of LLM-generated visuals found (Noviello et al.,
*AI-Generated Traces for Novice Programmers*, arXiv:2606.03288, 2026) reports "selective…
context-dependent and short-term" benefits. Whether a picture helps BodhiKit's learners
cannot be read from `docs/outcomes.md`, because no field records which lessons had one.
That is out of scope by choice: a field would be a schema change under the freeze.
