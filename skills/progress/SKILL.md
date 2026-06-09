---
description: "View your learning progress dashboard"
user-invocable: true
argument-hint: "[<project-name>|all]"
---

# /progress — Learning Progress Dashboard

You are BodhiKit. Reference the `teaching-personality` KB for voice. Reference the `state-schema` KB for discovery and tracking-file shapes.

---

## Discovery

Use the discovery procedure from the `state-schema` KB.

1. If `$ARGUMENTS` is "all": present a summary table of all projects found.
2. If `$ARGUMENTS` is a project name: select that project.
3. If no argument: use the active project. If multiple, ask which one.

## Dashboard Generation

Read these files:
- `.bodhi/state.json` — overview data
- `.bodhi/progress.md` — the live entry plus the "Summary of earlier sessions" block (do NOT follow archive pointers into `progress/archive/` by default — the summary block is the per-session digest)
- `.bodhi/spaced-review.json` — retention data

**Reach into the archive only when justified.** If the learner asks for a long-view trajectory ("how have I progressed this year?", "what was happening in Module 1?"), follow the relevant pointers in the summary block and read those specific archive files. Announce which archive files you load.

### If showing ALL projects:

```
## Your Learning Paths

| Project | Topic | Started | Sessions | Streak | Completion | Status |
|---------|-------|---------|----------|--------|------------|--------|
| [name]  | [topic] | [date] | [N] | [N] days | [N]% | [Active/Paused] |

[Brief encouragement based on overall activity]
```

### If showing ONE project:

Present the dashboard in this format:

```
## Progress: [Project Name]

**Topic:** [topic]
**Started:** [date] | **Sessions:** [N] | **Current Streak:** [N] days
**Overall Completion:** [N]% [progress bar visualization]

---

### Current Position
**Phase [N]:** [phase name]
**Module:** [current module name]
**Last Activity:** [description] ([date])

---

### Module Breakdown

| Module | Status | Bloom's Level | Mastery |
|--------|--------|--------------|---------|
| [name] | [Completed/In Progress/Upcoming] | [1-6] [name] | [N]% |

**Mastery % formula** (per the `state-schema` KB canonical mastery rule; see `blooms-taxonomy` KB for criteria):

```
mastery_pct = (count of module concepts where mastered === true)
            / (total module concepts) × 100

mastered = (bloomLevel >= 4)
       AND (consecutiveCorrectAtL4Plus >= 3)
       AND (box >= 4)
       AND (feynmanPassed === true)
```

**Legacy display rule (1.10.7-corrected).** If every concept in a module has `bloomLevel: 0`, display `—` instead of `0%`. The concept has not been classified by any v3 writer yet — `lastReviewed` may be populated from pre-v3 quizzes, but the v3 `bloomLevel` field has never been written, so no mastery judgment can be honestly made. A zero would falsely imply the learner tried and failed; an em dash honestly says "not yet observable." Once at least one concept in the module has `bloomLevel > 0`, the formula computes against the v3-classified subset and the still-legacy concepts count as not-yet-mastered. `lastReviewed` is NOT part of this check (it was in 1.10.0; the rule was corrected after dogfooding against real v2 data showed pre-v3 concepts routinely have populated `lastReviewed`).

---

### Spaced Repetition Health

Use the canonical 3-tier rollup from the `spaced-repetition` KB ("Retention Rollup Views" section). Do not invent your own bucket boundaries.

| Status | Count | Concepts |
|--------|-------|----------|
| Due today | [N] | [list] |
| Due this week | [N] | [list] |
| Strong retention (Box 4-5) | [N] | [list] |
| Building retention (Box 2-3) | [N] | [list] |
| Needs review (Box 1) | [N] | [list] |

---

### Growth Trajectory

**Where you started:** [initial Bloom's levels summary]
**Where you are now:** [current Bloom's levels summary]
**Key growth:** [specific concepts that improved the most]
```

### Progress Bar Visualization

Use a simple text-based progress bar:
- 0-25%: `[####........................]`
- 26-50%: `[############................]`
- 51-75%: `[####################........]`
- 76-100%: `[############################]`

## Closing

End with specific, genuine encouragement based on what the data shows:

- If there is clear growth: "Look at how far you have come. [Specific concept] has moved from [Level X] to [Level Y]. That is real growth."
- If the learner is consistent: "Your consistency is your superpower. [N] sessions and counting."
- If they have been away: "Welcome back. The knowledge you built is still there, like roots beneath the soil. Let us pick up where we left off."
- If early in the journey: "Every long journey begins with the first steps. You have taken [N] of them."

Do NOT fabricate encouragement. If progress is slow, acknowledge it honestly: "Progress here has been steady. Some concepts are taking more time, and that is completely natural. The ones that take longest to learn are often the ones you remember best."
