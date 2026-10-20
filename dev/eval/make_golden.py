#!/usr/bin/env python3
"""Golden baseline: what the 1.24.1 engine does on code projects.

learn-anything/REQ-1: a concept whose evidence kind is `code` is taught,
graded, scheduled and tracked exactly as release 1.24.1 does.
learn-anything/REQ-3: a project with no recorded kind is `code`.

CASES below is a fixed script of reader and writer calls over four code
projects, none of which records a kind. Running

    python3 dev/eval/make_golden.py

replays it with `bodhi-state` as released in 1.24.1 (`git show
cfe290b:scripts/bodhi-state`) and saves, per case, every call's exit code
and output and every file the calls left behind, under dev/eval/golden/.
`t_golden_code_path` in test_bodhi_state.py replays the same script on the
current engine and compares: reader JSON equal apart from the keys its
GOLDEN_NEW_KEYS allows, writer output and every file byte for byte.

The one thing masked is the time of day the engine stamps with the wall
clock (`now_iso()`: lastReviewCheck, lastSessionAt, lastUpdated).
BODHI_TODAY pins the date, not the time, and 1.24.1 has no way to pin it.

Rebuild the baseline only on purpose: a changed golden file is a change to
how code is tracked.
"""

import datetime
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
GOLDEN = os.path.join(HERE, "golden")
INPUTS = os.path.join(GOLDEN, "inputs")
FIXTURES = os.path.join(HERE, "fixtures")
SOURCE_REF = "cfe290b"  # release: 1.24.1

# Subcommands whose output is a read of the files, not a write report. A later
# release may add keys to these (GOLDEN_NEW_KEYS); writer output may not change.
READERS = {"due", "mastery", "calibration", "retention", "export-anonymized",
           "session-brief", "snapshot", "syllabus", "revision-brief",
           "gate-check", "verify"}

STAMP_RE = re.compile(r'("(?:lastReviewCheck|lastSessionAt|lastUpdated)": ")'
                      r'(\d{4}-\d{2}-\d{2})T\d{2}:\d{2}:\d{2}"')

ALL_READS = [["verify"], ["due"], ["snapshot"], ["mastery"], ["syllabus"],
             ["gate-check"], ["revision-brief"], ["retention"], ["calibration"],
             ["export-anonymized"]]


def at(day, calls):
    return [(day, *argv) for argv in calls]


def briefs(*concepts):
    return [["session-brief", "--concept", c] for c in concepts]


SQL = ["Query planning", "B-tree indexes", "Normalization trade-offs"]
RICH = ["Closures", "Recursion", "Iterators", "Generators", "Decorators",
        "Descriptors", "Metaclasses", "Protocols"]

# The current module has graded reviews, so its gate does not fire; these gate
# a module nothing has been reviewed in, which is where verdicts are computed.
RICH_GATES = [
    ["gate-check", "--module", "Threads and the GIL", "--prereqs", ", ".join(RICH)],
    ["gate-check", "--module", "Threads and the GIL", "--prior-module", "Collections"],
    ["gate-check", "--module", "Threads and the GIL", "--prior-module", "Functions"],
    ["gate-check", "--module", "Packaging"],
]

CASES = [
    {   # The v2 SQL eval fixture: legacy levels, migration, every writer.
        "name": "sql-deep-dive", "project": "sql-deep-dive",
        "steps": (
            at("2026-05-21", ALL_READS + briefs(*SQL) + [
                ["gate-check", "--prereqs", "B-tree indexes, Query planning"],
                ["migrate-spaced-review"],
                ["migrate-spaced-review"],
                ["record-review", "--concept", "Query planning", "--result", "correct",
                 "--tested-bloom", "3", "--confidence", "sure", "--source", "quiz"],
                ["record-review", "--concept", "B-tree indexes", "--result", "partial",
                 "--tested-bloom", "2", "--source", "teach", "--note", "mixed up leaf pages"],
                ["record-review", "--concept", "Normalization trade-offs", "--result",
                 "incorrect", "--tested-bloom", "2", "--confidence", "guessing",
                 "--source", "reflect"],
                ["record-review", "--concept", "Normalization trade-offs", "--result",
                 "correct", "--retry", "--source", "reflect"],
                ["add-concept", "--concept", "EXPLAIN plans", "--module",
                 "Query Optimization", "--question", "What does a seq scan cost?",
                 "--bloom", "2"],
                ["touch-state", "--activity", "Read an EXPLAIN plan", "--module",
                 "Query Optimization", "--module-index", "2", "--phase", "1",
                 "--completion", "40"],
                ["record-session", "--type", "spaced-review", "--data",
                 '{"conceptsReviewed": 2, "passes": 1, "misses": 1}'],
                ["record-session", "--type", "other"],
                ["record-session", "--type", "review-ish"],
                ["record-review", "--concept", "Hash joins", "--result", "correct"],
                ["set-feynman", "--concept", "Query planning"],
                ["forget", "--concept", "B-tree indexes", "--note", "felt shaky"],
                ["defer", "--concept", "EXPLAIN plans", "--days", "2", "--note", "ran out"],
                ["park", "--concept", "Normalization trade-offs"],
                ["park", "--concept", "Normalization trade-offs", "--resume"],
                ["bump-profile", "--counter", "totalExercises"],
                ["record-assessment", "--trigger", "assess", "--data",
                 '{"topic": "sql", "subTopics": [{"name": "joins", "bloomLevel": 2}, '
                 '{"name": "indexes", "bloomLevel": 4}]}'],
                ["record-assessment", "--trigger", "evaluate", "--data",
                 '{"topic": "sql", "subTopics": [{"name": "joins", "bloomLevel": 2}, '
                 '{"name": "indexes", "bloomLevel": 5}]}'],
                ["record-assessment", "--trigger", "plan-regenerate", "--data",
                 '{"topic": "sql", "subTopics": [{"name": "joins", "bloomLevel": 1}, '
                 '{"name": "indexes", "bloomLevel": 4}]}'],
                ["profile-update-patterns"],
                ["profile-update-project", "--name", "sql-deep-dive", "--module",
                 "Query Optimization", "--bloom", "3"],
                ["normalize"],
            ] + ALL_READS + briefs(*SQL, "EXPLAIN plans"))
            + at("2026-05-24", [
                ["record-review", "--concept", "Query planning", "--result", "correct",
                 "--tested-bloom", "4", "--applied", "--confidence", "mostly",
                 "--source", "practice"],
                ["record-review", "--concept", "EXPLAIN plans", "--result", "correct",
                 "--tested-bloom", "3", "--applied", "--source", "pair"],
                ["touch-state", "--activity", "Built an index for a slow query"],
            ] + ALL_READS + briefs("Query planning", "EXPLAIN plans")
                + [["gate-check", "--prereqs", "B-tree indexes, Query planning"]])
            + at("2026-06-30", [["due", "--limit", "1"], ["snapshot"], ["mastery"],
                                ["retention"], ["verify"]])
        ),
    },
    {   # The political-theory eval fixture as it is: no kind recorded, so code.
        "name": "political-theory", "project": "political-theory",
        "steps": (
            at("2026-10-09", ALL_READS + briefs("Descriptive and normative claims",
                                               "Premises and conclusions") + [
                ["record-review", "--concept", "Descriptive and normative claims",
                 "--result", "correct", "--tested-bloom", "3", "--applied",
                 "--source", "practice", "--confidence", "sure"],
                ["record-review", "--concept", "Premises and conclusions", "--result",
                 "partial", "--tested-bloom", "1", "--source", "teach"],
                ["set-feynman", "--concept", "Descriptive and normative claims"],
                ["touch-state", "--activity", "Applied the is/ought split to a new case"],
                ["record-session", "--type", "quiz", "--data", '{"conceptsReviewed": 1}'],
                ["profile-add-project", "--name", "ethics-primer", "--topic", "Ethics",
                 "--bloom", "1", "--track-purpose", "breadth"],
                ["profile-complete-project", "--name", "ethics-primer", "--final-bloom", "2"],
            ] + ALL_READS + briefs("Descriptive and normative claims") + [
                ["gate-check", "--module", "Justice", "--prior-module",
                 "Claims, reasons, and facts versus values"],
                ["gate-check", "--module", "Justice", "--prereqs",
                 "Descriptive and normative claims, Premises and conclusions"],
            ])
            + at("2026-10-12", [
                ["record-review", "--concept", "Descriptive and normative claims",
                 "--result", "correct", "--tested-bloom", "4", "--source", "quiz"],
            ] + ALL_READS)
        ),
    },
    {   # A synthetic v3 code project with every evidence path on record: a Solid
        # concept, one blocked on applied work, a full history the next review
        # cuts into the archive, an archived summary, and each exposure.
        "name": "rich-code", "project": "rich",
        "steps": (
            at("2026-04-10", ALL_READS + briefs(*RICH) + RICH_GATES + [
                ["record-review", "--concept", "Iterators", "--result", "correct",
                 "--tested-bloom", "4", "--applied", "--source", "practice"],
                ["record-review", "--concept", "Closures", "--result", "correct",
                 "--tested-bloom", "5", "--confidence", "sure", "--source", "quiz"],
                ["record-review", "--concept", "Recursion", "--result", "correct",
                 "--tested-bloom", "4", "--applied", "--source", "pair"],
                ["forget", "--concepts", "Generators, Protocols"],
                ["record-review", "--concept", "Generators", "--result", "correct",
                 "--retry", "--source", "quiz"],
                ["record-review", "--concept", "Decorators", "--result", "correct",
                 "--tested-bloom", "3", "--source", "teach"],
                ["record-review", "--concept", "Descriptors", "--result", "incorrect",
                 "--tested-bloom", "2", "--confidence", "sure", "--source", "quiz"],
                ["park", "--concept", "Metaclasses"],
                ["defer", "--concept", "Descriptors", "--days", "3"],
                ["add-concept", "--concept", "Slots", "--module", "Metaprogramming"],
                ["record-review", "--concept", "Class decorators", "--module",
                 "Metaprogramming", "--result", "correct", "--tested-bloom", "2",
                 "--source", "teach", "--question", "When does a class decorator run?"],
                ["touch-state", "--module", "Metaprogramming", "--module-index", "2"],
                ["record-session", "--type", "pair", "--data",
                 '{"conceptsReviewed": 3, "notes": "drove the iterator protocol"}'],
                ["record-session", "--type", "other", "--subtype", "probe"],
                ["set-feynman", "--concept", "Recursion"],
            ] + ALL_READS + briefs(*RICH, "Slots", "Class decorators") + RICH_GATES)
            + at("2026-05-15", [["due"], ["snapshot"], ["mastery"], ["retention"],
                                ["export-anonymized"], ["calibration"], ["verify"]]
                 + RICH_GATES)
        ),
    },
    {   # Executor drift from the wild: verify reports it, normalize repairs it.
        "name": "drift", "project": "proj",
        "steps": at("2026-06-10", [["verify"], ["snapshot"], ["due"], ["normalize"],
                                   ["normalize"], ["verify"], ["snapshot"],
                                   ["mastery"]]),
    },
]


def clean(text, ws, days):
    """Make one run's text comparable with another's: the temp workspace path
    becomes <WS>, and a wall-clock stamp on a replayed day loses its time."""
    text = text.replace(ws, "<WS>")
    return STAMP_RE.sub(lambda m: (f'{m.group(1)}{m.group(2)}T<time>"'
                                   if m.group(2) in days else m.group(0)), text)


def replay(script, case):
    """Run one case's calls with `script` on a fresh copy of its input.
    Returns {"steps": [...], "files": {relative path: text}}."""
    with tempfile.TemporaryDirectory() as tmp:
        ws = os.path.join(os.path.realpath(tmp), "ws")
        shutil.copytree(os.path.join(INPUTS, case["name"]), ws)
        project = os.path.join(ws, case["project"])
        days = {on for on, *_ in case["steps"]}
        steps = []
        for on, *argv in case["steps"]:
            r = subprocess.run([sys.executable, script, "--project", project, *argv],
                               capture_output=True, text=True,
                               env=dict(os.environ, BODHI_TODAY=on))
            steps.append({"on": on, "argv": argv, "rc": r.returncode,
                          "stdout": clean(r.stdout, ws, days),
                          "stderr": clean(r.stderr, ws, days)})
        files = {}
        for d, _, names in os.walk(ws):
            for n in names:
                if n.endswith(".lock"):
                    continue
                p = os.path.join(d, n)
                with open(p, encoding="utf-8") as f:
                    files[os.path.relpath(p, ws)] = clean(f.read(), ws, days)
        return {"steps": steps, "files": dict(sorted(files.items()))}


def golden_path(case):
    return os.path.join(GOLDEN, case["name"] + ".json")


# ---- inputs -----------------------------------------------------------------

def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def text(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)


def concept(name, module, box, next_review, last_reviewed, bloom, history,
            **extra):
    return {"name": name, "module": module, "introduced": "2026-01-01", "box": box,
            "nextReview": next_review, "lastReviewed": last_reviewed, "question": "",
            "lastResult": history[-1]["result"] if history else "",
            "bloomLevel": bloom, "feynmanPassed": False,
            "consecutiveCorrectAtL4Plus": 0, "reviewHistory": history, **extra}


def h(date, result, bloom, source, **extra):
    return {"date": date, "result": result, "bloomLevel": bloom, "source": source,
            **extra}


def climb(applied_on=None):
    """A due ladder from box 1 to box 4 at Bloom 4: three due corrects."""
    out = [h("2026-03-01", "correct", 3, "teach", boxBefore=1)]
    for date, box in (("2026-03-02", 1), ("2026-03-05", 2), ("2026-03-12", 3)):
        entry = h(date, "correct", 4, "practice" if date == applied_on else "quiz",
                  boxBefore=box)
        if date == applied_on:
            entry["applied"] = True
        out.append(entry)
    return out


def long_history():
    """100 entries, the history cap: an early miss, then a build, then quizzes.
    The next review moves the miss into archivedSummary."""
    start = datetime.date(2025, 12, 20)
    out = []
    for i in range(100):
        day = (start + datetime.timedelta(days=i)).isoformat()
        if i == 0:
            out.append(h(day, "incorrect", 2, "quiz", boxBefore=2))
        elif i == 1:
            out.append(h(day, "correct", 3, "teach", boxBefore=1, applied=True))
        else:
            out.append(h(day, "correct", 3, "quiz", boxBefore=3))
    return out


def rich_inputs(ws):
    proj = os.path.join(ws, "rich", ".bodhi")
    dump(os.path.join(ws, ".bodhi-profile.json"), {
        "version": 2, "careerGoal": "Python internals for library work",
        "whyLearning": "Golden fixture", "priorExperience": "5 years Python",
        "learningStyle": "hands-on", "overallBloomLevels": {"python": 3},
        "cumulativeStats": {"totalSessions": 14, "totalExercises": 6,
                            "totalConceptsLearned": 4, "totalMilestonesReached": 1,
                            "totalProjects": 1, "teachBacksWritten": 0,
                            "teachBacksPublished": 0},
        "patterns": {"persistentChallenges": [], "consistentStrengths": []},
        "lastUpdated": "2026-04-06T09:00:00"})
    dump(os.path.join(ws, ".bodhi-profile.projects.json"), {
        "version": 2, "activeProjects": [{
            "name": "rich", "topic": "Python internals", "startedAt": "2026-01-01",
            "currentPhase": "1", "currentModule": "Metaprogramming", "bloomLevel": 3,
            "pace": "steady", "status": "active", "trackPurpose": "depth"}],
        "completedProjects": []})
    dump(os.path.join(proj, "state.json"), {
        "version": 2, "projectName": "rich", "topic": "Python internals",
        "createdAt": "2026-01-01T09:00:00", "lastSessionAt": "2026-04-06T09:00:00",
        "totalSessions": 14,
        "sessionDates": ["2026-03-01", "2026-03-02", "2026-03-05", "2026-03-12",
                         "2026-04-05", "2026-04-06"],
        "currentStreak": 2, "currentPhase": "1", "currentModule": "Metaprogramming",
        "currentModuleIndex": 2, "previousModule": "Collections",
        "lastActivity": "Wrote a descriptor that validates types",
        "overallCompletion": 45,
        "initialBloomLevel": {"python": 2}, "currentBloomLevel": {"python": 3}})
    solid = dict(feynmanPassed=True, feynmanPassedAt="2026-03-12",
                 consecutiveCorrectAtL4Plus=3)
    dump(os.path.join(proj, "spaced-review.json"), {
        "version": 3, "lastReviewCheck": "2026-04-06T09:00:00",
        "concepts": [
            concept("Closures", "Functions", 4, "2026-03-26", "2026-03-12", 4,
                    climb(applied_on="2026-03-05"), **solid),
            concept("Recursion", "Functions", 4, "2026-04-20", "2026-03-12", 4,
                    climb(), **solid),
            concept("Iterators", "Collections", 3, "2026-04-10", "2026-03-29", 3,
                    long_history()),
            concept("Generators", "Collections", 3, "2026-03-15", "2026-03-08", 3,
                    [h("2026-03-01", "correct", 3, "quiz", boxBefore=2,
                       confidence="sure"),
                     h("2026-03-08", "correct", 3, "reflect", boxBefore=3)],
                    reviewHistoryArchived=12,
                    archivedSummary={"appliedEvidence": 1, "evidenceAt3Plus": 2,
                                     "through": "2026-02-01", "lastMiss": "2026-01-15",
                                     "exposure": "built"}),
            concept("Context managers", "Collections", 2, "2026-04-11", "2026-04-08", 2,
                    [h("2026-04-08", "correct", 2, "teach", boxBefore=1)]),
            concept("Decorators", "Metaprogramming", 1, "2026-04-02", None, 2, []),
            concept("Descriptors", "Metaprogramming", 1, "2026-03-31", "2026-03-30", 2,
                    [h("2026-03-30", "partial", 2, "quiz", boxBefore=1,
                       confidence="guessing")]),
            concept("Metaclasses", "Metaprogramming", 2, "2026-03-28", "2026-03-25", 3,
                    [h("2026-03-25", "correct", 3, "quiz", boxBefore=1,
                       confidence="mostly")]),
            concept("Protocols", "Typing", 1, "2026-04-02", "2026-04-01", 1,
                    [h("2026-04-01", "incorrect", 1, "quiz", boxBefore=1,
                       confidence="sure")]),
        ],
        "sessionHistory": [
            {"date": "2026-03-12", "type": "practice", "conceptsReviewed": 2},
            {"date": "2026-04-06", "type": "spaced-review", "conceptsReviewed": 3,
             "passes": 2, "misses": 1},
        ]})
    text(os.path.join(proj, "plan", "README.md"),
         "# Learning Plan — Python internals\n\n**Current phase:** 1 (`phase-1.md`)\n"
         "**Pace:** steady\n\n## Phases\n\n- **Phase 1 — Language machinery** → "
         "`phase-1.md`\n- **Phase 2 — Concurrency** → `phase-2.md`\n")
    text(os.path.join(proj, "plan", "phase-1.md"),
         "# Phase 1 — Language machinery\n\n## Modules\n\n"
         "### Module 1.1 — Functions\n**Status:** done\n**Target Bloom's:** Analyze\n"
         "**Concepts:** Closures, Recursion\n\n"
         "### Module 1.2 — Collections\n**Concepts:** Iterators, Generators, "
         "Context managers\n\n**Prerequisites for next module:** Closures, Recursion, "
         "Iterators\n\n"
         "### Module 1.3 — Metaprogramming\n**Target Bloom's:** Apply\n"
         "**Key terms:** descriptor, metaclass\n\n"
         "### Module 1.4 — Packaging\n**Status:** skipped\n")
    text(os.path.join(proj, "plan", "phase-2.md"),
         "# Phase 2 — Concurrency\n\n## Modules\n\n### Module 2 — Threads and the GIL\n"
         "**Target Bloom's:** Understand\n")


def drift_inputs(ws):
    """The drifted shapes t_normalize and t_verify_flags_drift use."""
    proj = os.path.join(ws, "proj", ".bodhi")
    dump(os.path.join(proj, "state.json"), {
        "version": 2, "projectName": "proj", "topic": "testing",
        "createdAt": "2026-06-01", "lastSessionAt": "2026-06-05",
        "session": {"totalSessions": 4,
                    "sessionDates": ["2026-06-05", "2026-06-05", "2026-06-05",
                                     "2026-06-04"],
                    "currentStreak": 1},
        "currentPhase": "1", "currentModule": 2, "currentModuleIndex": 0,
        "previousModule": {"id": "0.3", "name": "Module 0.3",
                           "completedAt": "2026-06-05",
                           "outcomes": "rich narrative that must survive"},
        "lastActivity": {"type": "phase-complete", "name": "Phase 0 assessments",
                         "completed": True, "result": "long narrative " * 30},
        "initialBloomLevels": {"ruby": 0}, "currentBloomLevels": {"ruby": 3},
        "overallCompletion": 5})
    dump(os.path.join(proj, "spaced-review.json"), {
        "version": 3, "lastReviewCheck": None,
        "concepts": [
            {"name": "CSRF tokens", "module": "Module 0", "introduced": "2026-05-01",
             "box": "2", "nextReview": "2026-06-11", "lastReviewed": "2026-06-09",
             "question": "", "lastResult": "skipped", "bloomLevel": "2",
             "feynmanPassed": "false", "consecutiveCorrectAtL4Plus": 0,
             "reviewHistory": [
                 {"date": "2026-06-01", "result": "correct", "bloomLevel": 2},
                 {"date": "2026-06-09", "result": "skipped",
                  "note": "session consumed; rolled +2 days"}]},
        ],
        "sessionHistory": [{"date": "2026-06-09", "type": "phase-0-reteach-partial",
                            "notes": "invented type from the wild"}]})


def write_inputs():
    if os.path.isdir(INPUTS):
        shutil.rmtree(INPUTS)
    keep_out = shutil.ignore_patterns("*.lock")
    shutil.copytree(os.path.join(FIXTURES, "v2-project"),
                    os.path.join(INPUTS, "sql-deep-dive"), ignore=keep_out)
    shutil.copytree(os.path.join(FIXTURES, "non-code-project"),
                    os.path.join(INPUTS, "political-theory"), ignore=keep_out)
    rich_inputs(os.path.join(INPUTS, "rich-code"))
    drift_inputs(os.path.join(INPUTS, "drift"))


def main():
    source = subprocess.run(["git", "-C", REPO, "show", f"{SOURCE_REF}:scripts/bodhi-state"],
                            capture_output=True, check=True).stdout
    write_inputs()
    with tempfile.TemporaryDirectory() as tmp:
        script = os.path.join(tmp, "bodhi-state")
        with open(script, "wb") as f:
            f.write(source)
        os.chmod(script, os.stat(script).st_mode | stat.S_IXUSR)
        for case in CASES:
            out = replay(script, case)
            dump(golden_path(case), {"source": SOURCE_REF, "case": case["name"], **out})
            failed = sum(1 for s in out["steps"] if s["rc"] != 0)
            print(f"{case['name']}: {len(out['steps'])} calls ({failed} exit non-zero), "
                  f"{len(out['files'])} files")


if __name__ == "__main__":
    main()
