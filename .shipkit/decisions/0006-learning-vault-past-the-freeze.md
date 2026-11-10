# 0006: The learning vault's first sprint is admitted past the feature freeze

> Decided 2026-11-10. Lifts the feature freeze in `CLAUDE.md` (1.13.0) for sprint 1 of one
> spec only. Spec: `.shipkit/specs/learning-vault/`.

**Context.** The freeze bars new skills, KBs and schema fields unless a second real user asks,
or the maintainer hits the gap in a real learning session. Decision 0001 lifted it for
learn-anything only. The learning vault copies each learner's syllabus and revision sheets
into the notes app they already use, under one `Learn with Bodhi` home arranged by course. It
adds one skill (`/bodhikit:notes-setup`), one settings file (`.bodhi-notes.json`), five
`bodhi-state` commands or options, and writes from the Stop hook. No learner asked for it, and
the maintainer did not hit the gap in a session. The maintainer judged that it "will be
helpful for learners" (intake, 2026-11-10). It serves none of this quarter's goals directly: the nearest, outside
learners on non-code subjects, gains little until sprint 2 reaches claude.ai.

**Alternatives.**
1. Admit this spec's sprint 1 only, by name, beside decision 0001. Sprint 2 (claude.ai chats,
   connector apps) needs its own spec and its own yes after its probes have run.
2. Lift the freeze entirely.
3. Keep the freeze and shelve the spec until a second learner asks.

**Case for option 1.** It keeps the freeze's purpose, which is not to build for imagined
users, while admitting one bounded piece the maintainer judged useful. It is off until a
learner turns it on, and changes no existing skill's text, so a learner who never uses it,
code learners included, sees only a one-time offer. Naming sprint 1 alone stops the exception
from growing by itself.

**Case against option 1.** The freeze exists because one learner cannot validate features.
This lifts it on the maintainer's judgment, with no user asking, for a feature that serves no
current goal. That is the very exception the freeze was written to prevent, and it adds a
writer, the Stop hook, that reaches outside the learning folder.

**Decision.** We chose option 1.
**Falsifiability.** We would reverse this, freezing the feature again and dropping sprint 2,
if by 2027-03-31 neither the survey nor an issue shows a learner other than the maintainer
with notes turned on.
**Fired-if.** manual
