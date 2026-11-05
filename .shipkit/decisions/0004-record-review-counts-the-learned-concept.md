# 0004: `record-review` counts a newly learned concept itself; the `newlyLearned` key goes

> Decided 2026-11-06. Supersedes 0002, whose reversal condition was met.

**Context.** Decision 0002 renamed `record-review`'s `crossedBloom3` output key to
`newlyLearned`, so the tutor would stop reading a Bloom number aloud. The number went, but the
narration stayed. In four of the first six live `kb-load` runs after the rename, the tutor told
the learner about the key or the duty it triggers, for example "`bump-profile --counter
totalConceptsLearned` (triggered by `newlyLearned`, now 3)". 0002 named this as its reversal
condition (2 in the next 10). The key exists only so a skill can run `bump-profile --counter
totalConceptsLearned` after a crossing write: `/teach` step 4, `understanding-only.md`, and
state-ops, which makes every skill that loads it do so (0002's 2026-11-06 correction). The
script already counts one stat itself: `touch-state` bumps `totalSessions` on the first touch
of a day, and state-ops says no skill calls `bump-profile` for it.

**Alternatives.**
1. Keep 0002. The narration is partly the eval harness: its prompt says to complete every
   tracking update, and the runs answer with a "Bookkeeping" receipt.
2. `record-review` increments `totalConceptsLearned` on the write that crosses the line, and
   prints no key for it. The skills drop the duty, and `bump-profile` refuses that counter.
3. Keep the key, and tell the skills not to mention it to the learner.

**Case for option 2.** With no key and no duty, nothing about it reaches the tutor, so there is
nothing to narrate. One fewer step a model can skip or repeat. It counts what is counted today,
since every skill that loads state-ops already bumps on a crossing, and the ratchet lets a concept
cross only once. It follows the `touch-state` precedent. Option 3 is louder prose, which CLAUDE.md
rules out for an executor-discipline bug.

**Case against option 2.** A review write now also writes the cross-project profile, a second
file. A project with no profile (one not made by `/learn`) must still record its review, so the
count is skipped there without a word. The golden comparison needs a file rewrite for
`.bodhi-profile.json`, not only output rewrites. A model that remembers the old duty could
bump the counter twice, which is why `bump-profile` must refuse the counter. A harness-driven
receipt may still mention "the profile" in general terms.

**Decision.** We chose option 2.
**Falsifiability.** We would revisit this if a live eval's file state shows
`totalConceptsLearned` moving by anything other than the number of crossing writes, or if the
tutor still tells the learner about the profile counter in 2 or more of the next 10 live
`kb-load` or `/teach` transcripts. That would mean the narration comes from the harness's
receipt, not from the key.
**Fired-if.** manual
