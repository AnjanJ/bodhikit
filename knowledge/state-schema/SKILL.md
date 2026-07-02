---
description: "Field-level reference for BodhiKit tracking files — the canonical file shapes and field semantics. Loaded only for manual carve-outs, the script-unavailable fallback, /housekeep, and authoring; routine operations load the state-ops KB instead"
user-invocable: false
---

# State Schema — Canonical Shape of BodhiKit Tracking Files

This KB is the field-level reference. **Routine skill fires do NOT load it** — the operational surface (discovery, the `bodhi-state` write path and subcommand table, session-type vocabulary, gate/mastery semantics) lives in the `state-ops` KB, and `bodhi-state` owns every JSON mutation, so most sessions never need field shapes at all.

Load this KB only when:

- performing a **manual carve-out** — `/learn` project scaffolding, `/evaluate` profile writes, the `currentBloomLevel` / `initialBloomLevel` maps;
- running the **script-unavailable fallback** (see *Fallback discipline* below);
- you are `/housekeep` (rotation and migration);
- you are authoring or reviewing plugin files.

If a field is not listed here, do not add it. If a new field is genuinely needed, update this KB first, then `scripts/bodhi-state`, then the skills that touch it.

See also:
- `state-ops` KB — the per-session operational surface (write path, discovery, vocabulary, gate/mastery).
- `spaced-repetition` KB — box→interval mapping and update rules (implemented by `bodhi-state`).
- `state-lifecycle` KB — rotation/archive/collapse protocol (loaded by `/housekeep` only).
- `state-migration` KB — version transforms (loaded by `/housekeep migrate`).

## Guiding Principle: Progressive Disclosure for the Learner's State

The learner's accumulated work is sacred — nothing is deleted, nothing is gatekept. But context is finite, so every tracking surface is shaped so that **the smallest useful slice is what loads by default**, and the full history remains on disk behind explicit pointers. Three mechanisms: live + archive + summary for narrative surfaces, sectional files for the plan, slim JSON for state. Rotation is `/housekeep`'s job alone (see `state-lifecycle` KB); every other skill stays oblivious to compaction.

## Fallback Discipline (script unavailable, or a declared manual carve-out)

Only after BOTH the `${CLAUDE_PLUGIN_ROOT}` path and the `find ~/.claude/plugins` lookup come up empty (per the `state-ops` KB), say so plainly, then perform the minimal write by hand following this KB's shapes — Read the file, mutate the parsed JSON in place preserving every unknown field, fill the three v3 per-concept defaults on any concept missing them and set `version: 3` (read-tolerance — the eval harness caught a manual fallback skipping exactly this), Write it back, re-read to verify. Never re-serialize from a schema template.

The same read → mutate-in-place → write → verify discipline applies to the declared manual carve-outs even when the script is available.

## File Shapes

### `learningWithBodhi/<project>/.bodhi/state.json`

Slim. No long narrative fields — session narrative lives in `progress.md`.

```json
{
  "version": 2,
  "projectName": "string",
  "topic": "string",
  "createdAt": "ISO-8601",
  "lastSessionAt": "ISO-8601",
  "totalSessions": 0,
  "sessionDates": ["YYYY-MM-DD"],
  "currentStreak": 0,
  "currentPhase": "string",
  "currentModule": "string",
  "previousModule": "string",
  "currentModuleIndex": 0,
  "lastActivity": "string",
  "initialBloomLevel": { "<sub-topic>": 0 },
  "currentBloomLevel": { "<sub-topic>": 0 },
  "overallCompletion": 0
}
```

- `currentStreak`: consecutive days. Reset to 1 if `sessionDates` gap exceeds 1 day. Maintained by `bodhi-state touch-state`.
- `previousModule`: set automatically by `touch-state --module` when the module advances; read by `gate-check`.
- `initialBloomLevel` / `currentBloomLevel`: the per-topic Bloom maps are an explicit **manual carve-out** — no script subcommand owns them. `/learn` seeds both; `/assess` and `/evaluate` may update `currentBloomLevel` via the Fallback discipline above.
- `lastActivity`: one short sentence (≤120 chars) used by `/progress quick` and `/continue`. Anything longer belongs in `progress.md`.
- **No `lastSessionSummary` / `bloomResetNote` in v2** — migrated to `progress.md`.

### `learningWithBodhi/<project>/.bodhi/progress.md`

Live narrative document. Latest session in full, then a "Summary of earlier sessions" block with pointers.

```markdown
# Progress Log

## <YYYY-MM-DD> — Session <N> (<short label>)

**Duration:** <approx>
**Activities:**
- <bullets>

**Outcomes:**
- <bullets>

**Bloom adjustments:**
- <area>: <from> → <to>

**Next:** <what the next session should open with>

---

## Summary of earlier sessions

- **<YYYY-MM-DD> — <one-line headline>**
  <optional 1-3 more lines>
  → `archive/<filename>.md`
```

### `learningWithBodhi/<project>/.bodhi/assessments/latest.md`

Most recent assessment in full, then a "Summary of earlier assessments" block with `→ archive/<filename>.md` pointers. Multi-stack projects may have multiple assessments per phase; each becomes its own archive entry.

### `learningWithBodhi/<project>/.bodhi/plan/`

Sectional. Generated at plan creation; rewritten only by `/plan regenerate`.

`plan/README.md`: arc overview — current phase pointer, target arc, pace, bulleted phase list with `→ phase-<N>.md` pointers.

`plan/phase-{N}.md`: per-phase goals, duration, success criteria, then `### Module <N>.<M> — <name>` sections with concepts, exercises, success markers. From Module 2 onward each module section carries a `**Prerequisites for next module:**` line naming the concepts the next module builds on (feeds `gate-check --prereqs`).

### `learningWithBodhi/<project>/.bodhi/spaced-review.json`

Whole JSON; written exclusively through `bodhi-state`. `/housekeep` does not rotate this file.

```json
{
  "version": 3,
  "lastReviewCheck": "ISO-8601",
  "concepts": [
    {
      "name": "string",
      "module": "string",
      "introduced": "YYYY-MM-DD",
      "box": 1,
      "nextReview": "YYYY-MM-DD",
      "lastReviewed": "YYYY-MM-DD",
      "question": "string",
      "lastResult": "string",
      "bloomLevel": 0,
      "feynmanPassed": false,
      "consecutiveCorrectAtL4Plus": 0,
      "reviewHistory": [
        { "date": "YYYY-MM-DD", "result": "correct|incorrect|partial", "bloomLevel": 0, "boxBefore": 1, "confidence": "sure|mostly|guessing", "source": "string" }
      ]
    }
  ],
  "sessionHistory": [
    { "date": "YYYY-MM-DD", "type": "spaced-review", "conceptsReviewed": 0, "passes": 0, "misses": 0 }
  ]
}
```

- `box`: integer 1–5; intervals and update rules in the `spaced-repetition` KB, implemented by `record-review`.
- `reviewHistory[].retry` (optional, 1.11.1): `true` marks a successive-relearning rep — recorded evidence that did NOT move the box. `reviewHistory[].note` (optional): short free-text annotation (e.g. "learner-initiated demote"). The script caps `reviewHistory` at the most recent 100 entries per concept; older entries roll into a `reviewHistoryArchived` integer counter.
- `reviewHistory[].confidence` (optional, 1.11.0): the learner's pre-reveal confidence tag — `sure` / `mostly` / `guessing`, collected by `/quiz` and `/reflect` BEFORE the answer is judged. `bodhi-state calibration` aggregates these into overconfidence/underconfidence rates (see `metacognition` KB for why predict-before-reveal is the load-bearing order).
- `reviewHistory[].source` (optional): which skill produced the review.
- `reviewHistory[].boxBefore` (optional, 1.11.3): the box the concept occupied when this review was answered — the box whose interval scheduled it. Written by `record-review` on every new entry; absent on older entries (readers tolerate absence; `retention` reports how many legacy entries lack it). This is what makes retention-at-review analysis exact instead of reconstructed.
- `reviewHistory[].result` is a closed vocabulary: `correct` / `incorrect` / `partial` — enforced by `record-review`, checked by `verify` (1.12.1). A due concept the session never reached gets a **deferral entry** instead: `{ "date": "YYYY-MM-DD", "deferred": true, "days": N, "note": "..." }` — no `result`, written by `defer`. Deferrals are excluded from `retention` (they are scheduling events, not retrieval evidence). Do not invent result values like `skipped`; found in the wild pre-1.12.1, repaired by `normalize`.
- `sessionHistory` is an append-only audit trail. `/evaluate` reads it; routine skills do not. The `type` field is a closed vocabulary enforced in code by `record-session` — the canonical table lives in the `state-ops` KB.

**Per-concept Bloom + Feynman fields (v3).** These make mastery observable from state:

- `bloomLevel`: integer 0–6. `0` = uninitialized (no v3 writer has classified it). Ratchets up only — `record-review` takes `max(current, tested-bloom)` on a correct answer and never demotes; even `/forget` demotes the box, not the Bloom classification.
- `feynmanPassed`: boolean. Set by `set-feynman` when `/teach` (a full session or its understanding-only path) observes a genuine explain-back. Set, never unset.
- `consecutiveCorrectAtL4Plus`: incremented on correct at tested-bloom ≥ 4; reset to 0 on any incorrect, any partial, and on `/forget` (1.11.2 — a partial retrieval breaks the consecutive-correct streak; "3 consecutive correct" means uninterrupted corrects). A correct at a lower tested level leaves the counter untouched (a routine low-level recall between two L4 demonstrations is a different measurement, not counter-evidence). `--retry` reps never touch it.

These four fields feed the canonical mastery formula, computed by `bodhi-state mastery` and documented in the `state-ops` KB. Skills MUST NOT redefine it inline; see `blooms-taxonomy` KB for the underlying criteria.

**Legacy fallthrough (v2 → v3).** A concept with `bloomLevel: 0` has never been classified by a v3 writer — regardless of `lastReviewed` (real v2 data routinely has populated `lastReviewed` from pre-v3 quizzes; the 1.10.0 rule that also required `lastReviewed: null` was wrong and was corrected in 1.10.7). Gates treat `bloomLevel: 0` as "no opinion yet, allow advancement"; `/progress` displays `—` (not 0%) for modules where every concept is at `bloomLevel: 0`. `bodhi-state` implements both rules.

### `learningWithBodhi/<project>/.bodhi/assessment-history.json`

Structured assessment data for `/evaluate` and `/progress`. Append-only; never edit past entries.

```json
{
  "version": 1,
  "entries": [
    {
      "date": "YYYY-MM-DD",
      "trigger": "learn-phase2 | assess | evaluate | plan-regenerate",
      "topic": "string",
      "subTopics": [
        { "name": "string", "bloomLevel": 0, "confidence": "high|medium|low", "evidence": "string" }
      ],
      "overallNote": "string",
      "predictionDelta": {
        "predictedBiggestGrowth": "string",
        "measuredBiggestGrowth": "string",
        "predictedBiggestGap": "string",
        "measuredBiggestGap": "string",
        "perTopicBloomPredictions": [ { "name": "string", "predicted": 0, "measured": 0 } ],
        "calibrationNote": "string"
      }
    }
  ]
}
```

- Skills that run assessments (`/learn` Phase 2, `/assess`, `/evaluate` Phase 2, `/plan regenerate`) MUST append an entry here via `bodhi-state record-assessment` (prose version goes to `assessments/latest.md`).
- `predictionDelta` is populated by `/evaluate` Phase 2.5 (predict-before-reveal); absent elsewhere. See `metacognition` KB.

### `learningWithBodhi/<project>/.bodhi/resources.md`

Markdown log, dated or status-grouped sections. Small; not housekept.

### `learningWithBodhi/<project>/teach-backs/`

Capstone artifacts from `/teach-back`, at the project root (learner-authored, not internal state). Each post: `teach-backs/<YYYY-MM-DD>-<slug>.md` with a header (thesis, reader, why-it-matters), the learner's prose, and a closing status block (`Status: draft | published | personal-notes`, `Decided:`, `Masters consulted:`, `Post-Phase-6 revisions:`). Only `/teach-back` writes here. Not housekept.

### `learningWithBodhi/.bodhi-profile.json`

Cross-project learner profile (v2 split layout: this file holds top-level fields; the project list lives in `.bodhi-profile.projects.json`).

```json
{
  "version": 2,
  "careerGoal": "string",
  "whyLearning": "string",
  "priorExperience": "string",
  "learningStyle": "string",
  "overallBloomLevels": { "<area>": 0 },
  "cumulativeStats": {
    "totalSessions": 0,
    "totalExercises": 0,
    "totalConceptsLearned": 0,
    "totalMilestonesReached": 0,
    "totalProjects": 0,
    "teachBacksWritten": 0,
    "teachBacksPublished": 0
  },
  "patterns": {
    "persistentChallenges": ["<topic>"],
    "consistentStrengths": ["<topic>"]
  },
  "learnerBackground": {
    "domains": ["<string>"],
    "analogyHistory": [
      { "concept": "string", "domain": "string", "landed": true, "date": "YYYY-MM-DD" }
    ]
  },
  "lastUpdated": "ISO-8601"
}
```

- `cumulativeStats` counters are incremented via `bodhi-state bump-profile` (the skill decides WHEN — e.g. `/teach` bumps `totalConceptsLearned` only when a concept first reaches Bloom 3+ and `progress.md` shows no prior count for it). Exception: `totalSessions` is bumped automatically by `touch-state` on the first touch of a new day — no skill calls it directly.
- `learnerBackground.domains[]` / `analogyHistory[]`: populated by the analogy-escalation protocol (see `feynman-technique` KB). Read-then-append; never overwrite.

### Project completion (canonical, 1.11.1)

A project is **complete** when every module in every plan phase is finished or explicitly skipped AND the learner confirms. Completion is never inferred silently — `/evaluate` asks ("Shall we mark this path complete?") and only the learner's yes moves the entry from `activeProjects` to `completedProjects`. Completion gates the capstone offer, the mentor offer, and `/teach-back` eligibility.

### `learningWithBodhi/.bodhi-profile.projects.json`

Per-project metadata, loaded only by cross-project skills (`/mentor`, `/evaluate`, `/learn`).

```json
{
  "version": 2,
  "activeProjects": [
    { "name": "string", "topic": "string", "startedAt": "YYYY-MM-DD", "currentPhase": "string", "currentModule": "string", "bloomLevel": 0, "pace": "string", "status": "string", "trackPurpose": "string" }
  ],
  "completedProjects": [
    { "name": "string", "completedAt": "YYYY-MM-DD", "finalBloomLevel": 0, "trackPurpose": "string" }
  ]
}
```

Writers: `/learn` (append on project start), `/evaluate` (refresh; move to `completedProjects` on completion), `/mentor` (career fields in the parent profile only). Profile-list mutations are the one JSON write the script does not own — apply the Fallback discipline above.

## Schema-Evolution Rules

- Skills MUST NOT introduce new top-level fields, files, or directories under `.bodhi/` without updating this KB (and `bodhi-state`) first.
- Skills MUST NOT stuff long narrative into JSON fields — narrative belongs in `progress.md` / `assessments/latest.md`.
- Schemas evolve; readers tolerate older `version` values (the script read-tolerates v1/v2 and persists v3 on write). Skills MUST NOT branch behavior on version in prose. Full transforms live in the `state-migration` KB.
