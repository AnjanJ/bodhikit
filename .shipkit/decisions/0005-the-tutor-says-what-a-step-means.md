# 0005: The tutor says what a step means, not what the engine printed

> Decided 2026-11-06. Spec `no-internals-in-learner-text`.

**Context.** On the 1.26.0 tree (`8f97f63`), two live transcripts showed the learner the
state engine's own words between tool calls. "The brief says this is a first exposure
(`pretestApplies: true`)" in `teach-vocabulary` came from `session-brief`'s output.
"`bodhi-state verify` reports no errors" in `kind-intake-change` named the script. That is
2 of the 19 stream transcripts kept that day. Decisions 0002 to 0004 dealt with the write
commands: a renamed key was still read aloud (0002), and the leaks stopped only when the
key went away (0004). The read commands cannot lose their keys, because the skills branch
on them: `pretestApplies` decides `/teach`'s Phase 2, and `isReteach` decides the reteach
duty. Decision 0003's reversal condition covers box numbers from read commands, not key
names, so it does not fire.

**Alternatives.**
1. A voice rule in the `teaching-personality` KB, which every skill and agent loads. Text
   between tool calls reaches the learner, so it says what a step means for them and never
   names a command, an output key or a tracking field.
2. Change the read commands' output, for example by renaming the keys or nesting them
   under a name that says they are not for the learner.
3. Change nothing, and only count the leaks.

**Case for option 1.** The leak is the tutor narrating its own reasoning, not a key that
invites repetition: its next message restated the same brief in words ("first exposure,
pretest applies"). Voice
rules live in that KB by the authoring contract, and it has room at 8.3 KB. One rule covers
every command, including ones not yet written. This is not an executor-discipline bug: no
file write is described without being done, and none is wrong. The CLAUDE.md rule against
louder markdown applies to those bugs.

**Case against option 1.** Prose can be ignored, and decision 0002 showed a model
narrating a key it had been told about. A rule in a KB the model has already loaded may
not reach the moment between two tool calls. Option 2 acts at the source the way 0004 did,
and 0004 is the one change that worked.

**Decision.** We chose option 1, with the name check running in every transcript scenario
(the spec's T1) so the rate is measured, not guessed.
**Falsifiability.** We would move to option 2, for the command the leaked name came from,
if 2 or more of the next 10 live stream transcripts that run the check still show a
state-engine name in learner text.
**Fired-if.** manual
