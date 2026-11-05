# 0003: Write commands say the schedule in words, not the box number

> Decided 2026-11-06. Amends learn-anything REQ-1's "exactly as 1.24.1" for three outputs.

**Context.** Learner-facing text never quotes a Leitner box (CLAUDE.md, `blooms-taxonomy` KB).
After `BARE_LEVEL_RE` was made case-insensitive on 2026-11-05, two of three live `kb-load`
runs failed. The tutor told the learner "review recorded (box 1 → 2, …)" in a closing line,
and "Review recorded (box 1→2, next review 2026-11-08, …)" between tool calls. Both copy
`record-review`'s output, `"box": "1 -> 2"`. Two other write commands print a box too:
`forget` (`"boxChanges": {"X": "4 -> 1"}`, and `/forget` tells the tutor to "report the box
changes from the script's JSON output") and `add-concept` (`"box": 1`). `/quiz` step 4 asks
for "box/Bloom movements (from the script outputs)". In 1.18.0 the same leak from `due`'s
output was fixed by taking the numbers out of `due`.

**Alternatives.**
1. Tell the skills not to say box numbers.
2. The three write commands stop printing a box. `record-review` reports the move in words
   (`schedule`: "moved up", "held", "back to the start"); `forget` and `add-concept` drop the
   field. Tracking files and the read commands keep their numbers.
3. Option 2, and also take the box out of the read commands (`session-brief`, `gate-check`,
   `revision-brief`), replacing it with the predicates the skills need.

**Case for option 2.** It removes the number at the source the leaks were traced to, as
1.18.0 did for `due`, without adding prose, which CLAUDE.md rules out for an
executor-discipline bug. No skill reads the box from a write command's output, so nothing
downstream needs it. The words carry what a learner may hear: whether the review moved the
schedule.

**Case against option 2.** The read commands still give the box as a number (the skills
decide with it, e.g. pitching a question one level higher when `box >= 3`), so a leak from
them stays possible. `t_golden_code_path` gains a second hand-made transform, this time on
values as well as names. Thirteen tests that read the box from `record-review`'s output have
to read it from the tracking file instead.

**Decision.** We chose option 2.
**Falsifiability.** We would extend this to option 3 if 2 or more of the next 10 live
transcripts show a box number that came from a read command's output.
**Fired-if.** manual
