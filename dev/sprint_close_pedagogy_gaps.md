# Sprint: Close Pedagogy Gaps (1.9.2 → 1.10.5)

**Status:** DRAFT — awaiting approval
**Drafted:** 2026-06-09
**Source audit:** `gaps_of_pedagogy.md` (35 confirmed + 9 adjusted = 44 findings)
**Verification status:** Adversarial re-verification confirms 41/44 hold as-stated, 3 nuanced (no fully-refuted findings)
**Author:** working draft for Anjan's review

---

## Sprint shape

- **One sprint, six internal milestones.** Each milestone is a releaseable point (1.10.0 → 1.10.5). After each milestone we can pause, dogfood, and decide whether to ship or continue.
- **Schema migration is zero-breakage.** `/housekeep migrate` is extended to handle v2 → v2.1 conversion with safe defaults. Existing projects continue to work; new fields populate on first write.
- **Every fix has a paired verification task.** `dev/check.sh` rules to catch the gap's absence, plus dogfood scenarios that surface it end-to-end.
- **Per-task side-effect block.** Each atomic task has: What changes / What might break / How we'd detect breakage / Rollback.

## Milestone order (impact-per-edit, audit-recommended)

| # | Milestone | Closes | Version | Risk |
|---|---|---|---|---|
| M1 | Schema fix: per-concept Bloom + Feynman tracking | H1, H2, H3, M2, M3 (5) | 1.10.0 | HIGH — schema migration |
| M2 | `/reflect` Phase 2 retrieval-gate rewrite | H5, H6, H9, M13, A5 (5) | 1.10.1 | LOW — one phase |
| M3 | Wire 1.4.0 auto-invoke chains | H11, H12, H13, M11, M27, M32, A3, A9 (8) | 1.10.2 | MEDIUM — multi-skill |
| M4 | One-line KB references batch | M10, M12, M14, M16, M18, M20, M23, M24, M26, A6 (10) | 1.10.3 | LOW — additions only |
| M5 | Decide `/pair` scope + ZPD signal gating | M5, M6, M8, L8 (4) | 1.10.4 | MEDIUM — depends on M3 |
| M6 | Lint upgrade + remaining LOWs + nuance corrections | H4, M7, H10, L2, L3, L6, A1, A2, A4, A7, A8 (11) | 1.10.5 | LOW |
| — | Dogfood + release tag | — | 1.10.5 | — |

**Total: 53 findings closed across 44 audit items.** (Some fixes close multiple. M3's wire-up closes A3 and A9 jointly with H11/H12/H13.)

## Cross-cutting constraints

1. **CLAUDE.md authoring contract holds throughout.** No restating personality, Leitner intervals, or tracking-file shapes. New KB references only.
2. **state-schema KB is updated FIRST whenever a tracked-file shape changes.** No skill writes a new field before the schema documents it.
3. **`--invoked-from=` chain convention applies** to every new auto-invocation. Chainable skills check `$ARGUMENTS` and skip redundant loads.
4. **No new top-level files** unless state-schema KB declares them first.
5. **Every PR runs `dev/check.sh` clean** (no new warns either; warns get promoted to errors in M6).
6. **Behavioral changes are announced in the relevant CHANGELOG entry.** Migration steps documented for users on existing data.

---

# Milestone 1 — Schema fix (1.10.0)

**Goal:** Make Bloom mastery observable. Closes H1, H2, H3, M2, M3.

**Theory of change:** The audit's Theme 1 root-cause. Five findings collapse into one schema extension. Once `bloomLevel`, `feynmanPassed`, and `consecutiveCorrectAtL4Plus` exist on `spaced-review.json.concepts[]`, every downstream skill can read/write them deterministically.

**Risk profile:** Highest risk milestone in the sprint. Touches the most load-bearing surface. Migration must be zero-loss. Recommend dogfooding for at least 48 hours before M2 lands.

## Task M1.1 — Extend `state-schema` KB with per-concept Bloom + Feynman fields

**File:** `knowledge/state-schema/SKILL.md` (specifically the `spaced-review.json` section around L268-307)

**What changes:**
- Add three fields to `concepts[]` entries:
  - `bloomLevel: integer 0-6` — current Bloom level for this concept (0 = uninitialized)
  - `feynmanPassed: boolean` — has the concept passed at least one Feynman explain-back gate?
  - `consecutiveCorrectAtL4Plus: integer ≥0` — counter for mastery criterion (3 consecutive correct at Bloom 4+)
- Add a `bloomLevel` field to `reviewHistory[]` entries: which Bloom level the question tested at on that date.
- Bump `spaced-review.json` schema version: `"version": 2` → `"version": 3`.
- Document the mastery formula explicitly: `mastered = (bloomLevel >= 4) AND (consecutiveCorrectAtL4Plus >= 3) AND (box >= 4) AND (feynmanPassed === true)`. Cross-link to `blooms-taxonomy` KB.
- Add `state-migration` KB entry for v2 → v3 conversion.

**What might break:**
- Skills that read `concepts[]` and don't tolerate the new fields → none should break (additive), but inline migration discipline must be confirmed.
- Skills that bump version on write may now write v3 against a v2 file without migrating first.
- Lint rules looking for `"version": 2` against `spaced-review.json` would need updating.

**How we'd detect breakage:**
- New `dev/check.sh` rule: any skill writing to `spaced-review.json` must read-tolerate v2 (auto-fill defaults) before writing v3.
- Dogfood: write a v2 fixture, run `/quiz`, verify the file rewrites as v3 with `bloomLevel`/`feynmanPassed` populated.

**Rollback:** Revert the KB section. Until skills start writing the new fields (M1.3+), the schema change is documentation-only.

---

## Task M1.2 — Add `state-migration` KB entry for v2 → v3

**File:** `knowledge/state-migration/SKILL.md`

**What changes:**
- New migration table row: `spaced-review.json v2 → v3`.
- Procedure: for each entry in `concepts[]`, add `bloomLevel: 0`, `feynmanPassed: false`, `consecutiveCorrectAtL4Plus: 0` if absent; set version to 3.
- Inline-read tolerance pattern: any skill reading v2 treats missing fields as defaults above; only writes v3 after performing the inline fill.
- Note that `currentBloomLevel` in `state.json` is preserved as-is (per-sub-topic legacy view) but is now considered a rollup; per-concept Bloom is authoritative.

**What might break:** Nothing additive at this stage. Risk is downstream skills mis-implementing the inline fill.

**How we'd detect breakage:** Dogfood `/quiz` against a v2 fixture and inspect output; M1.6 lint rule.

**Rollback:** Revert the KB entry; skills fall back to reading whatever is on disk.

---

## Task M1.3 — `/quiz` writes `bloomLevel` per question, updates `consecutiveCorrectAtL4Plus`

**File:** `skills/quiz/SKILL.md` (Phase 3, around L107-118)

**What changes:**
- Phase 2 Quiz Results table already shows "Bloom's Level Tested" (L96) — this becomes structured.
- Phase 3 `reviewHistory[]` append now includes `bloomLevel: <level the question tested at>`.
- New counter update logic: if `result === "correct"` AND `bloomLevel >= 4`, increment `consecutiveCorrectAtL4Plus`. Else reset to 0.
- Update `concepts[].bloomLevel` to the highest level on which the learner was correct in this quiz (preserve any higher prior value; never demote — that's `/forget`'s job).
- Schema-version write logic: read tolerate v2; write v3 (with inline-fill per M1.2).

**What might break:**
- A learner with mixed-Bloom answers on the same concept could see `bloomLevel` advance even though they failed a higher-level question — guard against this (only advance if the highest-correct question level exceeds the prior `bloomLevel`).
- `/forget` must reset `consecutiveCorrectAtL4Plus` to 0 (verified in M1.5).

**How we'd detect breakage:**
- Dogfood scenario: quiz on a concept with one Level-3 correct, one Level-5 incorrect → `bloomLevel` should not advance past the prior value, `consecutiveCorrectAtL4Plus` should reset to 0.
- New `dev/check.sh` rule: `/quiz` must mention `consecutiveCorrectAtL4Plus` or `bloomLevel` in Phase 3.

**Rollback:** Revert the Phase 3 edit. New fields stop populating; existing fields remain.

---

## Task M1.4 — `/teach` Phase 5 writes per-concept Bloom + Feynman, gates module advancement

**File:** `skills/teach/SKILL.md` (Phase 5, L102-116; plus Phase 1, L19-26 for the advancement gate)

**What changes:**
- **Phase 5 retention check** explicitly maps observed performance to a Bloom level for the concept and writes it to `concepts[].bloomLevel` (read-then-write; preserve unknown fields; never demote in this skill).
- **Phase 5 Feynman gate:** when the learner produces a clear, jargon-free explanation in their own words at the Phase 2 Checkpoint OR Phase 5 retention check, set `concepts[].feynmanPassed = true`. (Set, never unset.)
- **Phase 1 prerequisite gate:** before selecting the next concept from the plan, read `spaced-review.json.concepts[]` for the current module's prerequisite concepts. If any prerequisite has `bloomLevel < 3`, do NOT advance to the next module — instead surface the prerequisite gap to the learner and offer to review it ("the seeds need more time to root before this next concept can take hold"). Cite the `blooms-taxonomy` KB and `assessment-framework` KB.
- "Struggled but got there → Box 1" line at L110 stays separate from this milestone; M6 task handles it (M7 finding).

**What might break:**
- Learners mid-project may be blocked by the new gate if their existing state hasn't been backfilled with per-concept Bloom. Mitigation: the inline-fill from M1.2 defaults `bloomLevel: 0` for legacy concepts, which would trigger the gate falsely. **Fix:** in the gate check, if `bloomLevel === 0` AND `concepts[].introduced` is more than 7 days old, assume backfill (allow advancement). Only `bloomLevel === 0` with recent `introduced` blocks.
- Bloom "never demote in /teach" rule could mask regression that `/forget` should catch — that's intentional, but document it.

**How we'd detect breakage:**
- Dogfood: fresh project, teach concept A (prerequisite), move to concept B without completing A → gate should fire.
- Dogfood (legacy): existing learner with v2 state, teach next concept → gate should NOT fire (backfill recognized).
- New `dev/check.sh` rule: `/teach` Phase 5 must mention `bloomLevel` write.

**Rollback:** Revert the gate first (low impact); leave the writes if downstream skills already depend on them.

---

## Task M1.5 — `/explain`, `/practice`, `/forget` write per-concept Bloom appropriately

**Files:**
- `skills/explain/SKILL.md` Phase 5 (L88-96)
- `skills/practice/SKILL.md` Phase 3 step 6 (L140-145)
- `skills/forget/SKILL.md` (entire skill, but specifically the demote logic)

**What changes:**
- **`/explain`** Phase 5: when the Feynman explain-back is strong (per the qualitative criteria at L92-96), set `concepts[].feynmanPassed = true` and update `concepts[].bloomLevel` to the inferred upper-bound (never demote). The "Strong → Box 2" hardcode is fixed in M6 (H4) — don't double-fix here.
- **`/practice`** Phase 3 step 6: on successful exercise completion, update `concepts[].bloomLevel` to the exercise's tier (Beginner = 2, Intermediate = 4, Advanced = 6) capped at the highest correct level demonstrated. Never demote.
- **`/forget`**: when demoting, also reset `concepts[].consecutiveCorrectAtL4Plus = 0` and leave `feynmanPassed` as-is (Feynman passed once is forever; the demote is about retention, not understanding). Box → 1 unchanged.

**What might break:**
- `/explain` rule about "never demote" could mask cases where a learner's explain-back regressed; that's the design (regression is `/forget`'s domain).
- `/practice` "tier = inferred level" may overshoot for a learner who completed an Advanced exercise via brute-force — but the existing acknowledgment doesn't catch that either, so no new regression.

**How we'd detect breakage:**
- Dogfood: complete an exercise, check that `bloomLevel` advanced but `feynmanPassed` did NOT (only `/teach` and `/explain` set it).
- Dogfood: `/forget` a Bloom-4 concept → `consecutiveCorrectAtL4Plus` resets to 0, `feynmanPassed` preserved.

**Rollback:** Revert per-file. Existing skill behavior unchanged at field level.

---

## Task M1.6 — `/progress` Mastery % column computes from the new fields

**File:** `skills/progress/SKILL.md` (around L62-66)

**What changes:**
- Define Mastery % as: `(count of module concepts where mastered === true) / (total module concepts) × 100`, where `mastered` is the full criterion from M1.1.
- Update the Module Breakdown table header to cite the formula inline (or with a footnote to `blooms-taxonomy` KB).
- If no concepts in a module have populated `bloomLevel` (all legacy v2 with `bloomLevel: 0` and recent `introduced`), display "—" instead of "0%" to avoid misleading the learner.

**What might break:**
- Mastery % would read 0% for any existing learner on day one of upgrading until they re-quiz / re-teach. Mitigation: the "—" display covers it.

**How we'd detect breakage:**
- Dogfood on legacy data: `/progress` should show "—" not "0%".
- Dogfood on fresh data: `/progress` should show real percentages.

**Rollback:** Drop the column from the table (audit's M2 fix B). Skill stays functional minus the column.

---

## Task M1.7 — `/housekeep migrate` handles v2 → v3 for spaced-review.json

**File:** `skills/housekeep/SKILL.md` (the migrate subcommand)

**What changes:**
- New migration step: detect `spaced-review.json` at `"version": 2`, perform the inline fill from M1.2, write as `"version": 3`.
- Idempotent: running migrate twice is a no-op the second time.
- Non-destructive: original v2 preserved at `.bodhi/.pre-1.10-backup/spaced-review.json` for one minor version.
- Print before/after concept counts and field-fill stats.

**What might break:**
- Migration could fail if `concepts[]` has any malformed entries → tolerate and warn rather than abort.

**How we'd detect breakage:**
- Dogfood: synthetic v2 file with edge cases (empty concepts array, missing optional fields), run migrate, verify output.
- Re-run migrate; expect no changes second time.

**Rollback:** Restore from `.pre-1.10-backup/`. (Migrate is reversible by design.)

---

## Task M1.8 — Lint rules for M1

**File:** `dev/check.sh`

**New rules:**
- **Rule 16:** any skill that writes `spaced-review.json` must mention `bloomLevel` or `feynmanPassed` (catches regressions where a skill silently strips fields).
- **Rule 17:** `/teach` Phase 5 must mention prerequisite-Bloom gate (catches accidental removal of H3 fix).
- **Rule 18:** `/progress` must mention Mastery formula or "—" fallback (catches H1/M2 regression).

**What might break:** False positives on skills that legitimately don't touch those fields. Mitigation: scope the rules to the specific files.

**How we'd detect breakage:** Run lint against current branch; should clean.

**Rollback:** Remove rules.

---

## Task M1.9 — CHANGELOG + version bump

**Files:** `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `CHANGELOG.md`

**What changes:**
- Bump to `1.10.0` in both manifests.
- CHANGELOG entry: structural schema fix, mastery now observable, migration via `/housekeep migrate`, list of skills updated.
- README "Science" section — no change needed; the formula lives in the KB.

**What might break:** Version drift between manifests (lint catches this).

---

## M1 Dogfood scenarios (must pass before merge)

1. **Fresh project flow:** `/learn` → `/teach` → `/quiz` → `/progress`. Verify `bloomLevel` populated, `consecutiveCorrectAtL4Plus` tracked, Mastery % rendered.
2. **Legacy project flow:** v2 fixture → `/housekeep migrate` → `/teach` → `/progress`. Verify migration successful, gate doesn't false-fire, Mastery % shows "—" until first write.
3. **Mastery gate:** Quiz a concept correctly at Level 4 three times in a row → fourth check shows `mastered === true`.
4. **Demote and recover:** `/forget` a Bloom-4 concept → `consecutiveCorrectAtL4Plus` resets, `feynmanPassed` preserved.
5. **Prerequisite gate:** Try to advance past an incomplete prerequisite → gate fires.

---

# Milestone 2 — `/reflect` Phase 2 retrieval-gate rewrite (1.10.1)

**Goal:** Replace the bare confidence-rating flow with a retrieval-first calibration loop. Closes H5, H6, H9, M13, A5.

**Theory of change:** Five findings cluster in one phase. The current Q3 promotes a concept up a Leitner box on self-reported 8-10 confidence with no comparison against demonstrated performance — the exact Dunning-Kruger trap the metacognition KB names. One Phase 2 rewrite closes all five.

**Risk profile:** LOW. Single skill, well-scoped phase. Behavioral change is visible to the learner (they now have to demonstrate before rating), so the user-facing change is announced clearly.

## Task M2.1 — Rewrite `/reflect` Phase 2 around retrieval-first calibration

**File:** `skills/reflect/SKILL.md` (Phase 2 entirely, L29-51)

**What changes:**
- **New Q3 flow:** retrieval prompt FIRST, then confidence rating, then cross-check.
  1. "Before rating yourself, explain `[main concept]` in 2 sentences as if to a colleague who has never seen it."
  2. Wait for the explanation. Apply the `feynman-technique` KB's three fluency-without-understanding signals (jargon-without-definition, vague hedging, skipped steps) silently.
  3. Then ask the 1-10 confidence rating.
  4. Cross-check against today's quiz/exercise outcomes (from `progress.md` live entry or `spaced-review.json.reviewHistory[]` entries dated today).
  5. **Promote one Leitner box ONLY IF** confidence >= 8 AND retrieval was clean (no fluency-failure signals) AND today's observed outcomes align (no Level-3+ misses on this concept). Otherwise: hold the box, name the calibration gap aloud ("you rated yourself a 9, but the explanation showed some gaps — let us hold this one for review tomorrow"), and add to demote list if retrieval failed outright.
- **Drop the invented "5-7 → Box 1-2 depending on current box" rule** at L44. The new flow has only two outcomes: promote (clean retrieval + observed alignment) or hold/demote.
- **Reference `metacognition` KB explicitly** for the calibration rule and Dunning-Kruger framing.
- **Reference `feynman-technique` KB** for the fluency-failure signals.
- **Reference `desirable-difficulties` KB** for the retrieval-practice rationale (a one-liner is enough).

**What might break:**
- Learners who rate themselves quickly and don't want to "do another exercise" may resist. Mitigation: the retrieval prompt is brief (2 sentences), framed as "before rating yourself, just check" — not as an exercise.
- The new flow takes 30-60 seconds longer per concept. For 5-concept reflections this is 3-5 minutes added. Make it explicit in the skill that this is intentional — quoting Bjork.

**How we'd detect breakage:**
- Dogfood: run `/reflect` with deliberately overconfident self-rating but weak explanation → flow should hold the box and surface the gap.
- Dogfood: clean retrieval + 8 confidence + today's quiz at Level 3+ → flow promotes.
- New `dev/check.sh` rule: `/reflect` must mention `metacognition` KB AND `feynman-technique` KB in Phase 2.

**Rollback:** Revert Phase 2. Pre-rewrite behavior restored.

---

## Task M2.2 — Update Phase 3 high-confidence acknowledgment (A5)

**File:** `skills/reflect/SKILL.md` (L68)

**What changes:**
- "High confidence 8-10 (Q3) | Move concept up one box. Acknowledge alignment with observed performance." → "High confidence 8-10 (Q3) AND clean retrieval AND observed alignment | Move concept up one box. Acknowledge specifically what strategy worked (e.g., 'your approach of breaking the problem down into smaller cases is what made this click'), per the `growth-mindset` KB. Do NOT praise innate ability or general 'you got it'."
- Reference `growth-mindset` KB once at the top of Phase 2 (covers M14 partially).

**What might break:** None — strictly tightening guidance.

**How we'd detect breakage:** Lint for `growth-mindset` mention in `/reflect`.

**Rollback:** Revert the table row.

---

## Task M2.3 — Add reflect → practice handoff (M11)

**File:** `skills/reflect/SKILL.md` (Phase 3 Insight table, L64-69)

**What changes:**
- New table row: `Hard concept identified (Q1) OR low confidence 1-4 (Q3) | Add to demote list AND offer: "Want to start tomorrow with a /practice on [concept]?" Surface the offer once at session end; do NOT auto-invoke. If the learner accepts, write the suggested concept into state.json.lastActivity so /continue picks it up next session.`
- Reference `deliberate-practice` KB (one-liner).

**What might break:** The next `/continue` may pick up the suggestion and surface it; verify the integration.

**How we'd detect breakage:** Dogfood: reflect with low confidence → next `/continue` opens with the practice offer.

**Rollback:** Revert the table row.

---

## Task M2.4 — Lint rules for M2

**File:** `dev/check.sh`

**New rules:**
- **Rule 19:** `/reflect` Phase 2 must reference `metacognition` KB.
- **Rule 20:** `/reflect` Phase 2 must reference `feynman-technique` KB.
- **Rule 21:** `/reflect` Phase 3 must mention `growth-mindset` KB and `deliberate-practice` KB.

**Rollback:** Remove rules.

---

## Task M2.5 — CHANGELOG + version bump

`1.10.0 → 1.10.1`. Entry: `/reflect` Phase 2 rewritten to require retrieval before confidence rating; closes 5 audit findings.

## M2 Dogfood scenarios

1. **Calibrated reflection:** clean retrieval + 9 confidence + today's quiz at Level 4 → promote.
2. **Mis-calibrated reflection:** vague retrieval + 9 confidence → hold box, surface gap.
3. **Low confidence:** 3 confidence → demote AND offer practice for next session.

---

# Milestone 3 — Wire 1.4.0 auto-invoke chains (1.10.2)

**Goal:** Close the "promised but absent" gap. Closes H11, H12, H13, M11, M27, M32, A3, A9.

**Theory of change:** Theme 2 of the audit. CHANGELOG 1.4.0 promised four chains; zero are wired. This milestone wires all four using the existing `--invoked-from=` convention. Each chain needs (a) a trigger point in the caller, (b) chain-guard handling in the callee, (c) the callee added to CLAUDE.md's "Currently chainable" list, (d) a `dev/check.sh` rule to catch future regression.

**Risk profile:** MEDIUM. Touches multiple skills. The added invocations change session flow visibly. Each chain is independent so partial rollback is safe.

## Task M3.1 — Wire `/teach` Phase 3 → `/pair` (H11 + A9 + half of M5)

**Files:**
- `skills/teach/SKILL.md` (Phase 3, L54-66)
- `skills/pair/SKILL.md` (top of file for chain-guard, L11 area)
- `CLAUDE.md` (Currently chainable list at L16)

**What changes:**
- `/teach` Phase 3 gets a new step at the typing-code transition: when the We-Do step would move to actual code-typing, auto-invoke `/bodhikit:pair --invoked-from=teach <concept>` with the concept as the topic argument. Defaults to strong-style mode based on the learner's Bloom level (see `pair-programming` KB).
- `/pair` SKILL.md gets the chain-guard pattern: `if $ARGUMENTS contains --invoked-from=, skip personality/state-schema re-load and skip mode-prompt — the caller passes the resolved mode and topic.`
- `CLAUDE.md` "Currently chainable" list adds `/pair`.
- `/pair` references `zone-of-proximal-development` and `pair-programming` KBs at the top (already partially there).

**What might break:**
- Auto-invocation could chain `/teach → /pair → /pair's own session-end → /teach Phase 4`. Verify the return path — `/pair` Session End should hand control back to `/teach` Phase 4 rather than fully exiting. Add explicit handback prose.
- If `/pair` is auto-invoked in Phase 3, the learner may exit pair mode before Phase 4 fires — verify `/teach` handles the "learner exited mid-pair" case gracefully (proceed to Phase 4 with what was completed).

**How we'd detect breakage:**
- Dogfood: `/teach python:dictionaries` → Phase 3 should auto-invoke pair when code-typing begins. Verify the handback to Phase 4.
- Lint rule: `/teach` Phase 3 must mention `/pair` invocation. `/pair` must have `--invoked-from=` guard (existing rule 9 will catch this).
- Lint rule: CLAUDE.md "Currently chainable" must include `/pair`.

**Rollback:** Revert all three files. `/pair` becomes user-only-invoked again.

---

## Task M3.2 — Wire `/practice` Phase 3 → `/debug-together` (H12)

**Files:**
- `skills/practice/SKILL.md` (Phase 3 step 4, L126-133)
- `skills/debug-together/SKILL.md` (chain-guard)
- `CLAUDE.md` (Currently chainable list)

**What changes:**
- `/practice` Phase 3 step 4 ("If the code does not work"): after the existing graduated hints fail (or before, conditionally on the code-reviewer agent's `bugFound` signal from M3.4), auto-invoke `/bodhikit:debug-together --invoked-from=practice <brief bug description>`. **Do NOT pass a file path** as positional argument (per CLAUDE.md chain convention — `/debug-together` discovers failing code from `exercises/<current-module>/`).
- `/debug-together` gets chain-guard pattern: `if $ARGUMENTS contains --invoked-from=, skip personality/state-schema re-load and skip Phase 0 framing — the caller has the context.`
- `CLAUDE.md` adds `/debug-together` to "Currently chainable".

**What might break:**
- The new flow makes `/practice` longer when bugs happen. That's intentional but should be announced.
- If `bugFound` is set wrongly by the code-reviewer agent (a code smell mistaken for a bug), the chain fires unnecessarily. Mitigation: only fire when bugFound=true AND the existing hint chain has been at least partially exhausted (1 hint given).

**How we'd detect breakage:**
- Dogfood: `/practice` with a known-broken exercise → after first hint, debug-together fires.
- Lint rule: `/practice` Phase 3 must mention `/debug-together`. `/debug-together` must have chain guard.

**Rollback:** Revert.

---

## Task M3.3 — Wire `/teach` Phase 4 → `/debug-together` (H13 + A3)

**File:** `skills/teach/SKILL.md` (Phase 4 step 4, L94-98)

**What changes:**
- L98 ("Not working: guide them to find the issue (Socratic method).") is replaced with: `4. Not working: auto-invoke /bodhikit:debug-together --invoked-from=teach <brief description of the failing behavior>. The sub-skill discovers failing code from exercises/<current-module>/ per CLAUDE.md chain convention. After /debug-together returns, return to Phase 5 (Verify and Record).`
- Cross-references `scientific-debugging` KB once in Phase 4.

**What might break:**
- Same handback concern as M3.1 — verify `/debug-together` hands control back to `/teach` rather than fully exiting.

**How we'd detect breakage:**
- Dogfood: `/teach` with an exercise that the learner gets wrong → debug-together fires, then `/teach` Phase 5 runs.
- Lint rule: `/teach` Phase 4 must mention `/debug-together`.

**Rollback:** Revert L98.

---

## Task M3.4 — Add `bugFound` to `code-reviewer` agent output schema (M32)

**File:** `agents/code-reviewer.md` (Output Format section, L46-59)

**What changes:**
- Output Format gains two optional fields per finding:
  - `**Bug indicator:** true|false` — does this finding describe behavior that's actually wrong (not just a code smell)?
  - `**Bug summary (if bug):** [one-line description]` — populated when Bug indicator is true.
- Update `/review`, `/practice`, `/teach` to check the flag in their respective agent invocations and act on it (M3.2 + M3.3 already use it; `/review` gets an "Want to debug this with `/debug-together`?" offer when bugs found).

**What might break:**
- Agents may over-flag bugs. Mitigation: instruct the agent that bug indicator is for actual incorrect behavior, not style/idiom critique.
- Backward compatibility: existing call sites should treat missing `Bug indicator` as `false` (additive output).

**How we'd detect breakage:**
- Dogfood: review a known-broken file → agent should flag bugFound=true.
- Dogfood: review correct-but-ugly code → bugFound=false.

**Rollback:** Revert agent schema. Downstream calls treat field as absent.

---

## Task M3.5 — Wire `/evaluate` Closing → `/mentor` opt-in (M27)

**File:** `skills/evaluate/SKILL.md` (Closing section, L79-91)

**What changes:**
- After the existing Capstone offer block (L83-89), add a second opt-in offer when this evaluation moves the project to `completedProjects` OR detects a major milestone (significant Bloom delta from prior evaluation):
  > "One more invitation. The path forward is yours to choose, but if you would like to step back and look at the larger arc — where this project fits in your broader journey, what could come next — `/bodhikit:mentor` can hold that conversation. It is not part of the course. Take it if it calls to you."
- Do NOT auto-invoke. Opt-in only. Mirrors the Capstone pattern exactly.
- `/mentor` does NOT need chain-guard for this offer (it's opt-in, not auto-invoke), but we may add it for consistency in M3.6.

**What might break:** None — additive prose offer.

**How we'd detect breakage:**
- Dogfood: `/evaluate` on a completed project → both offers shown.
- Dogfood: `/evaluate` mid-journey → neither offer shown.
- Lint rule: `/evaluate` Closing must mention `/mentor` when project completion is detected.

**Rollback:** Revert.

---

## Task M3.6 — Add chain-guard to `/mentor` (consistency)

**File:** `skills/mentor/SKILL.md` (top of file)

**What changes:**
- Add chain-guard pattern: `if $ARGUMENTS contains --invoked-from=, skip personality/state-schema re-load and skip Phase 1 setup framing — the caller has the context. Use the remaining argument as the leading question.`
- Add `/mentor` to CLAUDE.md "Currently chainable".

**What might break:** None — additive.

**How we'd detect breakage:** Lint rule 9 (chainable list).

**Rollback:** Revert.

---

## Task M3.7 — Lint rules for M3

**File:** `dev/check.sh`

**New rules:**
- **Rule 22:** `/teach` Phase 3 must mention `/pair` invocation.
- **Rule 23:** `/practice` Phase 3 must mention `/debug-together`.
- **Rule 24:** `/teach` Phase 4 must mention `/debug-together`.
- **Rule 25:** `/evaluate` Closing must mention `/mentor` (under completion gate).
- **Rule 26:** Update chainable list (rule 9) to include `pair`, `debug-together`, `mentor`.
- **Rule 27:** code-reviewer agent must include `Bug indicator` in output schema.

**Rollback:** Remove rules.

---

## Task M3.8 — CHANGELOG + version bump

`1.10.1 → 1.10.2`. Entry: 1.4.0's auto-invocation chains finally wired. Lists the four chains: `/teach → /pair`, `/practice → /debug-together`, `/teach → /debug-together`, `/evaluate → /mentor` (opt-in).

## M3 Dogfood scenarios

1. **Teach + pair:** `/teach` reaches code-typing → pair fires → handback works.
2. **Practice + debug-together:** broken exercise → hint → debug-together fires → handback works.
3. **Teach + debug-together:** failing You-Do exercise → debug-together fires.
4. **Evaluate + mentor:** complete a project → see both offers.
5. **Code-reviewer signal:** review broken code → bugFound=true.

---

# Milestone 4 — One-line KB references batch (1.10.3)

**Goal:** Add missing KB references where the methodology is honored but not cited. Closes M10, M12, M14, M16, M18, M20, M23, M24, M26, A6.

**Theory of change:** Audit Move #4 — ten low-risk, mostly one-line edits. No behavioral changes; just making implicit references explicit so the progressive-disclosure contract holds (each KB loads only when its phase fires; each phase that uses a KB cites it).

**Risk profile:** LOW. All additive. Lint will already catch most of these once rules from earlier milestones land.

## Task M4.1 — `/pair` Mode 2 cites `deliberate-practice` KB (M10)

**File:** `skills/pair/SKILL.md` (Mode 2 Ping-Pong, L72-104)

**What changes:**
- Under "Research basis" at L74, add: "Reference the `deliberate-practice` KB: each ping-pong test must isolate ONE skill at the learner's edge of ability and provide immediate pass/fail signal; vary the behavior under test across rounds to prevent rote pattern-matching."

**What might break:** None.

**Rollback:** Revert.

---

## Task M4.2 — `/teach` Phase 4 cites `desirable-difficulties` KB (M12)

**File:** `skills/teach/SKILL.md` (Phase 4 reference line, L71)

**What changes:**
- L71 expands from "Reference the `deliberate-practice` and `assessment-framework` knowledge bases." to "Reference the `deliberate-practice`, `desirable-difficulties`, and `assessment-framework` knowledge bases."
- L83 "(desirable difficulty)" gets a brief KB-grounded restatement: "(per the `desirable-difficulties` KB — specifically generation and variation: the exercise should require the learner to construct the solution, not just recognize it)."

**Rollback:** Revert L71, L83.

---

## Task M4.3 — `/reflect` Phase 2 cites `desirable-difficulties` (M13 cross-fix)

Already covered in M2.1. Verify it landed.

---

## Task M4.4 — `/reflect` and `/debug-together` load `growth-mindset` KB (M14, M16)

**Files:**
- `skills/reflect/SKILL.md` (Phase 3, around L54)
- `skills/debug-together/SKILL.md` (Phase 0, L15-30)

**What changes:**
- `/reflect` Phase 3 already partially addressed in M2.2. Verify `growth-mindset` is referenced.
- `/debug-together` Phase 0: after the existing reference to `scientific-debugging` KB, add: "Reference the `growth-mindset` KB for the praise-strategy language patterns. 'Praise the debugging process' resolves to the KB's concrete examples (e.g., 'your approach of forming a hypothesis before changing code is the move that's catching real bugs'), not ungrounded encouragement."

**Rollback:** Revert.

---

## Task M4.5 — `/evaluate` loads `metacognition` KB with prediction step (M18)

**File:** `skills/evaluate/SKILL.md` (between Phase 2 and Phase 3, new Phase 2.5)

**What changes:**
- New Phase 2.5 "Predict Your Trajectory" inserted before Phase 3 (Comparative Analysis):
  - Reference `metacognition` KB.
  - Before revealing the trajectory-analyzer report, ask the learner three quick prediction questions: (1) biggest growth area, (2) biggest gap, (3) current Bloom level per major topic.
  - Persist as `predictionDelta` field in the new evaluation entry in `assessment-history.json` (extend state-schema KB in M4.5a if needed).
  - In Phase 4 Report, surface the calibration gap explicitly ("you predicted X as your biggest growth; the data shows Y. That gap is the metacognitive learning.").

**What might break:**
- Adds time to `/evaluate`. Make it brief; cap at 3 questions.
- `predictionDelta` is a new field — needs schema-KB update.

**Rollback:** Revert phase + schema entry.

---

## Task M4.6 — `skill-assessor` elicits learner self-rating per sub-topic (M20)

**File:** `agents/skill-assessor.md` (around L26-60)

**What changes:**
- Before the first question on each sub-topic, the agent prompts: "Before I ask, how would you rate yourself on `<sub-topic>`? (1-5; 1 = total beginner, 5 = could teach it)."
- Output table gains a `learnerSelfRating` column alongside `agentClassification` and `Confidence`.
- Note in output: parent skills can use the delta to surface calibration gaps.

**What might break:**
- Makes assessment longer. Cap to ONE self-rating per sub-topic; not per-question.
- Parent skills (`/learn`, `/assess`, `/evaluate`) must tolerate the new column (additive — should be fine).

**Rollback:** Revert agent output schema.

---

## Task M4.7 — `/teach-back` cites `constructivism` (M23)

**File:** `skills/teach-back/SKILL.md` (Phase 4, L118-142)

**What changes:**
- Phase 4 reference line gains `constructivism` KB. Frame the "stay silent; the writing is the demonstration" rule explicitly as the KB's "fully independent" tier — the capstone instance of project progression by level.

**Rollback:** Revert.

---

## Task M4.8 — `/mentor` Phase 4 cites `constructivism` (M24)

**File:** `skills/mentor/SKILL.md` (Phase 4, L65-71)

**What changes:**
- Add KB reference at Phase 4 top: "Reference the `constructivism` KB for the spiral-curriculum mechanic."
- Each suggested path option must name at least one concept from prior projects that it will revisit at a higher Bloom level.
- (Note: H10 fix to flip Options-generation is in M6, not here — keep this M4 task additive.)

**Rollback:** Revert.

---

## Task M4.9 — `/plan` Regenerate mode references KBs (M26 with nuance fix)

**File:** `skills/plan/SKILL.md` (Regenerate mode, L87-100)

**What changes:**
- Fix the pointer error from the audit: change "/learn Phase 4" → "/learn Phase 3 (plan principles) plus Phase 4 (sectional v2 layout)".
- Add at top of Regenerate mode: "Reference the `zone-of-proximal-development`, `constructivism`, and `spaced-repetition` KBs."

**Rollback:** Revert.

---

## Task M4.10 — `/practice` Phase 2 cross-references constructivism ladder (A6)

**File:** `skills/practice/SKILL.md` (Phase 2 around L43-98)

**What changes:**
- One line at the top of Phase 2: "Exercise-scale Beginner/Intermediate/Advanced tiers correspond to tiers 2-4 of the `constructivism` KB's project ladder applied at exercise scope. Do not restate the ladder; reference the KB."

**Rollback:** Revert.

---

## Task M4.11 — Lint rules for M4

**File:** `dev/check.sh`

**New rules:**
- **Rule 28:** `/pair` Mode 2 must reference `deliberate-practice`.
- **Rule 29:** `/teach` Phase 4 must reference `desirable-difficulties`.
- **Rule 30:** `/debug-together` Phase 0 must reference `growth-mindset`.
- **Rule 31:** `/evaluate` must reference `metacognition`.
- **Rule 32:** `/teach-back`, `/mentor`, `/plan` Regenerate must reference `constructivism`.

**Rollback:** Remove rules.

---

## Task M4.12 — CHANGELOG + version bump

`1.10.2 → 1.10.3`. Entry: ten KB references added across skills for progressive-disclosure contract compliance.

---

# Milestone 5 — `/pair` scope decision (1.10.4)

**Goal:** Resolve `/pair`'s half-wired state. Closes M5, M6, M8, L8 (+ resolves remaining A9 ambiguity from M3).

**Theory of change:** Audit Move #5. After M3 wired `/teach → /pair`, the remaining `/pair` findings are about ZPD-gated role reversal (not time-gated), spaced-repetition KB citation, deliberate-practice for Ping-Pong (M4 already added), and offering `/pair` from `/practice` as the active-collaboration alternative. We're committing to full wire, not scope-down — since M3 already wired the chain, scope-down would mean reverting M3.

**Risk profile:** MEDIUM. Most edits to one file; behavioral change (ZPD-gated reversal) is observable to the learner. Test against existing flows.

## Task M5.1 — Replace time-gated role reversal with ZPD signal-gated reversal (M5)

**File:** `skills/pair/SKILL.md` (Mode 1 Strong-Style step 7, L68)

**What changes:**
- L68 "Role reversal as competence grows: After 10-15 minutes of strong-style, offer: 'Now let us switch.'" → "Role reversal triggers on ZPD 'Below the ZPD' detection signals (per `zone-of-proximal-development` KB): (a) the learner is typing without hesitation, (b) anticipating the next navigation step, (c) explaining ahead of the prompt. When at least two of these signals fire within a session window, offer: 'You are starting to navigate without me. Want to switch?' The time floor is now a guard against premature handback: do not offer reversal before 5 minutes (the learner needs enough surface to demonstrate signals)."

**What might break:**
- The signals require the AI to track session-level behavior. Risk: too cautious → reversal never fires; too eager → reverses before the learner is ready. Test with intermediate-Bloom learner profile.

**How we'd detect breakage:**
- Dogfood: simulate a confident learner — verify reversal fires.
- Dogfood: simulate a struggling learner — verify reversal does not fire.

**Rollback:** Revert L68.

---

## Task M5.2 — `/pair` Session End references `spaced-repetition` KB with initial-box rule (M8)

**File:** `skills/pair/SKILL.md` (Session End step 2, L136-139)

**What changes:**
- L138 ("Add new concepts to `.bodhi/spaced-review.json`") expands to: "Apply the `spaced-repetition` KB update rules: new concepts start in Box 1 with `nextReview` = tomorrow and `bloomLevel: 0` (per M1.1 schema). Concepts the learner demonstrated mastery of during the session move per the KB's correct/incorrect mapping."
- Add `spaced-repetition` to the references-load line at the top of Session End.

**What might break:** None — corrects an existing contract violation.

**Rollback:** Revert.

---

## Task M5.3 — `/teach` Phase 4 scaffolding adds Below-ZPD escalation gate (M6)

**File:** `skills/teach/SKILL.md` (Phase 4 around L75-91)

**What changes:**
- Phase 4 reference line adds `zone-of-proximal-development` KB.
- Add a Below-ZPD signal check: "If at the Phase 2 Checkpoint OR the Phase 5 retention check the learner answers instantly with full correctness AND no engaged elaboration (e.g., flat 'yeah, obvious'), the learner may be Below the ZPD on this concept. Skip ahead within the module to the next concept, or escalate the next exercise's difficulty per the ZPD KB."

**What might break:**
- Risk of mis-classifying a confident-but-engaged learner as Below-ZPD. Guard: requires BOTH instant correctness AND lack of elaboration. Either alone doesn't trigger.

**Rollback:** Revert.

---

## Task M5.4 — `/practice` Phase 3 offers `/pair` as collaboration alternative (L8)

**File:** `skills/practice/SKILL.md` (Phase 3 step 5 "If they are stuck before starting" at L135-138, and after the 3-hint exhaustion in step 4)

**What changes:**
- Step 5: at the end of the existing decomposition path, add: "Or, if the learner prefers collaboration over decomposition, offer: 'Want to switch to pair mode? `/bodhikit:pair --invoked-from=practice <topic>` will work through this together.'"
- Step 4: after the 3-hint exhaustion path, before the "re-teach" fallback, add the same offer.
- Reference `pair-programming` KB.

**What might break:** None — additive offer.

**Rollback:** Revert.

---

## Task M5.5 — Lint rules for M5

**File:** `dev/check.sh`

**New rules:**
- **Rule 33:** `/pair` Strong-Style mode must mention ZPD signals (not time-gated).
- **Rule 34:** `/pair` Session End must reference `spaced-repetition`.
- **Rule 35:** `/teach` Phase 4 must reference `zone-of-proximal-development`.
- **Rule 36:** `/practice` Phase 3 must mention `/pair` offer.

**Rollback:** Remove.

---

## Task M5.6 — CHANGELOG + version bump

`1.10.3 → 1.10.4`. Entry: `/pair` fully wired with ZPD-gated reversal, spaced-rep contract, and bidirectional offers from `/practice`.

---

# Milestone 6 — Lint upgrade + remaining fixes (1.10.5)

**Goal:** Close remaining findings and prevent regression. Closes H4, M7, H10, L2, L3, L6, A1, A2, A4, A7, A8 (+ promotes M6 lint warns to hard fails).

**Theory of change:** Audit Move #6 + the leftover HIGH (H4, H10) and MEDIUM findings that don't fit the earlier clusters. Final milestone before sprint close.

**Risk profile:** LOW. Mostly small, targeted edits. The lint-warn → lint-fail promotion may surface previously-tolerated issues; handle iteratively.

## Task M6.1 — Fix hardcoded Leitner transitions (H4, M7, H5 inline rule)

**Files:**
- `skills/explain/SKILL.md` (L88)
- `skills/teach/SKILL.md` (L110)
- `skills/reflect/SKILL.md` (any remaining inline mapping after M2)

**What changes:**
- `/explain` L88: "Strong final explanation → Box 2. Gaps remained → Box 1." → "Strong final explanation → move up one box from current (max 5), per the `spaced-repetition` KB. Gaps remained → Box 1, per the KB's demote rule. Do NOT hardcode destination boxes."
- `/teach` L110: "Demonstrated understanding → move up one box from current. Struggled but got there → Box 1." → "Demonstrated understanding → move up one box from current. Struggled but got there → treat as correct (move up one); do NOT demote on partial success — that conflates struggle with failure." Optionally add a canonical "partial" rule to the spaced-repetition KB first (M6.1a below).
- `/reflect` cross-check after M2 that no inline mappings remain.

**What might break:**
- Some learners may see fewer demotions on partial-success quizzes. That's the corrected behavior, not a regression.

**Rollback:** Revert per-file.

---

## Task M6.1a — (Optional) Add canonical "partial" rule to `spaced-repetition` KB

**File:** `knowledge/spaced-repetition/SKILL.md`

**What changes:**
- New rule in the "Rules (canonical)" section: "Partial recall (struggled but eventually correct): stay in current box; `nextReview` = today + (current box interval / 2). Treat partial as 'needs reinforcement soon but not a reset.'"
- All skills that reference partial outcomes cite this rule.

**What might break:** New mathematical interval (half the current). Edge case: current box = 1 → half of 1 day = today, which collides with new-concept logic. Guard: minimum `nextReview` = tomorrow.

**Rollback:** Revert KB entry; M6.1 falls back to "treat as correct" without the partial rule.

---

## Task M6.2 — `/mentor` Phase 4 inverts to learner-generated options (H10)

**File:** `skills/mentor/SKILL.md` (Phase 4, L65-71)

**What changes:**
- Replace L65-71 with: "Phase 4: Generate Options (Options). Ask first, do not prescribe. 'What paths do you see from here? Where would you start if you had to choose right now?' Let the learner generate options. Then, AFTER they have offered their own paths: 'Here are a couple I see that might complement those — feel free to take, leave, or modify.' Offer 1-2 additional options only as augmentation, never as the primary list. Reference `mentoring-theory` KB: the learner generates options, not the mentor."

**What might break:**
- A learner who has no ideas may stall. Fallback: if "I do not know" → "Let us start with what you have ruled out. What do you NOT want to do next?" Then build up.

**Rollback:** Revert L65-71.

---

## Task M6.3 — `/evaluate` retention rollup cites canonical view (L2)

**File:** `skills/evaluate/SKILL.md` (L73)

**What changes:**
- Either: (a) add a "Retention Rollup Views" section to `spaced-repetition` KB defining a named 3-tier rollup, then L73 cites it; or (b) drop the inline tier scheme and use box-by-box display directly.
- Recommend (a) — it lets `/progress` (L76) and `/evaluate` (L73) share one rollup.

**What might break:** `/progress` may use a different rollup format; align in same PR.

**Rollback:** Revert KB section and skill edits.

---

## Task M6.4 — `/explain` Phase 2 gets CHECKPOINT marker (L3)

**File:** `skills/explain/SKILL.md` (L37-44)

**What changes:**
- L37-39 promoted to: "**CHECKPOINT: Do not proceed to Phase 3 until the learner has produced an explain-back in their own words. No proceeding on 'I get it' alone — this is the heart of the Feynman technique.**" Matches `/teach-back` formatting.

**Rollback:** Revert.

---

## Task M6.5 — `/explain` Phase 3 adds "Fluency without understanding" gap bucket (A4)

**File:** `skills/explain/SKILL.md` (Phase 3 around L49-60)

**What changes:**
- Add a fifth gap category at L60: "**Fluency without understanding:** jargon used without definition, vague hedging that papers over uncertainty, steps quietly skipped. Per the `feynman-technique` KB — these three signals are Feynman-failure indicators. Route any of them into Phase 4's mini-explanation loop the same way as other gaps."

**Rollback:** Revert.

---

## Task M6.6 — `/mentor` Phase 1 label fix (L6)

**File:** `skills/mentor/SKILL.md` (L22)

**What changes:**
- "## Phase 1: Understand the Learner (Reality)" → "## Phase 1: Understand the Learner (Kram: Acceptance)". Leaves Phase 3 as the canonical GROW Reality phase. Phases 2-5 are unchanged.

**Rollback:** Revert L22.

---

## Task M6.7 — `/practice` Phase 1 reads spaced-review for Box-1 prioritization (A1)

**File:** `skills/practice/SKILL.md` (Phase 1, L15-34)

**What changes:**
- Add to Phase 1 step 3: "When `$ARGUMENTS` is absent OR 'next', read `.bodhi/spaced-review.json` for Box-1 concepts tied to the current module. Prefer one of those for the exercise topic if available; announce the choice ('Targeting `<concept>` — it is in Box 1 from `<date>`'). Falls through to plan-position if no Box-1 concepts tied to current module."

**Rollback:** Revert.

---

## Task M6.8 — `/practice` Phase 2 loads `desirable-difficulties` + sketch-before-scaffolding (A2)

**File:** `skills/practice/SKILL.md` (Phase 2, L37-106)

**What changes:**
- Add `desirable-difficulties` KB to Phase 2 reference line at L39.
- Add a pre-scaffolding sketch step for Beginner/Intermediate tiers: "Before delivering starter files (Beginner) or test cases (Intermediate), ask: 'Before I give you the scaffolding, walk me through how you would approach this in 2-3 sentences.' Read their sketch; surface any obvious wrong-turn before they invest in implementation. Per `desirable-difficulties` KB: generation strengthens encoding."
- Enforce variation: "Read the current module's `exercises/` directory before designing this exercise; if a prior exercise covers the same concept, vary the context (different domain, different data shape, different success criterion) — do not duplicate."

**Rollback:** Revert.

---

## Task M6.9 — `/plan` View mode surfaces Spiral Revisits (A7)

**File:** `skills/plan/SKILL.md` (View mode, L24-51)

**What changes:**
- Add a "Spiral Revisits" line/section drawn from existing per-phase plan files' Bloom + spaced-review-concepts fields, distinct from the weekly Spaced Review Schedule section. Show concepts that reappear across phases at increasing Bloom targets.

**Rollback:** Revert.

---

## Task M6.10 — `/mentor` Phase 5 adds success-measurement prompt (A8)

**File:** `skills/mentor/SKILL.md` (Phase 5, L75-82)

**What changes:**
- Add a fourth prompt to Phase 5: "How will you know you have succeeded? What evidence will you trust?" Do NOT add a redundant commitment prompt — the `/learn` handoff already operationalizes commitment.

**Rollback:** Revert.

---

## Task M6.11 — Promote lint warns to hard fails

**File:** `dev/check.sh`

**What changes:**
- Rules 12-15 (currently `warn`) promoted to `err`.
- The pre-existing comment at L8-11 said this would happen "in 1.8.0 once the punch list is clean" — that prediction was wrong; do it in 1.10.5 instead. Update the comment.
- Add cumulative lint check: every rule introduced in M1-M5 (rules 16-36) becomes part of the standard set.

**What might break:**
- Any latent warns become CI-blocking. Verify clean before merging.

**Rollback:** Demote rules back to warn.

---

## Task M6.12 — CHANGELOG + version bump + README counts sync

`1.10.4 → 1.10.5`. Entry: lint upgrade, remaining audit fixes, sprint close. Update README skill count if any changes.

---

# Release-time tasks

## Task R.1 — Full dogfood pass on a synthetic learner profile

Create a synthetic `learningWithBodhi/` with realistic data: 2 active projects, 1 completed, 30+ days of progress, mixed Bloom levels, some Box-1 concepts. Run:

1. `/status all` → verify no health flags.
2. `/continue <project>` → full session: spaced review → teach → practice → reflect.
3. `/evaluate <project>` → verify trajectory-analyzer + Phase 2.5 prediction.
4. `/teach-back` (if eligible) → verify constructivism reference.
5. `/mentor` → verify learner-generated options flow.

Document any deviation from expected behavior. **This is the integration regression check.**

## Task R.2 — Migration smoke test on v2 fixture

Take a v2 fixture (pre-1.10) project. Run `/housekeep migrate`. Verify:
- `spaced-review.json` now v3 with new fields.
- Existing flow continues to work.
- Idempotency: second migrate is no-op.
- Backup preserved at `.pre-1.10-backup/`.

## Task R.3 — Update `gaps_of_pedagogy.md` with closure annotations

Annotate each finding in the original audit doc with: `CLOSED in M<n> — task M<n>.<m>`. Keep refuted section unchanged. This becomes the audit's "Phase 3 — Implementation" appendix and serves as the closure receipt.

## Task R.4 — Tag and push

After 1.10.5 dogfood clean: tag, push to Codeberg (source of truth), GitHub mirror auto-syncs. Update marketplace.json `metadata.description` if counts changed.

---

# Risk register (cross-cutting)

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Schema migration breaks existing state | LOW | HIGH | M1.7 idempotent `/housekeep migrate` with backup; M1.2 inline-fill tolerance |
| Auto-invoke chains create infinite loops | LOW | MEDIUM | Chain-guard pattern + handback prose; each callee returns control explicitly |
| Lint promotion (M6.11) blocks pre-existing warns | MEDIUM | LOW | Run lint clean at M5 close; fix any latent warns before promoting |
| `/reflect` retrieval-first flow feels too long | MEDIUM | LOW | Cap retrieval prompt at 2 sentences; framing explains the Bjork rationale |
| `/mentor` Phase 4 inversion stalls on "I don't know" | MEDIUM | LOW | Built-in fallback: "what would you NOT want?" |
| Bloom advancement gate (H3) false-fires on legacy data | MEDIUM | MEDIUM | M1.4 includes legacy-detection (bloomLevel: 0 + old `introduced` → allow) |
| New fields not preserved by skills that miss the schema update | LOW | HIGH | M1.8 lint rule enforces; "read before write, preserve unknown fields" rule in state-schema KB |
| `/pair` ZPD signal-gated reversal never fires (too cautious) | MEDIUM | LOW | Time floor of 5min still exists; failsafe is the learner can ask "let's switch" anytime |
| `code-reviewer` bugFound over-flags | MEDIUM | MEDIUM | Clear instruction in agent: "bug = incorrect behavior, not style"; downstream calls always offer, never auto-fire |

---

# What this sprint does NOT address

Findings outside this sprint's scope (none — all 44 verified findings are addressed). Out-of-scope explicitly:

- Performance / context-budget refactoring (separate concern; 1.7.x already did the heavy lift)
- New methodologies beyond the 12 already in the README Science section
- UI/UX of CLI output (out of audit scope)
- Marketplace metadata beyond version + counts

---

# Approval checklist for Anjan

Before I start M1, confirm:

- [ ] Sprint shape and milestone order (1.10.0 → 1.10.5) acceptable?
- [ ] Schema migration approach (v2 → v3 with inline-fill + `/housekeep migrate`) acceptable?
- [ ] Auto-invoke chain wiring with handback prose acceptable (vs. opt-in offers)?
- [ ] `/reflect` Phase 2 rewrite changes user-visible behavior — acceptable?
- [ ] `/mentor` Phase 4 inversion changes user-visible behavior — acceptable?
- [ ] Lint promotion in M6 acceptable?
- [ ] Should I dogfood between every milestone, or batch dogfooding at sprint end?
- [ ] Per-milestone CHANGELOG entries OR one sprint-close entry?
- [ ] Annotation of `gaps_of_pedagogy.md` with closure receipts — keep in repo or delete after closure?

Once approved, I start M1.1 (state-schema KB extension) as the first PR.
