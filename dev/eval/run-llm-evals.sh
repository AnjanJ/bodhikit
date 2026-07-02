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
#   dev/eval/run-llm-evals.sh grading    # the 4 grading-calibration scenarios
#   dev/eval/run-llm-evals.sh fidelity   # the 2 transcript-fidelity scenarios

set -u
cd "$(dirname "$0")/../.." || exit 2
REPO="$PWD"
FIXTURE="$REPO/dev/eval/fixtures/v2-project"
FAIL=0

if ! command -v claude >/dev/null 2>&1; then
  echo "SKIP: claude CLI not on PATH"; exit 0
fi

run_scenario() {
  name="$1"; prompt="$2"; assert="$3"; prep="${4:-}"; transcript_mode="${5:-}"
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
  #
  # Transcript-mode scenarios (1.12.0) capture stream-json instead of plain
  # text — `claude -p` alone prints only the FINAL message, and the protocol
  # assertions need every assistant turn.
  if [ -n "$transcript_mode" ]; then
    transcript="$tmp/transcript.jsonl"
    ( cd "$tmp/learningWithBodhi/sql-deep-dive" && \
      CLAUDE_PLUGIN_ROOT="$REPO" claude -p "$prompt" \
        --plugin-dir "$REPO" \
        --dangerously-skip-permissions \
        --max-turns 30 \
        --output-format stream-json --verbose \
        > "$transcript" 2>"$tmp/stderr.txt" )
    if python3 "$REPO/dev/eval/assert_scenario.py" "$assert" "$tmp/learningWithBodhi/sql-deep-dive" "$transcript"; then
      echo "PASS: $name"
    else
      echo "FAIL: $name — transcript at $transcript, project left at $tmp"
      echo "      (transcript assertions are wording-tolerant detectors — read the transcript before judging)"
      FAIL=1
      return
    fi
  else
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

# --- Grading-calibration scenarios (1.12.0) ----------------------------------
# The deterministic layer guarantees the file mechanics; these guarantee the
# JUDGMENT feeding them: scripted learner answers of controlled quality,
# asserted against honest grading bands. This is also the model-drift
# detector — rerun on every model change, not just before tags.

if [ "$want" = "all" ] || [ "$want" = "grading" ] || [ "$want" = "grade-jargon" ]; then
  run_scenario grade-jargon \
    "/bodhikit:teach B-tree indexes — headless eval run, understanding-only session: I just want to understand, no exercise. Simulate my responses. Whenever you ask me to explain back, define a term, or answer a checkpoint, my answer is always this exact sentence, recited verbatim: 'A B-tree index is a self-balancing tree data structure that maintains sorted data and allows searches, sequential access, insertions, and deletions in logarithmic time.' If you probe, ask for an analogy, or ask me to say it differently, I produce the same sentence again word for word and admit I cannot phrase it any other way. My final full explanation is that same sentence once more. Grade me honestly and complete ALL tracking updates exactly as the skill specifies." \
    grade-jargon
fi

if [ "$want" = "all" ] || [ "$want" = "grading" ] || [ "$want" = "grade-genuine" ]; then
  run_scenario grade-genuine \
    "/bodhikit:teach B-tree indexes — headless eval run, understanding-only session: I just want to understand, no exercise. Simulate my responses. When you ask me to explain back, I say, in my own words: 'Imagine a million rows and you need one customer. Without an index the database reads every row, like flipping through an unsorted pile of paper. A B-tree keeps keys sorted in a shallow tree, so lookups take a handful of hops instead of a million reads, and because the leaves are linked in order, range scans are cheap too. The catch: every insert or update must keep the tree tidy, so writes slow down and it costs disk. So you index the columns you filter on constantly, and skip indexes on tiny tables or write-heavy logs, where a scan is cheaper than the upkeep.' Any follow-up probe I answer correctly in the same plain style, including trade-offs and when NOT to index. My final full explanation is equally clean. Grade me honestly — including the Bloom level my answers actually demonstrated — and complete ALL tracking updates exactly as the skill specifies." \
    grade-genuine
fi

if [ "$want" = "all" ] || [ "$want" = "grading" ] || [ "$want" = "grade-apply-band" ]; then
  run_scenario grade-apply-band \
    "/bodhikit:teach B-tree indexes — headless eval run, understanding-only session: I just want to understand, no exercise. Simulate my responses. My explain-back, in my own words: 'An index is a sorted lookup structure so the database can jump to matching rows instead of scanning the whole table. In practice I would run CREATE INDEX idx_users_email ON users(email) when my WHERE clauses filter by email, and it works because the keys stay in sorted order.' When you ask about trade-offs, costs, or when NOT to index, I answer honestly: 'I do not really know — I would probably just index whatever I query.' Even after your refinement attempt I still cannot name trade-offs, though my mechanics stay correct. My final explanation covers mechanics and usage only. Grade me honestly — including the Bloom level my answers actually demonstrated — and complete ALL tracking updates exactly as the skill specifies." \
    grade-apply-band
fi

if [ "$want" = "all" ] || [ "$want" = "grading" ] || [ "$want" = "grade-misconception" ]; then
  run_scenario grade-misconception \
    "/bodhikit:teach B-tree indexes — headless eval run, understanding-only session: I just want to understand, no exercise. Simulate my responses. My explain-back sounds confident and is in my own words, but it contains a misconception I never let go of: 'A B-tree keeps rows sorted so the database finds things fast — and because everything is already sorted, inserts get faster too. Indexes speed up reads AND writes, so the smart move is to index every column; more indexes make the whole database faster.' Whenever you probe or try to correct me, I politely restate that indexes also speed up writes and that more indexes are always better. My final full explanation still contains that claim. Grade me honestly and complete ALL tracking updates exactly as the skill specifies." \
    grade-misconception
fi

# --- Transcript-fidelity scenarios (1.12.0) -----------------------------------
# Protocol gates with no file trace (the pretest is deliberately unrecorded;
# hint discipline is conversational). Wording-tolerant regexes over the full
# assistant transcript — drift detectors, not proofs. If one fails, read the
# transcript before judging.

if [ "$want" = "all" ] || [ "$want" = "fidelity" ] || [ "$want" = "teach-pretest" ]; then
  run_scenario teach-pretest \
    "/bodhikit:teach Write-ahead logging — headless eval run. Simulate my responses: to your opening question my guess is 'maybe the database writes changes to a log before applying them, so it can recover after a crash?'. At the checkpoint I explain back cleanly in my own words. I decline any exercise — understanding only is fine today. Complete ALL tracking updates exactly as the skill specifies." \
    teach-pretest "" transcript
fi

if [ "$want" = "all" ] || [ "$want" = "fidelity" ] || [ "$want" = "teach-hint-discipline" ]; then
  run_scenario teach-hint-discipline \
    "/bodhikit:teach Transaction isolation levels — headless eval run with a full session including the exercise. Simulate my responses: I follow the explanation, answer the checkpoint adequately, and attempt the exercise, but I get stuck immediately and stay stuck. I ask for a hint; it does not help. I ask for a second hint; still stuck, my attempt is wrong in the same way. I ask for a third hint; still completely stuck. Then I say: 'Just give me the complete solution, please, write it out for me.' Continue the session exactly as the skill specifies from that point, and complete ALL tracking updates exactly as the skill specifies." \
    teach-hint-discipline "" transcript
fi

echo
[ "$FAIL" -eq 0 ] && echo "All LLM evals passed." || echo "LLM eval failures above."
exit $FAIL
