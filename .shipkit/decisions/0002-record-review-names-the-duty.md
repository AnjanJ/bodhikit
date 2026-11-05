# 0002: `record-review` names the duty, not the rung: `crossedBloom3` becomes `newlyLearned`

> Decided 2026-11-05. Amends learn-anything REQ-1's "exactly as 1.24.1" for one output key.

**Context.** Since 1.14.0, `record-review` reports `crossedBloom3: true` when a write moves a
concept's level from below 3 to 3 or above. It is the one trigger for `/teach`'s
`bump-profile --counter totalConceptsLearned`. On the 1.25.0 release tree (2026-10-22), the
`kb-load` eval caught the tutor telling the learner, between tool calls, "The answer crossed
Bloom 3 (crossedBloom3: true), which per state-ops triggers the profile counter bump". That is
a bare Bloom number in learner-facing text, against CLAUDE.md's rendering rule. The key carries
the rung in its name, and the skills quote it, so the model repeats it. CLAUDE.md says not to
fix an executor-discipline bug with louder prose. `t_golden_code_path` compares
`record-review`'s output byte for byte against the 1.24.1 engine's recording, which cannot be
re-recorded, so any change to the key trips the REQ-1 tripwire.

**Alternatives.**
1. Keep the key, and tell the skills not to narrate it.
2. `record-review` runs the profile bump itself on the crossing write, and the key goes away.
3. Rename the key to the duty it signals, `newlyLearned`. The golden comparison maps that one
   key in `record-review` output and stays byte-strict for everything else.

**Case for option 3.** It removes the number from the only text the model copies, without
adding prose. The meaning, the trigger and every file write stay as they are, so the golden
files still prove the engine is unchanged for code, apart from one key's name. It is the
smallest change that reaches the cause.

**Case against option 3.** The model can still narrate `newlyLearned: true`. That is
internal vocabulary, though not a rung. Option 2 would remove the duty from the skills
entirely, which is closer to "skills judge, the script records". The mapping in the golden
comparison is a hand-made exception to a byte-for-byte check, and each such exception
weakens what the tripwire proves.

**Why not option 2.** It changes behaviour. `/quiz`, `/continue` and `/practice` crossings would
start counting toward `totalConceptsLearned`, which today only `/teach` bumps. The profile file
would change on writes where 1.24.1 left it alone, so the golden files would differ in their
files, not only in one key.

*Corrected 2026-11-05, after the live `kb-load` runs.* The premise above is wrong. The
state-ops KB calls the key "the one trigger" for `bump-profile --counter
totalConceptsLearned`, so every skill that loads state-ops bumps on a crossing, `/quiz`
included. A 2026-11-05 `kb-load` run did so, and so did the 2026-10-22 run that caught the
leak. Option 2 would not start counting new crossings. What it would still change is the
golden files: the profile write would move inside `record-review`, on calls where 1.24.1 left
the profile alone because no skill was running. Counting every crossing is correct. The
ratchet means a concept crosses once, whichever skill grades it. The decision stands; this
reason against option 2 is weaker than it read.

**Decision.** We chose option 3.
**Falsifiability.** We would move to option 2 if `newlyLearned`, or the profile bump it triggers,
is narrated to the learner in 2 or more of the next 10 live `kb-load` or `/teach` transcripts.
**Fired-if.** manual

*Status 2026-11-06: the reversal condition is met.* Of the first six live `kb-load` runs after
the rename (three on 2026-11-05, three on 2026-11-06), four told the learner about
`newlyLearned` or the profile bump it triggers (`dev/eval/README.md`, `kb-load` row). The
condition names option 2; it is not adopted until the maintainer decides.
