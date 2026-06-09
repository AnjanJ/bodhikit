#!/usr/bin/env bash
# dev/check.sh — bodhikit authoring-contract lint
#
# Verifies the contract documented in CLAUDE.md. Bash, no deps.
# Exit 0 = clean. Exit 1 = hard violations.
#
# Single severity since 1.10.5 (sprint M6 close — gaps_of_pedagogy.md):
#   err  — hard fail (exit 1). Schema drift, missing required pieces.
#
# Historical note: 1.7.0 introduced soft warnings for the
# progressive-disclosure contract; the pedagogy-audit sprint
# (1.10.0 → 1.10.5) closed every flagged finding, and 1.10.5
# promoted every warn to err. The warn() helper is kept for any
# future intentionally-soft check, but no current rule uses it.

set -u
cd "$(dirname "$0")/.." || exit 2

fail=0
warn_count=0
note() { printf '  %s\n' "$1"; }
err() { printf 'FAIL: %s\n' "$1"; fail=1; }
warn() { printf 'WARN: %s\n' "$1"; warn_count=$((warn_count + 1)); }
ok() { printf 'OK:   %s\n' "$1"; }

# ---------------------------------------------------------------------------
# 1. Manifests exist and versions agree
# ---------------------------------------------------------------------------
plugin_v=$(grep -E '"version"' .claude-plugin/plugin.json | head -1 | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')
mp_top_v=$(grep -E '"version"' .claude-plugin/marketplace.json | sed -n '1p' | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')
mp_plugin_v=$(grep -E '"version"' .claude-plugin/marketplace.json | sed -n '2p' | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')

if [ -z "$plugin_v" ]; then
  err "plugin.json missing version"
elif [ "$plugin_v" != "$mp_top_v" ] || [ "$plugin_v" != "$mp_plugin_v" ]; then
  err "version drift: plugin.json=$plugin_v marketplace.metadata=$mp_top_v marketplace.plugins[0]=$mp_plugin_v"
else
  ok "version consistent ($plugin_v)"
fi

# ---------------------------------------------------------------------------
# 2. Skill frontmatter contract
# ---------------------------------------------------------------------------
for f in skills/*/SKILL.md; do
  if ! head -10 "$f" | grep -q '^description:'; then
    err "$f missing 'description:' in frontmatter"
  fi
  if ! head -10 "$f" | grep -q '^user-invocable: true'; then
    err "$f missing 'user-invocable: true'"
  fi
  if ! grep -q 'teaching-personality' "$f"; then
    err "$f does not reference teaching-personality KB"
  fi
done

# ---------------------------------------------------------------------------
# 3. Agent-using skills must include mandate phrase and Fallback
# ---------------------------------------------------------------------------
for f in skills/*/SKILL.md; do
  if grep -q 'Agent tool' "$f"; then
    if ! grep -q 'You MUST use the Agent tool' "$f"; then
      err "$f uses an Agent but lacks the literal mandate phrase"
    fi
    if ! grep -qi '\*\*Fallback' "$f"; then
      err "$f uses an Agent but has no **Fallback:** paragraph"
    fi
  fi
done

# ---------------------------------------------------------------------------
# 4. Files that touch tracking shapes must reference state-schema
# ---------------------------------------------------------------------------
for f in skills/*/SKILL.md agents/*.md rules/*.md; do
  # state-schema KB itself is allowed to redeclare shapes
  case "$f" in *state-schema*) continue;; esac
  if grep -qE 'state\.json|spaced-review\.json|progress\.md|bodhi-profile' "$f"; then
    if ! grep -q 'state-schema' "$f"; then
      err "$f touches tracking files but does not reference state-schema KB"
    fi
  fi
done

# ---------------------------------------------------------------------------
# 5. Files that touch Leitner boxes must reference spaced-repetition KB
# ---------------------------------------------------------------------------
for f in skills/*/SKILL.md agents/*.md rules/*.md; do
  case "$f" in *spaced-repetition*) continue;; esac
  if grep -qE 'Box [0-9]|Leitner' "$f"; then
    if ! grep -q 'spaced-repetition' "$f"; then
      err "$f mentions Leitner/boxes but does not reference spaced-repetition KB"
    fi
  fi
done

# ---------------------------------------------------------------------------
# 6. Voice rules MUST NOT be restated outside teaching-personality KB
# ---------------------------------------------------------------------------
for f in skills/*/SKILL.md agents/*.md rules/*.md; do
  # The personality KB itself is the canonical home; rule file is the path-scoped trigger
  # and may carry a one-line directive. Everywhere else, restating is drift.
  case "$f" in *teaching-personality*) continue;; esac
  if grep -qE 'Oogway.*Yoda.*Buddha|Buddha.*Ambedkar.*Oogway|Yoda.*Buddha.*Ambedkar' "$f"; then
    err "$f restates the personality list inline — reference the KB instead"
  fi
done

# ---------------------------------------------------------------------------
# 7. Agent frontmatter contract
# ---------------------------------------------------------------------------
for f in agents/*.md; do
  if ! head -10 "$f" | grep -q '^name:'; then
    err "$f missing 'name:' in frontmatter"
  fi
  if ! head -10 "$f" | grep -qE '^model: (sonnet|haiku|opus)'; then
    err "$f missing or invalid 'model:'"
  fi
  if ! head -15 "$f" | grep -q 'disallowedTools'; then
    err "$f missing disallowedTools (agents should be read-only)"
  fi
done

# ---------------------------------------------------------------------------
# 8. KB frontmatter contract
# ---------------------------------------------------------------------------
for f in knowledge/*/SKILL.md; do
  if ! head -10 "$f" | grep -q '^user-invocable: false'; then
    err "$f must declare 'user-invocable: false'"
  fi
done

# ---------------------------------------------------------------------------
# 9. Chainable skills must handle --invoked-from=
# ---------------------------------------------------------------------------
chainable="teach practice reflect status quiz forget pair debug-together mentor"
for s in $chainable; do
  f="skills/$s/SKILL.md"
  if [ ! -f "$f" ]; then continue; fi
  if ! grep -q 'invoked-from' "$f"; then
    err "$f is in the chainable set but does not mention --invoked-from="
  fi
done

# ---------------------------------------------------------------------------
# 10. /continue must pass --invoked-from=continue to every chained sub-skill
# ---------------------------------------------------------------------------
if [ -f skills/continue/SKILL.md ]; then
  for sub in status teach practice reflect; do
    if grep -qE "Auto-invoke .\/${sub}\b" skills/continue/SKILL.md; then
      if ! grep -qE "\/${sub}([[:space:]]|--)[^\`]*--invoked-from=continue" skills/continue/SKILL.md; then
        err "skills/continue/SKILL.md auto-invokes /$sub but without --invoked-from=continue"
      fi
    fi
  done
fi

# ---------------------------------------------------------------------------
# 11. README skill count sanity (best-effort)
# ---------------------------------------------------------------------------
declared=$(grep -oE 'Skills \([0-9]+\)' README.md | head -1 | grep -oE '[0-9]+')
actual=$(find skills -name SKILL.md | wc -l | tr -d ' ')
if [ -n "$declared" ] && [ "$declared" != "$actual" ]; then
  err "README says Skills ($declared) but $actual SKILL.md files exist under skills/"
fi

# ---------------------------------------------------------------------------
# 12. v2 schema: no writes to lastSessionSummary or bloomResetNote outside
#     the v1-boundary skills (/housekeep, /status).
# ---------------------------------------------------------------------------
# These fields were removed from state.json in v2. The only legitimate
# references are inside skills that straddle the v1↔v2 boundary by design:
# /housekeep migrates them; /status all detects them as a health flag.
# Everywhere else, mentioning these fields is drift.
# Applies to skills AND agents — both can touch tracking files.
for f in skills/*/SKILL.md agents/*.md; do
  case "$f" in *housekeep*|*status*) continue;; esac
  while IFS= read -r line; do
    case "$line" in
      *"Do NOT write"*|*"do not write"*|*"removed in v2"*|*"v2 — narrative"*) continue;;
    esac
    case "$line" in
      *lastSessionSummary*|*bloomResetNote*)
        err "$f writes v1 narrative field — line: $(printf '%s' "$line" | head -c 80)..."
        ;;
    esac
  done < "$f"
done

# ---------------------------------------------------------------------------
# 13. v2 schema: no reads of v1 paths outside v1-boundary skills.
# ---------------------------------------------------------------------------
# assessment.md (singular, root of .bodhi/) and plan.md (root of .bodhi/) are
# v1 paths. v2 uses assessments/latest.md and plan/README.md + plan/phase-*.md.
# /housekeep references both during migration; /status all references them
# as legacy-layout health flags. Everywhere else is drift.
# Applies to skills AND agents.
for f in skills/*/SKILL.md agents/*.md; do
  case "$f" in *housekeep*|*status*) continue;; esac
  # Match `.bodhi/assessment.md` (NOT `.bodhi/assessments/...`) and
  # `.bodhi/plan.md` (NOT `.bodhi/plan/...`).
  if grep -qE '\.bodhi/assessment\.md([^/s]|$)' "$f"; then
    err "$f references v1 path .bodhi/assessment.md — should be .bodhi/assessments/latest.md"
  fi
  if grep -qE '\.bodhi/plan\.md([^/]|$)' "$f"; then
    err "$f references v1 path .bodhi/plan.md — should be .bodhi/plan/README.md or plan/phase-*.md"
  fi
done

# ---------------------------------------------------------------------------
# 14. Progressive disclosure: KBs referenced top-of-file should be in
#     teaching-personality + state-schema only. Methodology KBs belong
#     inside the phase that uses them.
# ---------------------------------------------------------------------------
# Reads the body lines 1-25 after frontmatter (the "load directive" zone
# Claude Code sees before phase content). Any backticked KB name there that
# isn't teaching-personality or state-schema → soft warn.
#
# Skips: /housekeep (legitimate conditional load of state-migration).
kb_names=$(find knowledge -mindepth 1 -maxdepth 1 -type d -exec basename {} \;)
for f in skills/*/SKILL.md; do
  case "$f" in *housekeep*) continue;; esac
  top=$(awk 'BEGIN{n=0} /^---$/{n++; next} n>=2 || (n==1 && NR>1) {print}' "$f" | head -8)
  for kb in $kb_names; do
    case "$kb" in
      teaching-personality|state-schema|read-defaults|state-migration) continue;;
    esac
    if printf '%s' "$top" | grep -qE "\`$kb\`"; then
      err "$f loads \`$kb\` top-of-file (lines 1-8) — consider moving into the phase that uses it"
    fi
  done
done

# ---------------------------------------------------------------------------
# 15. docs/example-project must use v2 layout
# ---------------------------------------------------------------------------
# v1 example will mislead contributors / users who pattern-match on it.
if [ -d docs/example-project/.bodhi ]; then
  if [ -f docs/example-project/.bodhi/plan.md ]; then
    err "docs/example-project/.bodhi/plan.md is v1 layout — should be plan/README.md + plan/phase-*.md"
  fi
  if [ -f docs/example-project/.bodhi/assessment.md ]; then
    err "docs/example-project/.bodhi/assessment.md is v1 layout — should be assessments/latest.md"
  fi
  # state.json should not carry lastSessionSummary or bloomResetNote in v2 example
  state_file=docs/example-project/.bodhi/state.json
  if [ -f "$state_file" ]; then
    if grep -qE '"(lastSessionSummary|bloomResetNote)"' "$state_file"; then
      err "$state_file carries v1 narrative fields — strip and move to progress.md"
    fi
    if ! grep -qE '"version":[[:space:]]*2' "$state_file"; then
      err "$state_file is not declared as version 2"
    fi
  fi
fi

# The profile in docs/example-project must use the split v2 layout
profile_file=docs/example-project/.bodhi-profile.json
projects_file=docs/example-project/.bodhi-profile.projects.json
if [ -f "$profile_file" ]; then
  # v2 = profile is split. activeProjects / completedProjects must live in projects file, not profile.
  if grep -qE '"(activeProjects|completedProjects)"' "$profile_file"; then
    err "$profile_file carries activeProjects/completedProjects inline — should be in $projects_file (v2 split layout)"
  fi
  if ! grep -qE '"version":[[:space:]]*2' "$profile_file"; then
    err "$profile_file is not declared as version 2"
  fi
  if [ ! -f "$projects_file" ]; then
    err "$projects_file is missing — v2 split profile requires this file"
  elif ! grep -qE '"version":[[:space:]]*2' "$projects_file"; then
    err "$projects_file is not declared as version 2 (cohort-consistent with parent profile)"
  fi
fi

# ---------------------------------------------------------------------------
# 16. v3 spaced-review schema: writers must mention new per-concept fields.
# ---------------------------------------------------------------------------
# Skills that write to spaced-review.json after 1.10.0 MUST mention at least one
# of the new v3 per-concept fields (bloomLevel, feynmanPassed,
# consecutiveCorrectAtL4Plus). Catches regressions where a skill silently strips
# the new fields by writing only the v2 shape. Warn for now; promotes to err in M6.
#
# Heuristic: a skill is a "writer" if it both references spaced-review.json AND
# mentions either "Update tracking", "Apply the spaced-repetition KB", or
# explicit append/update verbs near the file. Limit checks to the skills the
# sprint actually wired (quiz, teach, explain, practice, forget, pair).
for s in quiz teach explain practice forget pair; do
  f="skills/$s/SKILL.md"
  if [ ! -f "$f" ]; then continue; fi
  if grep -q 'spaced-review\.json' "$f"; then
    if ! grep -qE 'bloomLevel|feynmanPassed|consecutiveCorrectAtL4Plus' "$f"; then
      err "$f writes spaced-review.json but does not mention any v3 per-concept field (bloomLevel/feynmanPassed/consecutiveCorrectAtL4Plus)"
    fi
  fi
done

# ---------------------------------------------------------------------------
# 17. /teach Phase 1 must mention the prerequisite Bloom gate.
# ---------------------------------------------------------------------------
# H3 fix from the 1.10.0 audit — Bloom advancement is contractual now.
if [ -f skills/teach/SKILL.md ]; then
  if ! grep -qiE 'prerequisite.*(bloom|gate)|(bloom|gate).*prerequisite' skills/teach/SKILL.md; then
    err "skills/teach/SKILL.md missing the prerequisite Bloom gate language (H3 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 18. /progress must mention the canonical mastery formula or the legacy
#     fallthrough display rule.
# ---------------------------------------------------------------------------
# M2 (audit) + H1 fix — Mastery % can no longer be fabricated. Either the
# formula is cited inline (referencing the state-schema KB) or the column
# explicitly handles the legacy display fallthrough.
if [ -f skills/progress/SKILL.md ]; then
  if ! grep -qE 'mastered === true|Mastery % formula|consecutiveCorrectAtL4Plus' skills/progress/SKILL.md; then
    err "skills/progress/SKILL.md missing the canonical mastery formula or fallthrough rule (H1/M2 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 19. /reflect Phase 2 must reference metacognition KB.
# ---------------------------------------------------------------------------
# H5/H6/H9 fix — the retrieval-first calibration loop is grounded in the
# metacognition KB's Dunning-Kruger calibration rule. Reference must be in
# Phase 2 (where the rule applies), not buried elsewhere in the file.
if [ -f skills/reflect/SKILL.md ]; then
  if ! awk '/^## Phase 2/,/^## Phase 3/' skills/reflect/SKILL.md | grep -q 'metacognition'; then
    err "skills/reflect/SKILL.md Phase 2 does not reference metacognition KB (H5/H6/H9 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 20. /reflect Phase 2 must reference feynman-technique KB.
# ---------------------------------------------------------------------------
# The fluency-without-understanding signals (jargon, hedging, skipped steps)
# are the gate that catches Dunning-Kruger overconfidence at the explain-back.
if [ -f skills/reflect/SKILL.md ]; then
  if ! awk '/^## Phase 2/,/^## Phase 3/' skills/reflect/SKILL.md | grep -q 'feynman-technique'; then
    err "skills/reflect/SKILL.md Phase 2 does not reference feynman-technique KB (H6 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 21. /reflect Phase 3 must reference growth-mindset KB and deliberate-practice KB.
# ---------------------------------------------------------------------------
# A5 fix — strategy-naming acknowledgment per Dweck's false-effort nuance.
# M11 fix — the reflect→practice deliberate-practice handoff at weak signals.
if [ -f skills/reflect/SKILL.md ]; then
  phase3=$(awk '/^## Phase 3/,/^## Phase 4/' skills/reflect/SKILL.md)
  if ! printf '%s' "$phase3" | grep -q 'growth-mindset'; then
    err "skills/reflect/SKILL.md Phase 3 does not reference growth-mindset KB (A5 fix)"
  fi
  if ! printf '%s' "$phase3" | grep -q 'deliberate-practice'; then
    err "skills/reflect/SKILL.md Phase 3 does not reference deliberate-practice KB (M11 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 22. /teach Phase 3 must offer /pair (H11 + A9 fix, opt-in pattern).
# ---------------------------------------------------------------------------
# CHANGELOG 1.4.0 promised /teach -> /pair; 1.10.2 wires it as an offer per the
# sprint's chain-shape decision. Check that Phase 3 mentions the offer with the
# --invoked-from=teach chain flag.
if [ -f skills/teach/SKILL.md ]; then
  phase3=$(awk '/^## Phase 3/,/^## Phase 4/' skills/teach/SKILL.md)
  if ! printf '%s' "$phase3" | grep -qE 'bodhikit:pair.*invoked-from=teach'; then
    err "skills/teach/SKILL.md Phase 3 does not offer /pair with --invoked-from=teach (H11/A9 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 23. /practice Phase 3 must offer /debug-together (H12 fix).
# ---------------------------------------------------------------------------
if [ -f skills/practice/SKILL.md ]; then
  phase3=$(awk '/^## Phase 3/,/^## Phase 4|^---/' skills/practice/SKILL.md)
  if ! printf '%s' "$phase3" | grep -qE 'bodhikit:debug-together.*invoked-from=practice'; then
    err "skills/practice/SKILL.md Phase 3 does not offer /debug-together with --invoked-from=practice (H12 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 24. /teach Phase 4 must offer /debug-together (H13/A3 fix).
# ---------------------------------------------------------------------------
if [ -f skills/teach/SKILL.md ]; then
  phase4=$(awk '/^## Phase 4/,/^## Phase 5/' skills/teach/SKILL.md)
  if ! printf '%s' "$phase4" | grep -qE 'bodhikit:debug-together.*invoked-from=teach'; then
    err "skills/teach/SKILL.md Phase 4 does not offer /debug-together with --invoked-from=teach (H13/A3 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 25. /evaluate Closing must offer /mentor at project completion (M27 fix).
# ---------------------------------------------------------------------------
# Offer-only — auto-invoke is explicitly out of scope per the sprint decision.
if [ -f skills/evaluate/SKILL.md ]; then
  if ! grep -qE 'bodhikit:mentor' skills/evaluate/SKILL.md; then
    err "skills/evaluate/SKILL.md does not mention /bodhikit:mentor (M27 fix — opt-in offer at completion/milestone)"
  fi
fi

# ---------------------------------------------------------------------------
# 26. Newly chainable skills (pair, debug-together, mentor) must declare
#     the offer-only nature in their opening lines (consistency with the
#     CHANGELOG 1.4.0 contract reset and the Capstone offer pattern).
# ---------------------------------------------------------------------------
# Looking for the literal "Offered" word OR the chain-guard sentence — either
# proves the skill knows it is opted into rather than auto-fired.
for s in pair debug-together mentor; do
  f="skills/$s/SKILL.md"
  if [ ! -f "$f" ]; then continue; fi
  head30=$(head -30 "$f")
  if ! printf '%s' "$head30" | grep -qiE 'offer|opt-in|chained invocation'; then
    err "$f opening 30 lines do not declare offer/opt-in/chained-invocation framing"
  fi
done

# ---------------------------------------------------------------------------
# 28. /pair Mode 2 must reference deliberate-practice KB (M10 fix).
# ---------------------------------------------------------------------------
# Ping-Pong is a textbook deliberate-practice loop; citing the KB makes
# edge-of-ability targeting and per-round variation enforceable.
if [ -f skills/pair/SKILL.md ]; then
  mode2=$(awk '/^## Mode 2/,/^## Mode 3/' skills/pair/SKILL.md)
  if ! printf '%s' "$mode2" | grep -q 'deliberate-practice'; then
    err "skills/pair/SKILL.md Mode 2 does not reference deliberate-practice KB (M10 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 29. /teach Phase 4 must reference desirable-difficulties KB (M12 fix).
# ---------------------------------------------------------------------------
if [ -f skills/teach/SKILL.md ]; then
  phase4=$(awk '/^## Phase 4/,/^## Phase 5/' skills/teach/SKILL.md)
  if ! printf '%s' "$phase4" | grep -q 'desirable-difficulties'; then
    err "skills/teach/SKILL.md Phase 4 does not reference desirable-difficulties KB (M12 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 30. /debug-together Phase 0 must reference growth-mindset KB (M16 fix).
# ---------------------------------------------------------------------------
if [ -f skills/debug-together/SKILL.md ]; then
  phase0=$(awk '/^## Phase 0/,/^## Phase 1/' skills/debug-together/SKILL.md)
  if ! printf '%s' "$phase0" | grep -q 'growth-mindset'; then
    err "skills/debug-together/SKILL.md Phase 0 does not reference growth-mindset KB (M16 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 31. /evaluate must reference metacognition KB and have a Phase 2.5 prediction step (M18 fix).
# ---------------------------------------------------------------------------
if [ -f skills/evaluate/SKILL.md ]; then
  if ! grep -q 'metacognition' skills/evaluate/SKILL.md; then
    err "skills/evaluate/SKILL.md does not reference metacognition KB (M18 fix)"
  fi
  if ! grep -qE '## Phase 2\.5|Predict Your Trajectory' skills/evaluate/SKILL.md; then
    err "skills/evaluate/SKILL.md missing Phase 2.5 prediction step (M18 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 32. /teach-back, /mentor, /plan must reference constructivism KB
#     (M23, M24, M26 fixes).
# ---------------------------------------------------------------------------
for s in teach-back mentor plan; do
  f="skills/$s/SKILL.md"
  if [ ! -f "$f" ]; then continue; fi
  if ! grep -q 'constructivism' "$f"; then
    err "$f does not reference constructivism KB (M23/M24/M26 fix)"
  fi
done

# ---------------------------------------------------------------------------
# 33. skill-assessor agent must collect learner self-rating (M20 fix).
# ---------------------------------------------------------------------------
if [ -f agents/skill-assessor.md ]; then
  if ! grep -qiE 'self-rating|learnerSelfRating|rate yourself' agents/skill-assessor.md; then
    err "agents/skill-assessor.md does not collect learner self-rating (M20 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 34. /pair Strong-Style step 7 must be ZPD-signal-gated, not time-gated (M5 fix).
# ---------------------------------------------------------------------------
# The audit caught the hardcoded "After 10-15 minutes" rule as scaffolding-by-
# clock rather than scaffolding-by-competence. The rewrite (D5-corrected to
# observable-in-conversation signals) must mention ZPD signals explicitly.
if [ -f skills/pair/SKILL.md ]; then
  mode1=$(awk '/^## Mode 1/,/^## Mode 2/' skills/pair/SKILL.md)
  if ! printf '%s' "$mode1" | grep -qE 'ZPD|zone-of-proximal-development'; then
    err "skills/pair/SKILL.md Mode 1 does not reference ZPD for role-reversal gating (M5 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 35. /pair Session End must reference spaced-repetition KB (M8 fix).
# ---------------------------------------------------------------------------
if [ -f skills/pair/SKILL.md ]; then
  session_end=$(awk '/^## Session End/,/^## Pairing Principles/' skills/pair/SKILL.md)
  if ! printf '%s' "$session_end" | grep -q 'spaced-repetition'; then
    err "skills/pair/SKILL.md Session End does not reference spaced-repetition KB (M8 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 36. /teach Phase 4 must reference ZPD KB (M6 fix — Below-ZPD escalation gate).
# ---------------------------------------------------------------------------
if [ -f skills/teach/SKILL.md ]; then
  phase4=$(awk '/^## Phase 4/,/^## Phase 5/' skills/teach/SKILL.md)
  if ! printf '%s' "$phase4" | grep -q 'zone-of-proximal-development'; then
    err "skills/teach/SKILL.md Phase 4 does not reference zone-of-proximal-development KB (M6 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 37. /practice Phase 3 must offer /pair (L8 fix — collaboration alternative).
# ---------------------------------------------------------------------------
if [ -f skills/practice/SKILL.md ]; then
  phase3=$(awk '/^## Phase 3/,/^---$/' skills/practice/SKILL.md)
  if ! printf '%s' "$phase3" | grep -qE 'bodhikit:pair.*invoked-from=practice'; then
    err "skills/practice/SKILL.md Phase 3 does not offer /pair with --invoked-from=practice (L8 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 38. /quiz Phase 2 must reference ZPD KB (M4 fix — within-quiz signal-gated
#     escalation, not Bloom-distribution-only).
# ---------------------------------------------------------------------------
if [ -f skills/quiz/SKILL.md ]; then
  phase2=$(awk '/^## Phase 2/,/^## Phase 3/' skills/quiz/SKILL.md)
  if ! printf '%s' "$phase2" | grep -q 'zone-of-proximal-development'; then
    err "skills/quiz/SKILL.md Phase 2 does not reference zone-of-proximal-development KB (M4 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 39. /learn Phase 3 must require per-phase Spiral Revisits (M21 fix —
#     constructivism spiral-curriculum mechanic made enforceable).
# ---------------------------------------------------------------------------
if [ -f skills/learn/SKILL.md ]; then
  phase3=$(awk '/^## Phase 3/,/^## Phase 4/' skills/learn/SKILL.md)
  if ! printf '%s' "$phase3" | grep -qiE 'spiral revisit'; then
    err "skills/learn/SKILL.md Phase 3 does not declare the per-phase Spiral Revisit requirement (M21 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 41. /housekeep migrate must declare per-target idempotency markers, not a
#     single-marker exit (the 1.10.8 fix — a single .migration-1.7.0.md marker
#     would short-circuit the v2 -> v3 transform for every 1.7.0-migrated
#     project, leaving them stuck on v2 forever).
# ---------------------------------------------------------------------------
if [ -f skills/housekeep/SKILL.md ]; then
  if ! grep -q 'migration-1.10' skills/housekeep/SKILL.md; then
    err "skills/housekeep/SKILL.md missing .migration-1.10 marker (1.10.8 fix — per-target idempotency)"
  fi
  if ! grep -qiE 'per-target idempotency|per target idempotency' skills/housekeep/SKILL.md; then
    err "skills/housekeep/SKILL.md missing per-target idempotency declaration (1.10.8 fix)"
  fi
  # 1.10.9 — 5f-bis step 2 must declare in-place mutation discipline so an
  # executing model does not re-serialize from a schema template and silently
  # drop learner's non-canonical fields (precisionGap, lastResult prose, etc.).
  if ! grep -qiE 'mutate the parsed JSON object in place|in-place mutation' skills/housekeep/SKILL.md; then
    err "skills/housekeep/SKILL.md 5f-bis step 2 missing in-place mutation discipline (1.10.9 fix — prevents silent drop of non-canonical learner fields)"
  fi
  # 1.10.9 — 5f-bis step 1 verify must specify parsed-JSON equality, not
  # byte-for-byte (Write tool routinely reformats; byte-compare would
  # false-fail on healthy backups).
  if ! grep -qiE 'key-for-key equal|parsed-JSON level|parsed-JSON equality' skills/housekeep/SKILL.md; then
    err "skills/housekeep/SKILL.md 5f-bis step 1 verify missing parsed-JSON equality specification (1.10.9 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 40. Legacy fallthrough rule must NOT combine bloomLevel:0 with lastReviewed
#     (the 1.10.7 corrected boundary — pre-v3 concepts routinely have
#     populated lastReviewed; combining the two false-blocked every existing
#     learner on first migration).
# ---------------------------------------------------------------------------
# The corrected rule keys off bloomLevel: 0 alone. Any file pairing
# bloomLevel: 0 with lastReviewed === null in the SAME logical predicate
# is using the pre-1.10.7 broken rule.
for f in skills/*/SKILL.md knowledge/state-schema/SKILL.md knowledge/state-migration/SKILL.md; do
  # historical-note paragraphs are allowed to MENTION the old rule for
  # explanation. The check looks specifically for the broken predicate.
  if grep -qE 'bloomLevel.*0.*AND.*lastReviewed.*null|lastReviewed.*null.*AND.*bloomLevel.*0' "$f"; then
    # Allow if the line is inside a "Historical note" or explicitly marked as the broken/old rule
    if ! grep -B 2 -E 'bloomLevel.*0.*AND.*lastReviewed.*null|lastReviewed.*null.*AND.*bloomLevel.*0' "$f" | grep -qiE 'historical|1\.10\.0 rule|was wrong|corrected|broken'; then
      err "$f uses the pre-1.10.7 broken legacy-fallthrough predicate (bloomLevel:0 AND lastReviewed:null) — drop lastReviewed from the check"
    fi
  fi
done

# ---------------------------------------------------------------------------
echo
if [ "$warn_count" -gt 0 ]; then
  echo "$warn_count warning(s) above. (No current rule emits warns; this is a future-proofing fallback.)"
fi
if [ "$fail" -eq 0 ]; then
  echo "All hard checks passed."
  exit 0
else
  echo "Contract violations above."
  exit 1
fi
