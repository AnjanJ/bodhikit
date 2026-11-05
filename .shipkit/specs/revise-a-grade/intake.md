# Intake: Revise a grade

> Intake taken on 2026-11-06.

## Request
Let the tutor revise a review it recorded wrongly earlier the same session (the learner
shows the grade missed something they actually said), so the schedule, streak and level end
where the honest grade puts them. Flow agreed with the maintainer on 2026-11-06: the
`state-schema` KB first, then `scripts/bodhi-state` and `dev/eval/test_bodhi_state.py` in the
same change, then the skills (and `state-ops` if the operational surface changes). A wrong
grade is a bug, so the feature freeze does not apply.

Reproduced on 2026-11-06 on a scratch copy of `dev/eval/fixtures/v2-project`. With B-tree
indexes due at Box 3, `record-review incorrect` then `record-review correct` on the same day
leaves the concept at Box 1, next review tomorrow (`boxHeld: already reviewed today`). A
single honest `correct` gives Box 4, next review 2026-11-20. The live eval `grade-regrade`
(commit `2229817`) asserts the honest outcome and is expected to fail until this lands.

## Serves goal
None directly. It is a correctness fix. It protects the delayed-review recall that the
goal "Retention holds outside code" measures, since a wrong grade moves that number.

## Conflicts found
- **Bloom ratchet, `CLAUDE.md` *Glossary*:** "`bloomLevel` only rises". A wrong `correct`
  revised down lowers the level. Decided: allowed, as a correction and not as forgetting. The
  glossary and the `state-schema` KB will say that a revision restores the level the concept
  had before the wrong entry, and that nothing else lowers it.
- **Non-goal, `.shipkit/product.md`:** "No change to how a code concept is taught, graded or
  evidenced." Read as: `record-review` keeps its exact behaviour and `t_golden_code_path`
  holds. The new path runs only when a grade is revised, on any kind. Stated to the
  maintainer on 2026-11-06, with no objection.
- **Decision 0004** (`record-review` counts a newly learned concept in the profile): a
  revision that undoes or makes a crossing of level 3 must move the count to match.
- **`feynmanPassed` is set-never-unset** (`state-schema` KB): untouched. A wrong
  explain-back pass is out of scope here.

## Answers
- Which wrong grades may be revised? Both directions: too low and too high.
- When? Same day, and only the concept's latest graded entry.
- The wrong entry? Kept in the history, marked revised, and skipped by every reader.

## Assumptions made
- The tutor revises. The learner cannot run `bodhi-state`. What triggers a revision is the
  `feynman-technique` KB's existing pushback rule (`skills/feynman-technique/SKILL.md:55`):
  pushback that names something the learner actually said is re-read and regraded, while
  pushback that only asserts adequacy leaves the grade standing (`grade-pushback`).
- A revision carries a reason (what the grade missed), so the history says why.
- A relearning retry (`--retry`) is never the entry revised. It moves nothing.

## Out of scope
Revising an entry from an earlier day, or one with a later entry after it. Revising
`set-feynman`, `record-session` or `/forget`. Any way for the learner to revise a grade
without the tutor.
