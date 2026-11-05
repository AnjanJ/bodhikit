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

**Decision.** We chose option 3.
**Falsifiability.** We would move to option 2 if `newlyLearned`, or the profile bump it triggers,
is narrated to the learner in 2 or more of the next 10 live `kb-load` or `/teach` transcripts.
**Fired-if.** manual
