#!/usr/bin/env bash
# dev/check.sh — bodhikit authoring-contract lint
#
# Verifies the contract documented in CLAUDE.md. Bash, no deps.
# Exit 0 = clean. Exit 1 = hard violations.
#
# Two severities:
#   err  — hard fail (exit 1). Schema drift, missing required pieces.
#   warn — soft warning (no exit code change). v1.7.0 introduced these
#          for the progressive-disclosure contract; they will be promoted
#          to err in 1.8.0 once the punch list is clean.

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
chainable="teach practice reflect status quiz forget"
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
        warn "$f writes v1 narrative field — line: $(printf '%s' "$line" | head -c 80)..."
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
    warn "$f references v1 path .bodhi/assessment.md — should be .bodhi/assessments/latest.md"
  fi
  if grep -qE '\.bodhi/plan\.md([^/]|$)' "$f"; then
    warn "$f references v1 path .bodhi/plan.md — should be .bodhi/plan/README.md or plan/phase-*.md"
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
      warn "$f loads \`$kb\` top-of-file (lines 1-8) — consider moving into the phase that uses it"
    fi
  done
done

# ---------------------------------------------------------------------------
# 15. docs/example-project must use v2 layout
# ---------------------------------------------------------------------------
# v1 example will mislead contributors / users who pattern-match on it.
if [ -d docs/example-project/.bodhi ]; then
  if [ -f docs/example-project/.bodhi/plan.md ]; then
    warn "docs/example-project/.bodhi/plan.md is v1 layout — should be plan/README.md + plan/phase-*.md"
  fi
  if [ -f docs/example-project/.bodhi/assessment.md ]; then
    warn "docs/example-project/.bodhi/assessment.md is v1 layout — should be assessments/latest.md"
  fi
  # state.json should not carry lastSessionSummary or bloomResetNote in v2 example
  state_file=docs/example-project/.bodhi/state.json
  if [ -f "$state_file" ]; then
    if grep -qE '"(lastSessionSummary|bloomResetNote)"' "$state_file"; then
      warn "$state_file carries v1 narrative fields — strip and move to progress.md"
    fi
    if ! grep -qE '"version":[[:space:]]*2' "$state_file"; then
      warn "$state_file is not declared as version 2"
    fi
  fi
fi

# The profile in docs/example-project must use the split v2 layout
profile_file=docs/example-project/.bodhi-profile.json
projects_file=docs/example-project/.bodhi-profile.projects.json
if [ -f "$profile_file" ]; then
  # v2 = profile is split. activeProjects / completedProjects must live in projects file, not profile.
  if grep -qE '"(activeProjects|completedProjects)"' "$profile_file"; then
    warn "$profile_file carries activeProjects/completedProjects inline — should be in $projects_file (v2 split layout)"
  fi
  if ! grep -qE '"version":[[:space:]]*2' "$profile_file"; then
    warn "$profile_file is not declared as version 2"
  fi
  if [ ! -f "$projects_file" ]; then
    warn "$projects_file is missing — v2 split profile requires this file"
  elif ! grep -qE '"version":[[:space:]]*2' "$projects_file"; then
    warn "$projects_file is not declared as version 2 (cohort-consistent with parent profile)"
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
      warn "$f writes spaced-review.json but does not mention any v3 per-concept field (bloomLevel/feynmanPassed/consecutiveCorrectAtL4Plus)"
    fi
  fi
done

# ---------------------------------------------------------------------------
# 17. /teach Phase 1 must mention the prerequisite Bloom gate.
# ---------------------------------------------------------------------------
# H3 fix from the 1.10.0 audit — Bloom advancement is contractual now.
if [ -f skills/teach/SKILL.md ]; then
  if ! grep -qiE 'prerequisite.*(bloom|gate)|(bloom|gate).*prerequisite' skills/teach/SKILL.md; then
    warn "skills/teach/SKILL.md missing the prerequisite Bloom gate language (H3 fix)"
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
    warn "skills/progress/SKILL.md missing the canonical mastery formula or fallthrough rule (H1/M2 fix)"
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
    warn "skills/reflect/SKILL.md Phase 2 does not reference metacognition KB (H5/H6/H9 fix)"
  fi
fi

# ---------------------------------------------------------------------------
# 20. /reflect Phase 2 must reference feynman-technique KB.
# ---------------------------------------------------------------------------
# The fluency-without-understanding signals (jargon, hedging, skipped steps)
# are the gate that catches Dunning-Kruger overconfidence at the explain-back.
if [ -f skills/reflect/SKILL.md ]; then
  if ! awk '/^## Phase 2/,/^## Phase 3/' skills/reflect/SKILL.md | grep -q 'feynman-technique'; then
    warn "skills/reflect/SKILL.md Phase 2 does not reference feynman-technique KB (H6 fix)"
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
    warn "skills/reflect/SKILL.md Phase 3 does not reference growth-mindset KB (A5 fix)"
  fi
  if ! printf '%s' "$phase3" | grep -q 'deliberate-practice'; then
    warn "skills/reflect/SKILL.md Phase 3 does not reference deliberate-practice KB (M11 fix)"
  fi
fi

# ---------------------------------------------------------------------------
echo
if [ "$warn_count" -gt 0 ]; then
  echo "$warn_count warning(s) above. v1.7.0 soft-warn; will be hard-fail in 1.10.5."
fi
if [ "$fail" -eq 0 ]; then
  echo "All hard checks passed."
  exit 0
else
  echo "Contract violations above."
  exit 1
fi
