#!/usr/bin/env bash
# dev/eval/run-llm-evals.sh — end-to-end skill evals against a live model.
#
# Each scenario copies a fixture project into a temp dir, runs a BodhiKit
# skill headlessly via `claude -p`, then asserts on the resulting FILE STATE
# (not the prose). This is the automated version of the 1.10.x manual dogfood:
# it catches executor-discipline regressions (writes described but not
# performed, fields silently dropped, vocabulary invented) that dev/check.sh
# cannot see by design.
#
# Costs real tokens. Run before tagging a release, not on every commit.
# The deterministic layer is tested for free by dev/eval/test_bodhi_state.py.
#
# Usage:
#   dev/eval/run-llm-evals.sh            # run all scenarios
#   dev/eval/run-llm-evals.sh forget     # run one scenario

set -u
cd "$(dirname "$0")/../.." || exit 2
REPO="$PWD"
FIXTURE="$REPO/dev/eval/fixtures/v2-project"
FAIL=0

if ! command -v claude >/dev/null 2>&1; then
  echo "SKIP: claude CLI not on PATH"; exit 0
fi

run_scenario() {
  name="$1"; prompt="$2"; assert="$3"; prep="${4:-}"
  tmp=$(mktemp -d "/tmp/bodhi-eval-$name.XXXXXX")
  cp -r "$FIXTURE" "$tmp/learningWithBodhi"
  echo "== scenario: $name  (workdir $tmp)"
  if [ -n "$prep" ]; then "$prep" "$tmp/learningWithBodhi/sql-deep-dive" || { echo "FAIL: $name prep"; FAIL=1; return; }; fi
  # --dangerously-skip-permissions is safe here: the run is confined to a
  # throwaway temp copy of the fixture. Without it, headless runs cannot
  # execute bodhi-state via Bash and silently degrade to the manual fallback
  # (the first harness run proved the fallback under-delivers — see 1.11.0
  # CHANGELOG), which is exactly the path we do NOT want to certify releases on.
  # CLAUDE_PLUGIN_ROOT is exported so the Bash tool inside the run inherits it —
  # in a --plugin-dir run from a temp dir, neither the substitution nor the
  # ~/.claude/plugins find-fallback can locate scripts/bodhi-state otherwise.
  ( cd "$tmp/learningWithBodhi/sql-deep-dive" && \
    CLAUDE_PLUGIN_ROOT="$REPO" claude -p "$prompt" \
      --plugin-dir "$REPO" \
      --dangerously-skip-permissions \
      --max-turns 30 \
      > "$tmp/transcript.txt" 2>&1 )
  if python3 "$REPO/dev/eval/assert_scenario.py" "$assert" "$tmp/learningWithBodhi/sql-deep-dive"; then
    echo "PASS: $name"
  else
    echo "FAIL: $name — transcript at $tmp/transcript.txt, project left at $tmp"
    FAIL=1
    return
  fi
  rm -rf "$tmp"
}

want="${1:-all}"

# Scenario 1: migrate — the v2->v3 transform must land on disk with backup
# and marker, preserving non-canonical fields. (1.10.8/1.10.11 regression class)
if [ "$want" = "all" ] || [ "$want" = "migrate" ]; then
  run_scenario migrate \
    "/bodhikit:housekeep migrate" \
    migrate
fi

# Scenario 2: forget — learner-initiated demote must persist box reset,
# counter reset, learner-forget session entry. (1.10.12/1.10.13 regression class)
if [ "$want" = "all" ] || [ "$want" = "forget" ]; then
  run_scenario forget \
    "/bodhikit:forget B-tree indexes" \
    forget
fi

# Scenario 3: quiz — simulated learner; asserts reviews + session entry landed.
# The prompt embeds the learner's answers so the skill can run start-to-finish.
if [ "$want" = "all" ] || [ "$want" = "quiz" ]; then
  run_scenario quiz \
    "/bodhikit:quiz current — I cannot answer interactively in this headless run; simulate a brief 3-question quiz on the due concepts, assume I answered the first correctly (confidence: sure) and the rest incorrectly (confidence: mostly), then complete ALL tracking updates exactly as the skill specifies." \
    quiz
fi

# Scenario 4: reflect — the 1.11.1 same-day guard. Prep simulates a quiz
# earlier the same day; reflect must NOT re-move that concept's box, must
# record the un-reviewed concept, and touch-state must bump the profile once.
prep_reflect() {
  python3 "$REPO/scripts/bodhi-state" --project "$1" record-review \
    --concept "B-tree indexes" --result correct --tested-bloom 3 \
    --confidence sure --source quiz > /dev/null
}
if [ "$want" = "all" ] || [ "$want" = "reflect" ]; then
  run_scenario reflect \
    "/bodhikit:reflect — headless eval run: simulate my answers. Q1: honestly nothing felt hard today. Q2: normalization clicked faster than expected. Q3 covers today's two main concepts: for 'B-tree indexes' I give a clean, jargon-free 2-sentence explanation and rate myself 9; for 'Normalization trade-offs' I also give a clean 2-sentence explanation and rate myself 6. Q4: skip. Then complete ALL tracking updates exactly as the skill specifies, including the same-day guard." \
    reflect prep_reflect
fi

echo
[ "$FAIL" -eq 0 ] && echo "All LLM evals passed." || echo "LLM eval failures above."
exit $FAIL
