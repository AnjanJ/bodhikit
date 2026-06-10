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


def main():
    name, project = sys.argv[1], sys.argv[2]
    {"migrate": assert_migrate, "forget": assert_forget, "quiz": assert_quiz}[name](project)
    sys.exit(0)


if __name__ == "__main__":
    main()
