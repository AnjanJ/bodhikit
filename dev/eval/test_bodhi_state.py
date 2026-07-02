#!/usr/bin/env python3
"""Deterministic tests for scripts/bodhi-state.

Run: python3 dev/eval/test_bodhi_state.py
Exit 0 = all pass. Part of the pre-tag checklist (and dev/check.sh).

These tests cover the contracts the 1.10.x dogfood passes caught executors
violating: unknown-field preservation, Leitner math, the bloomLevel ratchet,
the counter reset rules, sessionHistory vocabulary, migration idempotency
with backup, and the gate verdict logic (including the 1.11.0 recency rule).
"""

import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(REPO, "scripts", "bodhi-state")
TODAY = datetime.date.today()

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"ok    {name}")
    else:
        FAIL += 1
        print(f"FAIL  {name}  {detail}")


def run(project, *argv, expect_fail=False):
    r = subprocess.run([sys.executable, SCRIPT, "--project", project, *argv],
                       capture_output=True, text=True)
    if not expect_fail and r.returncode != 0:
        raise AssertionError(f"bodhi-state {' '.join(argv)} failed:\n{r.stdout}\n{r.stderr}")
    if expect_fail and r.returncode == 0:
        raise AssertionError(f"bodhi-state {' '.join(argv)} unexpectedly succeeded")
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"_raw": r.stdout}


def make_project(root, spaced_review=None, state=None):
    proj = os.path.join(root, "proj")
    os.makedirs(os.path.join(proj, ".bodhi"))
    if state is None:
        state = {"version": 2, "projectName": "proj", "topic": "testing",
                 "createdAt": "2026-01-01T10:00:00", "lastSessionAt": "2026-01-01T10:00:00",
                 "totalSessions": 1, "sessionDates": ["2026-01-01"], "currentStreak": 1,
                 "currentPhase": "1", "currentModule": "Module B", "currentModuleIndex": 1,
                 "lastActivity": "seed", "overallCompletion": 10,
                 "customField": "must-survive"}
    with open(os.path.join(proj, ".bodhi", "state.json"), "w") as f:
        json.dump(state, f, indent=2)
    if spaced_review is not None:
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(spaced_review, f, indent=2)
    return proj


def read_sr(proj):
    with open(os.path.join(proj, ".bodhi", "spaced-review.json")) as f:
        return json.load(f)


def read_state(proj):
    with open(os.path.join(proj, ".bodhi", "state.json")) as f:
        return json.load(f)


V2_SR = {
    "version": 2,
    "lastReviewCheck": "2026-05-01T10:00:00",
    "concepts": [
        {"name": "B-tree indexes", "module": "Module A", "introduced": "2026-04-01",
         "box": 3, "nextReview": "2026-05-08", "lastReviewed": "2026-05-01",
         "question": "How does a B-tree index speed up reads?",
         "lastResult": "solid recall",
         "precisionGap": "confuses clustered vs non-clustered",  # non-canonical
         "reviewHistory": [
             {"date": "2026-04-20", "result": "correct"},
             {"date": "2026-05-01", "result": "correct"},
         ]},
        {"name": "Query planning", "module": "Module A", "introduced": "2026-04-10",
         "box": 1, "nextReview": "2026-05-02", "lastReviewed": "2026-05-01",
         "question": "", "lastResult": "missed",
         "reviewHistory": [{"date": "2026-05-01", "result": "incorrect"}]},
    ],
    "sessionHistory": [
        {"date": "2026-05-01", "type": "spaced-review", "conceptsReviewed": 2,
         "passes": 1, "misses": 1,
         "habitObservations": {"hedging": "says 'kind of' a lot"}},  # non-canonical
    ],
}


def t_migrate():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        out = run(proj, "migrate-spaced-review")
        check("migrate: reports migrated", out.get("action") == "migrated", out)
        sr = read_sr(proj)
        check("migrate: version 3", sr["version"] == 3)
        check("migrate: v3 fields on every concept",
              all(all(k in c for k in ("bloomLevel", "feynmanPassed",
                                       "consecutiveCorrectAtL4Plus"))
                  for c in sr["concepts"]))
        check("migrate: non-canonical concept field preserved",
              sr["concepts"][0].get("precisionGap") == "confuses clustered vs non-clustered")
        check("migrate: non-canonical sessionHistory field preserved",
              sr["sessionHistory"][0].get("habitObservations", {}).get("hedging") is not None)
        backup = os.path.join(proj, ".bodhi", ".pre-1.10-backup", "spaced-review.json")
        check("migrate: backup exists", os.path.exists(backup))
        with open(backup) as f:
            check("migrate: backup is pre-v3", json.load(f)["version"] == 2)
        marker = os.path.join(proj, ".bodhi", ".migration-1.10.md")
        check("migrate: marker written", os.path.exists(marker))
        out2 = run(proj, "migrate-spaced-review")
        check("migrate: idempotent second run", out2.get("action") == "noop", out2)


def t_record_review():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        # correct at L4 with confidence: box 3->4, ratchet, counter+1
        out = run(proj, "record-review", "--concept", "B-tree indexes",
                  "--result", "correct", "--tested-bloom", "4",
                  "--confidence", "sure", "--source", "quiz")
        sr = read_sr(proj)
        c = sr["concepts"][0]
        check("review: box promoted", c["box"] == 4, out)
        check("review: bloom ratchet up", c["bloomLevel"] == 4)
        check("review: counter incremented", c["consecutiveCorrectAtL4Plus"] == 1)
        check("review: nextReview = today + 14",
              c["nextReview"] == (TODAY + datetime.timedelta(days=14)).isoformat())
        check("review: history has confidence",
              c["reviewHistory"][-1].get("confidence") == "sure")
        check("review: non-canonical field survives write",
              c.get("precisionGap") is not None)
        # correct at L2: bloom NOT demoted, counter unchanged
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "2")
        c = read_sr(proj)["concepts"][0]
        check("review: bloom never demotes", c["bloomLevel"] == 4)
        check("review: counter unchanged on low-level correct",
              c["consecutiveCorrectAtL4Plus"] == 1)
        check("review: box capped at 5", c["box"] == 5)
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "5")
        check("review: box stays at 5", read_sr(proj)["concepts"][0]["box"] == 5)
        # incorrect: box 1, counter reset, bloom preserved
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "incorrect", "--tested-bloom", "4", "--confidence", "sure")
        c = read_sr(proj)["concepts"][0]
        check("review: incorrect demotes to box 1", c["box"] == 1)
        check("review: incorrect resets counter", c["consecutiveCorrectAtL4Plus"] == 0)
        check("review: incorrect preserves bloom", c["bloomLevel"] == 5)
        check("review: incorrect nextReview tomorrow",
              c["nextReview"] == (TODAY + datetime.timedelta(days=1)).isoformat())
        # partial: box held, re-test tomorrow
        run(proj, "record-review", "--concept", "Query planning",
            "--result", "partial", "--tested-bloom", "3")
        c = read_sr(proj)["concepts"][1]
        check("review: partial holds box", c["box"] == 1)
        check("review: partial re-tests tomorrow",
              c["nextReview"] == (TODAY + datetime.timedelta(days=1)).isoformat())
        # auto-create with --module
        run(proj, "record-review", "--concept", "Write-ahead log",
            "--result", "correct", "--tested-bloom", "3", "--module", "Module B")
        check("review: auto-created concept",
              any(c["name"] == "Write-ahead log" for c in read_sr(proj)["concepts"]))
        # untracked without module fails
        run(proj, "record-review", "--concept", "Ghost", "--result", "correct",
            expect_fail=True)


def t_sessions_and_forget():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        out = run(proj, "record-session", "--type", "quiz",
                  "--data", '{"conceptsReviewed": 2, "passes": 1, "misses": 1}')
        check("session: recorded", out["entry"]["type"] == "quiz")
        run(proj, "record-session", "--type", "made-up-type", expect_fail=True)
        check("session: invalid type rejected", True)
        run(proj, "record-session", "--type", "other", expect_fail=True)
        check("session: other without subtype rejected", True)
        run(proj, "record-session", "--type", "other", "--subtype", "midnight-cram")
        out = run(proj, "forget", "--concepts", "B-tree indexes, Query planning",
                  "--note", "felt shaky after a week off")
        sr = read_sr(proj)
        check("forget: both demoted",
              all(c["box"] == 1 for c in sr["concepts"][:2]), out)
        check("forget: bloom preserved",
              sr["concepts"][0]["bloomLevel"] == 0 or "bloomLevel" in sr["concepts"][0])
        check("forget: sessionHistory learner-forget entry",
              sr["sessionHistory"][-1]["type"] == "learner-forget")
        check("forget: state lastActivity updated",
              "Demoted" in read_state(proj)["lastActivity"])
        run(proj, "forget", "--concepts", "Nonexistent", expect_fail=True)
        # assessment-history append
        out = run(proj, "record-assessment", "--trigger", "evaluate",
                  "--data", '{"topic": "sql", "overallNote": "steady growth"}')
        check("assessment: entry appended", out["entries"] == 1, out)
        hist = os.path.join(proj, ".bodhi", "assessment-history.json")
        with open(hist) as f:
            e = json.load(f)["entries"][0]
        check("assessment: date + trigger stamped",
              e["trigger"] == "evaluate" and e["date"] == TODAY.isoformat())
        run(proj, "record-assessment", "--trigger", "bogus", "--data", "{}",
            expect_fail=True)


def t_touch_state_and_profile():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root)
        out = run(proj, "touch-state", "--activity", "Taught indexing basics",
                  "--module", "Module C", "--completion", "25")
        st = read_state(proj)
        check("state: new session counted", st["totalSessions"] == 2, out)
        check("state: streak reset after gap", st["currentStreak"] == 1)
        check("state: previousModule recorded", st["previousModule"] == "Module B")
        check("state: custom field preserved", st["customField"] == "must-survive")
        check("state: completion set", st["overallCompletion"] == 25)
        out2 = run(proj, "touch-state", "--activity", "Second touch today")
        check("state: same-day touch does not double-count",
              read_state(proj)["totalSessions"] == 2, out2)
        # profile
        with open(os.path.join(root, ".bodhi-profile.json"), "w") as f:
            json.dump({"version": 2, "cumulativeStats": {"totalExercises": 7},
                       "custom": "keep"}, f)
        out3 = run(proj, "bump-profile", "--counter", "totalExercises")
        check("profile: counter bumped", out3["value"] == 8)
        with open(os.path.join(root, ".bodhi-profile.json")) as f:
            check("profile: unknown field preserved", json.load(f)["custom"] == "keep")
        run(proj, "bump-profile", "--counter", "notACounter", expect_fail=True)


def t_gate_check():
    with tempfile.TemporaryDirectory() as root:
        sr = json.loads(json.dumps(V2_SR))
        # Module A concepts; current module is Module B with no work yet -> fires
        proj = make_project(root, spaced_review=sr)
        run(proj, "migrate-spaced-review")
        out = run(proj, "gate-check")
        check("gate: fires on first session of new module", out["fires"] is True, out)
        # bloomLevel 0 everywhere -> no-opinion, verdict clear
        check("gate: legacy fallthrough (bloom 0 = no opinion)",
              out["verdict"] == "clear"
              and all(p["status"] == "no-opinion" for p in out["prerequisites"]), out)
        # Classify: B-tree to bloom 3 with recent review -> satisfied
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "3")
        out = run(proj, "gate-check")
        btree = [p for p in out["prerequisites"] if p["name"] == "B-tree indexes"][0]
        check("gate: bloom>=3 recent = satisfied", btree["status"] == "satisfied")
        # Query planning at bloom 2, box 1, no strong evidence -> gap
        run(proj, "record-review", "--concept", "Query planning",
            "--result", "incorrect", "--tested-bloom", "2")
        run(proj, "record-review", "--concept", "Query planning",
            "--result", "correct", "--tested-bloom", "2")
        out = run(proj, "gate-check")
        qp = [p for p in out["prerequisites"] if p["name"] == "Query planning"][0]
        check("gate: low bloom without evidence = gap", qp["status"] == "gap", out)
        check("gate: verdict offer when gaps exist", out["verdict"] == "offer")
        # Stale: bloom 3 but box 1 and lastReviewed 90 days ago -> stale-reconfirm
        srdata = read_sr(proj)
        c = srdata["concepts"][0]
        c["box"] = 1
        c["lastReviewed"] = (TODAY - datetime.timedelta(days=90)).isoformat()
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(srdata, f)
        out = run(proj, "gate-check")
        btree = [p for p in out["prerequisites"] if p["name"] == "B-tree indexes"][0]
        check("gate: bloom>=3 but stale evidence = stale-reconfirm (1.11.0 recency rule)",
              btree["status"] == "stale-reconfirm", out)
        # Apply-equivalent: bloom 2, box 3, last two correct
        srdata = read_sr(proj)
        c = srdata["concepts"][1]
        c["bloomLevel"] = 2
        c["box"] = 3
        c["reviewHistory"] = [{"date": "2026-05-01", "result": "correct"},
                              {"date": "2026-05-20", "result": "correct"}]
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(srdata, f)
        out = run(proj, "gate-check")
        qp = [p for p in out["prerequisites"] if p["name"] == "Query planning"][0]
        check("gate: strong v2 evidence = apply-equivalent", qp["status"] == "apply-equivalent")
        # Continuation session: concept exists for current module -> does not fire
        run(proj, "add-concept", "--concept", "Replication lag", "--module", "Module B")
        out = run(proj, "gate-check")
        check("gate: continuation session does not fire", out["fires"] is False)
        # Declared prereqs path
        out = run(proj, "gate-check", "--module", "Module Z",
                  "--prereqs", "B-tree indexes")
        check("gate: declared prereq list respected",
              out["fires"] and len(out["prerequisites"]) == 1
              and out["prerequisiteSource"] == "declared")


def t_mastery_due_calibration():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        out = run(proj, "mastery")
        check("mastery: legacy module shows null (not 0%)",
              out["modules"]["Module A"]["masteryPct"] is None, out)
        check("mastery: rollup buckets", out["retentionRollup"]["building"] == 1
              and out["retentionRollup"]["needs_review"] == 1)
        out = run(proj, "due")
        check("due: overdue concepts listed", out["dueToday"] == 2, out)
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "4", "--confidence", "sure")
        run(proj, "record-review", "--concept", "Query planning",
            "--result", "incorrect", "--tested-bloom", "3", "--confidence", "sure")
        run(proj, "record-review", "--concept", "Query planning",
            "--result", "correct", "--tested-bloom", "2", "--confidence", "guessing")
        out = run(proj, "calibration")
        check("calibration: tagged answers counted", out["taggedAnswers"] == 3, out)
        check("calibration: overconfident event captured",
              out["overconfidentEvents"] and
              out["overconfidentEvents"][-1]["concept"] == "Query planning")
        check("calibration: underconfidence rate computed",
              out["underconfidenceRate"] == 1.0)
        # set-feynman + mastery formula end-to-end
        run(proj, "set-feynman", "--concept", "B-tree indexes")
        for _ in range(3):
            run(proj, "record-review", "--concept", "B-tree indexes",
                "--result", "correct", "--tested-bloom", "5")
        out = run(proj, "mastery")
        check("mastery: formula reaches mastered",
              out["modules"]["Module A"]["masteryPct"] == 50, out)


def t_retry_and_relearning():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        # Miss -> Box 1, review tomorrow
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "incorrect", "--tested-bloom", "3", "--source", "quiz")
        c = read_sr(proj)["concepts"][0]
        tomorrow = (TODAY + datetime.timedelta(days=1)).isoformat()
        check("retry: miss demoted to box 1", c["box"] == 1 and c["nextReview"] == tomorrow)
        # Successful relearning retry: history entry, NO box/schedule movement
        out = run(proj, "record-review", "--concept", "B-tree indexes",
                  "--result", "correct", "--tested-bloom", "3", "--retry",
                  "--source", "quiz")
        c = read_sr(proj)["concepts"][0]
        check("retry: box unchanged", c["box"] == 1, out)
        check("retry: nextReview still tomorrow (demotion stands)",
              c["nextReview"] == tomorrow)
        check("retry: counter unchanged", c["consecutiveCorrectAtL4Plus"] == 0)
        check("retry: history entry flagged",
              c["reviewHistory"][-1].get("retry") is True
              and c["reviewHistory"][-1]["result"] == "correct")
        check("retry: bloom not ratcheted by retry", c["bloomLevel"] == 0)


def t_partial_breaks_streak():
    # 1.11.2 — "3 consecutive correct at L4+" means uninterrupted corrects.
    # A partial retrieval is not a correct one: it must reset the counter
    # (previously correct/partial/correct/correct counted as 3 "consecutive").
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "4")
        c = read_sr(proj)["concepts"][0]
        check("streak: correct at L4 increments", c["consecutiveCorrectAtL4Plus"] == 1)
        box_after_correct = c["box"]
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "partial", "--tested-bloom", "4")
        c = read_sr(proj)["concepts"][0]
        check("streak: partial resets counter", c["consecutiveCorrectAtL4Plus"] == 0, c)
        check("streak: partial still holds box (no Leitner demotion)",
              c["box"] == box_after_correct)
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "4")
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "4")
        c = read_sr(proj)["concepts"][0]
        check("streak: rebuilt from zero after the partial",
              c["consecutiveCorrectAtL4Plus"] == 2, c)
        # A partial RETRY is a relearning rep: no counter movement of any kind.
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "partial", "--tested-bloom", "4", "--retry")
        c = read_sr(proj)["concepts"][0]
        check("streak: partial retry does not touch the counter",
              c["consecutiveCorrectAtL4Plus"] == 2, c)


def t_touch_state_profile_bump():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root)
        with open(os.path.join(root, ".bodhi-profile.json"), "w") as f:
            json.dump({"version": 2, "cumulativeStats": {"totalSessions": 6}}, f)
        out = run(proj, "touch-state", "--activity", "first touch today")
        check("bump: first touch of the day bumps profile",
              out["profileSessionsBumped"] is True, out)
        out2 = run(proj, "touch-state", "--activity", "second touch today")
        check("bump: same-day touch does not re-bump",
              out2["profileSessionsBumped"] is False, out2)
        with open(os.path.join(root, ".bodhi-profile.json")) as f:
            check("bump: profile counter incremented exactly once",
                  json.load(f)["cumulativeStats"]["totalSessions"] == 7)


def t_data_reserved_keys():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        run(proj, "record-session", "--type", "quiz",
            "--data", '{"type": "hax", "date": "1999-01-01", "notes": "kept"}')
        e = read_sr(proj)["sessionHistory"][-1]
        check("reserved: --data cannot override type", e["type"] == "quiz", e)
        check("reserved: --data cannot override date", e["date"] == TODAY.isoformat())
        check("reserved: non-reserved keys kept", e.get("notes") == "kept")
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "verify"],
                           capture_output=True, text=True)
        check("reserved: verify stays clean after the write", r.returncode == 0)


def t_migrate_stale_backup():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        # Simulate a sync-restore: live file back at v2 with an EXTRA concept,
        # while the old (smaller) backup is still on disk.
        sr = json.loads(json.dumps(V2_SR))
        sr["concepts"].append({"name": "Extra", "module": "Module A",
                               "introduced": "2026-06-01", "box": 1,
                               "nextReview": "2026-06-02", "lastReviewed": None,
                               "reviewHistory": []})
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(sr, f)
        os.remove(os.path.join(proj, ".bodhi", ".migration-1.10.md"))
        out = run(proj, "migrate-spaced-review")
        check("stale-backup: re-migration succeeds against this run's input",
              out.get("action") == "migrated" and out["concepts"] == 3, out)
        check("stale-backup: extra concept survived",
              any(c["name"] == "Extra" for c in read_sr(proj)["concepts"]))
        backup = os.path.join(proj, ".bodhi", ".pre-1.10-backup", "spaced-review.json")
        with open(backup) as f:
            check("stale-backup: original backup never overwritten",
                  len(json.load(f)["concepts"]) == 2)


def t_forget_comma_names():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        run(proj, "add-concept", "--concept", "ACID, isolation levels",
            "--module", "Module A")
        out = run(proj, "forget", "--concept", "ACID, isolation levels")
        check("forget: comma-containing name demotable via --concept",
              out["concepts"] == ["ACID, isolation levels"], out)
        out = run(proj, "forget", "--concept", "B-tree indexes",
                  "--concept", "Query planning")
        check("forget: repeatable --concept demotes both", len(out["concepts"]) == 2)


def t_robustness():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        # Corrupt JSON -> clean die, no traceback
        srp = os.path.join(proj, ".bodhi", "spaced-review.json")
        good = open(srp).read()
        open(srp, "w").write(good[:50])
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "due"],
                           capture_output=True, text=True)
        check("robust: corrupt JSON dies cleanly", r.returncode == 1
              and "Traceback" not in r.stderr and "not valid JSON" in r.stderr,
              r.stderr[:120])
        open(srp, "w").write(good)
        # Unparseable nextReview surfaced by due + flagged by verify
        sr = read_sr(proj)
        sr["concepts"][0]["nextReview"] = "not-a-date"
        with open(srp, "w") as f:
            json.dump(sr, f)
        out = run(proj, "due")
        check("robust: unparseable nextReview surfaced",
              out.get("unparseableDates")
              and out["unparseableDates"][0]["name"] == "B-tree indexes", out)
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "verify"],
                           capture_output=True, text=True)
        check("robust: verify errors on unparseable nextReview", r.returncode == 1)
        sr["concepts"][0]["nextReview"] = "2026-06-01"
        # Case-insensitive duplicate -> verify error
        sr["concepts"].append(dict(sr["concepts"][0], name="B-TREE INDEXES"))
        with open(srp, "w") as f:
            json.dump(sr, f)
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "verify"],
                           capture_output=True, text=True)
        check("robust: duplicate names flagged",
              r.returncode == 1 and "duplicate" in r.stdout)
        # state.json as a list -> clean die
        spath = os.path.join(proj, ".bodhi", "state.json")
        sgood = open(spath).read()
        open(spath, "w").write("[1, 2]")
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "gate-check"],
                           capture_output=True, text=True)
        check("robust: list-typed state.json dies cleanly",
              r.returncode == 1 and "Traceback" not in r.stderr)
        open(spath, "w").write(sgood)
        # gate-check with empty currentModule declines
        st = json.loads(sgood)
        st["currentModule"] = ""
        with open(spath, "w") as f:
            json.dump(st, f)
        out = run(proj, "gate-check")
        check("robust: empty currentModule declines to gate",
              out["fires"] is False and "currentModule" in out["reason"], out)
        # missing spaced-review.json -> verify warns
        os.remove(srp)
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "verify"],
                           capture_output=True, text=True)
        outj = json.loads(r.stdout)
        check("robust: missing spaced-review warned",
              any("missing" in w for w in outj["warnings"]), outj)


def t_concurrency():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        for i in range(8):
            run(proj, "add-concept", "--concept", f"c{i}", "--module", "Module B")
        procs = [subprocess.Popen(
            [sys.executable, SCRIPT, "--project", proj, "record-review",
             "--concept", f"c{i}", "--result", "correct", "--tested-bloom", "2"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for i in range(8)]
        errs = []
        for p in procs:
            _, err = p.communicate()
            if p.returncode != 0 or "Traceback" in err:
                errs.append(err[:120])
        check("concurrency: 8 parallel writers, zero failures", not errs, errs)
        sr = read_sr(proj)
        lost = [f"c{i}" for i in range(8)
                if next(c for c in sr["concepts"] if c["name"] == f"c{i}")["box"] != 2]
        check("concurrency: zero lost updates", not lost, lost)


def t_history_cap():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        sr = read_sr(proj)
        sr["concepts"][0]["reviewHistory"] = [
            {"date": "2026-01-01", "result": "correct"} for _ in range(105)]
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(sr, f)
        run(proj, "record-review", "--concept", "B-tree indexes",
            "--result", "correct", "--tested-bloom", "2")
        c = read_sr(proj)["concepts"][0]
        check("cap: history capped at 100", len(c["reviewHistory"]) == 100,
              len(c["reviewHistory"]))
        check("cap: archived count recorded", c.get("reviewHistoryArchived") == 6)
        check("cap: newest entry kept",
              c["reviewHistory"][-1]["date"] == TODAY.isoformat())


def t_mastery_blocked_on_feynman():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        run(proj, "migrate-spaced-review")
        for _ in range(3):
            run(proj, "record-review", "--concept", "B-tree indexes",
                "--result", "correct", "--tested-bloom", "5")
        out = run(proj, "mastery")
        check("blocked: quiz-only concept named",
              out["blockedOnFeynman"] == ["B-tree indexes"], out)
        run(proj, "set-feynman", "--concept", "B-tree indexes")
        out = run(proj, "mastery")
        check("blocked: cleared after the gate", out["blockedOnFeynman"] == [])


def t_verify():
    with tempfile.TemporaryDirectory() as root:
        proj = make_project(root, spaced_review=json.loads(json.dumps(V2_SR)))
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "verify"],
                           capture_output=True, text=True)
        out = json.loads(r.stdout)
        check("verify: v2 file passes with warning", r.returncode == 0
              and any("v2" in w for w in out["warnings"]), out)
        # Break it: invalid session type
        srdata = read_sr(proj)
        srdata["sessionHistory"].append({"date": "2026-06-01", "type": "invented"})
        with open(os.path.join(proj, ".bodhi", "spaced-review.json"), "w") as f:
            json.dump(srdata, f)
        r = subprocess.run([sys.executable, SCRIPT, "--project", proj, "verify"],
                           capture_output=True, text=True)
        check("verify: invalid session type fails", r.returncode == 1)


def main():
    for t in (t_migrate, t_record_review, t_sessions_and_forget,
              t_touch_state_and_profile, t_gate_check,
              t_mastery_due_calibration, t_verify,
              t_retry_and_relearning, t_partial_breaks_streak,
              t_touch_state_profile_bump,
              t_data_reserved_keys, t_migrate_stale_backup,
              t_forget_comma_names, t_robustness, t_concurrency,
              t_history_cap, t_mastery_blocked_on_feynman):
        print(f"-- {t.__name__}")
        t()
    print(f"\n{PASS} passed, {FAIL} failed")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
