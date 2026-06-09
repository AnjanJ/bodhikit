# Changelog

All notable changes to BodhiKit will be documented in this file.

## [1.10.7] - 2026-06-09

### Fixed
- **Legacy fallthrough rule corrected — `bloomLevel: 0` alone is the predicate, not `bloomLevel: 0 AND lastReviewed: null`.** The 1.10.0 rule paired the two checks as a conservative guard: a concept with `bloomLevel: 0` only fell through to "allow advancement" if `lastReviewed` was also null. Dogfooding against a real v2 `spaced-review.json` (in `learn_with_bodhi/rails-react-scaling/`) showed every concept had a populated `lastReviewed` from pre-v3 quizzes — which is the normal state of real v2 data. The combined predicate would have **false-blocked module advancement on every existing learner immediately after migration** and would have made `/progress` Mastery % compute `0%` for legacy modules instead of displaying `—`. The corrected predicate uses `bloomLevel: 0` alone — the field has never been written by any v3 writer, so the gate has no opinion; `lastReviewed` is not part of the check.
- **`/teach` Phase 1 prerequisite gate** now allows advancement on any prerequisite with `bloomLevel: 0` regardless of `lastReviewed`; only `1 <= bloomLevel < 3` blocks (the prerequisite has been classified but has not reached Apply).
- **`/progress` Mastery % display** shows `—` for any module where every concept has `bloomLevel: 0`; once at least one concept has `bloomLevel > 0`, the formula computes against the v3-classified subset.
- **`state-schema` and `state-migration` KBs** document the corrected predicate as canonical and carry a historical note explaining why the 1.10.0 rule was wrong, so future contributors do not re-derive the broken combination.

### Added
- **`dev/check.sh` rule 40** catches any file pairing `bloomLevel: 0` with `lastReviewed: null` in the same logical predicate, exempting paragraphs that explicitly mark the combination as historical / broken / corrected. Prevents the regression that the 1.10.0 → 1.10.7 chain just walked through.

### Why this exists
The first real dogfood pass — reading a single live `spaced-review.json` end-to-end before running any skill — surfaced this bug. The 1.10.0 design intent was correct (do not block on a value that no v3 writer ever wrote), but the implementation was overdetermined: requiring both `bloomLevel: 0` AND `lastReviewed: null` mis-modeled how migration interacts with pre-v3 data. The corrected rule keeps the design intent and matches the data shape that migration actually produces.

The good news: the 1.10.7 fix is a four-file edit (`state-schema` KB, `state-migration` KB, `/teach`, `/progress`) and the lint rule preventing regression is one paragraph. The five other v3 writers (`/quiz`, `/explain`, `/practice`, `/forget`, `/pair`) never used the `lastReviewed`-paired check — they all set `bloomLevel` directly on the concepts they touch, which is the correct shape.

This is a tail patch on a tail patch (1.10.6 closed the audit, 1.10.7 closes a regression the audit-closure work introduced) — but the rationale for keeping it as its own minor release is the same as 1.10.6's: v1.10.5 and v1.10.6 are tagged and on Codeberg. Retroactively editing them would mislead anyone who installed at the old SHA.

## [1.10.6] - 2026-06-09

### Changed
- **`/quiz` Phase 2 now ZPD-signal-gated, not Bloom-distribution-only** (M4). The original Question Mix table set the prior distribution; the new within-quiz adjustment treats the mix as a *budget* and shifts the *distribution* on the fly based on `zone-of-proximal-development` KB signals. Below-ZPD signals (quick correct, no engagement) move the next question up one Bloom level; two consecutive Below signals drop the easier band entirely. Beyond-ZPD signals (repeated "I do not know," hint did not help) step down one level; two consecutive Beyond signals drop the harder band and ground out where the learner can demonstrate something. Total question count unchanged; the distribution adapts to where the learner actually is rather than where the prior assessment said they were.
- **`/learn` Phase 3 Plan Principles now require a Spiral Revisit per phase** (M21). Each phase after Phase 0 MUST name at least one concept from an earlier phase that this phase revisits at a *higher* target Bloom level — the `constructivism` KB's spiral-curriculum mechanic made enforceable rather than aspirational. Each `plan/phase-{N}.md` file includes a `## Spiral Revisits` section near the top declaring which concepts are being deepened and from which earlier phase. `/plan` View mode (1.10.5) reads these sections to surface the spiral arc; `/plan` Regenerate (1.10.3) preserves them.
- **Two new lint rules in `dev/check.sh`** (rules 38, 39 — single-severity err since 1.10.5): `/quiz` Phase 2 must reference `zone-of-proximal-development` KB; `/learn` Phase 3 must declare the per-phase Spiral Revisit requirement.

### Why this exists
Two audit findings (M4, M21) were missed during the 1.10.0–1.10.5 sprint despite each being listed and validated in `dev/gaps_of_pedagogy.md`. The post-tag verification turned them up by diffing the audit's finding-ID set against the CHANGELOG's references. Both fixes are small (one phase reference + one principle each); shipping them under their own patch release rather than retroactively editing the 1.10.5 tag preserves the as-shipped record while honestly closing the audit.

With M4 and M21 closed, **every finding in the audit's confirmed and adjusted lists is now addressed in code**, with M32 documented as deliberately dropped per the sprint-review D3 rationale. The audit-closure receipt in `dev/gaps_of_pedagogy.md` and the sprint-summary table in the 1.10.5 CHANGELOG remain accurate for their respective releases; this entry adds the missing pair as a tail patch.

## [1.10.5] - 2026-06-09

### Changed
- **Hardcoded Leitner box destinations replaced with KB references** (H4, M7). `/explain` Update Tracking no longer says "Strong → Box 2, Gaps → Box 1" (which silently demoted a learner already in Box 3); now it says "treat as correct recall per the `spaced-repetition` KB — move up one box (max 5)." `/teach` Phase 5 no longer says "Struggled but got there → Box 1" (which conflated productive struggle with failure); now treats struggled-but-arrived as correct (move up one box). The KB defines no "partial" demote rule, and the audit caught both skills inventing one.
- **`/mentor` Phase 4 inverted to learner-generates-first** (H10). The original presented 2-3 paths for the learner to choose from, directly contradicting the `mentoring-theory` KB's explicit Options rule: "The learner generates options, not the mentor." The rewrite asks first ("From where you are now, what paths do you see ahead?"), handles "I do not know" via the negative-space prompt ("What do you NOT want to do next?"), and only after the learner has generated their own paths offers 1-2 augmentation options as a complement — never as the primary list.
- **Canonical retention rollup view** added to the `spaced-repetition` KB (L2). The "Retention Rollup Views" section defines one named 3-tier rollup (Strong = Box 4-5, Building = Box 2-3, Needs review = Box 1). `/evaluate` Phase 4 and `/progress` Spaced Repetition Health both cite the section by name and display the same buckets. Previously each invented its own rollup with subtly different boundaries.
- **`/explain` Phase 2 promoted to CHECKPOINT** (L3). The "Do NOT skip this phase" line read as guidance; the new CHECKPOINT marker matches the formatting used in `/teach-back` and makes the gate enforceable.
- **`/explain` Phase 3 adds a fifth gap bucket: fluency-without-understanding** (A4). The `feynman-technique` KB names three failure signals (jargon-without-definition, vague hedging, skipped steps); Phase 3's original four buckets caught none of them. The new fifth bucket routes any of the three signals into Phase 4's mini-explanation loop.
- **`/mentor` Phase 1 label corrected** from "(Reality)" to "(Kram: Acceptance)" (L6). Phase 3 is the canonical GROW Reality phase; Phase 1 is the Kram acceptance/setup phase. The duplicate label was a mis-tagging, not a phase-order issue — phases 2-5 already flow Goal → Reality → Options → Will canonically.
- **`/practice` Phase 1 prioritizes Box-1 concepts from the current module** (A1). When `$ARGUMENTS` is "next" or absent, the skill now reads `.bodhi/spaced-review.json` for Box-1 concepts tied to the current module and prefers one of those for the exercise — Box 1 is the highest-leverage deliberate-practice target the system can name. Falls through to plan-position only if no Box-1 concept exists for the module. Explicit `$ARGUMENTS` always wins; the skill does not override the learner's stated choice.
- **`/practice` Phase 2 sketch-before-scaffolding gate + variation enforcement** (A2). Per the `desirable-difficulties` KB's **generation** principle, Beginner and Intermediate tiers now run a 30-second sketch step before scaffolding is delivered ("Walk me through how you would approach this in 2-3 sentences"); obvious wrong-turns get surfaced before the learner invests in implementation. Per the **variation** principle, the skill reads prior entries in `exercises/<current-module>/` before designing the exercise and varies context if a prior exercise covers the same concept. Advanced tier skips the sketch gate — the absence of scaffolding *is* the sketch step.
- **`/plan` View mode surfaces Spiral Revisits** (A7). New section in the view output reads each `plan/phase-{N}.md` and extracts concepts that reappear in later phases at higher target Bloom levels. If the plan does not declare target Bloom levels for revisits, the section says so honestly ("Spiral revisits not declared in current plan — run `/plan regenerate` to apply the constructivism principle.") rather than omitting silently.
- **`/mentor` Phase 5 success-measurement prompt** (A8). The Will phase now asks the third canonical GROW-Will question — "How will you know you have succeeded?" — capturing the answer in the learner's own words. Timeline and commitment are already operationalized via the `/learn` handoff; success-measurement was the missing third.
- **All M1-M5 lint warns promoted to hard fails.** `dev/check.sh` is now single-severity — every rule emits `err` and exits 1 on violation. The `warn()` helper is kept for future intentionally-soft checks but no current rule uses it. The pre-existing 1.7.0 soft-warn rules (12-15) are also promoted; the `docs/example-project/` is in v2 layout per 1.7.1 so the promotion is no-op on current data.

### Why this exists
M6 closes the remaining single-finding fixes the audit identified — eleven targeted edits across nine surfaces. The cluster has two themes: (a) the audit caught skills that *cited* the KB but then invented inline mechanics that contradicted it (H4, M7 hardcoded boxes; H10 inverted Options; L2 reinvented rollup), and (b) the audit caught skills that *honored* the KB in spirit but missed a specific operationalization the KB calls out by name (L3 missing CHECKPOINT; A4 missing fluency-without-understanding bucket; A1 missing Box-1 prioritization; A2 missing generation gate; A7 missing spiral revisits in View; A8 missing success-measurement prompt; L6 label correction). The fixes are individually small; in aggregate they tighten the contract between every cited KB and the skill that cites it. The lint promotion makes future drift catchable at PR time rather than surfacing in audit form months later — which was the whole point of the authoring contract in the first place.

### Sprint summary (1.10.0 → 1.10.5)
This release closes the pedagogy audit (`gaps_of_pedagogy.md`): **35 confirmed findings + 9 adjusted = 44 actionable items**, plus the sprint review's D1/D2/D3/D5 corrections, all landed across six minor releases. Per-release summaries:

| Release | Closes | Theme |
|---|---|---|
| 1.10.0 | H1, H2, H3, M2, M3 | Per-concept Bloom + Feynman tracking makes mastery observable |
| 1.10.1 | H5, H6, H9, M13, A5 | `/reflect` Phase 2 rewritten as retrieval-first calibration |
| 1.10.2 | H11, H12, H13, M27, A3, A9 | 1.4.0 chains wired as opt-in offers (not auto-invocations) |
| 1.10.3 | M10, M12, M14, M16, M18, M20, M23, M24, M26, A6 | KB references batch + `/evaluate` Phase 2.5 calibration |
| 1.10.4 | M5, M6, M8, L8 | `/pair` fully wired with ZPD-signal-gated reversal |
| 1.10.5 | H4, M7, H10, L2, L3, L6, A1, A2, A4, A7, A8 | Targeted fixes + lint promotion to single severity |

**Total: 44 findings closed.** Lint is now hard-fail on every rule. The plugin's authoring contract is fully enforced — any future drift between cited KB and citing skill, between schema declaration and skill writer, between offer text and chain flag, will surface as a build failure.

## [1.10.4] - 2026-06-09

### Changed
- **`/pair` Mode 1 step 7 (role reversal) is now ZPD-signal-gated, not time-gated.** The hardcoded "After 10-15 minutes of strong-style, offer the switch" was scaffolding-by-clock, contradicting the `zone-of-proximal-development` KB's principle that scaffolding must fade as competence grows. The rewrite uses four observable-in-conversation signals (re-specified per the sprint review's D5 correction): the learner volunteers the next navigation step before being asked; their post-piece explain-back goes deeper than asked (trade-offs, edge cases, connections); a divergence they pushed turned out to be the better approach; or they preempt a syntax hint two or more times. When at least two fire, the switch is offered. A 5-minute floor prevents premature offers (the learner needs surface to demonstrate signals); a 25-minute ceiling triggers the Analogy-Escalation Protocol or sub-concept decomposition instead of pushing reversal that is not coming.
- **`/pair` Session End now references the `spaced-repetition` KB** and writes the v3 per-concept fields per the `state-schema` KB — new concepts initialize with `bloomLevel: 0`, `feynmanPassed: false`, `consecutiveCorrectAtL4Plus: 0`; mastery-demonstrated concepts move up one box per the KB's correct-recall rule. `feynmanPassed` is NOT set here — pairing's step-6 explain-back is necessary-but-not-sufficient for the gate (that field is owned by `/teach` and `/explain` Phase 5). Closes the v3-fields lint warn that was deferred from M1.
- **`/teach` Phase 4 has a Below-ZPD escalation gate.** Before delivering the calibrated exercise, the skill checks whether the Phase 2 Checkpoint signaled the learner is *Below* the ZPD (instant correctness AND flat acknowledgment AND no questions). If so, the planned exercise would be busywork; the skill instead skips ahead within the module, escalates the Bloom tier, or surfaces the choice to the learner. Beyond-ZPD is already covered via the Analogy-Escalation Protocol; this gate covers the opposite tail.
- **`/practice` Phase 3 now offers `/pair` as a collaboration alternative** to decomposition when the learner is stuck before starting. The decomposition path stays available; pair is named as a peer alternative, not a replacement, for learners who would do better with collaboration than further breakdown.
- **Four new lint rules in `dev/check.sh`** (warn for now, promoted in 1.10.5): `/pair` Mode 1 must reference ZPD for reversal gating; `/pair` Session End must reference spaced-repetition; `/teach` Phase 4 must reference ZPD (Below-ZPD gate); `/practice` Phase 3 must offer `/pair`.

### Why this exists
Four audit findings (M5, M6, M8, L8) clustered on `/pair`'s under-instrumentation relative to its documented pedagogical surface area. The audit named `/pair` as the most under-cited skill in the plugin: time-gated where it should be competence-gated, silent on the spaced-repetition contract it actually applies, and absent from `/practice`'s stuck-branch offer list. M3 already wired the `/teach → /pair` offer; M5 finishes the work — ZPD-gated reversal, spaced-repetition contract honored, and the bidirectional `/practice → /pair` offer added.

The sprint review (D5) caught that the audit's original "typing without hesitation" / "anticipating the next step" signals were not observable in a chat-based skill (the AI sees turns, not keystrokes or pauses). The re-specified signals are observable-in-conversation: volunteering navigation, going deeper than asked, divergence-as-navigation, preempting hints. They map to the same Below-ZPD detection rationale without requiring keystroke analytics.

The Below-ZPD gate in `/teach` closes the opposite tail of the ZPD gate the plugin already had. The original Phase 4 scaffolding selector keyed off Bloom level alone — never re-evaluating whether the learner's actual session signals matched the Bloom level on file. A learner who reaches Phase 4 with engaged-and-confident answers gets escalated; a learner who reaches it with flat-and-disengaged answers gets skipped past. Both responses respect what the conversation just showed.

## [1.10.3] - 2026-06-09

### Added
- **`/evaluate` Phase 2.5 — Predict Your Trajectory.** Before the Phase 3 trajectory-analyzer reveal, the skill collects three quick predictions from the learner: biggest growth, biggest gap, per-topic Bloom snapshot. Phase 4's report surfaces the calibration delta explicitly — what was predicted vs what the data shows — framed as the metacognition signal underneath every other skill. Across multiple evaluations the gap should shrink; that shrinkage *is* the calibration meta-skill. Capped at 60 seconds; quick predictions, not deliberation.
- **`predictionDelta` field on `assessment-history.json` entries** (optional). Populated by `/evaluate` Phase 2.5; absent for other triggers. Fields: `predictedBiggestGrowth`, `measuredBiggestGrowth`, `predictedBiggestGap`, `measuredBiggestGap`, `perTopicBloomPredictions[]` (each `{name, predicted, measured}`), one-sentence `calibrationNote`. Documented in `state-schema` KB.
- **`learnerSelfRating` collection in `skill-assessor` agent.** Before the first question on each sub-topic, the agent asks a single 1-5 self-rating. Output table gains a `Self-rating (1-5)` column. Parent skills (`/learn`, `/assess`, `/evaluate`) can compute Dunning-Kruger calibration deltas at sub-topic granularity. The rating does not bias question difficulty — the adaptive sequence remains independent.

### Changed
- **Eight KB references added at the canonical phase / mode** where the methodology was implicitly honored but not cited — closing the audit's "implicit citation" pattern:
  - `/pair` Mode 2 now references `deliberate-practice` (Ping-Pong IS deliberate practice — edge-of-ability per round, immediate red→green feedback, variation across rounds enforced).
  - `/teach` Phase 4 now references `desirable-difficulties` (the "slightly harder" framing now grounds in **generation** and **variation** specifically).
  - `/debug-together` Phase 0 now references `growth-mindset` (the "praise the debugging process" instruction grounds in the false-effort nuance with concrete strategy-praise examples).
  - `/evaluate` now references `metacognition` (Phase 2.5 is the load-bearing application).
  - `/teach-back` Phase 4 now references `constructivism` (the Phase 4 silence rule is the KB's "fully independent" tier; teach-back is the plugin's capstone instance of project progression by level).
  - `/mentor` Phase 4 now references `constructivism` for the spiral-curriculum mechanic; each suggested option must name the concept it revisits at a higher Bloom level.
  - `/plan` Regenerate now references `zone-of-proximal-development`, `constructivism`, and `spaced-repetition` at the top of the mode; the cross-reference fix points to `/learn` Phase 3 (principles) plus Phase 4 (layout), not Phase 4 alone.
  - `/practice` Phase 2 now cross-references the `constructivism` KB's 5-tier project ladder, noting Beginner/Intermediate/Advanced map to tiers 2-4 at exercise scope.
- **Six new lint rules in `dev/check.sh`** (warn for now, promoted in 1.10.5): rules 28-33 enforce each of the above references at the right phase / mode.

### Why this exists
Ten audit findings (M10, M12, M14, M16, M18, M20, M23, M24, M26, A6) flagged a single pattern: the methodology was honored in practice — the right framing, the right pacing, the right principles — but not cited explicitly. The progressive-disclosure contract requires the cite: a phase that uses a methodology MUST load its KB, both so a contributor can trust the file is the canonical home and so the lint can catch drift. The fixes are mostly one-line additions; `/evaluate` Phase 2.5 is the substantive change because the audit identified it as the highest-leverage Dunning-Kruger calibration moment in the plugin — and one the existing flow simply skipped past.

## [1.10.2] - 2026-06-09

### Changed
- **CHANGELOG 1.4.0's auto-invoke chains are wired** — but as **opt-in offers**, not auto-invocations, mirroring the 1.8.0 Capstone pattern. The original 1.4.0 contract overstated the integration ("/teach Phase 3 auto-invokes /pair", "/practice + /teach auto-invoke /debug-together when code breaks", "/evaluate auto-invokes /mentor at milestones"); 1.10.2 honors the spirit (the partner skill is named, the chain flag is wired, the moment is identified) without the loss of learner agency that an unconditional auto-invoke would cause. Each offer surfaces at the canonical moment, names the trade-off ("the longer path that teaches the skill"), and lets the learner accept or decline.
  - **`/teach` Phase 3** now offers `/bodhikit:pair --invoked-from=teach <concept>` when the We-Do step would move from talking-through-approach to typing code. Skipped when the concept is purely conceptual, the learner already declined pair this session, or the session is in its last 5-10 minutes.
  - **`/practice` Phase 3 step 4** ("If the code does not work") now offers `/bodhikit:debug-together --invoked-from=practice <brief description>` after Hint 2 (Approach) — before the Near-solution hint, so accepting the offer routes to TRAFFIC rather than collapsing to a near-solution that teaches the fix more than the debugging.
  - **`/teach` Phase 4 step 4** ("Not working") now offers `/bodhikit:debug-together --invoked-from=teach <brief description>` instead of going straight to the Socratic-method one-liner. Per the CLAUDE.md chain convention, the failing code is discovered from `exercises/<current-module>/` — no file path is passed positionally.
  - **`/evaluate` Closing** now offers `/bodhikit:mentor` after the existing Capstone offer (when shown) or as the sole offer at a major milestone. Triggers: project moves to `completedProjects` OR ≥2-level Bloom delta on any major topic since the previous evaluation OR ≥1-level delta on 3+ topics simultaneously. Skipped on mid-journey evaluations without a milestone.
- **Chain-guard pattern extended to `/pair`, `/debug-together`, and `/mentor`.** Each now checks `$ARGUMENTS` for `--invoked-from=`; when present, they skip personality/state-schema reload and skip their setup framing (the caller has context). `CLAUDE.md`'s "Currently chainable" list expands from 6 skills to 9, with a chain-shape note clarifying that the three new entries are offered (opt-in), not auto-invoked.
- **Five new lint rules in `dev/check.sh`** (warn for now, promoted in 1.10.5): rule 9 expanded to enforce the chain guard on the new chainable trio; rules 22-26 enforce offer language at the canonical moments (`/teach` Phase 3 → `/pair`, `/practice` Phase 3 → `/debug-together`, `/teach` Phase 4 → `/debug-together`, `/evaluate` → `/mentor`) and check that the three new chainable skills declare their offer/opt-in framing in the opening 30 lines.

### Why this exists
Five audit findings (H11, H12, H13, M27, A3, A9) traced to the same gap: CHANGELOG 1.4.0 documented four auto-invoke chains, GUIDE.md referenced them, but none was actually wired in the relevant phases. The audit's recommended fix was to wire the chains; the sprint review (D2) pushed back against unconditional auto-invocation as a state-machine risk (no return semantics exist in the plugin today; the existing `/continue → /status → /teach → /reflect` chain is sequential composition by the caller, not nested with handback). Opt-in offers close the same findings — the partner skill is named at the moment the audit identified, the chain flag is wired, the learner's agency is preserved — without inventing new return semantics. Accepting an offer transfers control; declining keeps the current skill's flow intact. The Capstone pattern (1.8.0) is the template: a structured invitation framed as credibility-protection, not gatekeeping.

The "decline by default" framing matters pedagogically. An auto-invoked `/debug-together` would teach the learner that bugs require a heavy ceremony; an *offered* `/debug-together` teaches that there is a longer path available when the shorter path stalls — and that choosing the longer path is itself a learning move. Same goes for `/pair` (collaboration is a tool, not a default mode) and `/mentor` (cross-project reflection is invited, not imposed at every milestone).

## [1.10.1] - 2026-06-09

### Changed
- **`/reflect` Phase 2 rewritten as a retrieval-first calibration loop.** The bare 1-10 confidence rating is gone; in its place, Q3 runs retrieval → rating → cross-check. Step 1 asks the learner to explain the concept in 2 sentences before rating, applying the `feynman-technique` KB's three fluency-without-understanding signals (jargon-without-definition, vague hedging, skipped steps) silently. Step 2 collects the rating. Step 3 cross-references today's `progress.md` and the day's `reviewHistory[]` entries on this concept. Only then does the Leitner update fire: promote ONLY IF confidence ≥ 8 AND retrieval was clean AND observed outcomes align; hold the box (naming the calibration gap aloud) if confidence is high but retrieval or outcomes disagree; demote to Box 1 on confidence ≤ 4, retrieval failure, or learner decline. The invented "5-7 → Box 1-2 depending on current box" rule is gone — there was no canonical home for it in the `spaced-repetition` KB; mid-band now holds and retests tomorrow.
- **`/reflect` Phase 3 strategy-naming acknowledgment.** Per the `growth-mindset` KB's false-effort nuance, high-confidence-with-aligned-outcome acknowledgments now name the *strategy* that worked ("your approach of breaking it into smaller cases"), never the *trait* ("you got it"). The mismatched-outcome row reinforces the calibration framing rather than glossing it.
- **`/reflect` → `/practice` handoff at weak signals.** For any concept named in Q1 as hard OR rated 1-4 in Q3 OR with retrieval failure, the skill offers (does not auto-invoke) `/practice <concept>` for the next session. Acceptance writes the concept into `state.json.lastActivity` so the next `/continue` opens with the targeted deliberate-practice rep.
- **Four lint rules added in `dev/check.sh`** (warn for now; promoted in 1.10.5): `/reflect` Phase 2 must reference `metacognition` and `feynman-technique` KBs; Phase 3 must reference `growth-mindset` and `deliberate-practice` KBs.

### Why this exists
Five audit findings (H5, H6, H9, M13, A5) clustered in `/reflect` Phase 2 around a single mistake: the bare confidence rating promoted concepts up a Leitner box on self-report alone, with no comparison against demonstrated performance. That is exactly the Dunning-Kruger trap the `metacognition` KB names and the illusion-of-competence pattern the `feynman-technique` KB is designed to catch. The KB said "compare to actual result"; the skill compared to nothing. One Phase 2 rewrite closes all five — and changes the retention contract from "the learner reports retention" to "the learner demonstrates retention, then reports it, then we cross-check." The 30-60 seconds this adds per concept is itself a deliberate-practice rep (the `desirable-difficulties` KB's retrieval principle) — Bjork-correct cost.

## [1.10.0] - 2026-06-09

### Added
- **Per-concept Bloom + Feynman tracking** in `spaced-review.json`. Three new fields on `concepts[]`: `bloomLevel` (0–6, current per-concept level; ratchet-up only — never demoted by routine writers), `feynmanPassed` (boolean; set once by `/teach` Phase 2 Checkpoint or Phase 5 retention check or `/explain` Phase 5 on a strong explain-back; never unset), `consecutiveCorrectAtL4Plus` (counter; incremented by `/quiz` on correct AND `bloomLevel ≥ 4`; reset to 0 on any incorrect or on `/forget`). `reviewHistory[]` entries now also carry `bloomLevel` (which level the question tested at). The canonical mastery formula now lives in the `state-schema` KB: `mastered = (bloomLevel ≥ 4) AND (consecutiveCorrectAtL4Plus ≥ 3) AND (box ≥ 4) AND (feynmanPassed === true)`. Skills MUST NOT redeclare this formula inline.
- **Prerequisite Bloom gate in `/teach` Phase 1.** When selecting a concept from a *new* module (not concept-to-concept within the same module), the skill reads `spaced-review.json` for the prior module's prerequisite concepts. If any has `bloomLevel < 3` AND has been observed post-migration (`lastReviewed !== null`), the gate fires — surfaces the gap to the learner with the seeds metaphor and offers revisit / defer / pause. Pure legacy entries (`bloomLevel: 0` AND `lastReviewed: null`) fall through as "allow advancement" — the gate cannot judge what was never observed.
- **`/progress` Mastery % column is now computed**, not fabricated. Uses the canonical formula. When every concept in a module is in pure legacy state, displays `—` instead of `0%` to avoid the false implication that the learner tried and failed.
- **`/housekeep migrate` v2 → v3 step (5f-bis).** Inline-fills the three new per-concept fields with safe defaults; preserves pre-v3 `spaced-review.json` at `.bodhi/.pre-1.10-backup/spaced-review.json` for one minor version; idempotent and step-verifying per the 1.7.1 imperative-write pattern. The migration marker is gated on `spaced-review.json` reaching `version: 3` with all three fields present on every concept.
- **Three new lint rules in `dev/check.sh`** (currently `warn`, promoted to `err` in 1.10.5): skills writing `spaced-review.json` must mention at least one v3 field; `/teach` must mention the prerequisite Bloom gate; `/progress` must mention the canonical mastery formula or the legacy fallthrough.

### Changed
- `spaced-review.json` schema bumped to `version: 3`. All other tracking files remain `version: 2` — per-file version is a schema-shape generation, not a cohort marker; the `state-migration` KB documents the v2 / v3 split explicitly. Skills MUST read-tolerate v2 (auto-fill defaults) before writing v3.
- `/quiz` Phase 3 now writes `bloomLevel` per `reviewHistory[]` entry, updates `concepts[].bloomLevel` to the highest correctly-answered level (never demote), and maintains the `consecutiveCorrectAtL4Plus` counter.
- `/teach` Phase 2 Checkpoint and Phase 5 retention check now write `feynmanPassed: true` when the learner produces a clear, jargon-free explanation. Phase 5 writes per-concept `bloomLevel` (preserve higher; never demote).
- `/explain` Phase 5 writes `feynmanPassed: true` on a strong final explanation and updates `concepts[].bloomLevel` to the inferred upper bound.
- `/practice` Phase 3 step 6 writes `concepts[].bloomLevel` on successful exercise completion — capped at the highest level the learner actually demonstrated, not the exercise's nominal tier. Does NOT write `feynmanPassed` (that field is owned by skills that run an explicit explain-back gate).
- `/forget` resets `consecutiveCorrectAtL4Plus: 0` on demote; preserves `feynmanPassed` (passed once is forever; the demote captures retention drift, not understanding regression).

### Why this exists
Five audit findings (H1, H2, H3, M2, M3 — see `gaps_of_pedagogy.md`) converged on a single root cause: the `blooms-taxonomy` KB defined mastery as "Level 4+ AND 3 consecutive correct AND Box 4–5 AND Feynman passed," but none of those pieces was tracked per concept. `state.json.currentBloomLevel` was sub-topic-coarse; `spaced-review.json.concepts[]` carried no Bloom or Feynman fields; no skill recorded the level a quiz question tested at. So every skill that surfaced "mastery" (the `/progress` Mastery column, the implied `/teach` advancement gate, the assessment-framework's Progression Gates) was either fabricating or silently omitting the answer. One schema extension closes all five — and makes Bloom advancement observable in the place a learner actually feels it: the moment `/teach` would otherwise wave them past a half-rooted prerequisite.

The legacy fallthrough rule (`bloomLevel: 0` AND `lastReviewed: null` = allow advancement) is the M1.4 backfill-bug fix from the sprint review: the gate cannot judge concepts the migration created from thin air with no observation history. Once any v3 writer touches a concept, normal gate logic applies.

## [1.9.2] - 2026-06-08

### Changed
- `GUIDE.md` adds **"The Pedagogy Behind BodhiKit"** — a new section between *Understanding Your Progress* and *How Spaced Repetition Works* answering three questions for the learner: what pedagogy, why, when each fires. Twelve per-methodology cards (Bloom, Spaced Repetition, ZPD, Feynman, Deliberate Practice, Desirable Difficulties, Growth Mindset, Metacognition, Constructivism, Mentoring/GROW, Pair Programming, Scientific Debugging). Each card: what it is, why BodhiKit uses it (the specific learning problem), when it fires (skills + phases), one link to a primary source. Closes with a "How they compose" table showing which methodologies fire at each phase of a learner's journey.
- `Pedagogy:` cross-links added under the Example of 10 skill entries (`/teach`, `/reflect`, `/quiz`, `/forget`, `/explain`, `/practice`, `/pair`, `/debug-together`, `/mentor`, `/teach-back`) so a learner reading about a skill can click through to the underlying research without leaving the GUIDE.

### Why
The GUIDE previously named methodologies in passing (Bloom in `/assess`, Feynman in `/explain`, etc.) but offered no answer to a learner who asked "what pedagogy and why?" The Science section in the README has the citations but no "when it fires" mapping, and the GUIDE did not link to it. The new section closes that gap with deep-dive links at the card level, and the per-skill cross-links make the pedagogy discoverable from any direction.

## [1.9.1] - 2026-06-08

### Changed
- `GUIDE.md` expanded from a thin reference (538 lines) into a complete usage manual (~992 lines). Two structural additions: (1) a "Your Journey from Zero to Completion" worked example following a backend Python engineer learning Rust over 10 weeks — Day 1 install through capstone, with real dialogue snippets and which skill to invoke when; (2) Skills Reference rewritten with a 5-field template per skill (What it does / When to use / When NOT to use / Pairs well with / Example) covering all 20 skills, grouped into six functional categories. Redundant prior sections (Starting a Project, Resuming, Daily Workflow) absorbed into the journey arc — no information lost.
- README link blurb to `GUIDE.md` updated to advertise the new scope.

### Why
The 1.9.0 GUIDE was a reference, not a how-to. Users had no zero-to-completion path and no guidance on when to reach for each skill. A concrete worked example carries more weight than topic-neutral prose, and the 5-field per-skill template makes optimal usage scannable and comparable.

## [1.9.0] - 2026-06-08

### Added
- **Analogy-Escalation Protocol** in `knowledge/feynman-technique/SKILL.md` — a single named protocol every struggle-sensitive skill reaches for when the learner is stuck. Trigger conditions tied to the ZPD "Beyond" signals (cannot articulate confusion, Approach-level hint did not move them, mechanical explain-back, surviving misconception). 4-rung ladder: (1) learner's own domain from `.bodhi-profile.json` `learnerBackground.domains[]`, (2) ask-once for a domain if none on file or all used for this concept, (3) universal-physical analogy as fallback, (4) code-restatement as last resort. Hard 2-analogy cap per concept — after two, the protocol decomposes to a smaller sub-concept rather than reach for a third analogy (correct ZPD response).
- `learnerBackground` object on `.bodhi-profile.json`: `domains[]` (cross-project list of fields/hobbies/jobs the learner knows well) and `analogyHistory[]` (append-only `{concept, domain, landed, date}` log so future invocations on the same concept pick a different domain). Both fields optional; absence means "no prior data" and the protocol falls through naturally. Documented in the `state-schema` KB; writers list updated.

### Changed
- `/teach` Phase 2 Checkpoint and Phase 4 hint chain (between Approach and Near-solution) now invoke the Analogy-Escalation Protocol instead of the one-line "different analogy" instruction.
- `/explain` Phase 1 prefers learner-domain analogies when `learnerBackground.domains[]` is populated; Phase 4 routes gap-refinement through the protocol's ladder rather than picking a random angle. The 2-analogy cap applies per gap.
- `/debug-together` Phase 2 (Hypothesize) pauses debugging and applies the protocol when rubber-ducking surfaces a conceptual gap underneath the bug. Phase 5 (Fix) applies the protocol between Approach and Near-solution hints.
- `/pair` strong-style step 6 (post-piece explain-back) and ping-pong step 3 (learner makes the test pass) invoke the protocol when the explanation is mechanical or the Approach hint did not unstick them.

### Why this exists
Analogies were already mentioned in three places (`feynman-technique` KB step 2, `/teach` Phase 2, `/explain` Phases 1 and 2), but as scattered instructions without a shared trigger condition, escalation order, or cap. The result was that analogies appeared inconsistently across skills — present in `/teach` and `/explain`, absent in `/debug-together` and `/pair` where struggle is most acute — and when they did fire, they reached for universal-physical analogies (mailboxes, libraries) before any attempt to ground in the learner's actual world. The new protocol makes analogy a **response to detected struggle**, escalates from the learner's domain first (highest leverage, lowest reuse if not personalized), caps at two before falling back to sub-concept decomposition (the real ZPD answer), and records what worked so the next session does not repeat. The "ask once for a domain" rung is gated to the moment struggle is detected — the learner is not interrogated at project start about their hobbies, only asked when an analogy is actually about to land.

## [1.8.0] - 2026-06-08

### Added
- `/teach-back` skill — optional capstone offered after `/evaluate` moves a project to `completedProjects`. The learner writes a Socratic-style blog post on a *formerly-shaky-now-solid* topic (multiple assessments climbing from Bloom <3 to ≥4, at least one demote-and-recover in spaced review, currently Bloom ≥4 AND Box ≥3), reads 3–5 acknowledged masters' work on the same topic *after* drafting (Bjork desirable-difficulty sequence — read after, not before), and decides for themselves whether to publish. **The skill never pronounces a post ready or not-ready** — that verdict is earned by the learner against the field, framed as credibility-protection rather than gatekeeping. Posts saved to `learningWithBodhi/<project>/teach-backs/<YYYY-MM-DD>-<slug>.md` (sibling to `.bodhi/`, not inside it, so the learner can edit them in their normal workflow). Reuses `trajectory-analyzer` for candidate topic surfacing and `resource-finder` (with masters-only instruction) for source discovery.
- `/evaluate` Closing section now emits a one-paragraph opt-in offer for `/teach-back` whenever this evaluation moves the project from `activeProjects` to `completedProjects`. Mid-journey evaluations skip the offer. Never auto-invokes.
- `cumulativeStats.teachBacksWritten` and `cumulativeStats.teachBacksPublished` fields added to `.bodhi-profile.json` (default 0; learner self-reports `published` if they actually publish). Profile-writer table in `state-schema` KB updated to list `/teach-back` as a writer.
- `teach-backs/` registered as a new tracking-surface family in `state-schema` KB. Per-post markdown files. Not housekept. Only `/teach-back` writes.

### Why this exists
The system already had a clear ending — `/evaluate` confirms completion and moves the project to `completedProjects`. But "completed" was the *measurement* of mastery, not the *demonstration* of it. The capstone gives the learner a way to demonstrate mastery the way the masters themselves did: by writing something defensible on a topic that was once hard. Picking *formerly-shaky* topics (rather than easy ones) honors Bjork's desirable-difficulty principle and produces the more useful post — the next learner benefits more from "I kept getting this wrong until I realized X" than from "here's how X works." Reading the masters *after* drafting (not before) is the second half of Feynman's technique; reading first would turn the post into a summary of what was read. And the publish question is framed as credibility-*protection* ("publish only when you can defend every claim") not credibility-*building* ("publish to be seen") — the former keeps the learner's interests aligned with the bodhi metaphor of awakening passed forward; the latter would have made BodhiKit into a hype engine at the moment of graduation.

## [1.7.1] - 2026-06-06

### Fixed
- **`/housekeep migrate` write defects.** The v1.7.0 migrate spec used declarative language ("remove the field", "bump the version", "replace progress.md with...") for steps that mutate `state.json` and `progress.md`. Executing models interpreted these as state-descriptions rather than file-write actions, so on real data the migration created the new directories, split `plan.md`, and wrote the receipt — but never actually rewrote `state.json` (left v1 `lastSessionSummary` + `bloomResetNote` fields intact and `version: "1.5.0"` unchanged) or rewrote `progress.md` to v2 live+archive+summary shape. Steps 5a, 5b, and 5c rewritten with explicit imperative writes ("Write the new content using the Write tool"), per-step idempotency checks, and post-write verification. The marker file (5g) now has an explicit precondition block — verify every preceding step persisted to disk before declaring migration complete. A broken migration can no longer falsely report success.
- `.bodhi-profile.projects.json` was being written as `version: 1` because the `state-schema` KB declared it that way. Pinned to `version: 2` in the KB for cohort consistency with every other v2 file; `/housekeep` skill spec updated to enforce.
- `docs/example-project/.bodhi-profile.json` was still in v1 single-file layout (despite v1.7.0 PR 5b claiming otherwise). Split into v2 layout: top-level profile + `.bodhi-profile.projects.json` sibling.

### Added
- `/status all` — table view of every project (active/stale/dormant classification, last-session, completion, health flags). Reads `.bodhi-profile.projects.json` plus each project's `state.json` only — no progress/plan/archive reads.
- `/status <project-name>` — single-project glance for a specific project regardless of which is most recently active.
- Health flags in `/status all`: `⚠ v1 fields` (unmigrated narrative fields in `state.json`), `⚠ unparseable` (JSON parse failure), `⚠ missing files` (state.json present but plan/ or progress.md absent), `⚠ legacy layout` (incomplete migration — `.bodhi/plan.md` or `.bodhi/assessment.md` singular still exist).
- `/learn` **Phase 1.5 — Cross-Project Reconciliation.** Before running skill assessment for a new project, read `.bodhi-profile.json` + `.bodhi-profile.projects.json` and surface: overlap with existing projects, relevant Bloom priors from prior work, capacity flag when ≥ 3 active projects exist. Presents structured options — standalone / fold into existing / replace existing / defer. Phase 2 (skill assessment) now receives Bloom priors as input. First-time learners with no profile see no change.
- `dev/check.sh` extended: rule 15 verifies `docs/example-project` profile uses v2 split layout (no inline `activeProjects` / `completedProjects`; both files declare `version: 2`). Rules 12 and 13 exempt `/status` alongside `/housekeep` — both are v1-boundary skills by design (one migrates, one detects).

### Changed
- `/continue` Phase 5 was already correct in v1.7.0 (Do NOT write `lastSessionSummary` / `bloomResetNote`); no behavioral change. Mentioned here so contributors don't re-flag it during 1.7.1 review.

## [1.7.0] - 2026-06-05

### Added
- `/housekeep` skill — tends the garden of tracking files. Rotates the previous entries of narrative surfaces (`progress.md`, `assessments/latest.md`) into archive directories and writes a 2–20 line summary block with explicit pointers so nothing is lost and nothing is hidden. Idempotent, non-destructive. Single source of all file-rotation logic — every other skill stays oblivious.
- `/housekeep migrate` — one-shot v1 → v2 conversion of pre-1.7.0 tracking files. Splits monolithic `plan.md` into `plan/README.md` + `plan/phase-<N>.md` files; lifts narrative fields (`lastSessionSummary`, `bloomResetNote`) out of `state.json` into `progress.md`; splits `.bodhi-profile.json` into top-level profile + `.bodhi-profile.projects.json`; reorganizes existing assessment files into `assessments/latest.md` + `assessments/archive/`. Preserves the original monolithic files at `.bodhi/.pre-1.7.0-backup/` for one minor version. Reports before/after byte sizes.
- `trajectory-analyzer` agent (Sonnet, read-only, max 15 turns) — reads a learner's full project history (live + archive + assessments + assessment-history + spaced-review + plan phases) and returns a structured trajectory report: per-topic Bloom movement with evidence quotes, retention distribution, activity timeline, precision-gap movements, completion, patterns. Used by `/evaluate` Phase 1 and Phase 3 so the parent skill stays light; for a learner six months in, ~80 KB of archive load happens in the agent's context instead of the parent's. Learner conversation is unchanged from the previous flow.
- `knowledge/read-defaults` KB — per-skill default-read contract, transparency rule, audit/lint guidance. Loaded only by `/housekeep`, the audit, and the lint; skills do not load it at runtime.
- `knowledge/state-migration` KB — schema versioning, migration table, and the full `/housekeep migrate` procedure. Loaded only by `/housekeep migrate`.

### Changed
- `knowledge/state-schema` KB rewritten for v2 tracking-file layout:
  - **Live + archive + summary pattern** for narrative surfaces (sessions, assessments). The live doc holds the latest entry plus a growing summary block with pointers; full prior text lives in the archive directory.
  - **Sectional layout** for plans. `plan/README.md` + `plan/phase-<N>.md` files. Routine skills load only the current phase.
  - **Slim JSON** for `state.json`. No more long narrative fields — `lastSessionSummary` and `bloomResetNote` removed; their content lives in `progress.md`.
  - **Split JSON** for the cross-project profile. `.bodhi-profile.json` keeps top-level + cumulativeStats + patterns; `.bodhi-profile.projects.json` holds `activeProjects` + `completedProjects` arrays.
  - Universal housekeeping protocol documented; only `/bodhikit:housekeep` rotates files.
- `state.json`, `progress.md`, `assessments/`, `plan/`, `.bodhi-profile.json`, `spaced-review.json` all bumped to schema `version: 2`. Older versions are read-tolerated via inline migration per the `state-migration` KB.
- `/status migrate` removed — the `migrate` subcommand moved to `/housekeep migrate` because all file-shape work now lives in one place. `/status` keeps its legacy-path detection notice but redirects users to `/housekeep migrate`.
- `marketplace.json` `metadata.description` and `plugins[0].description` updated to reflect new counts (19 skills, 18 KBs).
- Version bumped in both `plugin.json` and `marketplace.json`.

### Guiding principle

Progressive disclosure applied to the learner's own state. Nothing deleted. Nothing gatekept. Skills load the smallest useful slice by default and reach into the archive only when the learner's situation justifies it — announcing the read in their turn output. The audit and lint catch *accidental* eager loading; a deliberate, situational read is always allowed.

## [1.6.0] - 2026-06-05

### Added
- `/forget` skill — learner-initiated demotion of one or more concepts back to Box 1; comma-separated lists supported; auto-invoked by `/reflect` (batched once per session) when self-rated confidence is 1–4
- `knowledge/state-schema/` KB — canonical shape for `state.json`, `spaced-review.json`, `progress.md`, `.bodhi-profile.json`, plus the project discovery procedure (single source for all skills)
- `~/.bodhikit/config.json` optional global discovery config (`searchPaths` array). Defaults: `$PWD` (with parent walk) and `~/learningWithBodhi`
- Per-project `<repo>/.bodhikit/config.json` override with `projectRoot` — for users who keep `.bodhi/` somewhere other than `learningWithBodhi/` in a specific repo
- One-shot legacy-path migration via `/bodhikit:status migrate` — detects pre-1.6.0 `~/code/learningWithBodhi` or `~/projects/learningWithBodhi` and writes them into `~/.bodhikit/config.json` so discovery keeps finding them
- `.bodhi/assessment-history.json` — structured Bloom's-over-time data appended by `/learn` Phase 2, `/assess`, `/evaluate`, and `/plan regenerate`. `/evaluate` reads it for trajectory analysis. `assessment.md` remains the prose journal
- `--invoked-from=<caller>` convention for sub-skill chaining. Caller skills (currently `/continue`) pass the flag; chainable skills (`/teach`, `/practice`, `/reflect`, `/status`, `/quiz`, `/forget`) check for it and skip personality/state-schema reload and discovery when set
- Migration discipline section in `state-schema` KB — inline read-time migration pattern for forward-compatible schema changes
- Streak acknowledgment table and empty-state language table moved into `teaching-personality` KB (single source for all skills that open sessions or hit empty states)
- Profile feedback loops — `/reflect`, `/practice`, `/teach`, `/evaluate` now update `learningWithBodhi/.bodhi-profile.json` `cumulativeStats` and `patterns` (persistent challenges, consistent strengths)
- New profile fields: `cumulativeStats.totalConceptsLearned`, `cumulativeStats.totalMilestonesReached`, `patterns.persistentChallenges`, `patterns.consistentStrengths`
- `/resources remove <name>` mode
- `dev/install-hooks.sh` — installs a pre-commit hook that runs `dev/check.sh`
- `CLAUDE.md` at repo root — author/dev notes (not loaded by end-user installs)
- `dev/check.sh` — authoring-contract lint (version drift, frontmatter, agent fallback presence, KB references, voice duplication, chain-flag presence, README skill count)

### Changed
- Leitner box→interval mapping and update rules consolidated into the `spaced-repetition` KB. `/continue`, `/teach`, `/explain`, `/quiz`, `/reflect`, `/practice`, `/debug-together`, `/evaluate`, `/progress` no longer restate intervals
- Tracking file shapes consolidated into `state-schema` KB. Skills now reference it instead of restating field lists
- Project discovery consolidated into `state-schema` KB. Removed hardcoded `~/code/...` and `~/projects/...` paths
- Personality voice rules consolidated into `teaching-personality` KB. Skills, agents, and the path-scoped rule reference it with one line instead of restating DO/NEVER lists
- `/teach` and `/practice` now skip the `code-reviewer` agent invocation when no code file exists for the exercise (saves tokens on prose-only or thought-experiment exercises)
- KBs cross-link (`see also` lines) so the KB graph is navigable in both directions
- `marketplace.json` `metadata.description` corrected (was advertising "11 skills, 3 agents, 3 KBs"; now matches the actual 18/3/16 totals)
- Version bumped in both `plugin.json` and `marketplace.json`; README now displays a version badge
- `docs/example-project/README.md` updated for the new file list and discovery layers
- `.gitignore` adds `learningWithBodhi/` (defensive — prevents accidental commits when contributors test the plugin against this repo)

### Fixed
- Drift between `marketplace.json` `metadata.description` and `plugins[0].description`

## [1.5.0] - 2026-03-16

### Changed
- Teaching personality grounded in authentic Buddha and Ambedkar philosophies
- Buddha: Upaya (skillful means), four learner types, Kalama Sutta ("test through experience"), sandassetva teaching process, gradual progression
- Dr. B.R. Ambedkar: "Educate, Agitate, Organize", vachan-manan-chintan-adyeyan (listening, reflection, study), education as empowerment and transformation
- Every principle, language rule, and emotional response now traces to a specific teaching from the four root teachers
- Context optimization: teaching-personality 197→67 lines, skills trimmed 20%, phase-specific KB loading, shared-context in /continue chains

## [1.4.0] - 2026-03-16

### Added
- `/mentor` skill — career and learning path guidance using the GROW model (Whitmore) and Kram's mentoring theory
- `/pair` skill — research-backed pair programming with 3 modes: strong-style (Falco), ping-pong with TDD, navigator (Freudenberg)
- `/debug-together` skill — scientific debugging using Zeller's TRAFFIC method, O'Dell's Debugging Mindset, wolf fence algorithm
- Learner profile system (`learningWithBodhi/.bodhi-profile.json`) for cross-project personalization
- CONTRIBUTING.md for open source contributors
- New research references in README: Kram, Whitmore, Beck, Williams & Kessler, Falco, Zeller, O'Dell, Gauss

### Changed
- Learning methodology KB expanded with mentoring, pair programming, and debugging sections
- Teaching personality KB expanded with debugging, mentoring, and pairing language guidance
- `/learn` now creates and updates the learner profile
- `/mentor` auto-invoked by `/evaluate` at major milestones
- `/pair` auto-invoked by `/teach` during guided practice
- `/debug-together` auto-invoked by `/practice` and `/teach` when code has bugs
- Split monolithic `learning-methodology` KB (392 lines) into 13 focused KBs for progressive disclosure (ETH Zurich 2025 research compliance)
- All skills now reference only the specific KBs they need, reducing context load per interaction
- Knowledge base count: 3 → 16
- Skill count: 14 → 17

## [1.2.0] - 2026-03-15

### Added
- `/teach` skill — proactive guided teaching with explain, demonstrate, practice, verify flow
- `/reflect` skill — end-of-session metacognitive reflection with confidence self-rating
- `/status` skill — quick 3-line check-in (project, module, streak, concepts due)
- Example learning project in `docs/example-project/` showing realistic tracking files
- Error handling fallbacks in all skills that use agents (learn, assess, evaluate, review, resources, plan, practice)
- CHANGELOG.md

### Changed
- `/continue` now auto-invokes `/status`, `/teach`, `/reflect` for complete guided sessions
- Skill count: 11 → 14

## [1.1.0] - 2026-03-14

### Changed
- Made agent usage mandatory in all skills (changed "Delegate to agent" to "You MUST use the Agent tool")
- Used respectful full names: Gautama Buddha, Dr. B.R. Ambedkar, Master Oogway
- Fixed install instructions to match marketplace plugin format (two-step install)
- Added research references and credits for all learning methodologies in README

### Added
- .gitignore for OS files, editor state, and local Claude config
- Author signature and buy-me-a-coffee link in README

## [1.0.0] - 2026-03-14

### Added
- Initial release
- 11 skills: learn, continue, assess, review, quiz, plan, progress, resources, explain, practice, evaluate
- 3 agents: skill-assessor (Sonnet), code-reviewer (Sonnet), resource-finder (Haiku)
- 3 knowledge bases: learning-methodology, assessment-framework, teaching-personality
- 1 path-scoped rule: learning-project (activates in learningWithBodhi/)
- README, GUIDE, LICENSE (MIT)
- Plugin manifests for Claude Code marketplace
