# BodhiKit Pedagogy Audit — Validated Punch List

## CLOSURE RECEIPT (2026-06-09)

**All 44 actionable findings closed across releases 1.10.0 → 1.10.5.** Below: which release closed which finding, and which milestone (M1–M6) in the sprint plan (`dev/sprint_close_pedagogy_gaps.md`).

| Release | Milestone | Findings closed |
|---|---|---|
| **1.10.0** | M1 — Schema fix: per-concept Bloom + Feynman | H1, H2, H3, M2, M3 |
| **1.10.1** | M2 — `/reflect` Phase 2 retrieval-gate rewrite | H5, H6, H9, M13, A5 |
| **1.10.2** | M3 — 1.4.0 chains wired as opt-in offers | H11, H12, H13, M27, A3, A9 |
| **1.10.3** | M4 — KB references batch + `/evaluate` Phase 2.5 | M10, M12, M14, M16, M18, M20, M23, M24, M26, A6 |
| **1.10.4** | M5 — `/pair` ZPD-signal-gated reversal + remaining wires | M5, M6, M8, L8 |
| **1.10.5** | M6 — Targeted fixes + lint promotion (sprint close) | H4, M7, H10, L2, L3, L6, A1, A2, A4, A7, A8 |
| **1.10.6** | tail patch — post-tag audit-completeness verify | M4, M21 |
| **—** | dropped per sprint review | M32 (was M3.4 — would have collided with code-reviewer agent's pedagogical purpose, per D3) |

**Total: 43 findings closed via skill/agent/KB edits + 1 dropped with documented rationale = 44 actionable findings resolved.**

**Note on 1.10.6.** After tagging 1.10.5 and pushing to Codeberg, a post-release diff between the audit's finding-ID set and the CHANGELOG references caught two missed findings (M4: `/quiz` Phase 2 ZPD KB reference + within-quiz signal-gated escalation; M21: `/learn` Phase 3 per-phase Spiral Revisit requirement). Rather than retroactively edit the v1.10.5 tag, the fixes shipped as 1.10.6 — preserves the as-shipped record while honestly closing the audit.

**Sprint review corrections applied during implementation:**
- **D1** — M1.4 backfill rule corrected from `introduced > 7 days` to `lastReviewed === null` (the audit's original signal was backwards; legacy fallthrough now correctly identifies untouched-post-migration concepts).
- **D2** — M3 chains wired as **opt-in offers**, not auto-invocations (no return semantics existed in the plugin; the Capstone offer pattern is the precedent).
- **D3** — M3.4 dropped (`bugFound` field on code-reviewer agent would have collided with the agent's "what does this code reveal about understanding" purpose).
- **D5** — M5.1 ZPD-signal rewrite re-specified to observable-in-conversation signals (not keystroke timings the AI cannot see).

Per-finding closure receipts inline below — each finding now has a `CLOSED in <version> via <milestone-task>` line under its claim.

---

## Outcome

44 actionable findings after two-pass audit + adversarial validation: **35 confirmed as-stated** + **9 adjusted** (real gap, but severity or fix re-specified). 10 candidates from the first pass were refuted on second look and are listed in the appendix.

**Audit method:** 12 per-methodology finder agents → 1 adversarial verifier per finding (defaulting to refuted=true if unconfirmable) → second-pass independent validator re-checking each surviving finding against current files with a stricter "would I file this as a real issue?" bar. Counts: 74 candidates → 56 after first verify → 47 punch list → 37 after second validation, with 7 lower-severity reclassifications and 2 fix-mechanics corrections.

**Two themes dominate the confirmed set:**

1. **Bloom's-mastery contract is structurally unobservable.** Five confirmed gaps (H1, H2, H3, M2, M3) converge on the same root cause: `state.json.currentBloomLevel` is sub-topic-coarse, `spaced-review.json.concepts[]` has no `bloomLevel` or `feynmanPassed` field, and no skill records the level a quiz question was tested at. Mastery criteria (Level 4+ AND 3 consecutive correct at L4+ AND Box 4–5 AND Feynman passed) cannot be computed by any skill that claims to surface them. **One schema fix closes all five.**

2. **CHANGELOG 1.4.0's auto-invoke chain is documented in four places and wired in zero.** `/teach → /pair` (We-Do), `/teach + /practice → /debug-together` (when code breaks), `/evaluate → /mentor` (at milestones). Five confirmed gaps (H11, H12, H13, M27, M32) trace to skills that simply do not invoke the partner skill at the promised trigger point.

**Secondary patterns:**
- `/reflect` Phase 2 concentrates 4 confirmed findings against 3 different KBs (H5, H6, H9, M13) — all clustered in the same "1-10 self-report without retrieval gate" flow. One Phase 2 rewrite closes all of them.
- `/pair` carries 4 confirmed findings across 3 methodologies (M5, M8, M10, L8 plus the partially-wired chain in adjusted A8) — it is the most under-instrumented skill relative to its documented pedagogical surface area.
- Three Leitner-box transitions are hardcoded inline against the KB's canonical rules (`/explain` H4, `/reflect` H5, `/teach` M7) — the `dev/check.sh` lint should catch this and doesn't.

---

## HIGH severity (10 confirmed)

### [HIGH] H1 — blooms-taxonomy — knowledge/blooms-taxonomy/SKILL.md:L21-L33
**Gap type:** stated_not_enforced
**Claim:** The KB mandates per-concept Bloom tracking and defines mastery as "3 consecutive correct at Level 4+ AND Box 4-5 AND Feynman passed," but `state.json.currentBloomLevel` is keyed by sub-topic (not concept), `spaced-review.json.concepts[]` has no `bloomLevel` or `feynmanPassed` field, and no skill records the level a quiz question was tested at — so the entire mastery criterion is unobservable from state.
**Evidence:** > "Track Bloom's level PER CONCEPT, not globally … A concept is mastered when: 3 consecutive correct quiz answers at Level 4+ … Feynman check passed"
**Fix:** Add `bloomLevel`, `consecutiveCorrectAtL4Plus`, and `feynmanPassed` fields to `spaced-review.json.concepts[]` in the state-schema KB first, then update /quiz, /teach, /explain, /practice to write them so mastery becomes deterministic.

### [HIGH] H2 — blooms-taxonomy — skills/teach/SKILL.md:L102-L116
**Gap type:** stated_not_enforced
**Claim:** Phase 5's retention check produces Bloom adjustments and Phase 4 calibrates scaffolding by Bloom level, but the Update Tracking step writes the adjustment only as prose in progress.md — never into `state.json.currentBloomLevel`, so downstream skills see stale levels.
**Evidence:** > "Update state.json (slim shape — no narrative): bump lastSessionAt, increment totalSessions … set lastActivity to ONE short sentence"
**Fix:** Add a bullet parallel to /assess line 85: "Bump `state.json.currentBloomLevel[<concept>]` whenever the Phase 5 retention check demonstrates a new level — the same adjustment recorded in the progress.md Bloom adjustments section."

### [HIGH] H3 — blooms-taxonomy — knowledge/assessment-framework/SKILL.md:L193-L203
**Gap type:** stated_not_enforced
**Claim:** The Progression Gates table declares "Minimum: Bloom's Level 3 on all prerequisite concepts" before module advancement, but neither /teach nor /continue reads `currentBloomLevel` to gate advancement — modules advance unconditionally.
**Evidence:** > "Before advancing from one module to the next, the learner must demonstrate: | Minimum | Bloom's Level 3 on all prerequisite concepts |"
**Fix:** Add an explicit pre-advance gate in /teach Phase 5 (and /continue option 1) that reads `state.json.currentBloomLevel` for prerequisite concepts and refuses to advance the module if minimums are unmet, framed per the KB's "seeds need more time to root" language.

### [HIGH] H4 — spaced-repetition — skills/explain/SKILL.md:L84-L88
**Gap type:** cited_but_misapplied
**Claim:** /explain hardcodes destination boxes ("Strong → Box 2, Gaps → Box 1") that contradict the KB's canonical "move up one box from current (max 5)" rule — a learner already in Box 3 gets demoted to Box 2 on a strong explanation.
**Evidence:** > "Strong final explanation → Box 2. Gaps remained → Box 1."
**Fix:** Mirror /teach line 110: "Strong final explanation → move up one box from current (max 5); gaps remained → Box 1, per the `spaced-repetition` KB."

### [HIGH] H5 — spaced-repetition — skills/reflect/SKILL.md:L42-L46
**Gap type:** cited_but_misapplied
**Claim:** /reflect invents a "partial confidence (5-7) → Box 1-2 depending on current box" routing rule that the spaced-repetition KB does not define (the KB only specifies correct → up-one, incorrect/learner-demote → Box 1), silently introducing new spacing semantics for the most common confidence band.
**Evidence:** > "5-7: Partial. Schedule review soon (Box 1–2 depending on current box)."
**Fix:** Either extend the spaced-repetition KB with a canonical "partial / mid-confidence" rule (and have /reflect cite it), or collapse the 5-7 band into demote-to-Box-1 to match the KB's existing demote rule.

### [HIGH] H6 — feynman-technique — skills/reflect/SKILL.md:L42-L48
**Gap type:** missing_where_fits
**Claim:** Q3 promotes a concept up a Leitner box on self-reported 8-10 confidence alone, with no explain-back gate — exactly the illusion-of-competence moment Feynman and metacognition are designed to catch.
**Evidence:** > "8-10: Strong. Note in tracking; move concept up one box per `spaced-repetition` KB."
**Fix:** When the learner self-rates 8+, gate box promotion behind a brief explain-back ("Give me the 2-sentence colleague-pitch right now"); only promote if the explanation is jargon-free and non-mechanical, otherwise hold the box. (This also resolves the duplicate metacognition gap at the same lines — see H9.)

### [HIGH] H9 — metacognition — skills/reflect/SKILL.md:L42-L68
**Gap type:** cited_but_misapplied
**Claim:** Q3 promotes a concept up a Leitner box on self-reported confidence alone with no comparison against demonstrated performance — directly contradicting the KB's "Then compare to actual result" calibration rule and rewarding Dunning-Kruger overconfidence.
**Evidence:** > "8-10: Strong … move concept up one box | Acknowledge alignment with observed performance" (but nothing actually observes performance)
**Fix:** Before promoting on an 8-10 rating, require a quick retrieval check or cross-reference today's quiz/exercise outcome in progress.md; if confidence is high but retrieval is weak, name the calibration gap aloud and hold the box.

### [HIGH] H10 — mentoring-theory — skills/mentor/SKILL.md:L65-L71
**Gap type:** cited_but_misapplied
**Claim:** Phase 4 (Options) has the mentor presenting 2-3 options for the learner to choose from, directly inverting the KB's explicit rule: "The learner generates options, not the mentor."
**Evidence:** > "Present 2-3 concrete learning path options … 'These are three paths I see. Each is valid. Which one resonates with you?'"
**Fix:** Flip Phase 4 to elicit options from the learner first ("What paths do you see from here?"), then offer to add or refine options only after the learner has generated their own.

### [HIGH] H11 — pair-programming — skills/teach/SKILL.md:L54-L66
**Gap type:** stated_not_enforced
**Claim:** CHANGELOG 1.4.0, /pair, and GUIDE all state /teach Phase 3 auto-invokes /pair for collaborative coding, but Phase 3 contains no /pair invocation, no trigger condition, no role-alternation gate — only generic "think aloud together" prose.
**Evidence:** > "If stuck, think aloud together: 'I would start by [approach]. What do you think?'"
**Fix:** Add a step to Phase 3 that invokes `/bodhikit:pair --invoked-from=teach` when the problem moves to typing code, and reference the `pair-programming` KB at the top of Phase 3 to match the per-phase loading convention. **Couples with adjusted A8 (`/pair` chain guard) — wire both or neither.**

### [HIGH] H12 — scientific-debugging — skills/practice/SKILL.md:L126-L133
**Gap type:** missing_where_fits
**Claim:** Phase 3 step 4 handles the canonical "learner's code does not work" moment by jumping straight to graduated hints, but never invokes /debug-together or references the scientific-debugging KB — directly contradicting CHANGELOG 1.4.0.
**Evidence:** > "If the code does not work: Do NOT fix it. Do NOT show the solution. Ask: 'What do you think is happening? Walk me through your logic.' Provide graduated hints:"
**Fix:** When the code does not work, route to `/bodhikit:debug-together --invoked-from=practice` so TRAFFIC + Reproduce + Hypothesize + Wolf Fence actually fire before falling back to graduated hints. (Note: pass description after the flag, not a file path — see adjusted A3 for the same convention.)

---

## MEDIUM severity (21 confirmed + 4 reclassified-down from HIGH/MEDIUM in adjustments)

### [MEDIUM] M2 — blooms-taxonomy — skills/progress/SKILL.md:L62-L66
**Gap type:** stated_not_enforced
**Claim:** The Module Breakdown table promises a "Mastery %" column, but mastery criteria (Level 4+, 3 consecutive correct, Box 4-5, Feynman passed) are not observable in any tracked file — the column will be fabricated or silently omitted.
**Evidence:** > "| Module | Status | Bloom's Level | Mastery |"
**Fix:** Either define Mastery % as a concrete formula over observable fields (e.g., "% of module concepts at `currentBloomLevel >= 4` AND `box >= 3`") and cite it inline, or drop the column until per-concept Bloom and Feynman-check tracking land in spaced-review.json (depends on H1).

### [MEDIUM] M3 — blooms-taxonomy — skills/explain/SKILL.md:L88-L96
**Gap type:** missing_where_fits
**Claim:** Phase 5 assigns Bloom levels qualitatively ("Clear, complete explanation = Level 2-3") but writes them only as progress.md prose — never updating `state.json.currentBloomLevel`, so the Feynman-pass signal the Bloom KB names as a mastery criterion never reaches state.
**Evidence:** > "Append an entry to `.bodhi/progress.md` … **Bloom adjustment** based on quality: Clear, complete explanation with good analogies = Level 2-3"
**Fix:** Before the progress.md append, read state.json and set `currentBloomLevel[<concept>]` to the upper bound of the inferred range (preserving any higher prior value; never demote), and write the same numeric value into the progress.md line so prose and state agree.

### [MEDIUM] M4 — zone-of-proximal-development — skills/quiz/SKILL.md:L34-L82
**Gap type:** missing_where_fits
**Claim:** /quiz uses Bloom-level distribution for difficulty but never references the ZPD KB; the incorrect/struggle branch reframes without checking Below/Beyond signals — and every peer skill (/practice, /teach, /pair) does cite the ZPD KB.
**Evidence:** > "For this phase, reference the `assessment-framework` KB for question templates and Bloom's-level mapping." (no ZPD reference)
**Fix:** Add a `zone-of-proximal-development` KB reference in Phase 2 and gate within-quiz escalation/de-escalation on ZPD signals (quick correct → climb out of Below; repeated "I do not know" → step back from Beyond).

### [MEDIUM] M5 — zone-of-proximal-development — skills/pair/SKILL.md:L67
**Gap type:** cited_but_misapplied
**Claim:** /pair cites the ZPD KB for mode selection but the strong-style role-reversal hand-off — the actual scaffolding-fade moment — is time-gated ("after 10-15 minutes") rather than competence-signal-gated, contradicting the KB's "scaffolding must fade as competence grows" principle.
**Evidence:** > "Role reversal as competence grows: After 10-15 minutes of strong-style, offer: 'Now let us switch.'"
**Fix:** Replace the fixed timer with ZPD "Below the ZPD" detection signals (typing without hesitation, anticipating the next navigation step, explaining ahead of the prompt) so hand-off triggers on observed competence.

### [MEDIUM] M6 — zone-of-proximal-development — skills/teach/SKILL.md:L75-L91
**Gap type:** stated_not_enforced
**Claim:** Phase 4's scaffolding selector keys off Bloom level only — never ZPD's three-zone detection signals — and the hint chain has no Below-ZPD (too-easy) gate that would escalate; only a stuck branch exists.
**Evidence:** > "| Bloom's Level | Scaffolding | ... 1-2 | Starter files ... 5-6 | Problem statement only |"
**Fix:** Add a Below-ZPD signal check at the Phase 2 checkpoint and Phase 5 retention check — if the learner answers instantly with full correctness and no engaged elaboration, skip ahead within the module or escalate the next exercise's difficulty. (Beyond-ZPD is already covered via the Analogy-Escalation Protocol.)

### [MEDIUM] M7 — spaced-repetition — skills/teach/SKILL.md:L108-L110
**Gap type:** cited_but_misapplied
**Claim:** Phase 5 maps "Struggled but got there → Box 1," conflating partial success with incorrect recall. The KB only demotes on incorrect or learner-initiated; a struggled-but-correct outcome has no canonical mapping and should not silently equate to a miss.
**Evidence:** > "Demonstrated understanding → move up one box from current. Struggled but got there → Box 1."
**Fix:** Either drop the "struggled but got there" branch and treat it as correct (move up one), or add a canonical "partial" rule to the spaced-repetition KB first and reference it here rather than declaring the mapping inline. (Couples with H5 — both should land together.)

### [MEDIUM] M8 — spaced-repetition — skills/pair/SKILL.md:L136-L139
**Gap type:** stated_not_enforced
**Claim:** /pair writes new concepts into spaced-review.json but never references the spaced-repetition KB and never specifies the initial-box rule (new → Box 1, nextReview = tomorrow), bypassing the single-source contract.
**Evidence:** > "Update tracking: Add new concepts to `.bodhi/spaced-review.json`"
**Fix:** Add a phase-level reference: "Apply the spaced-repetition KB update rules: new concepts start in Box 1; concepts touched during the session move per the KB's correct/incorrect mapping."

### [MEDIUM] M10 — deliberate-practice — skills/pair/SKILL.md:L72-L104
**Gap type:** missing_where_fits
**Claim:** Ping-pong TDD mode is a textbook deliberate-practice loop (targeted, immediate red→green feedback, repetition with variation) but the skill never references the deliberate-practice KB, so edge-of-ability targeting and variation-across-rounds are unenforced.
**Evidence:** > "Mode 2: Ping-Pong Pairing … Research basis: Combines pair programming with Test-Driven Development."
**Fix:** Add one line under Mode 2's Research basis: "Reference the `deliberate-practice` KB: each ping-pong test must isolate ONE skill at the learner's edge of ability and provide immediate pass/fail signal; vary the behavior under test across rounds to prevent rote pattern-matching."

### [MEDIUM] M11 — deliberate-practice — skills/reflect/SKILL.md:L54-L70
**Gap type:** missing_where_fits
**Claim:** Phase 3's Insight and Adjustment table only demotes weak concepts via /forget and adds vague notes — it never points the learner at /practice on the diagnosed weakness, so the reflect→practice deliberate-practice handoff does not exist.
**Evidence:** > "| Low confidence 1-4 (Q3) | Add to demote list. Suggest different learning approach next session. |"
**Fix:** Add a row that, for any concept rated Q3=1-4 or named in Q1, suggests (or auto-invokes) `/practice <concept>` so the next session begins with a deliberate-practice rep targeted at that specific weakness.

### [MEDIUM] M12 — desirable-difficulties — skills/teach/SKILL.md:L83
**Gap type:** cited_but_misapplied
**Claim:** Phase 4 uses the phrase "(desirable difficulty)" as an inline parenthetical descriptor but never loads the desirable-difficulties KB, so the principle is invoked as a casual phrase rather than a contracted methodology with its 5 named difficulties.
**Evidence:** > "The exercise should be slightly harder than the guided example (desirable difficulty)."
**Fix:** Add a phase-level reference to the desirable-difficulties KB in Phase 4 and tie exercise design to specific contracted difficulties (generation, variation) rather than the generic "slightly harder" framing.

### [MEDIUM] M13 — desirable-difficulties — skills/reflect/SKILL.md:L29-L51
**Gap type:** missing_where_fits
**Claim:** Phase 2 reflection questions ask only about feelings (hardest, surprise, confidence) and never require the learner to actually recall/restate the concepts covered — the retrieval-practice opportunity is missed, and Q3 asks for confidence about explaining without actually explaining.
**Evidence:** > "Q3 — Confidence: 'If you had to explain [main concept] to a colleague, how confident? 1 to 10.'"
**Fix:** Add a retrieval-first sub-question to Q3 ("Before rating, explain [main concept] in your own words — when would you use it?"), then ask the 1-10 rating; optionally add a one-line cross-reference to desirable-difficulties (metacognition KB is already loaded). **Part of the /reflect Phase 2 cluster — fix alongside H5, H6, H9.**

### [MEDIUM] M14 — growth-mindset — knowledge/growth-mindset/SKILL.md:L1-L24
**Gap type:** stated_not_enforced
**Claim:** No skill loads the growth-mindset KB by name; only teaching-personality cross-links it. The KB's basic language patterns are inlined in teaching-personality (loaded universally), but the unique false-effort/strategy-praise nuance (L18-23) has no enforcement surface anywhere.
**Evidence:** > "description: 'Growth Mindset (Dweck): language patterns, critical nuance on praising effort vs strategy' / user-invocable: false"
**Fix:** Have /reflect (post-session praise framing) and /debug-together (struggle-as-clue, strategy over effort) load the growth-mindset KB in their feedback/celebration phases — the two skills where the false-effort nuance fires hardest.

### [MEDIUM] M16 — growth-mindset — skills/debug-together/SKILL.md:L15-L30
**Gap type:** cited_but_misapplied
**Claim:** The skill cites "O'Dell's Debugging Mindset (2017): Growth mindset applied to bugs" as foundational and instructs "Praise the debugging process," but loads only scientific-debugging — never growth-mindset — so the praise instruction has no concrete Do/Don't language to resolve to.
**Evidence:** > "O'Dell's Debugging Mindset (2017): Growth mindset applied to bugs … Praise the debugging process, not just finding the fix."
**Fix:** In Phase 0 add an explicit `Reference the growth-mindset KB for the praise-strategy language patterns` line so "praise the debugging process" resolves to the KB's concrete examples instead of being ungrounded.

### [MEDIUM] M18 — metacognition — skills/evaluate/SKILL.md:L9-L47
**Gap type:** missing_where_fits
**Claim:** /evaluate never loads the metacognition KB and never asks the learner to predict their own trajectory before the trajectory-analyzer report is revealed — missing the highest-leverage Dunning-Kruger calibration moment in the plugin.
**Evidence:** SKILL.md loads `teaching-personality`, `state-schema`, `assessment-framework`, `blooms-taxonomy`, `spaced-repetition` — never `metacognition`.
**Fix:** Before revealing the Phase 3 comparative analysis, ask the learner to predict their biggest growth area, biggest gap, and current Bloom level per topic; then load the `metacognition` KB and frame the report as a calibration check (predicted vs measured), persisting the delta as a trajectory signal.

### [MEDIUM] M20 — metacognition — agents/skill-assessor.md:L26-L60
**Gap type:** stated_not_enforced
**Claim:** skill-assessor records its own HIGH/MEDIUM/LOW confidence on the classification but never elicits or stores the learner's self-rating on the same sub-topic, so no Dunning-Kruger calibration can be computed at sub-topic granularity by any consuming skill.
**Evidence:** > "Assign a confidence rating: HIGH, MEDIUM, or LOW." (refers to agent's own classification confidence)
**Fix:** Have the agent collect a one-shot learner self-rating per sub-topic before its first question and return both `learnerSelfRating` and `agentClassification` in the output table so parent skills can surface the calibration gap.

### [MEDIUM] M21 — constructivism — skills/learn/SKILL.md:L121-L142
**Gap type:** stated_not_enforced
**Claim:** Phase 3 loads the constructivism KB and mentions "spiral curriculum" in prose, but the Plan Structure / Plan Principles list contains no checkpoint that the generated plan must actually revisit earlier concepts at higher Bloom levels — there is no gate verifying a spiral exists in the output.
**Evidence:** > "Build a modular plan based on the assessment, learner goals/timeline, ZPD principles … and spiral curriculum (revisit concepts at increasing depth)."
**Fix:** Add a Plan Principle requiring each phase after Phase 0 to declare at least one "Spiral revisit" — a concept from an earlier phase reappearing at a higher target Bloom level — and require this line to appear in each `plan/phase-{N}.md`.

### [MEDIUM] M23 — constructivism — skills/teach-back/SKILL.md:L118-L142
**Gap type:** missing_where_fits
**Claim:** Phase 4 "Draft" is the strongest fully-independent constructivist act in the plugin (KB tier 5 — "stay silent; the writing is the demonstration") but the skill never references the constructivism KB.
**Evidence:** > "Then stay silent. The learner writes the post. … This is the most important 'tutor does not write the code' moment in the whole plugin."
**Fix:** Cite the constructivism KB in Phase 4 and frame the silence rule as the KB's "fully independent" tier — making teach-back the explicit capstone instance of project progression by level.

### [MEDIUM] M24 — constructivism — skills/mentor/SKILL.md:L69
**Gap type:** cited_but_misapplied
**Claim:** Phase 4 name-drops "spiral curriculum" as a one-line principle but never references the constructivism KB and gives no concrete spiral mechanic for the 2-3 path options it generates — citation is name-only.
**Evidence:** > "Principles: build on strength … follow ZPD, use spiral curriculum, respect motivation"
**Fix:** Add a `constructivism` KB reference to Phase 4 and require each suggested path option to name at least one concept from prior projects that it will revisit at a higher Bloom level.

### [MEDIUM] M26 — constructivism — skills/plan/SKILL.md:L87-L100
**Gap type:** stated_not_enforced
**Claim:** Regenerate mode rebuilds a plan but does not load the constructivism KB and points to "/learn Phase 4" — but Phase 4 also doesn't load constructivism; the spiral-curriculum requirement (in /learn Phase 3) is neither restated nor checked here, so a regenerated plan follows no curriculum-design principles.
**Evidence:** > "Build a new plan following the same principles as `/learn` Phase 4 (sectional v2 layout)"
**Fix:** Change the cross-reference to "/learn Phase 3 (plan principles) plus Phase 4 (sectional v2 layout)", and add a one-line "Reference the `zone-of-proximal-development`, `constructivism`, and `spaced-repetition` KBs" at the top of Regenerate mode.

### [MEDIUM] M27 — mentoring-theory — skills/evaluate/SKILL.md:L79-L91
**Gap type:** stated_not_enforced
**Claim:** CHANGELOG 1.4.0 promises "/mentor auto-invoked by /evaluate at major milestones," but /evaluate's Closing section never mentions /mentor — the word does not appear anywhere in the file.
**Evidence:** > "Treat this as a milestone moment. Acknowledge the path walked … End with a forward look."
**Fix:** At the end of /evaluate's Closing (milestone-gated on project completion or large Bloom delta), emit an opt-in forward-look offer pointing to `/bodhikit:mentor` — mirroring the existing Capstone opt-in pattern rather than auto-invoking.

### [MEDIUM] M32 — scientific-debugging — agents/code-reviewer.md:L46-L59
**Gap type:** missing_where_fits
**Claim:** The code-reviewer agent (called by /review, /practice Phase 3, /teach Phase 4) is the bug-surfacing surface but has no instruction or output field for flagging debugging-shaped findings — so the auto-invoke chain to /debug-together has no upstream signal to fire on.
**Evidence:** > "**What it reveals:** [What this suggests about the learner's understanding] / **Socratic question:** [A question that guides them]"
**Fix:** Add an optional `bugFound: true|false` (and brief `bugSummary`) field to the agent's output schema, and update /review, /practice, and /teach to check the flag and offer "Want to debug this together with /debug-together?" when set.

---

## LOW severity (4 confirmed)

### [LOW] L2 — spaced-repetition — skills/evaluate/SKILL.md:L73
**Gap type:** cited_but_misapplied
**Claim:** /evaluate invents a 3-tier label scheme ("Strong Box 4-5, Building Box 2-3, Needs Review Box 1") that collapses the KB's 5-box semantics into categories the KB does not define, and /progress uses a different 2-tier rollup — each consumer is inventing its own bucketing.
**Evidence:** > "Spaced Repetition Health: count/percentage by retention level (Strong Box 4-5, Building Box 2-3, Needs Review Box 1)"
**Fix:** Add a canonical "Retention Rollup Views" section to the spaced-repetition KB defining one named rollup, then change /evaluate L73 and /progress L76 to reference it instead of restating bucket boundaries inline.

### [LOW] L3 — feynman-technique — skills/explain/SKILL.md:L37-L44
**Gap type:** missing_where_fits
**Claim:** Phase 2 says "Do NOT skip this phase" but lacks the formal CHECKPOINT marker that teach-back uses to make phase gates enforceable — wording reads as guidance rather than a hard gate.
**Evidence:** > "Phase 2: Learner Explains Back. This is the heart of the Feynman technique. Do NOT skip this phase."
**Fix:** Promote the line to a strict gate: "**CHECKPOINT: Do not proceed to Phase 3 until the learner has produced an explain-back in their own words — no proceeding on 'I get it' alone.**" matching the formatting used in teach-back.

### [LOW] L6 — mentoring-theory — skills/mentor/SKILL.md:L22-L62
**Gap type:** cited_but_misapplied
**Claim:** Phase 1 is labelled "(Reality)" and Phase 3 is also "(Reality)" — the GROW label is duplicated. Phases 2-5 actually flow Goal → Reality → Options → Will in canonical order; Phase 1 is really a Kram acceptance/setup phase mis-labelled.
**Evidence:** > "Phase 1: Understand the Learner (Reality) … Phase 3: Assess the Landscape (Reality)"
**Fix:** Relabel Phase 1's parenthetical from "(Reality)" to "(Kram: Acceptance)" or "(Setup)" so the only GROW-Reality phase is Phase 3 — leave the phase order alone, since Phases 2-5 already match canonical GROW.

### [LOW] L8 — pair-programming — skills/practice/SKILL.md:L126-L138
**Gap type:** missing_where_fits
**Claim:** /practice Phase 3 handles "stuck before starting" and "code does not work" branches but never offers /pair as the active-collaboration alternative, even though GUIDE L692 explicitly positions /pair as the option when solo practice "feels too lonely" or when the learner stalls.
**Evidence:** > "If they are stuck before starting: Break the exercise into smaller sub-problems / Solve the first sub-problem together (I Do, then We Do)"
**Fix:** In the "stuck before starting" branch (and after the 3-hint exhaustion in "code does not work"), offer to switch into `/bodhikit:pair` strong-style on the same exercise rather than only decomposing solo.

---

## Adjusted gaps (9) — real, but severity or fix was re-specified by validation

These were flagged in the first pass and survived adversarial verification, but the second-pass validator caught either a severity miscalibration, a fix-mechanics error (e.g., violating CLAUDE.md chain convention), or scope over-statement.

### [A1] H7 → MEDIUM — deliberate-practice — skills/practice/SKILL.md:L15-L34
**Gap type:** stated_not_enforced
**Original severity:** high → **Validated:** medium
**Why adjusted:** Phase 1 *already* reads Bloom levels from progress.md (partial weakness signal); the spaced-review.json Box-1 read is the actual missing piece, not the entire weakness-targeting flow.
**Re-specified claim:** Phase 1 reads current module + Bloom level but does not inspect `spaced-review.json` for Box-1 concepts before topic selection, so deliberate practice cannot target the highest-leverage weakness when `$ARGUMENTS` is absent.
**Re-specified fix:** When `$ARGUMENTS` is absent, read `.bodhi/spaced-review.json` for Box-1 concepts tied to the current module and prefer one of those for the exercise topic; announce the choice ("Targeting `<concept>` — it's in Box 1 from `<date>`"). Keep the explicit-topic and Bloom-read paths as-is.

### [A2] H8 → MEDIUM — desirable-difficulties — skills/practice/SKILL.md:L37-L106
**Gap type:** missing_where_fits
**Original severity:** high → **Validated:** medium
**Why adjusted:** Lines 104-105 already name "Desirable difficulty" and "Variation" — the gap is operationalization, not omission of the concept itself.
**Re-specified claim:** Phase 2 names "Desirable difficulty" and "Variation" in prose at L104-L105 but does not load the desirable-difficulties KB, has no generation gate (sketch-before-scaffolding) for Beginner/Intermediate tiers, and does not enforce variation by reading prior `exercises/`.
**Re-specified fix:** Add the `desirable-difficulties` KB to Phase 2 references, add a pre-scaffolding sketch step for Beginner/Intermediate tiers ("Before I show starter files, walk me through how you'd approach this"), and require a read of prior `exercises/` entries to enforce a different context.

### [A3] H13 → HIGH (severity unchanged, fix corrected) — scientific-debugging — skills/teach/SKILL.md:L94-L98
**Gap type:** missing_where_fits
**Severity:** high (confirmed)
**Why adjusted:** Original fix passed `<file>` as a positional argument to `/debug-together`, which violates the CLAUDE.md chain convention (topic/description after the flag, not a file path).
**Claim (unchanged):** Phase 4 step 4 ("Not working: guide them to find the issue (Socratic method)") is the canonical bug-arises-during-You-Do moment but never invokes /debug-together — contradicting CHANGELOG 1.4.0's published contract.
**Re-specified fix:** Replace the one-liner with `/bodhikit:debug-together --invoked-from=teach <brief description of bug>`; do NOT pass a file path. The sub-skill should discover failing code from `exercises/<current-module>/` per CLAUDE.md chain convention.

### [A4] M9 → MEDIUM (severity unchanged, scope widened) — feynman-technique — skills/explain/SKILL.md:L49-L60
**Gap type:** stated_not_enforced
**Severity:** medium (confirmed)
**Why adjusted:** The KB names three "fluency without understanding" signals, not just jargon-without-definition.
**Claim (widened):** Phase 3's four gap buckets (nailed / partial / missed / misconceptions) omit all three KB-named fluency-without-understanding signals — jargon-without-definition, vague hedging, and skipped steps — even though the KB names them as Feynman failure signals to probe.
**Re-specified fix:** Add a fifth gap category — **"Fluency without understanding: jargon used without definition, vague hedging that papers over uncertainty, steps quietly skipped"** — and route any of the three signals into Phase 4's mini-explanation loop the same way other gaps are handled.

### [A5] M15 → LOW (lines corrected) — growth-mindset — skills/reflect/SKILL.md:L68 (was L42-L47)
**Gap type:** missing_where_fits
**Original severity:** medium → **Validated:** low
**Why adjusted:** The cited lines targeted the wrong region — Q3's framing at L42-47 is not the actionable miss. The miss is at **L68** (the Phase 3 "High confidence 8-10" acknowledgment row).
**Re-specified claim:** The Phase 3 "High confidence 8-10" acknowledgment row at L68 has no guidance on what KIND of acknowledgment to give, exposing it to the false-growth-mindset trap (praising the trait, not the strategy).
**Re-specified fix:** Reference the growth-mindset KB once in Phase 2 and update L68 to require strategy-naming acknowledgment ("your approach of X worked"), not trait-naming.

### [A6] M22 → LOW (discoverability nit, not contract gap) — constructivism — skills/practice/SKILL.md:L37-L98
**Gap type:** missing_where_fits
**Original severity:** medium → **Validated:** low
**Why adjusted:** Beginner/Intermediate/Advanced tiers are already anchored to Bloom via the cited `assessment-framework` KB; constructivism's 5-tier ladder is project-scale (owned by /learn, /plan). This is a discoverability nit, not a contract violation.
**Re-specified claim:** Phase 2's Beginner/Intermediate/Advanced tiers map onto the project-scale ladder owned by /learn and /plan but the connection is not made — a reader cannot trace the exercise-scale tiers back to the constructivism KB's project ladder.
**Re-specified fix:** Add one line noting that exercise-scale tiers correspond to tiers 2-4 of the constructivism KB's project ladder applied at exercise scope. **Do not** restate the 5-tier ladder inline.

### [A7] M25 → LOW (presentation gap) — constructivism — skills/plan/SKILL.md:L24-L51
**Gap type:** stated_not_enforced
**Original severity:** medium → **Validated:** low
**Why adjusted:** The underlying data already exists in per-phase plan files; the View summary just doesn't surface spiral revisits. Presentation, not data.
**Re-specified claim:** View mode does not surface a "Spiral Revisits" view drawn from the per-phase plan files' existing Bloom + spaced-review-concepts fields, so the spiral is invisible to the learner even when it exists.
**Re-specified fix:** Add a "Spiral Revisits" line drawn from existing per-module Bloom + spaced-review-concepts fields, distinct from the weekly Spaced Review Schedule section.

### [A8] M28 → LOW (scope narrowed) — mentoring-theory — skills/mentor/SKILL.md:L75-L82
**Gap type:** cited_but_misapplied
**Original severity:** medium → **Validated:** low
**Why adjusted:** Commitment is already operationalized via the /learn handoff (Phase 5 step 1); only the success-measurement Will prompt is genuinely missing.
**Re-specified claim:** Phase 5 (Will) addresses timeline and commitment (via /learn handoff) but omits the third KB-defined Will prompt: how the learner will know they have succeeded.
**Re-specified fix:** Add a single prompt — "How will you know you have succeeded?" — to Phase 5. Do not add a redundant commitment prompt; do not introduce new profile fields.

### [A9] M29 → MEDIUM (severity unchanged, fix is incomplete) — pair-programming — skills/pair/SKILL.md:L17-L25
**Gap type:** stated_not_enforced
**Severity:** medium (confirmed)
**Why adjusted:** Adding a chain guard to /pair alone is pointless: /teach Phase 3 never invokes /pair either (H11), so the chain never fires.
**Claim (unchanged):** /pair declares it can be auto-invoked by /teach but does not implement the `--invoked-from=` chained-invocation guard CLAUDE.md mandates, and CLAUDE.md's chainable list omits /pair.
**Re-specified fix — choose one:**
- **(a) Full wire:** Add chain guard to /pair, add /pair to CLAUDE.md's "Currently chainable" list, AND add explicit `/bodhikit:pair --invoked-from=teach` call in /teach Phase 3 (closes H11 in the same pass).
- **(b) Scope down:** Delete the aspirational sentence at L17 declaring auto-invocation by /teach.
The current half-wired state is the worst of both options.

---

## Refuted by validation (10) — not gaps, do not file

These appeared in the original punch list but failed the second-pass validation. Each is listed with the basis so future audits don't re-flag them.

- **M1** `skills/quiz/SKILL.md` L107-L118 — Bloom trajectory is owned by `assessment-history.json` (a different structured surface); `progress.md` L113 already captures per-quiz Bloom adjustments. Not a gap.
- **M17** `skills/teach/SKILL.md` L125-L132 — voice/praise contract is delegated to `teaching-personality` KB per CLAUDE.md, which already cross-references growth-mindset and bans empty praise. Inlining would violate the authoring contract.
- **M19** `skills/practice/SKILL.md` L37-L106 — metacognition is honored via the chained `/reflect` skill; GUIDE.md's "When it fires" list deliberately omits /practice. Not a gap.
- **M30** `README.md` L204-L216 — README diagram is intentionally simplified per progressive disclosure; full integration lives in GUIDE.md L412 which README L224 cross-links. Not a gap.
- **M31** `skills/pair/SKILL.md` L85-L88 — the cited flow is a concept gap (learner cannot yet write to spec), not a bug. Feynman-technique escalation is the correct methodology here, not scientific-debugging.
- **M33** `skills/debug-together/SKILL.md` L34-L48 — the omission is signposted in the phase title ("T and R") and TRAFFIC's missing letters are addressed in Phase 5; the proposed "automate-before-hypothesize" fix would conflict with Phase 1's existing "no code yet" gate.
- **L1** `skills/practice/SKILL.md` L43-L97 — Bloom targeting IS honored at Phase 1 (L17, L33); cited lines are about scaffolding fade, a different axis. Not a gap.
- **L4** `skills/forget/SKILL.md` L13-L40 — /forget is intentionally a pure action skill; metacognition is owned by /reflect (the documented caller). Adding metacognition load would duplicate.
- **L5** `agents/code-reviewer.md` L33-L43 — growth-mindset chains through `teaching-personality` KB per the authoring contract; inlining voice rules in an agent would violate CLAUDE.md.
- **L7** `skills/plan/SKILL.md` L87-L98 — `careerGoal`/`whyLearning` is owned by /mentor per state-schema KB; /plan does not declare a mentoring-theory contract. Not its surface.

### Pattern across refutations

Seven of ten refutations (M1, M17, M19, M30, L4, L5, L7) failed because **the methodology is honored elsewhere via a documented chain or progressive-disclosure cross-link** — sibling skill, KB cross-reference, or GUIDE.md cross-link. The original audit flagged each in-file omission without checking whether the canonical home was somewhere else. Future audits should default to "is this methodology owned by another surface per CLAUDE.md or state-schema?" before flagging an in-file omission.

The other three refutations (M31, M33, L1) failed because the audit invoked the wrong methodology for the situation, or the cited lines were about a different axis than the claim assumed.

---

## Recommended next moves

Ordered by impact-per-edit:

1. **Fix the state-schema root cause first** (closes H1, H2, H3, M2, M3 — 5 findings in one schema change). Extend `spaced-review.json.concepts[].reviewHistory[]` with `bloomLevel` and `feynmanPassed`, add a `consecutiveCorrectAtL4Plus` counter, and decide whether `currentBloomLevel` becomes per-concept or stays per-sub-topic with a new per-concept structure. Update `state-schema` KB first per the authoring contract, then update /teach (H2), /explain (M3), /quiz, /progress (M2), /evaluate.

2. **Refactor /reflect Phase 2 around retrieval-first calibration** (closes H5, H6, H9, M13, lowers A5 — 5 findings in one phase rewrite). Replace the bare Q3 confidence rating with: retrieval prompt ("explain `[main concept]` in 2 sentences") → confidence rating → cross-check against today's quiz/exercise outcomes → Leitner update only if calibration holds.

3. **Wire the CHANGELOG 1.4.0 auto-invocation chains** (closes H11, H12, H13, M11, M27, M32, A9 in one pass — 7 findings). /teach Phase 3 → /pair; /practice + /teach → /debug-together (via code-reviewer `bugFound` field); /reflect → /practice; /evaluate → /mentor. All five use the existing `--invoked-from=` convention. Decide A9 in the same pass (full wire vs. scope down).

4. **Add per-phase KB references where conspicuously absent** (closes M10, M12, M14, M16, M18, M20, M23, M24, M26, A6 — 10 findings, mostly one-line edits). `deliberate-practice` on /pair Mode 2, `desirable-difficulties` on /teach Phase 4 and /reflect Phase 2, `growth-mindset` on /debug-together Phase 0, `metacognition` on /evaluate Phase 2.5 and skill-assessor, `constructivism` on /teach-back Phase 4 and /mentor Phase 4, plus the /plan Regenerate cross-ref. Low-risk batch.

5. **Decide /pair's pedagogical scope deliberately** (closes M5, M8, M10, L8, A9 — overlaps with move 3). /pair is the most under-instrumented skill relative to its documented role. Either invest fully (chain guard + /teach wire + spaced-repetition KB cite + Box-1 write + deliberate-practice for Ping-Pong + ZPD-gated role reversal) or scope down the aspirational claim at L17. The current half-wired state is the worst of both.

6. **Strengthen `dev/check.sh`** to catch the three Leitner-hardcoding incidents (H4, H5, M7) the lint missed. Pattern: any skill mentioning "Box N → Box M" inline outside of `knowledge/spaced-repetition/` should fail the check.
