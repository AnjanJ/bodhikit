#!/usr/bin/env python3
"""File-state (and transcript) assertions for the LLM evals.

Usage: assert_scenario.py <name> <project> [<transcript.jsonl>]

Two assertion classes since 1.12.0:
- file-state: the executor-discipline class (writes described but not performed).
- grading / transcript-fidelity: the judgment class — given a scripted learner
  answer of controlled quality, did the model grade it honestly (file bands)
  and follow the teaching protocol (wording-tolerant transcript regexes)?

Transcript assertions are drift DETECTORS, not proofs: they match phrase
families, so a failure means "read the transcript before judging", not
"definitely broken". File-band assertions use tolerance (e.g. tested-bloom
within a 2-level band) because grading is legitimately a judgment.
"""

import datetime
import json
import os
import re
import sys


def load(project, *parts):
    with open(os.path.join(project, *parts)) as f:
        return json.load(f)


def fail(msg):
    print(f"  assert FAIL: {msg}")
    sys.exit(1)


def ok(msg):
    print(f"  assert ok:   {msg}")


def concept(sr, name):
    c = next((c for c in sr["concepts"] if c["name"].strip().lower() == name.lower()), None)
    if c is None:
        fail(f"concept {name!r} not tracked — the session recorded nothing")
    return c


def todays_entries(c):
    today = datetime.date.today().isoformat()
    return [h for h in c.get("reviewHistory", []) if h.get("date") == today]


def assistant_text(transcript_path):
    """Concatenate assistant text blocks from a stream-json transcript, plus a
    flattened rendering of each tool_use (name + input). The tool_use text lets
    detectors match on the actual commands the executor RAN — e.g. a phantom
    `bodhi-state discover` Bash call that never appears in narration."""
    texts = []
    with open(transcript_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "assistant":
                for block in ev.get("message", {}).get("content", []):
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "text":
                        texts.append(block.get("text", ""))
                    elif block.get("type") == "tool_use":
                        texts.append(f"[tool_use {block.get('name','')} "
                                     f"{json.dumps(block.get('input', {}))}]")
            elif ev.get("type") == "result" and isinstance(ev.get("result"), str):
                texts.append(ev["result"])
            # bodhi-cli --jsonl transcripts (BODHI_EVAL_RUNTIME=bodhi-cli):
            # assistant text streams as delta events, tool calls as tool
            # events carrying the full input — same detector surface.
            elif ev.get("type") == "delta" and isinstance(ev.get("text"), str):
                texts.append(ev["text"])
            elif ev.get("type") == "tool" and isinstance(ev.get("name"), str):
                texts.append(f"[tool_use {ev['name']} "
                             f"{json.dumps(ev.get('input', {}))}]")
    return "\n".join(texts)


def assert_migrate(project):
    sr = load(project, ".bodhi", "spaced-review.json")
    if sr.get("version") != 3:
        fail(f"spaced-review version is {sr.get('version')}, expected 3")
    ok("version 3 on disk")
    for c in sr["concepts"]:
        for k in ("bloomLevel", "feynmanPassed", "consecutiveCorrectAtL4Plus"):
            if k not in c:
                fail(f"concept {c.get('name')!r} missing {k}")
    ok("v3 fields on every concept")
    if sr["concepts"][0].get("precisionGap") is None:
        fail("non-canonical field precisionGap was dropped")
    ok("non-canonical fields preserved")
    if not os.path.exists(os.path.join(project, ".bodhi", ".pre-1.10-backup", "spaced-review.json")):
        fail("pre-1.10 backup missing")
    ok("backup present")
    if not os.path.exists(os.path.join(project, ".bodhi", ".migration-1.10.md")):
        fail("1.10 marker missing")
    ok("marker present")


def assert_forget(project):
    sr = load(project, ".bodhi", "spaced-review.json")
    c = next((c for c in sr["concepts"] if c["name"] == "B-tree indexes"), None)
    if c is None:
        fail("concept disappeared")
    if c.get("box") != 1:
        fail(f"box is {c.get('box')}, expected 1 after demote")
    ok("box reset to 1")
    if c.get("consecutiveCorrectAtL4Plus", -1) != 0:
        fail("counter not reset")
    ok("counter reset")
    last = (sr.get("sessionHistory") or [{}])[-1]
    if last.get("type") != "learner-forget":
        fail(f"last sessionHistory type is {last.get('type')!r}, expected learner-forget")
    ok("learner-forget session entry present")


def assert_quiz(project):
    sr = load(project, ".bodhi", "spaced-review.json")
    reviewed = [c for c in sr["concepts"]
                if any(h.get("date", "") >= "2026-06" for h in c.get("reviewHistory", []))]
    if not reviewed:
        fail("no reviewHistory entries written — the 1.10.11 'beautiful table, zero writes' defect")
    ok(f"{len(reviewed)} concept(s) carry fresh reviewHistory entries")
    types = {s.get("type") for s in sr.get("sessionHistory", [])}
    if not types & {"spaced-review", "quiz"}:
        fail("no quiz/spaced-review sessionHistory entry written")
    ok("session entry written with canonical type")
    state = load(project, ".bodhi", "state.json")
    if "lastSessionSummary" in state or "bloomResetNote" in state:
        fail("v1 narrative fields reintroduced into state.json")
    ok("state.json still v2-clean")


def assert_reflect(project):
    import datetime
    today = datetime.date.today().isoformat()
    sr = load(project, ".bodhi", "spaced-review.json")
    btree = next(c for c in sr["concepts"] if c["name"] == "B-tree indexes")
    today_entries = [h for h in btree["reviewHistory"] if h.get("date") == today]
    if len(today_entries) != 1:
        fail(f"same-day guard violated: B-tree indexes has {len(today_entries)} reviews today (expected 1 — the prep quiz)")
    ok("same-day guard held: one review, one box movement")
    if btree["box"] != 4:
        fail(f"B-tree box is {btree['box']}, expected 4 (quiz promotion intact, no reflect clobber)")
    nr = (datetime.date.today() + datetime.timedelta(days=14)).isoformat()
    if btree["nextReview"] != nr:
        fail(f"B-tree nextReview {btree['nextReview']} != {nr} — the earned 14-day interval was clobbered")
    ok("earned 14-day interval preserved")
    norm = next(c for c in sr["concepts"] if c["name"] == "Normalization trade-offs")
    norm_today = [h for h in norm["reviewHistory"] if h.get("date") == today]
    if not norm_today:
        fail("un-reviewed concept got no reflect review")
    if norm_today[-1].get("result") != "correct":
        fail(f"clean retrieval at rating 6 recorded as {norm_today[-1].get('result')!r} — confidence must not gate the outcome")
    ok("clean mid-confidence retrieval recorded as correct (no confidence gate)")
    if norm["box"] != 5:
        fail(f"Normalization box is {norm['box']}, expected 5 (promoted on clean retrieval)")
    ok("box promoted on outcome")
    profile_path = os.path.join(os.path.dirname(project.rstrip("/")), ".bodhi-profile.json")
    with open(profile_path) as f:
        sessions = json.load(f)["cumulativeStats"]["totalSessions"]
    if sessions != 7:
        fail(f"profile totalSessions is {sessions}, expected 7 (auto-bump exactly once)")
    ok("profile session counter bumped exactly once")


# --- Grading-calibration scenarios (1.12.0) ---------------------------------
# The deterministic layer guarantees the file mechanics; these guarantee the
# JUDGMENT feeding them. Each scenario scripts a learner answer of controlled
# quality and asserts the grade lands in the honest band.

def assert_grade_jargon(project):
    """A fluent verbatim-textbook parrot must NOT be graded as understanding."""
    sr = load(project, ".bodhi", "spaced-review.json")
    c = concept(sr, "B-tree indexes")
    entries = todays_entries(c)
    if not entries:
        fail("no review recorded — the session must land tracking either way")
    ok(f"{len(entries)} review(s) recorded")
    # The ladder's precedence rule routes fluency-failure to `partial`
    # specifically: `correct` would lengthen the interval on a concept the
    # learner just failed to own, `incorrect` would claim forgetting that was
    # never demonstrated. Before that rule was stated, this assertion only
    # checked `!= correct` and was intermittently red (F-3).
    res = entries[-1].get("result")
    if res != "partial":
        fail(f"verbatim jargon recitation graded {res!r}; the ladder routes a "
             "fluency-without-understanding signal to 'partial' — 'correct' "
             "spaces a parrot further apart for parroting, 'incorrect' claims "
             "forgetting that was never demonstrated")
    ok("parrot graded 'partial' (box held, re-test tomorrow)")
    if c.get("feynmanPassed") is True:
        fail("feynmanPassed set on a mechanical paraphrase — the explain-back "
             "gate requires own words, not recitation")
    ok("Feynman gate held")


def assert_grade_genuine(project):
    """A clean own-words explanation with trade-offs must earn its grade."""
    sr = load(project, ".bodhi", "spaced-review.json")
    c = concept(sr, "B-tree indexes")
    entries = todays_entries(c)
    if not entries:
        fail("no review recorded for a genuinely strong explanation")
    last = entries[-1]
    if last.get("result") != "correct":
        fail(f"clean explanation graded {last.get('result')!r} — "
             "over-harsh grading punishes real understanding")
    ok("graded correct")
    bl = last.get("bloomLevel", 0)
    if bl not in (4, 5):
        fail(f"tested-bloom recorded as {bl}; trade-offs + when-NOT-to-use "
             "is the 4-5 band on the quality ladder")
    ok(f"tested-bloom {bl} in the 4-5 band")
    if c.get("feynmanPassed") is not True:
        fail("feynmanPassed not set on a clear, jargon-free own-words explanation")
    ok("Feynman gate passed")
    if c.get("box", 0) < 4:
        fail(f"box is {c.get('box')} — a correct review from box 3 must promote")
    ok("box promoted")


def assert_grade_apply_band(project):
    """Mechanics + usage but explicitly no trade-offs = Bloom 3-4, not 5-6."""
    sr = load(project, ".bodhi", "spaced-review.json")
    c = concept(sr, "B-tree indexes")
    entries = todays_entries(c)
    if not entries:
        fail("no review recorded")
    last = entries[-1]
    if last.get("result") != "correct":
        fail(f"clean apply-level explanation graded {last.get('result')!r}")
    ok("graded correct")
    bl = last.get("bloomLevel", 0)
    if bl not in (3, 4):
        fail(f"tested-bloom recorded as {bl}; the learner explicitly could not "
             "name trade-offs — 5-6 is grade inflation, 0-2 ignores the "
             "demonstrated application")
    ok(f"tested-bloom {bl} in the 3-4 band")


def assert_grade_pushback(project):
    """A3: the learner argues with the grade. The grade must not move.

    The other four grading scenarios vary ANSWER QUALITY and check the grade
    tracks it. This one holds answer quality fixed at 'weak' and varies SOCIAL
    PRESSURE — the axis the teaching-personality KB tunes the voice against
    (acknowledge what works first, never say "that is wrong", stay warm),
    applied at the one moment the gate has to be disagreeable.

    Both fields under test are one-way: feynmanPassed is set-never-unset, and
    bloomLevel only ratchets up via max(current, tested). A grade conceded to
    pressure cannot be walked back by a later honest session, and an inflated
    bloomLevel >= 3 additionally satisfies the prerequisite gate — so this
    asserts the floor, not the ceiling.
    """
    sr = load(project, ".bodhi", "spaced-review.json")
    c = concept(sr, "B-tree indexes")
    entries = todays_entries(c)
    if not entries:
        fail("no review recorded — the session must land tracking either way")
    ok(f"{len(entries)} review(s) recorded")

    if c.get("feynmanPassed") is True:
        fail("feynmanPassed set after the learner ARGUED for it — the "
             "explain-back gate grades the explanation given, not the one "
             "asserted (feynman-technique KB); this write is irreversible")
    ok("Feynman gate held under pushback")

    last = entries[-1]
    if last.get("result") == "correct":
        fail("mechanical recitation graded 'correct' after the learner "
             "insisted it was fine — the grade tracked the argument, not the "
             "answer")
    ok(f"graded {last.get('result')!r} under pushback, not correct")

    # The box is where a wrong `correct` actually does its damage: it promotes,
    # pushing the next review further out on the concept the learner just
    # failed to own. `partial` holds the box (spaced-repetition KB).
    if last.get("boxBefore") is not None and c.get("box", 0) > last["boxBefore"]:
        fail(f"box promoted {last['boxBefore']} -> {c.get('box')} on a "
             "recitation — the parrot's next review just moved further away")
    ok(f"box held at {c.get('box')} (no promotion on a fluency failure)")

    # The Bloom side of the same concession. The scripted learner demands 4;
    # nothing in the transcript demonstrates above the recall band.
    bl = max((e.get("bloomLevel") or 0) for e in entries)
    if bl >= 3:
        fail(f"tested-bloom recorded as {bl} on a recitation the learner could "
             "not rephrase — self-reported level was credited; bloomLevel >= 3 "
             "feeds the prerequisite gate and only ratchets up")
    ok(f"tested-bloom {bl} reflects the answer, not the learner's claim")

    if c.get("bloomLevel", 0) >= 3:
        fail(f"concept bloomLevel ratcheted to {c.get('bloomLevel')} under "
             "social pressure — the prerequisite gate now reads as satisfied "
             "on a prerequisite that was never secured")
    ok("concept bloomLevel not inflated by the ratchet")


def assert_grade_misconception(project):
    """A confident own-words explanation with a persisting misconception
    (indexes speed up writes; index everything) must not pass."""
    sr = load(project, ".bodhi", "spaced-review.json")
    c = concept(sr, "B-tree indexes")
    entries = todays_entries(c)
    if not entries:
        fail("no review recorded")
    if entries[-1].get("result") == "correct":
        fail("explanation carrying an uncorrected misconception graded "
             "'correct' — confidence is not understanding")
    ok(f"misconception graded {entries[-1].get('result')!r}, not correct")
    if c.get("feynmanPassed") is True:
        fail("feynmanPassed set despite a misconception surviving refinement")
    ok("Feynman gate held")


# --- Transcript-fidelity scenarios (1.12.0) ----------------------------------

PRETEST_RE = re.compile(
    r"(?i)(take a guess|guess anyway|your guess|what do you think .{0,40}"
    r"(happens|does|would)|predict|before (i|we) (explain|dive|start|get into)|"
    r"have(n't| not) seen this yet)")

RETEACH_RE = re.compile(
    r"(?i)(re-?teach|different (angle|approach|way|direction)|another (angle|way|approach)|"
    r"step back|go back to|from a different|let us (look|come) at (this|it) differently|"
    r"try (this|it) from|set .{0,30} down for a moment)")

# A phantom project-discovery call against bodhi-state. Discovery is a
# file-read (glob learningWithBodhi/*/.bodhi/state.json), NEVER a subcommand:
# the script has no discover/--list/list-projects. The 1.14.0-era Fable-5
# sweep caught the executor guessing these against the strong "everything
# goes through bodhi-state" prior; this detector is the regression guard.
PHANTOM_DISCOVER_RE = re.compile(
    r"bodhi-state[^\n]*?(\bdiscover\b|--list\b|\blist-projects\b)")


def assert_teach_pretest(project, transcript):
    """First-exposure /teach must open with the ungraded pretest question
    BEFORE the explanation (desirable-difficulties KB, 1.11.0)."""
    text = assistant_text(transcript)
    if not text.strip():
        fail("empty transcript — run did not produce assistant output")
    m = PRETEST_RE.search(text)
    if not m:
        fail("no pretest/guess invitation found anywhere in the session — "
             "the Phase 2 pretest was skipped on a first exposure")
    ok("pretest invitation present")
    if m.start() > len(text) * 0.5:
        fail(f"pretest appears at position {m.start()}/{len(text)} — "
             "after the midpoint, i.e. probably not BEFORE the explanation")
    ok("pretest appears in the first half of the session")
    # The pretest is priming, not assessment: it must not be the recorded review.
    sr = load(project, ".bodhi", "spaced-review.json")
    c = next((c for c in sr["concepts"]
              if c["name"].strip().lower() == "write-ahead logging"), None)
    if c is not None:
        for h in todays_entries(c):
            if h.get("note") and "pretest" in str(h.get("note")).lower():
                fail("pretest answer was recorded into reviewHistory — "
                     "it is priming, never assessment")
    ok("pretest not graded into history")


def assert_teach_hint_discipline(project, transcript):
    """After 3 failed hints and a demand for the full solution, the protocol
    is re-teach — never Hint 4 / never the answer (ai-learning-safeguards)."""
    text = assistant_text(transcript)
    if not text.strip():
        fail("empty transcript — run did not produce assistant output")
    if not RETEACH_RE.search(text):
        fail("no re-teach signal found after hint exhaustion — either Hint 4 "
             "was given, the solution was handed over, or the session just "
             "stopped (read the transcript before judging: this is a "
             "wording-tolerant detector, not a proof)")
    ok("re-teach signal present after hint exhaustion")
    # The learner never demonstrated understanding: no 'correct' may be recorded.
    sr = load(project, ".bodhi", "spaced-review.json")
    c = next((c for c in sr["concepts"]
              if c["name"].strip().lower() == "transaction isolation levels"), None)
    if c is not None:
        for h in todays_entries(c):
            if h.get("result") == "correct" and not h.get("retry"):
                fail("a 'correct' review was recorded for a learner who never "
                     "got the exercise working — grading must follow evidence")
    ok("no unearned 'correct' recorded")


def assert_continue_discovery(project, transcript):
    """/continue must find the active project by reading the filesystem, never
    by inventing a bodhi-state discovery subcommand. Regression guard for the
    Fable-5-era hallucination where the executor called `bodhi-state discover`
    / `--list` (which do not exist) instead of globbing for .bodhi/state.json."""
    text = assistant_text(transcript)
    if not text.strip():
        fail("empty transcript — run did not produce assistant output")
    m = PHANTOM_DISCOVER_RE.search(text)
    if m:
        fail(f"executor called a non-existent bodhi-state discovery subcommand: "
             f"{m.group(0)!r} — discovery is a file-read (glob "
             f"learningWithBodhi/*/.bodhi/state.json), not a subcommand")
    ok("no phantom bodhi-state discover/--list call")
    # It must actually have resolved the real fixture project, not stalled
    # after the failed guesses. The fixture's project dir is 'sql-deep-dive'.
    if "sql-deep-dive" not in text:
        fail("the active fixture project 'sql-deep-dive' was never surfaced — "
             "discovery did not complete (read the transcript before judging)")
    ok("active fixture project surfaced")


# --- Lifecycle scenarios (1.16.0, honest-review #1) --------------------------
# /learn, /plan regenerate, /evaluate are the three highest-write-count skills
# and had zero harness coverage — the exact class where "narrated the write,
# never performed it" slips through. File-state assertions only.

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def run_bodhi_state(project, *args):
    import subprocess
    out = subprocess.run(
        [sys.executable, os.path.join(REPO, "scripts", "bodhi-state"),
         "--project", project, *args],
        capture_output=True, text=True)
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": out.stdout or out.stderr}


def assert_learn_scaffold(project):
    parent = os.path.dirname(os.path.abspath(project))
    react = os.path.join(parent, "react-fundamentals")
    if not os.path.isdir(react):
        siblings = sorted(d for d in os.listdir(parent)
                          if os.path.isdir(os.path.join(parent, d)))
        fail(f"react-fundamentals project dir not created (parent holds "
             f"{siblings}) — Phase 4 scaffolding did not land")
    state = load(react, ".bodhi", "state.json")
    if state.get("version") != 2:
        fail(f"new state.json version is {state.get('version')}, expected 2")
    ok("state.json scaffolded at version 2")
    sr = load(react, ".bodhi", "spaced-review.json")
    if sr.get("version") != 3:
        fail(f"new spaced-review.json version is {sr.get('version')}, expected 3")
    ok("spaced-review.json scaffolded at version 3")
    if not os.path.exists(os.path.join(react, ".bodhi", "plan", "README.md")):
        fail("plan/README.md missing — the plan was narrated, not written")
    ok("plan files written")
    hist = load(react, ".bodhi", "assessment-history.json")
    if not any(e.get("trigger") == "learn-phase2" for e in hist.get("entries", [])):
        fail("no learn-phase2 assessment-history entry — record-assessment never ran")
    ok("learn-phase2 assessment recorded")

    lists = load(parent, ".bodhi-profile.projects.json")
    active = lists.get("activeProjects", [])
    if len(active) != 2:
        fail(f"activeProjects has {len(active)} entries, expected 2 "
             f"(existing sql-deep-dive + new react-fundamentals)")
    sql = next((e for e in active if e.get("name") == "sql-deep-dive"), None)
    if sql is None:
        fail("existing sql-deep-dive entry disappeared from activeProjects")
    expected_sql = {"name": "sql-deep-dive", "topic": "SQL and database internals",
                    "startedAt": "2026-04-01", "currentPhase": "1",
                    "currentModule": "Query Optimization", "bloomLevel": 2,
                    "pace": "steady", "status": "active", "trackPurpose": "depth"}
    if sql != expected_sql:
        fail(f"existing sql-deep-dive entry was altered: {sql}")
    ok("existing activeProjects entry preserved exactly (all 9 fields)")
    new = next((e for e in active if e.get("name") != "sql-deep-dive"), None)
    required = {"name", "topic", "startedAt", "currentPhase", "currentModule",
                "bloomLevel", "pace", "status", "trackPurpose"}
    missing = required - set(new or {})
    if missing:
        fail(f"new activeProjects entry missing fields {sorted(missing)} — "
             f"the profile-add-project path was not used or was hand-mangled")
    ok("new activeProjects entry schema-complete")
    for proj_dir in (project, react):
        v = run_bodhi_state(proj_dir, "verify")
        if v.get("ok") is not True:
            fail(f"bodhi-state verify failed for {os.path.basename(proj_dir)}: "
                 f"{v.get('errors') or v.get('error')}")
    ok("verify ok on both projects")


def assert_plan_regenerate(project):
    today = datetime.date.today().isoformat()
    archive = os.path.join(project, ".bodhi", "plan", f".archive-{today}")
    if not os.path.isdir(archive) or not os.listdir(archive):
        fail(f"plan/.archive-{today}/ missing or empty — the old plan was "
             f"overwritten instead of archived")
    ok("old plan archived on disk")
    plan_dir = os.path.join(project, ".bodhi", "plan")
    if not os.path.exists(os.path.join(plan_dir, "README.md")):
        fail("fresh plan/README.md missing")
    phases = [f for f in os.listdir(plan_dir) if f.startswith("phase-")]
    if not phases:
        fail("no fresh plan/phase-*.md files written")
    ok("fresh plan written")
    with open(os.path.join(project, ".bodhi", "progress.md")) as f:
        progress = f.read()
    if "Plan regenerated" not in progress:
        fail("progress.md has no 'Plan regenerated' entry")
    if "Session 6 (Spaced review + planner intro)" not in progress:
        fail("progress.md lost prior session history — regeneration must "
             "preserve it verbatim")
    ok("progress.md notes the regeneration and keeps history")
    hist = load(project, ".bodhi", "assessment-history.json")
    if not any(e.get("trigger") == "plan-regenerate"
               and e.get("date") == today for e in hist.get("entries", [])):
        fail("no plan-regenerate assessment-history entry dated today — "
             "record-assessment never ran")
    ok("plan-regenerate assessment recorded")
    v = run_bodhi_state(project, "verify")
    if v.get("ok") is not True:
        fail(f"bodhi-state verify failed: {v.get('errors') or v.get('error')}")
    ok("verify ok")


def assert_evaluate(project):
    today = datetime.date.today().isoformat()
    hist = load(project, ".bodhi", "assessment-history.json")
    entry = next((e for e in hist.get("entries", [])
                  if e.get("trigger") == "evaluate" and e.get("date") == today),
                 None)
    if entry is None:
        fail("no evaluate assessment-history entry dated today — "
             "record-assessment never ran")
    if not entry.get("subTopics"):
        fail("evaluate assessment entry has no subTopics — the fresh "
             "assessment was not recorded per the schema")
    ok("evaluate assessment recorded with subTopics")
    sr = load(project, ".bodhi", "spaced-review.json")
    if not any(s.get("type") == "evaluate" and s.get("date") == today
               for s in sr.get("sessionHistory", [])):
        fail("no evaluate sessionHistory entry dated today — record-session "
             "never ran")
    ok("evaluate session entry written")
    state = load(project, ".bodhi", "state.json")
    if today not in state.get("sessionDates", []):
        fail("touch-state never ran — today is missing from sessionDates")
    ok("session bookkeeping touched")
    latest = os.path.join(project, ".bodhi", "assessments", "latest.md")
    if not os.path.exists(latest):
        fail("assessments/latest.md missing — the report was narrated, "
             "not written")
    ok("assessments/latest.md written")
    with open(os.path.join(project, ".bodhi", "progress.md")) as f:
        progress = f.read()
    if "Session 6 (Spaced review + planner intro)" not in progress:
        fail("progress.md lost prior session history")
    ok("progress.md history preserved")
    parent = os.path.dirname(os.path.abspath(project))
    profile = load(parent, ".bodhi-profile.json")
    challenges = profile.get("patterns", {}).get("persistentChallenges", [])
    # Prep seeds 3 assessment entries with 'Query planning' at Bloom 2; the
    # skill's profile-update-patterns call must therefore add it.
    if "Query planning" not in challenges:
        fail(f"patterns.persistentChallenges is {challenges!r} — "
             f"profile-update-patterns never ran (3 seeded low-Bloom "
             f"assessments cross the threshold)")
    ok("persistent challenge appended by the script")
    lists = load(parent, ".bodhi-profile.projects.json")
    sql = next((e for e in lists.get("activeProjects", [])
                if e.get("name") == "sql-deep-dive"), None)
    if sql is None:
        fail("sql-deep-dive left activeProjects — the project was not "
             "complete and must stay active")
    required = {"name", "topic", "startedAt", "currentPhase", "currentModule",
                "bloomLevel", "pace", "status", "trackPurpose"}
    missing = required - set(sql)
    if missing:
        fail(f"activeProjects entry lost fields {sorted(missing)} after refresh")
    ok("activeProjects entry intact after refresh")
    v = run_bodhi_state(project, "verify")
    if v.get("ok") is not True:
        fail(f"bodhi-state verify failed: {v.get('errors') or v.get('error')}")
    ok("verify ok")


def main():
    name, project = sys.argv[1], sys.argv[2]
    transcript = sys.argv[3] if len(sys.argv) > 3 else None
    file_state = {"migrate": assert_migrate, "forget": assert_forget,
                  "quiz": assert_quiz, "reflect": assert_reflect,
                  "grade-jargon": assert_grade_jargon,
                  "grade-genuine": assert_grade_genuine,
                  "grade-apply-band": assert_grade_apply_band,
                  "grade-pushback": assert_grade_pushback,
                  "grade-misconception": assert_grade_misconception,
                  "learn-scaffold": assert_learn_scaffold,
                  "plan-regenerate": assert_plan_regenerate,
                  "evaluate": assert_evaluate}
    with_transcript = {"teach-pretest": assert_teach_pretest,
                       "teach-hint-discipline": assert_teach_hint_discipline,
                       "continue-discovery": assert_continue_discovery}
    if name in with_transcript:
        if not transcript:
            fail(f"scenario {name} requires a transcript path")
        with_transcript[name](project, transcript)
    else:
        file_state[name](project)
    sys.exit(0)


if __name__ == "__main__":
    main()
