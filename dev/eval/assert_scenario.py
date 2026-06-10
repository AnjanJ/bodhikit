#!/usr/bin/env python3
"""File-state assertions for the LLM evals. Usage: assert_scenario.py <name> <project>."""

import json
import os
import sys


def load(project, *parts):
    with open(os.path.join(project, *parts)) as f:
        return json.load(f)


def fail(msg):
    print(f"  assert FAIL: {msg}")
    sys.exit(1)


def ok(msg):
    print(f"  assert ok:   {msg}")


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


def main():
    name, project = sys.argv[1], sys.argv[2]
    {"migrate": assert_migrate, "forget": assert_forget, "quiz": assert_quiz,
     "reflect": assert_reflect}[name](project)
    sys.exit(0)


if __name__ == "__main__":
    main()
