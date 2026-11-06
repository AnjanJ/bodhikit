# Spec: No state-engine internals in learner text

> Spec accepted at commit `f0c4d52` on master (the maintainer asked on 2026-11-06 for the 1.26.1 fix to be carried through without a separate approval stop).
> Status: shipped
> Paths: skills/teaching-personality/, dev/eval/, .shipkit/decisions/

## Purpose
The learner should only ever see the lesson, never the plumbing. On the 1.26.0 tree the
tutor wrote, between tool calls where the learner sees it, "The brief says this is a first
exposure (`pretestApplies: true`)" (`teach-vocabulary`) and "`bodhi-state verify` reports no
errors" (`kind-intake-change`). Decisions 0002 to 0004 removed such words from the write
commands' output, but read commands still print the keys the skills branch on, and only
two scenarios check for them. This is a bug fix, so the feature freeze does not apply.

## User stories
- As a learner, I want the tutor to tell me what is happening in my own terms ("this is
  new to you, so a guess first"), so that I am not reading a log.
- As the maintainer, I want every scenario with a full transcript to fail on a leaked name,
  so that I can count the leak rate instead of finding leaks by hand.

## Requirements (EARS)
- **REQ-1.** When a scenario that saves a stream transcript is asserted, the harness shall
  fail it if learner-facing text names a hyphenated `bodhi-state` subcommand, `bodhi-state`
  itself, or one of its current or retired output keys.
- **REQ-2.** The check shall not fail on a tool call, a tool's output, or the harness's
  closing recap.
- **REQ-3.** While a BodhiKit skill runs, the tutor's text between tool calls shall name no
  state-engine command, output key or tracking-file field.
- **REQ-4.** When the tutor explains a step the state engine decided (a pretest, a gate, a
  review date), it shall say what the step means for the learner in plain words.
- **REQ-5.** `teach-vocabulary` and `kind-intake-change`, the two scenarios that leaked on
  the 1.26.0 tree, shall pass their live runs on the tree that builds this.

## Out of scope
Changing what any `bodhi-state` command prints. The learner's own files (`revision/…`, an
exercise folder) may still be named. Codex and bodhi-cli transcripts carry no tool output,
so REQ-1's attribution of a leak to a command is Claude-only.
