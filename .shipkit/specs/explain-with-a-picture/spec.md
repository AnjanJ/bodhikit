# Spec: Explain with a picture

> Spec accepted at commit `2229817` on karpathy-followups.
> Status: open
> Paths: skills/evidence-kinds/, dev/eval/, README.md

## Purpose
Off code, let the tutor explain a concept about structure or change with one plain-text
diagram or step-by-step trace, and keep the picture out of the check. Karpathy's format
advice is about understanding output with less effort. Learning needs the effort at
recall, so the picture lowers the cost of the explanation and never the cost of the check.
Gated: nothing is built until the maintainer's trial (`tasks.md`, *Gate*) shows the need.

## User stories
- As a learner on a non-code subject (an argument's structure, a genetic cross, a process
  in a cell), I want to see how the parts relate, so that the explanation is easier to follow.
- As the same learner, I want to be asked about it without the picture in front of me, so
  that what I get right is what I remember, not what I am looking at.

## Requirements (EARS)
- **REQ-1.** While a concept's effective evidence kind is not `code` and the concept is
  about relationships between parts or about state changing over time, `/teach` shall show
  at most one plain-text diagram or step-by-step trace in the I-Do explanation, in a `text`
  or untagged code fence.
- **REQ-2.** When the tutor shows a diagram or trace, the same message shall state its
  relationships or steps in words.
- **REQ-3.** When the tutor asks a Checkpoint or retention-check question on a concept
  explained with a diagram, the question's message shall not repeat that diagram.
- **REQ-4.** If the learner has only looked at a diagram or trace and given no graded
  answer, then the tutor shall not record a review.
- **REQ-5.** While a concept's effective evidence kind is `code`, `/teach` shall behave as it
  does today: no evidence-kinds load, and `t_golden_code_path` holds.
- **REQ-6.** The `evidence-kinds` KB shall name the research behind the rule and its
  evidence tier, including that the evidence for LLM-made visuals is weak.
  [untested: prose, verified by reading and by the lint's KB-citation rule]

## Out of scope
HTML, images, Mermaid, video, a wiki, any change on code, and any new tracking field or
`bodhi-state` subcommand. Choosing between "diagram" and "plain words" by a learning style:
the choice follows the concept, never the learner.
