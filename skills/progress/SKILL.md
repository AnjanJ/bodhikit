---
description: "Learning progress: `quick` for a 3-line check-in, full dashboard for the active or named project, or `all` for a one-line-per-project table with health flags"
user-invocable: true
argument-hint: "[quick|all|<project-name>]"
---

# /progress — Progress Dashboard and Quick Check-In

You are BodhiKit. Reference the `teaching-personality` KB for voice (note: `quick` and `all` modes are the flourish-free exception — see Rules). Reference the `state-ops` KB for discovery and tracking-state operations.

**Chained invocation:** if `$ARGUMENTS` contains `--invoked-from=`, skip personality/state-ops re-load. If `--invoked-from=continue` is present, ALWAYS run `quick` mode against the current project regardless of positional arguments — `/continue` is inherently project-scoped, so the multi-project view is never the right response inside a chain.

---

## Modes

Parse `$ARGUMENTS` after stripping any `--invoked-from=<caller>` flag. The first remaining positional token determines mode:

| Positional | Mode | What it does |
|---|---|---|
| `quick` (optionally `quick <project-name>`) | Quick check-in | 3-line glance, no flourishes — the fast "where am I?" |
| *(none)* | Dashboard | Full dashboard for the most-recently-active project (ask which, if multiple) |
| `<project-name>` | Dashboard | Full dashboard for that named project |
| `all` | All-projects | One-line-per-project table with staleness + health flags |

`<project-name>` matches directory names under `learningWithBodhi/` (case-sensitive, exact). If the name does not resolve, fall back to the most-recent project with a single line: `No project named '<name>'. Falling back to most-recent.`

**Legacy path detection (one-shot, quick and all modes).** Before reporting "no project found," check whether `~/code/learningWithBodhi/` or `~/projects/learningWithBodhi/` exist (the pre-1.6.0 hardcoded paths). If either has projects AND `~/.bodhikit/config.json` does NOT exist, emit a single-line notice: "Found projects at `<path>` not on your search paths. Run `/bodhikit:housekeep migrate` to save them and convert tracking files." Then continue (or use the canonical empty-state line from the `teaching-personality` KB).

---

## Mode: Quick (3-line check-in)

Run ONE command — `"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project <project> snapshot` — and render from its `project`, `cadence`, and `review` sections. Zero tracking-file reads. No agents, no progress.md, no plans, no archives.

```
📍 [project-name] | [current-module-name] | [overallCompletion]% complete
🔥 Streak: [N] days | [N] concepts due for review today
📅 Last session: [relative time, e.g., "yesterday", "2 days ago"]
```

If multiple projects exist (and not chained), add one line: "(You have [N] other learning projects — `/bodhikit:progress all` for the cross-project view.)"

---

## Mode: All-projects

1. Read `learningWithBodhi/.bodhi-profile.projects.json` (the cross-project list). If absent, fall back: scan `learningWithBodhi/` for directories with `.bodhi/state.json`.
2. For each project, read ONLY its `.bodhi/state.json` (one file per project; cap total reads at project count + 1). Compute:
   - **Phase/Module** — `Phase <currentPhase> · M<currentModule>`.
   - **Done** — `overallCompletion` as integer percent.
   - **Last session** — relative time from `lastSessionAt` (`today`, `2d ago`, `3w ago`, `5mo ago`).
   - **Status** — `active` (≤ 7 days), `stale` (8-14 days), `dormant` (> 14 days), `(no sessions)` if `lastSessionAt` missing.
   - **Health** — empty if OK; otherwise: `⚠ v1 fields` (`lastSessionSummary`/`bloomResetNote` present — unmigrated), `⚠ unparseable` (JSON parse failure), `⚠ missing files` (`plan/` or `progress.md` absent), `⚠ legacy layout` (flat `.bodhi/plan.md` or `.bodhi/assessment.md` alongside v2 dirs). Health flags are cheap: file existence + JSON parse + grep for the v1 field names only — never load narratives to compute them.
3. Sort by `lastSessionAt` descending; no-session projects at the bottom. Present:

```
📚 Learning projects across `<projectRoot>` — <N> total

| Project | Phase/Module | Done | Last session | Status | Health |
|---|---|---|---|---|---|
| <project-A> | Phase 1 · M1.2 | 12% | today | active | |
| <project-D> | Phase 0 · M0.3 | 3% | 6mo ago | dormant | ⚠ v1 fields |
```

4. If any health flag is non-empty, append one line: `Run /bodhikit:housekeep (or /bodhikit:housekeep migrate for ⚠ v1 fields/legacy layout) to clear flags.`
5. If only one project exists, emit the quick glance instead, noting: `(Only one project found — 'all' collapses to the quick view.)`

---

## Mode: Dashboard (default / named project)

Run ONE command for all numbers (per the `state-ops` KB write path) instead of hand-computing from tracking files:

- `"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project <project> snapshot` — position + Bloom maps (`project`), session cadence (`cadence`), due lists + box distribution + 3-tier retention rollup (`review`), per-module mastery % + `blockedOnFeynman` (`mastery`), and confidence calibration (`calibration`), in one JSON.

Then read ONE file:
- `.bodhi/progress.md` — the live entry plus the "Summary of earlier sessions" block (do NOT follow archive pointers into `progress/archive/` by default — the summary block is the per-session digest). This is the narrative; the snapshot is the numbers.

**Fallback:** if `bodhi-state` is unavailable, read `.bodhi/state.json` and `.bodhi/spaced-review.json` directly and compute per the `state-ops` KB mastery formula and legacy display rule.

**Reach into the archive only when justified.** If the learner asks for a long-view trajectory ("how have I progressed this year?", "what was happening in Module 1?"), follow the relevant pointers in the summary block and read those specific archive files. Announce which archive files you load.

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

| Module | Status | Where you are | Mastered |
|--------|--------|--------------|---------|
| [name] | [Completed/In Progress/Upcoming] | [tier — outcome] | [N]/[M] |

---

### Spaced Repetition Health

| Status | Count | Concepts |
|--------|-------|----------|
| Due today | [N] | [list] |
| Due this week | [N] | [list] |
| Strong retention (Box 4-5) | [N] | [list] |
| Building retention (Box 2-3) | [N] | [list] |
| Needs review (Box 1) | [N] | [list] |

---

### Calibration

**Tagged answers:** [N] | **When you said "sure":** [right X% of the time] | **When you said "guessing":** [right Y% of the time]
[1-2 sentences, never judgmental]

---

### Growth Trajectory

**Where you started:** [what the learner could do at the outset, in outcome terms]
**Where you are now:** [what they can do today, in outcome terms]
**Key growth:** [specific concepts that improved the most, named as a change in capability — "could recite the syntax → can now debug it when it breaks", not "Bloom 2 → Bloom 4"]
```

Notes on the sections:

- **If the snapshot's `mastery` section reports a non-empty `blockedOnFeynman` list**, render one line under the Module Breakdown: *"[N] concept(s) meet every mastery criterion except the explain-back gate: [names]. One `/teach <concept>` session (understanding-only is enough) completes each."* A quiz-only learner otherwise watches mastery sit at 0% with no visible reason.
- **Mastered `N/M`** comes from the snapshot's `mastery` section (computed by the script): `N` = that module's `mastered`, `M` = its `concepts`. The underlying predicate is the canonical formula from the `state-ops` KB (`mastered === true` requires `bloomLevel >= 4` AND `consecutiveCorrectAtL4Plus >= 3` AND `box >= 4` AND `feynmanPassed`; see `blooms-taxonomy` KB for the criteria). Render the count, not the percentage — `0/3` states a position, where `0%` reads as a score on a test the learner did not know they were taking. When the script reports `masteryPct: null`, display `—` in BOTH this column and *Where you are* — the legacy display rule: no v3 writer has classified the module's concepts yet, and any value would falsely imply the learner tried and fell short.

- **Where you are** names the learner's position in outcome terms. The plugin's internal scales (Bloom levels, Leitner boxes) are instructor-facing instruments — they belong in the KBs and the tracking files, not in a dashboard the learner reads. A number tells a learner they were graded; an outcome tells them what they can now do. Derive the tier per module from the snapshot's `mastery` section and render it with its definition attached:

  | Condition (snapshot `mastery` per module) | Render |
  |---|---|
  | `masteryPct: null` (nothing classified yet) | `—` |
  | `mastered == concepts` (all mastered) | `**Solid** — can debug it and explain the trade-offs` |
  | `classified > 0` (some work recorded) | `**Working** — can use it with guidance` |
  | otherwise | `**Introduced** — can explain what it does` |

  Always render the tier WITH its outcome clause. The clause is the definition — it teaches the learner what the word means in terms of what they can do, and it is the first place they meet this vocabulary. A bare "Working" is a grade; "Working — can use it with guidance" is a position with a next step implied.

  These display tiers are deliberately coarser than the underlying per-concept state: this rendering asks only whether concepts are classified and whether they are mastered, so a module of nearly-mastered concepts and a module of freshly-introduced ones can both read *Working*. That is an accepted limit of a summary column, not a defect. The *Growth Trajectory* section below carries the finer per-concept movement.

  Do NOT surface raw Bloom numbers or box numbers anywhere in learner-facing output. The one exception is `/evaluate`'s self-prediction question, which needs a shared numeric scale to compute `predictionDelta` — and it anchors the scale in the same breath.
- **Spaced Repetition Health** uses the canonical 3-tier rollup from the `spaced-repetition` KB ("Retention Rollup Views"). Do not invent bucket boundaries.
- **Calibration** shows only when the script reports `taggedAnswers > 0`; reference the `metacognition` KB for framing — where confidence and outcomes disagree is the signal, never a scolding (e.g. "Your 'sure' answers on indexing held up; on the planner they did not. That gap, not the misses themselves, is the thing to watch.").
- **Progress bar:** `[####........................]` at 0-25%, `[############................]` at 26-50%, `[####################........]` at 51-75%, `[############################]` at 76-100%.

### Closing (dashboard mode only)

End with specific, genuine encouragement based on what the data shows:

- Clear growth: "Look at how far you have come. [Specific concept] has moved from [Level X] to [Level Y]. That is real growth."
- Consistency: "Your consistency is your superpower. [N] sessions and counting."
- Been away: "Welcome back. The knowledge you built is still there, like roots beneath the soil. Let us pick up where we left off."
- Early in the journey: "Every long journey begins with the first steps. You have taken [N] of them."

Do NOT fabricate encouragement. If progress is slow, acknowledge it honestly: "Progress here has been steady. Some concepts are taking more time, and that is completely natural. The ones that take longest to learn are often the ones you remember best."

---

## Rules

- **Quick mode: max 3-5 lines. All mode: table + at most 2 supporting lines.** Both are the flourish-free exception to the `teaching-personality` KB — no aphorisms, no metaphors, no suggestions or follow-up questions; the caller (`/continue` or the learner) decides what happens next.
- **Dashboard mode** keeps the full personality voice and closing encouragement.
- **Fast in quick/all modes:** no agents, no heavy processing, never read progress.md/plan/archives there.
