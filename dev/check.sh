#!/usr/bin/env bash
# dev/check.sh — bodhikit authoring-contract lint
#
# Verifies the contract documented in CLAUDE.md. Bash, no deps. Exit 0 = clean.
#
# RULE-ADMISSION POLICY (1.17.0). A rule must be one of:
# STRUCTURAL — frontmatter, manifests, version sync, file existence, size
# budgets, the bodhi-state write path, chain flags, constants
# pinned between a KB and the script.
# CONDITIONAL — fires only when a file touches the thing (writes
# --tested-bloom, mentions Leitner boxes) and then demands the
# governing KB be in scope at that site.
# A rule that merely greps a KB name into a phase is not a test of anything:
# it proves a string is present, not that it is used. Behaviour is asserted in
# dev/eval/ — deterministic tests for the script, LLM evals on file state for
# the skills — never by adding a grep here.
#
# Sections: A manifests/frontmatter/budgets · B state layer · C chain
# convention · D KB single-sourcing · E behaviour pinned in prose
# (grandfathered from the 1.10.0 audit; shrink it, do not grow it).
#
# Rule numbers are stable identifiers (CHANGELOG entries and commits cite
# them), so they are not contiguous: 27 was retired earlier; 19-21, 25, 28-30,
# 32, 35, 36 and 38 were removed in 1.17.0 as KB-name greps.

set -u
cd "$(dirname "$0")/.." || exit 2

fail=0
err() { printf 'FAIL: %s\n' "$1"; fail=1; }
ok() { printf 'OK:   %s\n' "$1"; }

# ===========================================================================
# A. MANIFESTS, FRONTMATTER, BUDGETS
# ===========================================================================
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

# README version badge must match (1.13.0 — the badge drifted silently to 1.11.1
# because the sync check above never covered it).
readme_v=$(grep -oE 'badge/version-[0-9.]+-' README.md | head -1 | sed -E 's|badge/version-([0-9.]+)-|\1|')
if [ -z "$readme_v" ]; then
  err "README.md missing the version badge"
elif [ -n "$plugin_v" ] && [ "$readme_v" != "$plugin_v" ]; then
  err "README version badge ($readme_v) drifted from plugin.json ($plugin_v)"
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
done
# Voice contract applies to skills AND agents (CLAUDE.md authoring contract).
for f in skills/*/SKILL.md agents/*.md; do
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
# 11. README skill count sanity (best-effort)
# ---------------------------------------------------------------------------
declared=$(grep -oE 'Skills \([0-9]+\)' README.md | head -1 | grep -oE '[0-9]+')
actual=$(find skills -name SKILL.md | wc -l | tr -d ' ')
if [ -n "$declared" ] && [ "$declared" != "$actual" ]; then
  err "README says Skills ($declared) but $actual SKILL.md files exist under skills/"
fi
# ---------------------------------------------------------------------------
# 14. Progressive disclosure: KBs referenced top-of-file should be in
# teaching-personality + state-ops only (state-schema allowed where a
# manual carve-out is declared). Methodology KBs belong inside the
# phase that uses them.
# ---------------------------------------------------------------------------
# Reads the body lines 1-25 after frontmatter (the "load directive" zone
# Claude Code sees before phase content). Any backticked KB name there that
# isn't teaching-personality or state-ops/state-schema → soft warn.
#
# Skips: /housekeep (legitimate conditional load of state-migration).
kb_names=$(find knowledge -mindepth 1 -maxdepth 1 -type d -exec basename {} \;)
for f in skills/*/SKILL.md; do
  case "$f" in *housekeep*) continue;; esac
  top=$(awk 'BEGIN{n=0} /^---$/{n++; next} n>=2 || (n==1 && NR>1) {print}' "$f" | head -8)
  for kb in $kb_names; do
    case "$kb" in
      teaching-personality|state-ops|state-schema|state-migration|state-lifecycle) continue;;
    esac
    if printf '%s' "$top" | grep -qE "\`$kb\`"; then
      err "$f loads \`$kb\` top-of-file (lines 1-8) — consider moving into the phase that uses it"
    fi
  done
done
# ---------------------------------------------------------------------------
# 48. Hook manifest: valid JSON, references an existing executable hook
# script via CLAUDE_PLUGIN_ROOT.
# ---------------------------------------------------------------------------
if [ -f hooks/hooks.json ]; then
  if ! python3 -c 'import json,sys; json.load(open("hooks/hooks.json"))' 2>/dev/null; then
    err "hooks/hooks.json is not valid JSON"
  fi
  if ! grep -q 'CLAUDE_PLUGIN_ROOT' hooks/hooks.json; then
    err "hooks/hooks.json must address scripts via \${CLAUDE_PLUGIN_ROOT}"
  fi
  if [ ! -f scripts/bodhi-stop-hook.py ]; then
    err "hooks/hooks.json present but scripts/bodhi-stop-hook.py missing"
  fi
else
  err "hooks/hooks.json missing (1.11.0 Stop-hook safety net)"
fi
# ---------------------------------------------------------------------------
# 49. Skill size budget. Context weight is a feature: every SKILL.md must
# stay under 18 KB (the 1.11.0 trim baseline; ratchet down, never up —
# prose that wants to grow past this belongs in a phase-loaded KB or in
# bodhi-state).
# ---------------------------------------------------------------------------
for f in skills/*/SKILL.md; do
  bytes=$(wc -c < "$f" | tr -d ' ')
  if [ "$bytes" -gt 18432 ]; then
    err "$f is ${bytes} bytes (> 18 KB budget) — move detail into a phase-loaded KB or bodhi-state"
  fi
done

# ===========================================================================
# B. STATE LAYER — script integrity, schema, write path
# ===========================================================================
# ---------------------------------------------------------------------------
# 45. bodhi-state integrity: present, executable, compiles, constants pinned
# to the spaced-repetition KB (intervals) and state-ops KB (vocab).
# ---------------------------------------------------------------------------
if [ ! -x scripts/bodhi-state ]; then
  err "scripts/bodhi-state missing or not executable"
else
  if ! python3 -m py_compile scripts/bodhi-state 2>/dev/null; then
    err "scripts/bodhi-state does not compile"
  fi
  # Pin the Leitner table — if the spaced-repetition KB intervals change,
  # the script must change in the same PR.
  if ! grep -q 'BOX_INTERVALS = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30}' scripts/bodhi-state; then
    err "scripts/bodhi-state BOX_INTERVALS drifted from the spaced-repetition KB table (1d/3d/7d/14d/30d)"
  fi
  for t in spaced-review quiz targeted-reteach diagnostic-after-gap learner-forget learner-park pair practice evaluate other; do
    if ! grep -q "\"$t\"" scripts/bodhi-state; then
      err "scripts/bodhi-state SESSION_TYPES missing canonical type '$t' (state-ops KB)"
    fi
    if ! grep -q "\`$t\`" knowledge/state-ops/SKILL.md; then
      err "knowledge/state-ops/SKILL.md vocabulary table missing canonical type '$t'"
    fi
  done

  # 1.14.x: rule 45 pinned the two canonical values the
  # 44-finding audit actually broke on (Leitner intervals, session vocabulary)
  # and left the rest of the canonical surface unpinned — reactive pinning, not
  # comprehensive. The three below are equally load-bearing and equally
  # documented in a KB, so a divergence between KB and script would have been
  # silent. Pin them the same way: bidirectional, fails in the same PR.

  # (a) Prerequisite-gate recency window. Decides the stale-reconfirm verdict —
  # change one side only and the gate silently starts asking reconfirm
  # questions at the wrong cadence.
  if ! grep -q '^GATE_RECENCY_DAYS = 30$' scripts/bodhi-state; then
    err "scripts/bodhi-state GATE_RECENCY_DAYS drifted from the state-ops KB gate table (30 days)"
  fi
  if ! grep -q 'reviewed within 30 days' knowledge/state-ops/SKILL.md; then
    err "knowledge/state-ops/SKILL.md gate table no longer states the 30-day recency window (pins GATE_RECENCY_DAYS)"
  fi

  # (b) Retention rollup tiers. The spaced-repetition KB explicitly warns that
  # /progress and /evaluate previously diverged on these boundaries — so the
  # thresholds were canonicalized in the KB and implemented in cmd_snapshot,
  # with nothing pinning the two together until now.
  if ! grep -q 'b >= 4' scripts/bodhi-state || ! grep -q 'b >= 2' scripts/bodhi-state; then
    err "scripts/bodhi-state cmd_snapshot rollup thresholds drifted from the spaced-repetition KB 3-tier table (Box 4-5 / 2-3 / 1)"
  fi
  if ! grep -q 'Box 4-5' knowledge/spaced-repetition/SKILL.md; then
    err "knowledge/spaced-repetition/SKILL.md rollup table no longer states Box 4-5 (pins cmd_snapshot tiers)"
  fi

  # (c) Confidence vocabulary. cmd_record_review validates against the script's
  # set, so a KB listing a fourth value would let a skill pass something the
  # script rejects — a runtime error with no lint warning.
  for cv in sure mostly guessing; do
    if ! grep -q "CONFIDENCE_VALUES = {\"sure\", \"mostly\", \"guessing\"}" scripts/bodhi-state; then
      err "scripts/bodhi-state CONFIDENCE_VALUES drifted from the state-ops KB (sure|mostly|guessing)"
      break
    fi
    if ! grep -q "$cv" knowledge/state-ops/SKILL.md; then
      err "knowledge/state-ops/SKILL.md subcommand table missing confidence value '$cv'"
    fi
  done

  # (d) lastActivity length guidance — one value, three former spellings
  # (truncate/warn/message). Pins the script constant to the state-ops KB.
  if ! grep -q '^LAST_ACTIVITY_MAX = 120$' scripts/bodhi-state; then
    err "scripts/bodhi-state LAST_ACTIVITY_MAX drifted from the state-ops KB guidance (120 chars)"
  fi
  if ! grep -q '120 chars' knowledge/state-ops/SKILL.md; then
    err "knowledge/state-ops/SKILL.md no longer states the 120-char lastActivity guidance (pins LAST_ACTIVITY_MAX)"
  fi

  # (e) Concept tier ladder (1.14.x). `familiar` and `introduced`
  # were prose-only tiers for four minor versions — declared in the KB, computed
  # nowhere, so /progress inferred a coarser tier from two module rollups. Now
  # that concept_tier() implements them, pin the boundary that separates
  # familiar from introduced: it is the one threshold in the ladder that is a
  # judgment call (apply rung reached AND one retrieval survived spacing) rather
  # than a restatement of the mastery formula.
  if ! grep -q 'bloomLevel", 0) >= 3 and c.get("box", 1) >= 2' scripts/bodhi-state; then
    err "scripts/bodhi-state concept_tier familiar threshold drifted from the blooms-taxonomy KB ladder (Bloom 3+ AND Box 2+)"
  fi
  if ! grep -q 'Bloom 3+ AND Box 2+' knowledge/blooms-taxonomy/SKILL.md; then
    err "knowledge/blooms-taxonomy/SKILL.md tier ladder no longer states the familiar criteria (pins concept_tier)"
  fi
  # The four tier keys are a vocabulary the same way SESSION_TYPES is: /progress
  # indexes into them by name, so a rename on either side breaks the render.
  for tier in unclassified introduced familiar mastered; do
    if ! grep -q "\"$tier\": 0" scripts/bodhi-state; then
      err "scripts/bodhi-state new_module_row missing tier key '$tier'"
    fi
    if ! grep -qi "\*\*$tier\*\*\|\`$tier\`" knowledge/blooms-taxonomy/SKILL.md; then
      err "knowledge/blooms-taxonomy/SKILL.md tier ladder missing tier '$tier'"
    fi
  done
  # (f) Learner-facing Bloom labels + outcome clauses (1.17.0). The script
  # emits bloomLabel/bloomOutcome next to every bloomLevel so skills render
  # instead of translating; the KB table is the one the GUIDE and the skills
  # quote. Pin both sides: label names and the clause opening.
  for lbl in Remember Understand Apply Analyze Evaluate Create; do
    if ! grep -q "\"$lbl\"" scripts/bodhi-state; then
      err "scripts/bodhi-state BLOOM_LABELS missing '$lbl' (blooms-taxonomy KB rendering table)"
    fi
    if ! grep -q "| \*\*$lbl\*\* | you can" knowledge/blooms-taxonomy/SKILL.md; then
      err "knowledge/blooms-taxonomy/SKILL.md rendering table missing '**$lbl** | you can ...' (pins BLOOM_LABELS/BLOOM_OUTCOMES)"
    fi
  done
  if ! grep -q '"bloomLabel": BLOOM_LABELS' scripts/bodhi-state; then
    err "scripts/bodhi-state bloom_render no longer emits bloomLabel"
  fi
  if ! grep -q 'evidence_at_3_plus(c) >= 2' scripts/bodhi-state; then
    err "scripts/bodhi-state gate evidence rule drifted (two level-3+ corrects clear the gate; state-ops KB)"
  fi
  if ! grep -q 'two or more correct reviews graded at Bloom 3+' knowledge/state-ops/SKILL.md; then
    err "knowledge/state-ops/SKILL.md gate table no longer states the two-review evidence rule (pins gate_verdict)"
  fi
fi
# ---------------------------------------------------------------------------
# 46. Deterministic test suite must pass (free, every run).
# ---------------------------------------------------------------------------
if [ -f dev/eval/test_bodhi_state.py ]; then
  if ! python3 dev/eval/test_bodhi_state.py >/tmp/bodhi-state-tests.log 2>&1; then
    err "bodhi-state test suite failed — see /tmp/bodhi-state-tests.log"
  else
    ok "bodhi-state test suite passed"
  fi
else
  err "dev/eval/test_bodhi_state.py missing"
fi
# ---------------------------------------------------------------------------
# 47. docs/example-project must pass bodhi-state verify with zero errors
# (ties the in-repo example to the live schema).
# ---------------------------------------------------------------------------
if [ -d docs/example-project ]; then
  if ! python3 scripts/bodhi-state --project docs/example-project verify >/dev/null 2>&1; then
    err "docs/example-project fails bodhi-state verify"
  fi
fi
# ---------------------------------------------------------------------------
# 51. state-ops KB integrity (1.13.0 split): the operational surface must
# exist and carry the write path, gate, and mastery formula — and the
# state-schema KB must NOT re-grow an operational duplicate (one home
# per fact; the split exists to keep routine fires light).
# ---------------------------------------------------------------------------
if [ ! -f knowledge/state-ops/SKILL.md ]; then
  err "knowledge/state-ops/SKILL.md missing (1.13.0 operational surface)"
else
  for token in 'record-review' 'record-session' 'gate-check' 'consecutiveCorrectAtL4Plus >= 3' 'Discovery procedure'; do
    if ! grep -q "$token" knowledge/state-ops/SKILL.md; then
      err "knowledge/state-ops/SKILL.md missing '$token' (operational surface incomplete)"
    fi
  done
fi
if grep -q '| Subcommand | Owns |' knowledge/state-schema/SKILL.md; then
  err "knowledge/state-schema/SKILL.md re-grew the subcommand table — it lives in state-ops (1.13.0 split)"
fi
# ---------------------------------------------------------------------------
# 43. State-writing skills MUST route JSON mutations through bodhi-state
# (1.11.0). This replaces the 1.10.12 CHECKPOINT prose discipline: the
# descriptive-vs-imperative defect class is closed by moving the writes
# into a deterministic script instead of defending against it with
# louder markdown. Each writer must (a) invoke bodhi-state and (b) NOT
# reintroduce the retired CHECKPOINT prose (a reappearance means someone
# is hand-writing JSON again).
# ---------------------------------------------------------------------------
for s in quiz teach practice forget reflect pair evaluate continue; do
  f="skills/$s/SKILL.md"
  if [ ! -f "$f" ]; then continue; fi
  if ! grep -q 'bodhi-state' "$f"; then
    err "$f writes tracking state but never invokes bodhi-state (1.11.0 write path)"
  fi
  if grep -qE 'CHECKPOINT-before-writes|CHECKPOINT-after-writes' "$f"; then
    err "$f reintroduces retired CHECKPOINT prose — JSON writes belong in bodhi-state, not hand-edited (1.11.0)"
  fi
  if ! grep -qiE '\*\*Fallback' "$f"; then
    err "$f invokes bodhi-state but has no **Fallback:** paragraph for script-unavailable"
  fi
done
# ---------------------------------------------------------------------------
# 44. sessionHistory[] writers use record-session (vocabulary enforced in
# code by bodhi-state; the prose just has to route through it). Skills
# that hand-append sessionHistory are drift.
# ---------------------------------------------------------------------------
for s in quiz forget reflect pair practice evaluate; do
  f="skills/$s/SKILL.md"
  if [ ! -f "$f" ]; then continue; fi
  if grep -qE 'append.*sessionHistory|sessionHistory.*append' "$f"; then
    err "$f hand-appends sessionHistory — use bodhi-state record-session (1.11.0)"
  fi
done
if ! grep -q 'record-session' skills/quiz/SKILL.md; then
  err "skills/quiz/SKILL.md does not invoke bodhi-state record-session"
fi
# ---------------------------------------------------------------------------
# 52. /progress renders from bodhi-state snapshot (1.14.0) — one script call,
# not hand-computed rollups over tracking files.
# ---------------------------------------------------------------------------
if [ -f skills/progress/SKILL.md ]; then
  if ! grep -q 'snapshot' skills/progress/SKILL.md; then
    err "skills/progress/SKILL.md does not invoke bodhi-state snapshot (1.14.0)"
  fi
fi
# ---------------------------------------------------------------------------
# 50. 1.11.1 state-integrity contracts.
# ---------------------------------------------------------------------------
# Successive-relearning retries must use --retry (no box movement).
if ! grep -q -- '--retry' skills/quiz/SKILL.md; then
  err "skills/quiz/SKILL.md relearning loop does not use record-review --retry (1.11.1 — retries must not undo the demotion)"
fi
if ! grep -q -- '--retry' scripts/bodhi-state; then
  err "scripts/bodhi-state missing the --retry flag"
fi
# /reflect must carry the same-day guard (no double box movement per day).
if ! grep -qi 'same-day guard' skills/reflect/SKILL.md; then
  err "skills/reflect/SKILL.md missing the same-day guard (1.11.1 — one day of evidence, one box movement)"
fi
# /evaluate must carry the canonical completion criterion and the explicit ask.
if ! grep -qi 'completion criterion' skills/evaluate/SKILL.md; then
  err "skills/evaluate/SKILL.md missing the canonical completion criterion (1.11.1)"
fi
if ! grep -qi 'Project completion (canonical' knowledge/state-schema/SKILL.md; then
  err "knowledge/state-schema/SKILL.md missing the Project completion section (1.11.1)"
fi
# Pretest fires on first exposure only.
if ! grep -qi 'first exposure' skills/teach/SKILL.md; then
  err "skills/teach/SKILL.md pretest not gated on first exposure (1.11.1 — pretesting research covers untaught material only)"
fi
# Every bodhi-state invocation in a skill (or a skill's references/ file)
# carries --project.
for f in skills/*/SKILL.md skills/*/references/*.md; do
  [ -f "$f" ] || continue
  if grep 'scripts/bodhi-state" ' "$f" | grep -vq -- '--project'; then
    err "$f has a bodhi-state invocation without --project (defaults to cwd and errors outside the project dir)"
  fi
done
# ai-learning-safeguards KB must not re-orphan.
if ! grep -rq 'ai-learning-safeguards' skills/; then
  err "ai-learning-safeguards KB is orphaned again — no skill references it"
fi
# ---------------------------------------------------------------------------
# 53. Discovery is a file-read, never a bodhi-state subcommand. The Fable-5
# sweep caught /continue inventing `bodhi-state discover`/`--list` against
# the strong "everything goes through bodhi-state" prior. (a) state-ops
# must carry the negative guard so every skill's pointer inherits it;
# (b) no skill or KB may emit a phantom discovery subcommand call.
# ---------------------------------------------------------------------------
if [ -f knowledge/state-ops/SKILL.md ]; then
  if ! grep -qi 'not a .*bodhi-state.* subcommand\|Discovery is a file-read' knowledge/state-ops/SKILL.md; then
    err "knowledge/state-ops/SKILL.md missing the negative guard: discovery is a file-read, not a bodhi-state subcommand (rule 53)"
  fi
fi
if grep -rnE 'bodhi-state[^`]*(discover|--list|list-projects)' skills/ knowledge/ 2>/dev/null | grep -v 'not a.*subcommand\|no .discover\|there is no' >/dev/null; then
  grep -rnE 'bodhi-state[^`]*(discover|--list|list-projects)' skills/ knowledge/ 2>/dev/null | grep -v 'not a.*subcommand\|no .discover\|there is no'
  err "a skill/KB emits a non-existent bodhi-state discovery subcommand (discover/--list/list-projects) — discovery is a file-read (rule 53)"
fi
# ---------------------------------------------------------------------------
# 12. v2 schema: no writes to lastSessionSummary or bloomResetNote outside
# the v1-boundary skills (/housekeep, /progress all).
# ---------------------------------------------------------------------------
# These fields were removed from state.json in v2. The only legitimate
# references are inside skills that straddle the v1↔v2 boundary by design:
# /housekeep migrates them; /progress all detects them as a health flag.
# Everywhere else, mentioning these fields is drift.
# Applies to skills AND agents — both can touch tracking files.
for f in skills/*/SKILL.md agents/*.md; do
  case "$f" in *housekeep*|*progress*) continue;; esac
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
# /housekeep references both during migration; /progress all references them
# as legacy-layout health flags. Everywhere else is drift.
# Applies to skills AND agents.
for f in skills/*/SKILL.md agents/*.md; do
  case "$f" in *housekeep*|*progress*) continue;; esac
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
# the new fields by writing only the v2 shape.
#
# Heuristic: a skill is a "writer" if it both references spaced-review.json AND
# mentions either "Update tracking", "Apply the spaced-repetition KB", or
# explicit append/update verbs near the file. Scope: the v3 writer set
# (quiz, teach, practice, forget, pair; /explain merged into /teach in 1.11.0).
for s in quiz teach practice forget pair; do
  f="skills/$s/SKILL.md"
  if [ ! -f "$f" ]; then continue; fi
  if grep -q 'spaced-review\.json' "$f"; then
    if ! grep -qE 'bloomLevel|feynmanPassed|consecutiveCorrectAtL4Plus|record-review|set-feynman' "$f"; then
      err "$f writes spaced-review.json but routes through neither the v3 per-concept fields nor bodhi-state (record-review/set-feynman)"
    fi
  fi
done
# ---------------------------------------------------------------------------
# 17. /teach Phase 1 must mention the prerequisite Bloom gate.
# ---------------------------------------------------------------------------
# From the 1.10.0 pedagogy audit — Bloom advancement is contractual now.
# 1.10.10 strengthens the check: the gate must use the new trigger model
# (scan for prior work on currentModule, not "different module" string-match),
# must declare the strong-v2-evidence fallthrough, and must be offer-shaped
# (no auto-block).
if [ -f skills/teach/SKILL.md ]; then
  if ! grep -qiE 'prerequisite.*(bloom|gate)|(bloom|gate).*prerequisite' skills/teach/SKILL.md; then
    err "skills/teach/SKILL.md missing the prerequisite Bloom gate language "
  fi
  # 1.11.0 — the gate's trigger/verdict logic lives in bodhi-state gate-check
  # (canonical doc: state-ops KB since 1.13.0). The skill must delegate, not re-derive.
  if ! grep -q 'gate-check' skills/teach/SKILL.md; then
    err "skills/teach/SKILL.md prerequisite gate does not invoke bodhi-state gate-check (1.11.0)"
  fi
  # 1.10.10 — gate must be offer-shaped, not auto-block.
  if ! grep -qiE 'offer|let the learner (choose|decide|pick)|learner decides|opt-in' skills/teach/SKILL.md; then
    err "skills/teach/SKILL.md prerequisite gate missing offer-shape language (1.10.10 fix — gate must be offer-shaped per 1.10.2 discipline)"
  fi
  # 1.11.0 — pretesting must open Phase 2 (desirable-difficulties KB).
  if ! grep -qiE 'pretest' skills/teach/SKILL.md; then
    err "skills/teach/SKILL.md Phase 2 missing the pretest step (1.11.0 — desirable-difficulties KB Pretesting)"
  fi
  # 1.14.0 — pretest-vs-retrieval and the reteach duty come from
  # bodhi-state session-brief, not re-derived from tracking-file prose.
  if ! grep -q 'session-brief' skills/teach/SKILL.md; then
    err "skills/teach/SKILL.md does not invoke bodhi-state session-brief (1.14.0 — branch detection lives in code)"
  fi
  # 1.14.0 — the understanding-only sub-flow is phase-loaded from
  # references/, not inlined (progressive disclosure inside the skill).
  if [ ! -f skills/teach/references/understanding-only.md ]; then
    err "skills/teach/references/understanding-only.md missing (1.14.0 — understanding-only sub-flow)"
  elif ! grep -q 'references/understanding-only.md' skills/teach/SKILL.md; then
    err "skills/teach/SKILL.md does not point at references/understanding-only.md"
  fi
fi
# ---------------------------------------------------------------------------
# 18. /progress must mention the canonical mastery formula or the legacy
# fallthrough display rule.
# ---------------------------------------------------------------------------
# From the 1.10.0 pedagogy audit — Mastery % can no longer be fabricated. Either the
# formula is cited inline (referencing the state-schema KB) or the column
# explicitly handles the legacy display fallthrough.
if [ -f skills/progress/SKILL.md ]; then
  if ! grep -qE 'mastered === true|Mastery % formula|consecutiveCorrectAtL4Plus' skills/progress/SKILL.md; then
    err "skills/progress/SKILL.md missing the canonical mastery formula or fallthrough rule "
  fi
fi
# ---------------------------------------------------------------------------
# 40. Legacy fallthrough rule must NOT combine bloomLevel:0 with lastReviewed
# (the 1.10.7 corrected boundary — pre-v3 concepts routinely have
# populated lastReviewed; combining the two false-blocked every existing
# learner on first migration).
# ---------------------------------------------------------------------------
# The corrected rule keys off bloomLevel: 0 alone. Any file pairing
# bloomLevel: 0 with lastReviewed === null in the SAME logical predicate
# is using the pre-1.10.7 broken rule.
for f in skills/*/SKILL.md knowledge/state-schema/SKILL.md knowledge/state-ops/SKILL.md knowledge/state-migration/SKILL.md; do
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
# 41. /housekeep migrate: per-target idempotency markers (1.10.8) with the
# v2->v3 transform delegated to bodhi-state migrate-spaced-review
# (1.11.0 — idempotent in code; the STOP-banner/matrix/defensive-check
# prose apparatus from 1.10.9-1.10.11 was retired with it). /housekeep migrate must
# run the script unconditionally for every project.
# ---------------------------------------------------------------------------
if [ -f skills/housekeep/SKILL.md ]; then
  if ! grep -q 'migration-1.10' skills/housekeep/SKILL.md; then
    err "skills/housekeep/SKILL.md missing .migration-1.10 marker (1.10.8 fix — per-target idempotency)"
  fi
  if ! grep -qiE 'per-target idempotency|per target idempotency' skills/housekeep/SKILL.md; then
    err "skills/housekeep/SKILL.md missing per-target idempotency declaration (1.10.8 fix)"
  fi
  if ! grep -q 'migrate-spaced-review' skills/housekeep/SKILL.md; then
    err "skills/housekeep/SKILL.md migrate step does not invoke bodhi-state migrate-spaced-review (1.11.0)"
  fi
  if ! grep -qiE 'unconditionally|every project, regardless' skills/housekeep/SKILL.md; then
    err "skills/housekeep/SKILL.md must direct running migrate-spaced-review unconditionally (the 1.10.10 single-marker short-circuit class)"
  fi
  # Fallback path keeps the in-place mutation discipline for script-less runs.
  if ! grep -qiE 'mutate the parsed JSON in place|in-place mutation' skills/housekeep/SKILL.md; then
    err "skills/housekeep/SKILL.md fallback missing in-place mutation discipline (1.10.9 fix)"
  fi
fi
# ---------------------------------------------------------------------------
# 42. /learn Phase 3 and /plan Regenerate must require per-module
# "Prerequisites for next module:" declarations (1.10.10 fix —
# feeds the /teach Phase 1 gate's structured-declaration path).
# ---------------------------------------------------------------------------
for f in skills/learn/SKILL.md skills/plan/SKILL.md; do
  if [ ! -f "$f" ]; then continue; fi
  if ! grep -qE 'Prerequisites for next module' "$f"; then
    err "$f missing per-module Prerequisites-for-next-module declaration requirement (1.10.10 fix)"
  fi
done

# ===========================================================================
# C. CHAIN CONVENTION — --invoked-from on both sides
# ===========================================================================
# ---------------------------------------------------------------------------
# 9. Chainable skills must handle --invoked-from=
# ---------------------------------------------------------------------------
chainable="teach practice reflect progress quiz forget pair debug-together mentor"
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
  for sub in progress teach practice reflect; do
    if grep -qE "Auto-invoke .\/${sub}\b" skills/continue/SKILL.md; then
      if ! grep -qE "\/${sub}([[:space:]]|--)[^\`]*--invoked-from=continue" skills/continue/SKILL.md; then
        err "skills/continue/SKILL.md auto-invokes /$sub but without --invoked-from=continue"
      fi
    fi
  done
fi
# ---------------------------------------------------------------------------
# 55. The --invoked-from chain convention has two enforceable sides (1.16.0).
# ---------------------------------------------------------------------------
# The context economy depends on (a) every chainable skill
# checking $ARGUMENTS for --invoked-from= and skipping re-loads, and (b) every
# model-directed invocation of a chainable skill passing the flag. Neither was
# lint-visible: a skill that silently dropped its check would re-load every KB
# it was told to skip, and the LLM evals do not cover the chaining skills.
CHAINABLE_SKILLS="teach practice reflect progress quiz forget pair debug-together mentor"
for s in $CHAINABLE_SKILLS; do
  f="skills/$s/SKILL.md"
  [ -f "$f" ] || continue
  if ! grep -q -- '--invoked-from' "$f"; then
    err "$f is chainable (CLAUDE.md) but never checks --invoked-from= — a chained call would re-load personality/state-ops and re-run discovery (rule 55)"
  fi
done
# (b) an imperative auto-invoke of a chainable skill must carry the flag. The
# enforceable shape is "auto-invoke `/<skill> ...`" (the command adjacent in
# backticks) — descriptive mentions ("Can be auto-invoked by /continue"),
# prohibitions ("Do NOT auto-invoke `/mentor`"), and offers quoting a command
# for the LEARNER to type are not invocation sites and are exempt.
CHAINABLE_ALT="teach|practice|reflect|progress|quiz|forget|pair|debug-together|mentor"
bad_chain=$(grep -rniE 'auto-invoke \`/' skills/ --include='*.md' \
    | grep -viE 'not auto-invoke' \
    | grep -E "\`/(bodhikit:)?($CHAINABLE_ALT)\b" \
    | grep -v -- '--invoked-from=')
if [ -n "$bad_chain" ]; then
  printf '%s\n' "$bad_chain" | sed 's/^/  /'
  err "an auto-invoke of a chainable skill does not pass --invoked-from=<caller> — the callee will re-load everything the chain exists to skip (rule 55)"
fi
# ---------------------------------------------------------------------------
# 22. /teach Phase 3 must offer /pair (opt-in pattern).
# ---------------------------------------------------------------------------
# CHANGELOG 1.4.0 promised /teach -> /pair; 1.10.2 wires it as an offer per the
# sprint's chain-shape decision. Check that Phase 3 mentions the offer with the
# --invoked-from=teach chain flag.
if [ -f skills/teach/SKILL.md ]; then
  phase3=$(awk '/^## Phase 3/,/^## Phase 4/' skills/teach/SKILL.md)
  if ! printf '%s' "$phase3" | grep -qE 'bodhikit:pair.*invoked-from=teach'; then
    err "skills/teach/SKILL.md Phase 3 does not offer /pair with --invoked-from=teach "
  fi
fi
# ---------------------------------------------------------------------------
# 23. /practice Phase 3 must offer /debug-together.
# ---------------------------------------------------------------------------
if [ -f skills/practice/SKILL.md ]; then
  phase3=$(awk '/^## Phase 3/,/^## Phase 4|^---/' skills/practice/SKILL.md)
  if ! printf '%s' "$phase3" | grep -qE 'bodhikit:debug-together.*invoked-from=practice'; then
    err "skills/practice/SKILL.md Phase 3 does not offer /debug-together with --invoked-from=practice "
  fi
fi
# ---------------------------------------------------------------------------
# 24. /teach Phase 4 must offer /debug-together.
# ---------------------------------------------------------------------------
if [ -f skills/teach/SKILL.md ]; then
  phase4=$(awk '/^## Phase 4/,/^## Phase 5/' skills/teach/SKILL.md)
  if ! printf '%s' "$phase4" | grep -qE 'bodhikit:debug-together.*invoked-from=teach'; then
    err "skills/teach/SKILL.md Phase 4 does not offer /debug-together with --invoked-from=teach "
  fi
fi
# ---------------------------------------------------------------------------
# 37. /practice Phase 3 must offer /pair (collaboration alternative).
# ---------------------------------------------------------------------------
if [ -f skills/practice/SKILL.md ]; then
  phase3=$(awk '/^## Phase 3/,/^---$/' skills/practice/SKILL.md)
  if ! printf '%s' "$phase3" | grep -qE 'bodhikit:pair.*invoked-from=practice'; then
    err "skills/practice/SKILL.md Phase 3 does not offer /pair with --invoked-from=practice "
  fi
fi
# ---------------------------------------------------------------------------
# 26. Newly chainable skills (pair, debug-together, mentor) must declare
# the offer-only nature in their opening lines (consistency with the
# CHANGELOG 1.4.0 contract reset and the Capstone offer pattern).
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

# ===========================================================================
# D. KB SINGLE-SOURCING — conditional: fires only when a file touches the thing
# ===========================================================================
# ---------------------------------------------------------------------------
# 4. Files that touch tracking shapes must reference state-ops (the routine
# operational surface) or state-schema (the field-level reference, loaded
# only by manual carve-outs / fallbacks / housekeep). Since 1.13.0 the two
# are split so routine fires stop paying for field shapes they cannot use.
# ---------------------------------------------------------------------------
for f in skills/*/SKILL.md agents/*.md rules/*.md; do
  case "$f" in *state-schema*|*state-ops*) continue;; esac
  if grep -qE 'state\.json|spaced-review\.json|progress\.md|bodhi-profile' "$f"; then
    if ! grep -qE 'state-(ops|schema)' "$f"; then
      err "$f touches tracking files but references neither state-ops nor state-schema KB"
    fi
  fi
done
# Skills that hand-mutate JSON (the declared manual carve-outs) must ALSO
# reference state-schema — shapes are required where the script does not own
# the write: /learn scaffolding, /evaluate profile writes, /assess Bloom maps,
# /mentor career fields, /housekeep migrations.
for s in learn evaluate assess mentor housekeep; do
  f="skills/$s/SKILL.md"
  if [ ! -f "$f" ]; then continue; fi
  if ! grep -q 'state-schema' "$f"; then
    err "$f performs a manual carve-out but does not reference state-schema KB (shapes required where bodhi-state does not own the write)"
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
# 54. A judgment rule must be reachable from the site that applies it (1.14.x).
# ---------------------------------------------------------------------------
# A 1.14.x grading bug cost a day to diagnose because the precedence rule governing the parrot
# boundary lived in feynman-technique while the write that applied it (/teach
# Phase 5) cited only spaced-repetition. The rule was correct and out of scope.
# A KB reference is not decoration at a write site — it is the load path.
#
# --tested-bloom ratchets (never demotes) and feeds the prerequisite gate;
# the "what the answer reached, not what the learner claims"
# rule lives in blooms-taxonomy.
# set-feynman sets feynmanPassed, which is never unset; the grading
# ladder and its precedence rule live in feynman-technique.
#
# Both are one-way writes, which is exactly why the governing rule has to be
# in context at the moment of the call.
for f in skills/*/SKILL.md skills/*/references/*.md; do
  [ -f "$f" ] || continue
  if grep -q -- '--tested-bloom' "$f" && ! grep -q 'blooms-taxonomy' "$f"; then
    err "$f writes --tested-bloom (one-way ratchet, feeds the prerequisite gate) but never references the blooms-taxonomy KB — the anti-inflation rule is out of scope at the write site"
  fi
  # Match an actual invocation (bodhi-state ... set-feynman), not a prohibition
  # — /practice and /pair both say "Do NOT call set-feynman here", which is the
  # opposite of a write and must not trip this rule.
  if grep -q 'bodhi-state" --project <project> set-feynman' "$f" && ! grep -q 'feynman-technique' "$f"; then
    err "$f calls set-feynman (feynmanPassed is set-never-unset) but never references the feynman-technique KB — the grading ladder is out of scope at the write site"
  fi
done

# ===========================================================================
# E. BEHAVIOUR PINNED IN PROSE — grandfathered from the 1.10.0 audit; shrink, do not grow
# ===========================================================================
# ---------------------------------------------------------------------------
# 31. /evaluate must have a Phase 2.5 prediction step.
# ---------------------------------------------------------------------------
if [ -f skills/evaluate/SKILL.md ]; then
  if ! grep -qE '## Phase 2\.5|Predict Your Trajectory' skills/evaluate/SKILL.md; then
    err "skills/evaluate/SKILL.md missing Phase 2.5 prediction step "
  fi
fi
# ---------------------------------------------------------------------------
# 33. skill-assessor agent must collect learner self-rating.
# ---------------------------------------------------------------------------
if [ -f agents/skill-assessor.md ]; then
  if ! grep -qiE 'self-rating|learnerSelfRating|rate yourself' agents/skill-assessor.md; then
    err "agents/skill-assessor.md does not collect learner self-rating "
  fi
fi
# ---------------------------------------------------------------------------
# 34. /pair Strong-Style step 7 must be ZPD-signal-gated, not time-gated.
# ---------------------------------------------------------------------------
# The audit caught the hardcoded "After 10-15 minutes" rule as scaffolding-by-
# clock rather than scaffolding-by-competence. The rewrite (corrected to
# observable-in-conversation signals) must mention ZPD signals explicitly.
if [ -f skills/pair/SKILL.md ]; then
  mode1=$(awk '/^## Mode 1/,/^## Mode 2/' skills/pair/SKILL.md)
  if ! printf '%s' "$mode1" | grep -qE 'ZPD|zone-of-proximal-development'; then
    err "skills/pair/SKILL.md Mode 1 does not reference ZPD for role-reversal gating "
  fi
fi
# ---------------------------------------------------------------------------
# 39. /learn Phase 3 must require per-phase Spiral Revisits (constructivism spiral-curriculum mechanic made enforceable).
# ---------------------------------------------------------------------------
if [ -f skills/learn/SKILL.md ]; then
  phase3=$(awk '/^## Phase 3/,/^## Phase 4/' skills/learn/SKILL.md)
  if ! printf '%s' "$phase3" | grep -qiE 'spiral revisit'; then
    err "skills/learn/SKILL.md Phase 3 does not declare the per-phase Spiral Revisit requirement "
  fi
fi

# ---------------------------------------------------------------------------
echo
if [ "$fail" -eq 0 ]; then
  echo "All hard checks passed."
  exit 0
else
  echo "Contract violations above."
  exit 1
fi
