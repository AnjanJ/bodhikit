# 0001: BodhiKit teaches any subject, and takes the learner's word only where it cannot check

> Decided 2026-10-19. Supersedes the feature freeze in `CLAUDE.md` (1.13.0) for this
> initiative. Spec: `.shipkit/specs/learn-anything/`.

**Context.** BodhiKit was a coding tutor. Its honesty rested on a referee: code runs or it does
not. The 1.13.0 freeze allowed new tracking fields only when a second real user asked or when
the maintainer hit a gap in a real session. The maintainer hit that gap in a political-theory
course (2026-10-16), and chose on 2026-10-19 to make BodhiKit a learning tool for every subject,
mainly on Claude. Where the tutor cannot see the evidence, it takes the learner's word. Coding
must keep working exactly as before.

No chat tutor tracks spaced review or a stated definition of mastery (research, October 2026).
None schedules practice for performed skills, labels how each piece of evidence was judged, or
keeps the learner's record in files the learner owns.

**Alternatives.**
1. Stay a coding tutor, keeping only the 1.24.1 fixes for written subjects.
2. Teach any subject, but only where the tutor can check the work: code, problems and writing.
   Performed skills would be taught as knowledge only, and could never reach *Solid*.
3. Teach any subject, and take the learner's word for performed skills. The word is labelled as
   the learner's account everywhere it shows, and counts only toward "used it in practice". The
   level, the streak, the box and the explain-back stay tutor-graded.

**Case for option 3.** It covers every subject a learner brings. It keeps *Solid* meaningful,
because only one of its five conditions can rest on the learner's word, and only for a skill
the tutor cannot see. It owns the gaps no current product fills.

**Case against option 3.** It ends the freeze's discipline: one maintainer now carries four
evidence kinds, a safety rule, a second host (Cowork) and a larger eval matrix. Self-report is
the weakest evidence in the field (Dunlosky & Rawson 2012; Zell & Krizan 2014), so *Solid* on a
performed skill is a weaker claim than *Solid* on code, however clearly it is labelled. It also
moves BodhiKit from a clear niche into competition with general study tools.

**Decision.** We chose option 3.
**Falsifiability.** We would reverse the self-report half, falling back to option 2, if concepts
whose *Solid* rests on `reported` practice fail their next delayed review at a recall rate at
least 20 points below concepts resting on observed work, over the first 30 such reviews. We would
also revisit the whole decision if, by 2027-01-31, no learner other than the maintainer has used
BodhiKit on a non-code subject (intake goal 1).
**Fired-if.** manual
