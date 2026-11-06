# Spec: Revise a grade

> Spec accepted at commit `b6d6eb6` on karpathy-followups.
> Status: shipped
> Paths: scripts/bodhi-state, skills/state-schema/, skills/state-ops/, skills/feynman-technique/, dev/eval/, dev/outcomes.py

## Purpose
A grade the tutor records wrongly today can be corrected today, and the record then looks as
if the right grade had been given the first time, with the mistake still visible in the
history. Today a wrong `incorrect` permanently sends a concept back to the start, and a
wrong `correct` permanently promotes it.

## User stories
- As a learner whose right answer was graded wrong, I want the correction to reach my
  record, so that I am not re-tested tomorrow on something I recalled on time.
- As a learner who was graded too generously, I want the tutor to be able to take it back,
  so that my schedule reflects what I actually know.
- As anyone reading my record, I want to see that a grade was revised and why.

## Requirements (EARS)
- **REQ-1.** When the tutor revises today's latest graded review of a concept, the concept's
  box, next review, L4+ streak, level, last-reviewed date and last result shall equal those
  the revised grade would have produced had it been recorded in place of the wrong one.
- **REQ-2.** When a review is revised, `bodhi-state` shall keep the original entry in the
  concept's record, marked revised with the date and the stated reason, and add the revised
  entry to the review history.
- **REQ-3.** While an entry is marked revised, every `bodhi-state` reader (schedule, due list,
  retention, calibration, mastery, gate, session brief, snapshot, revision brief, Feynman
  currency, anonymized export) and `dev/outcomes.py` shall give the same output as for a
  record with that entry absent.
- **REQ-4.** When a revision moves a concept's level across 3, in either direction, the
  profile's count of learned concepts shall move by one in the same direction.
- **REQ-5.** If the review to revise is not the concept's latest graded entry dated today
  (an earlier day, a relearning retry, or no graded entry today), then `bodhi-state` shall
  refuse the revision with an error and change no file.
- **REQ-6.** If a revision states no reason, then `bodhi-state` shall refuse it and change no
  file.
- **REQ-7.** When a revision lands, `bodhi-state` shall report the schedule in words and the
  level's outcome clause, never a box number.
- **REQ-8.** `verify` shall accept a record that holds revised entries.
- **REQ-9.** While no review has been revised, `record-review` and every reader shall behave
  exactly as they do today.
- **REQ-10.** When the learner names something their answer actually said that the grade
  missed, and the re-check shows the grade was wrong, the tutor shall revise it through
  `bodhi-state`, never with a second review and never by editing a tracking file.
- **REQ-11.** If the learner only asserts that their answer was good enough, then the tutor
  shall keep the grade.

## Out of scope
Revising an earlier day's entry or one with a later entry after it. Revising `set-feynman`,
`record-session` or `/forget`. A revision started by the learner without the tutor.
