# Intake: Explain with a picture

> Intake taken on 2026-11-06.

## Request
After a review of Andrej Karpathy's advice on LLM output formats (2 Oct 2026: controlled
English, then diagrams, then interactive HTML, then explainer video), the maintainer said
"yes" to a short spec for a rule that lets `/teach` explain with a plain-text diagram or a
step-by-step trace, off code first. Its implementation waits on a hand-run trial. The rule:
the picture helps the explanation, never the check.

## Serves goal
Retention holds outside code — metric: delayed-review recall on non-code subjects minus code
subjects in `docs/outcomes.md`; target: within 10 points; by: 2026-12-31

## Conflicts found
- **Feature freeze, `CLAUDE.md` *Feature freeze*.** Decision 0001 admits only what
  `learn-anything/tasks.md` lists, and this is not on it. It can be built only under the
  freeze's condition (b): the maintainer hits the gap in a real learning session. Decided:
  the spec is written now, and implementation is gated on that trial (T0 in `tasks.md`).
- **Non-goal, `.shipkit/product.md`:** "No change to how a code concept is taught, graded or
  evidenced." Decided: off code only. Code keeps its current behaviour, and
  `t_golden_code_path` must hold.
- **Current rule, `skills/evidence-kinds/SKILL.md:34`:** "a diagram described in words". This
  feature changes that line, so the change is deliberate, not drift.
- **Lint budget, `dev/check.sh` rule 49:** `/teach` is at 18,052 of 18,432 bytes, so the rule
  cannot live in `/teach`.
- No open spec overlaps. `learn-anything` is `shipped`, and its REQ-14 already lists "a
  diagram" among a lesson's subject material.

## Answers
- Build it now, or spec it and wait? Spec now. The build waits on the hand-run reading-loop
  trial in the political-theory project (the maintainer's "yes to all", 2026-11-06).
- Which formats? Plain-text diagrams and step-by-step traces only. No HTML, images, video or
  wiki (the same reply, item 5).

## Assumptions made
- The rule lives in the `evidence-kinds` KB, which code sessions never load
  (`learn-anything/design.md`, *Non-code teaching lives in one KB that code sessions never
  load*). This keeps code untouched by construction.
- A diagram goes in a `text` (or untagged) fence. The no-code detector only flags fences
  tagged with a programming language (`dev/eval/assert_scenario.py`, `CODE_FENCE_RE`), so a
  diagram does not read as code.
- Evidence is weak, and the KB says so. The one controlled test of LLM-made visuals found
  (Noviello et al., arXiv:2606.03288, 2026) reports "selective… context-dependent and
  short-term" benefits.

## Out of scope
HTML pages, images, Mermaid that only some hosts render, narrated video, an LLM-maintained
wiki, any change on code, and any new tracking field.
