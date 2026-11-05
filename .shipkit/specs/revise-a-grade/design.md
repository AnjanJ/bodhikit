# Design: Revise a grade

## Approach
`record-review` saves what each concept looked like just before its latest review, in one
concept-level field. A new subcommand, `revise-review`, checks that the review to revise is
the concept's latest graded entry today. It marks that entry revised with a reason, puts the
concept back to the saved state, and applies the right grade through the same
`apply_review`. Every reader goes through one filter that drops revised entries. The skills
learn when to revise from a short rule in the `spaced-repetition` KB, beside the
same-day rule that causes the bug.

## Decision: Save the pre-review state on the concept, overwritten each review   (→ REQ-1, REQ-4, REQ-5)

**Context.** An entry records only `boxBefore`. The next review date, the L4+ streak, the
level (a ratchet: `max(current, tested)`), the last-reviewed date and the last result before
a review are lost once it is written. So the state before a wrong grade cannot be worked out
from the entry.

**Alternatives.**
1. One concept-level field, `beforeLastReview`, holding the date and the six fields as they
   were before the latest graded review. Each `record-review` overwrites it.
2. The same snapshot on every history entry.
3. Rebuild the concept by replaying its whole unrevised history from the start.

**Case for 1.** It is exact and small: one object per concept, not one per entry. It is only
ever needed for the latest entry today, which is all REQ-5 allows. Its date shows whether it
still applies.

**Case against 1.** It adds a field that `record-review` writes on every review. That changes
the file even when nothing is ever revised (REQ-9 holds for behaviour and output, not for
bytes). A concept reviewed before this ships has no snapshot, so its first review after the
upgrade cannot be revised until a new review writes one. Option 3 would need no new field,
but the engine is not replay-pure: migrations, `/forget` entries, seeded concepts and
archived history all break a replay.

**Decision.** We chose option 1.
**Falsifiability.** We would reverse this, moving to option 2, if a revision ever needs an
entry other than the latest, i.e. the same-day window is widened.
**Fired-if.** manual

## Decision: A new subcommand, not a flag on `record-review`   (→ REQ-5, REQ-6, REQ-9, REQ-10)

**Context.** `record-review` is the most-called write. The golden code path pins its
behaviour, and the evals detect its calls by name.

**Alternatives.**
1. `revise-review --concept C --result R --tested-bloom N --reason "…"`, taking the same
   optional flags as `record-review` (`--confidence`, `--applied`, `--evidence`, `--note`,
   `--source`).
2. A `--revises-last --reason "…"` flag on `record-review`.

**Case for 1.** `record-review`'s code path does not change, apart from saving the
snapshot. A transcript shows a revision by name, so `grade-regrade` can tell a revision from a
second review. The refusals (REQ-5, REQ-6) live in one place.

**Case against 1.** It is another subcommand for the skills to learn and the lint to know
(`SUBCOMMANDS`). Its flags must keep matching `record-review`'s as that command grows.

**Decision.** We chose option 1.
**Falsifiability.** We would reverse this if, in the first `grade-regrade` sweep
(`BODHI_EVAL_RUNS=3`), the tutor reaches for `record-review` instead of `revise-review` in 2
or more of the 3 runs, so a flag on the command it already uses would fit better.
**Fired-if.** manual

## Decision: A revision restores the level, the one exception to the ratchet   (→ REQ-1, REQ-4)

**Context.** `bloomLevel` only rises, so that forgetting is carried by the box and the
streak and never by the level (CLAUDE.md, *Glossary*). A wrong `correct` at a high tested
level raises the level, and may count a learned concept in the profile (decision 0004).

**Alternatives.**
1. A revision restores the saved level. Then the right grade applies through the ratchet as
   usual, and the learned count follows a crossing of 3 in either direction.
2. A revision never lowers the level. Only the schedule and the streak are restored.

**Case for 1.** The level the wrong entry produced was never earned, so keeping it would
make the record lie. The rule stays narrow: only a same-day revision of an entry the tutor
admits was wrong lowers a level, and nothing else does.

**Case against 1.** It is the first path that lowers a level, and the ratchet's guarantee
gets an exception the glossary and the `state-schema` KB must state. A lowered level can
also flip a prerequisite gate from passed back to a gap in the same session.

**Decision.** We chose option 1.
**Falsifiability.** We would reverse this if an eval or a real session shows a downward
revision made under pressure alone, with no named answer behind it, i.e. `grade-pushback`
fails because a revision lowered or raised a grade the learner only argued about.
**Fired-if.** manual

## Decision: The rule for when to revise lives in the `spaced-repetition` KB   (→ REQ-10, REQ-11)

**Context.** The pushback rule is in the `feynman-technique` KB
(`skills/feynman-technique/SKILL.md:55`): re-read and regrade when the learner names
something they said, and keep the grade when they only assert. `/quiz` and `/practice` never
load that KB. The `spaced-repetition` KB holds the canonical `record-review` rules,
including "already reviewed today". It is loaded by `/quiz`, `/practice`, `/teach`,
`/reflect` and the other grading skills, and it is at 6,933 bytes. `state-ops` is at 18,429
of the 18,432-byte budget.

**Alternatives.**
1. A short rule in `spaced-repetition`, beside "already reviewed today": a grade shown wrong
   is revised with `revise-review`, never with a second review. `feynman-technique`'s
   pushback line points to it.
2. The rule in `state-ops`, the operational surface, after trimming it to make room.
3. The rule in `feynman-technique`, and that KB added to `/quiz` and `/practice`.

**Case for 1.** It sits next to the exact rule that causes the bug. It is already loaded
wherever a review is graded, so no fire loads anything new, and it has room.

**Case against 1.** `spaced-repetition` is about scheduling. The judgment half (named
evidence vs. assertion) is about grading and stays in `feynman-technique`. So the rule is
split across two KBs, with a pointer between them. `state-ops` still has to name the new
subcommand in its write-path list, which needs a few bytes it does not have.

**Decision.** We chose option 1.
**Falsifiability.** We would reverse this, moving to option 3, if in the first
`grade-regrade` sweep the tutor on `/quiz` regrades by judgment but skips the named-evidence
check in 2 or more of 3 runs, which would show the judgment half has to travel with it.
**Fired-if.** manual

## Decision: The wrong entry moves to a sibling list no reader reads   (→ REQ-2, REQ-3, REQ-8, REQ-9)

**Context.** About fifteen places in `bodhi-state` read `reviewHistory`, and there is no
shared "graded entries" helper. The predicate is written out at five sites, and "not
deferred" at three more (`promotion_hold` 654, `retention_summary` 1709, `archive_history`
2467-2479, `exposure_of` 2586, `cmd_gate_check` 2674, `cmd_session_brief` 1863,
`cmd_revision_brief` 2268, `gate_verdict` 2641, `calibration_summary` 1602, `last_miss` 2535
and `_evidence_counts` 2436, among others). `archive_history` would fold a revised entry into
`archivedSummary` at the 100-entry cap. `verify` has no key allow-list, so unknown keys pass.
`dev/outcomes.py` and the Stop hook read only subcommand output.

**Alternatives.**
1. Move the wrong entry out of `reviewHistory` into `revisedReviews` on the concept, marked
   with `revisedOn` and `revisedReason`. The right entry is appended to `reviewHistory` with
   `revision: true`.
2. Keep the wrong entry in `reviewHistory` with `revised: true`, add one `live(h)` predicate,
   route every reader site through it, and pin it with an AST test like
   `t_single_applied_reader`.
3. A read-only view that strips revised entries at load, used by readers but not writers.

**Case for 1.** No reader changes, so REQ-3 and REQ-9 hold by construction. Archiving
cannot fold the wrong entry into the summary. `verify` already passes unknown keys, so the
`verify`-implies-readers contract holds without a new reader branch. It is the smallest
change to the most-read structure in the engine.

**Case against 1.** The audit trail is not inline. A person reading the raw JSON finds the
wrong grade in a second list, linked only by date and the `revision` flag on the right
entry, not where it stood in the sequence. `revisedReviews` has no cap. And a later feature
that wants to show revisions (in `/progress`, say) must read a second list.

**Decision.** We chose option 1.
**Falsifiability.** We would reverse this, moving to option 2, if any concept in a real
project reaches 10 revised reviews, which would show revisions are common enough to need
their place in the sequence.
**Fired-if.** manual


## Data / interface changes
- Concept field `beforeLastReview`: `{date, box, nextReview, consecutiveCorrectAtL4Plus,
  bloomLevel, lastReviewed, lastResult}`, written by `record-review` and `revise-review`.
- Concept list `revisedReviews`: the wrong entries, each as recorded plus `revisedOn`
  (date) and `revisedReason` (text). The replacing entry in `reviewHistory` carries
  `revision: true`.
- `record-review` writes `beforeLastReview`, so the golden code path registers the new field
  in `GOLDEN_FILE_CHANGES` (`dev/eval/test_bodhi_state.py:3921`). Every other byte, exit code
  and reader output stays identical (REQ-9).
- Subcommand `revise-review` (→ REQ-5, REQ-6, REQ-7).
- The `state-schema` KB first, then `bodhi-state` and its tests, then `spaced-repetition`,
  `state-ops` (the subcommand's name), `feynman-technique` and the CLAUDE.md glossary.
