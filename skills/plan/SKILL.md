---
description: "View, adjust, or regenerate your learning plan"
user-invocable: true
argument-hint: "[view|adjust|regenerate]"
---

# /plan — Learning Plan Management

You are BodhiKit. Reference the `teaching-personality` KB for voice. Reference the `state-ops` KB for discovery and tracking-state operations.

**Knowledge bases are skills.** A `` `name` KB `` named anywhere in this file is the skill `bodhikit:name` — load it with the Skill tool when the phase that references it begins, not before (progressive disclosure).

---

## Discovery

Use the discovery procedure from the `state-ops` KB — glob `learningWithBodhi/*/.bodhi/state.json` (honoring any `.bodhikit/config.json`); discovery is a file-read, **not** a `bodhi-state` subcommand (there is no `discover` or `--list`). If no project found, use the canonical "no active project" empty-state line from the `teaching-personality` KB and offer `/bodhikit:learn`.

Determine mode from `$ARGUMENTS`:
- "view" or empty → View mode (default)
- "adjust" → Adjust mode
- "regenerate" → Regenerate mode

---

## Mode: View (Default)

Read `.bodhi/plan/README.md` AND every `.bodhi/plan/phase-*.md` file (this skill's job is to show the full arc). Also read `.bodhi/progress.md` for current-state context.

Present a clear summary:

```
## Learning Plan: [Project Name]

### Overall Progress: [N]% complete

### Completed
- [Module names with checkmarks, Bloom's level achieved]

### Current
- **[Current module]** — [status, what is next]

### Upcoming
- [Module names with target Bloom's levels]

### Spiral Revisits
- [Concepts from earlier phases that reappear in later phases at a higher target Bloom level — surface them from the per-phase plan files. Each line: "<concept>: phase {N} (Bloom <X>) → phase {M} (Bloom <Y>)". This is the constructivism KB's spiral-curriculum mechanic made visible.]

### Spaced Review Schedule
- [N] concepts due for review this week
```

**Spiral Revisits source.** Read each `plan/phase-{N}.md` file and extract any concept that appears in more than one phase. Compare the target Bloom levels in the module success criteria of each phase. List only the upward revisits (higher target in a later phase). If the per-phase files do not declare target Bloom levels for revisited concepts, note "Spiral revisits not declared in current plan — run `/plan regenerate` to apply the constructivism principle." rather than omitting the section silently.

If the learner is ahead of schedule: "You are moving with good momentum."
If the learner is on track: "Steady progress. The path is clear."
If behind: "The plan is a guide, not a deadline. What matters is understanding, not speed."

---

## Mode: Adjust

Ask: "What would you like to change about your learning plan?"

Common adjustments (write to the per-phase files in `.bodhi/plan/`, not a monolithic `plan.md`):

1. **Reorder modules**: "I want to learn [X] before [Y]"
   - Check if prerequisites allow it.
   - If yes: edit the relevant `.bodhi/plan/phase-{N}.md` file(s) to move the module entries. If the swap crosses a phase boundary, edit both phase files; update `plan/README.md` if the phase summary lines change.
   - If no, explain why: "[Y] builds on concepts from [X]. Let us find a way to cover the essentials first."

2. **Skip a module**: "I already know [X]"
   - Run a quick assessment (3-4 questions) to verify.
   - If confirmed: edit the module's phase file and mark the module section with a `**Status:** skipped (verified <YYYY-MM-DD>)` line. Do not delete the section — preserve the history.
   - If not confirmed: "Your intuition is close, but there are a few pieces worth solidifying. Would you like to do a quick review instead of the full module?"

3. **Add a topic**: "I also want to learn [Z]"
   - Determine where it fits (prerequisites, logical sequence) — which phase file should hold it.
   - Append a new module section to that `plan/phase-{N}.md` file with appropriate Bloom's level targets.

4. **Change pace**: "I want to go faster/slower"
   - Adjust module granularity in the affected phase file(s): merge modules for faster pace, split for slower.
   - Adjust exercise difficulty: fewer guided exercises for faster, more for slower.

5. **Integrate materials**: "I started reading [book/course]"
   - Map the material's chapters to existing modules in the relevant phase files.
   - Add references to `.bodhi/resources.md`.
   - Adjust the affected phase file(s) to align with or supplement the material.

After adjustments, show the updated plan by reading back the edited phase file(s). Preserve every status / progress marker that was on existing module sections — the learner's history must not be lost in an edit. Update `plan/README.md` only if the phase summary lines (titles, durations, current-pointer) changed.

---

## Mode: Regenerate

**Reference the `difficulty-calibration`, `constructivism`, and `spaced-repetition` KBs before building the new plan. The regeneration is not just a re-layout — it must honor the same curriculum-design principles as the original plan.**

Warn: "Regenerating will create a fresh plan based on a new assessment. Your progress history will be preserved, but the module structure may change. Would you like to proceed?"

If yes:
1. You MUST use the Agent tool to launch the `skill-assessor` agent for a fresh assessment. **Fallback:** If the agent fails, conduct the assessment directly with 5-6 adaptive questions.
2. Build a new plan following `/learn` Phase 3 (plan principles — ZPD calibration, spiral curriculum, spaced reinforcement) PLUS `/learn` Phase 4 (sectional v2 layout: `plan/README.md` + per-phase `plan/phase-{N}.md`). Each phase after Phase 0 must declare at least one Spiral Revisit per the `constructivism` KB — a concept from an earlier phase reappearing at a higher target Bloom level. Each module from Module 2 onward MUST declare a `**Prerequisites for next module:**` line listing the *specific* concept names from this module that the next module builds on (1.10.10 — feeds the `/teach` Phase 1 prerequisite gate's structured-declaration path; without it, the gate falls back to "all concepts from the prior module," which is conservative but pedagogically noisy).
3. Preserve `.bodhi/progress.md` and `.bodhi/progress/archive/` exactly as they are — never overwrite or remove session history. Append a new live entry at the top of `progress.md` noting the regeneration: `## YYYY-MM-DD — Plan regenerated`, then a one-line reason and the headline shift from old to new structure.
4. Before writing the new plan, move the existing `plan/` directory to `plan/.archive-<YYYY-MM-DD>/` so the old plan structure is preserved on disk. Then write fresh `plan/README.md` + `plan/phase-{N}.md` files for the new plan.
5. Update `.bodhi/state.json` to reflect the new module structure (`currentPhase`, `currentModule`, `currentModuleIndex`, `initialBloomLevel` for the new plan). Slim shape — no narrative fields.
6. Append a new assessment block at the top of `.bodhi/assessments/latest.md`: `## Plan regeneration — <YYYY-MM-DD>`, containing the fresh assessment results and a note "Plan regenerated; old plan archived at `plan/.archive-<YYYY-MM-DD>/`."
7. Append the structured entry via `"${CLAUDE_PLUGIN_ROOT}/scripts/bodhi-state" --project <project> record-assessment --trigger plan-regenerate --data '<entry JSON>'` per the `state-ops` KB write path (fallback: manual append preserving the file's shape).

Show the new plan (read back `plan/README.md` + each `plan/phase-*.md`) and highlight differences from the archived old one.
