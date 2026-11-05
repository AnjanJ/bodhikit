# Rendering a module row — shared by `/progress` (Module Breakdown) and `/plan view`

Loaded by the phase that prints a per-module table. The rows come from `"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project <project> syllabus` — `modules[]` in plan order, each with `status`, `targetBloom*`, `evidenceKind`, and an `evidence` block (the module's tally plus `summaryTier`, `nextDue`, `dueToday`) — followed by `unplanned[]` (tracked modules the plan never declared). Render every row the script returns; never reorder, never drop one, never re-derive a status or a tier from the files.

## How the work is checked (from `evidenceKind`)

`syllabus` gives the project's `evidenceKind` and each row's. When the project's kind and every row's kind are `code`, say nothing about it: that is the view code learners have always had. Otherwise, in plain words and never the raw kind name:

- Above the table, one line for the project: `How your work is checked: <line>`.
- On a row whose `evidenceKind` differs from the project's (an `unplanned` row too), add `(<short>)` after the module's name.

| `evidenceKind` | `<line>` | `<short>` |
|---|---|---|
| `code` | you write code, and we run it | code you run |
| `problems` | you work problems, checked against answers I save before you start | problems, checked against saved answers |
| `writing` | you write short pieces applying an idea to a new case, read against criteria I save first | writing, read against saved criteria |
| `performed` | you practise away from the screen and tell me how it went, and it counts as your account | practice, by your account |

## Status (from `status`)

| `status` | Render |
|---|---|
| `done` | `Done` |
| `current` | `◀ Current` |
| `upcoming` | `Upcoming` (with `targetBloomOutcome` when present: `Upcoming — aims at: you can reason about why it behaves as it does`) |
| `skipped` | `Skipped` |
| (an `unplanned` row) | `Not in plan` |

## Where you are (from `evidence`)

The learner reads a position in outcome terms, never a Bloom number or a Leitner box (`blooms-taxonomy` KB *Learner-Facing Rendering*; the tier→word mapping is that KB's *Concept tiers* table). `summaryTier` is the script's reading of the **lowest occupied tier above `unclassified`** — the honest summary of a mixed module is where its weakest classified concept sits, not its best. Render it:

| `evidence` | Render |
|---|---|
| `tracked: false`, or `summaryTier: null` (`masteryPct: null`) | `—` (nothing observed; never `0%`) |
| `mastered == concepts`, `dueForCheck == 0` | `**Solid** — can find where it breaks and explain the trade-offs` |
| `mastered == concepts`, `dueForCheck > 0` | `**Solid, due for a check** — can find where it breaks and explain the trade-offs` |
| `summaryTier: introduced` | `**Introduced** — can explain it` |
| `summaryTier: familiar` | `**Working** — can use it with guidance` |
| `summaryTier: mastered`, `mastered < concepts` (the rest are unclassified seeds) | `**Solid** — can find where it breaks and explain the trade-offs (N solid; M not yet observed)` |

**By your account.** When `masteredByReport > 0`, some of the module's *Solid* rests on practice the learner reported (`evidence-kinds` KB): say so in the row. All of it → `**Solid, by your account** — …`; some → add `(N by your account)` after the word. The level, the reviews and the explain-back behind it were still graded; only the practice is their report, and a row that hid that would claim the tutor saw it.

Then, when the module is not uniform, append the spread from `tiers` using the learner-facing words and counting classified concepts only: `(2 solid, 1 working)`. When `applied` is below `classified`, add `; built with N of M`, so explained-but-never-run concepts are visible without a level. Always render the word with its outcome clause — a bare "Working" is a grade; "Working — can use it with guidance" is a position with a next step implied. Concepts at `unclassified` are left out of the spread: nothing has been observed about them.

## Mastered (from `evidence`)

`[mastered]/[concepts]` — the count, not a percentage (`0/3` states a position; `0%` reads as a score on a test the learner did not know they were taking). `—` when `masteryPct` is `null`.

## Next review (from `evidence`)

`nextDue` as a short date, with `(N due today)` when `dueToday > 0`; `—` when `nextDue` is `null`; append `· N parked` when `parked > 0`.
